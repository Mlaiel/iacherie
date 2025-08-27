"""
Blockchain Database Index Module

Central indexing system for blockchain data, smart contracts, NFTs, and transactions
in the IA Influencer Agent content protection ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import asyncio

# Import all blockchain components
from .contracts import SmartContractManager, ContractType, ChainNetwork
from .nft import NFTCreator, NFTCreationRequest, NFTCreationResult
from .registry import CopyrightRegistry, RightsRegistration, RightsTransfer
from .storage import DecentralizedStorageManager, StorageMetadata
from .transactions import TransactionProcessor, TransactionResult
from .validators import ContentValidator, ValidationResult

logger = logging.getLogger(__name__)

class BlockchainIndex:
    """
    Central index for all blockchain operations and data.
    
    Provides unified access to contracts, NFTs, registrations, storage,
    transactions, and validations for the IA Influencer Agent platform.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize blockchain index.
        
        Args:
            config: Comprehensive configuration for all blockchain services
        """
        self.config = config
        
        # Initialize core services
        self.contract_manager = SmartContractManager(config.get("contracts", {}))
        self.nft_creator = NFTCreator(config.get("nft", {}))
        self.copyright_registry = CopyrightRegistry(config.get("registry", {}))
        self.storage_manager = DecentralizedStorageManager(config.get("storage", {}))
        self.transaction_processor = TransactionProcessor(config.get("transactions", {}))
        self.content_validator = ContentValidator(config.get("validation", {}))
        
        # Index mappings
        self.content_index = {}  # content_hash -> content info
        self.owner_index = {}    # owner_address -> owned content list
        self.contract_index = {} # contract_address -> contract info
        self.nft_index = {}      # token_id -> NFT info
        
        logger.info("Blockchain index initialized")

    async def register_content_protection(
        self,
        content_hash: str,
        content_data: bytes,
        metadata: Dict[str, Any],
        creator_address: str,
        protection_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive content protection registration.
        
        Performs copyright registration, NFT creation, storage, and validation
        in a single coordinated operation.
        
        Args:
            content_hash: Unique hash of the content
            content_data: Raw content bytes
            metadata: Content metadata
            creator_address: Address of the content creator
            protection_options: Additional protection configuration
            
        Returns:
            Dictionary with all protection results
        """
        try:
            protection_options = protection_options or {}
            logger.info(f"Starting comprehensive protection for: {content_hash}")
            
            # Step 1: Store content in decentralized storage
            storage_result = await self.storage_manager.store_content(
                content=content_data,
                filename=metadata.get("filename", f"content_{content_hash}"),
                content_type=self.storage_manager.ContentType.ORIGINAL_CONTENT,
                creator_address=creator_address,
                encrypt=protection_options.get("encrypt_content", True),
                pin=protection_options.get("pin_content", True)
            )
            
            # Step 2: Register copyright on blockchain
            from .registry import RightsType, ContentCategory, CreatorInfo
            
            creator_info = CreatorInfo(
                name=metadata.get("creator_name", ""),
                wallet_address=creator_address,
                email=metadata.get("creator_email"),
                website=metadata.get("creator_website")
            )
            
            copyright_registration = await self.copyright_registry.register_rights(
                content_hash=content_hash,
                content_fingerprint=metadata.get("fingerprint", ""),
                rights_type=RightsType.COPYRIGHT,
                content_category=ContentCategory(metadata.get("category", "visual_art")),
                title=metadata.get("title", ""),
                description=metadata.get("description", ""),
                creator=creator_info,
                metadata=metadata
            )
            
            # Step 3: Create NFT (if requested)
            nft_result = None
            if protection_options.get("create_nft", True):
                from .nft import NFTCreationRequest, NFTContentType, NFTStandard
                
                nft_request = NFTCreationRequest(
                    content_hash=content_hash,
                    content_type=NFTContentType(metadata.get("nft_content_type", "mixed_media")),
                    content_url=storage_result.storage_url,
                    title=metadata.get("title", ""),
                    description=metadata.get("description", ""),
                    creator_address=creator_address,
                    royalty_percentage=protection_options.get("royalty_percentage", 5.0),
                    standard=NFTStandard.ERC721,
                    attributes=metadata.get("nft_attributes", [])
                )
                
                nft_result = await self.nft_creator.create_nft(nft_request)
                
            # Step 4: Validate content authenticity
            validation_result = await self.content_validator.validate_content_authenticity(
                content_hash=content_hash,
                claimed_owner=creator_address,
                claimed_timestamp=datetime.utcnow(),
                proof_data={
                    "storage_proof": storage_result,
                    "copyright_proof": copyright_registration,
                    "nft_proof": nft_result
                }
            )
            
            # Step 5: Update indexes
            await self._update_indexes(
                content_hash, creator_address, storage_result, 
                copyright_registration, nft_result, validation_result
            )
            
            # Step 6: Compile comprehensive result
            protection_result = {
                "content_hash": content_hash,
                "creator_address": creator_address,
                "protection_timestamp": datetime.utcnow().isoformat(),
                "storage": {
                    "content_id": storage_result.content_id,
                    "storage_url": storage_result.storage_url,
                    "ipfs_hash": storage_result.storage_hash,
                    "encrypted": bool(storage_result.encryption_key)
                },
                "copyright": {
                    "registration_id": copyright_registration.registration_id,
                    "blockchain_transaction": copyright_registration.blockchain_transaction,
                    "status": copyright_registration.status.value
                },
                "validation": {
                    "validation_id": validation_result.validation_id,
                    "status": validation_result.status.value,
                    "trust_level": validation_result.trust_level.value,
                    "confidence": validation_result.overall_confidence
                }
            }
            
            if nft_result:
                protection_result["nft"] = {
                    "token_id": nft_result.token_id,
                    "contract_address": nft_result.contract_address,
                    "marketplace_url": nft_result.marketplace_url,
                    "metadata_uri": nft_result.metadata_uri
                }
                
            logger.info(f"Content protection completed: {content_hash}")
            return protection_result
            
        except Exception as e:
            logger.error(f"Content protection failed: {e}")
            raise

    async def _update_indexes(
        self,
        content_hash: str,
        creator_address: str,
        storage_result: StorageMetadata,
        copyright_registration: RightsRegistration,
        nft_result: Optional[NFTCreationResult],
        validation_result: ValidationResult
    ) -> None:
        """Update all relevant indexes with new content."""
        try:
            # Update content index
            self.content_index[content_hash] = {
                "creator_address": creator_address,
                "storage": storage_result,
                "copyright": copyright_registration,
                "nft": nft_result,
                "validation": validation_result,
                "created_at": datetime.utcnow()
            }
            
            # Update owner index
            if creator_address not in self.owner_index:
                self.owner_index[creator_address] = []
            self.owner_index[creator_address].append(content_hash)
            
            # Update NFT index
            if nft_result:
                nft_key = f"{nft_result.contract_address}:{nft_result.token_id}"
                self.nft_index[nft_key] = {
                    "content_hash": content_hash,
                    "creator_address": creator_address,
                    "nft_result": nft_result
                }
                
            logger.debug(f"Indexes updated for content: {content_hash}")
            
        except Exception as e:
            logger.error(f"Index update failed: {e}")
            raise

    async def verify_content_ownership(
        self,
        content_hash: str,
        claiming_address: str
    ) -> Dict[str, Any]:
        """
        Verify ownership of content across all protection mechanisms.
        
        Args:
            content_hash: Hash of the content to verify
            claiming_address: Address claiming ownership
            
        Returns:
            Comprehensive ownership verification result
        """
        try:
            content_info = self.content_index.get(content_hash)
            if not content_info:
                return {
                    "verified": False,
                    "reason": "Content not found in protection registry"
                }
                
            verification_results = {}
            
            # Check copyright registration
            copyright_reg = content_info.get("copyright")
            if copyright_reg:
                copyright_verified = copyright_reg.creator.wallet_address == claiming_address
                verification_results["copyright"] = {
                    "verified": copyright_verified,
                    "registration_id": copyright_reg.registration_id,
                    "blockchain_tx": copyright_reg.blockchain_transaction
                }
                
            # Check NFT ownership
            nft_result = content_info.get("nft")
            if nft_result:
                # In a real implementation, this would query the blockchain
                nft_owner_verified = True  # Placeholder
                verification_results["nft"] = {
                    "verified": nft_owner_verified,
                    "token_id": nft_result.token_id,
                    "contract_address": nft_result.contract_address
                }
                
            # Check storage permissions
            storage_info = content_info.get("storage")
            if storage_info:
                storage_verified = claiming_address in storage_info.access_permissions
                verification_results["storage"] = {
                    "verified": storage_verified,
                    "content_id": storage_info.content_id
                }
                
            # Check validation history
            validation_info = content_info.get("validation")
            if validation_info:
                validation_verified = validation_info.status.value == "authentic"
                verification_results["validation"] = {
                    "verified": validation_verified,
                    "validation_id": validation_info.validation_id,
                    "trust_level": validation_info.trust_level.value
                }
                
            # Determine overall verification
            all_verified = all(
                result.get("verified", False) 
                for result in verification_results.values()
            )
            
            return {
                "content_hash": content_hash,
                "claiming_address": claiming_address,
                "verified": all_verified,
                "verification_details": verification_results,
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ownership verification failed: {e}")
            return {
                "verified": False,
                "reason": f"Verification error: {str(e)}"
            }

    async def transfer_content_rights(
        self,
        content_hash: str,
        from_address: str,
        to_address: str,
        transfer_type: str = "sale",
        terms: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Transfer content rights to another party.
        
        Args:
            content_hash: Hash of the content
            from_address: Current owner address
            to_address: New owner address
            transfer_type: Type of transfer (sale, license, etc.)
            terms: Terms of the transfer
            
        Returns:
            Transfer result with transaction details
        """
        try:
            content_info = self.content_index.get(content_hash)
            if not content_info:
                raise ValueError("Content not found")
                
            # Verify current ownership
            ownership_verified = await self.verify_content_ownership(content_hash, from_address)
            if not ownership_verified.get("verified"):
                raise ValueError("Transfer denied: ownership not verified")
                
            transfer_results = {}
            
            # Transfer copyright registration
            copyright_reg = content_info.get("copyright")
            if copyright_reg:
                rights_transfer = await self.copyright_registry.transfer_rights(
                    registration_id=copyright_reg.registration_id,
                    from_owner=from_address,
                    to_owner=to_address,
                    transfer_type=transfer_type,
                    terms=terms or {}
                )
                transfer_results["copyright"] = rights_transfer
                
            # Transfer NFT (if applicable)
            nft_result = content_info.get("nft")
            if nft_result and transfer_type in ["sale", "assignment"]:
                # NFT transfer would be handled through smart contract
                # For now, record the intent
                transfer_results["nft"] = {
                    "token_id": nft_result.token_id,
                    "contract_address": nft_result.contract_address,
                    "transfer_pending": True
                }
                
            # Update storage permissions
            storage_info = content_info.get("storage")
            if storage_info:
                access_granted = self.storage_manager.grant_access(
                    storage_info.content_id, to_address
                )
                if transfer_type in ["sale", "assignment"]:
                    # Revoke access from previous owner
                    self.storage_manager.revoke_access(
                        storage_info.content_id, from_address
                    )
                transfer_results["storage"] = {
                    "access_granted": access_granted,
                    "exclusive_transfer": transfer_type in ["sale", "assignment"]
                }
                
            # Update indexes
            if transfer_type in ["sale", "assignment"]:
                content_info["creator_address"] = to_address
                self.owner_index[to_address] = self.owner_index.get(to_address, [])
                self.owner_index[to_address].append(content_hash)
                if content_hash in self.owner_index.get(from_address, []):
                    self.owner_index[from_address].remove(content_hash)
                    
            return {
                "content_hash": content_hash,
                "from_address": from_address,
                "to_address": to_address,
                "transfer_type": transfer_type,
                "transfer_results": transfer_results,
                "transfer_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Rights transfer failed: {e}")
            raise

    def search_content_by_creator(self, creator_address: str) -> List[Dict[str, Any]]:
        """Search all content by creator address."""
        content_hashes = self.owner_index.get(creator_address, [])
        return [
            {
                "content_hash": content_hash,
                **self.content_index[content_hash]
            }
            for content_hash in content_hashes
            if content_hash in self.content_index
        ]

    def get_content_info(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about content."""
        return self.content_index.get(content_hash)

    def get_blockchain_statistics(self) -> Dict[str, Any]:
        """Get comprehensive blockchain operation statistics."""
        total_content = len(self.content_index)
        total_creators = len(self.owner_index)
        total_nfts = len(self.nft_index)
        
        # Get transaction statistics
        tx_stats = self.transaction_processor.get_transaction_statistics()
        
        # Get storage statistics
        storage_stats = self.storage_manager.get_storage_stats()
        
        return {
            "content_protection": {
                "total_protected_content": total_content,
                "total_creators": total_creators,
                "total_nfts": total_nfts
            },
            "transactions": tx_stats,
            "storage": storage_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def monitor_blockchain_events(self) -> None:
        """Monitor blockchain events for updates."""
        try:
            # Monitor pending transactions
            await self.transaction_processor.monitor_pending_transactions()
            
            # Additional monitoring logic would go here
            logger.debug("Blockchain event monitoring cycle completed")
            
        except Exception as e:
            logger.error(f"Blockchain monitoring failed: {e}")

# Initialize the blockchain index as a singleton
_blockchain_index_instance = None

def get_blockchain_index(config: Dict[str, Any] = None) -> BlockchainIndex:
    """Get the singleton blockchain index instance."""
    global _blockchain_index_instance
    if _blockchain_index_instance is None and config:
        _blockchain_index_instance = BlockchainIndex(config)
    return _blockchain_index_instance

# Module exports
__all__ = [
    "BlockchainIndex",
    "get_blockchain_index"
]
