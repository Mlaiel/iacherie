"""Advanced Copyright Registry for IA Influencer Agent Platform
Blockchain-based intellectual property protection and rights management

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import uuid

from ..core.exceptions import BlockchainError, CopyrightError
from ..security.encryption import EncryptionManager
from .transaction_manager import TransactionManager
from .smart_contracts import SmartContractManager


class CopyrightType(Enum):
    """Content copyright types for IA platform"""
    MUSIC_COMPOSITION = "music_composition"
    MUSIC_RECORDING = "music_recording"
    BLOG_POST = "blog_post"
    PHOTOGRAPHY = "photography"
    VIDEO_CONTENT = "video_content"
    PODCAST = "podcast"
    DIGITAL_ART = "digital_art"
    LIVE_PERFORMANCE = "live_performance"
    BRAND_CONTENT = "brand_content"


class ProtectionLevel(Enum):
    """Blockchain protection levels"""
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ULTRA_SECURE = "ultra_secure"


@dataclass
class CopyrightAsset:
    """Blockchain copyright asset representation"""
    asset_id: str
    creator_id: str
    title: str
    description: str
    copyright_type: CopyrightType
    protection_level: ProtectionLevel
    content_hash: str
    metadata_hash: str
    creation_timestamp: datetime
    registration_timestamp: datetime
    blockchain_tx_id: Optional[str] = None
    nft_token_id: Optional[str] = None
    license_terms: Optional[Dict[str, Any]] = None
    collaboration_rights: Optional[Dict[str, Any]] = None
    monetization_settings: Optional[Dict[str, Any]] = None


@dataclass
class CopyrightProof:
    """Blockchain copyright proof"""
    proof_id: str
    asset_id: str
    creator_id: str
    timestamp: datetime
    content_fingerprint: str
    blockchain_hash: str
    smart_contract_address: str
    verification_signature: str
    metadata: Dict[str, Any]


class CopyrightRegistryManager:
    """
    Advanced blockchain copyright registry for multi-format content protection
    Manages intellectual property rights with enterprise-grade security
    """
    
    def __init__(self, transaction_manager: TransactionManager, 
                 smart_contract_manager: SmartContractManager,
                 encryption_manager: EncryptionManager):
        self.transaction_manager = transaction_manager
        self.smart_contract_manager = smart_contract_manager
        self.encryption_manager = encryption_manager
        self.logger = logging.getLogger(__name__)
        self._registry_cache: Dict[str, CopyrightAsset] = {}
        self._proof_cache: Dict[str, CopyrightProof] = {}
    
    async def register_copyright(self, creator_id: str, content_data: bytes,
                               metadata: Dict[str, Any],
                               copyright_type: CopyrightType,
                               protection_level: ProtectionLevel = ProtectionLevel.PREMIUM) -> CopyrightAsset:
        """
        Register copyright on blockchain with advanced protection
        
        Args:
            creator_id: Content creator identifier
            content_data: Original content binary data
            metadata: Content metadata and attribution
            copyright_type: Type of copyrighted content
            protection_level: Blockchain protection level
            
        Returns:
            CopyrightAsset: Registered copyright asset with blockchain proof
            
        Raises:
            CopyrightError: If registration fails
        """
        try:
            # Generate unique asset ID
            asset_id = self._generate_asset_id(creator_id, content_data)
            
            # Create content fingerprint
            content_hash = self._generate_content_hash(content_data)
            metadata_hash = self._generate_metadata_hash(metadata)
            
            # Encrypt sensitive data
            encrypted_metadata = await self.encryption_manager.encrypt_data(
                json.dumps(metadata).encode()
            )
            
            # Create copyright asset
            asset = CopyrightAsset(
                asset_id=asset_id,
                creator_id=creator_id,
                title=metadata.get('title', 'Untitled'),
                description=metadata.get('description', ''),
                copyright_type=copyright_type,
                protection_level=protection_level,
                content_hash=content_hash,
                metadata_hash=metadata_hash,
                creation_timestamp=datetime.now(timezone.utc),
                registration_timestamp=datetime.now(timezone.utc),
                license_terms=metadata.get('license_terms'),
                collaboration_rights=metadata.get('collaboration_rights'),
                monetization_settings=metadata.get('monetization_settings')
            )
            
            # Deploy smart contract for copyright protection
            contract_address = await self.smart_contract_manager.deploy_copyright_contract(
                asset_id=asset_id,
                creator_id=creator_id,
                content_hash=content_hash,
                protection_level=protection_level.value
            )
            
            # Record on blockchain
            tx_id = await self.transaction_manager.create_copyright_transaction(
                asset_id=asset_id,
                creator_id=creator_id,
                content_hash=content_hash,
                contract_address=contract_address,
                encrypted_metadata=encrypted_metadata
            )
            
            asset.blockchain_tx_id = tx_id
            
            # Create NFT if premium protection
            if protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE, ProtectionLevel.ULTRA_SECURE]:
                nft_token_id = await self._create_copyright_nft(asset)
                asset.nft_token_id = nft_token_id
            
            # Cache registered asset
            self._registry_cache[asset_id] = asset
            
            self.logger.info(f"Copyright registered successfully: {asset_id}")
            return asset
            
        except Exception as e:
            self.logger.error(f"Copyright registration failed: {str(e)}")
            raise CopyrightError(f"Failed to register copyright: {str(e)}")
    
    async def verify_copyright(self, asset_id: str, 
                             content_data: Optional[bytes] = None) -> CopyrightProof:
        """
        Verify copyright authenticity on blockchain
        
        Args:
            asset_id: Copyright asset identifier
            content_data: Optional content data for verification
            
        Returns:
            CopyrightProof: Blockchain verification proof
            
        Raises:
            CopyrightError: If verification fails
        """
        try:
            # Get asset from registry
            asset = await self.get_copyright_asset(asset_id)
            if not asset:
                raise CopyrightError(f"Copyright asset not found: {asset_id}")
            
            # Verify blockchain transaction
            tx_verified = await self.transaction_manager.verify_transaction(
                asset.blockchain_tx_id
            )
            
            if not tx_verified:
                raise CopyrightError(f"Blockchain transaction verification failed")
            
            # Verify content integrity if provided
            if content_data:
                content_hash = self._generate_content_hash(content_data)
                if content_hash != asset.content_hash:
                    raise CopyrightError("Content integrity verification failed")
            
            # Create verification proof
            proof = CopyrightProof(
                proof_id=str(uuid.uuid4()),
                asset_id=asset_id,
                creator_id=asset.creator_id,
                timestamp=datetime.now(timezone.utc),
                content_fingerprint=asset.content_hash,
                blockchain_hash=asset.blockchain_tx_id,
                smart_contract_address=await self.smart_contract_manager.get_contract_address(asset_id),
                verification_signature=self._generate_verification_signature(asset),
                metadata={
                    'protection_level': asset.protection_level.value,
                    'registration_date': asset.registration_timestamp.isoformat(),
                    'copyright_type': asset.copyright_type.value
                }
            )
            
            # Cache proof
            self._proof_cache[proof.proof_id] = proof
            
            self.logger.info(f"Copyright verified successfully: {asset_id}")
            return proof
            
        except Exception as e:
            self.logger.error(f"Copyright verification failed: {str(e)}")
            raise CopyrightError(f"Failed to verify copyright: {str(e)}")
    
    async def get_copyright_asset(self, asset_id: str) -> Optional[CopyrightAsset]:
        """
        Retrieve copyright asset from registry
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Optional[CopyrightAsset]: Copyright asset if found
        """
        try:
            # Check cache first
            if asset_id in self._registry_cache:
                return self._registry_cache[asset_id]
            
            # Query blockchain
            asset_data = await self.smart_contract_manager.get_copyright_asset(asset_id)
            if not asset_data:
                return None
            
            # Reconstruct asset from blockchain data
            asset = self._reconstruct_asset_from_blockchain(asset_data)
            self._registry_cache[asset_id] = asset
            
            return asset
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve copyright asset {asset_id}: {str(e)}")
            return None
    
    async def get_creator_assets(self, creator_id: str) -> List[CopyrightAsset]:
        """
        Get all copyright assets for a creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            List[CopyrightAsset]: List of creator's copyright assets
        """
        try:
            asset_ids = await self.smart_contract_manager.get_creator_assets(creator_id)
            assets = []
            
            for asset_id in asset_ids:
                asset = await self.get_copyright_asset(asset_id)
                if asset:
                    assets.append(asset)
            
            return assets
            
        except Exception as e:
            self.logger.error(f"Failed to get creator assets: {str(e)}")
            return []
    
    async def transfer_copyright(self, asset_id: str, from_creator: str,
                               to_creator: str, transfer_terms: Dict[str, Any]) -> bool:
        """
        Transfer copyright ownership on blockchain
        
        Args:
            asset_id: Asset identifier
            from_creator: Current owner ID
            to_creator: New owner ID
            transfer_terms: Transfer conditions and terms
            
        Returns:
            bool: True if transfer successful
        """
        try:
            # Verify ownership
            asset = await self.get_copyright_asset(asset_id)
            if not asset or asset.creator_id != from_creator:
                raise CopyrightError("Unauthorized copyright transfer")
            
            # Execute blockchain transfer
            success = await self.smart_contract_manager.transfer_copyright(
                asset_id=asset_id,
                from_address=from_creator,
                to_address=to_creator,
                terms=transfer_terms
            )
            
            if success:
                # Update asset ownership
                asset.creator_id = to_creator
                self._registry_cache[asset_id] = asset
                
                # Record transfer transaction
                await self.transaction_manager.create_transfer_transaction(
                    asset_id=asset_id,
                    from_creator=from_creator,
                    to_creator=to_creator,
                    terms=transfer_terms
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Copyright transfer failed: {str(e)}")
            return False
    
    async def license_content(self, asset_id: str, licensee_id: str,
                            license_terms: Dict[str, Any]) -> Optional[str]:
        """
        Create content license on blockchain
        
        Args:
            asset_id: Asset identifier
            licensee_id: License recipient ID
            license_terms: License conditions and terms
            
        Returns:
            Optional[str]: License transaction ID if successful
        """
        try:
            # Verify asset exists
            asset = await self.get_copyright_asset(asset_id)
            if not asset:
                raise CopyrightError(f"Asset not found: {asset_id}")
            
            # Create license smart contract
            license_contract = await self.smart_contract_manager.create_license_contract(
                asset_id=asset_id,
                licensor=asset.creator_id,
                licensee=licensee_id,
                terms=license_terms
            )
            
            # Record license transaction
            license_tx_id = await self.transaction_manager.create_license_transaction(
                asset_id=asset_id,
                licensor=asset.creator_id,
                licensee=licensee_id,
                contract_address=license_contract,
                terms=license_terms
            )
            
            return license_tx_id
            
        except Exception as e:
            self.logger.error(f"Content licensing failed: {str(e)}")
            return None
    
    def _generate_asset_id(self, creator_id: str, content_data: bytes) -> str:
        """Generate unique asset identifier"""
        timestamp = str(int(datetime.now().timestamp()))
        data_hash = hashlib.sha256(content_data).hexdigest()[:16]
        return f"asset_{creator_id}_{timestamp}_{data_hash}"
    
    def _generate_content_hash(self, content_data: bytes) -> str:
        """Generate secure content hash"""
        return hashlib.sha3_256(content_data).hexdigest()
    
    def _generate_metadata_hash(self, metadata: Dict[str, Any]) -> str:
        """Generate metadata hash"""
        metadata_str = json.dumps(metadata, sort_keys=True)
        return hashlib.sha3_256(metadata_str.encode()).hexdigest()
    
    def _generate_verification_signature(self, asset: CopyrightAsset) -> str:
        """Generate verification signature"""
        signature_data = f"{asset.asset_id}_{asset.creator_id}_{asset.content_hash}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    async def _create_copyright_nft(self, asset: CopyrightAsset) -> str:
        """Create NFT for copyright protection"""
        try:
            nft_metadata = {
                'name': f"Copyright NFT - {asset.title}",
                'description': f"Blockchain copyright protection for {asset.title}",
                'asset_id': asset.asset_id,
                'creator': asset.creator_id,
                'copyright_type': asset.copyright_type.value,
                'protection_level': asset.protection_level.value,
                'registration_date': asset.registration_timestamp.isoformat()
            }
            
            token_id = await self.smart_contract_manager.mint_copyright_nft(
                recipient=asset.creator_id,
                metadata=nft_metadata
            )
            
            return token_id
            
        except Exception as e:
            self.logger.error(f"NFT creation failed: {str(e)}")
            raise CopyrightError(f"Failed to create copyright NFT: {str(e)}")
    
    def _reconstruct_asset_from_blockchain(self, blockchain_data: Dict[str, Any]) -> CopyrightAsset:
        """Reconstruct asset object from blockchain data"""
        return CopyrightAsset(
            asset_id=blockchain_data['asset_id'],
            creator_id=blockchain_data['creator_id'],
            title=blockchain_data['title'],
            description=blockchain_data['description'],
            copyright_type=CopyrightType(blockchain_data['copyright_type']),
            protection_level=ProtectionLevel(blockchain_data['protection_level']),
            content_hash=blockchain_data['content_hash'],
            metadata_hash=blockchain_data['metadata_hash'],
            creation_timestamp=datetime.fromisoformat(blockchain_data['creation_timestamp']),
            registration_timestamp=datetime.fromisoformat(blockchain_data['registration_timestamp']),
            blockchain_tx_id=blockchain_data.get('blockchain_tx_id'),
            nft_token_id=blockchain_data.get('nft_token_id'),
            license_terms=blockchain_data.get('license_terms'),
            collaboration_rights=blockchain_data.get('collaboration_rights'),
            monetization_settings=blockchain_data.get('monetization_settings')
        )


class CopyrightAnalytics:
    """Advanced copyright analytics and reporting"""
    
    def __init__(self, registry_manager: CopyrightRegistryManager):
        self.registry_manager = registry_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_copyright_statistics(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive copyright statistics"""
        try:
            stats = {
                'total_assets': 0,
                'by_type': {},
                'by_protection_level': {},
                'total_value_protected': 0,
                'recent_registrations': 0,
                'active_licenses': 0
            }
            
            if creator_id:
                assets = await self.registry_manager.get_creator_assets(creator_id)
            else:
                # Get all assets (admin function)
                assets = []  # Implementation depends on blockchain query capabilities
            
            for asset in assets:
                stats['total_assets'] += 1
                
                # Count by type
                type_key = asset.copyright_type.value
                stats['by_type'][type_key] = stats['by_type'].get(type_key, 0) + 1
                
                # Count by protection level
                level_key = asset.protection_level.value
                stats['by_protection_level'][level_key] = stats['by_protection_level'].get(level_key, 0) + 1
                
                # Recent registrations (last 30 days)
                if (datetime.now(timezone.utc) - asset.registration_timestamp).days <= 30:
                    stats['recent_registrations'] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get copyright statistics: {str(e)}")
            return {}
