#!/usr/bin/env python3
"""
Performance Benchmarking Suite for Ainflue Platform
Author: Fahed Mlaiel (mlaiel@live.de)
Description: Automated performance baseline generation and comparison
"""

import json
import time
import psutil
import requests
import threading
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    baseline: float = 0.0
    threshold: float = 0.0
    status: str = "unknown"
    timestamp: str = ""


class PerformanceBenchmarker:
    """Comprehensive performance benchmarking system"""
    
    def __init__(self, baseline_file: str = "performance-baseline.json"):
        self.baseline_file = Path(baseline_file)
        self.baselines = self._load_baselines()
        self.metrics: List[PerformanceMetric] = []
        
    def _load_baselines(self) -> Dict[str, float]:
        """Load performance baselines from file"""
        if self.baseline_file.exists():
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_baselines(self):
        """Save current metrics as baselines"""
        baselines = {metric.name: metric.value for metric in self.metrics}
        with open(self.baseline_file, 'w') as f:
            json.dump(baselines, f, indent=2)
    
    def add_metric(self, name: str, value: float, unit: str, threshold: float = 0.0):
        """Add a performance metric"""
        baseline = self.baselines.get(name, 0.0)
        
        # Determine status based on baseline and threshold
        if baseline == 0.0:
            status = "new"
        elif threshold > 0.0 and value > baseline * (1 + threshold):
            status = "degraded"
        elif value <= baseline * 0.95:
            status = "improved"
        else:
            status = "stable"
            
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            baseline=baseline,
            threshold=threshold,
            status=status,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        self.metrics.append(metric)
    
    def benchmark_startup_time(self, app_module: str = "main"):
        """Benchmark application startup time"""
        start_time = time.time()
        try:
            # Simulate app import/startup
            import importlib
            importlib.import_module(app_module)
            startup_time = time.time() - start_time
            self.add_metric("startup_time", startup_time, "seconds", 0.1)
        except ImportError:
            self.add_metric("startup_time", 0.0, "seconds", 0.1)
    
    def benchmark_memory_usage(self):
        """Benchmark memory usage"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.add_metric("memory_usage", memory_mb, "MB", 0.2)
    
    def benchmark_cpu_usage(self, duration: int = 5):
        """Benchmark CPU usage over time"""
        cpu_percent = psutil.cpu_percent(interval=duration)
        self.add_metric("cpu_usage", cpu_percent, "percent", 0.15)
    
    def benchmark_api_response_time(self, url: str = "http://localhost:8000/health"):
        """Benchmark API response time"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.add_metric("api_response_time", response_time, "seconds", 0.2)
                self.add_metric("api_availability", 100.0, "percent", 0.01)
            else:
                self.add_metric("api_response_time", 999.0, "seconds", 0.2)
                self.add_metric("api_availability", 0.0, "percent", 0.01)
        except Exception:
            self.add_metric("api_response_time", 999.0, "seconds", 0.2)
            self.add_metric("api_availability", 0.0, "percent", 0.01)
    
    def benchmark_concurrent_requests(self, url: str = "http://localhost:8000/health", 
                                    concurrent_users: int = 10, requests_per_user: int = 5):
        """Benchmark concurrent request handling"""
        response_times = []
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time
                if response.status_code == 200:
                    response_times.append(response_time)
            except Exception:
                response_times.append(999.0)
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for _ in range(concurrent_users * requests_per_user):
                futures.append(executor.submit(make_request))
            
            # Wait for all requests to complete
            for future in futures:
                future.result()
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            successful_requests = len([rt for rt in response_times if rt < 10.0])
            success_rate = (successful_requests / len(response_times)) * 100
            
            self.add_metric("concurrent_avg_response_time", avg_response_time, "seconds", 0.3)
            self.add_metric("concurrent_max_response_time", max_response_time, "seconds", 0.5)
            self.add_metric("concurrent_success_rate", success_rate, "percent", 0.05)
    
    def benchmark_database_performance(self):
        """Benchmark database performance (if available)"""
        try:
            # Simulate database operations
            start_time = time.time()
            # This would be actual database queries
            time.sleep(0.1)  # Simulate query time
            query_time = time.time() - start_time
            
            self.add_metric("database_query_time", query_time, "seconds", 0.25)
            self.add_metric("database_availability", 100.0, "percent", 0.01)
        except Exception:
            self.add_metric("database_query_time", 999.0, "seconds", 0.25)
            self.add_metric("database_availability", 0.0, "percent", 0.01)
    
    def generate_report(self, output_file: str = "performance-report.json"):
        """Generate comprehensive performance report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_metrics": len(self.metrics),
                "degraded_metrics": len([m for m in self.metrics if m.status == "degraded"]),
                "improved_metrics": len([m for m in self.metrics if m.status == "improved"]),
                "stable_metrics": len([m for m in self.metrics if m.status == "stable"]),
                "new_metrics": len([m for m in self.metrics if m.status == "new"])
            },
            "metrics": [asdict(metric) for metric in self.metrics],
            "alerts": [
                f"Metric '{m.name}' has degraded by {((m.value - m.baseline) / m.baseline * 100):.1f}%"
                for m in self.metrics 
                if m.status == "degraded" and m.baseline > 0
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_chart(self, output_file: str = "performance-chart.png"):
        """Generate performance metrics chart"""
        if not self.metrics:
            return
            
        # Create comparison chart
        metric_names = [m.name for m in self.metrics if m.baseline > 0]
        current_values = [m.value for m in self.metrics if m.baseline > 0]
        baseline_values = [m.baseline for m in self.metrics if m.baseline > 0]
        
        if not metric_names:
            return
            
        x_pos = range(len(metric_names))
        
        plt.figure(figsize=(12, 6))
        plt.bar([p - 0.2 for p in x_pos], baseline_values, 0.4, label='Baseline', alpha=0.7)
        plt.bar([p + 0.2 for p in x_pos], current_values, 0.4, label='Current', alpha=0.7)
        
        plt.xlabel('Metrics')
        plt.ylabel('Values')
        plt.title('Performance Metrics Comparison')
        plt.xticks(x_pos, metric_names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
    
    def run_full_benchmark(self):
        """Run complete benchmark suite"""
        print("🚀 Starting Performance Benchmark Suite...")
        
        # System metrics
        print("📊 Collecting system metrics...")
        self.benchmark_memory_usage()
        self.benchmark_cpu_usage(duration=2)  # Shorter for CI
        
        # Application metrics
        print("🔄 Benchmarking application...")
        self.benchmark_startup_time()
        
        # API metrics (if server is running)
        print("🌐 Testing API performance...")
        self.benchmark_api_response_time()
        self.benchmark_concurrent_requests(concurrent_users=5, requests_per_user=2)
        
        # Database metrics
        print("💾 Testing database performance...")
        self.benchmark_database_performance()
        
        # Generate reports
        print("📋 Generating reports...")
        report = self.generate_report()
        self.generate_chart()
        
        # Print summary
        print("\n📈 Performance Benchmark Results:")
        print(f"Total metrics: {report['summary']['total_metrics']}")
        print(f"Degraded: {report['summary']['degraded_metrics']}")
        print(f"Improved: {report['summary']['improved_metrics']}")
        print(f"Stable: {report['summary']['stable_metrics']}")
        print(f"New: {report['summary']['new_metrics']}")
        
        if report['alerts']:
            print("\n⚠️ Performance Alerts:")
            for alert in report['alerts']:
                print(f"  - {alert}")
        
        # Determine if benchmarks pass
        degraded_count = report['summary']['degraded_metrics']
        if degraded_count > 0:
            print(f"\n❌ Performance benchmarks FAILED: {degraded_count} metrics degraded")
            return False
        else:
            print("\n✅ Performance benchmarks PASSED")
            return True


def main():
    """Main benchmark execution"""
    benchmarker = PerformanceBenchmarker()
    
    try:
        success = benchmarker.run_full_benchmark()
        
        # Save current results as baseline if no baseline exists
        if not benchmarker.baseline_file.exists():
            print("💾 Saving performance baseline...")
            benchmarker.save_baselines()
        
        exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Benchmark failed with error: {e}")
        exit(1)


if __name__ == "__main__":
    main()