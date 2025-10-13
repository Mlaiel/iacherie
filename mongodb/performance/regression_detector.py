#!/usr/bin/env python3
"""MongoDB Performance Regression Detection
=========================================

Automated performance regression detection and alerting system.
Compares current performance against historical baselines.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import json
import os
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceBaseline:
    """Performance baseline metrics."""
    operation_type: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    operations_per_second: float
    success_rate: float
    cpu_usage_percent: float
    memory_usage_mb: float
    sample_count: int
    last_updated: str
    confidence_level: float

@dataclass
class RegressionAlert:
    """Performance regression alert."""
    alert_id: str
    operation_type: str
    metric_name: str
    baseline_value: float
    current_value: float
    deviation_percent: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    timestamp: str
    suggested_actions: List[str]

@dataclass
class RegressionConfig:
    """Regression detection configuration."""
    latency_threshold_percent: float = 20.0  # Alert if latency increases by 20%
    throughput_threshold_percent: float = 15.0  # Alert if throughput decreases by 15%
    success_rate_threshold_percent: float = 1.0  # Alert if success rate drops by 1%
    cpu_threshold_percent: float = 25.0  # Alert if CPU usage increases by 25%
    memory_threshold_percent: float = 30.0  # Alert if memory usage increases by 30%
    min_samples_for_baseline: int = 10
    baseline_retention_days: int = 30
    alert_retention_days: int = 7

class PerformanceRegressionDetector:
    """MongoDB performance regression detection system."""
    
    def __init__(self, config: RegressionConfig = None, storage_dir: str = None):
        self.config = config or RegressionConfig()
        self.storage_dir = Path(storage_dir or "performance_data")
        self.storage_dir.mkdir(exist_ok=True)
        
        self.baselines_file = self.storage_dir / "performance_baselines.json"
        self.alerts_file = self.storage_dir / "regression_alerts.json"
        self.history_file = self.storage_dir / "performance_history.json"
        
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.alerts: List[RegressionAlert] = []
        self.history: List[Dict[str, Any]] = []
        
        self._load_data()
    
    def _load_data(self):
        """Load existing performance data."""
        try:
            # Load baselines
            if self.baselines_file.exists():
                with open(self.baselines_file, 'r') as f:
                    data = json.load(f)
                    self.baselines = {
                        k: PerformanceBaseline(**v) for k, v in data.items()
                    }
            
            # Load alerts
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = [RegressionAlert(**alert) for alert in data]
            
            # Load history
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            
            # Clean old data
            self._cleanup_old_data()
            
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")
    
    def _save_data(self):
        """Save performance data to storage."""
        try:
            # Save baselines
            with open(self.baselines_file, 'w') as f:
                data = {k: asdict(v) for k, v in self.baselines.items()}
                json.dump(data, f, indent=2, default=str)
            
            # Save alerts
            with open(self.alerts_file, 'w') as f:
                data = [asdict(alert) for alert in self.alerts]
                json.dump(data, f, indent=2, default=str)
            
            # Save history
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old performance data."""
        now = datetime.now(timezone.utc)
        
        # Remove old alerts
        cutoff_date = now - timedelta(days=self.config.alert_retention_days)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00')) > cutoff_date
        ]
        
        # Remove old history
        history_cutoff = now - timedelta(days=self.config.baseline_retention_days)
        self.history = [
            entry for entry in self.history
            if datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00')) > history_cutoff
        ]
    
    def add_performance_data(self, benchmark_results: List[Dict[str, Any]]):
        """Add new performance data and update baselines."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Add to history
        history_entry = {
            'timestamp': timestamp,
            'results': benchmark_results
        }
        self.history.append(history_entry)
        
        # Update baselines
        for result in benchmark_results:
            operation_type = result.get('operation_type', 'unknown')
            self._update_baseline(operation_type, result, timestamp)
        
        # Save updated data
        self._save_data()
    
    def _update_baseline(self, operation_type: str, result: Dict[str, Any], timestamp: str):
        """Update performance baseline for an operation type."""
        # Get historical data for this operation type
        historical_data = self._get_historical_data(operation_type)
        
        if len(historical_data) < self.config.min_samples_for_baseline:
            # Not enough samples yet, store current result as initial baseline
            baseline = PerformanceBaseline(
                operation_type=operation_type,
                avg_latency_ms=result.get('avg_latency_ms', 0),
                p95_latency_ms=result.get('p95_latency_ms', 0),
                p99_latency_ms=result.get('p99_latency_ms', 0),
                operations_per_second=result.get('operations_per_second', 0),
                success_rate=result.get('success_rate', 100),
                cpu_usage_percent=result.get('cpu_usage_percent', 0),
                memory_usage_mb=result.get('memory_usage_mb', 0),
                sample_count=len(historical_data) + 1,
                last_updated=timestamp,
                confidence_level=0.5  # Low confidence with few samples
            )
        else:
            # Calculate new baseline from historical data
            baseline = self._calculate_baseline(operation_type, historical_data, timestamp)
        
        self.baselines[operation_type] = baseline
    
    def _get_historical_data(self, operation_type: str) -> List[Dict[str, Any]]:
        """Get historical performance data for an operation type."""
        historical_data = []
        
        for entry in self.history:
            for result in entry['results']:
                if result.get('operation_type') == operation_type:
                    historical_data.append(result)
        
        return historical_data
    
    def _calculate_baseline(self, operation_type: str, historical_data: List[Dict[str, Any]], timestamp: str) -> PerformanceBaseline:
        """Calculate performance baseline from historical data."""
        # Extract metrics
        latencies = [d.get('avg_latency_ms', 0) for d in historical_data]
        p95_latencies = [d.get('p95_latency_ms', 0) for d in historical_data]
        p99_latencies = [d.get('p99_latency_ms', 0) for d in historical_data]
        throughputs = [d.get('operations_per_second', 0) for d in historical_data]
        success_rates = [d.get('success_rate', 100) for d in historical_data]
        cpu_usages = [d.get('cpu_usage_percent', 0) for d in historical_data]
        memory_usages = [d.get('memory_usage_mb', 0) for d in historical_data]
        
        # Calculate confidence level based on sample count and variance
        sample_count = len(historical_data)
        latency_variance = statistics.variance(latencies) if len(latencies) > 1 else 0
        confidence = min(0.95, 0.5 + (sample_count - 10) * 0.05)  # Increase confidence with more samples
        
        if latency_variance > 0:
            confidence *= max(0.5, 1 - (latency_variance / statistics.mean(latencies)))
        
        return PerformanceBaseline(
            operation_type=operation_type,
            avg_latency_ms=statistics.median(latencies),
            p95_latency_ms=statistics.median(p95_latencies),
            p99_latency_ms=statistics.median(p99_latencies),
            operations_per_second=statistics.median(throughputs),
            success_rate=statistics.median(success_rates),
            cpu_usage_percent=statistics.median(cpu_usages),
            memory_usage_mb=statistics.median(memory_usages),
            sample_count=sample_count,
            last_updated=timestamp,
            confidence_level=confidence
        )
    
    def detect_regressions(self, current_results: List[Dict[str, Any]]) -> List[RegressionAlert]:
        """Detect performance regressions in current results."""
        new_alerts = []
        
        for result in current_results:
            operation_type = result.get('operation_type', 'unknown')
            
            if operation_type not in self.baselines:
                continue
            
            baseline = self.baselines[operation_type]
            
            # Skip detection if baseline has low confidence
            if baseline.confidence_level < 0.7:
                continue
            
            # Check each metric for regression
            alerts = self._check_metric_regressions(result, baseline)
            new_alerts.extend(alerts)
        
        # Add new alerts to the list
        self.alerts.extend(new_alerts)
        
        # Save updated alerts
        self._save_data()
        
        return new_alerts
    
    def _check_metric_regressions(self, result: Dict[str, Any], baseline: PerformanceBaseline) -> List[RegressionAlert]:
        """Check for regressions in individual metrics."""
        alerts = []
        timestamp = datetime.now(timezone.utc).isoformat()
        operation_type = result.get('operation_type', 'unknown')
        
        # Check latency regression (higher is worse)
        current_latency = result.get('avg_latency_ms', 0)
        if current_latency > 0 and baseline.avg_latency_ms > 0:
            latency_increase = ((current_latency - baseline.avg_latency_ms) / baseline.avg_latency_ms) * 100
            
            if latency_increase > self.config.latency_threshold_percent:
                severity = self._calculate_severity(latency_increase, self.config.latency_threshold_percent)
                
                alert = RegressionAlert(
                    alert_id=f"latency_{operation_type}_{timestamp}",
                    operation_type=operation_type,
                    metric_name="avg_latency_ms",
                    baseline_value=baseline.avg_latency_ms,
                    current_value=current_latency,
                    deviation_percent=latency_increase,
                    severity=severity,
                    description=f"Average latency increased by {latency_increase:.1f}% for {operation_type} operations",
                    timestamp=timestamp,
                    suggested_actions=[
                        "Check for missing or inefficient indexes",
                        "Analyze slow query logs",
                        "Review connection pool settings",
                        "Monitor system resources (CPU, memory, disk I/O)"
                    ]
                )
                alerts.append(alert)
        
        # Check throughput regression (lower is worse)
        current_throughput = result.get('operations_per_second', 0)
        if current_throughput > 0 and baseline.operations_per_second > 0:
            throughput_decrease = ((baseline.operations_per_second - current_throughput) / baseline.operations_per_second) * 100
            
            if throughput_decrease > self.config.throughput_threshold_percent:
                severity = self._calculate_severity(throughput_decrease, self.config.throughput_threshold_percent)
                
                alert = RegressionAlert(
                    alert_id=f"throughput_{operation_type}_{timestamp}",
                    operation_type=operation_type,
                    metric_name="operations_per_second",
                    baseline_value=baseline.operations_per_second,
                    current_value=current_throughput,
                    deviation_percent=throughput_decrease,
                    severity=severity,
                    description=f"Throughput decreased by {throughput_decrease:.1f}% for {operation_type} operations",
                    timestamp=timestamp,
                    suggested_actions=[
                        "Increase connection pool size",
                        "Optimize database indexes",
                        "Scale MongoDB cluster",
                        "Review application code for inefficiencies"
                    ]
                )
                alerts.append(alert)
        
        # Check success rate regression (lower is worse)
        current_success_rate = result.get('success_rate', 100)
        if baseline.success_rate > 0:
            success_rate_decrease = baseline.success_rate - current_success_rate
            
            if success_rate_decrease > self.config.success_rate_threshold_percent:
                severity = "CRITICAL" if success_rate_decrease > 5 else "HIGH"
                
                alert = RegressionAlert(
                    alert_id=f"success_rate_{operation_type}_{timestamp}",
                    operation_type=operation_type,
                    metric_name="success_rate",
                    baseline_value=baseline.success_rate,
                    current_value=current_success_rate,
                    deviation_percent=success_rate_decrease,
                    severity=severity,
                    description=f"Success rate decreased by {success_rate_decrease:.1f}% for {operation_type} operations",
                    timestamp=timestamp,
                    suggested_actions=[
                        "Check MongoDB server status and logs",
                        "Verify network connectivity",
                        "Review authentication and authorization settings",
                        "Monitor database resource utilization"
                    ]
                )
                alerts.append(alert)
        
        return alerts
    
    def _calculate_severity(self, deviation_percent: float, threshold_percent: float) -> str:
        """Calculate alert severity based on deviation."""
        if deviation_percent >= threshold_percent * 3:
            return "CRITICAL"
        elif deviation_percent >= threshold_percent * 2:
            return "HIGH"
        elif deviation_percent >= threshold_percent * 1.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        now = datetime.now(timezone.utc)
        
        # Calculate summary statistics
        active_alerts = [a for a in self.alerts if self._is_alert_active(a)]
        recent_alerts = [
            a for a in self.alerts
            if datetime.fromisoformat(a.timestamp.replace('Z', '+00:00')) > now - timedelta(days=1)
        ]
        
        # Performance trends
        trends = self._calculate_performance_trends()
        
        report = {
            "generated_at": now.isoformat(),
            "summary": {
                "total_baselines": len(self.baselines),
                "active_alerts": len(active_alerts),
                "recent_alerts_24h": len(recent_alerts),
                "historical_data_points": len(self.history)
            },
            "baselines": {k: asdict(v) for k, v in self.baselines.items()},
            "active_alerts": [asdict(a) for a in active_alerts],
            "recent_alerts": [asdict(a) for a in recent_alerts],
            "performance_trends": trends,
            "configuration": asdict(self.config)
        }
        
        return report
    
    def _is_alert_active(self, alert: RegressionAlert) -> bool:
        """Check if an alert is still active (within retention period)."""
        alert_time = datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00'))
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        return alert_time > cutoff_time
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time."""
        trends = {}
        
        for operation_type in self.baselines:
            historical_data = self._get_historical_data(operation_type)
            
            if len(historical_data) < 3:
                continue
            
            # Sort by timestamp
            historical_data.sort(key=lambda x: x.get('timestamp', ''))
            
            # Calculate trends for key metrics
            latencies = [d.get('avg_latency_ms', 0) for d in historical_data[-10:]]  # Last 10 data points
            throughputs = [d.get('operations_per_second', 0) for d in historical_data[-10:]]
            
            if len(latencies) >= 3:
                latency_trend = self._calculate_trend(latencies)
                throughput_trend = self._calculate_trend(throughputs)
                
                trends[operation_type] = {
                    "latency_trend": latency_trend,
                    "throughput_trend": throughput_trend,
                    "data_points": len(historical_data),
                    "trend_direction": "improving" if latency_trend < 0 and throughput_trend > 0 else "degrading" if latency_trend > 0 or throughput_trend < 0 else "stable"
                }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend (slope) for a series of values."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate linear regression slope
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def save_report(self, filename: str = None) -> str:
        """Save performance report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_regression_report_{timestamp}.json"
        
        report = self.get_performance_report()
        
        filepath = self.storage_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(filepath)
    
    def print_alert_summary(self):
        """Print summary of performance alerts."""
        active_alerts = [a for a in self.alerts if self._is_alert_active(a)]
        
        if not active_alerts:
            print("✅ No active performance alerts")
            return
        
        print(f"🚨 {len(active_alerts)} Active Performance Alerts")
        print("=" * 50)
        
        # Group by severity
        by_severity = {}
        for alert in active_alerts:
            severity = alert.severity
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(alert)
        
        # Display by severity (highest first)
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in by_severity:
                print(f"\n{severity} ({len(by_severity[severity])} alerts):")
                for alert in by_severity[severity]:
                    print(f"  • {alert.description}")
                    print(f"    Deviation: {alert.deviation_percent:.1f}%")
                    if alert.suggested_actions:
                        print(f"    Suggested: {alert.suggested_actions[0]}")

def main():
    """CLI interface for regression detection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MongoDB Performance Regression Detection")
    parser.add_argument("--data-dir", help="Directory for performance data storage")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--alerts", action="store_true", help="Show active alerts")
    parser.add_argument("--benchmark-file", help="Add benchmark results from file")
    
    args = parser.parse_args()
    
    detector = PerformanceRegressionDetector(storage_dir=args.data_dir)
    
    if args.benchmark_file:
        # Load and process benchmark results
        with open(args.benchmark_file, 'r') as f:
            benchmark_data = json.load(f)
        
        if 'results' in benchmark_data:
            detector.add_performance_data(benchmark_data['results'])
            alerts = detector.detect_regressions(benchmark_data['results'])
            
            if alerts:
                print(f"🚨 Detected {len(alerts)} performance regressions!")
                for alert in alerts:
                    print(f"  • {alert.description}")
            else:
                print("✅ No performance regressions detected")
    
    if args.alerts:
        detector.print_alert_summary()
    
    if args.report:
        report_file = detector.save_report()
        print(f"📋 Performance report saved to: {report_file}")

if __name__ == "__main__":
    main()