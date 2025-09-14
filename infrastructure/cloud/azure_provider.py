"""
Microsoft Azure Infrastructure Provider
Enterprise-grade Azure infrastructure management for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from datetime import datetime, timedelta

try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.containerservice import ContainerServiceClient
    from azure.mgmt.sql import SqlManagementClient
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.network import NetworkManagementClient
    from azure.mgmt.monitor import MonitorManagementClient
    from azure.mgmt.keyvault import KeyVaultManagementClient
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning("Azure SDK not available. Running in simulation mode.")

logger = logging.getLogger(__name__)


class AzureRegion(Enum):
    """Azure regions for global deployment"""
    EAST_US = "eastus"
    EAST_US_2 = "eastus2"
    WEST_US_2 = "westus2"
    WEST_EUROPE = "westeurope"
    NORTH_EUROPE = "northeurope"
    SOUTHEAST_ASIA = "southeastasia"
    EAST_ASIA = "eastasia"
    UK_SOUTH = "uksouth"
    CENTRAL_US = "centralus"
    SOUTH_CENTRAL_US = "southcentralus"


class AzureVMSize(Enum):
    """Azure VM sizes optimized for different workloads"""
    STANDARD_B2S = "Standard_B2s"
    STANDARD_D4S_V3 = "Standard_D4s_v3"
    STANDARD_F8S_V2 = "Standard_F8s_v2"
    STANDARD_NC6 = "Standard_NC6"  # GPU
    STANDARD_NC12 = "Standard_NC12"  # GPU
    STANDARD_NV6 = "Standard_NV6"  # GPU


@dataclass
class AzureCredentials:
    """Azure authentication credentials"""
    subscription_id: str
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    resource_group: str = "ainflue-resources"
    location: str = AzureRegion.EAST_US.value


@dataclass
class AzureVMConfig:
    """Azure Virtual Machine configuration"""
    vm_name: str
    vm_size: str = AzureVMSize.STANDARD_D4S_V3.value
    location: str = AzureRegion.EAST_US.value
    admin_username: str = "azureuser"
    admin_password: Optional[str] = None
    ssh_public_key: Optional[str] = None
    os_disk_size: int = 128
    data_disk_size: Optional[int] = None
    network_security_group: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class AKSClusterConfig:
    """Azure Kubernetes Service cluster configuration"""
    cluster_name: str
    location: str = AzureRegion.EAST_US.value
    node_count: int = 3
    vm_size: str = AzureVMSize.STANDARD_D4S_V3.value
    disk_size_gb: int = 100
    kubernetes_version: Optional[str] = None
    enable_auto_scaling: bool = True
    min_count: int = 1
    max_count: int = 10
    enable_rbac: bool = True
    network_plugin: str = "azure"
    load_balancer_sku: str = "standard"


@dataclass
class AzureSQLConfig:
    """Azure SQL Database configuration"""
    server_name: str
    database_name: str
    location: str = AzureRegion.EAST_US.value
    admin_login: str = "ainflue_admin"
    admin_password: str = "ComplexP@ssw0rd!"
    sku_name: str = "S2"  # Standard S2
    max_size_bytes: int = 268435456000  # 250 GB
    backup_retention_days: int = 7
    geo_redundant_backup: bool = True


@dataclass
class AzureStorageConfig:
    """Azure Storage Account configuration"""
    storage_account_name: str
    location: str = AzureRegion.EAST_US.value
    account_tier: str = "Standard"
    replication_type: str = "LRS"  # Locally Redundant Storage
    access_tier: str = "Hot"
    enable_https_traffic: bool = True
    containers: List[str] = field(default_factory=list)


class AzureProvider:
    """
    Microsoft Azure infrastructure provider
    
    Provides enterprise-grade Azure infrastructure management for:
    - Virtual Machines and Scale Sets
    - Azure Kubernetes Service (AKS) clusters
    - Azure SQL Database
    - Azure Storage Accounts and Blob Storage
    - Azure Cognitive Services for AI workloads
    - Azure Monitor for observability
    - Azure Key Vault for secrets management
    - Azure Virtual Networks and security groups
    """
    
    def __init__(self, credentials -> None: AzureCredentials) -> None:
        """Initialize Azure provider with credentials"""
        self.credentials = credentials
        self.subscription_id = credentials.subscription_id
        self.resource_group = credentials.resource_group
        self.location = credentials.location
        self.clients = {}
        self._initialize_clients()
        
        # Ainflue-specific configurations
        self.creator_services = {
            "content_processing": {
                "vm_size": AzureVMSize.STANDARD_F8S_V2.value,
                "disk_size": 256,
                "gpu_enabled": False
            },
            "ai_analysis": {
                "vm_size": AzureVMSize.STANDARD_NC6.value,
                "disk_size": 512,
                "gpu_enabled": True
            },
            "streaming_infrastructure": {
                "vm_size": AzureVMSize.STANDARD_D4S_V3.value,
                "disk_size": 128,
                "network_optimized": True
            }
        }
        
    def _initialize_clients(self) -> None:
        """Initialize Azure service clients"""
        if not AZURE_AVAILABLE:
            logger.warning("Azure SDK not available. Using simulation mode.")
            return
            
        try:
            # Initialize credentials
            if self.credentials.client_id and self.credentials.client_secret:
                credential = ClientSecretCredential(
                    tenant_id=self.credentials.tenant_id,
                    client_id=self.credentials.client_id,
                    client_secret=self.credentials.client_secret
                )
            else:
                credential = DefaultAzureCredential()
                
            # Initialize management clients
            self.clients = {
                'resource': ResourceManagementClient(credential, self.subscription_id),
                'compute': ComputeManagementClient(credential, self.subscription_id),
                'container': ContainerServiceClient(credential, self.subscription_id),
                'sql': SqlManagementClient(credential, self.subscription_id),
                'storage': StorageManagementClient(credential, self.subscription_id),
                'network': NetworkManagementClient(credential, self.subscription_id),
                'monitor': MonitorManagementClient(credential, self.subscription_id),
                'keyvault': KeyVaultManagementClient(credential, self.subscription_id),
                'cognitive': CognitiveServicesManagementClient(credential, self.subscription_id),
                'credential': credential
            }
            
            # Ensure resource group exists
            self._ensure_resource_group()
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {e}")
            
    def _ensure_resource_group(self) -> None:
        """Ensure resource group exists"""
        try:
            self.clients['resource'].resource_groups.create_or_update(
                self.resource_group,
                {
                    'location': self.location,
                    'tags': {
                        'platform': 'ainflue',
                        'created_by': 'azure_provider',
                        'environment': 'production'
                    }
                }
            )
        except Exception as e:
            logger.error(f"Failed to create resource group: {e}")
            
    async def create_virtual_machine(self, config: AzureVMConfig) -> Dict[str, Any]:
        """Create an Azure Virtual Machine"""
        if not AZURE_AVAILABLE:
            return self._simulate_vm_creation(config)
            
        try:
            # Create network interface
            nic_name = f"{config.vm_name}-nic"
            nic_result = await self._create_network_interface(nic_name, config.location)
            
            # VM configuration for Ainflue content processing
            vm_parameters = {
                'location': config.location,
                'os_profile': {
                    'computer_name': config.vm_name,
                    'admin_username': config.admin_username,
                    'admin_password': config.admin_password,
                    'linux_configuration': {
                        'disable_password_authentication': bool(config.ssh_public_key),
                        'ssh': {
                            'public_keys': [{
                                'path': f'/home/{config.admin_username}/.ssh/authorized_keys',
                                'key_data': config.ssh_public_key
                            }]
                        } if config.ssh_public_key else None
                    }
                },
                'hardware_profile': {
                    'vm_size': config.vm_size
                },
                'storage_profile': {
                    'image_reference': {
                        'publisher': 'Canonical',
                        'offer': 'UbuntuServer',
                        'sku': '18.04-LTS',
                        'version': 'latest'
                    },
                    'os_disk': {
                        'name': f"{config.vm_name}-os-disk",
                        'caching': 'ReadWrite',
                        'create_option': 'FromImage',
                        'disk_size_gb': config.os_disk_size,
                        'managed_disk': {
                            'storage_account_type': 'Premium_LRS'
                        }
                    }
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': nic_result['id']
                    }]
                },
                'tags': {
                    'platform': 'ainflue',
                    'content-processing': 'enabled',
                    'creator-services': 'true',
                    **config.tags
                }
            }
            
            # Add data disk if specified
            if config.data_disk_size:
                vm_parameters['storage_profile']['data_disks'] = [{
                    'disk_size_gb': config.data_disk_size,
                    'lun': 0,
                    'create_option': 'Empty',
                    'caching': 'ReadWrite',
                    'managed_disk': {
                        'storage_account_type': 'Premium_LRS'
                    }
                }]
                
            # Create VM
            operation = self.clients['compute'].virtual_machines.begin_create_or_update(
                self.resource_group,
                config.vm_name,
                vm_parameters
            )
            
            # Install Ainflue software via custom script extension
            await self._install_ainflue_extensions(config.vm_name, config.location)
            
            return {
                'vm_name': config.vm_name,
                'operation_id': operation.result().name if hasattr(operation, 'result') else 'pending',
                'status': 'creating',
                'location': config.location,
                'vm_size': config.vm_size,
                'resource_group': self.resource_group,
                'tags': config.tags
            }
            
        except Exception as e:
            logger.error(f"Failed to create Azure VM {config.vm_name}: {e}")
            raise
            
    async def create_aks_cluster(self, config: AKSClusterConfig) -> Dict[str, Any]:
        """Create an Azure Kubernetes Service cluster"""
        if not AZURE_AVAILABLE:
            return self._simulate_aks_creation(config)
            
        try:
            # AKS cluster optimized for Ainflue creator workloads
            cluster_parameters = {
                'location': config.location,
                'dns_prefix': f"{config.cluster_name}-dns",
                'kubernetes_version': config.kubernetes_version,
                'enable_rbac': config.enable_rbac,
                'network_profile': {
                    'network_plugin': config.network_plugin,
                    'load_balancer_sku': config.load_balancer_sku,
                    'outbound_type': 'loadBalancer'
                },
                'agent_pool_profiles': [{
                    'name': 'nodepool1',
                    'count': config.node_count,
                    'vm_size': config.vm_size,
                    'os_disk_size_gb': config.disk_size_gb,
                    'os_type': 'Linux',
                    'mode': 'System',
                    'enable_auto_scaling': config.enable_auto_scaling,
                    'min_count': config.min_count if config.enable_auto_scaling else None,
                    'max_count': config.max_count if config.enable_auto_scaling else None,
                    'availability_zones': ['1', '2', '3'],
                    'enable_node_public_ip': False,
                    'tags': {
                        'platform': 'ainflue',
                        'content-processing': 'enabled',
                        'creator-services': 'true'
                    }
                }],
                'service_principal_profile': {
                    'client_id': 'msi'  # Use managed identity
                },
                'addon_profiles': {
                    'monitoring': {'enabled': True},
                    'azure_policy': {'enabled': True},
                    'ingress_application_gateway': {'enabled': False},
                    'oms_agent': {
                        'enabled': True,
                        'config': {
                            'log_analytics_workspace_resource_id': await self._get_log_analytics_workspace()
                        }
                    }
                },
                'auto_scaler_profile': {
                    'scan_interval': '10s',
                    'scale_down_delay_after_add': '10m',
                    'scale_down_delay_after_delete': '10s',
                    'scale_down_delay_after_failure': '3m',
                    'scale_down_unneeded_time': '10m',
                    'scale_down_utilization_threshold': '0.5'
                } if config.enable_auto_scaling else None,
                'tags': {
                    'platform': 'ainflue',
                    'cluster-type': 'creator-workloads',
                    'auto-scaling': str(config.enable_auto_scaling).lower()
                }
            }
            
            operation = self.clients['container'].managed_clusters.begin_create_or_update(
                self.resource_group,
                config.cluster_name,
                cluster_parameters
            )
            
            return {
                'cluster_name': config.cluster_name,
                'operation_id': operation.result().name if hasattr(operation, 'result') else 'pending',
                'status': 'creating',
                'location': config.location,
                'node_count': config.node_count,
                'vm_size': config.vm_size,
                'kubernetes_version': config.kubernetes_version,
                'auto_scaling': config.enable_auto_scaling,
                'resource_group': self.resource_group
            }
            
        except Exception as e:
            logger.error(f"Failed to create AKS cluster {config.cluster_name}: {e}")
            raise
            
    async def create_sql_database(self, config: AzureSQLConfig) -> Dict[str, Any]:
        """Create Azure SQL Database"""
        if not AZURE_AVAILABLE:
            return self._simulate_sql_creation(config)
            
        try:
            # Create SQL Server first
            server_parameters = {
                'location': config.location,
                'administrator_login': config.admin_login,
                'administrator_login_password': config.admin_password,
                'version': '12.0',
                'public_network_access': 'Enabled',
                'minimal_tls_version': '1.2',
                'tags': {
                    'platform': 'ainflue',
                    'database-type': 'creator-data',
                    'environment': 'production'
                }
            }
            
            server_operation = self.clients['sql'].servers.begin_create_or_update(
                self.resource_group,
                config.server_name,
                server_parameters
            )
            
            # Database configuration for Ainflue creator data
            database_parameters = {
                'location': config.location,
                'sku': {
                    'name': config.sku_name,
                    'tier': 'Standard'
                },
                'max_size_bytes': config.max_size_bytes,
                'collation': 'SQL_Latin1_General_CP1_CI_AS',
                'backup_retention_days': config.backup_retention_days,
                'geo_redundant_backup_enabled': config.geo_redundant_backup,
                'storage_account_type': 'GRS' if config.geo_redundant_backup else 'LRS',
                'tags': {
                    'platform': 'ainflue',
                    'data-type': 'creator-profiles',
                    'backup-policy': 'daily'
                }
            }
            
            # Wait for server creation
            server_result = server_operation.result()
            
            # Create database
            database_operation = self.clients['sql'].databases.begin_create_or_update(
                self.resource_group,
                config.server_name,
                config.database_name,
                database_parameters
            )
            
            # Configure firewall rules for secure access
            await self._configure_sql_firewall(config.server_name)
            
            return {
                'server_name': config.server_name,
                'database_name': config.database_name,
                'operation_id': database_operation.result().name if hasattr(database_operation, 'result') else 'pending',
                'status': 'creating',
                'location': config.location,
                'sku': config.sku_name,
                'max_size_gb': config.max_size_bytes // (1024**3),
                'backup_retention_days': config.backup_retention_days,
                'resource_group': self.resource_group
            }
            
        except Exception as e:
            logger.error(f"Failed to create Azure SQL database {config.database_name}: {e}")
            raise
            
    async def create_storage_account(self, config: AzureStorageConfig) -> Dict[str, Any]:
        """Create Azure Storage Account"""
        if not AZURE_AVAILABLE:
            return self._simulate_storage_creation(config)
            
        try:
            # Storage account configuration for Ainflue creator content
            storage_parameters = {
                'sku': {
                    'name': f"{config.account_tier}_{config.replication_type}"
                },
                'kind': 'StorageV2',
                'location': config.location,
                'access_tier': config.access_tier,
                'enable_https_traffic_only': config.enable_https_traffic,
                'allow_blob_public_access': False,  # Security best practice
                'minimum_tls_version': 'TLS1_2',
                'network_rule_set': {
                    'default_action': 'Allow',  # Configure as needed
                    'bypass': 'AzureServices'
                },
                'encryption': {
                    'services': {
                        'blob': {'enabled': True},
                        'file': {'enabled': True}
                    },
                    'key_source': 'Microsoft.Storage'
                },
                'tags': {
                    'platform': 'ainflue',
                    'content-type': 'creator-uploads',
                    'tier': config.access_tier.lower()
                }
            }
            
            operation = self.clients['storage'].storage_accounts.begin_create(
                self.resource_group,
                config.storage_account_name,
                storage_parameters
            )
            
            # Wait for storage account creation
            storage_result = operation.result()
            
            # Create blob containers
            if config.containers:
                await self._create_blob_containers(config.storage_account_name, config.containers)
                
            # Get storage account keys
            keys = self.clients['storage'].storage_accounts.list_keys(
                self.resource_group,
                config.storage_account_name
            )
            
            return {
                'storage_account_name': config.storage_account_name,
                'operation_id': storage_result.name,
                'status': 'created',
                'location': config.location,
                'account_tier': config.account_tier,
                'replication_type': config.replication_type,
                'access_tier': config.access_tier,
                'containers': config.containers,
                'primary_key': keys.keys[0].value if keys.keys else None,
                'resource_group': self.resource_group
            }
            
        except Exception as e:
            logger.error(f"Failed to create storage account {config.storage_account_name}: {e}")
            raise
            
    async def setup_cognitive_services(self, location: str = None) -> Dict[str, Any]:
        """Setup Azure Cognitive Services for AI workloads"""
        if not AZURE_AVAILABLE:
            return self._simulate_cognitive_services_setup(location or self.location)
            
        try:
            location = location or self.location
            
            # Cognitive Services configuration for Ainflue AI features
            services_config = {
                'computer_vision': {
                    'name': f'ainflue-vision-{self.subscription_id[:8]}',
                    'kind': 'ComputerVision',
                    'sku': 'S1',
                    'description': 'Content analysis and moderation'
                },
                'text_analytics': {
                    'name': f'ainflue-text-{self.subscription_id[:8]}',
                    'kind': 'TextAnalytics',
                    'sku': 'S',
                    'description': 'Sentiment analysis and content insights'
                },
                'speech_services': {
                    'name': f'ainflue-speech-{self.subscription_id[:8]}',
                    'kind': 'SpeechServices',
                    'sku': 'S0',
                    'description': 'Audio content processing'
                },
                'content_moderator': {
                    'name': f'ainflue-moderator-{self.subscription_id[:8]}',
                    'kind': 'ContentModerator',
                    'sku': 'S0',
                    'description': 'Content safety and compliance'
                }
            }
            
            created_services = {}
            
            for service_type, config in services_config.items():
                parameters = {
                    'location': location,
                    'sku': {'name': config['sku']},
                    'kind': config['kind'],
                    'properties': {
                        'custom_sub_domain_name': config['name']
                    },
                    'tags': {
                        'platform': 'ainflue',
                        'service-type': service_type,
                        'ai-workload': 'true'
                    }
                }
                
                operation = self.clients['cognitive'].accounts.begin_create(
                    self.resource_group,
                    config['name'],
                    parameters
                )
                
                result = operation.result()
                
                # Get service keys
                keys = self.clients['cognitive'].accounts.list_keys(
                    self.resource_group,
                    config['name']
                )
                
                created_services[service_type] = {
                    'name': config['name'],
                    'endpoint': result.properties.endpoint,
                    'key': keys.key1,
                    'sku': config['sku'],
                    'description': config['description']
                }
                
            return {
                'status': 'created',
                'location': location,
                'services': created_services,
                'count': len(created_services)
            }
            
        except Exception as e:
            logger.error(f"Failed to setup Cognitive Services: {e}")
            raise
            
    async def _create_network_interface(self, nic_name: str, location: str) -> Dict[str, Any]:
        """Create network interface for VM"""
        try:
            # Create virtual network first
            vnet_name = f"ainflue-vnet"
            vnet_params = {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                },
                'subnets': [{
                    'name': 'default',
                    'address_prefix': '10.0.0.0/24'
                }],
                'tags': {
                    'platform': 'ainflue',
                    'network-type': 'creator-services'
                }
            }
            
            vnet_operation = self.clients['network'].virtual_networks.begin_create_or_update(
                self.resource_group,
                vnet_name,
                vnet_params
            )
            vnet_result = vnet_operation.result()
            
            # Create public IP
            public_ip_name = f"{nic_name}-ip"
            public_ip_params = {
                'location': location,
                'public_ip_allocation_method': 'Dynamic',
                'tags': {
                    'platform': 'ainflue'
                }
            }
            
            public_ip_operation = self.clients['network'].public_ip_addresses.begin_create_or_update(
                self.resource_group,
                public_ip_name,
                public_ip_params
            )
            public_ip_result = public_ip_operation.result()
            
            # Create network interface
            nic_params = {
                'location': location,
                'ip_configurations': [{
                    'name': 'ipconfig1',
                    'subnet': {
                        'id': vnet_result.subnets[0].id
                    },
                    'public_ip_address': {
                        'id': public_ip_result.id
                    }
                }],
                'tags': {
                    'platform': 'ainflue'
                }
            }
            
            nic_operation = self.clients['network'].network_interfaces.begin_create_or_update(
                self.resource_group,
                nic_name,
                nic_params
            )
            nic_result = nic_operation.result()
            
            return {
                'id': nic_result.id,
                'name': nic_name,
                'vnet_name': vnet_name,
                'public_ip_name': public_ip_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create network interface {nic_name}: {e}")
            raise
            
    async def _install_ainflue_extensions(self, vm_name -> None: str, location -> None: str) -> None:
        """Install Ainflue software via VM extensions"""
        try:
            extension_params = {
                'location': location,
                'publisher': 'Microsoft.Azure.Extensions',
                'type_handler_version': '2.0',
                'virtual_machine_extension_type': 'CustomScript',
                'settings': {
                    'commandToExecute': self._get_ainflue_install_script()
                },
                'tags': {
                    'platform': 'ainflue',
                    'extension-type': 'creator-setup'
                }
            }
            
            operation = self.clients['compute'].virtual_machine_extensions.begin_create_or_update(
                self.resource_group,
                vm_name,
                'ainflue-setup',
                extension_params
            )
            
            return operation.result()
            
        except Exception as e:
            logger.error(f"Failed to install Ainflue extensions on {vm_name}: {e}")
            
    def _get_ainflue_install_script(self) -> str:
        """Get Ainflue installation script"""
        return """#!/bin/bash
        
        # Ainflue Creator Platform Setup
        apt-get update
        apt-get install -y docker.io nginx python3-pip ffmpeg
        
        # Install creator content processing tools
        pip3 install tensorflow opencv-python pillow ffmpeg-python azure-storage-blob
        
        # Configure for creator uploads
        mkdir -p /opt/ainflue/{uploads,processing,cache,logs}
        chown -R www-data:www-data /opt/ainflue
        
        # Setup Azure monitoring agent
        wget https://aka.ms/downloadazcopy-v10-linux -O azcopy.tar.gz
        tar -xzf azcopy.tar.gz
        cp azcopy_linux_amd64_*/azcopy /usr/local/bin/
        
        # Start services
        systemctl enable docker nginx
        systemctl start docker nginx
        
        # Creator platform ready
        echo "Ainflue creator processing node ready - $(date)" > /opt/ainflue/status
        """
        
    async def _get_log_analytics_workspace(self) -> str:
        """Get or create Log Analytics workspace"""
        # This would create/get a Log Analytics workspace
        # For now, return a placeholder
        return f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.OperationalInsights/workspaces/ainflue-logs"
        
    async def _configure_sql_firewall(self, server_name -> None: str) -> None:
        """Configure SQL Server firewall rules"""
        try:
            # Allow Azure services
            firewall_params = {
                'start_ip_address': '0.0.0.0',
                'end_ip_address': '0.0.0.0'
            }
            
            self.clients['sql'].firewall_rules.create_or_update(
                self.resource_group,
                server_name,
                'AllowAzureServices',
                firewall_params
            )
            
        except Exception as e:
            logger.error(f"Failed to configure SQL firewall: {e}")
            
    async def _create_blob_containers(self, storage_account_name -> None: str, containers -> None: List[str]) -> None:
        """Create blob containers in storage account"""
        try:
            # Get storage account key
            keys = self.clients['storage'].storage_accounts.list_keys(
                self.resource_group,
                storage_account_name
            )
            
            if keys.keys:
                # Create blob service client
                blob_service = BlobServiceClient(
                    account_url=f"https://{storage_account_name}.blob.core.windows.net",
                    credential=keys.keys[0].value
                )
                
                for container_name in containers:
                    blob_service.create_container(
                        container_name,
                        public_access='none'  # Private containers
                    )
                    
        except Exception as e:
            logger.error(f"Failed to create blob containers: {e}")
            
    def _simulate_vm_creation(self, config: AzureVMConfig) -> Dict[str, Any]:
        """Simulate VM creation"""
        return {
            'vm_name': config.vm_name,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'location': config.location,
            'vm_size': config.vm_size,
            'simulation': True
        }
        
    def _simulate_aks_creation(self, config: AKSClusterConfig) -> Dict[str, Any]:
        """Simulate AKS cluster creation"""
        return {
            'cluster_name': config.cluster_name,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'location': config.location,
            'node_count': config.node_count,
            'simulation': True
        }
        
    def _simulate_sql_creation(self, config: AzureSQLConfig) -> Dict[str, Any]:
        """Simulate SQL database creation"""
        return {
            'server_name': config.server_name,
            'database_name': config.database_name,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'location': config.location,
            'simulation': True
        }
        
    def _simulate_storage_creation(self, config: AzureStorageConfig) -> Dict[str, Any]:
        """Simulate storage account creation"""
        return {
            'storage_account_name': config.storage_account_name,
            'operation_id': f"simulation-{datetime.now().isoformat()}",
            'status': 'simulated',
            'location': config.location,
            'simulation': True
        }
        
    def _simulate_cognitive_services_setup(self, location: str) -> Dict[str, Any]:
        """Simulate Cognitive Services setup"""
        return {
            'status': 'simulated',
            'location': location,
            'services': {
                'computer_vision': {'status': 'simulated'},
                'text_analytics': {'status': 'simulated'},
                'speech_services': {'status': 'simulated'},
                'content_moderator': {'status': 'simulated'}
            },
            'simulation': True
        }
        
    async def get_resource_status(self, resource_type: str, resource_name: str) -> Dict[str, Any]:
        """Get status of Azure resource"""
        if not AZURE_AVAILABLE:
            return {'status': 'simulation_mode', 'resource': resource_name}
            
        try:
            if resource_type == 'vm':
                vm = self.clients['compute'].virtual_machines.get(
                    self.resource_group, resource_name
                )
                return {
                    'resource_type': 'vm',
                    'name': resource_name,
                    'status': vm.provisioning_state,
                    'location': vm.location,
                    'vm_size': vm.hardware_profile.vm_size,
                    'created': vm.time_created
                }
                
            elif resource_type == 'aks':
                cluster = self.clients['container'].managed_clusters.get(
                    self.resource_group, resource_name
                )
                return {
                    'resource_type': 'aks',
                    'name': resource_name,
                    'status': cluster.provisioning_state,
                    'location': cluster.location,
                    'kubernetes_version': cluster.kubernetes_version,
                    'node_count': cluster.agent_pool_profiles[0].count if cluster.agent_pool_profiles else 0
                }
                
            elif resource_type == 'sql':
                database = self.clients['sql'].databases.get(
                    self.resource_group, resource_name.split('/')[0], resource_name.split('/')[1]
                )
                return {
                    'resource_type': 'sql',
                    'name': resource_name,
                    'status': database.status,
                    'location': database.location,
                    'sku': database.sku.name,
                    'max_size_bytes': database.max_size_bytes
                }
                
            return {'status': 'not_found', 'resource': resource_name}
            
        except Exception as e:
            logger.error(f"Failed to get status for {resource_type}/{resource_name}: {e}")
            return {'status': 'error', 'error': str(e)}
            
    def get_ainflue_optimized_configs(self) -> Dict[str, Any]:
        """Get Ainflue-optimized Azure configurations"""
        return {
            'content_processing': {
                'vm': AzureVMConfig(
                    vm_name="ainflue-content-processor",
                    vm_size=AzureVMSize.STANDARD_F8S_V2.value,
                    os_disk_size=256,
                    data_disk_size=512,
                    tags={'service': 'content-processing', 'platform': 'ainflue'}
                ),
                'storage': AzureStorageConfig(
                    storage_account_name=f"ainfluestg{self.subscription_id[:8]}",
                    account_tier="Premium",
                    access_tier="Hot",
                    containers=['uploads', 'processed', 'thumbnails']
                )
            },
            'ai_processing': {
                'vm': AzureVMConfig(
                    vm_name="ainflue-ai-processor",
                    vm_size=AzureVMSize.STANDARD_NC6.value,
                    os_disk_size=128,
                    data_disk_size=1024,
                    tags={'service': 'ai-processing', 'platform': 'ainflue'}
                ),
                'aks': AKSClusterConfig(
                    cluster_name="ainflue-ai-cluster",
                    vm_size=AzureVMSize.STANDARD_NC6.value,
                    node_count=3,
                    enable_auto_scaling=True,
                    max_count=20
                )
            },
            'database': {
                'sql': AzureSQLConfig(
                    server_name=f"ainflue-sql-{self.subscription_id[:8]}",
                    database_name="ainflue_creators",
                    sku_name="S4",
                    max_size_bytes=536870912000,  # 500 GB
                    backup_retention_days=30,
                    geo_redundant_backup=True
                )
            }
        }