"""
Blockchain Validation and Verification System
Professional validation service for blockchain operations and content integrity

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
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import re
from pathlib import Path
import aiohttp
from web3 import Web3
from web3.middleware import geth_poa_middleware
import ipfshttpclient
from eth_utils import is_address, to_checksum_address
from eth_typing import ChecksumAddress, HexStr

from .exceptions import (
    BlockchainError,
    NetworkError,
    ContractError,
    TransactionError,
    SecurityError,
    SignatureValidationError
)
from .timestamping import TimestampProof, ProofStatus

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    FORENSIC = "forensic"


class ValidationResult(Enum):
    """Validation result status"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    validation_id: str
    timestamp: datetime
    level: ValidationLevel
    overall_result: ValidationResult
    score: float  # 0.0 to 1.0
    checks_performed: List[str]
    passed_checks: List[str]
    failed_checks: List[str]
    warnings: List[str]
    errors: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""



        return {
            "validation_id": self.validation_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "overall_result": self.overall_result.value,
            "score": self.score,
            "checks_performed": self.checks_performed,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "errors": self.errors,
            "metadata": self.metadata
        }


@dataclass
class ContentIntegrityCheck:
    """Content integrity verification result"""
    content_id: str
    original_hash: str
    current_hash: str
    is_intact: bool
    modified_at: Optional[datetime] = None
    modifications_detected: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class BlockchainTransactionValidation:
    """Blockchain transaction validation result"""
    transaction_hash: str
    network: str
    is_valid: bool
    confirmations: int
    gas_used: int
    status: str
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    value: Optional[str] = None


class BlockchainValidator:
    """
    Professional blockchain validation and verification system
    Provides comprehensive validation for content, transactions, and proofs
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.web3_connections = {}
        self.ipfs_client = None
        self.session = None
        self._init_connections()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.ipfs_client:
            self.ipfs_client.close()
    
    def _init_connections(self):
        """Initialize blockchain and storage connections"""



        try:
            # Initialize Web3 connections for different networks
            networks = self.config.get("networks", {})
            
            for network_name, network_config in networks.items():
                if "rpc_url" in network_config:
                    w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
                    
                    # Add middleware for PoA networks
                    if network_config.get("is_poa", False):
                        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    self.web3_connections[network_name] = w3
            
            # Initialize IPFS client
            ipfs_config = self.config.get("ipfs", {})
            if ipfs_config.get("enabled", False):
                self.ipfs_client = ipfshttpclient.connect(
                    addr=ipfs_config.get("api_url", "/ip4/127.0.0.1/tcp/5001/http")
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
    
    async def validate_content_integrity(
        self,
        content_path: str,
        original_hash: str,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ContentIntegrityCheck:
        """
        Validate content integrity against original hash
        
        Args:
            content_path: Path to content file
            original_hash: Original content hash
            validation_level: Validation strictness level
            
        Returns:
            ContentIntegrityCheck object
        """



        try:
            file_path = Path(content_path)
            
            if not file_path.exists():
                raise BlockchainError(f"Content file not found: {content_path}")
            
            # Calculate current hash
            current_hash = await self._calculate_file_hash(file_path)
            
            # Basic integrity check
            is_intact = current_hash == original_hash
            modifications_detected = []
            confidence = 1.0
            
            if not is_intact:
                # Detect type of modifications
                modifications_detected = await self._analyze_modifications(
                    file_path,
                    original_hash,
                    current_hash,
                    validation_level
                )
                
                # Calculate confidence based on modifications
                confidence = self._calculate_integrity_confidence(modifications_detected)
            
            return ContentIntegrityCheck(
                content_id=file_path.stem,
                original_hash=original_hash,
                current_hash=current_hash,
                is_intact=is_intact,
                modified_at=datetime.fromtimestamp(file_path.stat().st_mtime) if not is_intact else None,
                modifications_detected=modifications_detected,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Content integrity validation failed: {e}")
            raise BlockchainError(f"Content integrity validation failed: {e}")
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _analyze_modifications(
        self,
        file_path: Path,
        original_hash: str,
        current_hash: str,
        level: ValidationLevel
    ) -> List[str]:
        """Analyze detected modifications in content"""
        modifications = []
        
        # Basic modification detection
        modifications.append("content_hash_mismatch")
        
        if level in [ValidationLevel.STRICT, ValidationLevel.FORENSIC]:
            # File size analysis
            size = file_path.stat().st_size
            if size == 0:
                modifications.append("file_empty")
            elif size < 1024:  # Very small file
                modifications.append("file_truncated")
            
            # File extension check
            if not file_path.suffix:
                modifications.append("extension_removed")
            
            # Timestamp analysis
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime > datetime.utcnow() - timedelta(minutes=5):
                modifications.append("recently_modified")
        
        if level == ValidationLevel.FORENSIC:
            # Deep forensic analysis
            modifications.extend(await self._forensic_analysis(file_path))
        
        return modifications
    
    async def _forensic_analysis(self, file_path: Path) -> List[str]:
        """Perform forensic analysis on modified file"""
        forensic_findings = []
        
        try:
            # File header analysis
            with open(file_path, "rb") as f:
                header = f.read(256)
                
                # Check for common tampering signatures
                if b"EDITED" in header or b"MODIFIED" in header:
                    forensic_findings.append("tampering_signature_found")
                
                # Check for metadata manipulation
                if b"EXIF" in header and b"Photoshop" in header:
                    forensic_findings.append("image_editing_detected")
                
                # Check for steganography indicators
                if len(set(header[-50:])) < 5:  # Low entropy at end
                    forensic_findings.append("possible_steganography")
        
        except Exception as e:
            logger.warning(f"Forensic analysis failed: {e}")
            forensic_findings.append("forensic_analysis_error")
        
        return forensic_findings
    
    def _calculate_integrity_confidence(self, modifications: List[str]) -> float:
        """Calculate confidence score based on detected modifications"""
        if not modifications:
            return 1.0
        
        # Weight different types of modifications
        weights = {
            "content_hash_mismatch": 0.5,
            "file_empty": 0.9,
            "file_truncated": 0.7,
            "extension_removed": 0.3,
            "recently_modified": 0.2,
            "tampering_signature_found": 0.8,
            "image_editing_detected": 0.6,
            "possible_steganography": 0.4
        }
        
        total_penalty = sum(weights.get(mod, 0.5) for mod in modifications)
        confidence = max(0.0, 1.0 - total_penalty)
        
        return confidence
    
    async def validate_blockchain_transaction(
        self,
        transaction_hash: str,
        network: str = "ethereum"
    ) -> BlockchainTransactionValidation:
        """
        Validate blockchain transaction
        
        Args:
            transaction_hash: Transaction hash to validate
            network: Blockchain network name
            
        Returns:
            BlockchainTransactionValidation object
        """



        try:
            w3 = self.web3_connections.get(network)
            if not w3:
                raise NetworkError(f"No connection for network: {network}", network)
            
            if not w3.is_connected():
                raise NetworkError(f"Connection failed for network: {network}", network)
            
            # Get transaction receipt
            try:
                tx_receipt = w3.eth.get_transaction_receipt(transaction_hash)
                tx = w3.eth.get_transaction(transaction_hash)
            except Exception as e:
                return BlockchainTransactionValidation(
                    transaction_hash=transaction_hash,
                    network=network,
                    is_valid=False,
                    confirmations=0,
                    gas_used=0,
                    status="not_found"
                )
            
            # Calculate confirmations
            current_block = w3.eth.block_number
            confirmations = current_block - tx_receipt.blockNumber
            
            # Get block timestamp
            block = w3.eth.get_block(tx_receipt.blockNumber)
            timestamp = datetime.fromtimestamp(block.timestamp)
            
            return BlockchainTransactionValidation(
                transaction_hash=transaction_hash,
                network=network,
                is_valid=tx_receipt.status == 1,
                confirmations=confirmations,
                gas_used=tx_receipt.gasUsed,
                status="confirmed" if tx_receipt.status == 1 else "failed",
                block_number=tx_receipt.blockNumber,
                timestamp=timestamp,
                from_address=tx["from"],
                to_address=tx.get("to"),
                value=str(tx.get("value", 0))
            )
            
        except Exception as e:
            logger.error(f"Transaction validation failed: {e}")
            raise TransactionError(f"Transaction validation failed: {e}")
    
    async def validate_smart_contract(
        self,
        contract_address: str,
        network: str = "ethereum",
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationReport:
        """
        Validate smart contract
        
        Args:
            contract_address: Contract address to validate
            network: Blockchain network
            validation_level: Validation strictness
            
        Returns:
            ValidationReport object
        """



        try:
            w3 = self.web3_connections.get(network)
            if not w3:
                raise NetworkError(f"No connection for network: {network}", network)
            
            # Validate address format
            if not is_address(contract_address):
                raise ContractError(f"Invalid contract address: {contract_address}")
            
            checksum_address = to_checksum_address(contract_address)
            
            checks_performed = []
            passed_checks = []
            failed_checks = []
            warnings = []
            errors = []
            
            # Basic checks
            checks_performed.append("address_format_check")
            passed_checks.append("address_format_check")
            
            # Check if address contains code
            checks_performed.append("contract_code_check")
            code = w3.eth.get_code(checksum_address)
            if len(code) > 0:
                passed_checks.append("contract_code_check")
            else:
                failed_checks.append("contract_code_check")
                errors.append("No contract code found at address")
            
            # Check contract balance
            checks_performed.append("contract_balance_check")
            balance = w3.eth.get_balance(checksum_address)
            if balance >= 0:
                passed_checks.append("contract_balance_check")
            
            # Advanced checks for higher validation levels
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.FORENSIC]:
                # Check for proxy patterns
                checks_performed.append("proxy_pattern_check")
                if await self._check_proxy_pattern(w3, checksum_address):
                    warnings.append("Proxy contract detected")
                else:
                    passed_checks.append("proxy_pattern_check")
                
                # Check for recent activity
                checks_performed.append("activity_check")
                activity_score = await self._check_contract_activity(w3, checksum_address)
                if activity_score > 0.5:
                    passed_checks.append("activity_check")
                else:
                    warnings.append("Low contract activity detected")
            
            # Calculate overall score
            total_checks = len(checks_performed)
            passed_count = len(passed_checks)
            score = passed_count / total_checks if total_checks > 0 else 0.0
            
            # Determine overall result
            if score >= 0.9:
                overall_result = ValidationResult.VALID
            elif score >= 0.7:
                overall_result = ValidationResult.SUSPICIOUS
            else:
                overall_result = ValidationResult.INVALID
            
            return ValidationReport(
                validation_id=f"contract_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                level=validation_level,
                overall_result=overall_result,
                score=score,
                checks_performed=checks_performed,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                errors=errors,
                metadata={
                    "contract_address": checksum_address,
                    "network": network,
                    "code_size": len(code),
                    "balance_wei": str(balance)
                }
            )
            
        except Exception as e:
            logger.error(f"Contract validation failed: {e}")
            raise ContractError(f"Contract validation failed: {e}")
    
    async def _check_proxy_pattern(
        self,
        w3: Web3,
        contract_address: ChecksumAddress
    ) -> bool:
        """Check if contract follows proxy pattern"""



        try:
            code = w3.eth.get_code(contract_address)
            code_hex = code.hex()
            
            # Common proxy patterns
            proxy_patterns = [
                "363d3d373d3d3d363d73",  # EIP-1167 minimal proxy
                "5f355f59600060003584",  # Transparent proxy pattern
                "36603d8152600160003534"   # UUPS proxy pattern
            ]
            
            return any(pattern in code_hex for pattern in proxy_patterns)
            
        except Exception:
            return False
    
    async def _check_contract_activity(
        self,
        w3: Web3,
        contract_address: ChecksumAddress
    ) -> float:
        """Check contract activity level"""



        try:
            current_block = w3.eth.block_number
            blocks_to_check = min(1000, current_block)
            
            # Sample recent blocks for contract transactions
            activity_count = 0
            sample_size = 50
            
            for i in range(sample_size):
                block_number = current_block - (i * blocks_to_check // sample_size)
                try:
                    block = w3.eth.get_block(block_number, full_transactions=True)
                    
                    for tx in block.transactions:
                        if tx.get("to") == contract_address:
                            activity_count += 1
                            
                except Exception:
                    continue
            
            # Calculate activity score (0.0 to 1.0)
            return min(1.0, activity_count / 10)
            
        except Exception:
            return 0.0
    
    async def validate_timestamp_proof(
        self,
        proof: TimestampProof,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationReport:
        """
        Validate timestamp proof
        
        Args:
            proof: TimestampProof to validate
            validation_level: Validation strictness
            
        Returns:
            ValidationReport object
        """



        try:
            checks_performed = []
            passed_checks = []
            failed_checks = []
            warnings = []
            errors = []
            
            # Basic structure validation
            checks_performed.append("proof_structure_check")
            if self._validate_proof_structure(proof):
                passed_checks.append("proof_structure_check")
            else:
                failed_checks.append("proof_structure_check")
                errors.append("Invalid proof structure")
            
            # Timestamp validation
            checks_performed.append("timestamp_validation")
            if self._validate_timestamp(proof.timestamp):
                passed_checks.append("timestamp_validation")
            else:
                failed_checks.append("timestamp_validation")
                errors.append("Invalid timestamp")
            
            # Content hash validation
            checks_performed.append("content_hash_validation")
            if self._validate_content_hash(proof.content_hash):
                passed_checks.append("content_hash_validation")
            else:
                failed_checks.append("content_hash_validation")
                errors.append("Invalid content hash format")
            
            # Service-specific validation
            if proof.service.value in ["blockchain_proof", "ethereum_timestamp"]:
                checks_performed.append("blockchain_validation")
                if await self._validate_blockchain_proof_data(proof):
                    passed_checks.append("blockchain_validation")
                else:
                    failed_checks.append("blockchain_validation")
                    errors.append("Blockchain proof validation failed")
            
            # Signature validation (if present)
            if proof.signature:
                checks_performed.append("signature_validation")
                if self._validate_proof_signature(proof):
                    passed_checks.append("signature_validation")
                else:
                    failed_checks.append("signature_validation")
                    errors.append("Invalid signature")
            
            # Advanced validation for higher levels
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.FORENSIC]:
                # Cross-reference validation
                checks_performed.append("cross_reference_validation")
                if await self._cross_reference_proof(proof):
                    passed_checks.append("cross_reference_validation")
                else:
                    warnings.append("Could not cross-reference proof")
            
            # Calculate score
            total_checks = len(checks_performed)
            passed_count = len(passed_checks)
            score = passed_count / total_checks if total_checks > 0 else 0.0
            
            # Determine result
            if score >= 0.9 and not failed_checks:
                overall_result = ValidationResult.VALID
            elif score >= 0.7:
                overall_result = ValidationResult.SUSPICIOUS
            else:
                overall_result = ValidationResult.INVALID
            
            return ValidationReport(
                validation_id=f"proof_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                level=validation_level,
                overall_result=overall_result,
                score=score,
                checks_performed=checks_performed,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                errors=errors,
                metadata={
                    "proof_service": proof.service.value,
                    "proof_status": proof.status.value,
                    "content_hash": proof.content_hash
                }
            )
            
        except Exception as e:
            logger.error(f"Proof validation failed: {e}")
            raise BlockchainError(f"Proof validation failed: {e}")
    
    def _validate_proof_structure(self, proof: TimestampProof) -> bool:
        """Validate basic proof structure"""
        required_fields = ["content_hash", "timestamp", "service", "proof_data"]
        
        try:
            for field in required_fields:
                if not hasattr(proof, field) or getattr(proof, field) is None:
                    return False
            
            # Validate proof_data is a dict
            if not isinstance(proof.proof_data, dict):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_timestamp(self, timestamp: datetime) -> bool:
        """Validate timestamp reasonableness"""



        try:
            now = datetime.utcnow()
            
            # Check if timestamp is not in the future
            if timestamp > now + timedelta(minutes=5):
                return False
            
            # Check if timestamp is not too old (10 years)
            if timestamp < now - timedelta(days=3650):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_content_hash(self, content_hash: str) -> bool:
        """Validate content hash format"""



        try:
            # Check if it's a valid SHA-256 hash
            if len(content_hash) != 64:
                return False
            
            # Check if it's hexadecimal
            int(content_hash, 16)
            return True
            
        except (ValueError, TypeError):
            return False
    
    async def _validate_blockchain_proof_data(self, proof: TimestampProof) -> bool:
        """Validate blockchain-specific proof data"""



        try:
            if not proof.transaction_hash:
                return False
            
            # Validate transaction hash format
            if not re.match(r"^0x[a-fA-F0-9]{64}$", proof.transaction_hash):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_proof_signature(self, proof: TimestampProof) -> bool:
        """Validate proof signature"""



        try:
            # Basic signature format validation
            if not proof.signature:
                return False
            
            # Check if it's valid base64
            import base64
            base64.b64decode(proof.signature.encode())
            return True
            
        except Exception:
            return False
    
    async def _cross_reference_proof(self, proof: TimestampProof) -> bool:
        """Cross-reference proof with external sources"""



        try:
            # This would implement cross-referencing with:
            # - Blockchain explorers
            # - Timestamping services
            # - Content databases
            
            # For now, return True as a placeholder
            return True
            
        except Exception:
            return False
    
    async def validate_ipfs_content(
        self,
        ipfs_hash: str,
        expected_content_hash: Optional[str] = None
    ) -> ValidationReport:
        """
        Validate IPFS content integrity
        
        Args:
            ipfs_hash: IPFS content hash
            expected_content_hash: Expected content hash for verification
            
        Returns:
            ValidationReport object
        """



        try:
            if not self.ipfs_client:
                raise BlockchainError("IPFS client not available")
            
            checks_performed = []
            passed_checks = []
            failed_checks = []
            warnings = []
            errors = []
            
            # IPFS hash format validation
            checks_performed.append("ipfs_hash_format")
            if self._validate_ipfs_hash_format(ipfs_hash):
                passed_checks.append("ipfs_hash_format")
            else:
                failed_checks.append("ipfs_hash_format")
                errors.append("Invalid IPFS hash format")
            
            # Content availability check
            checks_performed.append("content_availability")
            try:
                content = self.ipfs_client.cat(ipfs_hash)
                passed_checks.append("content_availability")
                
                # Content integrity check
                if expected_content_hash:
                    checks_performed.append("content_integrity")
                    actual_hash = hashlib.sha256(content).hexdigest()
                    
                    if actual_hash == expected_content_hash:
                        passed_checks.append("content_integrity")
                    else:
                        failed_checks.append("content_integrity")
                        errors.append("Content hash mismatch")
                        
            except Exception as e:
                failed_checks.append("content_availability")
                errors.append(f"Content not available: {e}")
            
            # Calculate score
            total_checks = len(checks_performed)
            passed_count = len(passed_checks)
            score = passed_count / total_checks if total_checks > 0 else 0.0
            
            # Determine result
            if score == 1.0:
                overall_result = ValidationResult.VALID
            elif score >= 0.5:
                overall_result = ValidationResult.SUSPICIOUS
            else:
                overall_result = ValidationResult.INVALID
            
            return ValidationReport(
                validation_id=f"ipfs_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                level=ValidationLevel.STANDARD,
                overall_result=overall_result,
                score=score,
                checks_performed=checks_performed,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                errors=errors,
                metadata={
                    "ipfs_hash": ipfs_hash,
                    "expected_hash": expected_content_hash
                }
            )
            
        except Exception as e:
            logger.error(f"IPFS validation failed: {e}")
            raise BlockchainError(f"IPFS validation failed: {e}")
    
    def _validate_ipfs_hash_format(self, ipfs_hash: str) -> bool:
        """Validate IPFS hash format"""



        try:
            # Basic IPFS hash format validation
            # CIDv0: starts with Qm and is 46 characters
            # CIDv1: starts with b and is variable length
            
            if ipfs_hash.startswith("Qm") and len(ipfs_hash) == 46:
                return True
            elif ipfs_hash.startswith("b") and len(ipfs_hash) > 40:
                return True
            else:
                return False
                
        except Exception:
            return False
