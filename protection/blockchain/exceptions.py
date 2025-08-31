"""Blockchain Module Custom Exceptions
Professional exception handling for blockchain operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Any unauthorized use, reproduction, or distribution
of this code without explicit written permission is strictly prohibited.

Project Team Specialties:
- Lead AI Developer & Backend Senior: Fahed Mlaiel
- ML Engineer & Blockchain Specialist: Advanced IA Processing
- Database Administrator & Security Expert: Data Protection
- Microservices Architect & Audio Processing: Multi-format Support  
- DevOps Engineer & IA Prompt Engineer: Production Deployment

⚠️ STRONG WARNING ⚠️
Any attempt to steal, copy, reproduce, or use this concept, idea, or code 
without explicit written authorization from Fahed Mlaiel is strictly 
prohibited and will result in legal action.

Contact: mlaiel@live.de
"""
from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Blockchain error codes for standardized error handling"""    
    # General blockchain errors
    NETWORK_CONNECTION_FAILED = "BLOCKCHAIN_001"
    INVALID_NETWORK_CONFIG = "BLOCKCHAIN_002"
    TIMEOUT_ERROR = "BLOCKCHAIN_003"
    RATE_LIMIT_EXCEEDED = "BLOCKCHAIN_004"
    
    # Transaction errors
    TRANSACTION_FAILED = "TRANSACTION_001"
    INSUFFICIENT_FUNDS = "TRANSACTION_002"
    GAS_ESTIMATION_FAILED = "TRANSACTION_003"
    NONCE_TOO_LOW = "TRANSACTION_004"
    NONCE_TOO_HIGH = "TRANSACTION_005"
    
    # Smart contract errors
    CONTRACT_DEPLOYMENT_FAILED = "CONTRACT_001"
    CONTRACT_EXECUTION_FAILED = "CONTRACT_002"
    CONTRACT_NOT_FOUND = "CONTRACT_003"
    INVALID_CONTRACT_ADDRESS = "CONTRACT_004"
    CONTRACT_PAUSED = "CONTRACT_005"
    
    # NFT specific errors
    NFT_MINT_FAILED = "NFT_001"
    NFT_TRANSFER_FAILED = "NFT_002"
    NFT_METADATA_INVALID = "NFT_003"
    NFT_NOT_OWNED = "NFT_004"
    NFT_ALREADY_EXISTS = "NFT_005"
    
    # DeFi errors
    LIQUIDITY_INSUFFICIENT = "DEFI_001"
    SLIPPAGE_TOO_HIGH = "DEFI_002"
    POOL_NOT_FOUND = "DEFI_003"
    SWAP_FAILED = "DEFI_004"
    
    # Security errors
    SIGNATURE_VALIDATION_FAILED = "SECURITY_001"
    UNAUTHORIZED_ACCESS = "SECURITY_002"
    ENCRYPTION_FAILED = "SECURITY_003"
    PRIVATE_KEY_INVALID = "SECURITY_004"
    
    # IPFS/Storage errors
    IPFS_UPLOAD_FAILED = "STORAGE_001"
    IPFS_DOWNLOAD_FAILED = "STORAGE_002"
    ARWEAVE_UPLOAD_FAILED = "STORAGE_003"
    STORAGE_QUOTA_EXCEEDED = "STORAGE_004"


class BlockchainError(Exception):
    """Base exception for all blockchain operations"""    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        transaction_hash: Optional[str] = None,
        network: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.transaction_hash = transaction_hash
        self.network = network
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/API responses"""        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value,
            "details": self.details,
            "transaction_hash": self.transaction_hash,
            "network": self.network
        }


class NetworkError(BlockchainError):
    """Network connection and configuration errors"""    
    def __init__(
        self,
        message: str,
        network: str,
        error_code: ErrorCode = ErrorCode.NETWORK_CONNECTION_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details, network=network)


class TransactionError(BlockchainError):
    """Transaction execution errors"""    
    def __init__(
        self,
        message: str,
        transaction_hash: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.TRANSACTION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        network: Optional[str] = None
    ):
        super().__init__(message, error_code, details, transaction_hash, network)


class InsufficientFundsError(TransactionError):
    """Insufficient funds for transaction"""    
    def __init__(
        self,
        required_amount: str,
        available_amount: str,
        currency: str,
        network: Optional[str] = None
    ):
        message = f"Insufficient {currency}: required {required_amount}, available {available_amount}"
        details = {
            "required_amount": required_amount,
            "available_amount": available_amount,
            "currency": currency
        }
        super().__init__(
            message,
            error_code=ErrorCode.INSUFFICIENT_FUNDS,
            details=details,
            network=network
        )


class GasEstimationError(TransactionError):
    """Gas estimation failed"""    
    def __init__(
        self,
        message: str = "Failed to estimate gas for transaction",
        network: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message,
            error_code=ErrorCode.GAS_ESTIMATION_FAILED,
            details=details,
            network=network
        )


class ContractError(BlockchainError):
    """Smart contract related errors"""    
    def __init__(
        self,
        message: str,
        contract_address: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.CONTRACT_EXECUTION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        transaction_hash: Optional[str] = None,
        network: Optional[str] = None
    ):
        self.contract_address = contract_address
        if contract_address:
            details = details or {}
            details["contract_address"] = contract_address
        super().__init__(message, error_code, details, transaction_hash, network)


class ContractDeploymentError(ContractError):
    """Contract deployment specific errors"""    
    def __init__(
        self,
        message: str,
        contract_type: str,
        network: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["contract_type"] = contract_type
        super().__init__(
            message,
            error_code=ErrorCode.CONTRACT_DEPLOYMENT_FAILED,
            details=details,
            network=network
        )


class ContractExecutionError(ContractError):
    """Contract method execution errors"""    
    def __init__(
        self,
        message: str,
        contract_address: str,
        method_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        network: Optional[str] = None,
        transaction_hash: Optional[str] = None
    ):
        details = {
            "method_name": method_name,
            "parameters": parameters or {}
        }
        super().__init__(
            message,
            contract_address=contract_address,
            error_code=ErrorCode.CONTRACT_EXECUTION_FAILED,
            details=details,
            transaction_hash=transaction_hash,
            network=network
        )


class NFTError(BlockchainError):
    """NFT operation errors"""    
    def __init__(
        self,
        message: str,
        token_id: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.NFT_MINT_FAILED,
        details: Optional[Dict[str, Any]] = None,
        transaction_hash: Optional[str] = None,
        network: Optional[str] = None
    ):
        self.token_id = token_id
        if token_id:
            details = details or {}
            details["token_id"] = token_id
        super().__init__(message, error_code, details, transaction_hash, network)


class NFTMintError(NFTError):
    """NFT minting specific errors"""    
    def __init__(
        self,
        message: str,
        metadata_uri: Optional[str] = None,
        network: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if metadata_uri:
            details["metadata_uri"] = metadata_uri
        super().__init__(
            message,
            error_code=ErrorCode.NFT_MINT_FAILED,
            details=details,
            network=network
        )


class SecurityError(BlockchainError):
    """Security and authentication errors"""    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.SIGNATURE_VALIDATION_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class SignatureValidationError(SecurityError):
    """Digital signature validation errors"""    
    def __init__(
        self,
        message: str = "Invalid signature",
        signature: Optional[str] = None,
        expected_signer: Optional[str] = None
    ):
        details = {}
        if signature:
            details["signature"] = signature
        if expected_signer:
            details["expected_signer"] = expected_signer
        
        super().__init__(
            message,
            error_code=ErrorCode.SIGNATURE_VALIDATION_FAILED,
            details=details
        )


class StorageError(BlockchainError):
    """Decentralized storage errors"""    
    def __init__(
        self,
        message: str,
        storage_type: str,
        error_code: ErrorCode = ErrorCode.IPFS_UPLOAD_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["storage_type"] = storage_type
        super().__init__(message, error_code, details)


class IPFSError(StorageError):
    """IPFS specific errors"""    
    def __init__(
        self,
        message: str,
        ipfs_hash: Optional[str] = None,
        error_code: ErrorCode = ErrorCode.IPFS_UPLOAD_FAILED,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if ipfs_hash:
            details["ipfs_hash"] = ipfs_hash
        super().__init__(message, "ipfs", error_code, details)


class DeFiError(BlockchainError):
    """DeFi operation errors"""    
    def __init__(
        self,
        message: str,
        protocol: str,
        error_code: ErrorCode = ErrorCode.SWAP_FAILED,
        details: Optional[Dict[str, Any]] = None,
        transaction_hash: Optional[str] = None,
        network: Optional[str] = None
    ):
        details = details or {}
        details["protocol"] = protocol
        super().__init__(message, error_code, details, transaction_hash, network)


# Exception mapping for quick access
EXCEPTION_MAP = {
    ErrorCode.NETWORK_CONNECTION_FAILED: NetworkError,
    ErrorCode.TRANSACTION_FAILED: TransactionError,
    ErrorCode.INSUFFICIENT_FUNDS: InsufficientFundsError,
    ErrorCode.GAS_ESTIMATION_FAILED: GasEstimationError,
    ErrorCode.CONTRACT_DEPLOYMENT_FAILED: ContractDeploymentError,
    ErrorCode.CONTRACT_EXECUTION_FAILED: ContractExecutionError,
    ErrorCode.NFT_MINT_FAILED: NFTMintError,
    ErrorCode.SIGNATURE_VALIDATION_FAILED: SignatureValidationError,
    ErrorCode.IPFS_UPLOAD_FAILED: IPFSError,
    ErrorCode.SWAP_FAILED: DeFiError,
}


def create_exception(
    error_code: ErrorCode,
    message: str,
    **kwargs
) -> BlockchainError:
    """Factory function to create appropriate exception based on error code"""    exception_class = EXCEPTION_MAP.get(error_code, BlockchainError)
    return exception_class(message, error_code=error_code, **kwargs)

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BlockchainError(Exception):
    """Base exception for all blockchain-related errors"""    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        transaction_hash: str = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.transaction_hash = transaction_hash
        self.timestamp = self._get_timestamp()
        
        # Log the error for monitoring
        logger.error(f"BlockchainError: {message}", extra={
            'error_code': error_code,
            'details': details,
            'transaction_hash': transaction_hash
        })
        
        super().__init__(self.message)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for error tracking"""        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details,
            'transaction_hash': self.transaction_hash,
            'timestamp': self.timestamp
        }


class BlockchainConnectionError(BlockchainError):
    """Raised when blockchain network connection fails"""    
    def __init__(self, network: str, endpoint: str, **kwargs):
        message = f"Failed to connect to {network} blockchain at {endpoint}"
        super().__init__(message, error_code="BLOCKCHAIN_CONNECTION_FAILED", **kwargs)
        self.network = network
        self.endpoint = endpoint


class ContractDeploymentError(BlockchainError):
    """Raised when smart contract deployment fails"""    
    def __init__(self, contract_name: str, reason: str, **kwargs):
        message = f"Failed to deploy {contract_name} contract: {reason}"
        super().__init__(message, error_code="CONTRACT_DEPLOYMENT_FAILED", **kwargs)
        self.contract_name = contract_name
        self.reason = reason


class ContractExecutionError(BlockchainError):
    """Raised when smart contract execution fails"""    
    def __init__(self, contract_address: str, method: str, reason: str, **kwargs):
        message = f"Failed to execute {method} on contract {contract_address}: {reason}"
        super().__init__(message, error_code="CONTRACT_EXECUTION_FAILED", **kwargs)
        self.contract_address = contract_address
        self.method = method
        self.reason = reason


class TransactionError(BlockchainError):
    """Raised when blockchain transaction fails"""    
    def __init__(self, transaction_type: str, reason: str, gas_used: int = None, **kwargs):
        message = f"Transaction {transaction_type} failed: {reason}"
        super().__init__(message, error_code="TRANSACTION_FAILED", **kwargs)
        self.transaction_type = transaction_type
        self.reason = reason
        self.gas_used = gas_used


class InsufficientFundsError(BlockchainError):
    """Raised when wallet has insufficient funds for transaction"""    
    def __init__(self, required_amount: str, available_amount: str, currency: str = "ETH", **kwargs):
        message = f"Insufficient {currency}: required {required_amount}, available {available_amount}"
        super().__init__(message, error_code="INSUFFICIENT_FUNDS", **kwargs)
        self.required_amount = required_amount
        self.available_amount = available_amount
        self.currency = currency


class NFTMintingError(BlockchainError):
    """Raised when NFT minting operation fails"""    
    def __init__(self, token_id: str, collection: str, reason: str, **kwargs):
        message = f"Failed to mint NFT {token_id} in collection {collection}: {reason}"
        super().__init__(message, error_code="NFT_MINTING_FAILED", **kwargs)
        self.token_id = token_id
        self.collection = collection
        self.reason = reason


class NFTTransferError(BlockchainError):
    """Raised when NFT transfer fails"""    
    def __init__(self, token_id: str, from_address: str, to_address: str, reason: str, **kwargs):
        message = f"Failed to transfer NFT {token_id} from {from_address} to {to_address}: {reason}"
        super().__init__(message, error_code="NFT_TRANSFER_FAILED", **kwargs)
        self.token_id = token_id
        self.from_address = from_address
        self.to_address = to_address
        self.reason = reason


class DLTStorageError(BlockchainError):
    """Raised when distributed ledger storage operation fails"""    
    def __init__(self, operation: str, data_hash: str, reason: str, **kwargs):
        message = f"DLT storage {operation} failed for data {data_hash}: {reason}"
        super().__init__(message, error_code="DLT_STORAGE_FAILED", **kwargs)
        self.operation = operation
        self.data_hash = data_hash
        self.reason = reason


class CryptoPaymentError(BlockchainError):
    """Raised when cryptocurrency payment processing fails"""    
    def __init__(self, payment_id: str, amount: str, currency: str, reason: str, **kwargs):
        message = f"Crypto payment {payment_id} of {amount} {currency} failed: {reason}"
        super().__init__(message, error_code="CRYPTO_PAYMENT_FAILED", **kwargs)
        self.payment_id = payment_id
        self.amount = amount
        self.currency = currency
        self.reason = reason


class DeFiIntegrationError(BlockchainError):
    """Raised when DeFi protocol integration fails"""    
    def __init__(self, protocol: str, operation: str, reason: str, **kwargs):
        message = f"DeFi integration with {protocol} failed during {operation}: {reason}"
        super().__init__(message, error_code="DEFI_INTEGRATION_FAILED", **kwargs)
        self.protocol = protocol
        self.operation = operation
        self.reason = reason


class Web3ProviderError(BlockchainError):
    """Raised when Web3 provider connection or operation fails"""    
    def __init__(self, provider_url: str, operation: str, reason: str, **kwargs):
        message = f"Web3 provider {provider_url} failed during {operation}: {reason}"
        super().__init__(message, error_code="WEB3_PROVIDER_FAILED", **kwargs)
        self.provider_url = provider_url
        self.operation = operation
        self.reason = reason


class GasEstimationError(BlockchainError):
    """Raised when gas estimation for transaction fails"""    
    def __init__(self, transaction_data: str, reason: str, **kwargs):
        message = f"Gas estimation failed for transaction: {reason}"
        super().__init__(message, error_code="GAS_ESTIMATION_FAILED", **kwargs)
        self.transaction_data = transaction_data
        self.reason = reason


class SignatureValidationError(BlockchainError):
    """Raised when cryptographic signature validation fails"""    
    def __init__(self, signature: str, signer_address: str, reason: str, **kwargs):
        message = f"Signature validation failed for {signer_address}: {reason}"
        super().__init__(message, error_code="SIGNATURE_VALIDATION_FAILED", **kwargs)
        self.signature = signature
        self.signer_address = signer_address
        self.reason = reason


class BlockchainSyncError(BlockchainError):
    """Raised when blockchain synchronization fails"""    
    def __init__(self, current_block: int, target_block: int, reason: str, **kwargs):
        message = f"Blockchain sync failed at block {current_block}/{target_block}: {reason}"
        super().__init__(message, error_code="BLOCKCHAIN_SYNC_FAILED", **kwargs)
        self.current_block = current_block
        self.target_block = target_block
        self.reason = reason
