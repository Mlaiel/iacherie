#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Redis CPU Optimizer - Enterprise Performance Module
======================================================

**Rôles Experts:**
- **Performance Engineer**: CPU usage optimization and monitoring
- **Backend Senior**: CPU-efficient algorithms and processing
- **DevOps**: System resource optimization and scaling
- **Infrastructure Engineer**: Multi-core optimization and load balancing

Optimiseur CPU Redis pour utilisation optimale des ressources processeur
avec distribution intelligente et monitoring temps-réel.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import time
import logging
import multiprocessing
import threading
import psutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import concurrent.futures

logger = logging.getLogger(__name__)

class CPUTier(Enum):
    """Niveaux d'utilisation CPU"""
    OPTIMAL = "optimal"          # < 50% utilisation
    GOOD = "good"                # 50-70% utilisation
    HIGH = "high"                # 70-85% utilisation
    CRITICAL = "critical"        # 85-95% utilisation
    OVERLOADED = "overloaded"    # > 95% utilisation

class OptimizationMode(Enum):
    """Modes d'optimisation CPU"""
    PERFORMANCE = "performance"   # Performance maximale
    EFFICIENCY = "efficiency"     # Efficacité énergétique
    BALANCED = "balanced"         # Équilibre performance/efficacité
    CONSERVATIVE = "conservative" # Conservation ressources

@dataclass
class CPUMetrics:
    """Métriques CPU"""
    cpu_percent: float = 0.0
    cpu_count: int = multiprocessing.cpu_count()
    cpu_per_core: List[float] = field(default_factory=list)
    load_average: List[float] = field(default_factory=list)
    current_tier: CPUTier = CPUTier.OPTIMAL
    thread_count: int = 0
    process_count: int = 0
    context_switches: int = 0
    interrupts: int = 0
    cpu_history: deque = field(default_factory=lambda: deque(maxlen=1000))

@dataclass
class CPUConfig:
    """Configuration optimisation CPU"""
    target_cpu_usage: float = 0.75      # 75% max
    max_threads: int = None              # Auto-detect
    max_processes: int = None            # Auto-detect
    optimization_mode: OptimizationMode = OptimizationMode.BALANCED
    enable_auto_scaling: bool = True
    enable_affinity_optimization: bool = True
    monitoring_interval: float = 1.0
    optimization_interval: float = 30.0

class CPUOptimizer:
    """Optimiseur CPU Redis enterprise"""
    
    def __init__(self, config: CPUConfig):
        self.config = config
        self.metrics = CPUMetrics()
        self.is_running = False
        self._monitoring_task = None
        self._optimization_task = None
        self._thread_pool = None
        self._process_pool = None
        
        # Auto-configuration
        if config.max_threads is None:
            self.config.max_threads = min(32, multiprocessing.cpu_count() * 4)
        if config.max_processes is None:
            self.config.max_processes = multiprocessing.cpu_count()
    
    async def start(self):
        """Démarrage optimiseur CPU"""
        if self.is_running:
            return
            
        logger.info("⚙️ Démarrage optimiseur CPU Redis")
        self.is_running = True
        
        # Initialisation pools
        await self._initialize_execution_pools()
        
        # Démarrage monitoring
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Démarrage optimisation
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("✅ Optimiseur CPU démarré")
    
    async def stop(self):
        """Arrêt optimiseur CPU"""
        if not self.is_running:
            return
            
        logger.info("🛑 Arrêt optimiseur CPU")
        self.is_running = False
        
        # Arrêt tâches
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._optimization_task:
            self._optimization_task.cancel()
        
        # Nettoyage pools
        await self._cleanup_execution_pools()
        
        logger.info("✅ Optimiseur CPU arrêté")
    
    async def _initialize_execution_pools(self):
        """Initialisation pools d'exécution"""
        # Thread pool pour I/O bound operations
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.max_threads,
            thread_name_prefix="redis-cpu-opt"
        )
        
        # Process pool pour CPU bound operations
        self._process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.config.max_processes
        )
        
        logger.info(f"📊 Pools initialisés: {self.config.max_threads} threads, {self.config.max_processes} processes")
    
    async def _cleanup_execution_pools(self):
        """Nettoyage pools d'exécution"""
        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)
        if self._process_pool:
            self._process_pool.shutdown(wait=True)
    
    async def execute_cpu_optimized(self, func, *args, cpu_intensive=True, **kwargs):
        """Exécution optimisée CPU"""
        loop = asyncio.get_event_loop()
        
        if cpu_intensive and self._process_pool:
            # CPU intensive: utiliser process pool
            future = self._process_pool.submit(func, *args, **kwargs)
        else:
            # I/O bound: utiliser thread pool
            future = self._thread_pool.submit(func, *args, **kwargs)
        
        try:
            result = await loop.run_in_executor(None, future.result)
            return result
        except Exception as e:
            logger.error(f"❌ Erreur exécution optimisée: {e}")
            raise
    
    async def _collect_cpu_metrics(self):
        """Collection métriques CPU"""
        # CPU global
        self.metrics.cpu_percent = psutil.cpu_percent(interval=None)
        
        # CPU par core
        self.metrics.cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        
        # Load average
        try:
            self.metrics.load_average = list(psutil.getloadavg())
        except AttributeError:
            self.metrics.load_average = [0.0, 0.0, 0.0]
        
        # Compteurs système
        self.metrics.thread_count = threading.active_count()
        
        # Historique
        self.metrics.cpu_history.append(self.metrics.cpu_percent)
        
        # Mise à jour tier
        await self._update_cpu_tier()
    
    async def _update_cpu_tier(self):
        """Mise à jour tier CPU"""
        cpu_percent = self.metrics.cpu_percent
        
        if cpu_percent >= 95:
            self.metrics.current_tier = CPUTier.OVERLOADED
        elif cpu_percent >= 85:
            self.metrics.current_tier = CPUTier.CRITICAL
        elif cpu_percent >= 70:
            self.metrics.current_tier = CPUTier.HIGH
        elif cpu_percent >= 50:
            self.metrics.current_tier = CPUTier.GOOD
        else:
            self.metrics.current_tier = CPUTier.OPTIMAL
    
    async def _monitoring_loop(self):
        """Boucle monitoring CPU"""
        while self.is_running:
            try:
                await self._collect_cpu_metrics()
                await asyncio.sleep(self.config.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur monitoring CPU: {e}")
                await asyncio.sleep(1.0)
    
    async def _optimization_loop(self):
        """Boucle optimisation CPU"""
        while self.is_running:
            try:
                await self._optimize_cpu_usage()
                await asyncio.sleep(self.config.optimization_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur optimisation CPU: {e}")
                await asyncio.sleep(5.0)
    
    async def _optimize_cpu_usage(self):
        """Optimisation utilisation CPU"""
        current_tier = self.metrics.current_tier
        
        if current_tier == CPUTier.OVERLOADED:
            await self._emergency_cpu_optimization()
        elif current_tier == CPUTier.CRITICAL:
            await self._aggressive_cpu_optimization()
        elif current_tier == CPUTier.HIGH:
            await self._moderate_cpu_optimization()
        else:
            await self._maintenance_cpu_optimization()
    
    async def _emergency_cpu_optimization(self):
        """Optimisation d'urgence CPU"""
        logger.warning("🚨 Optimisation d'urgence CPU")
        
        # Réduction threads/processes
        if self._thread_pool:
            current_threads = self._thread_pool._max_workers
            new_threads = max(1, current_threads // 2)
            logger.info(f"🔧 Réduction threads: {current_threads} -> {new_threads}")
        
        # Optimisation affinité CPU si activée
        if self.config.enable_affinity_optimization:
            await self._optimize_cpu_affinity()
    
    async def _aggressive_cpu_optimization(self):
        """Optimisation agressive CPU"""
        logger.info("⚡ Optimisation agressive CPU")
        
        # Ajustement pools selon charge
        await self._adjust_pool_sizes()
    
    async def _moderate_cpu_optimization(self):
        """Optimisation modérée CPU"""
        logger.debug("🔧 Optimisation modérée CPU")
        
        # Optimisation légère
        await self._optimize_thread_distribution()
    
    async def _maintenance_cpu_optimization(self):
        """Optimisation maintenance CPU"""
        # Nettoyage threads inactifs
        pass
    
    async def _optimize_cpu_affinity(self):
        """Optimisation affinité CPU"""
        try:
            import os
            current_process = psutil.Process()
            
            # Distribuer sur tous les cores disponibles
            available_cpus = list(range(self.metrics.cpu_count))
            current_process.cpu_affinity(available_cpus)
            
            logger.info(f"🎯 Affinité CPU optimisée: {len(available_cpus)} cores")
        except Exception as e:
            logger.error(f"❌ Erreur optimisation affinité: {e}")
    
    async def _adjust_pool_sizes(self):
        """Ajustement taille pools"""
        target_usage = self.config.target_cpu_usage
        current_usage = self.metrics.cpu_percent / 100.0
        
        if current_usage > target_usage:
            # Réduction pools
            scaling_factor = target_usage / current_usage
            new_thread_count = max(1, int(self.config.max_threads * scaling_factor))
            logger.info(f"📉 Réduction pool threads: {self.config.max_threads} -> {new_thread_count}")
        
    async def _optimize_thread_distribution(self):
        """Optimisation distribution threads"""
        # Équilibrage charge entre cores
        core_loads = self.metrics.cpu_per_core
        if core_loads:
            avg_load = sum(core_loads) / len(core_loads)
            max_load = max(core_loads)
            
            if max_load > avg_load * 1.5:
                logger.info("⚖️ Rééquilibrage charge cores détecté")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Récupération métriques CPU"""
        return {
            'cpu_percent': self.metrics.cpu_percent,
            'cpu_count': self.metrics.cpu_count,
            'cpu_per_core': self.metrics.cpu_per_core,
            'load_average': self.metrics.load_average,
            'current_tier': self.metrics.current_tier.value,
            'thread_count': self.metrics.thread_count,
            'process_count': self.metrics.process_count,
            'target_cpu_usage': self.config.target_cpu_usage,
            'max_threads': self.config.max_threads,
            'max_processes': self.config.max_processes,
            'optimization_mode': self.config.optimization_mode.value
        }

# Factory function
async def create_cpu_optimizer(
    target_cpu_usage: float = 0.75,
    optimization_mode: OptimizationMode = OptimizationMode.BALANCED
) -> CPUOptimizer:
    """Création optimiseur CPU configuré"""
    config = CPUConfig(
        target_cpu_usage=target_cpu_usage,
        optimization_mode=optimization_mode
    )
    
    optimizer = CPUOptimizer(config)
    await optimizer.start()
    return optimizer

# Export public API
__all__ = [
    'CPUOptimizer',
    'CPUTier',
    'OptimizationMode',
    'CPUMetrics',
    'CPUConfig',
    'create_cpu_optimizer'
]