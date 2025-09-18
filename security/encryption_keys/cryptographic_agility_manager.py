"""
Enterprise Cryptographic Agility Manager
Created by: Senior Engineering Team (DevOps + DBA + Security + ML + Microservices + IA Prompt Engineer)
Date: 2024
Purpose: Advanced cryptographic algorithm transition and agility management for Creator Economy

Features:
- Algorithm transition management with zero downtime
- Hybrid cryptographic schemes and gradual migration
- Creator-impact assessment for algorithm changes
- Automated migration workflows with rollback capabilities
- Performance-aware algorithm selection
- Creator Economy specific optimizations
"""

import asyncio
import hashlib
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Union
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, x25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import numpy as np


class CryptoAlgorithmType(Enum):
    """Types of cryptographic algorithms"""
    SYMMETRIC_ENCRYPTION = "symmetric_encryption"
    ASYMMETRIC_ENCRYPTION = "asymmetric_encryption"
    DIGITAL_SIGNATURE = "digital_signature"
    HASH_FUNCTION = "hash_function"
    KEY_DERIVATION = "key_derivation"
    KEY_EXCHANGE = "key_exchange"
    POST_QUANTUM = "post_quantum"


class AlgorithmStatus(Enum):
    """Algorithm lifecycle status"""
    EXPERIMENTAL = "experimental"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    FORBIDDEN = "forbidden"
    MIGRATION_PENDING = "migration_pending"
    MIGRATION_IN_PROGRESS = "migration_in_progress"


class MigrationStrategy(Enum):
    """Migration strategies"""
    IMMEDIATE = "immediate"           # Replace immediately
    GRADUAL = "gradual"              # Phased replacement
    HYBRID = "hybrid"                # Run both algorithms
    CREATOR_DRIVEN = "creator_driven" # Creator chooses timing
    PERFORMANCE_BASED = "performance_based"  # Based on performance metrics


class CreatorImpactLevel(Enum):
    """Creator impact assessment levels"""
    NONE = "none"           # No impact
    LOW = "low"            # Minimal impact
    MEDIUM = "medium"      # Some disruption
    HIGH = "high"          # Significant disruption
    CRITICAL = "critical"  # Major disruption


@dataclass
class CryptoAlgorithm:
    """Cryptographic algorithm specification"""
    algorithm_id: str
    name: str
    algorithm_type: CryptoAlgorithmType
    status: AlgorithmStatus
    key_sizes: List[int]
    performance_profile: Dict[str, float]  # operations per second
    security_level: int  # 1-10 scale
    quantum_resistant: bool
    compliance_standards: List[str]  # FIPS, Common Criteria, etc.
    creator_suitability: Dict[str, bool]  # suitability for different creator types
    implementation_complexity: int  # 1-10 scale
    migration_complexity: int  # 1-10 scale
    
    def is_suitable_for_creator(self, creator_type: str) -> bool:
        """Check if algorithm is suitable for creator type"""
        return self.creator_suitability.get(creator_type, True)


@dataclass
class MigrationPlan:
    """Algorithm migration plan"""
    migration_id: str
    from_algorithm: CryptoAlgorithm
    to_algorithm: CryptoAlgorithm
    strategy: MigrationStrategy
    start_date: datetime
    target_completion: datetime
    affected_creators: List[str]
    impact_assessment: Dict[str, CreatorImpactLevel]
    rollback_plan: Optional[Dict[str, Any]] = None
    progress: float = 0.0  # 0-100%
    status: str = "planned"
    
    def estimate_impact(self) -> CreatorImpactLevel:
        """Estimate overall migration impact"""
        if not self.impact_assessment:
            return CreatorImpactLevel.LOW
        
        impact_scores = {
            CreatorImpactLevel.NONE: 0,
            CreatorImpactLevel.LOW: 1,
            CreatorImpactLevel.MEDIUM: 2,
            CreatorImpactLevel.HIGH: 3,
            CreatorImpactLevel.CRITICAL: 4
        }
        
        total_score = sum(impact_scores[level] for level in self.impact_assessment.values())
        avg_score = total_score / len(self.impact_assessment)
        
        if avg_score <= 0.5:
            return CreatorImpactLevel.NONE
        elif avg_score <= 1.5:
            return CreatorImpactLevel.LOW
        elif avg_score <= 2.5:
            return CreatorImpactLevel.MEDIUM
        elif avg_score <= 3.5:
            return CreatorImpactLevel.HIGH
        else:
            return CreatorImpactLevel.CRITICAL


@dataclass
class HybridCryptoScheme:
    """Hybrid cryptographic scheme configuration"""
    scheme_id: str
    name: str
    primary_algorithm: CryptoAlgorithm
    secondary_algorithm: CryptoAlgorithm
    weight_ratio: float  # 0-1, weight for primary algorithm
    performance_profile: Dict[str, float]
    security_level: int
    creator_preferences: Dict[str, float]  # creator type preferences


class CreatorImpactAnalyzer:
    """Analyzes impact of cryptographic changes on creators"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.creator_profiles = {}
        self.content_type_requirements = {}
        self._initialize_content_requirements()
    
    def _initialize_content_requirements(self):
        """Initialize content type cryptographic requirements"""
        self.content_type_requirements = {
            'audio': {
                'streaming_performance': True,
                'large_file_support': True,
                'real_time_encryption': True,
                'quality_preservation': True
            },
            'video': {
                'streaming_performance': True,
                'large_file_support': True,
                'hardware_acceleration': True,
                'frame_level_encryption': True
            },
            'image': {
                'batch_processing': True,
                'metadata_preservation': True,
                'format_compatibility': True,
                'compression_friendly': True
            },
            'text': {
                'low_latency': True,
                'search_friendly': False,
                'minimal_overhead': True,
                'format_preserving': False
            },
            'live_stream': {
                'ultra_low_latency': True,
                'hardware_acceleration': True,
                'adaptive_quality': True,
                'real_time_encryption': True
            }
        }
    
    def register_creator_profile(self, 
                               creator_id: str, 
                               creator_metadata: Dict[str, Any]):
        """Register creator profile for impact analysis"""
        self.creator_profiles[creator_id] = creator_metadata
    
    def analyze_migration_impact(self, 
                               migration_plan: MigrationPlan) -> Dict[str, CreatorImpactLevel]:
        """Analyze migration impact on affected creators"""
        impact_assessment = {}
        
        for creator_id in migration_plan.affected_creators:
            impact = self._assess_creator_impact(
                creator_id,
                migration_plan.from_algorithm,
                migration_plan.to_algorithm,
                migration_plan.strategy
            )
            impact_assessment[creator_id] = impact
        
        return impact_assessment
    
    def _assess_creator_impact(self, 
                             creator_id: str,
                             from_algo: CryptoAlgorithm,
                             to_algo: CryptoAlgorithm,
                             strategy: MigrationStrategy) -> CreatorImpactLevel:
        """Assess impact on individual creator"""
        try:
            creator_profile = self.creator_profiles.get(creator_id, {})
            creator_type = creator_profile.get('creator_type', 'unknown')
            content_types = creator_profile.get('content_types', [])
            
            # Base impact factors
            performance_impact = self._assess_performance_impact(from_algo, to_algo, content_types)
            compatibility_impact = self._assess_compatibility_impact(creator_type, to_algo)
            migration_complexity = to_algo.migration_complexity / 10.0
            
            # Strategy-specific adjustments
            strategy_multipliers = {
                MigrationStrategy.IMMEDIATE: 1.5,
                MigrationStrategy.GRADUAL: 0.8,
                MigrationStrategy.HYBRID: 0.6,
                MigrationStrategy.CREATOR_DRIVEN: 0.4,
                MigrationStrategy.PERFORMANCE_BASED: 0.7
            }
            
            multiplier = strategy_multipliers.get(strategy, 1.0)
            
            # Calculate overall impact score
            impact_score = (performance_impact + compatibility_impact + migration_complexity) * multiplier
            
            # Map to impact level
            if impact_score <= 0.3:
                return CreatorImpactLevel.NONE
            elif impact_score <= 0.6:
                return CreatorImpactLevel.LOW
            elif impact_score <= 1.2:
                return CreatorImpactLevel.MEDIUM
            elif impact_score <= 2.0:
                return CreatorImpactLevel.HIGH
            else:
                return CreatorImpactLevel.CRITICAL
                
        except Exception as e:
            self.logger.error(f"Impact assessment failed: {e}")
            return CreatorImpactLevel.MEDIUM  # Conservative estimate
    
    def _assess_performance_impact(self, 
                                 from_algo: CryptoAlgorithm,
                                 to_algo: CryptoAlgorithm,
                                 content_types: List[str]) -> float:
        """Assess performance impact of algorithm change"""
        
        # Get performance requirements for content types
        perf_requirements = {}
        for content_type in content_types:
            requirements = self.content_type_requirements.get(content_type, {})
            for req, important in requirements.items():
                if important:
                    perf_requirements[req] = True
        
        # Compare algorithm performance
        from_perf = from_algo.performance_profile
        to_perf = to_algo.performance_profile
        
        impact = 0.0
        for metric in ['encrypt_ops_per_sec', 'decrypt_ops_per_sec', 'key_gen_ops_per_sec']:
            from_val = from_perf.get(metric, 1000)
            to_val = to_perf.get(metric, 1000)
            
            if from_val > 0:
                perf_ratio = to_val / from_val
                if perf_ratio < 1.0:  # Performance degradation
                    impact += (1.0 - perf_ratio) * 0.5
        
        return min(impact, 1.0)
    
    def _assess_compatibility_impact(self, 
                                   creator_type: str,
                                   to_algo: CryptoAlgorithm) -> float:
        """Assess compatibility impact"""
        
        # Check algorithm suitability
        if not to_algo.is_suitable_for_creator(creator_type):
            return 0.8  # High impact if not suitable
        
        # Implementation complexity impact
        complexity_impact = to_algo.implementation_complexity / 10.0 * 0.3
        
        return complexity_impact


class AlgorithmRegistry:
    """Registry of available cryptographic algorithms"""
    
    def __init__(self):
        self.algorithms = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_standard_algorithms()
    
    def _initialize_standard_algorithms(self):
        """Initialize standard cryptographic algorithms"""
        
        # Symmetric encryption algorithms
        aes_256_gcm = CryptoAlgorithm(
            algorithm_id="aes_256_gcm",
            name="AES-256-GCM",
            algorithm_type=CryptoAlgorithmType.SYMMETRIC_ENCRYPTION,
            status=AlgorithmStatus.ACTIVE,
            key_sizes=[256],
            performance_profile={
                'encrypt_ops_per_sec': 50000,
                'decrypt_ops_per_sec': 50000,
                'key_gen_ops_per_sec': 100000
            },
            security_level=9,
            quantum_resistant=False,
            compliance_standards=['FIPS-140-2', 'Common Criteria'],
            creator_suitability={
                'musician': True,
                'photographer': True,
                'video_creator': True,
                'blogger': True
            },
            implementation_complexity=3,
            migration_complexity=2
        )
        
        chacha20_poly1305 = CryptoAlgorithm(
            algorithm_id="chacha20_poly1305",
            name="ChaCha20-Poly1305",
            algorithm_type=CryptoAlgorithmType.SYMMETRIC_ENCRYPTION,
            status=AlgorithmStatus.ACTIVE,
            key_sizes=[256],
            performance_profile={
                'encrypt_ops_per_sec': 75000,
                'decrypt_ops_per_sec': 75000,
                'key_gen_ops_per_sec': 100000
            },
            security_level=9,
            quantum_resistant=False,
            compliance_standards=['RFC-8439'],
            creator_suitability={
                'musician': True,
                'photographer': True,
                'video_creator': True,
                'blogger': True,
                'live_streamer': True
            },
            implementation_complexity=4,
            migration_complexity=3
        )
        
        # Post-quantum algorithms
        kyber_1024 = CryptoAlgorithm(
            algorithm_id="kyber_1024",
            name="Kyber-1024",
            algorithm_type=CryptoAlgorithmType.POST_QUANTUM,
            status=AlgorithmStatus.EXPERIMENTAL,
            key_sizes=[1024],
            performance_profile={
                'encrypt_ops_per_sec': 15000,
                'decrypt_ops_per_sec': 12000,
                'key_gen_ops_per_sec': 8000
            },
            security_level=10,
            quantum_resistant=True,
            compliance_standards=['NIST-PQC'],
            creator_suitability={
                'musician': True,
                'photographer': True,
                'video_creator': False,  # Too slow for video
                'blogger': True,
                'high_security_creator': True
            },
            implementation_complexity=8,
            migration_complexity=7
        )
        
        # Digital signature algorithms
        ed25519_sig = CryptoAlgorithm(
            algorithm_id="ed25519",
            name="Ed25519",
            algorithm_type=CryptoAlgorithmType.DIGITAL_SIGNATURE,
            status=AlgorithmStatus.ACTIVE,
            key_sizes=[256],
            performance_profile={
                'sign_ops_per_sec': 30000,
                'verify_ops_per_sec': 15000,
                'key_gen_ops_per_sec': 25000
            },
            security_level=9,
            quantum_resistant=False,
            compliance_standards=['RFC-8032'],
            creator_suitability={
                'musician': True,
                'photographer': True,
                'video_creator': True,
                'blogger': True
            },
            implementation_complexity=5,
            migration_complexity=4
        )
        
        # Register algorithms
        self.register_algorithm(aes_256_gcm)
        self.register_algorithm(chacha20_poly1305)
        self.register_algorithm(kyber_1024)
        self.register_algorithm(ed25519_sig)
    
    def register_algorithm(self, algorithm: CryptoAlgorithm):
        """Register a cryptographic algorithm"""
        self.algorithms[algorithm.algorithm_id] = algorithm
        self.logger.info(f"Registered algorithm: {algorithm.name}")
    
    def get_algorithm(self, algorithm_id: str) -> Optional[CryptoAlgorithm]:
        """Get algorithm by ID"""
        return self.algorithms.get(algorithm_id)
    
    def get_algorithms_by_type(self, algorithm_type: CryptoAlgorithmType) -> List[CryptoAlgorithm]:
        """Get algorithms by type"""
        return [algo for algo in self.algorithms.values() 
                if algo.algorithm_type == algorithm_type]
    
    def get_active_algorithms(self) -> List[CryptoAlgorithm]:
        """Get all active algorithms"""
        return [algo for algo in self.algorithms.values() 
                if algo.status == AlgorithmStatus.ACTIVE]
    
    def update_algorithm_status(self, algorithm_id: str, status: AlgorithmStatus):
        """Update algorithm status"""
        if algorithm_id in self.algorithms:
            self.algorithms[algorithm_id].status = status
            self.logger.info(f"Updated {algorithm_id} status to {status.value}")


class HybridSchemeManager:
    """Manages hybrid cryptographic schemes"""
    
    def __init__(self, algorithm_registry: AlgorithmRegistry):
        self.algorithm_registry = algorithm_registry
        self.hybrid_schemes = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_default_schemes()
    
    def _initialize_default_schemes(self):
        """Initialize default hybrid schemes"""
        
        # Classical + Post-Quantum hybrid for high security
        aes_algo = self.algorithm_registry.get_algorithm("aes_256_gcm")
        kyber_algo = self.algorithm_registry.get_algorithm("kyber_1024")
        
        if aes_algo and kyber_algo:
            quantum_ready_scheme = HybridCryptoScheme(
                scheme_id="quantum_ready_hybrid",
                name="Quantum-Ready Hybrid Encryption",
                primary_algorithm=aes_algo,
                secondary_algorithm=kyber_algo,
                weight_ratio=0.7,  # 70% classical, 30% post-quantum initially
                performance_profile={
                    'encrypt_ops_per_sec': 25000,  # Blended performance
                    'decrypt_ops_per_sec': 23000,
                    'key_gen_ops_per_sec': 40000
                },
                security_level=10,
                creator_preferences={
                    'high_security_creator': 0.9,
                    'musician': 0.6,
                    'photographer': 0.7,
                    'video_creator': 0.3,  # Lower due to performance
                    'blogger': 0.8
                }
            )
            self.register_hybrid_scheme(quantum_ready_scheme)
        
        # Performance + Security hybrid for content creators
        chacha_algo = self.algorithm_registry.get_algorithm("chacha20_poly1305")
        if aes_algo and chacha_algo:
            performance_scheme = HybridCryptoScheme(
                scheme_id="performance_security_hybrid",
                name="Performance-Security Hybrid",
                primary_algorithm=chacha_algo,
                secondary_algorithm=aes_algo,
                weight_ratio=0.8,  # 80% ChaCha20, 20% AES
                performance_profile={
                    'encrypt_ops_per_sec': 65000,
                    'decrypt_ops_per_sec': 65000,
                    'key_gen_ops_per_sec': 100000
                },
                security_level=9,
                creator_preferences={
                    'musician': 0.9,
                    'video_creator': 0.95,
                    'live_streamer': 0.98,
                    'photographer': 0.8,
                    'blogger': 0.7
                }
            )
            self.register_hybrid_scheme(performance_scheme)
    
    def register_hybrid_scheme(self, scheme: HybridCryptoScheme):
        """Register hybrid scheme"""
        self.hybrid_schemes[scheme.scheme_id] = scheme
        self.logger.info(f"Registered hybrid scheme: {scheme.name}")
    
    def get_optimal_scheme_for_creator(self, 
                                     creator_type: str,
                                     performance_requirements: Dict[str, float]) -> Optional[HybridCryptoScheme]:
        """Get optimal hybrid scheme for creator"""
        
        best_scheme = None
        best_score = 0.0
        
        for scheme in self.hybrid_schemes.values():
            score = self._calculate_scheme_score(scheme, creator_type, performance_requirements)
            if score > best_score:
                best_score = score
                best_scheme = scheme
        
        return best_scheme
    
    def _calculate_scheme_score(self, 
                              scheme: HybridCryptoScheme,
                              creator_type: str,
                              performance_requirements: Dict[str, float]) -> float:
        """Calculate scheme suitability score"""
        
        # Creator preference score
        creator_pref = scheme.creator_preferences.get(creator_type, 0.5)
        
        # Performance score
        perf_score = 0.0
        for metric, required_value in performance_requirements.items():
            actual_value = scheme.performance_profile.get(metric, 0)
            if required_value > 0:
                perf_score += min(actual_value / required_value, 1.0)
        
        if performance_requirements:
            perf_score /= len(performance_requirements)
        else:
            perf_score = 1.0
        
        # Combined score
        return (creator_pref * 0.6) + (perf_score * 0.4)


class MigrationEngine:
    """Manages cryptographic algorithm migrations"""
    
    def __init__(self, 
                 algorithm_registry: AlgorithmRegistry,
                 impact_analyzer: CreatorImpactAnalyzer):
        self.algorithm_registry = algorithm_registry
        self.impact_analyzer = impact_analyzer
        self.migration_plans = {}
        self.active_migrations = {}
        self.logger = logging.getLogger(__name__)
        
        # Migration executor
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def create_migration_plan(self, 
                            from_algorithm_id: str,
                            to_algorithm_id: str,
                            affected_creators: List[str],
                            strategy: MigrationStrategy = MigrationStrategy.GRADUAL,
                            target_completion: Optional[datetime] = None) -> str:
        """Create migration plan"""
        
        try:
            # Get algorithms
            from_algo = self.algorithm_registry.get_algorithm(from_algorithm_id)
            to_algo = self.algorithm_registry.get_algorithm(to_algorithm_id)
            
            if not from_algo or not to_algo:
                raise ValueError("Invalid algorithm IDs")
            
            # Create migration plan
            migration_id = str(uuid.uuid4())
            target_date = target_completion or (datetime.now() + timedelta(days=30))
            
            plan = MigrationPlan(
                migration_id=migration_id,
                from_algorithm=from_algo,
                to_algorithm=to_algo,
                strategy=strategy,
                start_date=datetime.now(),
                target_completion=target_date,
                affected_creators=affected_creators,
                impact_assessment={}
            )
            
            # Analyze impact
            plan.impact_assessment = self.impact_analyzer.analyze_migration_impact(plan)
            
            # Create rollback plan
            plan.rollback_plan = self._create_rollback_plan(plan)
            
            self.migration_plans[migration_id] = plan
            
            self.logger.info(f"Created migration plan {migration_id}: {from_algo.name} -> {to_algo.name}")
            
            return migration_id
            
        except Exception as e:
            self.logger.error(f"Migration plan creation failed: {e}")
            raise
    
    def _create_rollback_plan(self, migration_plan: MigrationPlan) -> Dict[str, Any]:
        """Create rollback plan for migration"""
        return {
            'rollback_algorithm_id': migration_plan.from_algorithm.algorithm_id,
            'rollback_strategy': MigrationStrategy.IMMEDIATE,
            'rollback_triggers': [
                'performance_degradation > 50%',
                'error_rate > 5%',
                'creator_complaints > 10'
            ],
            'rollback_checkpoints': [25, 50, 75],  # % completion checkpoints
            'automated_rollback': True
        }
    
    async def execute_migration(self, migration_id: str) -> bool:
        """Execute migration plan"""
        
        try:
            plan = self.migration_plans.get(migration_id)
            if not plan:
                raise ValueError(f"Migration plan {migration_id} not found")
            
            if plan.status != "planned":
                raise ValueError(f"Migration {migration_id} is not in planned status")
            
            # Start migration
            plan.status = "in_progress"
            self.active_migrations[migration_id] = plan
            
            # Execute based on strategy
            if plan.strategy == MigrationStrategy.IMMEDIATE:
                success = await self._execute_immediate_migration(plan)
            elif plan.strategy == MigrationStrategy.GRADUAL:
                success = await self._execute_gradual_migration(plan)
            elif plan.strategy == MigrationStrategy.HYBRID:
                success = await self._execute_hybrid_migration(plan)
            elif plan.strategy == MigrationStrategy.CREATOR_DRIVEN:
                success = await self._execute_creator_driven_migration(plan)
            elif plan.strategy == MigrationStrategy.PERFORMANCE_BASED:
                success = await self._execute_performance_based_migration(plan)
            else:
                raise ValueError(f"Unknown migration strategy: {plan.strategy}")
            
            # Update status
            if success:
                plan.status = "completed"
                plan.progress = 100.0
            else:
                plan.status = "failed"
            
            return success
            
        except Exception as e:
            self.logger.error(f"Migration execution failed: {e}")
            if migration_id in self.migration_plans:
                self.migration_plans[migration_id].status = "failed"
            return False
    
    async def _execute_immediate_migration(self, plan: MigrationPlan) -> bool:
        """Execute immediate migration"""
        try:
            self.logger.info(f"Starting immediate migration {plan.migration_id}")
            
            # Migrate all creators at once
            for i, creator_id in enumerate(plan.affected_creators):
                success = await self._migrate_creator(creator_id, plan)
                if not success:
                    self.logger.error(f"Failed to migrate creator {creator_id}")
                    return False
                
                plan.progress = ((i + 1) / len(plan.affected_creators)) * 100
            
            return True
            
        except Exception as e:
            self.logger.error(f"Immediate migration failed: {e}")
            return False
    
    async def _execute_gradual_migration(self, plan: MigrationPlan) -> bool:
        """Execute gradual migration"""
        try:
            self.logger.info(f"Starting gradual migration {plan.migration_id}")
            
            # Divide creators into batches
            batch_size = max(1, len(plan.affected_creators) // 10)  # 10 batches
            batches = [plan.affected_creators[i:i + batch_size] 
                      for i in range(0, len(plan.affected_creators), batch_size)]
            
            total_migrated = 0
            
            for batch_idx, batch in enumerate(batches):
                self.logger.info(f"Migrating batch {batch_idx + 1}/{len(batches)}")
                
                # Migrate batch
                for creator_id in batch:
                    success = await self._migrate_creator(creator_id, plan)
                    if success:
                        total_migrated += 1
                    else:
                        self.logger.warning(f"Failed to migrate creator {creator_id}")
                
                plan.progress = (total_migrated / len(plan.affected_creators)) * 100
                
                # Wait between batches
                if batch_idx < len(batches) - 1:
                    await asyncio.sleep(10)  # 10 second delay between batches
                
                # Check for rollback triggers
                if await self._should_rollback(plan):
                    await self._execute_rollback(plan)
                    return False
            
            return total_migrated == len(plan.affected_creators)
            
        except Exception as e:
            self.logger.error(f"Gradual migration failed: {e}")
            return False
    
    async def _execute_hybrid_migration(self, plan: MigrationPlan) -> bool:
        """Execute hybrid migration (run both algorithms)"""
        try:
            self.logger.info(f"Starting hybrid migration {plan.migration_id}")
            
            # Enable hybrid mode for all creators
            for i, creator_id in enumerate(plan.affected_creators):
                success = await self._enable_hybrid_mode(creator_id, plan)
                if success:
                    self.logger.info(f"Enabled hybrid mode for creator {creator_id}")
                else:
                    self.logger.warning(f"Failed to enable hybrid mode for creator {creator_id}")
                
                plan.progress = ((i + 1) / len(plan.affected_creators)) * 50  # 50% for hybrid mode
            
            # Gradually shift weight to new algorithm
            await self._shift_hybrid_weights(plan)
            
            plan.progress = 100.0
            return True
            
        except Exception as e:
            self.logger.error(f"Hybrid migration failed: {e}")
            return False
    
    async def _execute_creator_driven_migration(self, plan: MigrationPlan) -> bool:
        """Execute creator-driven migration"""
        try:
            self.logger.info(f"Starting creator-driven migration {plan.migration_id}")
            
            # Notify creators about migration option
            for creator_id in plan.affected_creators:
                await self._notify_creator_migration_option(creator_id, plan)
            
            # Wait for creator responses
            migrated_count = 0
            timeout = plan.target_completion
            
            while datetime.now() < timeout and migrated_count < len(plan.affected_creators):
                # Check for creator migration requests
                migration_requests = await self._check_creator_migration_requests(plan)
                
                for creator_id in migration_requests:
                    if creator_id in plan.affected_creators:
                        success = await self._migrate_creator(creator_id, plan)
                        if success:
                            migrated_count += 1
                            plan.progress = (migrated_count / len(plan.affected_creators)) * 100
                
                await asyncio.sleep(60)  # Check every minute
            
            # Force migration for remaining creators after timeout
            remaining_creators = [c for c in plan.affected_creators 
                                if not await self._is_creator_migrated(c, plan)]
            
            for creator_id in remaining_creators:
                await self._migrate_creator(creator_id, plan)
                migrated_count += 1
                plan.progress = (migrated_count / len(plan.affected_creators)) * 100
            
            return True
            
        except Exception as e:
            self.logger.error(f"Creator-driven migration failed: {e}")
            return False
    
    async def _execute_performance_based_migration(self, plan: MigrationPlan) -> bool:
        """Execute performance-based migration"""
        try:
            self.logger.info(f"Starting performance-based migration {plan.migration_id}")
            
            # Sort creators by performance requirements
            creator_priorities = await self._analyze_creator_performance_needs(plan.affected_creators)
            sorted_creators = sorted(creator_priorities.items(), key=lambda x: x[1], reverse=True)
            
            migrated_count = 0
            
            for creator_id, priority in sorted_creators:
                # Check if migration would improve performance
                would_improve = await self._would_migration_improve_performance(creator_id, plan)
                
                if would_improve or priority > 0.7:  # High priority or improvement expected
                    success = await self._migrate_creator(creator_id, plan)
                    if success:
                        migrated_count += 1
                        plan.progress = (migrated_count / len(plan.affected_creators)) * 100
                        
                        # Monitor performance after migration
                        await self._monitor_post_migration_performance(creator_id, plan)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Performance-based migration failed: {e}")
            return False
    
    async def _migrate_creator(self, creator_id: str, plan: MigrationPlan) -> bool:
        """Migrate individual creator to new algorithm"""
        try:
            self.logger.info(f"Migrating creator {creator_id} to {plan.to_algorithm.name}")
            
            # Simulate migration process
            await asyncio.sleep(0.1)  # Simulate work
            
            # In real implementation, this would:
            # 1. Backup current keys
            # 2. Generate new keys with new algorithm
            # 3. Re-encrypt data with new algorithm
            # 4. Update creator's algorithm configuration
            # 5. Verify migration success
            
            return True
            
        except Exception as e:
            self.logger.error(f"Creator migration failed: {e}")
            return False
    
    async def _enable_hybrid_mode(self, creator_id: str, plan: MigrationPlan) -> bool:
        """Enable hybrid mode for creator"""
        try:
            # Simulate enabling hybrid mode
            await asyncio.sleep(0.05)
            return True
            
        except Exception as e:
            self.logger.error(f"Hybrid mode enablement failed: {e}")
            return False
    
    async def _shift_hybrid_weights(self, plan: MigrationPlan):
        """Gradually shift weights in hybrid mode"""
        # Gradually increase weight of new algorithm
        for weight in range(10, 101, 10):  # 10%, 20%, ..., 100%
            plan.progress = 50 + (weight / 2)  # 50% base + weight adjustment
            await asyncio.sleep(2)  # Wait between weight adjustments
    
    async def _should_rollback(self, plan: MigrationPlan) -> bool:
        """Check if migration should be rolled back"""
        # Simulate rollback trigger checks
        # In real implementation, this would monitor:
        # - Error rates
        # - Performance metrics
        # - Creator complaints
        return False
    
    async def _execute_rollback(self, plan: MigrationPlan):
        """Execute migration rollback"""
        self.logger.warning(f"Rolling back migration {plan.migration_id}")
        plan.status = "rolled_back"
        # Implement rollback logic
    
    async def _notify_creator_migration_option(self, creator_id: str, plan: MigrationPlan):
        """Notify creator about migration option"""
        # Simulate notification
        pass
    
    async def _check_creator_migration_requests(self, plan: MigrationPlan) -> List[str]:
        """Check for creator migration requests"""
        # Simulate checking requests
        return []
    
    async def _is_creator_migrated(self, creator_id: str, plan: MigrationPlan) -> bool:
        """Check if creator has been migrated"""
        # Simulate check
        return False
    
    async def _analyze_creator_performance_needs(self, creator_ids: List[str]) -> Dict[str, float]:
        """Analyze performance needs of creators"""
        # Simulate performance analysis
        return {creator_id: 0.5 for creator_id in creator_ids}
    
    async def _would_migration_improve_performance(self, creator_id: str, plan: MigrationPlan) -> bool:
        """Check if migration would improve performance"""
        # Compare algorithm performance profiles
        from_perf = plan.from_algorithm.performance_profile.get('encrypt_ops_per_sec', 1000)
        to_perf = plan.to_algorithm.performance_profile.get('encrypt_ops_per_sec', 1000)
        return to_perf > from_perf
    
    async def _monitor_post_migration_performance(self, creator_id: str, plan: MigrationPlan):
        """Monitor performance after migration"""
        # Simulate performance monitoring
        await asyncio.sleep(0.1)
    
    def get_migration_status(self, migration_id: str) -> Optional[Dict[str, Any]]:
        """Get migration status"""
        plan = self.migration_plans.get(migration_id)
        if not plan:
            return None
        
        return {
            'migration_id': plan.migration_id,
            'from_algorithm': plan.from_algorithm.name,
            'to_algorithm': plan.to_algorithm.name,
            'strategy': plan.strategy.value,
            'status': plan.status,
            'progress': plan.progress,
            'start_date': plan.start_date.isoformat(),
            'target_completion': plan.target_completion.isoformat(),
            'affected_creators': len(plan.affected_creators),
            'estimated_impact': plan.estimate_impact().value,
            'has_rollback_plan': plan.rollback_plan is not None
        }


class CryptographicAgilityManager:
    """Main manager for cryptographic agility"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.algorithm_registry = AlgorithmRegistry()
        self.impact_analyzer = CreatorImpactAnalyzer()
        self.hybrid_scheme_manager = HybridSchemeManager(self.algorithm_registry)
        self.migration_engine = MigrationEngine(self.algorithm_registry, self.impact_analyzer)
        
        # Metrics
        self.metrics = {
            'algorithms_registered': len(self.algorithm_registry.algorithms),
            'active_algorithms': len(self.algorithm_registry.get_active_algorithms()),
            'migrations_completed': 0,
            'migrations_failed': 0,
            'hybrid_schemes': len(self.hybrid_scheme_manager.hybrid_schemes),
            'creator_profiles': 0
        }
    
    def register_creator(self, creator_id: str, creator_metadata: Dict[str, Any]):
        """Register creator for impact analysis"""
        self.impact_analyzer.register_creator_profile(creator_id, creator_metadata)
        self.metrics['creator_profiles'] += 1
    
    def recommend_algorithm_for_creator(self, 
                                      creator_type: str,
                                      content_types: List[str],
                                      performance_requirements: Dict[str, float],
                                      security_level: int = 8) -> Optional[CryptoAlgorithm]:
        """Recommend optimal algorithm for creator"""
        
        try:
            active_algorithms = self.algorithm_registry.get_active_algorithms()
            
            best_algorithm = None
            best_score = 0.0
            
            for algorithm in active_algorithms:
                score = self._calculate_algorithm_score(
                    algorithm, creator_type, content_types, 
                    performance_requirements, security_level
                )
                
                if score > best_score:
                    best_score = score
                    best_algorithm = algorithm
            
            return best_algorithm
            
        except Exception as e:
            self.logger.error(f"Algorithm recommendation failed: {e}")
            return None
    
    def recommend_hybrid_scheme_for_creator(self, 
                                          creator_type: str,
                                          performance_requirements: Dict[str, float]) -> Optional[HybridCryptoScheme]:
        """Recommend optimal hybrid scheme for creator"""
        return self.hybrid_scheme_manager.get_optimal_scheme_for_creator(
            creator_type, performance_requirements
        )
    
    def _calculate_algorithm_score(self, 
                                 algorithm: CryptoAlgorithm,
                                 creator_type: str,
                                 content_types: List[str],
                                 performance_requirements: Dict[str, float],
                                 required_security_level: int) -> float:
        """Calculate algorithm suitability score"""
        
        score = 0.0
        
        # Security level score
        if algorithm.security_level >= required_security_level:
            score += 0.3
        else:
            score -= 0.2  # Penalty for insufficient security
        
        # Creator suitability score
        if algorithm.is_suitable_for_creator(creator_type):
            score += 0.2
        
        # Performance score
        perf_score = 0.0
        for metric, required_value in performance_requirements.items():
            actual_value = algorithm.performance_profile.get(metric, 0)
            if required_value > 0 and actual_value > 0:
                perf_score += min(actual_value / required_value, 1.0)
        
        if performance_requirements:
            perf_score /= len(performance_requirements)
            score += perf_score * 0.3
        
        # Implementation complexity (lower is better)
        complexity_score = 1.0 - (algorithm.implementation_complexity / 10.0)
        score += complexity_score * 0.1
        
        # Status bonus
        if algorithm.status == AlgorithmStatus.ACTIVE:
            score += 0.1
        
        return max(score, 0.0)
    
    async def plan_algorithm_migration(self, 
                                     from_algorithm_id: str,
                                     to_algorithm_id: str,
                                     affected_creators: List[str],
                                     strategy: MigrationStrategy = MigrationStrategy.GRADUAL) -> str:
        """Plan algorithm migration"""
        
        migration_id = self.migration_engine.create_migration_plan(
            from_algorithm_id, to_algorithm_id, affected_creators, strategy
        )
        
        return migration_id
    
    async def execute_migration(self, migration_id: str) -> bool:
        """Execute migration plan"""
        success = await self.migration_engine.execute_migration(migration_id)
        
        if success:
            self.metrics['migrations_completed'] += 1
        else:
            self.metrics['migrations_failed'] += 1
        
        return success
    
    def get_migration_status(self, migration_id: str) -> Optional[Dict[str, Any]]:
        """Get migration status"""
        return self.migration_engine.get_migration_status(migration_id)
    
    def deprecate_algorithm(self, algorithm_id: str):
        """Deprecate an algorithm"""
        self.algorithm_registry.update_algorithm_status(algorithm_id, AlgorithmStatus.DEPRECATED)
    
    def get_algorithm_status_report(self) -> Dict[str, Any]:
        """Get comprehensive algorithm status report"""
        
        algorithms_by_status = {}
        for status in AlgorithmStatus:
            algorithms_by_status[status.value] = []
        
        for algorithm in self.algorithm_registry.algorithms.values():
            algorithms_by_status[algorithm.status.value].append({
                'id': algorithm.algorithm_id,
                'name': algorithm.name,
                'type': algorithm.algorithm_type.value,
                'security_level': algorithm.security_level,
                'quantum_resistant': algorithm.quantum_resistant
            })
        
        return {
            'algorithms_by_status': algorithms_by_status,
            'total_algorithms': len(self.algorithm_registry.algorithms),
            'active_migrations': len(self.migration_engine.active_migrations),
            'hybrid_schemes': len(self.hybrid_scheme_manager.hybrid_schemes),
            'metrics': self.metrics.copy()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agility manager metrics"""
        return self.metrics.copy()


# Example usage
async def demo_cryptographic_agility():
    """Demonstrate cryptographic agility management"""
    
    # Initialize manager
    manager = CryptographicAgilityManager()
    
    # Register creators
    creators = [
        {
            'creator_id': 'musician_001',
            'creator_type': 'musician',
            'content_types': ['audio', 'video'],
            'performance_requirements': {
                'encrypt_ops_per_sec': 30000,
                'decrypt_ops_per_sec': 30000
            }
        },
        {
            'creator_id': 'photographer_001',
            'creator_type': 'photographer',
            'content_types': ['image'],
            'performance_requirements': {
                'encrypt_ops_per_sec': 10000,
                'decrypt_ops_per_sec': 10000
            }
        }
    ]
    
    for creator in creators:
        manager.register_creator(creator['creator_id'], creator)
    
    # Get algorithm recommendations
    for creator in creators:
        recommended_algo = manager.recommend_algorithm_for_creator(
            creator['creator_type'],
            creator['content_types'],
            creator['performance_requirements']
        )
        
        if recommended_algo:
            print(f"Recommended algorithm for {creator['creator_id']}: {recommended_algo.name}")
        
        # Get hybrid scheme recommendation
        hybrid_scheme = manager.recommend_hybrid_scheme_for_creator(
            creator['creator_type'],
            creator['performance_requirements']
        )
        
        if hybrid_scheme:
            print(f"Recommended hybrid scheme for {creator['creator_id']}: {hybrid_scheme.name}")
    
    # Plan migration
    migration_id = await manager.plan_algorithm_migration(
        from_algorithm_id="aes_256_gcm",
        to_algorithm_id="chacha20_poly1305",
        affected_creators=[c['creator_id'] for c in creators],
        strategy=MigrationStrategy.GRADUAL
    )
    
    print(f"Created migration plan: {migration_id}")
    
    # Execute migration
    success = await manager.execute_migration(migration_id)
    print(f"Migration execution {'succeeded' if success else 'failed'}")
    
    # Get status report
    status_report = manager.get_algorithm_status_report()
    print(f"Algorithm status report: {json.dumps(status_report, indent=2)}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demo
    asyncio.run(demo_cryptographic_agility())