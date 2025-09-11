"""
⛓️ Blockchain Rights Monitor - Enterprise Content Rights Management
Advanced blockchain-based intellectual property and rights management

Role Expertise Applied:
- Security Engineer: Cryptographic rights validation and blockchain security
- Blockchain Engineer: Smart contract integration and chain monitoring  
- Backend Senior: High-performance blockchain interaction architecture
- Database Administrator: Rights metadata and chain data optimization
- Lead Dev IA: Intelligent rights pattern recognition and validation
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

class RightsType(Enum):
    """Content rights types"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    CREATIVE_COMMONS = "creative_commons"
    EXCLUSIVE_LICENSE = "exclusive_license"
    NON_EXCLUSIVE_LICENSE = "non_exclusive_license"
    DERIVATIVE_RIGHTS = "derivative_rights"
    COMMERCIAL_USE = "commercial_use"
    DISTRIBUTION_RIGHTS = "distribution_rights"

class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_TESTNET = "ethereum_testnet"
    POLYGON = "polygon"
    BSC = "bsc"
    SOLANA = "solana"
    IPFS = "ipfs"

class RightsStatus(Enum):
    """Rights validation status"""
    VERIFIED = "verified"
    PENDING = "pending"
    DISPUTED = "disputed"
    REVOKED = "revoked"
    EXPIRED = "expired"
    INVALID = "invalid"

@dataclass
class BlockchainRightsRecord:
    """Blockchain rights record"""
    content_id: str
    rights_holder: str
    rights_type: RightsType
    blockchain_network: BlockchainNetwork
    transaction_hash: str
    block_number: int
    smart_contract_address: str
    registration_timestamp: datetime
    expiration_date: Optional[datetime]
    rights_metadata: Dict[str, Any]
    verification_status: RightsStatus
    license_terms: Dict[str, Any]

@dataclass
class RightsValidationResult:
    """Rights validation result"""
    content_id: str
    is_valid: bool
    rights_holder: str
    rights_type: RightsType
    confidence_score: float
    blockchain_proof: Dict[str, Any]
    validation_timestamp: datetime
    expiration_check: bool
    license_compatibility: Dict[str, Any]
    violation_risk: str

@dataclass
class SmartContractInteraction:
    """Smart contract interaction record"""
    contract_address: str
    function_name: str
    parameters: Dict[str, Any]
    transaction_hash: str
    gas_used: int
    status: str
    result: Dict[str, Any]
    timestamp: datetime

class BlockchainRightsMonitor:
    """Enterprise blockchain rights monitoring system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Network configurations
        self.network_configs = {
            BlockchainNetwork.ETHEREUM_MAINNET: {
                'rpc_url': 'https://mainnet.infura.io/v3/your-key',
                'contract_address': '0x1234567890123456789012345678901234567890',
                'gas_limit': 200000,
                'confirmation_blocks': 12
            },
            BlockchainNetwork.POLYGON: {
                'rpc_url': 'https://polygon-rpc.com',
                'contract_address': '0x2345678901234567890123456789012345678901',
                'gas_limit': 150000,
                'confirmation_blocks': 6
            }
        }
        
        # Rights monitoring cache
        self.rights_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Smart contract ABIs
        self.contract_abis = self._load_contract_abis()
        
        # Validation thresholds
        self.validation_thresholds = {
            'min_confirmations': 6,
            'max_block_age': 86400,  # 24 hours
            'confidence_threshold': 0.8
        }
        
        # Performance metrics
        self.monitoring_metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'average_response_time': 0.0,
            'blockchain_queries': 0,
            'smart_contract_calls': 0
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('blockchain_rights_monitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_contract_abis(self) -> Dict[str, Any]:
        """Load smart contract ABIs"""
        return {
            'rights_registry': [
                {
                    "name": "registerRights",
                    "type": "function",
                    "inputs": [
                        {"name": "contentHash", "type": "bytes32"},
                        {"name": "rightsHolder", "type": "address"},
                        {"name": "rightsType", "type": "uint8"},
                        {"name": "metadata", "type": "string"}
                    ]
                },
                {
                    "name": "validateRights",
                    "type": "function",
                    "inputs": [
                        {"name": "contentHash", "type": "bytes32"}
                    ],
                    "outputs": [
                        {"name": "isValid", "type": "bool"},
                        {"name": "rightsHolder", "type": "address"},
                        {"name": "registrationTime", "type": "uint256"}
                    ]
                }
            ]
        }
    
    async def validate_content_rights(self, content_data: Dict[str, Any]) -> RightsValidationResult:
        """
        Comprehensive blockchain rights validation
        
        Args:
            content_data: Content metadata and identification
            
        Returns:
            RightsValidationResult: Comprehensive rights validation result
        """
        start_time = time.time()
        
        try:
            content_id = content_data.get('content_id', '')
            
            # Check cache first
            cached_result = self._get_cached_validation(content_id)
            if cached_result:
                return cached_result
            
            # Generate content hash for blockchain lookup
            content_hash = self._generate_content_hash(content_data)
            
            # Query multiple blockchain networks
            validation_results = await self._query_multiple_networks(content_hash, content_data)
            
            # Aggregate and validate results
            final_result = self._aggregate_validation_results(validation_results, content_data)
            
            # Cache result
            self._cache_validation_result(content_id, final_result)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_monitoring_metrics(processing_time, final_result.is_valid)
            
            self.logger.info(f"Blockchain rights validation completed for {content_id}: "
                           f"Valid={final_result.is_valid}, Confidence={final_result.confidence_score:.3f}")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Blockchain rights validation failed: {str(e)}")
            return RightsValidationResult(
                content_id=content_data.get('content_id', ''),
                is_valid=False,
                rights_holder="unknown",
                rights_type=RightsType.COPYRIGHT,
                confidence_score=0.0,
                blockchain_proof={},
                validation_timestamp=datetime.now(),
                expiration_check=False,
                license_compatibility={},
                violation_risk="high"
            )
    
    async def _query_multiple_networks(self, content_hash: str, content_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query multiple blockchain networks for rights information"""
        query_tasks = []
        
        for network in [BlockchainNetwork.ETHEREUM_MAINNET, BlockchainNetwork.POLYGON]:
            task = self._query_blockchain_network(network, content_hash, content_data)
            query_tasks.append(task)
        
        results = await asyncio.gather(*query_tasks, return_exceptions=True)
        
        # Filter successful results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                valid_results.append(result)
            elif isinstance(result, Exception):
                self.logger.warning(f"Blockchain query failed: {str(result)}")
        
        return valid_results
    
    async def _query_blockchain_network(self, network: BlockchainNetwork, content_hash: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query specific blockchain network for rights information"""
        start_time = time.time()
        
        try:
            network_config = self.network_configs.get(network)
            if not network_config:
                raise ValueError(f"Network {network.value} not configured")
            
            # Simulate blockchain query
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Mock blockchain response
            import random
            has_rights_record = random.random() > 0.3  # 70% chance of having rights record
            
            if has_rights_record:
                rights_record = {
                    'content_hash': content_hash,
                    'rights_holder': f"0x{random.randint(1000000000000000, 9999999999999999):016x}",
                    'rights_type': random.choice(list(RightsType)).value,
                    'registration_timestamp': int(time.time()) - random.randint(86400, 31536000),
                    'expiration_timestamp': int(time.time()) + random.randint(86400, 31536000),
                    'transaction_hash': f"0x{random.randint(10**60, 10**64-1):064x}",
                    'block_number': random.randint(15000000, 18000000),
                    'confirmations': random.randint(6, 1000),
                    'smart_contract_address': network_config['contract_address'],
                    'license_terms': {
                        'commercial_use': random.choice([True, False]),
                        'derivative_works': random.choice([True, False]),
                        'attribution_required': True,
                        'share_alike': random.choice([True, False])
                    }
                }
                
                confidence = 0.85 + random.random() * 0.15
                is_valid = rights_record['confirmations'] >= self.validation_thresholds['min_confirmations']
                
            else:
                rights_record = None
                confidence = 0.1
                is_valid = False
            
            query_time = (time.time() - start_time) * 1000
            
            return {
                'network': network.value,
                'content_hash': content_hash,
                'rights_record': rights_record,
                'is_valid': is_valid,
                'confidence': confidence,
                'query_time_ms': query_time,
                'block_height': random.randint(15000000, 18000000),
                'network_status': 'operational'
            }
            
        except Exception as e:
            self.logger.error(f"Blockchain network query failed for {network.value}: {str(e)}")
            raise
    
    def _aggregate_validation_results(self, results: List[Dict[str, Any]], content_data: Dict[str, Any]) -> RightsValidationResult:
        """Aggregate validation results from multiple networks"""
        if not results:
            return RightsValidationResult(
                content_id=content_data.get('content_id', ''),
                is_valid=False,
                rights_holder="unknown",
                rights_type=RightsType.COPYRIGHT,
                confidence_score=0.0,
                blockchain_proof={},
                validation_timestamp=datetime.now(),
                expiration_check=False,
                license_compatibility={},
                violation_risk="high"
            )
        
        # Find the best validation result
        best_result = max(results, key=lambda x: x.get('confidence', 0))
        
        # Calculate overall confidence
        confidence_scores = [r.get('confidence', 0) for r in results]
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine validity
        valid_results = [r for r in results if r.get('is_valid', False)]
        is_valid = len(valid_results) > 0 and overall_confidence >= self.validation_thresholds['confidence_threshold']
        
        # Extract rights information
        rights_record = best_result.get('rights_record', {})
        
        if rights_record:
            rights_holder = rights_record.get('rights_holder', 'unknown')
            rights_type = RightsType(rights_record.get('rights_type', 'copyright'))
            
            # Check expiration
            expiration_timestamp = rights_record.get('expiration_timestamp', 0)
            current_timestamp = int(time.time())
            expiration_check = expiration_timestamp > current_timestamp
            
            # License compatibility analysis
            license_terms = rights_record.get('license_terms', {})
            license_compatibility = self._analyze_license_compatibility(license_terms, content_data)
            
        else:
            rights_holder = "unknown"
            rights_type = RightsType.COPYRIGHT
            expiration_check = False
            license_compatibility = {}
        
        # Assess violation risk
        violation_risk = self._assess_violation_risk(is_valid, overall_confidence, expiration_check)
        
        # Compile blockchain proof
        blockchain_proof = {
            'networks_queried': [r.get('network') for r in results],
            'valid_networks': [r.get('network') for r in valid_results],
            'best_result_network': best_result.get('network'),
            'transaction_hash': rights_record.get('transaction_hash') if rights_record else None,
            'block_number': rights_record.get('block_number') if rights_record else None,
            'confirmations': rights_record.get('confirmations') if rights_record else 0,
            'smart_contract_address': rights_record.get('smart_contract_address') if rights_record else None
        }
        
        return RightsValidationResult(
            content_id=content_data.get('content_id', ''),
            is_valid=is_valid,
            rights_holder=rights_holder,
            rights_type=rights_type,
            confidence_score=overall_confidence,
            blockchain_proof=blockchain_proof,
            validation_timestamp=datetime.now(),
            expiration_check=expiration_check,
            license_compatibility=license_compatibility,
            violation_risk=violation_risk
        )
    
    def _analyze_license_compatibility(self, license_terms: Dict[str, Any], content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze license compatibility for intended use"""
        intended_use = content_data.get('intended_use', {})
        
        compatibility = {
            'commercial_use_allowed': license_terms.get('commercial_use', False),
            'derivative_works_allowed': license_terms.get('derivative_works', False),
            'attribution_required': license_terms.get('attribution_required', True),
            'share_alike_required': license_terms.get('share_alike', False)
        }
        
        # Check compatibility with intended use
        compatibility_issues = []
        
        if intended_use.get('commercial', False) and not compatibility['commercial_use_allowed']:
            compatibility_issues.append('Commercial use not permitted')
        
        if intended_use.get('derivative', False) and not compatibility['derivative_works_allowed']:
            compatibility_issues.append('Derivative works not permitted')
        
        if compatibility['attribution_required'] and not intended_use.get('attribution_provided', False):
            compatibility_issues.append('Attribution required but not provided')
        
        compatibility['issues'] = compatibility_issues
        compatibility['is_compatible'] = len(compatibility_issues) == 0
        
        return compatibility
    
    def _assess_violation_risk(self, is_valid: bool, confidence: float, expiration_check: bool) -> str:
        """Assess intellectual property violation risk"""
        if not is_valid:
            return "high"
        elif confidence < 0.6:
            return "medium"
        elif not expiration_check:
            return "medium"
        elif confidence >= 0.9:
            return "very_low"
        else:
            return "low"
    
    async def register_content_rights(self, content_data: Dict[str, Any], rights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register content rights on blockchain"""
        try:
            content_hash = self._generate_content_hash(content_data)
            
            # Prepare registration transaction
            transaction_data = {
                'content_hash': content_hash,
                'rights_holder': rights_data.get('rights_holder'),
                'rights_type': rights_data.get('rights_type', RightsType.COPYRIGHT.value),
                'metadata': json.dumps(rights_data.get('metadata', {})),
                'license_terms': json.dumps(rights_data.get('license_terms', {}))
            }
            
            # Select optimal network for registration
            target_network = self._select_optimal_network(content_data)
            
            # Submit to blockchain (simulated)
            registration_result = await self._submit_registration_transaction(target_network, transaction_data)
            
            self.logger.info(f"Content rights registered: {content_hash} on {target_network.value}")
            
            return registration_result
            
        except Exception as e:
            self.logger.error(f"Rights registration failed: {str(e)}")
            raise
    
    def _select_optimal_network(self, content_data: Dict[str, Any]) -> BlockchainNetwork:
        """Select optimal blockchain network for registration"""
        # Simple selection logic - can be enhanced based on content type, cost, speed
        content_type = content_data.get('content_type', '')
        
        if content_type in ['audio', 'video']:
            return BlockchainNetwork.POLYGON  # Lower gas fees for multimedia
        else:
            return BlockchainNetwork.ETHEREUM_MAINNET  # Higher security for important content
    
    async def _submit_registration_transaction(self, network: BlockchainNetwork, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit registration transaction to blockchain"""
        # Simulate transaction submission
        await asyncio.sleep(0.2)  # Simulate network delay
        
        import random
        transaction_hash = f"0x{random.randint(10**60, 10**64-1):064x}"
        block_number = random.randint(15000000, 18000000)
        
        return {
            'transaction_hash': transaction_hash,
            'block_number': block_number,
            'network': network.value,
            'status': 'pending',
            'gas_used': random.randint(50000, 150000),
            'timestamp': datetime.now().isoformat(),
            'confirmation_time_estimate': '2-5 minutes'
        }
    
    def _generate_content_hash(self, content_data: Dict[str, Any]) -> str:
        """Generate content hash for blockchain storage"""
        # Create deterministic hash from content data
        content_str = json.dumps({
            'content_id': content_data.get('content_id', ''),
            'creator_id': content_data.get('creator_id', ''),
            'content_type': content_data.get('content_type', ''),
            'creation_timestamp': content_data.get('creation_timestamp', ''),
            'file_hash': content_data.get('file_hash', '')
        }, sort_keys=True)
        
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _get_cached_validation(self, content_id: str) -> Optional[RightsValidationResult]:
        """Retrieve cached validation result"""
        if content_id in self.rights_cache:
            cached_data = self.rights_cache[content_id]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['result']
            else:
                del self.rights_cache[content_id]
        return None
    
    def _cache_validation_result(self, content_id: str, result: RightsValidationResult):
        """Cache validation result"""
        self.rights_cache[content_id] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def _update_monitoring_metrics(self, processing_time: float, is_valid: bool):
        """Update monitoring performance metrics"""
        self.monitoring_metrics['total_validations'] += 1
        self.monitoring_metrics['blockchain_queries'] += 1
        
        if is_valid:
            self.monitoring_metrics['successful_validations'] += 1
        else:
            self.monitoring_metrics['failed_validations'] += 1
        
        # Update average response time
        current_avg = self.monitoring_metrics['average_response_time']
        total = self.monitoring_metrics['total_validations']
        self.monitoring_metrics['average_response_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    async def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring metrics"""
        return {
            "performance_metrics": self.monitoring_metrics.copy(),
            "cache_statistics": {
                "cached_validations": len(self.rights_cache),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "cache_ttl_minutes": self.cache_ttl / 60
            },
            "network_status": {
                network.value: await self._check_network_status(network)
                for network in self.network_configs.keys()
            },
            "validation_thresholds": self.validation_thresholds.copy(),
            "supported_networks": [network.value for network in self.network_configs.keys()],
            "supported_rights_types": [rights_type.value for rights_type in RightsType]
        }
    
    async def _check_network_status(self, network: BlockchainNetwork) -> Dict[str, Any]:
        """Check blockchain network status"""
        # Simulate network status check
        import random
        return {
            "status": "operational",
            "block_height": random.randint(15000000, 18000000),
            "avg_block_time": random.uniform(12, 15),
            "gas_price_gwei": random.randint(20, 100),
            "network_congestion": random.choice(["low", "medium", "high"])
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        # Mock cache hit rate calculation
        return 0.65 if self.monitoring_metrics['total_validations'] > 0 else 0.0

# Global blockchain rights monitor instance
blockchain_rights_monitor = BlockchainRightsMonitor()

async def validate_content_rights(content_data: Dict[str, Any]) -> RightsValidationResult:
    """Global function for blockchain rights validation"""
    return await blockchain_rights_monitor.validate_content_rights(content_data)

async def register_content_rights(content_data: Dict[str, Any], rights_data: Dict[str, Any]) -> Dict[str, Any]:
    """Global function for blockchain rights registration"""
    return await blockchain_rights_monitor.register_content_rights(content_data, rights_data)

async def get_monitoring_metrics() -> Dict[str, Any]:
    """Global function to get blockchain monitoring metrics"""
    return await blockchain_rights_monitor.get_monitoring_metrics()
