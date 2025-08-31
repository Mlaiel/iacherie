"""
Cryptographic Timestamping System
Professional timestamping service for content protection proof of existence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Any unauthorized use, reproduction, or distribution
of this code without explicit written permission is strictly prohibited.

Project Team Specialties:
- Lead AI Developer & Backend Senior: Fahed Mlaiel
- ML Engineer & Blockchain Specialist: Advanced IA Processing
- Database Administrator & Security Expert: Data Protection
- Microservices Architect & Audio Processing: Multi-format Support  
- DevOps Engineer & IA Prompt Engineer: Production Deployment

 STRONG WARNING 
Any attempt to steal, copy, reproduce, or use this concept, idea, or code 
without explicit written authorization from Fahed Mlaiel is strictly 
prohibited and will result in legal action.

Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import hmac
import secrets
from pathlib import Path
import base64
import time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import aiohttp

from .exceptions import (
    BlockchainError,
    SecurityError,
    SignatureValidationError,
    NetworkError
)

logger = logging.getLogger(__name__)


class TimestampingService(Enum):
    """Available timestamping services"""
    OPENTIMESTAMPS = "opentimestamps"
    BLOCKCHAIN_PROOF = "blockchain_proof"
    RFC3161_TSA = "rfc3161_tsa"
    ETHEREUM_TIMESTAMP = "ethereum_timestamp"
    BITCOIN_TIMESTAMP = "bitcoin_timestamp"


class ProofStatus(Enum):
    """Proof verification status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass
class TimestampProof:
    """Cryptographic timestamp proof structure"""
    content_hash: str
    timestamp: datetime
    service: TimestampingService
    proof_data: Dict[str, Any]
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    merkle_root: Optional[str] = None
    signature: Optional[str] = None
    status: ProofStatus = ProofStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""



        return {
            "content_hash": self.content_hash,
            "timestamp": self.timestamp.isoformat(),
            "service": self.service.value,
            "proof_data": self.proof_data,
            "transaction_hash": self.transaction_hash,
            "block_number": self.block_number,
            "merkle_root": self.merkle_root,
            "signature": self.signature,
            "status": self.status.value
        }


@dataclass
class ContentFingerprint:
    """Content fingerprint for timestamping"""
    content_id: str
    content_type: str  # audio, video, image, text
    file_hash: str
    metadata_hash: str
    combined_hash: str
    created_at: datetime
    size_bytes: int
    mime_type: str
    
    def __post_init__(self):
        """Generate combined hash from content and metadata"""
        if not self.combined_hash:
            data = f"{self.file_hash}:{self.metadata_hash}:{self.content_type}"
            self.combined_hash = hashlib.sha256(data.encode()).hexdigest()


class CryptographicTimestamping:
    """
    Professional cryptographic timestamping system for content protection
    Provides immutable proof of existence and integrity for digital content
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.private_key = self._load_private_key()
        self.public_key = self.private_key.public_key()
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _load_private_key(self) -> rsa.RSAPrivateKey:
        """Load or generate RSA private key for signing"""
        key_path = self.config.get("private_key_path")
        
        if key_path and Path(key_path).exists():
            with open(key_path, "rb") as key_file:
                return serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        else:
            # Generate new key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            if key_path:
                # Save key for future use
                pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                Path(key_path).parent.mkdir(parents=True, exist_ok=True)
                with open(key_path, "wb") as key_file:
                    key_file.write(pem)
            
            return private_key
    
    async def create_content_fingerprint(
        self,
        content_path: str,
        content_id: str,
        metadata: Dict[str, Any]
    ) -> ContentFingerprint:
        """
        Create cryptographic fingerprint of content
        
        Args:
            content_path: Path to content file
            content_id: Unique content identifier
            metadata: Content metadata
            
        Returns:
            ContentFingerprint object
        """



        try:
            file_path = Path(content_path)
            
            if not file_path.exists():
                raise BlockchainError(f"Content file not found: {content_path}")
            
            # Calculate file hash
            file_hash = await self._calculate_file_hash(file_path)
            
            # Calculate metadata hash
            metadata_str = json.dumps(metadata, sort_keys=True)
            metadata_hash = hashlib.sha256(metadata_str.encode()).hexdigest()
            
            # Determine content type and MIME type
            content_type = self._determine_content_type(file_path)
            mime_type = self._get_mime_type(file_path)
            
            return ContentFingerprint(
                content_id=content_id,
                content_type=content_type,
                file_hash=file_hash,
                metadata_hash=metadata_hash,
                combined_hash="",  # Will be calculated in __post_init__
                created_at=datetime.utcnow(),
                size_bytes=file_path.stat().st_size,
                mime_type=mime_type
            )
            
        except Exception as e:
            logger.error(f"Failed to create content fingerprint: {e}")
            raise BlockchainError(f"Content fingerprinting failed: {e}")
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            while chunk := f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _determine_content_type(self, file_path: Path) -> str:
        """Determine content type from file extension"""
        extension = file_path.suffix.lower()
        
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        text_extensions = {'.txt', '.md', '.json', '.xml', '.csv'}
        
        if extension in audio_extensions:
            return "audio"
        elif extension in video_extensions:
            return "video"
        elif extension in image_extensions:
            return "image"
        elif extension in text_extensions:
            return "text"
        else:
            return "unknown"
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type from file extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"
    
    async def create_timestamp_proof(
        self,
        fingerprint: ContentFingerprint,
        service: TimestampingService = TimestampingService.BLOCKCHAIN_PROOF
    ) -> TimestampProof:
        """
        Create cryptographic timestamp proof for content
        
        Args:
            fingerprint: Content fingerprint
            service: Timestamping service to use
            
        Returns:
            TimestampProof object
        """



        try:
            proof_data = {}
            transaction_hash = None
            block_number = None
            merkle_root = None
            
            if service == TimestampingService.BLOCKCHAIN_PROOF:
                # Use blockchain for timestamping
                result = await self._create_blockchain_timestamp(fingerprint)
                proof_data = result["proof_data"]
                transaction_hash = result.get("transaction_hash")
                block_number = result.get("block_number")
                
            elif service == TimestampingService.OPENTIMESTAMPS:
                # Use OpenTimestamps
                proof_data = await self._create_opentimestamps_proof(fingerprint)
                
            elif service == TimestampingService.RFC3161_TSA:
                # Use RFC3161 TSA
                proof_data = await self._create_rfc3161_proof(fingerprint)
            
            # Create digital signature
            signature = self._create_signature(fingerprint, proof_data)
            
            return TimestampProof(
                content_hash=fingerprint.combined_hash,
                timestamp=datetime.utcnow(),
                service=service,
                proof_data=proof_data,
                transaction_hash=transaction_hash,
                block_number=block_number,
                merkle_root=merkle_root,
                signature=signature,
                status=ProofStatus.PENDING
            )
            
        except Exception as e:
            logger.error(f"Failed to create timestamp proof: {e}")
            raise BlockchainError(f"Timestamp proof creation failed: {e}")
    
    async def _create_blockchain_timestamp(
        self,
        fingerprint: ContentFingerprint
    ) -> Dict[str, Any]:
        """Create blockchain-based timestamp proof"""
        # Implementation would integrate with smart contract
        # For now, return mock data structure
        return {
            "proof_data": {
                "hash": fingerprint.combined_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "network": "ethereum",
                "gas_used": 21000
            },
            "transaction_hash": f"0x{secrets.token_hex(32)}",
            "block_number": 18500000
        }
    
    async def _create_opentimestamps_proof(
        self,
        fingerprint: ContentFingerprint
    ) -> Dict[str, Any]:
        """Create OpenTimestamps proof"""
        # Implementation would integrate with OpenTimestamps
        return {
            "ots_file": f"{fingerprint.combined_hash}.ots",
            "calendar_urls": [
                "https://alice.btc.calendar.opentimestamps.org",
                "https://bob.btc.calendar.opentimestamps.org"
            ],
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _create_rfc3161_proof(
        self,
        fingerprint: ContentFingerprint
    ) -> Dict[str, Any]:
        """Create RFC3161 TSA proof"""
        # Implementation would integrate with TSA service
        return {
            "tsa_url": "http://timestamp.digicert.com",
            "tsr_token": base64.b64encode(secrets.token_bytes(64)).decode(),
            "policy_oid": "1.2.3.4.5",
            "hash_algorithm": "SHA-256"
        }
    
    def _create_signature(
        self,
        fingerprint: ContentFingerprint,
        proof_data: Dict[str, Any]
    ) -> str:
        """Create digital signature for proof integrity"""
        # Combine fingerprint and proof data for signing
        data_to_sign = {
            "content_hash": fingerprint.combined_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "proof_data": proof_data
        }
        
        message = json.dumps(data_to_sign, sort_keys=True).encode()
        
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
    
    async def verify_timestamp_proof(
        self,
        proof: TimestampProof,
        original_content: Optional[str] = None
    ) -> bool:
        """
        Verify the integrity and authenticity of a timestamp proof
        
        Args:
            proof: TimestampProof to verify
            original_content: Optional path to original content for verification
            
        Returns:
            True if proof is valid, False otherwise
        """



        try:
            # Verify signature
            if not self._verify_signature(proof):
                logger.warning(f"Signature verification failed for proof {proof.content_hash}")
                return False
            
            # Verify content hash if original content provided
            if original_content:
                fingerprint = await self.create_content_fingerprint(
                    original_content,
                    "verification",
                    {}
                )
                
                if fingerprint.combined_hash != proof.content_hash:
                    logger.warning(f"Content hash mismatch for proof {proof.content_hash}")
                    return False
            
            # Service-specific verification
            if proof.service == TimestampingService.BLOCKCHAIN_PROOF:
                return await self._verify_blockchain_proof(proof)
            elif proof.service == TimestampingService.OPENTIMESTAMPS:
                return await self._verify_opentimestamps_proof(proof)
            elif proof.service == TimestampingService.RFC3161_TSA:
                return await self._verify_rfc3161_proof(proof)
            
            return True
            
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return False
    
    def _verify_signature(self, proof: TimestampProof) -> bool:
        """Verify digital signature of proof"""



        try:
            if not proof.signature:
                return False
            
            # Reconstruct data that was signed
            data_to_verify = {
                "content_hash": proof.content_hash,
                "timestamp": proof.timestamp.isoformat(),
                "proof_data": proof.proof_data
            }
            
            message = json.dumps(data_to_verify, sort_keys=True).encode()
            signature_bytes = base64.b64decode(proof.signature.encode())
            
            self.public_key.verify(
                signature_bytes,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    async def _verify_blockchain_proof(self, proof: TimestampProof) -> bool:
        """Verify blockchain-based proof"""
        # Implementation would check transaction on blockchain
        return proof.transaction_hash is not None
    
    async def _verify_opentimestamps_proof(self, proof: TimestampProof) -> bool:
        """Verify OpenTimestamps proof"""
        # Implementation would verify with OpenTimestamps
        return "ots_file" in proof.proof_data
    
    async def _verify_rfc3161_proof(self, proof: TimestampProof) -> bool:
        """Verify RFC3161 TSA proof"""
        # Implementation would verify with TSA
        return "tsr_token" in proof.proof_data
    
    async def get_proof_status(self, proof: TimestampProof) -> ProofStatus:
        """Get current status of timestamp proof"""



        try:
            if proof.service == TimestampingService.BLOCKCHAIN_PROOF:
                # Check blockchain confirmation
                if proof.transaction_hash:
                    # Mock confirmation check - in reality would check blockchain
                    return ProofStatus.CONFIRMED
                else:
                    return ProofStatus.PENDING
            
            elif proof.service == TimestampingService.OPENTIMESTAMPS:
                # Check OpenTimestamps confirmation
                return ProofStatus.CONFIRMED
            
            elif proof.service == TimestampingService.RFC3161_TSA:
                # RFC3161 proofs are immediately confirmed
                return ProofStatus.CONFIRMED
            
            return ProofStatus.PENDING
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return ProofStatus.FAILED
    
    async def create_merkle_proof(
        self,
        fingerprints: List[ContentFingerprint]
    ) -> Dict[str, Any]:
        """
        Create Merkle tree proof for batch content verification
        
        Args:
            fingerprints: List of content fingerprints
            
        Returns:
            Merkle tree structure with root hash
        """



        try:
            if not fingerprints:
                raise ValueError("At least one fingerprint required")
            
            # Build Merkle tree
            leaves = [fp.combined_hash for fp in fingerprints]
            tree = self._build_merkle_tree(leaves)
            
            return {
                "merkle_root": tree[-1][0] if tree else None,
                "tree_depth": len(tree),
                "leaf_count": len(leaves),
                "tree_structure": tree,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Merkle proof creation failed: {e}")
            raise BlockchainError(f"Merkle proof creation failed: {e}")
    
    def _build_merkle_tree(self, leaves: List[str]) -> List[List[str]]:
        """Build Merkle tree from leaf hashes"""
        if not leaves:
            return []
        
        tree = [leaves]
        current_level = leaves
        
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Combine hashes
                combined = hashlib.sha256(f"{left}:{right}".encode()).hexdigest()
                next_level.append(combined)
            
            tree.append(next_level)
            current_level = next_level
        
        return tree
    
    async def batch_timestamp_content(
        self,
        content_paths: List[str],
        service: TimestampingService = TimestampingService.BLOCKCHAIN_PROOF
    ) -> List[TimestampProof]:
        """
        Batch timestamp multiple content files efficiently
        
        Args:
            content_paths: List of content file paths
            service: Timestamping service to use
            
        Returns:
            List of TimestampProof objects
        """



        try:
            # Create fingerprints for all content
            fingerprints = []
            for i, path in enumerate(content_paths):
                fingerprint = await self.create_content_fingerprint(
                    path,
                    f"batch_{i}_{int(time.time())}",
                    {"batch_index": i}
                )
                fingerprints.append(fingerprint)
            
            # Create Merkle proof for batch
            merkle_proof = await self.create_merkle_proof(fingerprints)
            
            # Create individual timestamp proofs
            proofs = []
            for fingerprint in fingerprints:
                proof = await self.create_timestamp_proof(fingerprint, service)
                proof.merkle_root = merkle_proof["merkle_root"]
                proofs.append(proof)
            
            return proofs
            
        except Exception as e:
            logger.error(f"Batch timestamping failed: {e}")
            raise BlockchainError(f"Batch timestamping failed: {e}")
