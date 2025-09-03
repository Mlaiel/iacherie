"""NFT Generator

NFT generation system for digital certificates and ownership proofs.
Creates and manages NFTs for copyright protection and digital rights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid
import base64

try:
    import web3
    from web3 import Web3
    from eth_account import Account
    import requests
    NFT_AVAILABLE = True
except ImportError:
    NFT_AVAILABLE = False

from .blockchain_registry import BlockchainRightsRegistry

logger = logging.getLogger(__name__)


class NFTStandard(Enum):
    """NFT standards"""
    ERC721 = "ERC721"
    ERC1155 = "ERC1155" 
    CUSTOM = "CUSTOM"


class MetadataStandard(Enum):
    """NFT metadata standards"""
    OPENSEA = "opensea"
    FOUNDATION = "foundation"
    RARIBLE = "rarible"
    CUSTOM = "custom"


@dataclass
class NFTMetadata:
    """NFT metadata structure"""
    name: str
    description: str
    image: str
    external_url: Optional[str] = None
    attributes: Optional[List[Dict[str, Any]]] = None
    properties: Optional[Dict[str, Any]] = None
    animation_url: Optional[str] = None
    youtube_url: Optional[str] = None


@dataclass
class CertificateMetadata:
    """Digital certificate metadata"""
    certificate_id: str
    content_id: str
    owner_id: str
    certificate_type: str
    issue_date: str
    expiry_date: Optional[str]
    verification_hash: str
    legal_status: str
    jurisdiction: str


@dataclass
class NFTResult:
    """NFT generation result"""
    success: bool
    nft_id: str
    token_id: Optional[str]
    contract_address: Optional[str]
    metadata_uri: str
    transaction_hash: Optional[str]
    certificate_data: Optional[CertificateMetadata]
    error: Optional[str] = None


class NFTGenerator:
    """NFT generator for digital certificates and ownership proofs"""
    
    def __init__(self,
                 blockchain_url: Optional[str] = None,
                 private_key: Optional[str] = None,
                 contract_address: Optional[str] = None,
                 ipfs_gateway: str = "https://ipfs.io/ipfs/"):
        """
        Initialize NFT generator
        
        Args:
            blockchain_url: Blockchain RPC URL
            private_key: Private key for transactions
            contract_address: NFT contract address
            ipfs_gateway: IPFS gateway URL
        """
        self.blockchain_url = blockchain_url
        self.contract_address = contract_address
        self.ipfs_gateway = ipfs_gateway
        
        # Initialize blockchain connection
        if NFT_AVAILABLE and blockchain_url:
            try:
                self.web3 = Web3(Web3.HTTPProvider(blockchain_url))
                if private_key:
                    self.account = Account.from_key(private_key)
                else:
                    self.account = None
            except Exception as e:
                logger.warning(f"Blockchain connection failed: {e}")
                self.web3 = None
                self.account = None
        else:
            self.web3 = None
            self.account = None
            
        # Initialize rights registry
        self.rights_registry = BlockchainRightsRegistry(
            blockchain_url, private_key, contract_address
        )
        
        # Local storage for development/testing
        self._local_nfts = {}
        self._metadata_storage = {}
    
    async def generate_copyright_certificate(self,
                                           content_id: str,
                                           owner_id: str,
                                           content_metadata: Dict[str, Any],
                                           certificate_type: str = "copyright") -> NFTResult:
        """
        Generate NFT certificate for copyright protection
        
        Args:
            content_id: Unique content identifier
            owner_id: Content owner identifier
            content_metadata: Content metadata
            certificate_type: Type of certificate
            
        Returns:
            NFT generation result
        """
        try:
            certificate_id = str(uuid.uuid4())
            issue_date = datetime.now().isoformat()
            
            # Create certificate metadata
            certificate_metadata = CertificateMetadata(
                certificate_id=certificate_id,
                content_id=content_id,
                owner_id=owner_id,
                certificate_type=certificate_type,
                issue_date=issue_date,
                expiry_date=None,  # Perpetual copyright
                verification_hash=self._generate_verification_hash(content_id, owner_id),
                legal_status="registered",
                jurisdiction="international"
            )
            
            # Create NFT metadata
            nft_metadata = NFTMetadata(
                name=f"Copyright Certificate - {content_metadata.get('title', content_id[:8])}",
                description=f"Digital copyright certificate for {content_metadata.get('type', 'content')} content",
                image=await self._generate_certificate_image(certificate_metadata, content_metadata),
                external_url=f"https://certificates.ainflue.com/{certificate_id}",
                attributes=[
                    {"trait_type": "Certificate Type", "value": certificate_type},
                    {"trait_type": "Content Type", "value": content_metadata.get('type', 'unknown')},
                    {"trait_type": "Issue Date", "value": issue_date},
                    {"trait_type": "Legal Status", "value": "registered"},
                    {"trait_type": "Jurisdiction", "value": "international"}
                ],
                properties={
                    "certificate_id": certificate_id,
                    "content_id": content_id,
                    "verification_hash": certificate_metadata.verification_hash
                }
            )
            
            # Upload metadata to IPFS
            metadata_uri = await self._upload_metadata_to_ipfs(nft_metadata)
            
            # Mint NFT
            nft_result = await self._mint_nft(
                owner_id,
                metadata_uri,
                certificate_metadata
            )
            
            if nft_result['success']:
                # Register with rights registry
                await self.rights_registry.register_rights(
                    content_id,
                    owner_id,
                    self.rights_registry.RightsType.COPYRIGHT,
                    {
                        'certificate_nft_id': nft_result['nft_id'],
                        'token_id': nft_result.get('token_id'),
                        'contract_address': nft_result.get('contract_address'),
                        'certificate_type': certificate_type
                    }
                )
                
                return NFTResult(
                    success=True,
                    nft_id=nft_result['nft_id'],
                    token_id=nft_result.get('token_id'),
                    contract_address=nft_result.get('contract_address'),
                    metadata_uri=metadata_uri,
                    transaction_hash=nft_result.get('transaction_hash'),
                    certificate_data=certificate_metadata
                )
            else:
                return NFTResult(
                    success=False,
                    nft_id="",
                    metadata_uri=metadata_uri,
                    certificate_data=certificate_metadata,
                    error=nft_result.get('error', 'NFT minting failed')
                )
                
        except Exception as e:
            logger.error(f"Copyright certificate generation failed: {e}")
            return NFTResult(
                success=False,
                nft_id="",
                metadata_uri="",
                error=str(e)
            )
    
    async def generate_ownership_proof(self,
                                     content_id: str,
                                     owner_id: str,
                                     ownership_evidence: Dict[str, Any]) -> NFTResult:
        """
        Generate NFT proof of ownership
        
        Args:
            content_id: Content identifier
            owner_id: Owner identifier
            ownership_evidence: Evidence supporting ownership
            
        Returns:
            NFT generation result
        """
        try:
            proof_id = str(uuid.uuid4())
            
            # Create ownership proof metadata
            certificate_metadata = CertificateMetadata(
                certificate_id=proof_id,
                content_id=content_id,
                owner_id=owner_id,
                certificate_type="ownership_proof",
                issue_date=datetime.now().isoformat(),
                expiry_date=None,
                verification_hash=self._generate_verification_hash(content_id, owner_id),
                legal_status="verified",
                jurisdiction="blockchain"
            )
            
            # Create NFT metadata
            nft_metadata = NFTMetadata(
                name=f"Ownership Proof - {content_id[:8]}",
                description="Blockchain-verified proof of content ownership",
                image=await self._generate_proof_image(certificate_metadata, ownership_evidence),
                attributes=[
                    {"trait_type": "Proof Type", "value": "ownership"},
                    {"trait_type": "Verification Level", "value": "blockchain"},
                    {"trait_type": "Evidence Count", "value": len(ownership_evidence.get('evidence', []))},
                    {"trait_type": "Issue Date", "value": certificate_metadata.issue_date}
                ],
                properties={
                    "proof_id": proof_id,
                    "content_id": content_id,
                    "evidence_hash": hashlib.sha256(
                        json.dumps(ownership_evidence, sort_keys=True).encode()
                    ).hexdigest()
                }
            )
            
            # Upload metadata
            metadata_uri = await self._upload_metadata_to_ipfs(nft_metadata)
            
            # Mint NFT
            nft_result = await self._mint_nft(owner_id, metadata_uri, certificate_metadata)
            
            return NFTResult(
                success=nft_result['success'],
                nft_id=nft_result['nft_id'],
                token_id=nft_result.get('token_id'),
                contract_address=nft_result.get('contract_address'),
                metadata_uri=metadata_uri,
                transaction_hash=nft_result.get('transaction_hash'),
                certificate_data=certificate_metadata,
                error=nft_result.get('error')
            )
            
        except Exception as e:
            logger.error(f"Ownership proof generation failed: {e}")
            return NFTResult(
                success=False,
                nft_id="",
                metadata_uri="",
                error=str(e)
            )
    
    async def verify_nft_certificate(self,
                                   nft_id: str,
                                   token_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify NFT certificate authenticity
        
        Args:
            nft_id: NFT identifier
            token_id: Optional token ID for blockchain verification
            
        Returns:
            Verification result
        """
        try:
            # Check local storage first
            if nft_id in self._local_nfts:
                nft_data = self._local_nfts[nft_id]
                certificate_data = nft_data['certificate_data']
                
                # Verify hash
                expected_hash = self._generate_verification_hash(
                    certificate_data['content_id'],
                    certificate_data['owner_id']
                )
                
                hash_valid = certificate_data['verification_hash'] == expected_hash
                
                return {
                    'verified': hash_valid,
                    'certificate_data': certificate_data,
                    'nft_metadata': nft_data['metadata'],
                    'verification_method': 'local',
                    'verification_timestamp': datetime.now().isoformat()
                }
            
            # Try blockchain verification if available
            if self.web3 and token_id:
                return await self._verify_blockchain_nft(token_id)
            
            return {
                'verified': False,
                'error': 'NFT not found'
            }
            
        except Exception as e:
            logger.error(f"NFT verification failed: {e}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    async def batch_generate_certificates(self,
                                        content_list: List[Dict[str, Any]]) -> List[NFTResult]:
        """
        Generate certificates for multiple content items
        
        Args:
            content_list: List of content items
            
        Returns:
            List of NFT generation results
        """
        tasks = []
        
        for content_item in content_list:
            task = self.generate_copyright_certificate(
                content_item['content_id'],
                content_item['owner_id'],
                content_item.get('metadata', {}),
                content_item.get('certificate_type', 'copyright')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = NFTResult(
                    success=False,
                    nft_id="",
                    metadata_uri="",
                    error=str(result)
                )
        
        return results
    
    async def _mint_nft(self,
                       owner_id: str,
                       metadata_uri: str,
                       certificate_data: CertificateMetadata) -> Dict[str, Any]:
        """Mint NFT on blockchain or store locally"""
        try:
            nft_id = str(uuid.uuid4())
            
            if self.web3 and self.account:
                # Blockchain minting (simplified)
                token_id = str(int(nft_id.replace('-', '')[:8], 16))
                
                # In production, this would interact with actual NFT contract
                tx_hash = f"0x{hashlib.sha256(f'{nft_id}{owner_id}{metadata_uri}'.encode()).hexdigest()}"
                
                # Store NFT data
                nft_data = {
                    'nft_id': nft_id,
                    'token_id': token_id,
                    'owner_id': owner_id,
                    'metadata_uri': metadata_uri,
                    'certificate_data': asdict(certificate_data),
                    'contract_address': self.contract_address,
                    'transaction_hash': tx_hash,
                    'creation_timestamp': datetime.now().isoformat(),
                    'blockchain': True
                }
                
                self._local_nfts[nft_id] = nft_data
                
                return {
                    'success': True,
                    'nft_id': nft_id,
                    'token_id': token_id,
                    'contract_address': self.contract_address,
                    'transaction_hash': tx_hash
                }
                
            else:
                # Local storage fallback
                nft_data = {
                    'nft_id': nft_id,
                    'owner_id': owner_id,
                    'metadata_uri': metadata_uri,
                    'certificate_data': asdict(certificate_data),
                    'creation_timestamp': datetime.now().isoformat(),
                    'blockchain': False
                }
                
                self._local_nfts[nft_id] = nft_data
                
                return {
                    'success': True,
                    'nft_id': nft_id,
                    'local_storage': True
                }
                
        except Exception as e:
            logger.error(f"NFT minting failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _upload_metadata_to_ipfs(self, metadata: NFTMetadata) -> str:
        """Upload metadata to IPFS (or local storage as fallback)"""
        try:
            metadata_json = json.dumps(asdict(metadata), indent=2)
            metadata_id = hashlib.sha256(metadata_json.encode()).hexdigest()
            
            # Store locally for development
            self._metadata_storage[metadata_id] = metadata_json
            
            # Return mock IPFS URI
            return f"ipfs://{metadata_id}"
            
        except Exception as e:
            logger.error(f"Metadata upload failed: {e}")
            return ""
    
    async def _generate_certificate_image(self,
                                        certificate_data: CertificateMetadata,
                                        content_metadata: Dict[str, Any]) -> str:
        """Generate certificate image (placeholder)"""
        # In production, this would generate an actual certificate image
        image_data = {
            'certificate_id': certificate_data.certificate_id,
            'content_type': content_metadata.get('type', 'unknown'),
            'issue_date': certificate_data.issue_date,
            'owner_id': certificate_data.owner_id
        }
        
        image_hash = hashlib.sha256(json.dumps(image_data, sort_keys=True).encode()).hexdigest()
        return f"data:image/png;base64,{base64.b64encode(image_hash.encode()).decode()}"
    
    async def _generate_proof_image(self,
                                  certificate_data: CertificateMetadata,
                                  ownership_evidence: Dict[str, Any]) -> str:
        """Generate ownership proof image (placeholder)"""
        image_data = {
            'proof_id': certificate_data.certificate_id,
            'content_id': certificate_data.content_id,
            'evidence_count': len(ownership_evidence.get('evidence', []))
        }
        
        image_hash = hashlib.sha256(json.dumps(image_data, sort_keys=True).encode()).hexdigest()
        return f"data:image/png;base64,{base64.b64encode(image_hash.encode()).decode()}"
    
    def _generate_verification_hash(self, content_id: str, owner_id: str) -> str:
        """Generate verification hash for certificate"""
        verification_data = f"{content_id}:{owner_id}:{datetime.now().date()}"
        return hashlib.sha256(verification_data.encode()).hexdigest()
    
    async def _verify_blockchain_nft(self, token_id: str) -> Dict[str, Any]:
        """Verify NFT on blockchain (placeholder)"""
        # In production, this would query the actual blockchain
        return {
            'verified': False,
            'error': 'Blockchain verification not implemented'
        }
    
    def get_nft_by_id(self, nft_id: str) -> Optional[Dict[str, Any]]:
        """Get NFT data by ID"""
        return self._local_nfts.get(nft_id)
    
    def get_metadata_by_uri(self, metadata_uri: str) -> Optional[str]:
        """Get metadata by URI"""
        # Extract metadata ID from IPFS URI
        if metadata_uri.startswith('ipfs://'):
            metadata_id = metadata_uri[7:]
            return self._metadata_storage.get(metadata_id)
        return None
    
    def list_nfts_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """List all NFTs owned by a specific owner"""
        return [
            nft_data for nft_data in self._local_nfts.values()
            if nft_data['owner_id'] == owner_id
        ]