"""
Ainflue Platform - Blockchain Rights Monitor
==========================================

Enterprise-grade blockchain monitoring for content rights management,
ownership verification, and decentralized rights enforcement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
from prometheus_client import Counter, Histogram, Gauge
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)

# Metrics
blockchain_transactions_total = Counter('ainflue_blockchain_transactions_total',
                                       'Total blockchain transactions', ['chain', 'type', 'status'])
blockchain_verification_duration = Histogram('ainflue_blockchain_verification_duration_seconds',
                                            'Time spent verifying blockchain records')
blockchain_rights_validated = Gauge('ainflue_blockchain_rights_validated',
                                   'Number of blockchain-validated rights', ['content_type'])

class BlockchainNetwork(Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"
    AVALANCHE = "avalanche"
    CARDANO = "cardano"

class RightsType(Enum):
    """Types of content rights."""
    COPYRIGHT = "copyright"
    USAGE_RIGHTS = "usage_rights"
    DISTRIBUTION_RIGHTS = "distribution_rights"
    MONETIZATION_RIGHTS = "monetization_rights"
    DERIVATIVE_RIGHTS = "derivative_rights"
    PERFORMANCE_RIGHTS = "performance_rights"
    SYNC_RIGHTS = "sync_rights"
    MECHANICAL_RIGHTS = "mechanical_rights"

class TransactionStatus(Enum):
    """Blockchain transaction status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REVERTED = "reverted"
    EXPIRED = "expired"

@dataclass
class RightsRecord:
    """Blockchain rights record."""
    content_hash: str
    creator_address: str
    rights_type: RightsType
    ownership_percentage: float
    valid_from: datetime
    valid_until: Optional[datetime]
    conditions: Dict[str, Any]
    blockchain_network: BlockchainNetwork
    transaction_hash: str
    block_number: int
    contract_address: str

@dataclass
class BlockchainTransaction:
    """Blockchain transaction record."""
    transaction_hash: str
    blockchain_network: BlockchainNetwork
    from_address: str
    to_address: str
    contract_address: Optional[str]
    function_name: str
    parameters: Dict[str, Any]
    gas_used: int
    gas_price: int
    status: TransactionStatus
    block_number: int
    timestamp: datetime
    confirmations: int

@dataclass
class SmartContractEvent:
    """Smart contract event record."""
    event_name: str
    contract_address: str
    blockchain_network: BlockchainNetwork
    transaction_hash: str
    block_number: int
    log_index: int
    parameters: Dict[str, Any]
    timestamp: datetime

class BlockchainRightsMonitor:
    """Enterprise blockchain rights monitoring system."""
    
    def __init__(self) -> None:
        self.network_providers = {}
        self.contract_abis = {}
        self.monitored_contracts = {}
        self.rights_cache = {}
        self.transaction_cache = {}
        
    async def initialize_networks(self, network_configs -> None: Dict[BlockchainNetwork, Dict[str, Any]]) -> None:
        """Initialize blockchain network connections."""
        for network, config in network_configs.items():
            try:
                provider_url = config.get('rpc_url')
                api_key = config.get('api_key')
                
                self.network_providers[network] = {
                    'rpc_url': provider_url,
                    'api_key': api_key,
                    'session': aiohttp.ClientSession()
                }
                
                logger.info(f"Initialized blockchain network: {network.value}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {network.value}: {str(e)}")
    
    async def register_content_rights(self, content_hash: str, creator_address: str,
                                    rights_type: RightsType, ownership_percentage: float,
                                    blockchain_network: BlockchainNetwork,
                                    conditions: Optional[Dict[str, Any]] = None) -> str:
        """Register content rights on blockchain."""
        start_time = time.time()
        
        try:
            # Prepare transaction data
            conditions = conditions or {}
            transaction_data = {
                'content_hash': content_hash,
                'creator_address': creator_address,
                'rights_type': rights_type.value,
                'ownership_percentage': ownership_percentage,
                'conditions': conditions,
                'timestamp': int(time.time())
            }
            
            # Submit to blockchain
            transaction_hash = await self._submit_rights_transaction(
                blockchain_network, transaction_data
            )
            
            # Monitor transaction
            await self._monitor_transaction_confirmation(
                blockchain_network, transaction_hash
            )
            
            # Update metrics
            duration = time.time() - start_time
            blockchain_verification_duration.observe(duration)
            blockchain_transactions_total.labels(
                chain=blockchain_network.value,
                type='rights_registration',
                status='confirmed'
            ).inc()
            
            logger.info(f"Rights registered on {blockchain_network.value}: {transaction_hash}")
            return transaction_hash
            
        except Exception as e:
            blockchain_transactions_total.labels(
                chain=blockchain_network.value,
                type='rights_registration',
                status='failed'
            ).inc()
            logger.error(f"Rights registration failed: {str(e)}")
            raise
    
    async def _submit_rights_transaction(self, network: BlockchainNetwork,
                                       transaction_data: Dict[str, Any]) -> str:
        """Submit rights registration transaction to blockchain."""
        
        if network not in self.network_providers:
            raise ValueError(f"Network {network.value} not initialized")
        
        provider = self.network_providers[network]
        
        # Simulate blockchain transaction submission
        # In real implementation, would use web3.py, ethers.js, or similar
        
        # Create transaction hash
        data_string = json.dumps(transaction_data, sort_keys=True)
        transaction_hash = hashlib.sha256(
            f"{data_string}{time.time()}".encode()
        ).hexdigest()
        
        # Simulate network submission
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Store pending transaction
        self.transaction_cache[transaction_hash] = {
            'status': TransactionStatus.PENDING,
            'network': network,
            'data': transaction_data,
            'submitted_at': datetime.now()
        }
        
        return f"0x{transaction_hash}"
    
    async def _monitor_transaction_confirmation(self, network: BlockchainNetwork,
                                              transaction_hash: str) -> None:
        """Monitor transaction confirmation on blockchain."""
        
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                status = await self._get_transaction_status(network, transaction_hash)
                
                if status == TransactionStatus.CONFIRMED:
                    logger.info(f"Transaction confirmed: {transaction_hash}")
                    return
                elif status == TransactionStatus.FAILED:
                    raise Exception(f"Transaction failed: {transaction_hash}")
                
                # Wait before checking again
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.warning(f"Transaction monitoring error: {str(e)}")
                await asyncio.sleep(5)
        
        # Timeout reached
        logger.error(f"Transaction confirmation timeout: {transaction_hash}")
        raise TimeoutError(f"Transaction not confirmed within {max_wait_time} seconds")
    
    async def _get_transaction_status(self, network: BlockchainNetwork,
                                    transaction_hash: str) -> TransactionStatus:
        """Get transaction status from blockchain."""
        
        # Simulate blockchain status check
        # In real implementation, would query actual blockchain
        
        if transaction_hash in self.transaction_cache:
            tx_data = self.transaction_cache[transaction_hash]
            
            # Simulate confirmation after some time
            elapsed = (datetime.now() - tx_data['submitted_at']).total_seconds()
            
            if elapsed > 30:  # Simulate 30-second confirmation
                tx_data['status'] = TransactionStatus.CONFIRMED
                return TransactionStatus.CONFIRMED
            else:
                return TransactionStatus.PENDING
        
        return TransactionStatus.FAILED
    
    async def verify_content_ownership(self, content_hash: str,
                                     creator_address: str,
                                     blockchain_network: BlockchainNetwork) -> Tuple[bool, List[RightsRecord]]:
        """Verify content ownership on blockchain."""
        start_time = time.time()
        
        try:
            # Query blockchain for rights records
            rights_records = await self._query_rights_records(
                content_hash, blockchain_network
            )
            
            # Filter by creator address
            creator_rights = [
                record for record in rights_records
                if record.creator_address.lower() == creator_address.lower()
            ]
            
            # Check ownership validity
            is_owner = len(creator_rights) > 0
            
            # Validate rights are current
            current_time = datetime.now()
            valid_rights = []
            
            for record in creator_rights:
                if record.valid_from <= current_time:
                    if record.valid_until is None or record.valid_until > current_time:
                        valid_rights.append(record)
            
            is_valid_owner = len(valid_rights) > 0
            
            # Update metrics
            duration = time.time() - start_time
            blockchain_verification_duration.observe(duration)
            
            if is_valid_owner:
                blockchain_rights_validated.labels(content_type='verified').inc()
            
            logger.info(f"Ownership verification completed for {content_hash}: {is_valid_owner}")
            return is_valid_owner, valid_rights
            
        except Exception as e:
            logger.error(f"Ownership verification failed: {str(e)}")
            return False, []
    
    async def _query_rights_records(self, content_hash: str,
                                  blockchain_network: BlockchainNetwork) -> List[RightsRecord]:
        """Query blockchain for content rights records."""
        
        # Simulate blockchain query
        # In real implementation, would query smart contracts
        
        # Return simulated rights records
        if len(content_hash) > 10:  # Simulate some content having records
            return [
                RightsRecord(
                    content_hash=content_hash,
                    creator_address="0x742b35cfe078d442bb37d85e1b57e2c62ed0f",
                    rights_type=RightsType.COPYRIGHT,
                    ownership_percentage=100.0,
                    valid_from=datetime.now() - timedelta(days=30),
                    valid_until=None,
                    conditions={},
                    blockchain_network=blockchain_network,
                    transaction_hash=f"0x{hashlib.sha256(content_hash.encode()).hexdigest()}",
                    block_number=1234567,
                    contract_address="0x1234567890abcdef1234567890abcdef12345678"
                )
            ]
        
        return []
    
    async def transfer_rights(self, content_hash: str, from_address: str,
                            to_address: str, rights_type: RightsType,
                            percentage: float, blockchain_network: BlockchainNetwork,
                            conditions: Optional[Dict[str, Any]] = None) -> str:
        """Transfer content rights on blockchain."""
        
        try:
            # Verify current ownership
            is_owner, current_rights = await self.verify_content_ownership(
                content_hash, from_address, blockchain_network
            )
            
            if not is_owner:
                raise ValueError("Sender does not own rights to this content")
            
            # Check if sender has sufficient ownership percentage
            total_owned = sum(record.ownership_percentage for record in current_rights
                            if record.rights_type == rights_type)
            
            if total_owned < percentage:
                raise ValueError(f"Insufficient ownership: {total_owned}% < {percentage}%")
            
            # Prepare transfer transaction
            transfer_data = {
                'content_hash': content_hash,
                'from_address': from_address,
                'to_address': to_address,
                'rights_type': rights_type.value,
                'percentage': percentage,
                'conditions': conditions or {},
                'timestamp': int(time.time())
            }
            
            # Submit transfer transaction
            transaction_hash = await self._submit_transfer_transaction(
                blockchain_network, transfer_data
            )
            
            # Monitor confirmation
            await self._monitor_transaction_confirmation(
                blockchain_network, transaction_hash
            )
            
            blockchain_transactions_total.labels(
                chain=blockchain_network.value,
                type='rights_transfer',
                status='confirmed'
            ).inc()
            
            logger.info(f"Rights transferred: {from_address} -> {to_address} ({percentage}%)")
            return transaction_hash
            
        except Exception as e:
            blockchain_transactions_total.labels(
                chain=blockchain_network.value,
                type='rights_transfer',
                status='failed'
            ).inc()
            logger.error(f"Rights transfer failed: {str(e)}")
            raise
    
    async def _submit_transfer_transaction(self, network: BlockchainNetwork,
                                         transfer_data: Dict[str, Any]) -> str:
        """Submit rights transfer transaction to blockchain."""
        
        # Similar to _submit_rights_transaction but for transfers
        data_string = json.dumps(transfer_data, sort_keys=True)
        transaction_hash = hashlib.sha256(
            f"{data_string}{time.time()}transfer".encode()
        ).hexdigest()
        
        await asyncio.sleep(0.1)  # Simulate network delay
        
        self.transaction_cache[f"0x{transaction_hash}"] = {
            'status': TransactionStatus.PENDING,
            'network': network,
            'data': transfer_data,
            'submitted_at': datetime.now()
        }
        
        return f"0x{transaction_hash}"
    
    async def revoke_rights(self, content_hash: str, owner_address: str,
                          rights_type: RightsType, blockchain_network: BlockchainNetwork,
                          reason: str = "") -> str:
        """Revoke content rights on blockchain."""
        
        try:
            # Verify ownership
            is_owner, current_rights = await self.verify_content_ownership(
                content_hash, owner_address, blockchain_network
            )
            
            if not is_owner:
                raise ValueError("Address does not own rights to this content")
            
            # Prepare revocation transaction
            revocation_data = {
                'content_hash': content_hash,
                'owner_address': owner_address,
                'rights_type': rights_type.value,
                'reason': reason,
                'timestamp': int(time.time())
            }
            
            # Submit revocation transaction
            transaction_hash = await self._submit_revocation_transaction(
                blockchain_network, revocation_data
            )
            
            # Monitor confirmation
            await self._monitor_transaction_confirmation(
                blockchain_network, transaction_hash
            )
            
            blockchain_transactions_total.labels(
                chain=blockchain_network.value,
                type='rights_revocation',
                status='confirmed'
            ).inc()
            
            logger.info(f"Rights revoked for {content_hash}: {rights_type.value}")
            return transaction_hash
            
        except Exception as e:
            blockchain_transactions_total.labels(
                chain=blockchain_network.value,
                type='rights_revocation',
                status='failed'
            ).inc()
            logger.error(f"Rights revocation failed: {str(e)}")
            raise
    
    async def _submit_revocation_transaction(self, network: BlockchainNetwork,
                                           revocation_data: Dict[str, Any]) -> str:
        """Submit rights revocation transaction to blockchain."""
        
        data_string = json.dumps(revocation_data, sort_keys=True)
        transaction_hash = hashlib.sha256(
            f"{data_string}{time.time()}revoke".encode()
        ).hexdigest()
        
        await asyncio.sleep(0.1)
        
        self.transaction_cache[f"0x{transaction_hash}"] = {
            'status': TransactionStatus.PENDING,
            'network': network,
            'data': revocation_data,
            'submitted_at': datetime.now()
        }
        
        return f"0x{transaction_hash}"
    
    async def validate_usage_rights(self, content_hash: str, user_address: str,
                                  usage_type: str, blockchain_network: BlockchainNetwork) -> Tuple[bool, Dict[str, Any]]:
        """Validate user's rights to use content in specific way."""
        
        try:
            # Get all rights records for content
            rights_records = await self._query_rights_records(content_hash, blockchain_network)
            
            # Check for applicable usage rights
            applicable_rights = []
            current_time = datetime.now()
            
            for record in rights_records:
                # Check if rights apply to user
                if record.creator_address.lower() == user_address.lower():
                    # Check if rights are valid
                    if record.valid_from <= current_time:
                        if record.valid_until is None or record.valid_until > current_time:
                            # Check if usage type is allowed
                            if self._check_usage_allowed(record, usage_type):
                                applicable_rights.append(record)
            
            has_rights = len(applicable_rights) > 0
            
            # Compile usage conditions
            usage_conditions = {}
            if has_rights:
                for record in applicable_rights:
                    usage_conditions.update(record.conditions)
            
            return has_rights, usage_conditions
            
        except Exception as e:
            logger.error(f"Usage rights validation failed: {str(e)}")
            return False, {}
    
    def _check_usage_allowed(self, rights_record: RightsRecord, usage_type: str) -> bool:
        """Check if usage type is allowed by rights record."""
        
        # Map usage types to rights types
        usage_rights_mapping = {
            'stream': [RightsType.DISTRIBUTION_RIGHTS, RightsType.PERFORMANCE_RIGHTS],
            'download': [RightsType.DISTRIBUTION_RIGHTS],
            'remix': [RightsType.DERIVATIVE_RIGHTS],
            'commercial': [RightsType.MONETIZATION_RIGHTS],
            'sync': [RightsType.SYNC_RIGHTS],
            'broadcast': [RightsType.PERFORMANCE_RIGHTS, RightsType.DISTRIBUTION_RIGHTS]
        }
        
        required_rights = usage_rights_mapping.get(usage_type, [])
        return rights_record.rights_type in required_rights
    
    async def monitor_smart_contract_events(self, contract_address: str,
                                          blockchain_network: BlockchainNetwork,
                                          event_filter: Optional[Dict[str, Any]] = None) -> List[SmartContractEvent]:
        """Monitor smart contract events for rights management."""
        
        try:
            # Simulate event monitoring
            # In real implementation, would use web3 event filters
            
            events = await self._query_contract_events(
                contract_address, blockchain_network, event_filter
            )
            
            # Process events
            processed_events = []
            for event_data in events:
                event = SmartContractEvent(
                    event_name=event_data['event'],
                    contract_address=contract_address,
                    blockchain_network=blockchain_network,
                    transaction_hash=event_data['transactionHash'],
                    block_number=event_data['blockNumber'],
                    log_index=event_data['logIndex'],
                    parameters=event_data['args'],
                    timestamp=datetime.fromtimestamp(event_data['timestamp'])
                )
                processed_events.append(event)
            
            logger.info(f"Monitored {len(processed_events)} contract events")
            return processed_events
            
        except Exception as e:
            logger.error(f"Contract event monitoring failed: {str(e)}")
            return []
    
    async def _query_contract_events(self, contract_address: str,
                                   blockchain_network: BlockchainNetwork,
                                   event_filter: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Query smart contract events from blockchain."""
        
        # Simulate contract event query
        return [
            {
                'event': 'RightsRegistered',
                'transactionHash': f"0x{hashlib.sha256(f'{contract_address}1'.encode()).hexdigest()}",
                'blockNumber': 1234567,
                'logIndex': 0,
                'args': {
                    'contentHash': 'content_hash_example',
                    'creator': '0x742b35cfe078d442bb37d85e1b57e2c62ed0f',
                    'rightsType': 'copyright'
                },
                'timestamp': time.time()
            }
        ]
    
    async def get_rights_history(self, content_hash: str,
                               blockchain_network: BlockchainNetwork) -> List[Dict[str, Any]]:
        """Get complete rights history for content."""
        
        try:
            # Query all transactions related to content
            rights_transactions = await self._query_rights_history(content_hash, blockchain_network)
            
            # Sort by timestamp
            rights_transactions.sort(key=lambda x: x['timestamp'])
            
            return rights_transactions
            
        except Exception as e:
            logger.error(f"Rights history query failed: {str(e)}")
            return []
    
    async def _query_rights_history(self, content_hash: str,
                                  blockchain_network: BlockchainNetwork) -> List[Dict[str, Any]]:
        """Query rights transaction history from blockchain."""
        
        # Simulate rights history query
        return [
            {
                'type': 'registration',
                'transaction_hash': f"0x{hashlib.sha256(f'{content_hash}reg'.encode()).hexdigest()}",
                'creator': '0x742b35cfe078d442bb37d85e1b57e2c62ed0f',
                'rights_type': 'copyright',
                'percentage': 100.0,
                'timestamp': time.time() - 86400,  # 1 day ago
                'block_number': 1234560
            }
        ]
    
    async def validate_contract_compliance(self, contract_address: str,
                                         blockchain_network: BlockchainNetwork) -> Dict[str, Any]:
        """Validate smart contract compliance with rights management standards."""
        
        try:
            # Check contract code and functionality
            compliance_results = {
                'contract_address': contract_address,
                'network': blockchain_network.value,
                'compliance_score': 0.0,
                'checks_passed': [],
                'checks_failed': [],
                'recommendations': []
            }
            
            # Simulate compliance checks
            checks = [
                'rights_registration_function',
                'rights_transfer_function',
                'ownership_verification',
                'access_control',
                'event_emission',
                'emergency_functions'
            ]
            
            passed_checks = 0
            for check in checks:
                # Simulate check result
                if hash(f"{contract_address}{check}") % 3 != 0:  # 2/3 pass rate
                    compliance_results['checks_passed'].append(check)
                    passed_checks += 1
                else:
                    compliance_results['checks_failed'].append(check)
                    compliance_results['recommendations'].append(f"Implement {check}")
            
            compliance_results['compliance_score'] = passed_checks / len(checks)
            
            logger.info(f"Contract compliance validated: {compliance_results['compliance_score']:.2f}")
            return compliance_results
            
        except Exception as e:
            logger.error(f"Contract compliance validation failed: {str(e)}")
            return {'error': str(e)}
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get blockchain monitoring statistics."""
        
        network_stats = {}
        for network in self.network_providers:
            network_stats[network.value] = {
                'connected': True,
                'monitored_contracts': len(self.monitored_contracts.get(network, [])),
                'cached_transactions': len([
                    tx for tx in self.transaction_cache.values()
                    if tx['network'] == network
                ])
            }
        
        return {
            'networks': network_stats,
            'total_rights_records': len(self.rights_cache),
            'total_transactions': len(self.transaction_cache),
            'monitoring_active': True
        }

# Global blockchain monitor instance
blockchain_rights_monitor = BlockchainRightsMonitor()