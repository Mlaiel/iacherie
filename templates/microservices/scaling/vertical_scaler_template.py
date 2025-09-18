#!/usr/bin/env python3
"""Vertical Scaler Template - Dynamic vertical scaling (CPU/Memory)"""

from dataclasses import dataclass

@dataclass
class VerticalScalingConfig:
    min_cpu: str = "100m"
    max_cpu: str = "2000m"
    min_memory: str = "128Mi"
    max_memory: str = "2Gi"

class VerticalScalerTemplate:
    """Vertical scaling template for CPU and memory adjustment"""
    
    def __init__(self, service_name: str, config: VerticalScalingConfig):
        self.service_name = service_name
        self.config = config
        self.current_cpu = config.min_cpu
        self.current_memory = config.min_memory
    
    def scale_resources(self, cpu_target: str, memory_target: str) -> bool:
        """Scale CPU and memory resources"""
        self.current_cpu = cpu_target
        self.current_memory = memory_target
        print(f"Scaled {self.service_name} to CPU: {cpu_target}, Memory: {memory_target}")
        return True