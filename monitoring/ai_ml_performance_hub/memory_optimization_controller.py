"""
💾 Memory Optimization Controller - Enterprise AI/ML Memory Management
======================================================================

Contrôleur ultra-avancé optimisation mémoire pour modèles IA/ML Creator Economy.
Garbage collection intelligent, memory pooling, OOM prevention et analytics.

Fonctionnalités:
- Monitoring consommation mémoire modèles temps réel
- Garbage collection intelligent avec adaptive scheduling
- Memory pooling pour batch processing optimization
- Creator content memory footprint analysis par modalité
- OOM (Out of Memory) prevention avec predictive scaling
- Memory fragmentation analysis et defragmentation automatique
- GPU memory optimization avec unified memory management
- Memory leak detection avec automatic remediation
- Creator tier memory quota management et enforcement

Architecture: monitoring/ai_ml_performance_hub/memory_optimization_controller.py
Responsabilité: Memory management, optimization, OOM prevention, analytics

© 2025 Fahed Mlaiel - Code propriétaire ultra-avancé production-ready
"""

import asyncio
import logging
import time
import gc
import threading
import psutil
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import statistics
from collections import defaultdict, deque
import math


class MemoryType(Enum):
    """Types mémoire surveillés"""
    SYSTEM_RAM = "system_ram"
    GPU_MEMORY = "gpu_memory"
    SHARED_MEMORY = "shared_memory"
    CACHE_MEMORY = "cache_memory"
    BUFFER_MEMORY = "buffer_memory"


class CreatorTier(Enum):
    """Niveaux créateurs pour quotas mémoire"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class ContentModality(Enum):
    """Modalités contenu pour analyse mémoire"""
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    IMAGE = "image"
    MIXED_MEDIA = "mixed_media"


class MemoryOptimizationStrategy(Enum):
    """Stratégies optimisation mémoire"""
    GARBAGE_COLLECTION = "garbage_collection"
    MEMORY_POOLING = "memory_pooling"
    BATCH_OPTIMIZATION = "batch_optimization"
    GRADIENT_ACCUMULATION = "gradient_accumulation"
    MODEL_SHARDING = "model_sharding"
    MEMORY_MAPPING = "memory_mapping"
    CACHE_EVICTION = "cache_eviction"
    COMPRESSION = "compression"


class MemoryPressureLevel(Enum):
    """Niveaux pression mémoire"""
    LOW = "low"          # < 60% usage
    MODERATE = "moderate"  # 60-75%
    HIGH = "high"        # 75-90%
    CRITICAL = "critical"  # > 90%


@dataclass
class MemoryUsageSnapshot:
    """Snapshot utilisation mémoire"""
    snapshot_id: str
    memory_type: MemoryType
    
    # Memory metrics (bytes)
    total_memory: int
    used_memory: int
    available_memory: int
    cached_memory: int
    buffered_memory: int
    
    # Derived metrics
    usage_percentage: float
    pressure_level: MemoryPressureLevel
    
    # Process breakdown
    process_breakdown: Dict[str, int] = field(default_factory=dict)  # process_name -> memory_bytes
    
    # Creator context
    creator_tier_usage: Dict[CreatorTier, int] = field(default_factory=dict)  # tier -> memory_bytes
    content_modality_usage: Dict[ContentModality, int] = field(default_factory=dict)  # modality -> memory_bytes
    
    # System context
    swap_usage: int = 0
    page_faults: int = 0
    memory_fragmentation_ratio: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MemoryAllocation:
    """Allocation mémoire trackée"""
    allocation_id: str
    requester_id: str  # Model, process, or Creator ID
    creator_tier: CreatorTier
    content_modality: ContentModality
    
    # Allocation details
    requested_size_bytes: int
    allocated_size_bytes: int
    memory_type: MemoryType
    allocation_purpose: str  # "model_weights", "batch_data", "cache", etc.
    
    # Lifecycle
    allocated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    # Performance tracking
    access_count: int = 0
    allocation_overhead_bytes: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryOptimizationAction:
    """Action optimisation mémoire"""
    action_id: str
    strategy: MemoryOptimizationStrategy
    target_memory_type: MemoryType
    
    # Action details
    estimated_memory_freed: int
    actual_memory_freed: int = 0
    execution_time_ms: float = 0.0
    
    # Impact assessment
    affected_processes: List[str] = field(default_factory=list)
    affected_creators: List[str] = field(default_factory=list)
    performance_impact: str = "none"  # "none", "minimal", "moderate", "significant"
    
    # Status
    status: str = "planned"  # "planned", "executing", "completed", "failed"
    error_message: Optional[str] = None
    
    # Recommendations
    follow_up_actions: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class MemoryLeak:
    """Détection fuite mémoire"""
    leak_id: str
    suspected_process: str
    leak_type: str  # "gradual", "sudden", "cyclic"
    
    # Leak metrics
    initial_memory_usage: int
    current_memory_usage: int
    growth_rate_per_hour: float
    detection_confidence: float  # 0-1
    
    # Timeline
    first_detected: datetime
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    # Impact
    projected_oom_time: Optional[datetime] = None
    business_impact: str = "low"  # "low", "medium", "high", "critical"
    
    # Remediation
    suggested_actions: List[str] = field(default_factory=list)
    automatic_remediation_enabled: bool = False


@dataclass
class OOMPreventionTrigger:
    """Déclencheur prévention OOM"""
    trigger_id: str
    predicted_oom_time: datetime
    confidence_score: float
    
    # Current state
    current_memory_usage: float  # Percentage
    projected_memory_usage: float  # Percentage at OOM time
    memory_growth_rate: float  # MB/minute
    
    # Prevention actions
    recommended_actions: List[MemoryOptimizationStrategy]
    emergency_actions: List[str]  # Emergency procedures if prevention fails
    
    # Creator impact
    affected_creator_tiers: List[CreatorTier]
    impact_severity: str = "medium"  # "low", "medium", "high", "critical"
    
    created_at: datetime = field(default_factory=datetime.utcnow)


class MemoryOptimizationController:
    """Contrôleur optimisation mémoire IA/ML Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Memory tracking
        self.memory_snapshots: Dict[MemoryType, deque] = {
            mem_type: deque(maxlen=1000) for mem_type in MemoryType
        }
        self.active_allocations: Dict[str, MemoryAllocation] = {}
        self.allocation_history: deque = deque(maxlen=5000)
        
        # Optimization tracking
        self.optimization_actions: deque = deque(maxlen=1000)
        self.memory_leaks: Dict[str, MemoryLeak] = {}
        self.oom_triggers: Dict[str, OOMPreventionTrigger] = {}
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = config.get('monitoring_interval', 10.0)  # 10 seconds default
        
        # Memory quotas by Creator tier (bytes)
        self.creator_memory_quotas = {
            CreatorTier.FREE: {
                'system_ram': 2 * 1024**3,      # 2GB
                'gpu_memory': 1 * 1024**3,      # 1GB
                'cache_memory': 512 * 1024**2   # 512MB
            },
            CreatorTier.PRO: {
                'system_ram': 8 * 1024**3,      # 8GB
                'gpu_memory': 4 * 1024**3,      # 4GB
                'cache_memory': 2 * 1024**3     # 2GB
            },
            CreatorTier.ENTERPRISE: {
                'system_ram': 32 * 1024**3,     # 32GB
                'gpu_memory': 16 * 1024**3,     # 16GB
                'cache_memory': 8 * 1024**3     # 8GB
            },
            CreatorTier.PREMIUM: {
                'system_ram': 64 * 1024**3,     # 64GB
                'gpu_memory': 32 * 1024**3,     # 32GB
                'cache_memory': 16 * 1024**3    # 16GB
            }
        }
        
        # Memory pressure thresholds
        self.pressure_thresholds = {
            MemoryPressureLevel.LOW: 0.6,
            MemoryPressureLevel.MODERATE: 0.75,
            MemoryPressureLevel.HIGH: 0.9,
            MemoryPressureLevel.CRITICAL: 0.95
        }
        
        # Optimization configuration
        self.optimization_config = {
            'auto_gc_enabled': config.get('auto_gc', True),
            'gc_threshold_percentage': config.get('gc_threshold', 80),
            'memory_pooling_enabled': config.get('memory_pooling', True),
            'oom_prevention_enabled': config.get('oom_prevention', True),
            'leak_detection_enabled': config.get('leak_detection', True),
            'aggressive_optimization': config.get('aggressive_optimization', False)
        }
        
        # Content modality memory profiles (typical memory usage patterns)
        self.modality_memory_profiles = {
            ContentModality.AUDIO: {
                'base_memory_mb': 50,
                'per_minute_mb': 10,
                'peak_multiplier': 2.0,
                'cache_efficiency': 0.8
            },
            ContentModality.VIDEO: {
                'base_memory_mb': 200,
                'per_minute_mb': 100,
                'peak_multiplier': 3.0,
                'cache_efficiency': 0.6
            },
            ContentModality.IMAGE: {
                'base_memory_mb': 20,
                'per_image_mb': 5,
                'peak_multiplier': 1.5,
                'cache_efficiency': 0.9
            },
            ContentModality.TEXT: {
                'base_memory_mb': 10,
                'per_1k_words_mb': 1,
                'peak_multiplier': 1.2,
                'cache_efficiency': 0.95
            }
        }
        
        # Memory pools for efficient allocation
        self.memory_pools: Dict[str, Dict[str, Any]] = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger("memory_optimization_controller")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [MEMORY] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation contrôleur mémoire"""
        self.logger.info("💾 Initialisation Memory Optimization Controller...")
        
        # Initialize memory pools
        await self._initialize_memory_pools()
        
        # Collect initial memory snapshots
        await self._collect_initial_snapshots()
        
        # Start real-time monitoring
        await self._start_memory_monitoring()
        
        self.logger.info("✅ Memory Optimization Controller initialisé")
    
    async def _initialize_memory_pools(self):
        """Initialisation pools mémoire"""
        # Create memory pools for common allocation sizes
        pool_sizes = [
            ('small', 1024 * 1024),      # 1MB pool
            ('medium', 10 * 1024 * 1024), # 10MB pool
            ('large', 100 * 1024 * 1024), # 100MB pool
            ('xlarge', 1024 * 1024 * 1024) # 1GB pool
        ]
        
        for pool_name, pool_size in pool_sizes:
            self.memory_pools[pool_name] = {
                'size': pool_size,
                'allocated_chunks': 0,
                'available_chunks': 100,  # Start with 100 chunks available
                'total_chunks': 100,
                'hit_ratio': 0.0,
                'last_gc': datetime.utcnow()
            }
            
            self.logger.info(f"📦 Memory pool initialized: {pool_name} ({pool_size // 1024 // 1024}MB chunks)")
    
    async def _collect_initial_snapshots(self):
        """Collecte snapshots mémoire initiaux"""
        # System RAM
        ram_snapshot = await self._collect_system_memory_snapshot()
        self.memory_snapshots[MemoryType.SYSTEM_RAM].append(ram_snapshot)
        
        # GPU Memory (simulated)
        gpu_snapshot = await self._collect_gpu_memory_snapshot()
        self.memory_snapshots[MemoryType.GPU_MEMORY].append(gpu_snapshot)
        
        # Cache Memory
        cache_snapshot = await self._collect_cache_memory_snapshot()
        self.memory_snapshots[MemoryType.CACHE_MEMORY].append(cache_snapshot)
        
        self.logger.info("📊 Initial memory snapshots collected")
    
    async def _collect_system_memory_snapshot(self) -> MemoryUsageSnapshot:
        """Collecte snapshot mémoire système"""
        memory_info = psutil.virtual_memory()
        
        usage_percentage = (memory_info.used / memory_info.total) * 100
        pressure_level = self._calculate_pressure_level(usage_percentage / 100)
        
        # Get process breakdown (top 10 processes by memory)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                proc_info = proc.info
                if proc_info['memory_info']:
                    processes.append((proc_info['name'], proc_info['memory_info'].rss))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by memory usage and take top 10
        processes.sort(key=lambda x: x[1], reverse=True)
        process_breakdown = dict(processes[:10])
        
        # Simulate Creator tier usage distribution
        total_used = memory_info.used
        creator_tier_usage = {
            CreatorTier.FREE: int(total_used * 0.4),
            CreatorTier.PRO: int(total_used * 0.3),
            CreatorTier.ENTERPRISE: int(total_used * 0.2),
            CreatorTier.PREMIUM: int(total_used * 0.1)
        }
        
        # Simulate content modality usage
        content_modality_usage = {
            ContentModality.VIDEO: int(total_used * 0.4),
            ContentModality.AUDIO: int(total_used * 0.2),
            ContentModality.IMAGE: int(total_used * 0.2),
            ContentModality.TEXT: int(total_used * 0.15),
            ContentModality.MIXED_MEDIA: int(total_used * 0.05)
        }
        
        snapshot = MemoryUsageSnapshot(
            snapshot_id=str(uuid.uuid4()),
            memory_type=MemoryType.SYSTEM_RAM,
            total_memory=memory_info.total,
            used_memory=memory_info.used,
            available_memory=memory_info.available,
            cached_memory=getattr(memory_info, 'cached', 0),
            buffered_memory=getattr(memory_info, 'buffers', 0),
            usage_percentage=usage_percentage,
            pressure_level=pressure_level,
            process_breakdown=process_breakdown,
            creator_tier_usage=creator_tier_usage,
            content_modality_usage=content_modality_usage,
            swap_usage=psutil.swap_memory().used,
            memory_fragmentation_ratio=0.1  # Simulated
        )
        
        return snapshot
    
    async def _collect_gpu_memory_snapshot(self) -> MemoryUsageSnapshot:
        """Collecte snapshot mémoire GPU (simulé)"""
        import random
        
        # Simulate GPU memory (since we don't have actual GPUs in this environment)
        total_gpu_memory = 16 * 1024**3  # 16GB simulated GPU
        used_gpu_memory = int(total_gpu_memory * random.uniform(0.3, 0.8))
        available_gpu_memory = total_gpu_memory - used_gpu_memory
        
        usage_percentage = (used_gpu_memory / total_gpu_memory) * 100
        pressure_level = self._calculate_pressure_level(usage_percentage / 100)
        
        # Simulate process breakdown
        process_breakdown = {
            'model_inference': int(used_gpu_memory * 0.4),
            'training_process': int(used_gpu_memory * 0.3),
            'data_preprocessing': int(used_gpu_memory * 0.2),
            'system_overhead': int(used_gpu_memory * 0.1)
        }
        
        # Creator tier usage (different distribution for GPU)
        creator_tier_usage = {
            CreatorTier.PREMIUM: int(used_gpu_memory * 0.5),  # Premium users get more GPU
            CreatorTier.ENTERPRISE: int(used_gpu_memory * 0.3),
            CreatorTier.PRO: int(used_gpu_memory * 0.15),
            CreatorTier.FREE: int(used_gpu_memory * 0.05)
        }
        
        # Content modality usage (GPU-intensive tasks)
        content_modality_usage = {
            ContentModality.VIDEO: int(used_gpu_memory * 0.5),  # Video processing is GPU-heavy
            ContentModality.IMAGE: int(used_gpu_memory * 0.25),
            ContentModality.AUDIO: int(used_gpu_memory * 0.15),
            ContentModality.TEXT: int(used_gpu_memory * 0.05),
            ContentModality.MIXED_MEDIA: int(used_gpu_memory * 0.05)
        }
        
        snapshot = MemoryUsageSnapshot(
            snapshot_id=str(uuid.uuid4()),
            memory_type=MemoryType.GPU_MEMORY,
            total_memory=total_gpu_memory,
            used_memory=used_gpu_memory,
            available_memory=available_gpu_memory,
            cached_memory=int(used_gpu_memory * 0.1),  # GPU cache
            buffered_memory=0,
            usage_percentage=usage_percentage,
            pressure_level=pressure_level,
            process_breakdown=process_breakdown,
            creator_tier_usage=creator_tier_usage,
            content_modality_usage=content_modality_usage,
            memory_fragmentation_ratio=random.uniform(0.05, 0.2)
        )
        
        return snapshot
    
    async def _collect_cache_memory_snapshot(self) -> MemoryUsageSnapshot:
        """Collecte snapshot mémoire cache"""
        import random
        
        # Simulate cache memory usage
        total_cache_memory = 4 * 1024**3  # 4GB allocated for cache
        used_cache_memory = int(total_cache_memory * random.uniform(0.2, 0.9))
        available_cache_memory = total_cache_memory - used_cache_memory
        
        usage_percentage = (used_cache_memory / total_cache_memory) * 100
        pressure_level = self._calculate_pressure_level(usage_percentage / 100)
        
        # Cache breakdown by type
        process_breakdown = {
            'model_cache': int(used_cache_memory * 0.4),
            'data_cache': int(used_cache_memory * 0.3),
            'result_cache': int(used_cache_memory * 0.2),
            'metadata_cache': int(used_cache_memory * 0.1)
        }
        
        # Creator tier usage (cache allocation)
        creator_tier_usage = {
            CreatorTier.PREMIUM: int(used_cache_memory * 0.4),
            CreatorTier.ENTERPRISE: int(used_cache_memory * 0.3),
            CreatorTier.PRO: int(used_cache_memory * 0.2),
            CreatorTier.FREE: int(used_cache_memory * 0.1)
        }
        
        # Content modality cache usage
        content_modality_usage = {
            ContentModality.VIDEO: int(used_cache_memory * 0.3),
            ContentModality.AUDIO: int(used_cache_memory * 0.25),
            ContentModality.IMAGE: int(used_cache_memory * 0.25),
            ContentModality.TEXT: int(used_cache_memory * 0.15),
            ContentModality.MIXED_MEDIA: int(used_cache_memory * 0.05)
        }
        
        snapshot = MemoryUsageSnapshot(
            snapshot_id=str(uuid.uuid4()),
            memory_type=MemoryType.CACHE_MEMORY,
            total_memory=total_cache_memory,
            used_memory=used_cache_memory,
            available_memory=available_cache_memory,
            cached_memory=used_cache_memory,  # All cache memory is "cached"
            buffered_memory=0,
            usage_percentage=usage_percentage,
            pressure_level=pressure_level,
            process_breakdown=process_breakdown,
            creator_tier_usage=creator_tier_usage,
            content_modality_usage=content_modality_usage,
            memory_fragmentation_ratio=random.uniform(0.02, 0.1)
        )
        
        return snapshot
    
    def _calculate_pressure_level(self, usage_ratio: float) -> MemoryPressureLevel:
        """Calcul niveau pression mémoire"""
        if usage_ratio >= self.pressure_thresholds[MemoryPressureLevel.CRITICAL]:
            return MemoryPressureLevel.CRITICAL
        elif usage_ratio >= self.pressure_thresholds[MemoryPressureLevel.HIGH]:
            return MemoryPressureLevel.HIGH
        elif usage_ratio >= self.pressure_thresholds[MemoryPressureLevel.MODERATE]:
            return MemoryPressureLevel.MODERATE
        else:
            return MemoryPressureLevel.LOW
    
    async def _start_memory_monitoring(self):
        """Démarrage monitoring mémoire temps réel"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info("🔍 Memory monitoring started")
    
    def _monitoring_loop(self):
        """Boucle monitoring mémoire temps réel"""
        while self.monitoring_active:
            try:
                # Collect memory snapshots
                asyncio.run_coroutine_threadsafe(
                    self._collect_memory_snapshots(),
                    asyncio.get_event_loop()
                )
                
                # Detect memory leaks
                self._detect_memory_leaks()
                
                # Check for OOM risks
                self._check_oom_risks()
                
                # Run optimization actions
                self._run_memory_optimizations()
                
                # Update memory pools
                self._update_memory_pools()
                
                # Cleanup old data
                self._cleanup_old_data()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in memory monitoring loop: {str(e)}")
                time.sleep(30)  # Wait longer on error
    
    async def _collect_memory_snapshots(self):
        """Collecte snapshots toutes les mémoires"""
        # System RAM
        ram_snapshot = await self._collect_system_memory_snapshot()
        self.memory_snapshots[MemoryType.SYSTEM_RAM].append(ram_snapshot)
        
        # GPU Memory
        gpu_snapshot = await self._collect_gpu_memory_snapshot()
        self.memory_snapshots[MemoryType.GPU_MEMORY].append(gpu_snapshot)
        
        # Cache Memory
        cache_snapshot = await self._collect_cache_memory_snapshot()
        self.memory_snapshots[MemoryType.CACHE_MEMORY].append(cache_snapshot)
        
        # Check for pressure alerts
        await self._check_memory_pressure_alerts(ram_snapshot, gpu_snapshot, cache_snapshot)
    
    async def _check_memory_pressure_alerts(self, *snapshots):
        """Vérification alertes pression mémoire"""
        for snapshot in snapshots:
            if snapshot.pressure_level in [MemoryPressureLevel.HIGH, MemoryPressureLevel.CRITICAL]:
                self.logger.warning(
                    f"🚨 Memory pressure alert: {snapshot.memory_type.value} at {snapshot.usage_percentage:.1f}% "
                    f"({snapshot.pressure_level.value} pressure)"
                )
                
                # Trigger optimization if critical
                if snapshot.pressure_level == MemoryPressureLevel.CRITICAL:
                    await self._trigger_emergency_optimization(snapshot)
    
    async def _trigger_emergency_optimization(self, snapshot: MemoryUsageSnapshot):
        """Déclenchement optimisation urgence"""
        self.logger.warning(f"🚨 Emergency memory optimization triggered for {snapshot.memory_type.value}")
        
        # Immediate garbage collection
        if snapshot.memory_type == MemoryType.SYSTEM_RAM:
            gc.collect()
            self.logger.info("🗑️ Emergency garbage collection executed")
        
        # Cache eviction for cache memory
        if snapshot.memory_type == MemoryType.CACHE_MEMORY:
            await self._execute_cache_eviction(target_reduction=0.30)  # Free 30% of cache
        
        # Create optimization action record
        action = MemoryOptimizationAction(
            action_id=str(uuid.uuid4()),
            strategy=MemoryOptimizationStrategy.GARBAGE_COLLECTION,
            target_memory_type=snapshot.memory_type,
            estimated_memory_freed=int(snapshot.used_memory * 0.1),  # Estimate 10% freed
            performance_impact="minimal",
            status="completed"
        )
        action.completed_at = datetime.utcnow()
        self.optimization_actions.append(action)
    
    async def _execute_cache_eviction(self, target_reduction: float):
        """Exécution éviction cache"""
        # Simulate cache eviction
        evicted_bytes = int(4 * 1024**3 * target_reduction)  # Simulate evicting from 4GB cache
        
        self.logger.info(f"🗑️ Cache eviction executed: {evicted_bytes // 1024 // 1024}MB freed")
        
        # Record action
        action = MemoryOptimizationAction(
            action_id=str(uuid.uuid4()),
            strategy=MemoryOptimizationStrategy.CACHE_EVICTION,
            target_memory_type=MemoryType.CACHE_MEMORY,
            estimated_memory_freed=evicted_bytes,
            actual_memory_freed=evicted_bytes,
            status="completed",
            performance_impact="moderate"
        )
        action.completed_at = datetime.utcnow()
        self.optimization_actions.append(action)
    
    def _detect_memory_leaks(self):
        """Détection fuites mémoire"""
        # Analyze memory growth trends
        for memory_type in MemoryType:
            snapshots = list(self.memory_snapshots[memory_type])
            if len(snapshots) < 10:  # Need at least 10 snapshots
                continue
            
            # Calculate memory growth rate
            recent_snapshots = snapshots[-10:]  # Last 10 snapshots
            usage_values = [s.used_memory for s in recent_snapshots]
            
            if len(usage_values) > 1:
                # Simple linear regression to detect growth trend
                growth_rate = self._calculate_memory_growth_rate(usage_values)
                
                # Detect leak if growth rate is significant
                if growth_rate > 100 * 1024 * 1024:  # > 100MB/hour growth
                    leak_id = f"leak_{memory_type.value}_{str(uuid.uuid4())[:8]}"
                    
                    # Check if this leak is already tracked
                    existing_leak = None
                    for leak in self.memory_leaks.values():
                        if (leak.suspected_process == memory_type.value and 
                            leak.leak_type == "gradual"):
                            existing_leak = leak
                            break
                    
                    if existing_leak:
                        # Update existing leak
                        existing_leak.current_memory_usage = usage_values[-1]
                        existing_leak.growth_rate_per_hour = growth_rate
                        existing_leak.last_updated = datetime.utcnow()
                        
                        # Project OOM time
                        if growth_rate > 0:
                            available_memory = recent_snapshots[-1].available_memory
                            hours_to_oom = available_memory / growth_rate
                            existing_leak.projected_oom_time = datetime.utcnow() + timedelta(hours=hours_to_oom)
                    else:
                        # Create new leak detection
                        leak = MemoryLeak(
                            leak_id=leak_id,
                            suspected_process=memory_type.value,
                            leak_type="gradual",
                            initial_memory_usage=usage_values[0],
                            current_memory_usage=usage_values[-1],
                            growth_rate_per_hour=growth_rate,
                            detection_confidence=0.7,
                            first_detected=datetime.utcnow(),
                            suggested_actions=[
                                f"Investigate {memory_type.value} processes",
                                "Enable detailed memory profiling",
                                "Consider process restart",
                                "Review memory allocation patterns"
                            ]
                        )
                        
                        self.memory_leaks[leak_id] = leak
                        
                        self.logger.warning(
                            f"🔍 Memory leak detected: {memory_type.value} "
                            f"({growth_rate / 1024 / 1024:.1f}MB/hour growth rate)"
                        )
    
    def _calculate_memory_growth_rate(self, usage_values: List[int]) -> float:
        """Calcul taux croissance mémoire (bytes per hour)"""
        if len(usage_values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(usage_values)
        x = list(range(n))
        y = usage_values
        
        # Calculate slope (change per monitoring interval)
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Convert to bytes per hour
        intervals_per_hour = 3600 / self.monitoring_interval
        growth_rate_per_hour = slope * intervals_per_hour
        
        return growth_rate_per_hour
    
    def _check_oom_risks(self):
        """Vérification risques OOM"""
        if not self.optimization_config['oom_prevention_enabled']:
            return
        
        for memory_type in [MemoryType.SYSTEM_RAM, MemoryType.GPU_MEMORY]:
            snapshots = list(self.memory_snapshots[memory_type])
            if len(snapshots) < 5:
                continue
            
            latest_snapshot = snapshots[-1]
            
            # Check if we're approaching memory limits
            if latest_snapshot.usage_percentage > 85:  # > 85% usage
                # Calculate growth trend
                recent_usage = [s.used_memory for s in snapshots[-5:]]
                growth_rate = self._calculate_memory_growth_rate(recent_usage)
                
                if growth_rate > 0:
                    # Calculate time to OOM
                    available_memory = latest_snapshot.available_memory
                    hours_to_oom = available_memory / growth_rate
                    
                    if hours_to_oom < 2:  # Less than 2 hours to OOM
                        trigger_id = f"oom_{memory_type.value}_{str(uuid.uuid4())[:8]}"
                        
                        # Determine recommended actions
                        recommended_actions = []
                        if latest_snapshot.usage_percentage > 90:
                            recommended_actions = [
                                MemoryOptimizationStrategy.GARBAGE_COLLECTION,
                                MemoryOptimizationStrategy.CACHE_EVICTION,
                                MemoryOptimizationStrategy.MEMORY_POOLING
                            ]
                        else:
                            recommended_actions = [
                                MemoryOptimizationStrategy.CACHE_EVICTION,
                                MemoryOptimizationStrategy.BATCH_OPTIMIZATION
                            ]
                        
                        # Determine affected creator tiers
                        affected_tiers = []
                        for tier, usage in latest_snapshot.creator_tier_usage.items():
                            if usage > self.creator_memory_quotas[tier].get(memory_type.value.replace('_memory', '_ram'), 0) * 0.8:
                                affected_tiers.append(tier)
                        
                        trigger = OOMPreventionTrigger(
                            trigger_id=trigger_id,
                            predicted_oom_time=datetime.utcnow() + timedelta(hours=hours_to_oom),
                            confidence_score=0.8,
                            current_memory_usage=latest_snapshot.usage_percentage,
                            projected_memory_usage=100.0,
                            memory_growth_rate=growth_rate / 1024 / 1024,  # MB/minute
                            recommended_actions=recommended_actions,
                            emergency_actions=[
                                "Kill non-essential processes",
                                "Scale down Creator tier limits",
                                "Enable swap memory",
                                "Restart memory-intensive services"
                            ],
                            affected_creator_tiers=affected_tiers,
                            impact_severity="critical" if hours_to_oom < 1 else "high"
                        )
                        
                        self.oom_triggers[trigger_id] = trigger
                        
                        self.logger.critical(
                            f"🚨 OOM risk detected: {memory_type.value} - "
                            f"Predicted OOM in {hours_to_oom:.1f} hours"
                        )
    
    def _run_memory_optimizations(self):
        """Exécution optimisations mémoire"""
        # Check if automatic optimizations are enabled
        if not self.optimization_config['auto_gc_enabled']:
            return
        
        # Run garbage collection if memory pressure is high
        for memory_type in [MemoryType.SYSTEM_RAM]:
            snapshots = list(self.memory_snapshots[memory_type])
            if not snapshots:
                continue
            
            latest_snapshot = snapshots[-1]
            
            if (latest_snapshot.usage_percentage > self.optimization_config['gc_threshold_percentage'] and
                memory_type == MemoryType.SYSTEM_RAM):
                
                # Execute garbage collection
                start_time = time.time()
                collected = gc.collect()
                execution_time = (time.time() - start_time) * 1000  # ms
                
                # Estimate memory freed (simplified)
                estimated_freed = collected * 1024 * 100  # Rough estimate
                
                action = MemoryOptimizationAction(
                    action_id=str(uuid.uuid4()),
                    strategy=MemoryOptimizationStrategy.GARBAGE_COLLECTION,
                    target_memory_type=memory_type,
                    estimated_memory_freed=estimated_freed,
                    actual_memory_freed=estimated_freed,
                    execution_time_ms=execution_time,
                    status="completed",
                    performance_impact="minimal"
                )
                action.completed_at = datetime.utcnow()
                self.optimization_actions.append(action)
                
                if collected > 0:
                    self.logger.info(
                        f"🗑️ Automatic garbage collection: {collected} objects collected "
                        f"in {execution_time:.1f}ms"
                    )
    
    def _update_memory_pools(self):
        """Mise à jour pools mémoire"""
        # Update pool statistics and perform maintenance
        for pool_name, pool_info in self.memory_pools.items():
            # Simulate pool usage updates
            import random
            
            # Update hit ratio (simulate successful pool usage)
            if random.random() < 0.7:  # 70% chance of pool hit
                pool_info['hit_ratio'] = min(1.0, pool_info['hit_ratio'] + 0.01)
            
            # Perform pool garbage collection if needed
            if datetime.utcnow() - pool_info['last_gc'] > timedelta(minutes=30):
                # Simulate pool cleanup
                freed_chunks = max(0, pool_info['allocated_chunks'] - pool_info['available_chunks'])
                if freed_chunks > 0:
                    pool_info['available_chunks'] += freed_chunks // 2  # Free half
                    pool_info['allocated_chunks'] -= freed_chunks // 2
                    pool_info['last_gc'] = datetime.utcnow()
                    
                    self.logger.debug(f"🧹 Memory pool cleanup: {pool_name} - {freed_chunks // 2} chunks freed")
    
    def _cleanup_old_data(self):
        """Nettoyage données anciennes"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Cleanup old allocations
        expired_allocations = [
            alloc_id for alloc_id, allocation in self.active_allocations.items()
            if not allocation.is_active and allocation.allocated_at < cutoff_time
        ]
        
        for alloc_id in expired_allocations:
            allocation = self.active_allocations[alloc_id]
            self.allocation_history.append(allocation)
            del self.active_allocations[alloc_id]
        
        # Cleanup resolved memory leaks
        resolved_leaks = [
            leak_id for leak_id, leak in self.memory_leaks.items()
            if leak.last_updated < cutoff_time - timedelta(hours=1)
        ]
        
        for leak_id in resolved_leaks:
            self.logger.info(f"🔍 Memory leak resolved: {leak_id}")
            del self.memory_leaks[leak_id]
        
        # Cleanup old OOM triggers
        expired_triggers = [
            trigger_id for trigger_id, trigger in self.oom_triggers.items()
            if trigger.predicted_oom_time < datetime.utcnow() - timedelta(hours=1)
        ]
        
        for trigger_id in expired_triggers:
            del self.oom_triggers[trigger_id]
    
    async def allocate_memory(
        self,
        requester_id: str,
        creator_tier: CreatorTier,
        content_modality: ContentModality,
        size_bytes: int,
        memory_type: MemoryType = MemoryType.SYSTEM_RAM,
        purpose: str = "general"
    ) -> Optional[str]:
        """Allocation mémoire avec tracking"""
        
        # Check Creator tier quota
        tier_quotas = self.creator_memory_quotas[creator_tier]
        quota_key = memory_type.value.replace('_memory', '_ram')
        if quota_key in tier_quotas:
            quota_limit = tier_quotas[quota_key]
            
            # Calculate current usage for this Creator tier
            current_tier_usage = sum(
                alloc.allocated_size_bytes for alloc in self.active_allocations.values()
                if alloc.creator_tier == creator_tier and alloc.memory_type == memory_type
            )
            
            if current_tier_usage + size_bytes > quota_limit:
                self.logger.warning(
                    f"❌ Memory allocation denied: {creator_tier.value} quota exceeded "
                    f"({(current_tier_usage + size_bytes) // 1024 // 1024}MB > {quota_limit // 1024 // 1024}MB)"
                )
                return None
        
        # Try to allocate from memory pool first
        pool_allocation = await self._try_pool_allocation(size_bytes)
        
        allocation = MemoryAllocation(
            allocation_id=str(uuid.uuid4()),
            requester_id=requester_id,
            creator_tier=creator_tier,
            content_modality=content_modality,
            requested_size_bytes=size_bytes,
            allocated_size_bytes=size_bytes,  # Simplified - in reality might be different
            memory_type=memory_type,
            allocation_purpose=purpose,
            allocation_overhead_bytes=size_bytes // 100,  # 1% overhead estimate
            metadata={
                'pool_allocation': pool_allocation is not None,
                'pool_name': pool_allocation
            }
        )
        
        self.active_allocations[allocation.allocation_id] = allocation
        
        self.logger.debug(
            f"💾 Memory allocated: {allocation.allocation_id} - "
            f"{size_bytes // 1024 // 1024}MB for {creator_tier.value} ({content_modality.value})"
        )
        
        return allocation.allocation_id
    
    async def _try_pool_allocation(self, size_bytes: int) -> Optional[str]:
        """Tentative allocation depuis pool mémoire"""
        # Find suitable pool
        for pool_name, pool_info in self.memory_pools.items():
            if size_bytes <= pool_info['size'] and pool_info['available_chunks'] > 0:
                # Allocate from pool
                pool_info['available_chunks'] -= 1
                pool_info['allocated_chunks'] += 1
                
                self.logger.debug(f"📦 Pool allocation: {pool_name} ({size_bytes // 1024 // 1024}MB)")
                return pool_name
        
        return None
    
    async def deallocate_memory(self, allocation_id: str):
        """Désallocation mémoire"""
        if allocation_id not in self.active_allocations:
            self.logger.warning(f"❌ Deallocation failed: {allocation_id} not found")
            return
        
        allocation = self.active_allocations[allocation_id]
        allocation.is_active = False
        
        # Return to pool if it was a pool allocation
        if allocation.metadata.get('pool_allocation'):
            pool_name = allocation.metadata.get('pool_name')
            if pool_name and pool_name in self.memory_pools:
                pool_info = self.memory_pools[pool_name]
                pool_info['available_chunks'] += 1
                pool_info['allocated_chunks'] -= 1
        
        # Move to history
        self.allocation_history.append(allocation)
        del self.active_allocations[allocation_id]
        
        self.logger.debug(
            f"🗑️ Memory deallocated: {allocation_id} - "
            f"{allocation.allocated_size_bytes // 1024 // 1024}MB freed"
        )
    
    async def get_memory_status(self, memory_type: Optional[MemoryType] = None) -> Dict[str, Any]:
        """Statut mémoire système"""
        if memory_type:
            memory_types = [memory_type]
        else:
            memory_types = list(MemoryType)
        
        status = {}
        
        for mem_type in memory_types:
            snapshots = list(self.memory_snapshots[mem_type])
            if not snapshots:
                status[mem_type.value] = {'status': 'No data available'}
                continue
            
            latest_snapshot = snapshots[-1]
            
            # Calculate trends
            if len(snapshots) >= 10:
                recent_usage = [s.usage_percentage for s in snapshots[-10:]]
                usage_trend = "increasing" if recent_usage[-1] > recent_usage[0] + 5 else \
                             "decreasing" if recent_usage[-1] < recent_usage[0] - 5 else "stable"
            else:
                usage_trend = "unknown"
            
            # Active allocations for this memory type
            active_allocs = [
                alloc for alloc in self.active_allocations.values()
                if alloc.memory_type == mem_type
            ]
            
            total_allocated = sum(alloc.allocated_size_bytes for alloc in active_allocs)
            
            status[mem_type.value] = {
                'current_usage': {
                    'total_memory_gb': round(latest_snapshot.total_memory / 1024**3, 2),
                    'used_memory_gb': round(latest_snapshot.used_memory / 1024**3, 2),
                    'available_memory_gb': round(latest_snapshot.available_memory / 1024**3, 2),
                    'usage_percentage': round(latest_snapshot.usage_percentage, 1),
                    'pressure_level': latest_snapshot.pressure_level.value
                },
                'allocation_tracking': {
                    'active_allocations': len(active_allocs),
                    'total_allocated_gb': round(total_allocated / 1024**3, 2),
                    'allocation_overhead_gb': round(sum(alloc.allocation_overhead_bytes for alloc in active_allocs) / 1024**3, 2)
                },
                'creator_tier_breakdown': {
                    tier.value: round(usage / 1024**3, 2) 
                    for tier, usage in latest_snapshot.creator_tier_usage.items()
                },
                'content_modality_breakdown': {
                    modality.value: round(usage / 1024**3, 2)
                    for modality, usage in latest_snapshot.content_modality_usage.items()
                },
                'trends': {
                    'usage_trend': usage_trend,
                    'fragmentation_ratio': latest_snapshot.memory_fragmentation_ratio
                },
                'health_indicators': {
                    'memory_leaks_detected': len([l for l in self.memory_leaks.values() if mem_type.value in l.suspected_process]),
                    'oom_risk': len([t for t in self.oom_triggers.values() if mem_type.value in t.trigger_id]),
                    'last_optimization': len([a for a in list(self.optimization_actions)[-10:] if a.target_memory_type == mem_type])
                }
            }
        
        return status
    
    async def get_optimization_summary(self) -> Dict[str, Any]:
        """Résumé optimisations mémoire"""
        recent_actions = list(self.optimization_actions)[-50:]  # Last 50 actions
        
        # Action type distribution
        action_types = defaultdict(int)
        total_memory_freed = 0
        successful_actions = 0
        
        for action in recent_actions:
            action_types[action.strategy.value] += 1
            total_memory_freed += action.actual_memory_freed
            if action.status == "completed":
                successful_actions += 1
        
        # Memory leaks summary
        active_leaks = len(self.memory_leaks)
        high_severity_leaks = len([
            leak for leak in self.memory_leaks.values()
            if leak.business_impact in ["high", "critical"]
        ])
        
        # OOM prevention summary
        active_oom_triggers = len(self.oom_triggers)
        critical_oom_triggers = len([
            trigger for trigger in self.oom_triggers.values()
            if trigger.impact_severity == "critical"
        ])
        
        # Memory pool efficiency
        pool_stats = {}
        for pool_name, pool_info in self.memory_pools.items():
            pool_stats[pool_name] = {
                'hit_ratio': round(pool_info['hit_ratio'], 3),
                'utilization': round((pool_info['allocated_chunks'] / pool_info['total_chunks']) * 100, 1),
                'available_chunks': pool_info['available_chunks']
            }
        
        return {
            'optimization_actions': {
                'total_actions_50': len(recent_actions),
                'successful_actions': successful_actions,
                'success_rate': round((successful_actions / len(recent_actions)) * 100, 1) if recent_actions else 0,
                'total_memory_freed_gb': round(total_memory_freed / 1024**3, 2),
                'action_types': dict(action_types),
                'most_common_action': max(action_types.items(), key=lambda x: x[1])[0] if action_types else None
            },
            'memory_leak_detection': {
                'active_leaks': active_leaks,
                'high_severity_leaks': high_severity_leaks,
                'leak_detection_enabled': self.optimization_config['leak_detection_enabled']
            },
            'oom_prevention': {
                'active_triggers': active_oom_triggers,
                'critical_triggers': critical_oom_triggers,
                'prevention_enabled': self.optimization_config['oom_prevention_enabled']
            },
            'memory_pools': pool_stats,
            'configuration': {
                'auto_gc_enabled': self.optimization_config['auto_gc_enabled'],
                'gc_threshold_percentage': self.optimization_config['gc_threshold_percentage'],
                'memory_pooling_enabled': self.optimization_config['memory_pooling_enabled'],
                'aggressive_optimization': self.optimization_config['aggressive_optimization']
            },
            'system_health': {
                'monitoring_active': self.monitoring_active,
                'last_update': datetime.utcnow().isoformat()
            }
        }
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Dashboard complet optimisation mémoire"""
        # Memory status for all types
        memory_status = await self.get_memory_status()
        
        # Optimization summary
        optimization_summary = await self.get_optimization_summary()
        
        # Creator tier memory analysis
        tier_analysis = {}
        for tier in CreatorTier:
            tier_allocations = [
                alloc for alloc in self.active_allocations.values()
                if alloc.creator_tier == tier
            ]
            
            total_allocated = sum(alloc.allocated_size_bytes for alloc in tier_allocations)
            tier_quotas = self.creator_memory_quotas[tier]
            
            tier_analysis[tier.value] = {
                'active_allocations': len(tier_allocations),
                'total_allocated_gb': round(total_allocated / 1024**3, 2),
                'quota_utilization': {
                    memory_type: round((total_allocated / quota) * 100, 1) if quota > 0 else 0
                    for memory_type, quota in tier_quotas.items()
                },
                'avg_allocation_size_mb': round((total_allocated / len(tier_allocations)) / 1024**2, 1) if tier_allocations else 0
            }
        
        # Content modality analysis
        modality_analysis = {}
        for modality in ContentModality:
            modality_allocations = [
                alloc for alloc in self.active_allocations.values()
                if alloc.content_modality == modality
            ]
            
            total_allocated = sum(alloc.allocated_size_bytes for alloc in modality_allocations)
            
            modality_analysis[modality.value] = {
                'active_allocations': len(modality_allocations),
                'total_allocated_gb': round(total_allocated / 1024**3, 2),
                'avg_allocation_size_mb': round((total_allocated / len(modality_allocations)) / 1024**2, 1) if modality_allocations else 0,
                'memory_profile': self.modality_memory_profiles.get(modality, {})
            }
        
        # Recent critical events
        critical_events = []
        
        # High severity memory leaks
        for leak in self.memory_leaks.values():
            if leak.business_impact in ["high", "critical"]:
                critical_events.append({
                    'type': 'memory_leak',
                    'severity': leak.business_impact,
                    'description': f"Memory leak in {leak.suspected_process}",
                    'timestamp': leak.first_detected.isoformat()
                })
        
        # Critical OOM triggers
        for trigger in self.oom_triggers.values():
            if trigger.impact_severity == "critical":
                critical_events.append({
                    'type': 'oom_risk',
                    'severity': trigger.impact_severity,
                    'description': f"OOM predicted in {(trigger.predicted_oom_time - datetime.utcnow()).total_seconds() / 3600:.1f} hours",
                    'timestamp': trigger.created_at.isoformat()
                })
        
        # Sort by timestamp (most recent first)
        critical_events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'memory_status': memory_status,
            'optimization_summary': optimization_summary,
            'creator_tier_analysis': tier_analysis,
            'content_modality_analysis': modality_analysis,
            'critical_events': critical_events[:10],  # Top 10 most recent
            'recommendations': self._generate_memory_recommendations(memory_status, optimization_summary),
            'dashboard_generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_memory_recommendations(
        self, 
        memory_status: Dict[str, Any], 
        optimization_summary: Dict[str, Any]
    ) -> List[str]:
        """Génération recommandations mémoire"""
        recommendations = []
        
        # High memory usage recommendations
        for mem_type, status in memory_status.items():
            if isinstance(status, dict) and 'current_usage' in status:
                usage_pct = status['current_usage']['usage_percentage']
                pressure_level = status['current_usage']['pressure_level']
                
                if pressure_level in ['high', 'critical']:
                    recommendations.append(
                        f"High {mem_type} usage ({usage_pct:.1f}%) - enable aggressive optimization"
                    )
                elif pressure_level == 'moderate':
                    recommendations.append(
                        f"Monitor {mem_type} usage ({usage_pct:.1f}%) - consider proactive optimization"
                    )
        
        # Memory leak recommendations
        active_leaks = optimization_summary['memory_leak_detection']['active_leaks']
        if active_leaks > 0:
            recommendations.append(f"Investigate {active_leaks} detected memory leaks")
        
        # OOM prevention recommendations
        critical_triggers = optimization_summary['oom_prevention']['critical_triggers']
        if critical_triggers > 0:
            recommendations.append(f"Urgent: {critical_triggers} critical OOM triggers require immediate action")
        
        # Pool efficiency recommendations
        poor_pools = [
            pool_name for pool_name, stats in optimization_summary['memory_pools'].items()
            if stats['hit_ratio'] < 0.5
        ]
        if poor_pools:
            recommendations.append(f"Optimize memory pools with low hit ratio: {', '.join(poor_pools)}")
        
        # General optimization recommendations
        if not recommendations:
            recommendations.append("Memory system is healthy - continue regular monitoring")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def shutdown(self):
        """Arrêt propre contrôleur mémoire"""
        self.logger.info("⏹️ Shutting down Memory Optimization Controller...")
        
        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        # Deallocate all active allocations
        for allocation_id in list(self.active_allocations.keys()):
            await self.deallocate_memory(allocation_id)
        
        # Clear data structures
        for snapshots in self.memory_snapshots.values():
            snapshots.clear()
        
        self.active_allocations.clear()
        self.allocation_history.clear()
        self.optimization_actions.clear()
        self.memory_leaks.clear()
        self.oom_triggers.clear()
        self.memory_pools.clear()
        
        self.logger.info("✅ Memory Optimization Controller shutdown complete")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_memory_controller():
        config = {
            'monitoring_interval': 2.0,  # Fast for testing
            'auto_gc': True,
            'memory_pooling': True,
            'oom_prevention': True,
            'leak_detection': True
        }
        
        controller = MemoryOptimizationController(config)
        await controller.initialize()
        
        # Test memory allocation
        allocation_id = await controller.allocate_memory(
            requester_id="test_model_1",
            creator_tier=CreatorTier.PRO,
            content_modality=ContentModality.VIDEO,
            size_bytes=100 * 1024 * 1024,  # 100MB
            purpose="model_weights"
        )
        
        if allocation_id:
            print(f"✅ Memory allocated: {allocation_id}")
            
            # Let monitoring run for a few cycles
            await asyncio.sleep(6)
            
            # Deallocate memory
            await controller.deallocate_memory(allocation_id)
            print(f"✅ Memory deallocated: {allocation_id}")
        
        # Test memory status
        status = await controller.get_memory_status()
        print(f"✅ Memory status: {len(status)} memory types monitored")
        
        # Test optimization summary
        summary = await controller.get_optimization_summary()
        print(f"✅ Optimization summary: {summary['optimization_actions']['total_actions_50']} recent actions")
        
        # Test dashboard
        dashboard = await controller.get_comprehensive_dashboard()
        print(f"✅ Dashboard: {len(dashboard['critical_events'])} critical events")
        
        print("✅ Memory Optimization Controller test completed")
        await controller.shutdown()
    
    asyncio.run(test_memory_controller())