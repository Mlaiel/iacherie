#!/usr/bin/env python3
"""Auto Scaler Template - Combined horizontal and vertical auto-scaling"""

class AutoScalerTemplate:
    """Combined auto-scaling template"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.enabled = True
    
    def enable_auto_scaling(self):
        """Enable auto-scaling"""
        self.enabled = True
        print(f"Auto-scaling enabled for {self.service_name}")
    
    def disable_auto_scaling(self):
        """Disable auto-scaling"""
        self.enabled = False
        print(f"Auto-scaling disabled for {self.service_name}")