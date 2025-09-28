"""🔥 Blockchain Exceptions - Ultra-Professional Error Handling System
================================================================

Comprehensive exception hierarchy for blockchain operations with detailed
error information, recovery strategies, and proper error propagation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standardized error codes for blockchain operations"""
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TRANSACTION_FAILED = "TRANSACTION_FAILED"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    CONTRACT_ERROR = "CONTRACT_ERROR"
    GAS_ERROR = "GAS_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    NFT_ERROR = "NFT_ERROR"


class BlockchainError(Exception):
    """Base exception for all blockchain-related errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[ErrorCode] = None,
        details: Optional[Dict[str, Any]] = None,
        transaction_hash: Optional[str] = None,
        network: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCode.UNKNOWN_ERROR
        self.details = details or {}
        self.transaction_hash = transaction_hash
        self.network = network
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
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
        network_name: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        super().__init__(message, ErrorCode.NETWORK_ERROR)
        self.network_name = network_name
        self.endpoint = endpoint


class BlockchainConnectionError(NetworkError):
    """Blockchain connection specific errors"""
    
    def __init__(
        self,
        message: str,
        network_name: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        super().__init__(message, network_name, endpoint)


class TransactionError(BlockchainError):
    """Transaction-related errors"""
    
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
        if network:
            details["network"] = network
        
        super().__init__(message, None, ErrorCode.INSUFFICIENT_FUNDS, details, network)


class GasEstimationError(TransactionError):
    """Gas estimation failed"""
    
    def __init__(
        self,
        message: str,
        transaction_data: Optional[Dict[str, Any]] = None,
        network: Optional[str] = None
    ):
        super().__init__(message, None, ErrorCode.GAS_ERROR, transaction_data, network)


class SmartContractError(BlockchainError):
    """Smart contract execution errors"""
    
    def __init__(
        self,
        message: str,
        contract_address: Optional[str] = None,
        function_name: Optional[str] = None,
        transaction_hash: Optional[str] = None
    ):
        super().__init__(message, ErrorCode.CONTRACT_ERROR, None, transaction_hash)
        self.contract_address = contract_address
        self.function_name = function_name


class ContractDeploymentError(SmartContractError):
    """Contract deployment specific errors"""
    
    def __init__(
        self,
        message: str,
        contract_address: Optional[str] = None,
        transaction_hash: Optional[str] = None
    ):
        super().__init__(message, contract_address, None, transaction_hash)


class ContractExecutionError(SmartContractError):
    """Contract execution specific errors"""
    
    def __init__(
        self,
        message: str,
        contract_address: Optional[str] = None,
        function_name: Optional[str] = None,
        transaction_hash: Optional[str] = None
    ):
        super().__init__(message, contract_address, function_name, transaction_hash)


class ValidationError(BlockchainError):
    """Data validation errors"""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None
    ):
        super().__init__(message, ErrorCode.VALIDATION_ERROR)
        self.field_name = field_name
        self.field_value = field_value


class SignatureValidationError(ValidationError):
    """Signature validation specific errors"""
    
    def __init__(
        self,
        message: str,
        signature: Optional[str] = None,
        public_key: Optional[str] = None
    ):
        super().__init__(message, "signature", signature)
        self.signature = signature
        self.public_key = public_key


class NFTError(BlockchainError):
    """NFT-related errors"""
    
    def __init__(
        self,
        message: str,
        token_id: Optional[str] = None,
        contract_address: Optional[str] = None
    ):
        super().__init__(message, ErrorCode.NFT_ERROR)
        self.token_id = token_id
        self.contract_address = contract_address


class NFTMintError(NFTError):
    """NFT minting specific errors"""
    
    def __init__(
        self,
        message: str,
        token_id: Optional[str] = None,
        contract_address: Optional[str] = None
    ):
        super().__init__(message, token_id, contract_address)


# Aliases for compatibility
NFTMintingError = NFTMintError
NFTTransferError = NFTError
Web3ProviderError = NetworkError
DLTStorageError = BlockchainError
CryptoPaymentError = TransactionError
DeFiIntegrationError = SmartContractError
# Specific DeFi error alias for backward compatibility
DeFiError = SmartContractError

class BlockchainSyncError(BlockchainError):
    """Raised when blockchain synchronization fails."""
    pass
ContractError = SmartContractError
SecurityError = ValidationError


# Export all exception classes
__all__ = [
    'ErrorCode',
    'BlockchainError',
    'NetworkError',
    'BlockchainConnectionError',
    'TransactionError',
    'InsufficientFundsError',
    'GasEstimationError',
    'SmartContractError',
    'ContractDeploymentError',
    'ContractExecutionError',
    'ValidationError',
    'SignatureValidationError',
    'NFTError',
    'NFTMintError',
    'NFTMintingError',
    'NFTTransferError',
    'Web3ProviderError',
    'DLTStorageError',
    'CryptoPaymentError',
    'DeFiIntegrationError',
    'DeFiError',
    'BlockchainSyncError'
]