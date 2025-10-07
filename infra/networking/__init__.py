# IA Chérie Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for IA Chérie platform
# Supports multi-cloud deployment and enterprise networking
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Networking Infrastructure Module

Enterprise networking infrastructure for IA Chérie platform.
Provides comprehensive network management, security, and optimization capabilities.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary"

# Network infrastructure components
from .load_balancer_manager import LoadBalancerManager
from .cdn_configuration import CDNConfiguration
from .dns_management import DNSManagement
from .network_topology_manager import NetworkTopologyManager
from .firewall_configuration import FirewallConfiguration
from .vpc_manager import VPCManager
from .subnet_configuration import SubnetConfiguration
from .security_group_manager import SecurityGroupManager
from .network_access_control import NetworkAccessControl
from .vpn_gateway_manager import VPNGatewayManager

__all__ = [
    # Network Management
    "LoadBalancerManager",
    "CDNConfiguration",
    "DNSManagement",
    "NetworkTopologyManager",
    "FirewallConfiguration",
    
    # Network Security
    "VPCManager",
    "SubnetConfiguration",
    "SecurityGroupManager",
    "NetworkAccessControl",
    "VPNGatewayManager",
]

# Network configuration constants
NETWORK_PROTOCOLS = [
    "TCP",
    "UDP",
    "ICMP",
    "HTTP",
    "HTTPS",
    "WebSocket"
]

LOAD_BALANCER_TYPES = {
    "application": "ALB",
    "network": "NLB",
    "classic": "CLB",
    "gateway": "GWLB"
}

def get_networking_info():
    """Get networking module information."""
    return {
        "version": __version__,
        "author": __author__,
        "protocols": NETWORK_PROTOCOLS,
        "load_balancer_types": LOAD_BALANCER_TYPES
    }
