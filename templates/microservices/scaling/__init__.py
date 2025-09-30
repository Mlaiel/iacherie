#!/usr/bin/env python3
"""
📈 Scaling Templates - IA Chérie Microservices Enterprise

Auto-scaling and resource management templates for horizontal scaling,
vertical scaling, load balancing, and capacity planning.

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

from .horizontal_scaler_template import HorizontalScalerTemplate
from .vertical_scaler_template import VerticalScalerTemplate
from .auto_scaler_template import AutoScalerTemplate
from .load_balancer_template import LoadBalancerTemplate
from .cluster_manager_template import ClusterManagerTemplate
from .resource_manager_template import ResourceManagerTemplate
from .capacity_planner_template import CapacityPlannerTemplate
from .cost_optimizer_template import CostOptimizerTemplate

__all__ = [
    "HorizontalScalerTemplate",
    "VerticalScalerTemplate",
    "AutoScalerTemplate", 
    "LoadBalancerTemplate",
    "ClusterManagerTemplate",
    "ResourceManagerTemplate",
    "CapacityPlannerTemplate",
    "CostOptimizerTemplate"
]