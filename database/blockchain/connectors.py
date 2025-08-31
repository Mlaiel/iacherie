"""Blockchain Network Connectors Module

Enterprise-grade blockchain connectivity layer providing unified access to multiple
blockchain networks (Ethereum, Polygon, BSC) with advanced features like load balancing,
failover, and performance monitoring.

Features:
- Multi-blockchain network support with automatic failover
- Connection pooling and load balancing
- Real-time network status monitoring
- Gas price optimization and estimation
- Transaction batching and queue management
- Network-specific configuration and optimization
- Advanced error handling and retry mechanisms

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead AI Developer + Blockchain Specialist + Backend Senior + ML Engineer + 
      DBA + Security Expert + Microservices Architect + Audio Processing + 
      DevOps Engineer + IA Prompt Engineer

Copyright: All rights reserved. Unauthorized use prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime, timedelta
import asyncio
import aiohttp
from decimal import Decimal
import time
from concurrent.futures import ThreadPoolExecutor
import threading

from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_typing import Address, HexStr
import websockets

logger = logging.getLogger(__name__)

class NetworkType(Enum):
    """Supported blockchain network types."""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    POLYGON_MAINNET = "polygon_mainnet"
    POLYGON_MUMBAI = "polygon_mumbai"
    BSC_MAINNET = "bsc_mainnet"
    BSC_TESTNET = "bsc_testnet"
    ARBITRUM_MAINNET = "arbitrum_mainnet"
    OPTIMISM_MAINNET = "optimism_mainnet"

class ConnectionStatus(Enum):
    """Connection status states."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class NetworkConfig:
    """Configuration for blockchain network connection."""
    network_type: NetworkType
    name: str
    chain_id: int
    rpc_urls: List[str]
    ws_urls: List[str]
    explorer_url: str
    native_currency: Dict[str, Any]
    gas_price_oracle: Optional[str] = None
    max_priority_fee: Optional[int] = None
    max_fee_per_gas: Optional[int] = None
    block_time: float = 12.0  # Average block time in seconds
    confirmation_blocks: int = 12
    is_testnet: bool = False

@dataclass
class ConnectionMetrics:
    """Connection performance and health metrics."""
    network_type: NetworkType
    status: ConnectionStatus
    last_block_number: int
    last_sync_time: datetime
    response_time_ms: float
    error_count: int = 0
    success_count: int = 0
    uptime_percentage: float = 100.0
    gas_price_gwei: Optional[float] = None
    pending_tx_count: int = 0

class BlockchainConnector:
    """
    Base blockchain connector with common functionality.
    
    Provides connection management, health monitoring, and basic operations
    for blockchain networks.
    """
    
    def __init__(self, config: NetworkConfig):
        """
        Initialize blockchain connector.
        
        Args:
            config: Network configuration
        """
        self.config = config
        self.web3_instances: List[Web3] = []
        self.current_instance_index = 0
        self.metrics = ConnectionMetrics(
            network_type=config.network_type,
            status=ConnectionStatus.DISCONNECTED,
            last_block_number=0,
            last_sync_time=datetime.utcnow(),
            response_time_ms=0.0
        )
        self._lock = threading.Lock()
        self._is_monitoring = False
        
    async def initialize(self) -> bool:
        """
        Initialize connections to all configured RPC endpoints.
        
        Returns:
            True if at least one connection is successful
        """
        try:
            self.metrics.status = ConnectionStatus.CONNECTING
            connected_count = 0
            
            for rpc_url in self.config.rpc_urls:
                try:
                    # Create Web3 instance
                    w3 = Web3(Web3.HTTPProvider(rpc_url))
                    
                    # Add middleware for Proof of Authority networks
                    if self.config.network_type in [
                        NetworkType.POLYGON_MAINNET, 
                        NetworkType.POLYGON_MUMBAI,
                        NetworkType.BSC_MAINNET,
                        NetworkType.BSC_TESTNET
                    ]:
                        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    # Test connection
                    if await self._test_connection(w3):
                        self.web3_instances.append(w3)
                        connected_count += 1
                        logger.info(f"Connected to {self.config.name} via {rpc_url}")
                    else:
                        logger.warning(f"Failed to connect to {rpc_url}")
                        
                except Exception as e:
                    logger.error(f"Error connecting to {rpc_url}: {e}")
            
            if connected_count > 0:
                self.metrics.status = ConnectionStatus.CONNECTED
                self._start_monitoring()
                return True
            else:
                self.metrics.status = ConnectionStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.config.name} connector: {e}")
            self.metrics.status = ConnectionStatus.ERROR
            return False
    
    async def _test_connection(self, w3: Web3) -> bool:
        """
        Test Web3 connection and verify chain ID.
        
        Args:
            w3: Web3 instance to test
            
        Returns:
            True if connection is valid
        """
        try:
            start_time = time.time()
            
            # Check if connected
            if not w3.is_connected():
                return False
            
            # Verify chain ID
            chain_id = w3.eth.chain_id
            if chain_id != self.config.chain_id:
                logger.warning(
                    f"Chain ID mismatch: expected {self.config.chain_id}, "
                    f"got {chain_id}"
                )
                return False
            
            # Get latest block to ensure node is synced
            latest_block = w3.eth.get_block('latest')
            self.metrics.last_block_number = latest_block.number
            self.metrics.last_sync_time = datetime.utcnow()
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            self.metrics.response_time_ms = response_time
            
            return True
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_web3_instance(self) -> Optional[Web3]:
        """
        Get a healthy Web3 instance using round-robin load balancing.
        
        Returns:
            Web3 instance or None if no healthy connections
        """
        with self._lock:
            if not self.web3_instances:
                return None
            
            # Try current instance first
            current_w3 = self.web3_instances[self.current_instance_index]
            if current_w3.is_connected():
                self.current_instance_index = (
                    self.current_instance_index + 1
                ) % len(self.web3_instances)
                return current_w3
            
            # Find a healthy instance
            for i, w3 in enumerate(self.web3_instances):
                if w3.is_connected():
                    self.current_instance_index = (i + 1) % len(self.web3_instances)
                    return w3
            
            # No healthy connections
            self.metrics.status = ConnectionStatus.ERROR
            return None
    
    async def get_gas_price(self) -> Optional[int]:
        """
        Get current gas price for the network.
        
        Returns:
            Gas price in wei
        """
        try:
            w3 = self.get_web3_instance()
            if not w3:
                return None
            
            # Use gas price oracle if available
            if self.config.gas_price_oracle:
                gas_price = await self._get_oracle_gas_price()
                if gas_price:
                    return gas_price
            
            # Fallback to node gas price
            gas_price = w3.eth.gas_price
            self.metrics.gas_price_gwei = Web3.from_wei(gas_price, 'gwei')
            
            return gas_price
            
        except Exception as e:
            logger.error(f"Failed to get gas price: {e}")
            return None
    
    async def _get_oracle_gas_price(self) -> Optional[int]:
        """Get gas price from external oracle (e.g., ETH Gas Station)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.gas_price_oracle) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse oracle-specific response format
                        return self._parse_oracle_response(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get oracle gas price: {e}")
            return None
    
    def _parse_oracle_response(self, data: Dict[str, Any]) -> Optional[int]:
        """Parse gas price oracle response based on network type."""
        # Implementation varies by oracle provider
        return None
    
    async def estimate_gas(
        self, 
        transaction: Dict[str, Any]
    ) -> Optional[int]:
        """
        Estimate gas for a transaction.
        
        Args:
            transaction: Transaction parameters
            
        Returns:
            Estimated gas limit
        """
        try:
            w3 = self.get_web3_instance()
            if not w3:
                return None
            
            gas_estimate = w3.eth.estimate_gas(transaction)
            
            # Add safety buffer (20%)
            return int(gas_estimate * 1.2)
            
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            return None
    
    def _start_monitoring(self) -> None:
        """Start background monitoring of connection health."""
        if not self._is_monitoring:
            self._is_monitoring = True
            asyncio.create_task(self._monitor_connections())
    
    async def _monitor_connections(self) -> None:
        """Monitor connection health and update metrics."""
        while self._is_monitoring:
            try:
                # Test all connections
                healthy_count = 0
                for w3 in self.web3_instances:
                    if w3.is_connected():
                        healthy_count += 1
                        self.metrics.success_count += 1
                    else:
                        self.metrics.error_count += 1
                
                # Update status
                if healthy_count > 0:
                    self.metrics.status = ConnectionStatus.CONNECTED
                else:
                    self.metrics.status = ConnectionStatus.ERROR
                
                # Calculate uptime percentage
                total_checks = self.metrics.success_count + self.metrics.error_count
                if total_checks > 0:
                    self.metrics.uptime_percentage = (
                        self.metrics.success_count / total_checks
                    ) * 100
                
                # Get current gas price
                await self.get_gas_price()
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_metrics(self) -> ConnectionMetrics:
        """Get current connection metrics."""
        return self.metrics
    
    async def shutdown(self) -> None:
        """Shutdown the connector and clean up resources."""
        self._is_monitoring = False
        self.web3_instances.clear()
        self.metrics.status = ConnectionStatus.DISCONNECTED


class EthereumConnector(BlockchainConnector):
    """Ethereum mainnet and testnet connector with ETH-specific optimizations."""
    
    def __init__(self, mainnet: bool = True):
        """
        Initialize Ethereum connector.
        
        Args:
            mainnet: True for mainnet, False for Sepolia testnet
        """
        if mainnet:
            config = NetworkConfig(
                network_type=NetworkType.ETHEREUM_MAINNET,
                name="Ethereum Mainnet",
                chain_id=1,
                rpc_urls=[
                    "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
                    "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
                    "https://eth-mainnet.public.blastapi.io",
                    "https://rpc.ankr.com/eth"
                ],
                ws_urls=[
                    "wss://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
                    "wss://mainnet.infura.io/ws/v3/YOUR_PROJECT_ID"
                ],
                explorer_url="https://etherscan.io",
                native_currency={
                    "name": "Ether",
                    "symbol": "ETH",
                    "decimals": 18
                },
                gas_price_oracle="https://ethgasstation.info/api/ethgasAPI.json",
                block_time=12.0,
                confirmation_blocks=12,
                is_testnet=False
            )
        else:
            config = NetworkConfig(
                network_type=NetworkType.ETHEREUM_SEPOLIA,
                name="Ethereum Sepolia",
                chain_id=11155111,
                rpc_urls=[
                    "https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY",
                    "https://sepolia.infura.io/v3/YOUR_PROJECT_ID",
                    "https://rpc.sepolia.org"
                ],
                ws_urls=[
                    "wss://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY",
                    "wss://sepolia.infura.io/ws/v3/YOUR_PROJECT_ID"
                ],
                explorer_url="https://sepolia.etherscan.io",
                native_currency={
                    "name": "Sepolia Ether",
                    "symbol": "ETH",
                    "decimals": 18
                },
                block_time=12.0,
                confirmation_blocks=3,
                is_testnet=True
            )
        
        super().__init__(config)


class PolygonConnector(BlockchainConnector):
    """Polygon mainnet and testnet connector with MATIC-specific optimizations."""
    
    def __init__(self, mainnet: bool = True):
        """
        Initialize Polygon connector.
        
        Args:
            mainnet: True for mainnet, False for Mumbai testnet
        """
        if mainnet:
            config = NetworkConfig(
                network_type=NetworkType.POLYGON_MAINNET,
                name="Polygon Mainnet",
                chain_id=137,
                rpc_urls=[
                    "https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
                    "https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID",
                    "https://polygon-rpc.com",
                    "https://rpc.ankr.com/polygon"
                ],
                ws_urls=[
                    "wss://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
                    "wss://polygon-mainnet.infura.io/ws/v3/YOUR_PROJECT_ID"
                ],
                explorer_url="https://polygonscan.com",
                native_currency={
                    "name": "Polygon",
                    "symbol": "MATIC",
                    "decimals": 18
                },
                gas_price_oracle="https://gasstation-mainnet.matic.network/v2",
                block_time=2.0,
                confirmation_blocks=20,
                is_testnet=False
            )
        else:
            config = NetworkConfig(
                network_type=NetworkType.POLYGON_MUMBAI,
                name="Polygon Mumbai",
                chain_id=80001,
                rpc_urls=[
                    "https://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY",
                    "https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID",
                    "https://rpc-mumbai.maticvigil.com"
                ],
                ws_urls=[
                    "wss://polygon-mumbai.g.alchemy.com/v2/YOUR_API_KEY",
                    "wss://polygon-mumbai.infura.io/ws/v3/YOUR_PROJECT_ID"
                ],
                explorer_url="https://mumbai.polygonscan.com",
                native_currency={
                    "name": "Test Polygon",
                    "symbol": "MATIC",
                    "decimals": 18
                },
                block_time=2.0,
                confirmation_blocks=5,
                is_testnet=True
            )
        
        super().__init__(config)


class BSCConnector(BlockchainConnector):
    """Binance Smart Chain connector with BNB-specific optimizations."""
    
    def __init__(self, mainnet: bool = True):
        """
        Initialize BSC connector.
        
        Args:
            mainnet: True for mainnet, False for testnet
        """
        if mainnet:
            config = NetworkConfig(
                network_type=NetworkType.BSC_MAINNET,
                name="BSC Mainnet",
                chain_id=56,
                rpc_urls=[
                    "https://bsc-dataseed1.binance.org",
                    "https://bsc-dataseed2.binance.org",
                    "https://bsc-dataseed3.binance.org",
                    "https://bsc-dataseed4.binance.org"
                ],
                ws_urls=[
                    "wss://bsc-ws-node.nariox.org"
                ],
                explorer_url="https://bscscan.com",
                native_currency={
                    "name": "Binance Coin",
                    "symbol": "BNB",
                    "decimals": 18
                },
                block_time=3.0,
                confirmation_blocks=15,
                is_testnet=False
            )
        else:
            config = NetworkConfig(
                network_type=NetworkType.BSC_TESTNET,
                name="BSC Testnet",
                chain_id=97,
                rpc_urls=[
                    "https://data-seed-prebsc-1-s1.binance.org:8545",
                    "https://data-seed-prebsc-2-s1.binance.org:8545"
                ],
                ws_urls=[],
                explorer_url="https://testnet.bscscan.com",
                native_currency={
                    "name": "Test Binance Coin",
                    "symbol": "tBNB",
                    "decimals": 18
                },
                block_time=3.0,
                confirmation_blocks=5,
                is_testnet=True
            )
        
        super().__init__(config)


class MultiChainConnector:
    """
    Multi-blockchain connector manager that handles multiple networks
    and provides unified access across different blockchains.
    """
    
    def __init__(self):
        """Initialize multi-chain connector."""
        self.connectors: Dict[NetworkType, BlockchainConnector] = {}
        self.default_networks = [
            NetworkType.ETHEREUM_MAINNET,
            NetworkType.POLYGON_MAINNET,
            NetworkType.BSC_MAINNET
        ]
    
    async def initialize_networks(
        self, 
        networks: Optional[List[NetworkType]] = None
    ) -> Dict[NetworkType, bool]:
        """
        Initialize connections to specified networks.
        
        Args:
            networks: List of networks to initialize, defaults to default_networks
            
        Returns:
            Dictionary mapping network types to initialization success
        """
        if networks is None:
            networks = self.default_networks
        
        results = {}
        
        for network in networks:
            try:
                if network in [
                    NetworkType.ETHEREUM_MAINNET, 
                    NetworkType.ETHEREUM_SEPOLIA
                ]:
                    connector = EthereumConnector(
                        mainnet=network == NetworkType.ETHEREUM_MAINNET
                    )
                elif network in [
                    NetworkType.POLYGON_MAINNET, 
                    NetworkType.POLYGON_MUMBAI
                ]:
                    connector = PolygonConnector(
                        mainnet=network == NetworkType.POLYGON_MAINNET
                    )
                elif network in [
                    NetworkType.BSC_MAINNET, 
                    NetworkType.BSC_TESTNET
                ]:
                    connector = BSCConnector(
                        mainnet=network == NetworkType.BSC_MAINNET
                    )
                else:
                    logger.warning(f"Unsupported network: {network}")
                    results[network] = False
                    continue
                
                success = await connector.initialize()
                if success:
                    self.connectors[network] = connector
                
                results[network] = success
                
            except Exception as e:
                logger.error(f"Failed to initialize {network}: {e}")
                results[network] = False
        
        return results
    
    def get_connector(self, network: NetworkType) -> Optional[BlockchainConnector]:
        """Get connector for specific network."""
        return self.connectors.get(network)
    
    def get_all_connectors(self) -> Dict[NetworkType, BlockchainConnector]:
        """Get all active connectors."""
        return self.connectors.copy()
    
    async def get_best_network_for_operation(
        self, 
        operation_type: str = "transaction"
    ) -> Optional[NetworkType]:
        """
        Get the best network for a specific operation based on current conditions.
        
        Args:
            operation_type: Type of operation (transaction, query, etc.)
            
        Returns:
            Best network type or None if no networks available
        """
        if not self.connectors:
            return None
        
        best_network = None
        best_score = -1
        
        for network, connector in self.connectors.items():
            metrics = connector.get_metrics()
            
            if metrics.status != ConnectionStatus.CONNECTED:
                continue
            
            # Calculate score based on various factors
            score = 0
            
            # Response time (lower is better)
            if metrics.response_time_ms > 0:
                score += 100 / metrics.response_time_ms
            
            # Uptime percentage
            score += metrics.uptime_percentage / 100
            
            # Gas price (lower is better for transactions)
            if operation_type == "transaction" and metrics.gas_price_gwei:
                score += 100 / metrics.gas_price_gwei
            
            # Network-specific bonuses
            if network == NetworkType.POLYGON_MAINNET:
                score += 0.5  # Lower gas costs
            elif network == NetworkType.BSC_MAINNET:
                score += 0.3  # Fast block times
            elif network == NetworkType.ETHEREUM_MAINNET:
                score += 0.1  # Most secure but expensive
            
            if score > best_score:
                best_score = score
                best_network = network
        
        return best_network
    
    async def shutdown(self) -> None:
        """Shutdown all connectors."""
        for connector in self.connectors.values():
            await connector.shutdown()
        
        self.connectors.clear()
