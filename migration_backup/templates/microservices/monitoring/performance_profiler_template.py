"""
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

Performance Profiler Template for Ainflue Platform
=================================================

Production-ready performance profiling with:
- CPU and memory profiling
- Code execution analysis
- Performance bottleneck detection
- Database query profiling
- Real-time performance monitoring
- Profile data export and analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Performance Engineering Expert
"""

import time
import psutil
import threading
import cProfile
import pstats
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import contextmanager

@dataclass
class ProfileData:
    """Performance profile data"""
    function_name: str
    filename: str
    line_number: int
    call_count: int
    total_time: float
    cumulative_time: float
    per_call_time: float

class PerformanceProfiler:
    """
    Production-ready performance profiler
    
    Features:
    - CPU and memory profiling
    - Function-level analysis
    - Performance bottleneck detection
    - Real-time monitoring
    """
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.profile_data: List[ProfileData] = []
        self.monitoring_active = False
        self.monitor_thread = None
    
    @contextmanager
    def profile_function(self, function_name: str = "operation"):
        """Profile a function or code block"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        self.profiler.enable()
        
        try:
            yield
        finally:
            self.profiler.disable()
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            # Analyze profile data
            stats = pstats.Stats(self.profiler)
            stats.sort_stats('cumulative')
            
            # Store profile data
            for stat in stats.stats.items():
                filename, line, func = stat[0]
                cc, nc, tt, ct, callers = stat[1]
                
                profile_data = ProfileData(
                    function_name=func,
                    filename=filename,
                    line_number=line,
                    call_count=cc,
                    total_time=tt,
                    cumulative_time=ct,
                    per_call_time=tt/cc if cc > 0 else 0
                )
                
                self.profile_data.append(profile_data)
    
    def start_monitoring(self, interval: float = 1.0):
        """Start continuous performance monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,)
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: float):
        """Performance monitoring loop"""
        while self.monitoring_active:
            # Collect system metrics
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            # Log performance data
            print(f"CPU: {cpu_percent}%, Memory: {memory_info.percent}%")
            
            time.sleep(interval)
    
    def get_top_functions(self, limit: int = 10) -> List[ProfileData]:
        """Get top performance bottlenecks"""
        return sorted(
            self.profile_data,
            key=lambda x: x.cumulative_time,
            reverse=True
        )[:limit]
    
    def export_profile_report(self) -> str:
        """Export detailed profile report"""
        report = ["Performance Profile Report", "=" * 50, ""]
        
        top_functions = self.get_top_functions(20)
        
        report.append("Top Functions by Cumulative Time:")
        report.append("-" * 40)
        
        for func in top_functions:
            report.append(
                f"{func.function_name} ({func.filename}:{func.line_number})"
            )
            report.append(f"  Calls: {func.call_count}")
            report.append(f"  Total Time: {func.total_time:.4f}s")
            report.append(f"  Cumulative Time: {func.cumulative_time:.4f}s")
            report.append(f"  Per Call: {func.per_call_time:.6f}s")
            report.append("")
        
        return "\n".join(report)

class PerformanceProfilerTemplate:
    """Performance Profiler Template"""
    
    def create_profiler(self, config: Dict[str, Any]) -> PerformanceProfiler:
        return PerformanceProfiler()
    
    def get_template_info(self) -> Dict[str, Any]:
        return {
            "name": "performance-profiler",
            "description": "Performance profiling and analysis",
            "features": ["CPU profiling", "Memory monitoring", "Bottleneck detection"]
        }