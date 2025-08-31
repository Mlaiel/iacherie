"""
Azure Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional Microsoft Azure cloud infrastructure configuration
for enterprise-grade AI-powered content protection and monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class AzureResourceConfig:
    """Azure resource configuration"""
    resource_type: str
    name: str
    location: str
    tags: Dict[str, str] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)


class AzureConfig:
    """
    Professional Azure cloud configuration manager for IA-Influencer Agent Platform.
    
    Provides enterprise-grade Azure services integration:
    - AKS clusters for Kubernetes orchestration
    - Azure Database for PostgreSQL and Redis Cache
    - Azure Storage accounts for content and AI models
    - Container Instances for microservices
    - Azure Functions for serverless AI processing
    - API Management for external integrations
    - CDN for global content delivery
    - Cognitive Services for content analysis
    - Azure Monitor for comprehensive observability
    - Key Vault for secrets management
    """
    
    def __init__(self, environment: str = "development", location: str = "East US"):
        self.environment = environment
        self.location = location
        self.project_name = "ia-influencer-agent"
        self.resource_group_name = f"{self.project_name}-rg-{environment}"
        self.subscription_id = "00000000-0000-0000-0000-000000000000"  # Placeholder
        
        # Common tags
        self.default_tags = {
            "Project": "IA-Influencer-Agent",
            "Environment": environment,
            "Owner": "Fahed Mlaiel",
            "Email": "mlaiel@live.de",
            "ManagedBy": "Terraform",
            "CostCenter": "IA-Platform",
            "Compliance": "GDPR-CCPA"
        }
    
    def get_resource_group_configuration(self) -> Dict[str, Any]:
        """Generate resource group configuration"""



        return {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                "environment": {
                    "type": "string",
                    "defaultValue": self.environment,
                    "metadata": {
                        "description": "Environment name"
                    }
                },
                "location": {
                    "type": "string",
                    "defaultValue": self.location,
                    "metadata": {
                        "description": "Azure region"
                    }
                }
            },
            "variables": {
                "projectName": self.project_name,
                "resourceGroupName": self.resource_group_name
            },
            "resources": [
                {
                    "type": "Microsoft.Resources/resourceGroups",
                    "apiVersion": "2021-04-01",
                    "name": "[variables('resourceGroupName')]",
                    "location": "[parameters('location')]",
                    "tags": self.default_tags,
                    "properties": {}
                }
            ]
        }
    
    def get_virtual_network_configuration(self) -> Dict[str, Any]:
        """Generate virtual network configuration"""



        return {
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2023-05-01",
            "name": f"{self.project_name}-vnet-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "addressSpace": {
                    "addressPrefixes": ["10.0.0.0/16"]
                },
                "subnets": [
                    {
                        "name": "aks-subnet",
                        "properties": {
                            "addressPrefix": "10.0.1.0/24",
                            "networkSecurityGroup": {
                                "id": "[resourceId('Microsoft.Network/networkSecurityGroups', 'aks-nsg')]"
                            }
                        }
                    },
                    {
                        "name": "database-subnet",
                        "properties": {
                            "addressPrefix": "10.0.2.0/24",
                            "networkSecurityGroup": {
                                "id": "[resourceId('Microsoft.Network/networkSecurityGroups', 'database-nsg')]"
                            }
                        }
                    },
                    {
                        "name": "storage-subnet",
                        "properties": {
                            "addressPrefix": "10.0.3.0/24",
                            "networkSecurityGroup": {
                                "id": "[resourceId('Microsoft.Network/networkSecurityGroups', 'storage-nsg')]"
                            }
                        }
                    },
                    {
                        "name": "functions-subnet",
                        "properties": {
                            "addressPrefix": "10.0.4.0/24",
                            "delegations": [
                                {
                                    "name": "Microsoft.Web.serverFarms",
                                    "properties": {
                                        "serviceName": "Microsoft.Web/serverFarms"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def get_network_security_groups_configuration(self) -> List[Dict[str, Any]]:
        """Generate network security groups configuration"""
        security_groups = []
        
        # AKS Security Group
        aks_nsg = {
            "type": "Microsoft.Network/networkSecurityGroups",
            "apiVersion": "2023-05-01",
            "name": "aks-nsg",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "securityRules": [
                    {
                        "name": "AllowHTTPS",
                        "properties": {
                            "protocol": "Tcp",
                            "sourcePortRange": "*",
                            "destinationPortRange": "443",
                            "sourceAddressPrefix": "*",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 100,
                            "direction": "Inbound"
                        }
                    },
                    {
                        "name": "AllowHTTP",
                        "properties": {
                            "protocol": "Tcp",
                            "sourcePortRange": "*",
                            "destinationPortRange": "80",
                            "sourceAddressPrefix": "*",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 110,
                            "direction": "Inbound"
                        }
                    },
                    {
                        "name": "AllowKubelet",
                        "properties": {
                            "protocol": "Tcp",
                            "sourcePortRange": "*",
                            "destinationPortRange": "10250",
                            "sourceAddressPrefix": "10.0.0.0/16",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 120,
                            "direction": "Inbound"
                        }
                    }
                ]
            }
        }
        security_groups.append(aks_nsg)
        
        # Database Security Group
        db_nsg = {
            "type": "Microsoft.Network/networkSecurityGroups",
            "apiVersion": "2023-05-01",
            "name": "database-nsg",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "securityRules": [
                    {
                        "name": "AllowPostgreSQL",
                        "properties": {
                            "protocol": "Tcp",
                            "sourcePortRange": "*",
                            "destinationPortRange": "5432",
                            "sourceAddressPrefix": "10.0.1.0/24",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 100,
                            "direction": "Inbound"
                        }
                    },
                    {
                        "name": "AllowRedis",
                        "properties": {
                            "protocol": "Tcp",
                            "sourcePortRange": "*",
                            "destinationPortRange": "6379",
                            "sourceAddressPrefix": "10.0.1.0/24",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 110,
                            "direction": "Inbound"
                        }
                    }
                ]
            }
        }
        security_groups.append(db_nsg)
        
        # Storage Security Group
        storage_nsg = {
            "type": "Microsoft.Network/networkSecurityGroups",
            "apiVersion": "2023-05-01",
            "name": "storage-nsg",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "securityRules": [
                    {
                        "name": "AllowStorageHTTPS",
                        "properties": {
                            "protocol": "Tcp",
                            "sourcePortRange": "*",
                            "destinationPortRange": "443",
                            "sourceAddressPrefix": "10.0.0.0/16",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 100,
                            "direction": "Inbound"
                        }
                    }
                ]
            }
        }
        security_groups.append(storage_nsg)
        
        return security_groups
    
    def get_aks_configuration(self) -> Dict[str, Any]:
        """Generate AKS cluster configuration"""



        return {
            "type": "Microsoft.ContainerService/managedClusters",
            "apiVersion": "2023-10-01",
            "name": f"{self.project_name}-aks-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "identity": {
                "type": "SystemAssigned"
            },
            "properties": {
                "kubernetesVersion": "1.28.3",
                "dnsPrefix": f"{self.project_name}-{self.environment}",
                "agentPoolProfiles": [
                    {
                        "name": "systempool",
                        "count": 1 if self.environment == "development" else 3,
                        "vmSize": "Standard_DS2_v2" if self.environment == "development" else "Standard_DS3_v2",
                        "osType": "Linux",
                        "mode": "System",
                        "enableAutoScaling": True,
                        "minCount": 1,
                        "maxCount": 3 if self.environment == "development" else 10,
                        "vnetSubnetID": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'aks-subnet')]",
                        "tags": {
                            "NodePool": "System",
                            **self.default_tags
                        }
                    },
                    {
                        "name": "workerpool",
                        "count": 2 if self.environment == "development" else 6,
                        "vmSize": "Standard_DS3_v2" if self.environment == "development" else "Standard_DS4_v2",
                        "osType": "Linux",
                        "mode": "User",
                        "enableAutoScaling": True,
                        "minCount": 1 if self.environment == "development" else 3,
                        "maxCount": 5 if self.environment == "development" else 20,
                        "vnetSubnetID": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'aks-subnet')]",
                        "tags": {
                            "NodePool": "Worker",
                            **self.default_tags
                        }
                    },
                    {
                        "name": "gpupool",
                        "count": 0 if self.environment == "development" else 1,
                        "vmSize": "Standard_NC6s_v3",
                        "osType": "Linux",
                        "mode": "User",
                        "enableAutoScaling": True,
                        "minCount": 0,
                        "maxCount": 2 if self.environment == "development" else 5,
                        "vnetSubnetID": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'aks-subnet')]",
                        "nodeTaints": ["nvidia.com/gpu=true:NoSchedule"],
                        "tags": {
                            "NodePool": "GPU",
                            "AcceleratedNetworking": "true",
                            **self.default_tags
                        }
                    }
                ],
                "networkProfile": {
                    "networkPlugin": "azure",
                    "serviceCidr": "10.1.0.0/16",
                    "dnsServiceIP": "10.1.0.10",
                    "outboundType": "loadBalancer"
                },
                "addonProfiles": {
                    "azureKeyvaultSecretsProvider": {
                        "enabled": True,
                        "config": {
                            "enableSecretRotation": "true"
                        }
                    },
                    "azurepolicy": {
                        "enabled": True
                    },
                    "omsagent": {
                        "enabled": True,
                        "config": {
                            "logAnalyticsWorkspaceResourceID": "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]"
                        }
                    }
                },
                "autoUpgradeProfile": {
                    "upgradeChannel": "stable"
                },
                "enableRBAC": True,
                "aadProfile": {
                    "managed": True,
                    "enableAzureRBAC": True
                }
            }
        }
    
    def get_postgresql_configuration(self) -> Dict[str, Any]:
        """Generate Azure Database for PostgreSQL configuration"""



        return {
            "type": "Microsoft.DBforPostgreSQL/flexibleServers",
            "apiVersion": "2022-12-01",
            "name": f"{self.project_name}-postgres-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "sku": {
                "name": "Standard_B1ms" if self.environment == "development" else "Standard_D2s_v3",
                "tier": "Burstable" if self.environment == "development" else "GeneralPurpose"
            },
            "properties": {
                "version": "15",
                "administratorLogin": "ia_admin",
                "administratorLoginPassword": "[parameters('postgresPassword')]",
                "storage": {
                    "storageSizeGB": 32 if self.environment == "development" else 128
                },
                "backup": {
                    "backupRetentionDays": 7,
                    "geoRedundantBackup": "Disabled" if self.environment == "development" else "Enabled"
                },
                "network": {
                    "delegatedSubnetResourceId": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'database-subnet')]",
                    "privateDnsZoneArmResourceId": "[resourceId('Microsoft.Network/privateDnsZones', 'ia-influencer.postgres.database.azure.com')]"
                },
                "highAvailability": {
                    "mode": "Disabled" if self.environment == "development" else "ZoneRedundant"
                },
                "maintenanceWindow": {
                    "customWindow": "Enabled",
                    "startHour": 3,
                    "startMinute": 0,
                    "dayOfWeek": 0
                }
            }
        }
    
    def get_redis_cache_configuration(self) -> Dict[str, Any]:
        """Generate Azure Cache for Redis configuration"""



        return {
            "type": "Microsoft.Cache/Redis",
            "apiVersion": "2023-08-01",
            "name": f"{self.project_name}-redis-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "sku": {
                    "name": "Basic" if self.environment == "development" else "Premium",
                    "family": "C" if self.environment == "development" else "P",
                    "capacity": 0 if self.environment == "development" else 1
                },
                "redisVersion": "6.0",
                "enableNonSslPort": False,
                "minimumTlsVersion": "1.2",
                "publicNetworkAccess": "Disabled",
                "redisConfiguration": {
                    "maxmemory-policy": "allkeys-lru"
                },
                "subnetId": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'database-subnet')]",
                "staticIP": "10.0.2.100"
            }
        }
    
    def get_storage_account_configuration(self) -> List[Dict[str, Any]]:
        """Generate Azure Storage Account configurations"""
        storage_accounts = []
        
        # Content Storage Account
        content_storage = {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2023-01-01",
            "name": f"{self.project_name.replace('-', '')}content{self.environment}",
            "location": "[parameters('location')]",
            "tags": {**self.default_tags, "Purpose": "Content Storage"},
            "sku": {
                "name": "Standard_LRS" if self.environment == "development" else "Standard_GRS"
            },
            "kind": "StorageV2",
            "properties": {
                "accessTier": "Hot",
                "allowBlobPublicAccess": False,
                "allowSharedKeyAccess": True,
                "encryption": {
                    "services": {
                        "blob": {"enabled": True},
                        "file": {"enabled": True}
                    },
                    "keySource": "Microsoft.Storage"
                },
                "minimumTlsVersion": "TLS1_2",
                "networkAcls": {
                    "defaultAction": "Deny",
                    "virtualNetworkRules": [
                        {
                            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'aks-subnet')]",
                            "action": "Allow"
                        }
                    ]
                }
            }
        }
        storage_accounts.append(content_storage)
        
        # AI Models Storage Account
        models_storage = {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2023-01-01",
            "name": f"{self.project_name.replace('-', '')}models{self.environment}",
            "location": "[parameters('location')]",
            "tags": {**self.default_tags, "Purpose": "AI Models Storage"},
            "sku": {
                "name": "Premium_LRS"
            },
            "kind": "BlockBlobStorage",
            "properties": {
                "accessTier": "Hot",
                "allowBlobPublicAccess": False,
                "allowSharedKeyAccess": True,
                "encryption": {
                    "services": {
                        "blob": {"enabled": True}
                    },
                    "keySource": "Microsoft.Storage"
                },
                "minimumTlsVersion": "TLS1_2"
            }
        }
        storage_accounts.append(models_storage)
        
        # Backup Storage Account
        backup_storage = {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2023-01-01",
            "name": f"{self.project_name.replace('-', '')}backup{self.environment}",
            "location": "[parameters('location')]",
            "tags": {**self.default_tags, "Purpose": "Backups Storage"},
            "sku": {
                "name": "Standard_GRS"
            },
            "kind": "StorageV2",
            "properties": {
                "accessTier": "Cool",
                "allowBlobPublicAccess": False,
                "allowSharedKeyAccess": True,
                "encryption": {
                    "services": {
                        "blob": {"enabled": True},
                        "file": {"enabled": True}
                    },
                    "keySource": "Microsoft.Storage"
                },
                "minimumTlsVersion": "TLS1_2"
            }
        }
        storage_accounts.append(backup_storage)
        
        return storage_accounts
    
    def get_key_vault_configuration(self) -> Dict[str, Any]:
        """Generate Azure Key Vault configuration"""



        return {
            "type": "Microsoft.KeyVault/vaults",
            "apiVersion": "2023-07-01",
            "name": f"{self.project_name}-kv-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "sku": {
                    "family": "A",
                    "name": "standard"
                },
                "tenantId": "[subscription().tenantId]",
                "enabledForDeployment": True,
                "enabledForTemplateDeployment": True,
                "enabledForDiskEncryption": True,
                "enableRbacAuthorization": True,
                "enableSoftDelete": True,
                "softDeleteRetentionInDays": 7 if self.environment == "development" else 30,
                "enablePurgeProtection": False if self.environment == "development" else True,
                "networkAcls": {
                    "defaultAction": "Deny",
                    "bypass": "AzureServices",
                    "virtualNetworkRules": [
                        {
                            "id": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'aks-subnet')]"
                        }
                    ]
                }
            }
        }
    
    def get_function_app_configuration(self) -> Dict[str, Any]:
        """Generate Azure Functions configuration"""



        return {
            "type": "Microsoft.Web/sites",
            "apiVersion": "2023-01-01",
            "name": f"{self.project_name}-functions-{self.environment}",
            "location": "[parameters('location')]",
            "kind": "functionapp,linux",
            "tags": self.default_tags,
            "properties": {
                "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('hostingPlanName'))]",
                "siteConfig": {
                    "appSettings": [
                        {
                            "name": "AzureWebJobsStorage",
                            "value": "[concat('DefaultEndpointsProtocol=https;AccountName=', variables('storageAccountName'), ';EndpointSuffix=', environment().suffixes.storage, ';AccountKey=', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName')), '2023-01-01').keys[0].value)]"
                        },
                        {
                            "name": "FUNCTIONS_EXTENSION_VERSION",
                            "value": "~4"
                        },
                        {
                            "name": "FUNCTIONS_WORKER_RUNTIME",
                            "value": "python"
                        },
                        {
                            "name": "PYTHON_VERSION",
                            "value": "3.11"
                        },
                        {
                            "name": "ENVIRONMENT",
                            "value": self.environment
                        }
                    ],
                    "linuxFxVersion": "Python|3.11",
                    "alwaysOn": False if self.environment == "development" else True,
                    "http20Enabled": True
                },
                "httpsOnly": True,
                "publicNetworkAccess": "Enabled",
                "virtualNetworkSubnetId": "[resourceId('Microsoft.Network/virtualNetworks/subnets', variables('vnetName'), 'functions-subnet')]"
            },
            "dependsOn": [
                "[resourceId('Microsoft.Web/serverfarms', variables('hostingPlanName'))]",
                "[resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
            ]
        }
    
    def get_cognitive_services_configuration(self) -> List[Dict[str, Any]]:
        """Generate Azure Cognitive Services configuration"""
        services = []
        
        # Computer Vision for image analysis
        computer_vision = {
            "type": "Microsoft.CognitiveServices/accounts",
            "apiVersion": "2023-05-01",
            "name": f"{self.project_name}-vision-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "sku": {
                "name": "S1" if self.environment == "production" else "F0"
            },
            "kind": "ComputerVision",
            "properties": {
                "customSubDomainName": f"{self.project_name}-vision-{self.environment}",
                "networkAcls": {
                    "defaultAction": "Allow"
                },
                "publicNetworkAccess": "Enabled"
            }
        }
        services.append(computer_vision)
        
        # Speech Services for audio analysis
        speech_service = {
            "type": "Microsoft.CognitiveServices/accounts",
            "apiVersion": "2023-05-01",
            "name": f"{self.project_name}-speech-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "sku": {
                "name": "S0" if self.environment == "production" else "F0"
            },
            "kind": "SpeechServices",
            "properties": {
                "customSubDomainName": f"{self.project_name}-speech-{self.environment}",
                "networkAcls": {
                    "defaultAction": "Allow"
                },
                "publicNetworkAccess": "Enabled"
            }
        }
        services.append(speech_service)
        
        # Text Analytics for content analysis
        text_analytics = {
            "type": "Microsoft.CognitiveServices/accounts",
            "apiVersion": "2023-05-01",
            "name": f"{self.project_name}-text-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "sku": {
                "name": "S" if self.environment == "production" else "F0"
            },
            "kind": "TextAnalytics",
            "properties": {
                "customSubDomainName": f"{self.project_name}-text-{self.environment}",
                "networkAcls": {
                    "defaultAction": "Allow"
                },
                "publicNetworkAccess": "Enabled"
            }
        }
        services.append(text_analytics)
        
        return services
    
    def get_log_analytics_configuration(self) -> Dict[str, Any]:
        """Generate Log Analytics workspace configuration"""



        return {
            "type": "Microsoft.OperationalInsights/workspaces",
            "apiVersion": "2023-09-01",
            "name": f"{self.project_name}-workspace-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "properties": {
                "sku": {
                    "name": "PerGB2018"
                },
                "retentionInDays": 30 if self.environment == "development" else 90,
                "workspaceCapping": {
                    "dailyQuotaGb": 1 if self.environment == "development" else 10
                },
                "publicNetworkAccessForIngestion": "Enabled",
                "publicNetworkAccessForQuery": "Enabled"
            }
        }
    
    def get_application_insights_configuration(self) -> Dict[str, Any]:
        """Generate Application Insights configuration"""



        return {
            "type": "Microsoft.Insights/components",
            "apiVersion": "2020-02-02",
            "name": f"{self.project_name}-insights-{self.environment}",
            "location": "[parameters('location')]",
            "tags": self.default_tags,
            "kind": "web",
            "properties": {
                "Application_Type": "web",
                "WorkspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]",
                "SamplingPercentage": 100 if self.environment == "development" else 50,
                "DisableIpMasking": False,
                "DisableLocalAuth": False
            }
        }
    
    def generate_arm_template(self, output_file: str = "azure-infrastructure.json") -> None:
        """Generate complete ARM template"""
        template = {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
            "contentVersion": "1.0.0.0",
            "metadata": {
                "description": f"IA-Influencer Agent Platform Infrastructure - {self.environment} Environment",
                "author": "Fahed Mlaiel <mlaiel@live.de>"
            },
            "parameters": {
                "environment": {
                    "type": "string",
                    "defaultValue": self.environment,
                    "metadata": {
                        "description": "Environment name"
                    }
                },
                "location": {
                    "type": "string",
                    "defaultValue": self.location,
                    "metadata": {
                        "description": "Azure region"
                    }
                },
                "postgresPassword": {
                    "type": "securestring",
                    "metadata": {
                        "description": "PostgreSQL administrator password"
                    }
                }
            },
            "variables": {
                "projectName": self.project_name,
                "vnetName": f"{self.project_name}-vnet-{self.environment}",
                "workspaceName": f"{self.project_name}-workspace-{self.environment}",
                "hostingPlanName": f"{self.project_name}-plan-{self.environment}",
                "storageAccountName": f"{self.project_name.replace('-', '')}func{self.environment}"
            },
            "resources": []
        }
        
        # Add all resource configurations
        template["resources"].append(self.get_virtual_network_configuration())
        template["resources"].extend(self.get_network_security_groups_configuration())
        template["resources"].append(self.get_aks_configuration())
        template["resources"].append(self.get_postgresql_configuration())
        template["resources"].append(self.get_redis_cache_configuration())
        template["resources"].extend(self.get_storage_account_configuration())
        template["resources"].append(self.get_key_vault_configuration())
        template["resources"].append(self.get_function_app_configuration())
        template["resources"].extend(self.get_cognitive_services_configuration())
        template["resources"].append(self.get_log_analytics_configuration())
        template["resources"].append(self.get_application_insights_configuration())
        
        # Add outputs
        template["outputs"] = {
            "aksClusterName": {
                "type": "string",
                "value": f"{self.project_name}-aks-{self.environment}"
            },
            "postgresqlFQDN": {
                "type": "string",
                "value": f"[reference(resourceId('Microsoft.DBforPostgreSQL/flexibleServers', '{self.project_name}-postgres-{self.environment}')).fullyQualifiedDomainName]"
            },
            "redisCacheName": {
                "type": "string",
                "value": f"{self.project_name}-redis-{self.environment}"
            },
            "keyVaultUri": {
                "type": "string",
                "value": f"[reference(resourceId('Microsoft.KeyVault/vaults', '{self.project_name}-kv-{self.environment}')).vaultUri]"
            },
            "applicationInsightsInstrumentationKey": {
                "type": "string",
                "value": f"[reference(resourceId('Microsoft.Insights/components', '{self.project_name}-insights-{self.environment}')).InstrumentationKey]"
            }
        }
        
        # Write template to file
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2)
    
    def get_deployment_script(self) -> str:
        """Generate Azure deployment script"""



        return f'''#!/bin/bash
# Azure deployment script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

ENVIRONMENT="{self.environment}"
LOCATION="{self.location}"
RESOURCE_GROUP="{self.resource_group_name}"
TEMPLATE_FILE="azure-infrastructure.json"

echo " Deploying IA-Influencer Agent to Azure..."
echo "Environment: $ENVIRONMENT"
echo "Location: $LOCATION"
echo "Resource Group: $RESOURCE_GROUP"

# Check prerequisites
if ! command -v az &> /dev/null; then
    echo " Azure CLI is not installed"
    exit 1
fi

# Check Azure login
if ! az account show &> /dev/null; then
    echo " Not logged in to Azure"
    echo "Run: az login"
    exit 1
fi

# Create resource group
echo " Creating resource group..."
az group create \\
    --name $RESOURCE_GROUP \\
    --location "$LOCATION" \\
    --tags \\
        Project="IA-Influencer-Agent" \\
        Environment=$ENVIRONMENT \\
        Owner="Fahed Mlaiel" \\
        Email=mlaiel@live.de

# Validate ARM template
echo " Validating ARM template..."
az deployment group validate \\
    --resource-group $RESOURCE_GROUP \\
    --template-file $TEMPLATE_FILE \\
    --parameters \\
        environment=$ENVIRONMENT \\
        location="$LOCATION" \\
        postgresPassword="$(openssl rand -base64 32)"

# Deploy infrastructure
echo " Deploying infrastructure..."
az deployment group create \\
    --resource-group $RESOURCE_GROUP \\
    --template-file $TEMPLATE_FILE \\
    --parameters \\
        environment=$ENVIRONMENT \\
        location="$LOCATION" \\
        postgresPassword="$(openssl rand -base64 32)"

# Get deployment outputs
echo " Getting deployment outputs..."
az deployment group show \\
    --resource-group $RESOURCE_GROUP \\
    --name azuredeploy \\
    --query properties.outputs

# Configure kubectl for AKS
echo " Configuring kubectl for AKS..."
az aks get-credentials \\
    --resource-group $RESOURCE_GROUP \\
    --name ia-influencer-agent-aks-$ENVIRONMENT

# Verify AKS connection
echo " Verifying AKS connection..."
kubectl get nodes

echo " Azure infrastructure deployed successfully!"
echo " Next steps:"
echo "1. Deploy Kubernetes manifests: kubectl apply -f k8s-manifests/"
echo "2. Configure DNS: Update Azure DNS records"
echo "3. Setup monitoring: Configure Azure Monitor"
echo "4. Configure CI/CD: Setup GitHub Actions with Azure"
'''
    
    def get_terraform_configuration(self) -> str:
        """Generate Terraform configuration for Azure"""



        return f'''# Terraform configuration for IA-Influencer Agent on Azure
# Author: Fahed Mlaiel <mlaiel@live.de>

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
    azuread = {{
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{
    key_vault {{
      purge_soft_delete_on_destroy = true
    }}
  }}
}}

# Local variables
locals {{
  project_name = "{self.project_name}"
  environment = "{self.environment}"
  location = "{self.location}"
  
  common_tags = {{
    Project = "IA-Influencer-Agent"
    Environment = local.environment
    Owner = "Fahed Mlaiel"
    Email = "mlaiel@live.de"
    ManagedBy = "Terraform"
    CostCenter = "IA-Platform"
    Compliance = "GDPR-CCPA"
  }}
}}

# Data sources
data "azurerm_client_config" "current" {{}}

# Resource Group
resource "azurerm_resource_group" "main" {{
  name = "${{local.project_name}}-rg-${{local.environment}}"
  location = local.location
  tags = local.common_tags
}}

# Virtual Network
resource "azurerm_virtual_network" "main" {{
  name = "${{local.project_name}}-vnet-${{local.environment}}"
  location = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space = ["10.0.0.0/16"]
  tags = local.common_tags
}}

# AKS Subnet
resource "azurerm_subnet" "aks" {{
  name = "aks-subnet"
  resource_group_name = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes = ["10.0.1.0/24"]
}}

# Database Subnet
resource "azurerm_subnet" "database" {{
  name = "database-subnet"
  resource_group_name = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes = ["10.0.2.0/24"]
  
  delegation {{
    name = "postgres-delegation"
    service_delegation {{
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }}
  }}
}}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {{
  name = "${{local.project_name}}-aks-${{local.environment}}"
  location = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix = "${{local.project_name}}-${{local.environment}}"
  kubernetes_version = "1.28.3"
  
  default_node_pool {{
    name = "system"
    node_count = {1 if self.environment == "development" else 3}
    vm_size = "{"Standard_DS2_v2" if self.environment == "development" else "Standard_DS3_v2"}"
    vnet_subnet_id = azurerm_subnet.aks.id
    enable_auto_scaling = true
    min_count = 1
    max_count = {3 if self.environment == "development" else 10}
    
    tags = merge(local.common_tags, {{
      NodePool = "System"
    }})
  }}
  
  identity {{
    type = "SystemAssigned"
  }}
  
  network_profile {{
    network_plugin = "azure"
    service_cidr = "10.1.0.0/16"
    dns_service_ip = "10.1.0.10"
  }}
  
  addon_profile {{
    azure_keyvault_secrets_provider {{
      enabled = true
      secret_rotation_enabled = true
    }}
    
    azure_policy {{
      enabled = true
    }}
    
    oms_agent {{
      enabled = true
      log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
    }}
  }}
  
  role_based_access_control {{
    enabled = true
    azure_active_directory {{
      managed = true
      azure_rbac_enabled = true
    }}
  }}
  
  tags = local.common_tags
}}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {{
  name = "${{local.project_name}}-postgres-${{local.environment}}"
  resource_group_name = azurerm_resource_group.main.name
  location = azurerm_resource_group.main.location
  version = "15"
  
  administrator_login = "ia_admin"
  administrator_password = var.postgres_password
  
  zone = "1"
  
  storage_mb = {32768 if self.environment == "development" else 131072}
  
  sku_name = "{"B_Standard_B1ms" if self.environment == "development" else "GP_Standard_D2s_v3"}"
  
  backup_retention_days = 7
  geo_redundant_backup_enabled = {"false" if self.environment == "development" else "true"}
  
  delegated_subnet_id = azurerm_subnet.database.id
  private_dns_zone_id = azurerm_private_dns_zone.postgres.id
  
  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
  
  tags = local.common_tags
}}

# Outputs
output "aks_cluster_name" {{
  value = azurerm_kubernetes_cluster.main.name
}}

output "postgresql_fqdn" {{
  value = azurerm_postgresql_flexible_server.main.fqdn
}}

output "resource_group_name" {{
  value = azurerm_resource_group.main.name
}}
'''
