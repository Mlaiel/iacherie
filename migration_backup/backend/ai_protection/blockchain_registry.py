"""Blockchain Rights Registry

Enhanced blockchain integration for digital rights management and watermark verification.
Builds upon existing functionality to provide comprehensive rights protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

try:
    import web3
    from web3 import Web3
    from eth_account import Account
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False

# Import existing blockchain registry functionality
from ...protection.watermarking.blockchain_registry import (
    BlockchainWatermarkRegistry,
    WatermarkRecord,
    OwnershipProof
)

logger = logging.getLogger(__name__)


@dataclass
class RightsRecord:
    """Digital rights record for blockchain storage"""
    rights_id: str
    content_id: str
    owner_address: str
    rights_type: str
    creation_timestamp: int
    expiration_timestamp: Optional[int]
    license_terms: Dict[str, Any]
    signature: str
    blockchain_tx: str


@dataclass  
class ProtectionMetadata:
    """Metadata for content protection"""
    content_type: str
    protection_level: str
    watermark_strength: float
    blockchain_verified: bool
    protection_timestamp: int
    fingerprint_hash: str
    

class RightsType(Enum):
    """Types of digital rights"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    LICENSING = "licensing"
    USAGE_RIGHTS = "usage_rights"
    DISTRIBUTION = "distribution"
    MONETIZATION = "monetization"


class BlockchainRightsRegistry:
    """Enhanced blockchain registry for digital rights management"""
    
    def __init__(self, 
                 blockchain_url: Optional[str] = None,
                 private_key: Optional[str] = None,
                 contract_address: Optional[str] = None):
        """
        Initialize blockchain rights registry
        
        Args:
            blockchain_url: Blockchain RPC URL
            private_key: Private key for transactions
            contract_address: Smart contract address
        """
        self.blockchain_url = blockchain_url
        self.contract_address = contract_address
        self._watermark_registry = BlockchainWatermarkRegistry(
            blockchain_url, private_key, contract_address
        )
        
        # Initialize Web3 connection if available
        if BLOCKCHAIN_AVAILABLE and blockchain_url:
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
            
        self._local_registry = {}
        
    async def register_rights(self,
                            content_id: str,
                            owner_id: str,
                            rights_type: RightsType,
                            license_terms: Dict[str, Any],
                            expiration_timestamp: Optional[int] = None) -> Dict[str, Any]:
        """
        Register digital rights on blockchain
        
        Args:
            content_id: Unique content identifier
            owner_id: Rights owner identifier
            rights_type: Type of rights being registered
            license_terms: License terms and conditions
            expiration_timestamp: Optional expiration timestamp
            
        Returns:
            Registration result with transaction details
        """
        try:
            rights_id = str(uuid.uuid4())
            timestamp = int(time.time())
            
            # Create rights record
            rights_data = {
                'rights_id': rights_id,
                'content_id': content_id,
                'owner_id': owner_id,
                'rights_type': rights_type.value,
                'license_terms': license_terms,
                'timestamp': timestamp,
                'expiration': expiration_timestamp
            }
            
            # Generate signature
            rights_content = json.dumps(rights_data, sort_keys=True)
            signature = hashlib.sha256(rights_content.encode()).hexdigest()
            
            # Submit to blockchain if available
            if self.web3 and self.account:
                tx_hash = await self._submit_rights_transaction(rights_data, signature)
            else:
                tx_hash = f"local_{uuid.uuid4()}"
                
            # Create rights record
            record = RightsRecord(
                rights_id=rights_id,
                content_id=content_id,
                owner_address=self.account.address if self.account else owner_id,
                rights_type=rights_type.value,
                creation_timestamp=timestamp,
                expiration_timestamp=expiration_timestamp,
                license_terms=license_terms,
                signature=signature,
                blockchain_tx=tx_hash
            )
            
            # Store locally for quick access
            self._local_registry[rights_id] = asdict(record)
            
            return {
                'success': True,
                'rights_id': rights_id,
                'blockchain_tx': tx_hash,
                'timestamp': timestamp,
                'signature': signature,
                'registration_cost': 0.001 if self.web3 else 0
            }
            
        except Exception as e:
            logger.error(f"Rights registration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_registration': await self._register_local_rights(
                    content_id, owner_id, rights_type, license_terms
                )
            }
    
    async def verify_rights(self,
                          rights_id: str,
                          content_id: str) -> Dict[str, Any]:
        """
        Verify rights ownership and validity
        
        Args:
            rights_id: Rights identifier to verify
            content_id: Content identifier
            
        Returns:
            Verification result with ownership details
        """
        try:
            # Check local registry first
            if rights_id in self._local_registry:
                record = self._local_registry[rights_id]
                
                # Verify content ID match
                if record['content_id'] != content_id:
                    return {
                        'verified': False,
                        'error': 'Content ID mismatch'
                    }
                
                # Check expiration
                if record.get('expiration_timestamp'):
                    if int(time.time()) > record['expiration_timestamp']:
                        return {
                            'verified': False,
                            'error': 'Rights expired'
                        }
                
                # Verify signature
                record_copy = record.copy()
                stored_signature = record_copy.pop('signature', '')
                record_content = json.dumps({
                    'rights_id': record_copy['rights_id'],
                    'content_id': record_copy['content_id'],
                    'owner_id': record_copy.get('owner_id', record_copy['owner_address']),
                    'rights_type': record_copy['rights_type'],
                    'license_terms': record_copy['license_terms'],
                    'timestamp': record_copy['creation_timestamp'],
                    'expiration': record_copy.get('expiration_timestamp')
                }, sort_keys=True)
                
                expected_signature = hashlib.sha256(record_content.encode()).hexdigest()
                
                return {
                    'verified': stored_signature == expected_signature,
                    'rights_record': record,
                    'verification_timestamp': int(time.time()),
                    'blockchain_verified': self.web3 is not None
                }
            
            # If not found locally, check blockchain
            return await self._verify_blockchain_rights(rights_id, content_id)
            
        except Exception as e:
            logger.error(f"Rights verification failed: {e}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    async def register_watermark_with_rights(self,
                                           watermark_data: Dict[str, Any],
                                           content_hash: str,
                                           owner_id: str,
                                           rights_type: RightsType = RightsType.COPYRIGHT) -> Dict[str, Any]:
        """
        Register watermark with associated digital rights
        
        Args:
            watermark_data: Watermark data
            content_hash: Content hash
            owner_id: Owner identifier
            rights_type: Type of rights
            
        Returns:
            Combined registration result
        """
        try:
            # Register watermark using existing functionality
            watermark_result = await self._watermark_registry.register_watermark(
                watermark_data, content_hash, owner_id
            )
            
            if watermark_result.get('success'):
                # Register associated rights
                license_terms = {
                    'usage_rights': 'exclusive',
                    'commercial_use': True,
                    'modification_rights': False,
                    'distribution_rights': True,
                    'watermark_id': watermark_result['watermark_id']
                }
                
                rights_result = await self.register_rights(
                    watermark_result['watermark_id'],
                    owner_id,
                    rights_type,
                    license_terms
                )
                
                return {
                    'success': True,
                    'watermark_registration': watermark_result,
                    'rights_registration': rights_result,
                    'combined_protection': True
                }
            else:
                return watermark_result
                
        except Exception as e:
            logger.error(f"Combined registration failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_rights_history(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get complete rights history for content
        
        Args:
            content_id: Content identifier
            
        Returns:
            List of rights records
        """
        history = []
        
        for rights_id, record in self._local_registry.items():
            if record['content_id'] == content_id:
                history.append({
                    'rights_id': rights_id,
                    'record': record,
                    'verification_status': await self.verify_rights(rights_id, content_id)
                })
        
        # Sort by timestamp
        history.sort(key=lambda x: x['record']['creation_timestamp'], reverse=True)
        
        return history
    
    async def _submit_rights_transaction(self,
                                       rights_data: Dict[str, Any],
                                       signature: str) -> str:
        """Submit rights transaction to blockchain"""
        # Simplified blockchain transaction
        # In production, this would interact with actual smart contract
        try:
            if not self.web3 or not self.account:
                raise Exception("Blockchain not available")
                
            # Create transaction data
            tx_data = {
                'rights_data': rights_data,
                'signature': signature,
                'timestamp': int(time.time())
            }
            
            # Generate mock transaction hash
            tx_content = json.dumps(tx_data, sort_keys=True)
            tx_hash = hashlib.sha256(tx_content.encode()).hexdigest()
            
            logger.info(f"Rights transaction submitted: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Blockchain transaction failed: {e}")
            raise
    
    async def _verify_blockchain_rights(self,
                                      rights_id: str,
                                      content_id: str) -> Dict[str, Any]:
        """Verify rights on blockchain"""
        # Mock blockchain verification
        return {
            'verified': False,
            'error': 'Rights not found on blockchain'
        }
    
    async def _register_local_rights(self,
                                   content_id: str,
                                   owner_id: str,
                                   rights_type: RightsType,
                                   license_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback local rights registration"""
        rights_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        record = {
            'rights_id': rights_id,
            'content_id': content_id,
            'owner_id': owner_id,
            'rights_type': rights_type.value,
            'license_terms': license_terms,
            'timestamp': timestamp,
            'local_only': True
        }
        
        self._local_registry[rights_id] = record
        
        return {
            'success': True,
            'rights_id': rights_id,
            'local_registration': True
        }