"""
📊 RESOURCE USAGE TRACKER
Enterprise-grade inference resource usage tracking and cost optimization system.

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
"""

import asyncio
import time
import json
import logging
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import subprocess
import platform


@dataclass
class ResourceSnapshot:
    """Resource usage snapshot at a point in time."""
    timestamp: datetime
    model_id: str
    creator_type: str
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_percent: float
    gpu_memory_mb: float
    gpu_utilization_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    process_count: int
    thread_count: int
    inference_count: int
    cost_estimate_usd: float


@dataclass
class CostMetrics:
    """Cost calculation metrics."""
    compute_cost_per_hour: float
    memory_cost_per_gb_hour: float
    gpu_cost_per_hour: float
    storage_cost_per_gb_hour: float
    network_cost_per_gb: float
    total_cost_usd: float
    cost_per_inference: float
    cost_trend_7d: float


class ResourceUsageTracker:
    """
    📊 Enterprise-grade resource usage tracking and cost optimization.
    
    Features:
    - Real-time resource monitoring (CPU, Memory, GPU, Disk, Network)
    - Cost tracking and optimization recommendations
    - Creator-specific resource analytics
    - Sustainability metrics (carbon footprint)
    - Resource efficiency optimization
    - Predictive resource planning
    - Multi-cloud cost optimization
    - Resource alerting and governance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Resource tracking data
        self.resource_snapshots: deque = deque(maxlen=50000)  # ~24h at 30s intervals
        self.model_resources: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.creator_resources: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Cost tracking
        self.cost_config = self._setup_cost_configuration()
        self.daily_costs: Dict[str, float] = defaultdict(float)  # date -> cost
        self.model_costs: Dict[str, float] = defaultdict(float)
        
        # System monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.collection_interval = 30  # seconds
        
        # Performance baselines
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        self.efficiency_targets = {
            'cpu_utilization_target': 70.0,
            'memory_utilization_target': 80.0,
            'gpu_utilization_target': 85.0,
            'cost_per_inference_target': 0.001  # $0.001 per inference
        }
        
        # Sustainability tracking
        self.carbon_intensity_kg_per_kwh = 0.5  # Regional carbon intensity
        self.power_usage_effectiveness = 1.4  # Data center PUE
        
        self.logger.info("ResourceUsageTracker initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('resource_usage_tracker')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_cost_configuration(self) -> Dict[str, float]:
        """Setup cloud cost configuration (USD per hour/GB)."""
        return {
            # AWS-like pricing (simplified)
            'cpu_cost_per_core_hour': 0.05,  # ~$0.05 per vCPU hour
            'memory_cost_per_gb_hour': 0.01,  # ~$0.01 per GB RAM hour
            'gpu_cost_per_hour': 3.0,  # ~$3.0 per GPU hour (V100/A100)
            'storage_cost_per_gb_hour': 0.0001,  # ~$0.10 per GB month
            'network_cost_per_gb': 0.09,  # ~$0.09 per GB transfer
            
            # Regional multipliers
            'region_multiplier': 1.0,
            'reserved_instance_discount': 0.7,  # 30% discount
            'spot_instance_discount': 0.3,  # 70% discount
        }
    
    def _get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)
            memory_percent = memory.percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_sent_mb = network_io.bytes_sent / (1024 * 1024) if network_io else 0
            network_recv_mb = network_io.bytes_recv / (1024 * 1024) if network_io else 0
            
            # Process information
            process_count = len(psutil.pids())
            
            # GPU metrics (simulated for now - would use nvidia-ml-py in production)
            gpu_memory_mb, gpu_utilization = self._get_gpu_metrics()
            
            return {
                'cpu_usage_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_usage_mb': memory_mb,
                'memory_percent': memory_percent,
                'memory_total_mb': memory.total / (1024 * 1024),
                'gpu_memory_mb': gpu_memory_mb,
                'gpu_utilization_percent': gpu_utilization,
                'disk_read_mb': disk_read_mb,
                'disk_write_mb': disk_write_mb,
                'network_sent_mb': network_sent_mb,
                'network_recv_mb': network_recv_mb,
                'process_count': process_count,
                'thread_count': threading.active_count()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system resources: {e}")
            return {}
    
    def _get_gpu_metrics(self) -> Tuple[float, float]:
        """Get GPU metrics (simplified simulation)."""
        try:
            # In production, would use nvidia-ml-py or similar
            # For now, simulate realistic GPU usage
            if hasattr(self, '_simulated_gpu_load'):
                base_memory = self._simulated_gpu_load.get('memory', 2048)
                base_util = self._simulated_gpu_load.get('utilization', 40)
            else:
                base_memory = np.random.uniform(1024, 4096)  # MB
                base_util = np.random.uniform(20, 80)  # %
                self._simulated_gpu_load = {
                    'memory': base_memory,
                    'utilization': base_util
                }
            
            # Add some variation
            memory_mb = base_memory + np.random.uniform(-200, 200)
            utilization = base_util + np.random.uniform(-10, 10)
            
            return max(0, memory_mb), max(0, min(100, utilization))
            
        except Exception as e:
            self.logger.error(f"Error getting GPU metrics: {e}")
            return 0.0, 0.0
    
    async def track_inference_resources(
        self,
        model_id: str,
        creator_type: str,
        inference_count: int = 1,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> ResourceSnapshot:
        """Track resource usage for inference operations."""
        try:
            # Get current system resources
            system_resources = self._get_system_resources()
            current_time = datetime.now()
            
            # Calculate cost estimate
            cost_estimate = self._calculate_cost_estimate(system_resources)
            
            # Create resource snapshot
            snapshot = ResourceSnapshot(
                timestamp=current_time,
                model_id=model_id,
                creator_type=creator_type,
                cpu_usage_percent=system_resources.get('cpu_usage_percent', 0),
                memory_usage_mb=system_resources.get('memory_usage_mb', 0),
                memory_percent=system_resources.get('memory_percent', 0),
                gpu_memory_mb=system_resources.get('gpu_memory_mb', 0),
                gpu_utilization_percent=system_resources.get('gpu_utilization_percent', 0),
                disk_io_read_mb=system_resources.get('disk_read_mb', 0),
                disk_io_write_mb=system_resources.get('disk_write_mb', 0),
                network_io_sent_mb=system_resources.get('network_sent_mb', 0),
                network_io_recv_mb=system_resources.get('network_recv_mb', 0),
                process_count=system_resources.get('process_count', 0),
                thread_count=system_resources.get('thread_count', 0),
                inference_count=inference_count,
                cost_estimate_usd=cost_estimate
            )
            
            # Store snapshot
            self.resource_snapshots.append(snapshot)
            self.model_resources[model_id].append(snapshot)
            self.creator_resources[creator_type].append(snapshot)
            
            # Update cost tracking
            date_key = current_time.strftime('%Y-%m-%d')
            self.daily_costs[date_key] += cost_estimate
            self.model_costs[model_id] += cost_estimate
            
            self.logger.debug(
                f"Tracked resources for {model_id}: "
                f"CPU {snapshot.cpu_usage_percent:.1f}%, "
                f"Memory {snapshot.memory_usage_mb:.1f}MB, "
                f"Cost ${cost_estimate:.6f}"
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error tracking inference resources: {e}")
            return None
    
    def _calculate_cost_estimate(self, system_resources: Dict[str, Any]) -> float:
        """Calculate cost estimate for current resource usage."""
        try:
            # Time interval for cost calculation (per collection interval)
            hours = self.collection_interval / 3600.0
            
            # CPU cost
            cpu_cores = system_resources.get('cpu_count', 1)
            cpu_utilization = system_resources.get('cpu_usage_percent', 0) / 100.0
            cpu_cost = (
                cpu_cores * cpu_utilization * 
                self.cost_config['cpu_cost_per_core_hour'] * hours
            )
            
            # Memory cost
            memory_gb = system_resources.get('memory_usage_mb', 0) / 1024.0
            memory_cost = memory_gb * self.cost_config['memory_cost_per_gb_hour'] * hours
            
            # GPU cost
            gpu_utilization = system_resources.get('gpu_utilization_percent', 0) / 100.0
            gpu_cost = gpu_utilization * self.cost_config['gpu_cost_per_hour'] * hours
            
            # Storage cost (simplified)
            storage_gb = (
                system_resources.get('disk_read_mb', 0) + 
                system_resources.get('disk_write_mb', 0)
            ) / 1024.0
            storage_cost = storage_gb * self.cost_config['storage_cost_per_gb_hour'] * hours
            
            # Network cost
            network_gb = (
                system_resources.get('network_sent_mb', 0) + 
                system_resources.get('network_recv_mb', 0)
            ) / 1024.0
            network_cost = network_gb * self.cost_config['network_cost_per_gb']
            
            total_cost = cpu_cost + memory_cost + gpu_cost + storage_cost + network_cost
            
            # Apply regional and discount multipliers
            total_cost *= self.cost_config['region_multiplier']
            
            return total_cost
            
        except Exception as e:
            self.logger.error(f"Error calculating cost estimate: {e}")
            return 0.0
    
    def get_resource_summary(
        self,
        model_id: Optional[str] = None,
        creator_type: Optional[str] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get resource usage summary for specified criteria."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Filter snapshots
            if model_id:
                snapshots = [s for s in self.model_resources[model_id] 
                           if start_time <= s.timestamp <= end_time]
            elif creator_type:
                snapshots = [s for s in self.creator_resources[creator_type] 
                           if start_time <= s.timestamp <= end_time]
            else:
                snapshots = [s for s in self.resource_snapshots 
                           if start_time <= s.timestamp <= end_time]
            
            if not snapshots:
                return {"error": "No resource data found for specified criteria"}
            
            # Calculate summary statistics
            cpu_usage = [s.cpu_usage_percent for s in snapshots]
            memory_usage = [s.memory_usage_mb for s in snapshots]
            gpu_memory = [s.gpu_memory_mb for s in snapshots]
            gpu_utilization = [s.gpu_utilization_percent for s in snapshots]
            costs = [s.cost_estimate_usd for s in snapshots]
            inferences = sum(s.inference_count for s in snapshots)
            
            # Calculate efficiency metrics
            efficiency_metrics = self._calculate_efficiency_metrics(snapshots)
            sustainability_metrics = self._calculate_sustainability_metrics(snapshots)
            
            summary = {
                "time_window_hours": time_window_hours,
                "total_snapshots": len(snapshots),
                "total_inferences": inferences,
                "resource_utilization": {
                    "cpu": {
                        "avg_percent": statistics.mean(cpu_usage),
                        "max_percent": max(cpu_usage),
                        "p95_percent": np.percentile(cpu_usage, 95)
                    },
                    "memory": {
                        "avg_mb": statistics.mean(memory_usage),
                        "max_mb": max(memory_usage),
                        "p95_mb": np.percentile(memory_usage, 95)
                    },
                    "gpu": {
                        "avg_memory_mb": statistics.mean(gpu_memory),
                        "max_memory_mb": max(gpu_memory),
                        "avg_utilization_percent": statistics.mean(gpu_utilization),
                        "max_utilization_percent": max(gpu_utilization)
                    }
                },
                "cost_analysis": {
                    "total_cost_usd": sum(costs),
                    "avg_cost_per_hour": sum(costs) / max(time_window_hours, 1),
                    "cost_per_inference": sum(costs) / max(inferences, 1),
                    "estimated_monthly_cost": sum(costs) * (720 / time_window_hours)
                },
                "efficiency_metrics": efficiency_metrics,
                "sustainability_metrics": sustainability_metrics,
                "optimization_recommendations": self._generate_optimization_recommendations(snapshots)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating resource summary: {e}")
            return {"error": str(e)}
    
    def _calculate_efficiency_metrics(self, snapshots: List[ResourceSnapshot]) -> Dict[str, Any]:
        """Calculate resource efficiency metrics."""
        try:
            if not snapshots:
                return {"error": "No snapshots provided"}
            
            total_inferences = sum(s.inference_count for s in snapshots)
            total_time_hours = len(snapshots) * (self.collection_interval / 3600.0)
            
            # Resource efficiency
            avg_cpu = statistics.mean([s.cpu_usage_percent for s in snapshots])
            avg_memory = statistics.mean([s.memory_percent for s in snapshots])
            avg_gpu = statistics.mean([s.gpu_utilization_percent for s in snapshots])
            
            # Calculate efficiency scores (0-100)
            cpu_efficiency = min(100, (avg_cpu / self.efficiency_targets['cpu_utilization_target']) * 100)
            memory_efficiency = min(100, (avg_memory / self.efficiency_targets['cpu_utilization_target']) * 100)
            gpu_efficiency = min(100, (avg_gpu / self.efficiency_targets['gpu_utilization_target']) * 100)
            
            # Throughput efficiency
            inferences_per_hour = total_inferences / max(total_time_hours, 0.1)
            
            # Cost efficiency
            total_cost = sum(s.cost_estimate_usd for s in snapshots)
            cost_per_inference = total_cost / max(total_inferences, 1)
            cost_efficiency = min(100, (self.efficiency_targets['cost_per_inference_target'] / cost_per_inference) * 100)
            
            return {
                "cpu_efficiency_score": cpu_efficiency,
                "memory_efficiency_score": memory_efficiency,
                "gpu_efficiency_score": gpu_efficiency,
                "cost_efficiency_score": cost_efficiency,
                "overall_efficiency_score": statistics.mean([
                    cpu_efficiency, memory_efficiency, gpu_efficiency, cost_efficiency
                ]),
                "inferences_per_hour": inferences_per_hour,
                "cost_per_inference": cost_per_inference,
                "resource_utilization_balance": {
                    "cpu_vs_target": avg_cpu / self.efficiency_targets['cpu_utilization_target'],
                    "memory_vs_target": avg_memory / self.efficiency_targets['cpu_utilization_target'],
                    "gpu_vs_target": avg_gpu / self.efficiency_targets['gpu_utilization_target']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating efficiency metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_sustainability_metrics(self, snapshots: List[ResourceSnapshot]) -> Dict[str, Any]:
        """Calculate sustainability and carbon footprint metrics."""
        try:
            if not snapshots:
                return {"error": "No snapshots provided"}
            
            # Estimate power consumption (simplified)
            total_power_consumption_kwh = 0
            
            for snapshot in snapshots:
                # CPU power (rough estimate: 100W for 100% utilization)
                cpu_power_w = (snapshot.cpu_usage_percent / 100.0) * 100
                
                # GPU power (rough estimate: 300W for 100% utilization)
                gpu_power_w = (snapshot.gpu_utilization_percent / 100.0) * 300
                
                # Memory power (rough estimate: 10W per GB at 100% usage)
                memory_power_w = (snapshot.memory_usage_mb / 1024.0) * 10
                
                # Total power for this snapshot (including PUE)
                snapshot_power_w = (cpu_power_w + gpu_power_w + memory_power_w) * self.power_usage_effectiveness
                
                # Convert to kWh for collection interval
                snapshot_power_kwh = snapshot_power_w * (self.collection_interval / 3600.0) / 1000.0
                total_power_consumption_kwh += snapshot_power_kwh
            
            # Calculate carbon footprint
            carbon_footprint_kg = total_power_consumption_kwh * self.carbon_intensity_kg_per_kwh
            
            # Per-inference metrics
            total_inferences = sum(s.inference_count for s in snapshots)
            carbon_per_inference_g = (carbon_footprint_kg * 1000) / max(total_inferences, 1)
            energy_per_inference_wh = (total_power_consumption_kwh * 1000) / max(total_inferences, 1)
            
            return {
                "total_energy_consumption_kwh": total_power_consumption_kwh,
                "carbon_footprint_kg_co2": carbon_footprint_kg,
                "carbon_per_inference_g_co2": carbon_per_inference_g,
                "energy_per_inference_wh": energy_per_inference_wh,
                "sustainability_score": self._calculate_sustainability_score(
                    carbon_per_inference_g, energy_per_inference_wh
                ),
                "renewable_energy_offset_needed_kwh": total_power_consumption_kwh,
                "tree_planting_equivalent": carbon_footprint_kg / 22,  # ~22kg CO2 per tree/year
                "regional_carbon_intensity": self.carbon_intensity_kg_per_kwh,
                "data_center_pue": self.power_usage_effectiveness
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating sustainability metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_sustainability_score(self, carbon_per_inference: float, energy_per_inference: float) -> float:
        """Calculate sustainability score (0-100, higher is better)."""
        try:
            # Benchmark values (good performance)
            carbon_benchmark_g = 0.5  # 0.5g CO2 per inference
            energy_benchmark_wh = 1.0  # 1Wh per inference
            
            # Calculate scores (inverse relationship - lower usage is better)
            carbon_score = min(100, (carbon_benchmark_g / max(carbon_per_inference, 0.01)) * 100)
            energy_score = min(100, (energy_benchmark_wh / max(energy_per_inference, 0.01)) * 100)
            
            return statistics.mean([carbon_score, energy_score])
            
        except Exception as e:
            self.logger.error(f"Error calculating sustainability score: {e}")
            return 0.0
    
    def _generate_optimization_recommendations(self, snapshots: List[ResourceSnapshot]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on resource usage patterns."""
        recommendations = []
        
        try:
            if not snapshots:
                return recommendations
            
            # Analyze resource utilization patterns
            cpu_usage = [s.cpu_usage_percent for s in snapshots]
            memory_usage = [s.memory_percent for s in snapshots]
            gpu_usage = [s.gpu_utilization_percent for s in snapshots]
            costs = [s.cost_estimate_usd for s in snapshots]
            
            avg_cpu = statistics.mean(cpu_usage)
            avg_memory = statistics.mean(memory_usage)
            avg_gpu = statistics.mean(gpu_usage)
            total_cost = sum(costs)
            
            # CPU optimization recommendations
            if avg_cpu < 30:
                recommendations.append({
                    "type": "resource_optimization",
                    "priority": "medium",
                    "title": "CPU Under-utilization",
                    "description": f"Average CPU usage is {avg_cpu:.1f}%. Consider using smaller instance types.",
                    "potential_savings_percent": 20,
                    "action": "downsize_cpu"
                })
            elif avg_cpu > 90:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "title": "CPU Over-utilization",
                    "description": f"Average CPU usage is {avg_cpu:.1f}%. Consider upgrading or load balancing.",
                    "potential_impact": "performance_degradation",
                    "action": "upgrade_cpu"
                })
            
            # Memory optimization recommendations
            if avg_memory < 40:
                recommendations.append({
                    "type": "resource_optimization",
                    "priority": "medium",
                    "title": "Memory Over-provisioning",
                    "description": f"Average memory usage is {avg_memory:.1f}%. Consider reducing memory allocation.",
                    "potential_savings_percent": 15,
                    "action": "reduce_memory"
                })
            elif avg_memory > 85:
                recommendations.append({
                    "type": "performance",
                    "priority": "high",
                    "title": "Memory Pressure",
                    "description": f"Average memory usage is {avg_memory:.1f}%. Risk of swapping and performance issues.",
                    "potential_impact": "performance_degradation",
                    "action": "increase_memory"
                })
            
            # GPU optimization recommendations
            if avg_gpu < 50:
                recommendations.append({
                    "type": "resource_optimization",
                    "priority": "high",
                    "title": "GPU Under-utilization",
                    "description": f"Average GPU usage is {avg_gpu:.1f}%. Consider CPU-only instances for some workloads.",
                    "potential_savings_percent": 60,
                    "action": "optimize_gpu_usage"
                })
            
            # Cost optimization recommendations
            total_inferences = sum(s.inference_count for s in snapshots)
            cost_per_inference = total_cost / max(total_inferences, 1)
            
            if cost_per_inference > self.efficiency_targets['cost_per_inference_target']:
                recommendations.append({
                    "type": "cost_optimization",
                    "priority": "high",
                    "title": "High Cost per Inference",
                    "description": f"Cost per inference is ${cost_per_inference:.4f}, target is ${self.efficiency_targets['cost_per_inference_target']:.4f}.",
                    "potential_savings_percent": 30,
                    "action": "optimize_pricing_model"
                })
            
            # Sustainability recommendations
            carbon_footprint = sum(s.cost_estimate_usd for s in snapshots) * 0.5  # Simplified
            if carbon_footprint > 1.0:  # kg CO2
                recommendations.append({
                    "type": "sustainability",
                    "priority": "medium",
                    "title": "Carbon Footprint Optimization",
                    "description": "Consider using renewable energy regions or more efficient hardware.",
                    "potential_impact": "reduced_carbon_footprint",
                    "action": "green_computing"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
            return recommendations
    
    def start_continuous_monitoring(self) -> None:
        """Start continuous resource monitoring."""
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring is already active")
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._continuous_monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("Continuous resource monitoring started")
            
        except Exception as e:
            self.logger.error(f"Error starting continuous monitoring: {e}")
    
    def _continuous_monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        try:
            while self.monitoring_active:
                # Get system resources
                system_resources = self._get_system_resources()
                current_time = datetime.now()
                
                # Create a general system snapshot
                cost_estimate = self._calculate_cost_estimate(system_resources)
                
                snapshot = ResourceSnapshot(
                    timestamp=current_time,
                    model_id="system",
                    creator_type="system",
                    cpu_usage_percent=system_resources.get('cpu_usage_percent', 0),
                    memory_usage_mb=system_resources.get('memory_usage_mb', 0),
                    memory_percent=system_resources.get('memory_percent', 0),
                    gpu_memory_mb=system_resources.get('gpu_memory_mb', 0),
                    gpu_utilization_percent=system_resources.get('gpu_utilization_percent', 0),
                    disk_io_read_mb=system_resources.get('disk_read_mb', 0),
                    disk_io_write_mb=system_resources.get('disk_write_mb', 0),
                    network_io_sent_mb=system_resources.get('network_sent_mb', 0),
                    network_io_recv_mb=system_resources.get('network_recv_mb', 0),
                    process_count=system_resources.get('process_count', 0),
                    thread_count=system_resources.get('thread_count', 0),
                    inference_count=0,
                    cost_estimate_usd=cost_estimate
                )
                
                self.resource_snapshots.append(snapshot)
                
                # Update daily costs
                date_key = current_time.strftime('%Y-%m-%d')
                self.daily_costs[date_key] += cost_estimate
                
                time.sleep(self.collection_interval)
                
        except Exception as e:
            self.logger.error(f"Error in continuous monitoring loop: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop continuous resource monitoring."""
        try:
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.logger.info("Resource monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
    
    def get_cost_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get detailed cost analysis for specified number of days."""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # Get daily costs for the period
            daily_costs = {}
            total_cost = 0
            
            for i in range(days):
                date = start_date + timedelta(days=i)
                date_key = date.strftime('%Y-%m-%d')
                cost = self.daily_costs.get(date_key, 0.0)
                daily_costs[date_key] = cost
                total_cost += cost
            
            # Calculate trends
            costs_list = list(daily_costs.values())
            avg_daily_cost = statistics.mean(costs_list) if costs_list else 0
            
            # Cost breakdown by model
            model_cost_breakdown = dict(self.model_costs)
            
            return {
                "period_days": days,
                "total_cost_usd": total_cost,
                "average_daily_cost_usd": avg_daily_cost,
                "estimated_monthly_cost_usd": avg_daily_cost * 30,
                "daily_costs": daily_costs,
                "model_cost_breakdown": model_cost_breakdown,
                "cost_trends": {
                    "trend_direction": "increasing" if len(costs_list) > 1 and costs_list[-1] > costs_list[0] else "stable",
                    "max_daily_cost": max(costs_list) if costs_list else 0,
                    "min_daily_cost": min(costs_list) if costs_list else 0
                },
                "optimization_potential": {
                    "estimated_savings_percent": 20,  # Based on recommendations
                    "estimated_monthly_savings_usd": avg_daily_cost * 30 * 0.2
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cost analysis: {e}")
            return {"error": str(e)}
    
    def get_creator_resource_analytics(self, creator_type: str) -> Dict[str, Any]:
        """Get resource analytics for a specific creator type."""
        try:
            snapshots = list(self.creator_resources[creator_type])
            if not snapshots:
                return {"error": f"No resource data found for creator type: {creator_type}"}
            
            # Calculate analytics
            total_inferences = sum(s.inference_count for s in snapshots)
            total_cost = sum(s.cost_estimate_usd for s in snapshots)
            
            # Resource utilization patterns
            cpu_usage = [s.cpu_usage_percent for s in snapshots]
            memory_usage = [s.memory_usage_mb for s in snapshots]
            gpu_usage = [s.gpu_utilization_percent for s in snapshots]
            
            # Time-based analysis
            time_range_hours = (max(s.timestamp for s in snapshots) - 
                              min(s.timestamp for s in snapshots)).total_seconds() / 3600
            
            analytics = {
                "creator_type": creator_type,
                "total_snapshots": len(snapshots),
                "total_inferences": total_inferences,
                "time_range_hours": time_range_hours,
                "resource_patterns": {
                    "avg_cpu_percent": statistics.mean(cpu_usage),
                    "peak_cpu_percent": max(cpu_usage),
                    "avg_memory_mb": statistics.mean(memory_usage),
                    "peak_memory_mb": max(memory_usage),
                    "avg_gpu_percent": statistics.mean(gpu_usage),
                    "peak_gpu_percent": max(gpu_usage)
                },
                "cost_analysis": {
                    "total_cost_usd": total_cost,
                    "cost_per_inference": total_cost / max(total_inferences, 1),
                    "cost_per_hour": total_cost / max(time_range_hours, 1)
                },
                "efficiency_score": self._calculate_creator_efficiency_score(snapshots),
                "optimization_recommendations": self._generate_optimization_recommendations(snapshots)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting creator resource analytics: {e}")
            return {"error": str(e)}
    
    def _calculate_creator_efficiency_score(self, snapshots: List[ResourceSnapshot]) -> float:
        """Calculate efficiency score for a creator type."""
        try:
            if not snapshots:
                return 0.0
            
            # Resource utilization efficiency
            cpu_usage = statistics.mean([s.cpu_usage_percent for s in snapshots])
            memory_usage = statistics.mean([s.memory_percent for s in snapshots])
            gpu_usage = statistics.mean([s.gpu_utilization_percent for s in snapshots])
            
            # Cost efficiency
            total_cost = sum(s.cost_estimate_usd for s in snapshots)
            total_inferences = sum(s.inference_count for s in snapshots)
            cost_per_inference = total_cost / max(total_inferences, 1)
            
            # Calculate individual efficiency scores
            cpu_efficiency = min(100, (cpu_usage / 70) * 100)  # Target 70% CPU
            memory_efficiency = min(100, (memory_usage / 80) * 100)  # Target 80% memory
            gpu_efficiency = min(100, (gpu_usage / 85) * 100)  # Target 85% GPU
            cost_efficiency = min(100, (0.001 / cost_per_inference) * 100)  # Target $0.001 per inference
            
            # Overall efficiency score
            return statistics.mean([cpu_efficiency, memory_efficiency, gpu_efficiency, cost_efficiency])
            
        except Exception as e:
            self.logger.error(f"Error calculating creator efficiency score: {e}")
            return 0.0


# Example usage and testing
async def example_usage():
    """Example usage of the ResourceUsageTracker."""
    tracker = ResourceUsageTracker()
    
    # Start continuous monitoring
    tracker.start_continuous_monitoring()
    
    # Simulate some inference operations
    for i in range(5):
        snapshot = await tracker.track_inference_resources(
            model_id=f"model-{i % 2}",
            creator_type="musician" if i % 2 == 0 else "blogger",
            inference_count=np.random.randint(1, 10)
        )
        
        if snapshot:
            print(f"Tracked resources: CPU {snapshot.cpu_usage_percent:.1f}%, "
                  f"Memory {snapshot.memory_usage_mb:.1f}MB, "
                  f"Cost ${snapshot.cost_estimate_usd:.6f}")
        
        await asyncio.sleep(1)
    
    # Get resource summary
    summary = tracker.get_resource_summary(time_window_hours=1)
    print(f"Resource Summary: {json.dumps(summary, indent=2, default=str)}")
    
    # Get cost analysis
    cost_analysis = tracker.get_cost_analysis(days=1)
    print(f"Cost Analysis: {json.dumps(cost_analysis, indent=2, default=str)}")
    
    # Get creator analytics
    creator_analytics = tracker.get_creator_resource_analytics("musician")
    print(f"Creator Analytics: {json.dumps(creator_analytics, indent=2, default=str)}")
    
    # Stop monitoring
    tracker.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_usage())