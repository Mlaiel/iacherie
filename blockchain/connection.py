"""Blockchain connection and network management for IA Influencer Agent.

This module handles blockchain connections, network management, and Web3 integration
for the IA Influencer Agent platform's blockchain functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited.
"""
from typing import Dict, Optional, Any, Union
import asyncio
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    """Network configuration for blockchain connections."""
    
    name: str
    rpc_url: str
    chain_id: int
    currency_symbol: str
    block_explorer_url: str
    is_testnet: bool = False
    supports_eip1559: bool = True


class BlockchainConnection:
    """Professional blockchain connection manager for multi-network support."""
    
    # Network configurations
    NETWORKS = {
        "ethereum": NetworkConfig(
            name="Ethereum Mainnet",
            rpc_url="https://mainnet.infura.io/v3/",
            chain_id=1,
            currency_symbol="ETH",
            block_explorer_url="https://etherscan.io",
            supports_eip1559=True
        ),
        "polygon": NetworkConfig(
            name="Polygon Mainnet",
            rpc_url="https://polygon-rpc.com/",
            chain_id=137,
            currency_symbol="MATIC",
            block_explorer_url="https://polygonscan.com",
            supports_eip1559=True
        ),
        "bsc": NetworkConfig(
            name="BNB Smart Chain",
            rpc_url="https://bsc-dataseed1.binance.org/",
            chain_id=56,
            currency_symbol="BNB",
            block_explorer_url="https://bscscan.com",
            supports_eip1559=False
        ),
        "arbitrum": NetworkConfig(
            name="Arbitrum One",
            rpc_url="https://arb1.arbitrum.io/rpc",
            chain_id=42161,
            currency_symbol="ETH",
            block_explorer_url="https://arbiscan.io",
            supports_eip1559=True
        ),
        "optimism": NetworkConfig(
            name="Optimism",
            rpc_url="https://mainnet.optimism.io",
            chain_id=10,
            currency_symbol="ETH",
            block_explorer_url="https://optimistic.etherscan.io",
            supports_eip1559=True
        )
    }
    
    def __init__(self, network: str = "polygon", api_key: Optional[str] = None):
        """Initialize blockchain connection.
        
        Args:
            network: Target blockchain network
            api_key: API key for RPC provider
        """
        self.network = network
        self.api_key = api_key
        self.web3: Optional[Web3] = None
        self.account: Optional[Account] = None
        self.connection_pool: Dict[str, Web3] = {}
        self.last_health_check = datetime.utcnow()
        self.connection_retries = 3
        
    async def initialize_connection(self) -> bool:
        """Initialize blockchain connection with retry logic."""
        try:
            network_config = self.NETWORKS.get(self.network)
            if not network_config:
                raise ValueError(f"Unsupported network: {self.network}")
            
            rpc_url = self._build_rpc_url(network_config.rpc_url)
            
            for attempt in range(self.connection_retries):
                try:
                    self.web3 = Web3(Web3.HTTPProvider(rpc_url))
                    
                    # Add PoA middleware if needed
                    if network_config.name in ["BNB Smart Chain", "Polygon Mainnet"]:
                        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    # Test connection
                    if await self._test_connection():
                        logger.info(f"Successfully connected to {network_config.name}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                    if attempt < self.connection_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain connection: {e}")
            return False
    
    def _build_rpc_url(self, base_url: str) -> str:
        """Build complete RPC URL with API key if needed."""
        if self.api_key and "infura.io" in base_url:
            return f"{base_url}{self.api_key}"
        return base_url
    
    async def _test_connection(self) -> bool:
        """Test blockchain connection health."""
        try:
            if not self.web3:
                return False
                
            # Test basic connectivity
            latest_block = await asyncio.get_event_loop().run_in_executor(
                None, self.web3.eth.get_block, "latest"
            )
            
            if latest_block and latest_block.number > 0:
                self.last_health_check = datetime.utcnow()
                return True
                
        except Exception as e:
            logger.error(f"Connection health check failed: {e}")
            
        return False
    
    async def switch_network(self, network: str) -> bool:
        """Switch to different blockchain network."""
        if network == self.network:
            return True
            
        old_network = self.network
        self.network = network
        
        if await self.initialize_connection():
            logger.info(f"Switched from {old_network} to {network}")
            return True
        else:
            self.network = old_network
            logger.error(f"Failed to switch to {network}, reverted to {old_network}")
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information."""
        network_config = self.NETWORKS.get(self.network)
        if not network_config:
            return {}
            
        return {
            "name": network_config.name,
            "chain_id": network_config.chain_id,
            "currency": network_config.currency_symbol,
            "explorer": network_config.block_explorer_url,
            "is_testnet": network_config.is_testnet,
            "supports_eip1559": network_config.supports_eip1559,
            "connected": self.web3 is not None and self.web3.isConnected(),
            "last_health_check": self.last_health_check.isoformat()
        }
    
    async def get_balance(self, address: str) -> Dict[str, Union[int, str]]:
        """Get wallet balance for address."""
        try:
            if not self.web3:
                raise ValueError("Blockchain connection not initialized")
                
            balance_wei = await asyncio.get_event_loop().run_in_executor(
                None, self.web3.eth.get_balance, address
            )
            
            balance_ether = self.web3.fromWei(balance_wei, 'ether')
            network_config = self.NETWORKS[self.network]
            
            return {
                "address": address,
                "balance_wei": balance_wei,
                "balance_formatted": float(balance_ether),
                "currency": network_config.currency_symbol,
                "network": network_config.name
            }
            
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {e}")
            raise
    
    async def estimate_gas_price(self) -> Dict[str, int]:
        """Estimate current gas prices."""
        try:
            if not self.web3:
                raise ValueError("Blockchain connection not initialized")
            
            network_config = self.NETWORKS[self.network]
            
            if network_config.supports_eip1559:
                # EIP-1559 gas estimation
                fee_history = await asyncio.get_event_loop().run_in_executor(
                    None, self.web3.eth.fee_history, 20, "latest", [25, 50, 75]
                )
                
                base_fee = fee_history['baseFeePerGas'][-1]
                priority_fees = fee_history['reward'][-10:]  # Last 10 blocks
                
                # Calculate percentiles
                low_priority = int(sum(r[0] for r in priority_fees) / len(priority_fees))
                standard_priority = int(sum(r[1] for r in priority_fees) / len(priority_fees))
                fast_priority = int(sum(r[2] for r in priority_fees) / len(priority_fees))
                
                return {
                    "base_fee": base_fee,
                    "slow": {
                        "max_fee": base_fee * 2 + low_priority,
                        "max_priority_fee": low_priority
                    },
                    "standard": {
                        "max_fee": base_fee * 2 + standard_priority,
                        "max_priority_fee": standard_priority
                    },
                    "fast": {
                        "max_fee": base_fee * 2 + fast_priority,
                        "max_priority_fee": fast_priority
                    }
                }
            else:
                # Legacy gas pricing
                gas_price = await asyncio.get_event_loop().run_in_executor(
                    None, self.web3.eth.gas_price
                )
                
                return {
                    "slow": int(gas_price * 0.9),
                    "standard": gas_price,
                    "fast": int(gas_price * 1.2)
                }
                
        except Exception as e:
            logger.error(f"Failed to estimate gas price: {e}")
            raise
    
    def create_account(self, private_key: Optional[str] = None) -> Dict[str, str]:
        """Create or load blockchain account."""
        try:
            if private_key:
                account = Account.from_key(private_key)
            else:
                account = Account.create()
            
            self.account = account
            
            return {
                "address": account.address,
                "private_key": account.privateKey.hex(),
                "network": self.network
            }
            
        except Exception as e:
            logger.error(f"Failed to create account: {e}")
            raise
    
    async def close_connection(self) -> None:
        """Close blockchain connection and cleanup resources."""
        try:
            if self.web3:
                # Cleanup any pending transactions or connections
                self.web3 = None
                logger.info("Blockchain connection closed")
                
        except Exception as e:
            logger.error(f"Error closing blockchain connection: {e}")


class MultiNetworkManager:
    """Manager for multiple blockchain network connections."""
    
    def __init__(self):
        self.connections: Dict[str, BlockchainConnection] = {}
        self.active_network = "polygon"
    
    async def add_network(self, network: str, api_key: Optional[str] = None) -> bool:
        """Add and initialize a new network connection."""
        try:
            if network in self.connections:
                return True
                
            connection = BlockchainConnection(network, api_key)
            if await connection.initialize_connection():
                self.connections[network] = connection
                logger.info(f"Added network connection: {network}")
                return True
            else:
                logger.error(f"Failed to initialize network: {network}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding network {network}: {e}")
            return False
    
    def get_connection(self, network: Optional[str] = None) -> Optional[BlockchainConnection]:
        """Get connection for specific network."""
        target_network = network or self.active_network
        return self.connections.get(target_network)
    
    async def switch_active_network(self, network: str) -> bool:
        """Switch active network."""
        if network in self.connections:
            self.active_network = network
            return True
        else:
            # Try to add the network
            if await self.add_network(network):
                self.active_network = network
                return True
        return False
    
    def get_all_network_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all network connections."""
        status = {}
        for network, connection in self.connections.items():
            status[network] = {
                **connection.get_network_info(),
                "is_active": network == self.active_network
            }
        return status
    
    async def close_all_connections(self) -> None:
        """Close all network connections."""
        for connection in self.connections.values():
            await connection.close_connection()
        self.connections.clear()
        logger.info("All blockchain connections closed")
