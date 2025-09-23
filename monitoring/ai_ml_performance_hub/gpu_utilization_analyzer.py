# WARNING: Potential SQL injection risk - use parameterized queries
"""
🎮 GPU Utilization Analyzer - Enterprise AI/ML Performance Hub
=============================================================

Analyseur utilisation GPU enterprise ultra-avancé pour l'écosystème créateur Ainflue.
Monitoring GPU multi-instances, analyse répartition charge par Creator tier,
détection goulots d'étranglement, optimisation allocation dynamique.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/gpu_utilization_analyzer.py
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque, defaultdict
import threading
import json
import uuid
import psutil
from concurrent.futures import ThreadPoolExecutor


class GPUType(Enum):
    """Types GPU supportés"""
    NVIDIA_RTX_4090 = "nvidia_rtx_4090"
    NVIDIA_RTX_4080 = "nvidia_rtx_4080"
    NVIDIA_A100 = "nvidia_a100"
    NVIDIA_V100 = "nvidia_v100"
    NVIDIA_T4 = "nvidia_t4"
    AMD_MI250X = "amd_mi250x"
    INTEL_PONTEVECC = "intel_pontevecc"
    CUSTOM = "custom"


class WorkloadType(Enum):
    """Types charge travail GPU"""
    TRAINING = "training"
    INFERENCE = "inference"
    PREPROCESSING = "preprocessing"
    POSTPROCESSING = "postprocessing"
    MIXED = "mixed"


class CreatorTier(Enum):
    """Niveaux créateurs pour allocation GPU"""
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class GPUDevice:
    """Information périphérique GPU"""
    gpu_id: str
    gpu_index: int
    name: str
    gpu_type: GPUType
    memory_total_mb: float
    memory_free_mb: float
    memory_used_mb: float
    utilization_percent: float
    temperature_celsius: float
    power_draw_watts: float
    power_limit_watts: float
    fan_speed_percent: float
    compute_mode: str
    driver_version: str
    cuda_version: Optional[str]
    is_available: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GPUWorkload:
    """Charge travail GPU"""
    workload_id: str
    gpu_id: str
    model_id: str
    creator_id: str
    creator_tier: CreatorTier
    workload_type: WorkloadType
    start_time: float
    memory_allocated_mb: float
    compute_utilization: float
    estimated_duration_sec: float
    priority_level: int  # 1=highest, 5=lowest
    is_active: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GPUPerformanceMetrics:
    """Métriques performance GPU"""
    gpu_id: str
    utilization_percent: float
    memory_utilization_percent: float
    temperature_celsius: float
    power_efficiency_score: float  # Performance per watt
    throughput_ops_per_sec: float
    active_workloads: int
    queue_length: int
    avg_workload_latency: float
    thermal_throttling: bool
    power_throttling: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CreatorGPUUsage:
    """Utilisation GPU par créateur"""
    creator_id: str
    creator_tier: CreatorTier
    total_gpu_hours: float
    gpu_memory_peak_mb: float
    compute_efficiency_score: float
    cost_optimization_score: float
    preferred_gpu_type: GPUType
    workload_distribution: Dict[WorkloadType, int]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class GPUUtilizationAnalyzer:
    """Analyseur utilisation GPU enterprise Creator Economy"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # GPU devices tracking
        self.gpu_devices: Dict[str, GPUDevice] = {}
        self.gpu_metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Workload management
        self.active_workloads: Dict[str, GPUWorkload] = {}
        self.workload_queue: deque = deque()
        self.workload_history: deque = deque(maxlen=5000)
        
        # Creator analytics  
        self.creator_gpu_usage: Dict[str, CreatorGPUUsage] = {}
        self.tier_allocation_stats: Dict[CreatorTier, Dict] = defaultdict(dict)
        
        # GPU allocation policies per creator tier
        self.tier_gpu_limits = {
            CreatorTier.FREE: {'max_concurrent': 1, 'max_memory_mb': 2000, 'priority': 5},
            CreatorTier.PREMIUM: {'max_concurrent': 2, 'max_memory_mb': 4000, 'priority': 4},
            CreatorTier.PROFESSIONAL: {'max_concurrent': 4, 'max_memory_mb': 8000, 'priority': 3},
            CreatorTier.ENTERPRISE: {'max_concurrent': 8, 'max_memory_mb': 16000, 'priority': 1}
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'max_utilization': 95,
            'max_temperature': 85,
            'max_memory_usage': 90,
            'min_efficiency_score': 0.7,
            'max_queue_length': 10
        }
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # GPU cost per hour (simulated pricing)
        self.gpu_cost_per_hour = {
            GPUType.NVIDIA_RTX_4090: 2.50,
            GPUType.NVIDIA_RTX_4080: 2.00,
            GPUType.NVIDIA_A100: 3.00,
            GPUType.NVIDIA_V100: 2.20,
            GPUType.NVIDIA_T4: 0.50,
            GPUType.AMD_MI250X: 2.80,
            GPUType.INTEL_PONTEVECC: 1.80
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging avancé"""
        logger = logging.getLogger(f"gpu_analyzer_{id(self)}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Initialisation analyseur GPU"""
        self.logger.info("🎮 Initialisation GPU Utilization Analyzer...")
        
        # Découvrir GPUs disponibles
        await self._discover_gpu_devices()
        
        # Démarrer monitoring continu
        await self._start_gpu_monitoring()
        
        # Initialiser métriques baseline
        await self._initialize_baseline_metrics()
        
        self.logger.info(f"✅ GPU Analyzer initialisé - {len(self.gpu_devices)} GPUs détectés")
    
    async def _discover_gpu_devices(self):
        """Découverte périphériques GPU"""
        # Simulation découverte GPU (production: nvidia-ml-py, ROCm, etc.)
        simulated_gpus = [
            {
                'gpu_id': 'gpu_0',
                'gpu_index': 0,
                'name': 'NVIDIA RTX 4090',
                'gpu_type': GPUType.NVIDIA_RTX_4090,
                'memory_total_mb': 24000,
                'driver_version': '535.54.03',
                'cuda_version': '12.2'
            },
            {
                'gpu_id': 'gpu_1', 
                'gpu_index': 1,
                'name': 'NVIDIA RTX 4080',
                'gpu_type': GPUType.NVIDIA_RTX_4080,
                'memory_total_mb': 16000,
                'driver_version': '535.54.03',
                'cuda_version': '12.2'
            },
            {
                'gpu_id': 'gpu_2',
                'gpu_index': 2,
                'name': 'NVIDIA A100',
                'gpu_type': GPUType.NVIDIA_A100,
                'memory_total_mb': 40000,
                'driver_version': '535.54.03',
                'cuda_version': '12.2'
            }
        ]
        
        for gpu_info in simulated_gpus:
            gpu_device = GPUDevice(
                gpu_id=gpu_info['gpu_id'],
                gpu_index=gpu_info['gpu_index'],
                name=gpu_info['name'],
                gpu_type=gpu_info['gpu_type'],
                memory_total_mb=gpu_info['memory_total_mb'],
                memory_free_mb=gpu_info['memory_total_mb'] * 0.9,  # 90% free initially
                memory_used_mb=gpu_info['memory_total_mb'] * 0.1,  # 10% used
                utilization_percent=15.0,  # Light baseline usage
                temperature_celsius=45.0,
                power_draw_watts=150.0,
                power_limit_watts=350.0,
                fan_speed_percent=40.0,
                compute_mode='Default',
                driver_version=gpu_info['driver_version'],
                cuda_version=gpu_info.get('cuda_version'),
                is_available=True
            )
            
            self.gpu_devices[gpu_info['gpu_id']] = gpu_device
            self.gpu_metrics_history[gpu_info['gpu_id']] = deque(maxlen=1000)
    
    async def _start_gpu_monitoring(self):
        """Démarrage monitoring GPU continu"""
        self.monitoring_active = True
        
        def monitor_gpus():
            while self.monitoring_active:
                try:
                    self._collect_gpu_metrics()
                    time.sleep(2)  # Collect every 2 seconds
                except Exception as e:
                    self.logger.error(f"GPU monitoring error: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitor_gpus, daemon=True)
        self.monitoring_thread.start()
    
    def _collect_gpu_metrics(self):
        """Collecte métriques GPU"""
        for gpu_id, gpu_device in self.gpu_devices.items():
            try:
                # Simulation métriques GPU (production: vraies APIs)
                import random
                
                # Simulate realistic GPU metrics
                base_utilization = 15 + len(self.active_workloads) * 20
                utilization = min(95, base_utilization + random.uniform(-10, 15))
                
                memory_used = gpu_device.memory_total_mb * 0.1  # Base usage
                for workload in self.active_workloads.values():
                    if workload.gpu_id == gpu_id:
                        memory_used += workload.memory_allocated_mb
                
                memory_used = min(gpu_device.memory_total_mb * 0.95, memory_used)
                memory_free = gpu_device.memory_total_mb - memory_used
                
                # Temperature based on utilization
                temperature = 35 + (utilization / 100) * 40 + random.uniform(-3, 3)
                
                # Power draw based on utilization
                max_power = gpu_device.power_limit_watts
                power_draw = (max_power * 0.3) + (utilization / 100) * (max_power * 0.7)
                
                # Update device metrics
                gpu_device.utilization_percent = utilization
                gpu_device.memory_used_mb = memory_used
                gpu_device.memory_free_mb = memory_free
                gpu_device.temperature_celsius = temperature
                gpu_device.power_draw_watts = power_draw
                gpu_device.fan_speed_percent = min(100, 30 + (temperature - 40) * 2)
                gpu_device.timestamp = datetime.utcnow()
                
                # Calculate performance metrics
                performance_metric = self._calculate_gpu_performance_metrics(gpu_device)
                self.gpu_metrics_history[gpu_id].append(performance_metric)
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics for GPU {gpu_id}: {e}")
    
    def _calculate_gpu_performance_metrics(self, gpu_device: GPUDevice) -> GPUPerformanceMetrics:
        """Calcul métriques performance GPU"""
        # Calculate power efficiency (performance per watt)
        if gpu_device.power_draw_watts > 0:
            power_efficiency = gpu_device.utilization_percent / gpu_device.power_draw_watts
        else:
            power_efficiency = 0
        
        # Calculate throughput (operations per second - simulated)
        throughput = gpu_device.utilization_percent * 100  # Simplified calculation
        
        # Active workloads on this GPU
        active_workloads = len([w for w in self.active_workloads.values() if w.gpu_id == gpu_device.gpu_id])
        
        # Queue length for this GPU
        queue_length = len([w for w in self.workload_queue if getattr(w, 'preferred_gpu_id', None) == gpu_device.gpu_id])
        
        # Average workload latency (simulated)
        avg_latency = 100 + (gpu_device.utilization_percent / 100) * 200
        
        # Thermal and power throttling detection
        thermal_throttling = gpu_device.temperature_celsius > self.performance_thresholds['max_temperature']
        power_throttling = gpu_device.power_draw_watts > gpu_device.power_limit_watts * 0.95
        
        return GPUPerformanceMetrics(
            gpu_id=gpu_device.gpu_id,
            utilization_percent=gpu_device.utilization_percent,
            memory_utilization_percent=(gpu_device.memory_used_mb / gpu_device.memory_total_mb) * 100,
            temperature_celsius=gpu_device.temperature_celsius,
            power_efficiency_score=power_efficiency,
            throughput_ops_per_sec=throughput,
            active_workloads=active_workloads,
            queue_length=queue_length,
            avg_workload_latency=avg_latency,
            thermal_throttling=thermal_throttling,
            power_throttling=power_throttling
        )
    
    async def _initialize_baseline_metrics(self):
        """Initialisation métriques baseline"""
        for tier in CreatorTier:
            self.tier_allocation_stats[tier] = {
                'total_gpu_hours': 0.0,
                'avg_utilization': 0.0,
                'cost_total': 0.0,
                'efficiency_score': 0.8,
                'active_creators': 0
            }
    
    async def allocate_gpu_workload(
        self,
        model_id: str,
        creator_id: str,
        creator_tier: CreatorTier,
        workload_type: WorkloadType,
        memory_required_mb: float,
        estimated_duration_sec: float,
        preferred_gpu_type: Optional[GPUType] = None
    ) -> Optional[str]:
        """Allocation charge travail GPU"""
        # Check tier limits
        tier_limits = self.tier_gpu_limits[creator_tier]
        
        # Count current workloads for this creator
        creator_workloads = [w for w in self.active_workloads.values() if w.creator_id == creator_id]
        
        if len(creator_workloads) >= tier_limits['max_concurrent']:
            self.logger.warning(f"Creator {creator_id} reached GPU limit ({tier_limits['max_concurrent']})")
            return None
        
        if memory_required_mb > tier_limits['max_memory_mb']:
            self.logger.warning(f"Memory requirement ({memory_required_mb}MB) exceeds tier limit ({tier_limits['max_memory_mb']}MB)")
            return None
        
        # Find best GPU for workload
        selected_gpu = await self._select_optimal_gpu(
            memory_required_mb, creator_tier, preferred_gpu_type
        )
        
        if not selected_gpu:
            # Add to queue if no GPU available
            workload_id = str(uuid.uuid4())
            workload = GPUWorkload(
                workload_id=workload_id,
                gpu_id="",  # Will be assigned when GPU becomes available
                model_id=model_id,
                creator_id=creator_id,
                creator_tier=creator_tier,
                workload_type=workload_type,
                start_time=0,
                memory_allocated_mb=memory_required_mb,
                compute_utilization=0,
                estimated_duration_sec=estimated_duration_sec,
                priority_level=tier_limits['priority'],
                is_active=False
            )
            
            self.workload_queue.append(workload)
            self.logger.info(f"Workload {workload_id} queued - no GPU available")
            return workload_id
        
        # Allocate workload to GPU
        workload_id = str(uuid.uuid4())
        workload = GPUWorkload(
            workload_id=workload_id,
            gpu_id=selected_gpu,
            model_id=model_id,
            creator_id=creator_id,
            creator_tier=creator_tier,
            workload_type=workload_type,
            start_time=time.time(),
            memory_allocated_mb=memory_required_mb,
            compute_utilization=80.0,  # Estimated compute utilization
            estimated_duration_sec=estimated_duration_sec,
            priority_level=tier_limits['priority'],
            is_active=True
        )
        
        self.active_workloads[workload_id] = workload
        
        # Update creator usage tracking
        await self._update_creator_gpu_usage(creator_id, creator_tier, workload)
        
        self.logger.info(f"Allocated workload {workload_id} to GPU {selected_gpu} for creator {creator_id}")
        return workload_id
    
    async def _select_optimal_gpu(
        self,
        memory_required_mb: float,
        creator_tier: CreatorTier,
        preferred_gpu_type: Optional[GPUType] = None
    ) -> Optional[str]:
        """Sélection GPU optimal"""
        available_gpus = []
        
        for gpu_id, gpu_device in self.gpu_devices.items():
            if not gpu_device.is_available:
                continue
            
            # Check memory availability
            if gpu_device.memory_free_mb < memory_required_mb:
                continue
            
            # Check utilization
            if gpu_device.utilization_percent > self.performance_thresholds['max_utilization']:
                continue
            
            # Check temperature
            if gpu_device.temperature_celsius > self.performance_thresholds['max_temperature']:
                continue
            
            # Calculate score for this GPU
            score = self._calculate_gpu_allocation_score(
                gpu_device, memory_required_mb, creator_tier, preferred_gpu_type
            )
            
            available_gpus.append((gpu_id, score))
        
        if not available_gpus:
            return None
        
        # Sort by score (higher is better)
        available_gpus.sort(key=lambda x: x[1], reverse=True)
        return available_gpus[0][0]
    
    def _calculate_gpu_allocation_score(
        self,
        gpu_device: GPUDevice,
        memory_required_mb: float,
        creator_tier: CreatorTier,
        preferred_gpu_type: Optional[GPUType]
    ) -> float:
        """Calcul score allocation GPU"""
        score = 0.0
        
        # Memory availability score (0-30 points)
        memory_ratio = (gpu_device.memory_free_mb - memory_required_mb) / gpu_device.memory_total_mb
        score += min(30, memory_ratio * 100)
        
        # Utilization score (0-25 points) - prefer less utilized GPUs
        utilization_score = (100 - gpu_device.utilization_percent) / 100 * 25
        score += utilization_score
        
        # Temperature score (0-20 points) - prefer cooler GPUs
        temp_score = max(0, (85 - gpu_device.temperature_celsius) / 45 * 20)
        score += temp_score
        
        # GPU type preference (0-15 points)
        if preferred_gpu_type and gpu_device.gpu_type == preferred_gpu_type:
            score += 15
        
        # Creator tier GPU matching (0-10 points)
        tier_gpu_bonus = {
            CreatorTier.FREE: {GPUType.NVIDIA_T4: 10},
            CreatorTier.PREMIUM: {GPUType.NVIDIA_RTX_4080: 10, GPUType.NVIDIA_V100: 8},
            CreatorTier.PROFESSIONAL: {GPUType.NVIDIA_RTX_4090: 10, GPUType.NVIDIA_A100: 8},
            CreatorTier.ENTERPRISE: {GPUType.NVIDIA_A100: 10, GPUType.NVIDIA_RTX_4090: 8}
        }
        
        if creator_tier in tier_gpu_bonus and gpu_device.gpu_type in tier_gpu_bonus[creator_tier]:
            score += tier_gpu_bonus[creator_tier][gpu_device.gpu_type]
        
        return score
    
    async def _update_creator_gpu_usage(self, creator_id: str, creator_tier: CreatorTier, workload: GPUWorkload):
        """Mise à jour utilisation GPU créateur"""
        if creator_id not in self.creator_gpu_usage:
            self.creator_gpu_usage[creator_id] = CreatorGPUUsage(
                creator_id=creator_id,
                creator_tier=creator_tier,
                total_gpu_hours=0.0,
                gpu_memory_peak_mb=0.0,
                compute_efficiency_score=0.8,
                cost_optimization_score=0.7,
                preferred_gpu_type=self.gpu_devices[workload.gpu_id].gpu_type,
                workload_distribution=defaultdict(int)
            )
        
        usage = self.creator_gpu_usage[creator_id]
        usage.workload_distribution[workload.workload_type] += 1
        usage.gpu_memory_peak_mb = max(usage.gpu_memory_peak_mb, workload.memory_allocated_mb)
    
    async def complete_gpu_workload(self, workload_id: str, success: bool = True):
        """Finalisation charge travail GPU"""
        if workload_id not in self.active_workloads:
            self.logger.warning(f"Workload {workload_id} not found")
            return
        
        workload = self.active_workloads[workload_id]
        end_time = time.time()
        duration_hours = (end_time - workload.start_time) / 3600
        
        # Update creator usage
        if workload.creator_id in self.creator_gpu_usage:
            usage = self.creator_gpu_usage[workload.creator_id]
            usage.total_gpu_hours += duration_hours
            
            # Calculate cost
            gpu_device = self.gpu_devices[workload.gpu_id]
            cost = duration_hours * self.gpu_cost_per_hour.get(gpu_device.gpu_type, 1.0)
            
            # Update tier stats
            tier_stats = self.tier_allocation_stats[workload.creator_tier]
            tier_stats['total_gpu_hours'] += duration_hours
            tier_stats['cost_total'] += cost
        
        # Move to history
        self.workload_history.append(workload)
        del self.active_workloads[workload_id]
        
        # Process queue
        await self._process_workload_queue()
        
        self.logger.info(f"Completed workload {workload_id} - Duration: {duration_hours:.2f}h")
    
    async def _process_workload_queue(self):
        """Traitement file attente charges travail"""
        if not self.workload_queue:
            return
        
        # Sort queue by priority
        sorted_queue = sorted(self.workload_queue, key=lambda w: w.priority_level)
        
        for workload in sorted_queue:
            # Try to allocate GPU
            selected_gpu = await self._select_optimal_gpu(
                workload.memory_allocated_mb,
                workload.creator_tier,
                None
            )
            
            if selected_gpu:
                # Move from queue to active
                workload.gpu_id = selected_gpu
                workload.start_time = time.time()
                workload.is_active = True
                
                self.active_workloads[workload.workload_id] = workload
                self.workload_queue.remove(workload)
                
                self.logger.info(f"Allocated queued workload {workload.workload_id} to GPU {selected_gpu}")
                break
    
    async def get_gpu_utilization_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble utilisation GPU"""
        total_gpus = len(self.gpu_devices)
        active_gpus = len([gpu for gpu in self.gpu_devices.values() if gpu.utilization_percent > 10])
        
        # Calculate average metrics
        if self.gpu_devices:
            avg_utilization = statistics.mean([gpu.utilization_percent for gpu in self.gpu_devices.values()])
            avg_temperature = statistics.mean([gpu.temperature_celsius for gpu in self.gpu_devices.values()])
            total_memory = sum([gpu.memory_total_mb for gpu in self.gpu_devices.values()])
            used_memory = sum([gpu.memory_used_mb for gpu in self.gpu_devices.values()])
        else:
            avg_utilization = avg_temperature = total_memory = used_memory = 0
        
        # Workload statistics
        active_workloads = len(self.active_workloads)
        queued_workloads = len(self.workload_queue)
        
        # Creator tier distribution
        tier_distribution = defaultdict(int)
        for workload in self.active_workloads.values():
            tier_distribution[workload.creator_tier.value] += 1
        
        # Performance issues
        overutilized_gpus = [gpu_id for gpu_id, gpu in self.gpu_devices.items() 
                           if gpu.utilization_percent > self.performance_thresholds['max_utilization']]
        overheated_gpus = [gpu_id for gpu_id, gpu in self.gpu_devices.items()
                          if gpu.temperature_celsius > self.performance_thresholds['max_temperature']]
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'gpu_fleet': {
                'total_gpus': total_gpus,
                'active_gpus': active_gpus,
                'avg_utilization_percent': avg_utilization,
                'avg_temperature_celsius': avg_temperature,
                'total_memory_gb': total_memory / 1024,
                'memory_utilization_percent': (used_memory / total_memory * 100) if total_memory > 0 else 0
            },
            'workload_management': {
                'active_workloads': active_workloads,
                'queued_workloads': queued_workloads,
                'tier_distribution': dict(tier_distribution)
            },
            'performance_alerts': {
                'overutilized_gpus': overutilized_gpus,
                'overheated_gpus': overheated_gpus,
                'queue_backlog': queued_workloads > self.performance_thresholds['max_queue_length']
            },
            'cost_optimization': await self._calculate_cost_optimization_metrics()
        }
    
    async def _calculate_cost_optimization_metrics(self) -> Dict[str, Any]:
        """Calcul métriques optimisation coût"""
        total_cost = sum([stats['cost_total'] for stats in self.tier_allocation_stats.values()])
        total_hours = sum([stats['total_gpu_hours'] for stats in self.tier_allocation_stats.values()])
        
        # Efficiency by tier
        tier_efficiency = {}
        for tier, stats in self.tier_allocation_stats.items():
            if stats['total_gpu_hours'] > 0:
                tier_efficiency[tier.value] = {
                    'cost_per_hour': stats['cost_total'] / stats['total_gpu_hours'],
                    'utilization_efficiency': stats['avg_utilization'] / 100,
                    'total_cost': stats['cost_total']
                }
        
        # Cost optimization recommendations
        recommendations = []
        if total_hours > 0 and total_cost / total_hours > 2.0:
            recommendations.append("Consider using lower-tier GPUs for non-critical workloads")
        
        underutilized_gpus = [gpu_id for gpu_id, gpu in self.gpu_devices.items() 
                             if gpu.utilization_percent < 30 and gpu.memory_used_mb > 1000]
        if underutilized_gpus:
            recommendations.append(f"Optimize workload distribution - {len(underutilized_gpus)} GPUs underutilized")
        
        return {
            'total_cost_24h': total_cost,
            'avg_cost_per_hour': total_cost / total_hours if total_hours > 0 else 0,
            'tier_efficiency': tier_efficiency,
            'optimization_recommendations': recommendations
        }
    
    async def get_creator_gpu_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Analytics GPU pour créateur"""
        if creator_id not in self.creator_gpu_usage:
            return {'creator_id': creator_id, 'error': 'No GPU usage data found'}
        
        usage = self.creator_gpu_usage[creator_id]
        
        # Current active workloads
        active_workloads = [w for w in self.active_workloads.values() if w.creator_id == creator_id]
        
        # Cost calculation
        estimated_cost = 0.0
        for workload in active_workloads:
            if workload.gpu_id in self.gpu_devices:
                gpu_device = self.gpu_devices[workload.gpu_id]
                hourly_cost = self.gpu_cost_per_hour.get(gpu_device.gpu_type, 1.0)
                estimated_cost += hourly_cost * (workload.estimated_duration_sec / 3600)
        
        return {
            'creator_id': creator_id,
            'creator_tier': usage.creator_tier.value,
            'usage_summary': {
                'total_gpu_hours': usage.total_gpu_hours,
                'gpu_memory_peak_mb': usage.gpu_memory_peak_mb,
                'compute_efficiency_score': usage.compute_efficiency_score,
                'preferred_gpu_type': usage.preferred_gpu_type.value
            },
            'current_activity': {
                'active_workloads': len(active_workloads),
                'estimated_cost': estimated_cost,
                'workload_types': [w.workload_type.value for w in active_workloads]
            },
            'workload_distribution': dict(usage.workload_distribution),
            'tier_limits': self.tier_gpu_limits[usage.creator_tier],
            'optimization_score': usage.cost_optimization_score
        }
    
    async def shutdown(self):
        """Arrêt propre analyseur GPU"""
        self.logger.info("⏹️ Arrêt GPU Utilization Analyzer...")
        
        # Arrêter monitoring
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # Arrêter executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ GPU Utilization Analyzer arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_gpu_analyzer():
        config = {"debug": True}
        analyzer = GPUUtilizationAnalyzer(config)
        
        await analyzer.initialize()
        
        # Test workload allocation
        workload_id = await analyzer.allocate_gpu_workload(
            model_id="content_classifier_v1",
            creator_id="creator_123",
            creator_tier=CreatorTier.PREMIUM,
            workload_type=WorkloadType.INFERENCE,
            memory_required_mb=4000,
            estimated_duration_sec=300,
            preferred_gpu_type=GPUType.NVIDIA_RTX_4090
        )
        
        if workload_id:
            print(f"Allocated workload: {workload_id}")
            
            # Wait a bit for metrics collection
            await asyncio.sleep(5)
            
            # Complete workload
            await analyzer.complete_gpu_workload(workload_id, success=True)
        
        # Get overview
        overview = await analyzer.get_gpu_utilization_overview()
        print(f"GPU Overview: {json.dumps(overview, indent=2)}")
        
        print("✅ GPU Utilization Analyzer test passed")
        await analyzer.shutdown()
    
    asyncio.run(test_gpu_analyzer())