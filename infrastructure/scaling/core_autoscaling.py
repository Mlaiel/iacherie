"""Autoscaling Infrastructure Management - Consolidated Module
============================================================
All autoscaling functionality consolidated into a single module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

class AutoscalingType(Enum):
    """Autoscaling types"""
    HORIZONTAL_POD = "horizontal_pod"
    VERTICAL_POD = "vertical_pod"
    CLUSTER = "cluster"

class MetricType(Enum):
    """Metric types for autoscaling"""
    CPU = "cpu"
    MEMORY = "memory"
    CUSTOM = "custom"
    EXTERNAL = "external"

@dataclass
class HPAConfig:
    """Horizontal Pod Autoscaler configuration"""
    name: str
    target_deployment: str
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_percentage: int = 70
    target_memory_percentage: Optional[int] = None

@dataclass
class VPAConfig:
    """Vertical Pod Autoscaler configuration"""
    name: str
    target_deployment: str
    update_mode: str = "Auto"  # Auto, Initial, Off
    resource_policy: Dict[str, Any] = field(default_factory=dict)

class AutoscalingManager:
    """Unified autoscaling management interface"""
    
    def __init__(self):
        self.hpa_manager = HPAManager()
        self.vpa_manager = VPAManager()
        self.cluster_autoscaler = ClusterAutoscaler()
        self.logger = logging.getLogger(__name__)

class HPAManager:
    """Horizontal Pod Autoscaler management"""
    
    def __init__(self):
        self.hpa_configs = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_hpa(self, config: HPAConfig) -> bool:
        """Create Horizontal Pod Autoscaler"""
        try:
            self.logger.info(f"Creating HPA: {config.name}")
            
            hpa_spec = {
                'apiVersion': 'autoscaling/v2',
                'kind': 'HorizontalPodAutoscaler',
                'metadata': {
                    'name': config.name
                },
                'spec': {
                    'scaleTargetRef': {
                        'apiVersion': 'apps/v1',
                        'kind': 'Deployment',
                        'name': config.target_deployment
                    },
                    'minReplicas': config.min_replicas,
                    'maxReplicas': config.max_replicas,
                    'metrics': []
                }
            }
            
            # Add CPU metric
            if config.target_cpu_percentage:
                hpa_spec['spec']['metrics'].append({
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': config.target_cpu_percentage
                        }
                    }
                })
            
            # Add memory metric
            if config.target_memory_percentage:
                hpa_spec['spec']['metrics'].append({
                    'type': 'Resource',
                    'resource': {
                        'name': 'memory',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': config.target_memory_percentage
                        }
                    }
                })
            
            self.hpa_configs[config.name] = hpa_spec
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create HPA: {e}")
            return False

class VPAManager:
    """Vertical Pod Autoscaler management"""
    
    def __init__(self):
        self.vpa_configs = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_vpa(self, config: VPAConfig) -> bool:
        """Create Vertical Pod Autoscaler"""
        try:
            self.logger.info(f"Creating VPA: {config.name}")
            
            vpa_spec = {
                'apiVersion': 'autoscaling.k8s.io/v1',
                'kind': 'VerticalPodAutoscaler',
                'metadata': {
                    'name': config.name
                },
                'spec': {
                    'targetRef': {
                        'apiVersion': 'apps/v1',
                        'kind': 'Deployment',
                        'name': config.target_deployment
                    },
                    'updatePolicy': {
                        'updateMode': config.update_mode
                    }
                }
            }
            
            if config.resource_policy:
                vpa_spec['spec']['resourcePolicy'] = config.resource_policy
            
            self.vpa_configs[config.name] = vpa_spec
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create VPA: {e}")
            return False

class ClusterAutoscaler:
    """Cluster autoscaler management"""
    
    def __init__(self):
        self.cluster_config = {}
        self.logger = logging.getLogger(__name__)
    
    async def configure_cluster_autoscaler(self, 
                                         min_nodes: int = 1,
                                         max_nodes: int = 10,
                                         node_groups: List[Dict[str, Any]] = None) -> bool:
        """Configure cluster autoscaler"""
        try:
            self.logger.info("Configuring cluster autoscaler")
            
            config = {
                'min_nodes': min_nodes,
                'max_nodes': max_nodes,
                'node_groups': node_groups or [],
                'scale_down_delay_after_add': '10m',
                'scale_down_unneeded_time': '10m',
                'scale_down_utilization_threshold': 0.5
            }
            
            self.cluster_config = config
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure cluster autoscaler: {e}")
            return False

# Global instances
autoscaling_manager = AutoscalingManager()
hpa_manager = HPAManager()
vpa_manager = VPAManager()
cluster_autoscaler = ClusterAutoscaler()

__all__ = [
    "AutoscalingManager",
    "HPAManager",
    "VPAManager", 
    "ClusterAutoscaler",
    "HPAConfig",
    "VPAConfig",
    "AutoscalingType",
    "MetricType",
    "autoscaling_manager",
    "hpa_manager",
    "vpa_manager",
    "cluster_autoscaler"
]