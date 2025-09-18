#!/usr/bin/env python3
"""
🏃 PERFORMANCE TEST TEMPLATE - COMPREHENSIVE PERFORMANCE TESTING
================================================================

Performance testing with resource monitoring, bottleneck detection,
and optimization recommendations for microservices.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

import asyncio
import psutil
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_received_mb: float = 0.0
    response_time_ms: float = 0.0

class PerformanceTestTemplate:
    """Enterprise performance testing template"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics_history: List[PerformanceMetrics] = []
    
    async def monitor_system_resources(self, duration_seconds: int = 60) -> List[PerformanceMetrics]:
        """Monitor system resources during test"""
        metrics = []
        
        for _ in range(duration_seconds):
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            metric = PerformanceMetrics(
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory.used / 1024 / 1024,
                disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
                disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
                network_sent_mb=network_io.bytes_sent / 1024 / 1024 if network_io else 0,
                network_received_mb=network_io.bytes_recv / 1024 / 1024 if network_io else 0
            )
            
            metrics.append(metric)
            await asyncio.sleep(1)
        
        self.metrics_history.extend(metrics)
        return metrics
    
    def analyze_bottlenecks(self) -> Dict[str, str]:
        """Analyze performance bottlenecks"""
        if not self.metrics_history:
            return {}
        
        avg_cpu = sum(m.cpu_usage_percent for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m.memory_usage_mb for m in self.metrics_history) / len(self.metrics_history)
        
        bottlenecks = {}
        
        if avg_cpu > 80:
            bottlenecks["CPU"] = f"High CPU usage: {avg_cpu:.1f}%"
        
        if avg_memory > 1024:  # > 1GB
            bottlenecks["Memory"] = f"High memory usage: {avg_memory:.1f}MB"
        
        return bottlenecks
    
    def generate_performance_report(self) -> str:
        """Generate performance test report"""
        bottlenecks = self.analyze_bottlenecks()
        
        report = f"=== PERFORMANCE TEST REPORT - {self.service_name} ===\n"
        
        if bottlenecks:
            report += "BOTTLENECKS DETECTED:\n"
            for resource, issue in bottlenecks.items():
                report += f"- {resource}: {issue}\n"
        else:
            report += "No significant bottlenecks detected.\n"
        
        return report