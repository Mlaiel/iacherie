"""
Blockchain Content Protection - Main Index
Professional blockchain integration hub for all content protection services

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

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

# Import all blockchain components
from .config import BlockchainConfig, Environment
from .smart_contracts import SmartContractManager, ContractType, ContractDeploymentConfig
from .nft_management import NFTManager, NFTMetadata, NFTCreationConfig
from .distributed_ledger import DistributedLedgerManager, LedgerRecord
from .crypto_payments import CryptoPaymentProcessor, PaymentMethod, PaymentConfig
from .defi_integration import DeFiIntegration, LiquidityPool, DeFiProtocol
from .monitoring import BlockchainMonitor, TransactionStatus, MonitoringAlert
from .timestamping import CryptographicTimestamping, TimestampProof, ContentFingerprint
from .validation import BlockchainValidator, ValidationReport, ValidationLevel
from .contract_templates import SmartContractTemplates, ContractTemplate, ContractConfig
from .exceptions import (
    BlockchainError,
    NetworkError,
    ContractError,
    TransactionError,
    SecurityError,
    NFTError,
    DeFiError
)

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Blockchain service status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class BlockchainServiceConfig:
    """Complete blockchain service configuration"""
    environment: Environment
    networks: Dict[str, Dict[str, Any]]
    smart_contracts: Dict[str, Any]
    nft_settings: Dict[str, Any]
    payment_processors: Dict[str, Any]
    defi_protocols: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    timestamping_config: Dict[str, Any]
    validation_config: Dict[str, Any]
    security_settings: Dict[str, Any]


class BlockchainContentProtectionHub:
    """
    Professional blockchain content protection hub
    Central orchestrator for all blockchain-based content protection services
    """
    
    def __init__(self, config: BlockchainServiceConfig):
        self.config = config
        self.status = ServiceStatus.INITIALIZING
        self.services = {}
        self.session_id = None
        
        # Core service managers
        self.contract_manager: Optional[SmartContractManager] = None
        self.nft_manager: Optional[NFTManager] = None
        self.ledger_manager: Optional[DistributedLedgerManager] = None
        self.payment_processor: Optional[CryptoPaymentProcessor] = None
        self.defi_integration: Optional[DeFiIntegration] = None
        self.monitor: Optional[BlockchainMonitor] = None
        self.timestamping: Optional[CryptographicTimestamping] = None
        self.validator: Optional[BlockchainValidator] = None
        
        # Service registry
        self.registered_contracts = {}
        self.active_sessions = {}
        self.performance_metrics = {}
        
    async def initialize(self) -> bool:
        """
        Initialize all blockchain services
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Blockchain Content Protection Hub...")
            
            # Initialize core services
            await self._initialize_core_services()
            
            # Initialize contract manager
            await self._initialize_contract_manager()
            
            # Initialize NFT manager
            await self._initialize_nft_manager()
            
            # Initialize payment processing
            await self._initialize_payment_processor()
            
            # Initialize DeFi integration
            await self._initialize_defi_integration()
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Initialize timestamping
            await self._initialize_timestamping()
            
            # Initialize validation
            await self._initialize_validation()
            
            # Perform health checks
            health_status = await self._perform_health_checks()
            
            if health_status:
                self.status = ServiceStatus.ACTIVE
                logger.info("Blockchain Content Protection Hub initialized successfully")
                return True
            else:
                self.status = ServiceStatus.ERROR
                logger.error("Blockchain Content Protection Hub initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Hub initialization error: {e}")
            self.status = ServiceStatus.ERROR
            return False
    
    async def _initialize_core_services(self):
        """Initialize core blockchain services"""
        try:
            # Create blockchain configuration
            blockchain_config = BlockchainConfig(
                environment=self.config.environment,
                ethereum_config=self.config.networks.get("ethereum", {}),
                polygon_config=self.config.networks.get("polygon", {}),
                bsc_config=self.config.networks.get("binance_smart_chain", {}),
                ipfs_config=self.config.networks.get("ipfs", {}),
                arweave_config=self.config.networks.get("arweave", {})
            )
            
            self.services["blockchain_config"] = blockchain_config
            logger.info("Core services initialized")
            
        except Exception as e:
            logger.error(f"Core services initialization failed: {e}")
            raise
    
    async def _initialize_contract_manager(self):
        """Initialize smart contract manager"""
        try:
            contract_config = self.config.smart_contracts
            
            self.contract_manager = SmartContractManager(contract_config)
            await self.contract_manager.initialize()
            
            self.services["contract_manager"] = self.contract_manager
            logger.info("Smart contract manager initialized")
            
        except Exception as e:
            logger.error(f"Contract manager initialization failed: {e}")
            raise
    
    async def _initialize_nft_manager(self):
        """Initialize NFT manager"""
        try:
            nft_config = self.config.nft_settings
            
            self.nft_manager = NFTManager(nft_config)
            await self.nft_manager.initialize()
            
            self.services["nft_manager"] = self.nft_manager
            logger.info("NFT manager initialized")
            
        except Exception as e:
            logger.error(f"NFT manager initialization failed: {e}")
            raise
    
    async def _initialize_payment_processor(self):
        """Initialize payment processor"""
        try:
            payment_config = PaymentConfig(**self.config.payment_processors)
            
            self.payment_processor = CryptoPaymentProcessor(payment_config)
            await self.payment_processor.initialize()
            
            self.services["payment_processor"] = self.payment_processor
            logger.info("Payment processor initialized")
            
        except Exception as e:
            logger.error(f"Payment processor initialization failed: {e}")
            raise
    
    async def _initialize_defi_integration(self):
        """Initialize DeFi integration"""
        try:
            defi_config = self.config.defi_protocols
            
            self.defi_integration = DeFiIntegration(defi_config)
            await self.defi_integration.initialize()
            
            self.services["defi_integration"] = self.defi_integration
            logger.info("DeFi integration initialized")
            
        except Exception as e:
            logger.error(f"DeFi integration initialization failed: {e}")
            raise
    
    async def _initialize_monitoring(self):
        """Initialize blockchain monitoring"""
        try:
            monitoring_config = self.config.monitoring_config
            
            self.monitor = BlockchainMonitor(monitoring_config)
            await self.monitor.start_monitoring()
            
            self.services["monitor"] = self.monitor
            logger.info("Blockchain monitoring initialized")
            
        except Exception as e:
            logger.error(f"Monitoring initialization failed: {e}")
            raise
    
    async def _initialize_timestamping(self):
        """Initialize cryptographic timestamping"""
        try:
            timestamping_config = self.config.timestamping_config
            
            self.timestamping = CryptographicTimestamping(timestamping_config)
            
            self.services["timestamping"] = self.timestamping
            logger.info("Timestamping service initialized")
            
        except Exception as e:
            logger.error(f"Timestamping initialization failed: {e}")
            raise
    
    async def _initialize_validation(self):
        """Initialize blockchain validation"""
        try:
            validation_config = self.config.validation_config
            
            self.validator = BlockchainValidator(validation_config)
            
            self.services["validator"] = self.validator
            logger.info("Blockchain validator initialized")
            
        except Exception as e:
            logger.error(f"Validator initialization failed: {e}")
            raise
    
    async def _perform_health_checks(self) -> bool:
        """Perform comprehensive health checks on all services"""
        try:
            health_results = {}
            
            # Check smart contract manager
            if self.contract_manager:
                health_results["contracts"] = await self._check_contract_health()
            
            # Check NFT manager
            if self.nft_manager:
                health_results["nft"] = await self._check_nft_health()
            
            # Check payment processor
            if self.payment_processor:
                health_results["payments"] = await self._check_payment_health()
            
            # Check DeFi integration
            if self.defi_integration:
                health_results["defi"] = await self._check_defi_health()
            
            # Check monitoring
            if self.monitor:
                health_results["monitoring"] = await self._check_monitoring_health()
            
            # All checks must pass
            return all(health_results.values())
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def _check_contract_health(self) -> bool:
        """Check smart contract manager health"""
        try:
            # Test contract deployment capability
            return await self.contract_manager.test_connection()
        except Exception:
            return False
    
    async def _check_nft_health(self) -> bool:
        """Check NFT manager health"""
        try:
            # Test NFT operations
            return await self.nft_manager.test_connection()
        except Exception:
            return False
    
    async def _check_payment_health(self) -> bool:
        """Check payment processor health"""
        try:
            # Test payment processing capability
            return await self.payment_processor.test_connection()
        except Exception:
            return False
    
    async def _check_defi_health(self) -> bool:
        """Check DeFi integration health"""
        try:
            # Test DeFi protocol connectivity
            return await self.defi_integration.test_protocols()
        except Exception:
            return False
    
    async def _check_monitoring_health(self) -> bool:
        """Check monitoring service health"""
        try:
            # Test monitoring capabilities
            return self.monitor.is_healthy()
        except Exception:
            return False
    
    # Public API Methods
    
    async def register_content_copyright(
        self,
        content_path: str,
        metadata: Dict[str, Any],
        license_terms: Dict[str, Any],
        network: str = "ethereum"
    ) -> Dict[str, Any]:
        """
        Register content copyright on blockchain
        
        Args:
            content_path: Path to content file
            metadata: Content metadata
            license_terms: Licensing terms
            network: Target blockchain network
            
        Returns:
            Registration result with transaction details
        """
        try:
            if not self.contract_manager:
                raise BlockchainError("Contract manager not initialized")
            
            # Create content fingerprint
            fingerprint = await self.timestamping.create_content_fingerprint(
                content_path,
                metadata.get("content_id"),
                metadata
            )
            
            # Create timestamp proof
            proof = await self.timestamping.create_timestamp_proof(fingerprint)
            
            # Deploy or use existing copyright registry contract
            contract_address = await self._get_or_deploy_copyright_contract(network)
            
            # Register copyright on blockchain
            registration_result = await self.contract_manager.register_copyright(
                contract_address,
                fingerprint.combined_hash,
                metadata,
                license_terms,
                proof
            )
            
            return {
                "success": True,
                "content_hash": fingerprint.combined_hash,
                "transaction_hash": registration_result.get("transaction_hash"),
                "copyright_id": registration_result.get("copyright_id"),
                "timestamp_proof": proof.to_dict(),
                "network": network,
                "contract_address": contract_address
            }
            
        except Exception as e:
            logger.error(f"Copyright registration failed: {e}")
            raise BlockchainError(f"Copyright registration failed: {e}")
    
    async def create_content_nft(
        self,
        content_path: str,
        metadata: NFTMetadata,
        network: str = "ethereum"
    ) -> Dict[str, Any]:
        """
        Create NFT for content protection
        
        Args:
            content_path: Path to content file
            metadata: NFT metadata
            network: Target blockchain network
            
        Returns:
            NFT creation result
        """
        try:
            if not self.nft_manager:
                raise BlockchainError("NFT manager not initialized")
            
            # Create NFT configuration
            nft_config = NFTCreationConfig(
                metadata=metadata,
                network=network,
                royalty_percentage=metadata.royalty_percentage or 250,  # 2.5%
                max_supply=1  # Unique content NFT
            )
            
            # Create NFT
            nft_result = await self.nft_manager.create_nft(
                content_path,
                nft_config
            )
            
            return {
                "success": True,
                "token_id": nft_result.token_id,
                "contract_address": nft_result.contract_address,
                "transaction_hash": nft_result.transaction_hash,
                "metadata_uri": nft_result.metadata_uri,
                "network": network
            }
            
        except Exception as e:
            logger.error(f"NFT creation failed: {e}")
            raise NFTError(f"NFT creation failed: {e}")
    
    async def process_content_payment(
        self,
        content_id: str,
        payment_amount: float,
        currency: str,
        payment_method: PaymentMethod,
        recipient_address: str
    ) -> Dict[str, Any]:
        """
        Process payment for content usage
        
        Args:
            content_id: Content identifier
            payment_amount: Payment amount
            currency: Payment currency
            payment_method: Payment method
            recipient_address: Recipient wallet address
            
        Returns:
            Payment processing result
        """
        try:
            if not self.payment_processor:
                raise BlockchainError("Payment processor not initialized")
            
            # Process payment
            payment_result = await self.payment_processor.process_payment(
                amount=payment_amount,
                currency=currency,
                method=payment_method,
                recipient=recipient_address,
                metadata={"content_id": content_id}
            )
            
            return {
                "success": True,
                "payment_id": payment_result.payment_id,
                "transaction_hash": payment_result.transaction_hash,
                "amount": payment_amount,
                "currency": currency,
                "status": payment_result.status.value
            }
            
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            raise BlockchainError(f"Payment processing failed: {e}")
    
    async def validate_content_integrity(
        self,
        content_path: str,
        original_hash: str,
        validation_level: ValidationLevel = ValidationLevel.STANDARD
    ) -> ValidationReport:
        """
        Validate content integrity using blockchain validation
        
        Args:
            content_path: Path to content file
            original_hash: Original content hash
            validation_level: Validation strictness level
            
        Returns:
            Validation report
        """
        try:
            if not self.validator:
                raise BlockchainError("Validator not initialized")
            
            # Perform content integrity validation
            integrity_check = await self.validator.validate_content_integrity(
                content_path,
                original_hash,
                validation_level
            )
            
            # Create validation report
            report = ValidationReport(
                validation_id=f"content_{int(datetime.utcnow().timestamp())}",
                timestamp=datetime.utcnow(),
                level=validation_level,
                overall_result=ValidationResult.VALID if integrity_check.is_intact else ValidationResult.INVALID,
                score=integrity_check.confidence,
                checks_performed=["content_hash", "file_integrity"],
                passed_checks=["content_hash"] if integrity_check.is_intact else [],
                failed_checks=[] if integrity_check.is_intact else ["content_hash"],
                warnings=[],
                errors=[] if integrity_check.is_intact else ["Content integrity compromised"],
                metadata={
                    "original_hash": original_hash,
                    "current_hash": integrity_check.current_hash,
                    "modifications": integrity_check.modifications_detected
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            raise BlockchainError(f"Content validation failed: {e}")
    
    async def create_timestamp_proof(
        self,
        content_path: str,
        metadata: Dict[str, Any]
    ) -> TimestampProof:
        """
        Create cryptographic timestamp proof for content
        
        Args:
            content_path: Path to content file
            metadata: Content metadata
            
        Returns:
            Timestamp proof
        """
        try:
            if not self.timestamping:
                raise BlockchainError("Timestamping service not initialized")
            
            # Create content fingerprint
            fingerprint = await self.timestamping.create_content_fingerprint(
                content_path,
                metadata.get("content_id", "unknown"),
                metadata
            )
            
            # Create timestamp proof
            proof = await self.timestamping.create_timestamp_proof(fingerprint)
            
            return proof
            
        except Exception as e:
            logger.error(f"Timestamp proof creation failed: {e}")
            raise BlockchainError(f"Timestamp proof creation failed: {e}")
    
    async def monitor_content_usage(
        self,
        content_id: str,
        monitoring_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Monitor content usage across blockchain networks
        
        Args:
            content_id: Content identifier
            monitoring_period: Monitoring duration
            
        Returns:
            Usage monitoring results
        """
        try:
            if not self.monitor:
                raise BlockchainError("Monitor not initialized")
            
            # Start content monitoring
            monitoring_id = await self.monitor.start_content_monitoring(
                content_id,
                monitoring_period
            )
            
            return {
                "success": True,
                "monitoring_id": monitoring_id,
                "content_id": content_id,
                "monitoring_period": monitoring_period.total_seconds(),
                "start_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content monitoring failed: {e}")
            raise BlockchainError(f"Content monitoring failed: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all blockchain services
        
        Returns:
            Service status report
        """
        try:
            status_report = {
                "hub_status": self.status.value,
                "services": {},
                "performance_metrics": self.performance_metrics,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Check each service status
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, "get_status"):
                        status_report["services"][service_name] = await service.get_status()
                    else:
                        status_report["services"][service_name] = "active"
                except Exception as e:
                    status_report["services"][service_name] = f"error: {e}"
            
            return status_report
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "hub_status": "error",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def _get_or_deploy_copyright_contract(self, network: str) -> str:
        """Get existing or deploy new copyright registry contract"""
        try:
            # Check if contract already deployed for this network
            contract_key = f"copyright_registry_{network}"
            
            if contract_key in self.registered_contracts:
                return self.registered_contracts[contract_key]
            
            # Deploy new contract
            template = SmartContractTemplates.get_copyright_registry_contract()
            
            deployment_result = await self.contract_manager.deploy_contract(
                contract_source=template,
                contract_name="ContentCopyrightRegistry",
                network=network,
                constructor_args=[]
            )
            
            contract_address = deployment_result["contract_address"]
            self.registered_contracts[contract_key] = contract_address
            
            logger.info(f"Copyright registry deployed on {network}: {contract_address}")
            
            return contract_address
            
        except Exception as e:
            logger.error(f"Copyright contract deployment failed: {e}")
            raise ContractError(f"Copyright contract deployment failed: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown all blockchain services"""
        try:
            logger.info("Shutting down Blockchain Content Protection Hub...")
            
            # Stop monitoring
            if self.monitor:
                await self.monitor.stop_monitoring()
            
            # Close all service connections
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, "close"):
                        await service.close()
                    elif hasattr(service, "shutdown"):
                        await service.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down {service_name}: {e}")
            
            self.status = ServiceStatus.DISABLED
            logger.info("Blockchain Content Protection Hub shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Factory function for easy initialization
async def create_blockchain_hub(
    config_path: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None
) -> BlockchainContentProtectionHub:
    """
    Factory function to create and initialize blockchain hub
    
    Args:
        config_path: Path to configuration file
        config_dict: Configuration dictionary
        
    Returns:
        Initialized BlockchainContentProtectionHub
    """
    try:
        # Load configuration
        if config_path:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        elif config_dict:
            config_data = config_dict
        else:
            # Use default configuration
            config_data = _get_default_config()
        
        # Create service configuration
        service_config = BlockchainServiceConfig(**config_data)
        
        # Create and initialize hub
        hub = BlockchainContentProtectionHub(service_config)
        
        success = await hub.initialize()
        
        if not success:
            raise BlockchainError("Failed to initialize blockchain hub")
        
        return hub
        
    except Exception as e:
        logger.error(f"Hub creation failed: {e}")
        raise BlockchainError(f"Hub creation failed: {e}")


def _get_default_config() -> Dict[str, Any]:
    """Get default configuration for blockchain services"""
    return {
        "environment": Environment.DEVELOPMENT.value,
        "networks": {
            "ethereum": {
                "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                "chain_id": 1,
                "gas_price_gwei": 20
            },
            "polygon": {
                "rpc_url": "https://polygon-rpc.com/",
                "chain_id": 137,
                "gas_price_gwei": 30
            }
        },
        "smart_contracts": {
            "deployment_gas_limit": 5000000,
            "confirmation_blocks": 6
        },
        "nft_settings": {
            "default_royalty": 250,  # 2.5%
            "metadata_storage": "ipfs"
        },
        "payment_processors": {
            "supported_currencies": ["ETH", "MATIC", "USDC"],
            "transaction_timeout": 300
        },
        "defi_protocols": {
            "enabled_protocols": ["uniswap", "aave"],
            "slippage_tolerance": 0.5
        },
        "monitoring_config": {
            "check_interval": 60,
            "alert_thresholds": {
                "transaction_failure_rate": 0.05,
                "gas_price_spike": 2.0
            }
        },
        "timestamping_config": {
            "default_service": "blockchain_proof",
            "retention_period": 2592000  # 30 days
        },
        "validation_config": {
            "default_level": "standard",
            "cache_results": True,
            "cache_ttl": 3600
        },
        "security_settings": {
            "encryption_enabled": True,
            "signature_verification": True,
            "rate_limiting": True
        }
    }

from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Core blockchain service
from . import (
    BlockchainService,
    BlockchainCertificate,
    ContentHash,
    OwnershipRecord,
    BlockchainNetwork,
    CertificationType,
    TransactionStatus,
    get_blockchain_service
)

# Smart contract management
from .smart_contracts import (
    SmartContractManager,
    ContractType,
    NetworkConfig,
    ContractDeploymentConfig,
    GasOptimizer
)

# NFT management
from .nft_management import (
    NFTManager,
    NFTStandard,
    NFTMarketplace,
    NFTMetadata,
    CollectionManager,
    RarityCalculator
)

# Cryptocurrency payments
from .crypto_payments import (
    CryptoPaymentProcessor,
    SupportedCryptocurrency,
    PaymentStatus,
    PaymentGateway,
    WalletManager,
    TransactionMonitor
)

# DeFi integration
from .defi_integration import (
    DeFiManager,
    DeFiProtocol,
    LiquidityStrategy,
    StakingType,
    YieldFarmingManager,
    LiquidityPoolManager
)

# Distributed ledger technology
from .distributed_ledger import (
    DLTManager,
    DLTNetwork,
    StorageClass,
    ContentMetadata,
    IPFSClient,
    ArweaveClient,
    HyperledgerClient
)

# Exception handling
from .exceptions import (
    BlockchainError,
    BlockchainConnectionError,
    ContractDeploymentError,
    ContractExecutionError,
    TransactionError,
    InsufficientFundsError,
    NFTMintingError,
    NFTTransferError,
    DLTStorageError,
    CryptoPaymentError,
    DeFiIntegrationError,
    Web3ProviderError,
    GasEstimationError,
    SignatureValidationError,
    BlockchainSyncError
)

logger = logging.getLogger(__name__)


class BlockchainModuleManager:
    """
    Central manager for all blockchain functionality
    Provides unified access to all blockchain services
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.blockchain_service: Optional[BlockchainService] = None
        self.smart_contract_manager: Optional[SmartContractManager] = None
        self.nft_manager: Optional[NFTManager] = None
        self.crypto_payment_processor: Optional[CryptoPaymentProcessor] = None
        self.defi_manager: Optional[DeFiManager] = None
        self.dlt_manager: Optional[DLTManager] = None
        self.initialized = False
        
        logger.info("Blockchain Module Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize all blockchain components"""
        try:
            logger.info("Initializing blockchain module components...")
            
            # Initialize core blockchain service
            self.blockchain_service = await get_blockchain_service()
            if not await self.blockchain_service.initialize():
                logger.error("Failed to initialize blockchain service")
                return False
            
            # Initialize smart contract manager
            network_config = self.config.get('network_config', {})
            private_key = self.config.get('private_key')
            
            if network_config and private_key:
                self.smart_contract_manager = SmartContractManager(network_config, private_key)
                await self.smart_contract_manager.initialize()
            
            # Initialize NFT manager
            nft_config = self.config.get('nft_config', {})
            if nft_config:
                self.nft_manager = NFTManager(nft_config)
                await self.nft_manager.initialize()
            
            # Initialize crypto payment processor
            payment_config = self.config.get('payment_config', {})
            if payment_config:
                self.crypto_payment_processor = CryptoPaymentProcessor(payment_config)
                await self.crypto_payment_processor.initialize()
            
            # Initialize DeFi manager
            defi_config = self.config.get('defi_config', {})
            if defi_config:
                self.defi_manager = DeFiManager(defi_config)
                await self.defi_manager.initialize()
            
            # Initialize DLT manager
            dlt_config = self.config.get('dlt_config', {})
            if dlt_config:
                self.dlt_manager = DLTManager(dlt_config)
                await self.dlt_manager.initialize()
            
            self.initialized = True
            logger.info("Blockchain module fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain module: {e}")
            return False
    
    async def register_content_protection(
        self,
        content_id: str,
        content_path: str,
        owner_info: Dict[str, Any],
        protection_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete content protection registration
        Combines blockchain registration, NFT minting, and DLT storage
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            results = {}
            
            # 1. Register copyright on blockchain
            if self.blockchain_service:
                certificate_id = await self.blockchain_service.register_content_ownership(
                    content_id=content_id,
                    content_path=content_path,
                    owner_info=owner_info,
                    certification_type=CertificationType.COPYRIGHT_REGISTRATION
                )
                results['copyright_certificate'] = certificate_id
            
            # 2. Store content on distributed ledger
            if self.dlt_manager:
                storage_results = await self.dlt_manager.store_content_multi_network(
                    content_path=content_path,
                    metadata={'content_id': content_id, 'owner': owner_info}
                )
                results['storage'] = storage_results
            
            # 3. Mint NFT if requested
            if protection_options and protection_options.get('mint_nft') and self.nft_manager:
                nft_result = await self.nft_manager.mint_content_nft(
                    content_id=content_id,
                    content_path=content_path,
                    owner_address=owner_info.get('address'),
                    collection_name=protection_options.get('collection_name', 'Content Protection')
                )
                results['nft'] = nft_result
            
            # 4. Create timestamp proof
            if self.blockchain_service:
                timestamp_cert = await self.blockchain_service.create_timestamp_proof(
                    content_id=content_id,
                    content_path=content_path
                )
                results['timestamp_proof'] = timestamp_cert
            
            logger.info(f"Content protection registered: {content_id}")
            return {
                'success': True,
                'content_id': content_id,
                'protection_results': results,
                'registered_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content protection registration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'content_id': content_id
            }
    
    async def verify_content_authenticity(
        self,
        content_id: str,
        content_path: str
    ) -> Dict[str, Any]:
        """Complete content authenticity verification"""
        try:
            if not self.initialized:
                await self.initialize()
            
            verification_results = {}
            
            # Blockchain verification
            if self.blockchain_service:
                blockchain_result = await self.blockchain_service.verify_content_authenticity(
                    content_id=content_id,
                    content_path=content_path
                )
                verification_results['blockchain'] = blockchain_result
            
            # DLT verification
            if self.dlt_manager:
                dlt_result = await self.dlt_manager.verify_content_integrity(
                    content_id=content_id,
                    content_path=content_path
                )
                verification_results['distributed_ledger'] = dlt_result
            
            # Smart contract verification
            if self.smart_contract_manager:
                try:
                    # Generate content hash for verification
                    with open(content_path, 'rb') as f:
                        content_data = f.read()
                    content_hash = hashlib.sha256(content_data).hexdigest()
                    
                    # Verify via smart contract
                    contract_result = await self.smart_contract_manager.verify_content_authenticity(
                        content_hash=content_hash,
                        signature="",  # Would be actual signature
                        creator_address=""  # Would be actual creator address
                    )
                    verification_results['smart_contract'] = contract_result
                except Exception as e:
                    logger.warning(f"Smart contract verification failed: {e}")
            
            # Overall authenticity score
            authentic_checks = sum(1 for result in verification_results.values() 
                                 if isinstance(result, dict) and result.get('authentic', False))
            total_checks = len(verification_results)
            authenticity_score = (authentic_checks / total_checks * 100) if total_checks > 0 else 0
            
            return {
                'content_id': content_id,
                'authenticity_score': authenticity_score,
                'is_authentic': authenticity_score >= 75,  # 75% threshold
                'verification_results': verification_results,
                'verified_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content verification failed: {e}")
            return {
                'content_id': content_id,
                'authenticity_score': 0,
                'is_authentic': False,
                'error': str(e)
            }
    
    async def process_content_payment(
        self,
        content_id: str,
        amount: float,
        currency: SupportedCryptocurrency,
        payer_address: str,
        license_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process cryptocurrency payment for content licensing"""
        try:
            if not self.crypto_payment_processor:
                raise CryptoPaymentError("Payment processor not initialized")
            
            # Process payment
            payment_result = await self.crypto_payment_processor.process_payment(
                payment_id=f"content_{content_id}_{secrets.token_hex(8)}",
                amount=amount,
                currency=currency,
                from_address=payer_address,
                metadata={'content_id': content_id, 'license_terms': license_terms}
            )
            
            # Create usage license if payment successful
            if payment_result.get('status') == PaymentStatus.CONFIRMED and self.smart_contract_manager:
                try:
                    license_result = await self.smart_contract_manager.create_usage_license(
                        content_id=content_id,
                        licensee_address=payer_address,
                        license_terms=license_terms,
                        price_wei=int(amount * 10**18),  # Convert to wei
                        duration_seconds=license_terms.get('duration_days', 30) * 24 * 3600
                    )
                    payment_result['license'] = license_result
                except Exception as e:
                    logger.warning(f"License creation failed: {e}")
            
            return payment_result
            
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'content_id': content_id
            }
    
    async def get_module_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all blockchain components"""
        try:
            status = {
                'initialized': self.initialized,
                'timestamp': datetime.utcnow().isoformat(),
                'components': {}
            }
            
            # Check each component
            components = {
                'blockchain_service': self.blockchain_service,
                'smart_contract_manager': self.smart_contract_manager,
                'nft_manager': self.nft_manager,
                'crypto_payment_processor': self.crypto_payment_processor,
                'defi_manager': self.defi_manager,
                'dlt_manager': self.dlt_manager
            }
            
            for name, component in components.items():
                if component:
                    status['components'][name] = {
                        'active': True,
                        'status': 'operational'
                    }
                    
                    # Get specific status if available
                    if hasattr(component, 'get_status'):
                        try:
                            component_status = await component.get_status()
                            status['components'][name].update(component_status)
                        except Exception as e:
                            status['components'][name]['status'] = f'error: {e}'
                else:
                    status['components'][name] = {
                        'active': False,
                        'status': 'not_initialized'
                    }
            
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                'initialized': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Graceful shutdown of all blockchain components"""
        try:
            logger.info("Shutting down blockchain module...")
            
            if self.blockchain_service:
                await self.blockchain_service.shutdown()
            
            if self.dlt_manager and hasattr(self.dlt_manager, 'shutdown'):
                await self.dlt_manager.shutdown()
            
            if self.crypto_payment_processor and hasattr(self.crypto_payment_processor, 'shutdown'):
                await self.crypto_payment_processor.shutdown()
            
            if self.defi_manager and hasattr(self.defi_manager, 'shutdown'):
                await self.defi_manager.shutdown()
            
            self.initialized = False
            logger.info("Blockchain module shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Global module instance
blockchain_module = BlockchainModuleManager()


async def get_blockchain_module(config: Optional[Dict[str, Any]] = None) -> BlockchainModuleManager:
    """Get the global blockchain module instance"""
    if config and not blockchain_module.initialized:
        blockchain_module.config.update(config)
        await blockchain_module.initialize()
    
    return blockchain_module


# Export all public interfaces
__all__ = [
    # Core services
    'BlockchainService',
    'BlockchainModuleManager',
    'get_blockchain_module',
    'get_blockchain_service',
    
    # Smart contracts
    'SmartContractManager',
    'ContractType',
    'NetworkConfig',
    'GasOptimizer',
    
    # NFT management
    'NFTStandard',
    'NFTMarketplace',
    
    # Payments
    'SupportedCryptocurrency',
    'PaymentStatus',
    
    # DeFi
    'DeFiProtocol',
    'LiquidityStrategy',
    'StakingType',
    
    # DLT
    'DLTNetwork',
    'StorageClass',
    
    # Data models
    'BlockchainCertificate',
    'ContentHash',
    'OwnershipRecord',
    'BlockchainNetwork',
    'CertificationType',
    'TransactionStatus',
    
    # Exceptions
    'BlockchainError',
    'BlockchainConnectionError',
    'ContractDeploymentError',
    'TransactionError',
    'NFTMintingError',
    'CryptoPaymentError',
    'DeFiIntegrationError',
    'DLTStorageError'
]
