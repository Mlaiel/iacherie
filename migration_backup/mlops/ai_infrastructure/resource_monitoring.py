"""
Resource Monitoring System
Comprehensive resource monitoring for AI infrastructure

Features:
- Real-time resource tracking
- Multi-dimensional metrics collection
- Predictive resource analytics
- Alert management
- Performance optimization insights

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil
import numpy as np


@dataclass
class MonitoringConfig:
    """Configuration for resource monitoring"""
    collection_interval: int = 30  # seconds
    retention_period: int = 7  # days
    alert_thresholds: Dict[str, float] = None
    metrics_enabled: List[str] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "cpu": 0.8,
                "memory": 0.85,
                "disk": 0.9,
                "gpu": 0.9
            }
        if self.metrics_enabled is None:
            self.metrics_enabled = ["cpu", "memory", "disk", "network", "gpu"]


class ResourceMonitoringSystem:
    """Comprehensive resource monitoring for AI infrastructure"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics_storage = {}
        self.alerts = []
        self.monitoring_active = False
        
    async def start_monitoring(self) -> Dict[str, Any]:
        """Start resource monitoring"""
        try:
            if self.monitoring_active:
                return {"status": "already_running"}
            
            self.monitoring_active = True
            
            # Start monitoring task
            asyncio.create_task(self._monitoring_loop())
            
            # Initialize metrics storage
            await self._initialize_metrics_storage()
            
            return {
                "status": "success",
                "monitoring_started": True,
                "collection_interval": self.config.collection_interval,
                "enabled_metrics": self.config.metrics_enabled
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return {"status": "error", "error": str(e)}
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop resource monitoring"""
        try:
            self.monitoring_active = False
            
            return {
                "status": "success",
                "monitoring_stopped": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current resource metrics"""
        try:
            metrics = {}
            
            # CPU metrics
            if "cpu" in self.config.metrics_enabled:
                metrics["cpu"] = await self._collect_cpu_metrics()
            
            # Memory metrics
            if "memory" in self.config.metrics_enabled:
                metrics["memory"] = await self._collect_memory_metrics()
            
            # Disk metrics
            if "disk" in self.config.metrics_enabled:
                metrics["disk"] = await self._collect_disk_metrics()
            
            # Network metrics
            if "network" in self.config.metrics_enabled:
                metrics["network"] = await self._collect_network_metrics()
            
            # GPU metrics
            if "gpu" in self.config.metrics_enabled:
                metrics["gpu"] = await self._collect_gpu_metrics()
            
            # AI workload metrics
            metrics["ai_workloads"] = await self._collect_ai_workload_metrics()
            
            metrics["timestamp"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "metrics": metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_historical_metrics(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get historical metrics data"""
        try:
            # Parse time range
            hours = self._parse_time_range(time_range)
            start_time = datetime.now() - timedelta(hours=hours)
            
            # Filter metrics by time range
            historical_data = {}
            for metric_type, data_points in self.metrics_storage.items():
                filtered_points = [
                    point for point in data_points 
                    if point["timestamp"] >= start_time
                ]
                historical_data[metric_type] = filtered_points
            
            # Generate statistics
            statistics = await self._calculate_metrics_statistics(historical_data)
            
            return {
                "status": "success",
                "time_range": time_range,
                "data_points": len(sum(historical_data.values(), [])),
                "historical_data": historical_data,
                "statistics": statistics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get historical metrics: {e}")
            return {"status": "error", "error": str(e)}
    
    async def analyze_resource_trends(self) -> Dict[str, Any]:
        """Analyze resource usage trends"""
        try:
            trends = {}
            
            for metric_type in self.config.metrics_enabled:
                if metric_type in self.metrics_storage:
                    trend_analysis = await self._analyze_metric_trend(metric_type)
                    trends[metric_type] = trend_analysis
            
            # Generate predictions
            predictions = await self._predict_resource_usage(trends)
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(trends)
            
            return {
                "status": "success",
                "trends": trends,
                "predictions": predictions,
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def check_alert_conditions(self) -> Dict[str, Any]:
        """Check for alert conditions"""
        try:
            current_metrics = await self.get_current_metrics()
            
            if current_metrics["status"] != "success":
                return current_metrics
            
            metrics = current_metrics["metrics"]
            triggered_alerts = []
            
            # Check each metric against thresholds
            for metric_type, threshold in self.config.alert_thresholds.items():
                if metric_type in metrics:
                    metric_value = self._extract_metric_value(metrics[metric_type])
                    
                    if metric_value > threshold:
                        alert = {
                            "type": metric_type,
                            "severity": self._calculate_alert_severity(metric_value, threshold),
                            "current_value": metric_value,
                            "threshold": threshold,
                            "timestamp": datetime.now().isoformat(),
                            "message": f"{metric_type.upper()} usage ({metric_value:.2%}) exceeds threshold ({threshold:.2%})"
                        }
                        triggered_alerts.append(alert)
                        self.alerts.append(alert)
            
            return {
                "status": "success",
                "alerts_triggered": len(triggered_alerts),
                "alerts": triggered_alerts
            }
            
        except Exception as e:
            self.logger.error(f"Alert check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        try:
            status = {
                "monitoring_active": self.monitoring_active,
                "collection_interval": self.config.collection_interval,
                "enabled_metrics": self.config.metrics_enabled,
                "total_data_points": sum(len(data) for data in self.metrics_storage.values()),
                "recent_alerts": len([a for a in self.alerts if 
                                   datetime.fromisoformat(a["timestamp"]) > datetime.now() - timedelta(hours=1)]),
                "storage_usage": await self._get_storage_usage(),
                "health": "healthy" if self.monitoring_active else "stopped"
            }
            
            return {
                "status": "success",
                "monitoring_status": status
            }
            
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect current metrics
                metrics_result = await self.get_current_metrics()
                
                if metrics_result["status"] == "success":
                    # Store metrics
                    await self._store_metrics(metrics_result["metrics"])
                    
                    # Check for alerts
                    await self.check_alert_conditions()
                    
                    # Cleanup old data
                    await self._cleanup_old_metrics()
                
                # Wait for next collection
                await asyncio.sleep(self.config.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.config.collection_interval)
    
    async def _initialize_metrics_storage(self):
        """Initialize metrics storage"""
        for metric_type in self.config.metrics_enabled:
            if metric_type not in self.metrics_storage:
                self.metrics_storage[metric_type] = []
    
    async def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect CPU metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        
        return {
            "utilization": cpu_percent / 100.0,
            "core_count": cpu_count,
            "load_average": {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2]
            }
        }
    
    async def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect memory metrics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "utilization": memory.percent / 100.0,
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "swap_utilization": swap.percent / 100.0
        }
    
    async def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect disk metrics"""
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        return {
            "utilization": (disk_usage.used / disk_usage.total),
            "total_gb": disk_usage.total / (1024**3),
            "free_gb": disk_usage.free / (1024**3),
            "read_iops": disk_io.read_count if disk_io else 0,
            "write_iops": disk_io.write_count if disk_io else 0
        }
    
    async def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect network metrics"""
        network_io = psutil.net_io_counters()
        
        return {
            "bytes_sent": network_io.bytes_sent if network_io else 0,
            "bytes_recv": network_io.bytes_recv if network_io else 0,
            "packets_sent": network_io.packets_sent if network_io else 0,
            "packets_recv": network_io.packets_recv if network_io else 0
        }
    
    async def _collect_gpu_metrics(self) -> Dict[str, Any]:
        """Collect GPU metrics"""
        # Simulate GPU metrics (would use nvidia-ml-py in real implementation)
        return {
            "utilization": np.random.uniform(0.3, 0.9),
            "memory_utilization": np.random.uniform(0.4, 0.8),
            "temperature": np.random.uniform(65, 80),
            "power_usage": np.random.uniform(150, 250)
        }
    
    async def _collect_ai_workload_metrics(self) -> Dict[str, Any]:
        """Collect AI workload specific metrics"""
        return {
            "active_models": np.random.randint(5, 15),
            "inference_requests": np.random.randint(100, 1000),
            "training_jobs": np.random.randint(1, 5),
            "model_accuracy": np.random.uniform(0.85, 0.95)
        }
    
    async def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in internal storage"""
        timestamp = datetime.now()
        
        for metric_type, metric_data in metrics.items():
            if metric_type != "timestamp" and metric_type in self.config.metrics_enabled:
                data_point = {
                    "timestamp": timestamp,
                    "data": metric_data
                }
                
                if metric_type not in self.metrics_storage:
                    self.metrics_storage[metric_type] = []
                
                self.metrics_storage[metric_type].append(data_point)
    
    async def _cleanup_old_metrics(self):
        """Remove old metrics data"""
        cutoff_time = datetime.now() - timedelta(days=self.config.retention_period)
        
        for metric_type in self.metrics_storage:
            self.metrics_storage[metric_type] = [
                point for point in self.metrics_storage[metric_type]
                if point["timestamp"] > cutoff_time
            ]
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours"""
        if time_range.endswith('h'):
            return int(time_range[:-1])
        elif time_range.endswith('d'):
            return int(time_range[:-1]) * 24
        else:
            return 1  # Default to 1 hour
    
    async def _calculate_metrics_statistics(self, historical_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate statistics for historical metrics"""
        statistics = {}
        
        for metric_type, data_points in historical_data.items():
            if data_points:
                values = [self._extract_metric_value(point["data"]) for point in data_points]
                statistics[metric_type] = {
                    "mean": np.mean(values),
                    "max": np.max(values),
                    "min": np.min(values),
                    "std": np.std(values),
                    "count": len(values)
                }
        
        return statistics
    
    async def _analyze_metric_trend(self, metric_type: str) -> Dict[str, Any]:
        """Analyze trend for specific metric"""
        if metric_type not in self.metrics_storage:
            return {"trend": "no_data"}
        
        data_points = self.metrics_storage[metric_type][-50:]  # Last 50 points
        if len(data_points) < 10:
            return {"trend": "insufficient_data"}
        
        values = [self._extract_metric_value(point["data"]) for point in data_points]
        
        # Simple trend calculation
        recent_avg = np.mean(values[-10:])
        older_avg = np.mean(values[:10])
        trend_direction = "increasing" if recent_avg > older_avg else "decreasing"
        
        return {
            "trend": trend_direction,
            "recent_average": recent_avg,
            "change_rate": (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        }
    
    async def _predict_resource_usage(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future resource usage"""
        predictions = {}
        
        for metric_type, trend_data in trends.items():
            if trend_data.get("trend") == "increasing":
                prediction = "high_usage_expected"
            elif trend_data.get("trend") == "decreasing":
                prediction = "low_usage_expected"
            else:
                prediction = "stable_usage_expected"
            
            predictions[metric_type] = {
                "prediction": prediction,
                "confidence": 0.7
            }
        
        return predictions
    
    async def _generate_optimization_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        for metric_type, trend_data in trends.items():
            if trend_data.get("recent_average", 0) > 0.8:
                recommendations.append(f"Consider scaling up {metric_type} resources")
            elif trend_data.get("recent_average", 0) < 0.3:
                recommendations.append(f"Consider scaling down {metric_type} resources")
        
        return recommendations
    
    def _extract_metric_value(self, metric_data: Any) -> float:
        """Extract numerical value from metric data"""
        if isinstance(metric_data, dict):
            return metric_data.get("utilization", 0.0)
        elif isinstance(metric_data, (int, float)):
            return float(metric_data)
        else:
            return 0.0
    
    def _calculate_alert_severity(self, value: float, threshold: float) -> str:
        """Calculate alert severity based on threshold breach"""
        breach_ratio = value / threshold
        
        if breach_ratio >= 1.5:
            return "critical"
        elif breach_ratio >= 1.2:
            return "high"
        elif breach_ratio >= 1.0:
            return "medium"
        else:
            return "low"
    
    async def _get_storage_usage(self) -> Dict[str, Any]:
        """Get metrics storage usage information"""
        total_points = sum(len(data) for data in self.metrics_storage.values())
        estimated_size_mb = total_points * 0.001  # Rough estimate
        
        return {
            "total_data_points": total_points,
            "estimated_size_mb": estimated_size_mb,
            "retention_days": self.config.retention_period
        }