#!/usr/bin/env python3
"""
📊 AI PERFORMANCE MONITORING
===========================

Real-time monitoring and analytics for AI operations.
"""

import time
import json
from typing import Dict, Any
from datetime import datetime, timedelta

class AIPerformanceMonitor:
    """Monitor AI system performance"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            "max_response_time": 10.0,  # seconds
            "min_success_rate": 0.95,   # 95%
            "max_cost_per_hour": 100.0  # dollars
        }
    
    def record_metric(self, metric: Dict[str, Any]) -> None:
        """Record a performance metric"""
        metric["timestamp"] = datetime.now().isoformat()
        self.metrics_history.append(metric)
        
        # Keep only last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 metrics
        
        total_tasks = len(recent_metrics)
        successful_tasks = sum(1 for m in recent_metrics if m.get("success", False))
        avg_response_time = sum(m.get("processing_time", 0) for m in recent_metrics) / total_tasks
        total_cost = sum(m.get("cost", 0) for m in recent_metrics)
        
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        # Check for alerts
        alerts = []
        if avg_response_time > self.alert_thresholds["max_response_time"]:
            alerts.append(f"High response time: {avg_response_time:.2f}s")
        if success_rate < self.alert_thresholds["min_success_rate"]:
            alerts.append(f"Low success rate: {success_rate:.1%}")
        
        return {
            "total_tasks": total_tasks,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "total_cost": total_cost,
            "alerts": alerts,
            "status": "healthy" if not alerts else "warning"
        }

# Global monitor instance
ai_monitor = AIPerformanceMonitor()
