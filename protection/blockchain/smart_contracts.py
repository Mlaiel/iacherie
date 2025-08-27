"""
Smart Contract Management System for Content Protection
Professional blockchain smart contract interface and management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Any unauthorized use, reproduction, or distribution
of this code without explicit written permission is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import secrets
from decimal import Decimal
import aiohttp
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
from eth_typing import ChecksumAddress

from .exceptions import (
    BlockchainConnectionError,
    ContractDeploymentError,
    ContractExecutionError,
    TransactionError,
    InsufficientFundsError,
    GasEstimationError,
    SignatureValidationError
)

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of smart contracts for content protection"""
    COPYRIGHT_REGISTRY = "copyright_registry"
    CONTENT_AUTHENTICITY = "content_authenticity"
    USAGE_LICENSE = "usage_license"
    ROYALTY_DISTRIBUTION = "royalty_distribution"
    OWNERSHIP_TRANSFER = "ownership_transfer"
    ACCESS_CONTROL = "access_control"


class NetworkConfig:
    """Blockchain network configuration"""
    
    ETHEREUM_MAINNET = {
        'name': 'Ethereum Mainnet',
        'chain_id': 1,
        'rpc_url': 'https://mainnet.infura.io/v3/',
        'explorer_url': 'https://etherscan.io',
        'gas_price_gwei': 20,
        'block_time': 13
    }
    
    ETHEREUM_SEPOLIA = {
        'name': 'Ethereum Sepolia',
        'chain_id': 11155111,
        'rpc_url': 'https://sepolia.infura.io/v3/',
        'explorer_url': 'https://sepolia.etherscan.io',
        'gas_price_gwei': 10,
        'block_time': 13
    }
    
    POLYGON_MAINNET = {
        'name': 'Polygon Mainnet',
        'chain_id': 137,
        'rpc_url': 'https://polygon-rpc.com/',
        'explorer_url': 'https://polygonscan.com',
        'gas_price_gwei': 30,
        'block_time': 2
    }
    
    POLYGON_MUMBAI = {
        'name': 'Polygon Mumbai',
        'chain_id': 80001,
        'rpc_url': 'https://rpc-mumbai.maticvigil.com/',
        'explorer_url': 'https://mumbai.polygonscan.com',
        'gas_price_gwei': 1,
        'block_time': 2
    }


@dataclass
class ContractDeploymentConfig:
    """Configuration for smart contract deployment"""
    contract_type: ContractType
    network_config: Dict[str, Any]
    deployer_private_key: str
    gas_limit: int = 5000000
    gas_price_gwei: Optional[int] = None
    constructor_args: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        if self.gas_price_gwei is None:
            self.gas_price_gwei = self.network_config.get('gas_price_gwei', 20)


class SmartContractManager:
    """Professional smart contract management system"""
    
    def __init__(self, network_config: Dict[str, Any], private_key: Optional[str] = None):
        self.network_config = network_config
        self.private_key = private_key
        self.w3: Optional[Web3] = None
        self.account: Optional[Account] = None
        self.contracts: Dict[str, Contract] = {}
        self.contract_addresses: Dict[ContractType, str] = {}
        
        # Contract ABIs (loaded from JSON files or embedded)
        self.contract_abis = self._load_contract_abis()
        
        # Gas estimation cache
        self.gas_estimates: Dict[str, int] = {}
    
    async def initialize(self) -> bool:
        """Initialize blockchain connection and account"""
        try:
            # Initialize Web3 connection
            rpc_url = self.network_config['rpc_url']
            if self.network_config.get('api_key'):
                rpc_url += self.network_config['api_key']
            
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Verify connection
            if not self.w3.is_connected():
                raise BlockchainConnectionError(f"Failed to connect to {rpc_url}")
            
            # Setup account if private key provided
            if self.private_key:
                self.account = Account.from_key(self.private_key)
                logger.info(f"Account initialized: {self.account.address}")
            
            # Load deployed contract addresses
            await self._load_deployed_contracts()
            
            logger.info(f"Smart contract manager initialized for {self.network_config['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize smart contract manager: {e}")
            return False
    
    def _load_contract_abis(self) -> Dict[ContractType, List[Dict[str, Any]]]:
        """Load smart contract ABIs"""
        # In production, these would be loaded from JSON files
        return {
            ContractType.COPYRIGHT_REGISTRY: self._get_copyright_registry_abi(),
            ContractType.CONTENT_AUTHENTICITY: self._get_content_authenticity_abi(),
            ContractType.USAGE_LICENSE: self._get_usage_license_abi(),
            ContractType.ROYALTY_DISTRIBUTION: self._get_royalty_distribution_abi(),
            ContractType.OWNERSHIP_TRANSFER: self._get_ownership_transfer_abi(),
            ContractType.ACCESS_CONTROL: self._get_access_control_abi()
        }
    
    async def _load_deployed_contracts(self):
        """Load deployed contract addresses from configuration"""
        try:
            # In production, load from database or configuration file
            deployed_contracts = {
                ContractType.COPYRIGHT_REGISTRY: "0x742d35Cc631C0532925a3b8D4684dE0C0090D4F9",
                ContractType.CONTENT_AUTHENTICITY: "0x742d35Cc631C0532925a3b8D4684dE0C0090D4FA",
                ContractType.USAGE_LICENSE: "0x742d35Cc631C0532925a3b8D4684dE0C0090D4FB",
            }
            
            for contract_type, address in deployed_contracts.items():
                if self.w3.is_address(address):
                    self.contract_addresses[contract_type] = Web3.to_checksum_address(address)
                    
        except Exception as e:
            logger.warning(f"Could not load deployed contracts: {e}")
    
    async def deploy_contract(self, config: ContractDeploymentConfig) -> Tuple[str, str]:
        """Deploy a smart contract to the blockchain"""
        try:
            if not self.w3 or not self.account:
                raise ContractDeploymentError("Web3 or account not initialized")
            
            # Get contract ABI and bytecode
            abi = self.contract_abis.get(config.contract_type)
            if not abi:
                raise ContractDeploymentError(f"ABI not found for contract type {config.contract_type}")
            
            bytecode = self._get_contract_bytecode(config.contract_type)
            
            # Create contract factory
            contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
            
            # Estimate gas
            gas_estimate = await self._estimate_deployment_gas(
                contract, config.constructor_args
            )
            
            # Build transaction
            transaction = contract.constructor(*config.constructor_args).build_transaction({
                'from': self.account.address,
                'gas': min(gas_estimate, config.gas_limit),
                'gasPrice': self.w3.to_wei(config.gas_price_gwei, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt.status != 1:
                raise ContractDeploymentError(f"Contract deployment failed: {receipt}")
            
            contract_address = receipt.contractAddress
            
            # Store deployed contract
            self.contract_addresses[config.contract_type] = contract_address
            self.contracts[contract_address] = self.w3.eth.contract(
                address=contract_address,
                abi=abi
            )
            
            logger.info(f"Contract deployed: {config.contract_type.value} at {contract_address}")
            return tx_hash.hex(), contract_address
            
        except Exception as e:
            logger.error(f"Contract deployment failed: {e}")
            raise ContractDeploymentError(f"Failed to deploy contract: {e}")
    
    async def _estimate_deployment_gas(self, contract: Contract, constructor_args: List[Any]) -> int:
        """Estimate gas for contract deployment"""
        try:
            gas_estimate = contract.constructor(*constructor_args).estimate_gas({
                'from': self.account.address
            })
            
            # Add 20% buffer
            return int(gas_estimate * 1.2)
            
        except Exception as e:
            logger.warning(f"Gas estimation failed, using default: {e}")
            return 5000000  # Default gas limit
    
    async def register_copyright(
        self,
        content_hash: str,
        content_metadata: Dict[str, Any],
        owner_address: str,
        rights_description: str
    ) -> Tuple[str, int]:
        """Register copyright on blockchain"""
        try:
            contract_address = self.contract_addresses.get(ContractType.COPYRIGHT_REGISTRY)
            if not contract_address:
                raise TransactionError("Copyright registry contract not deployed")
            
            contract = self.contracts.get(contract_address)
            if not contract:
                contract = self.w3.eth.contract(
                    address=contract_address,
                    abi=self.contract_abis[ContractType.COPYRIGHT_REGISTRY]
                )
                self.contracts[contract_address] = contract
            
            # Prepare transaction data
            metadata_json = json.dumps(content_metadata, sort_keys=True)
            timestamp = int(datetime.utcnow().timestamp())
            
            # Build transaction
            function = contract.functions.registerCopyright(
                content_hash,
                metadata_json,
                owner_address,
                rights_description,
                timestamp
            )
            
            # Estimate gas
            gas_estimate = function.estimate_gas({'from': self.account.address})
            
            # Build and send transaction
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': int(gas_estimate * 1.2),
                'gasPrice': self.w3.to_wei(20, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status != 1:
                raise TransactionError(f"Copyright registration failed: {receipt}")
            
            # Extract registration ID from logs
            registration_id = self._extract_registration_id(receipt)
            
            logger.info(f"Copyright registered: {content_hash} -> ID {registration_id}")
            return tx_hash.hex(), registration_id
            
        except Exception as e:
            logger.error(f"Copyright registration failed: {e}")
            raise TransactionError(f"Failed to register copyright: {e}")
    
    async def verify_content_authenticity(
        self,
        content_hash: str,
        signature: str,
        creator_address: str
    ) -> bool:
        """Verify content authenticity on blockchain"""
        try:
            contract_address = self.contract_addresses.get(ContractType.CONTENT_AUTHENTICITY)
            if not contract_address:
                logger.warning("Content authenticity contract not deployed")
                return False
            
            contract = self.contracts.get(contract_address)
            if not contract:
                contract = self.w3.eth.contract(
                    address=contract_address,
                    abi=self.contract_abis[ContractType.CONTENT_AUTHENTICITY]
                )
                self.contracts[contract_address] = contract
            
            # Call contract function
            is_authentic = contract.functions.verifyAuthenticity(
                content_hash,
                signature,
                creator_address
            ).call()
            
            logger.info(f"Content authenticity verified: {content_hash} -> {is_authentic}")
            return is_authentic
            
        except Exception as e:
            logger.error(f"Content authenticity verification failed: {e}")
            return False
    
    async def create_usage_license(
        self,
        content_id: str,
        licensee_address: str,
        license_terms: Dict[str, Any],
        price_wei: int,
        duration_seconds: int
    ) -> Tuple[str, int]:
        """Create a usage license on blockchain"""
        try:
            contract_address = self.contract_addresses.get(ContractType.USAGE_LICENSE)
            if not contract_address:
                raise TransactionError("Usage license contract not deployed")
            
            contract = self.contracts.get(contract_address)
            if not contract:
                contract = self.w3.eth.contract(
                    address=contract_address,
                    abi=self.contract_abis[ContractType.USAGE_LICENSE]
                )
                self.contracts[contract_address] = contract
            
            # Prepare license terms
            terms_json = json.dumps(license_terms, sort_keys=True)
            expiry = int((datetime.utcnow() + timedelta(seconds=duration_seconds)).timestamp())
            
            # Build transaction
            function = contract.functions.createLicense(
                content_id,
                licensee_address,
                terms_json,
                expiry
            )
            
            # Build transaction with payment
            transaction = function.build_transaction({
                'from': self.account.address,
                'value': price_wei,
                'gas': 200000,
                'gasPrice': self.w3.to_wei(20, 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status != 1:
                raise TransactionError(f"License creation failed: {receipt}")
            
            license_id = self._extract_license_id(receipt)
            
            logger.info(f"Usage license created: {content_id} -> License {license_id}")
            return tx_hash.hex(), license_id
            
        except Exception as e:
            logger.error(f"License creation failed: {e}")
            raise TransactionError(f"Failed to create license: {e}")
    
    def _extract_registration_id(self, receipt) -> int:
        """Extract registration ID from transaction receipt"""
        try:
            # Parse logs to extract registration ID
            for log in receipt.logs:
                if log.topics[0].hex() == '0x1234...':  # Event signature hash
                    return int(log.data.hex(), 16)
            return 0
        except Exception:
            return 0
    
    def _extract_license_id(self, receipt) -> int:
        """Extract license ID from transaction receipt"""
        try:
            # Parse logs to extract license ID
            for log in receipt.logs:
                if log.topics[0].hex() == '0x5678...':  # Event signature hash
                    return int(log.data.hex(), 16)
            return 0
        except Exception:
            return 0
    
    def _get_contract_bytecode(self, contract_type: ContractType) -> str:
        """Get contract bytecode for deployment"""
        # In production, load from compiled contract artifacts
        bytecodes = {
            ContractType.COPYRIGHT_REGISTRY: "0x608060405234801561001057600080fd5b50...",
            ContractType.CONTENT_AUTHENTICITY: "0x608060405234801561001057600080fd5b50...",
            ContractType.USAGE_LICENSE: "0x608060405234801561001057600080fd5b50...",
        }
        return bytecodes.get(contract_type, "")
    
    def _get_copyright_registry_abi(self) -> List[Dict[str, Any]]:
        """Get Copyright Registry contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "contentHash", "type": "string"},
                    {"name": "metadata", "type": "string"},
                    {"name": "owner", "type": "address"},
                    {"name": "rights", "type": "string"},
                    {"name": "timestamp", "type": "uint256"}
                ],
                "name": "registerCopyright",
                "outputs": [{"name": "registrationId", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "registrationId", "type": "uint256"},
                    {"indexed": True, "name": "owner", "type": "address"},
                    {"indexed": False, "name": "contentHash", "type": "string"}
                ],
                "name": "CopyrightRegistered",
                "type": "event"
            }
        ]
    
    def _get_content_authenticity_abi(self) -> List[Dict[str, Any]]:
        """Get Content Authenticity contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "contentHash", "type": "string"},
                    {"name": "signature", "type": "string"},
                    {"name": "creator", "type": "address"}
                ],
                "name": "verifyAuthenticity",
                "outputs": [{"name": "isAuthentic", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _get_usage_license_abi(self) -> List[Dict[str, Any]]:
        """Get Usage License contract ABI"""
        return [
            {
                "inputs": [
                    {"name": "contentId", "type": "string"},
                    {"name": "licensee", "type": "address"},
                    {"name": "terms", "type": "string"},
                    {"name": "expiry", "type": "uint256"}
                ],
                "name": "createLicense",
                "outputs": [{"name": "licenseId", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
    
    def _get_royalty_distribution_abi(self) -> List[Dict[str, Any]]:
        """Get Royalty Distribution contract ABI"""
        return []
    
    def _get_ownership_transfer_abi(self) -> List[Dict[str, Any]]:
        """Get Ownership Transfer contract ABI"""
        return []
    
    def _get_access_control_abi(self) -> List[Dict[str, Any]]:
        """Get Access Control contract ABI"""
        return []


class GasOptimizer:
    """Gas optimization utilities for smart contracts"""
    
    @staticmethod
    def estimate_optimal_gas_price(w3: Web3, priority: str = "standard") -> int:
        """Estimate optimal gas price based on network conditions"""
        try:
            # Get gas price from network
            current_gas_price = w3.eth.gas_price
            
            # Apply priority multipliers
            multipliers = {
                "slow": 0.8,
                "standard": 1.0,
                "fast": 1.2,
                "fastest": 1.5
            }
            
            multiplier = multipliers.get(priority, 1.0)
            optimal_price = int(current_gas_price * multiplier)
            
            return optimal_price
            
        except Exception as e:
            logger.warning(f"Gas price estimation failed: {e}")
            # Return default gas price in wei (20 gwei)
            return 20000000000
    
    @staticmethod
    def batch_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch multiple transactions to reduce gas costs"""
        # Implementation for transaction batching
        return transactions


# Export classes
__all__ = [
    'ContractType',
    'NetworkConfig',
    'ContractDeploymentConfig',
    'SmartContractManager',
    'GasOptimizer'
]
