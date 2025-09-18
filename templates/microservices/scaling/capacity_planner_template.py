#!/usr/bin/env python3
"""Capacity Planner Template - Capacity planning and forecasting"""

from typing import List
import statistics

class CapacityPlannerTemplate:
    """Capacity planning template"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.usage_history: List[float] = []
    
    def add_usage_data(self, usage_percent: float):
        """Add usage data point"""
        self.usage_history.append(usage_percent)
        # Keep only last 100 data points
        if len(self.usage_history) > 100:
            self.usage_history.pop(0)
    
    def predict_capacity_needs(self) -> dict:
        """Predict future capacity needs"""
        if not self.usage_history:
            return {"recommendation": "insufficient_data"}
        
        avg_usage = statistics.mean(self.usage_history)
        max_usage = max(self.usage_history)
        
        if avg_usage > 80:
            recommendation = "scale_up"
        elif avg_usage < 30:
            recommendation = "scale_down"
        else:
            recommendation = "maintain"
        
        return {
            "service": self.service_name,
            "avg_usage": avg_usage,
            "max_usage": max_usage,
            "recommendation": recommendation
        }