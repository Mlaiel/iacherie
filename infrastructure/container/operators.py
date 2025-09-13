"""Operators Infrastructure Management - Consolidated Module
==========================================================
All custom operators functionality consolidated into a single module

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

import asyncio
import logging
import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

class OperatorType(Enum):
    """Operator types"""
    STATEFUL = "stateful"
    STATELESS = "stateless"
    CONTROLLER = "controller"
    WEBHOOK = "webhook"

class CRDScope(Enum):
    """CRD scope"""
    NAMESPACED = "Namespaced"
    CLUSTER = "Cluster"

@dataclass
class CRDConfig:
    """Custom Resource Definition configuration"""
    name: str
    group: str
    version: str
    kind: str
    plural: str
    scope: CRDScope = CRDScope.NAMESPACED
    schema: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperatorConfig:
    """Operator configuration"""
    name: str
    operator_type: OperatorType
    image: str
    replicas: int = 1
    resources: Dict[str, Any] = field(default_factory=dict)
    rbac_rules: List[Dict[str, Any]] = field(default_factory=list)

class OperatorManager:
    """Unified operator management interface"""
    
    def __init__(self):
        self.crd_manager = CRDManager()
        self.custom_controller_manager = CustomControllerManager()
        self.operator_lifecycle_manager = OperatorLifecycleManager()
        self.logger = logging.getLogger(__name__)

class CRDManager:
    """Custom Resource Definition management"""
    
    def __init__(self):
        self.crds = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_crd(self, config: CRDConfig) -> bool:
        """Create Custom Resource Definition"""
        try:
            self.logger.info(f"Creating CRD: {config.name}")
            
            crd_spec = {
                'apiVersion': 'apiextensions.k8s.io/v1',
                'kind': 'CustomResourceDefinition',
                'metadata': {
                    'name': f"{config.plural}.{config.group}"
                },
                'spec': {
                    'group': config.group,
                    'versions': [{
                        'name': config.version,
                        'served': True,
                        'storage': True,
                        'schema': {
                            'openAPIV3Schema': config.schema or self._default_schema()
                        }
                    }],
                    'scope': config.scope.value,
                    'names': {
                        'plural': config.plural,
                        'singular': config.name.lower(),
                        'kind': config.kind
                    }
                }
            }
            
            self.crds[config.name] = crd_spec
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create CRD: {e}")
            return False
    
    def _default_schema(self) -> Dict[str, Any]:
        """Default OpenAPI v3 schema for CRD"""
        return {
            'type': 'object',
            'properties': {
                'spec': {
                    'type': 'object',
                    'properties': {
                        'replicas': {
                            'type': 'integer',
                            'minimum': 1
                        },
                        'image': {
                            'type': 'string'
                        }
                    }
                },
                'status': {
                    'type': 'object',
                    'properties': {
                        'replicas': {
                            'type': 'integer'
                        },
                        'readyReplicas': {
                            'type': 'integer'
                        }
                    }
                }
            }
        }
    
    async def create_ai_engine_crd(self) -> bool:
        """Create AI Engine CRD for the platform"""
        config = CRDConfig(
            name="aiengine",
            group="ainflue.io",
            version="v1",
            kind="AIEngine",
            plural="aiengines",
            schema={
                'type': 'object',
                'properties': {
                    'spec': {
                        'type': 'object',
                        'properties': {
                            'modelType': {
                                'type': 'string',
                                'enum': ['text', 'audio', 'video', 'image']
                            },
                            'modelPath': {
                                'type': 'string'
                            },
                            'replicas': {
                                'type': 'integer',
                                'minimum': 1,
                                'maximum': 10
                            },
                            'resources': {
                                'type': 'object',
                                'properties': {
                                    'gpu': {
                                        'type': 'boolean'
                                    },
                                    'memory': {
                                        'type': 'string'
                                    },
                                    'cpu': {
                                        'type': 'string'
                                    }
                                }
                            }
                        },
                        'required': ['modelType', 'modelPath']
                    },
                    'status': {
                        'type': 'object',
                        'properties': {
                            'phase': {
                                'type': 'string',
                                'enum': ['Pending', 'Running', 'Failed']
                            },
                            'replicas': {
                                'type': 'integer'
                            },
                            'readyReplicas': {
                                'type': 'integer'
                            }
                        }
                    }
                }
            }
        )
        
        return await self.create_crd(config)

class CustomControllerManager:
    """Custom controller management"""
    
    def __init__(self):
        self.controllers = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_controller(self, config: OperatorConfig) -> bool:
        """Create custom controller"""
        try:
            self.logger.info(f"Creating controller: {config.name}")
            
            # Create RBAC resources
            await self._create_rbac_resources(config)
            
            # Create controller deployment
            controller_deployment = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': f"{config.name}-controller",
                    'labels': {
                        'app': f"{config.name}-controller"
                    }
                },
                'spec': {
                    'replicas': config.replicas,
                    'selector': {
                        'matchLabels': {
                            'app': f"{config.name}-controller"
                        }
                    },
                    'template': {
                        'metadata': {
                            'labels': {
                                'app': f"{config.name}-controller"
                            }
                        },
                        'spec': {
                            'serviceAccountName': f"{config.name}-controller",
                            'containers': [{
                                'name': 'controller',
                                'image': config.image,
                                'resources': config.resources,
                                'env': [
                                    {
                                        'name': 'WATCH_NAMESPACE',
                                        'valueFrom': {
                                            'fieldRef': {
                                                'fieldPath': 'metadata.namespace'
                                            }
                                        }
                                    }
                                ]
                            }]
                        }
                    }
                }
            }
            
            self.controllers[config.name] = controller_deployment
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create controller: {e}")
            return False
    
    async def _create_rbac_resources(self, config: OperatorConfig):
        """Create RBAC resources for controller"""
        
        # Service Account
        service_account = {
            'apiVersion': 'v1',
            'kind': 'ServiceAccount',
            'metadata': {
                'name': f"{config.name}-controller"
            }
        }
        
        # Cluster Role
        cluster_role = {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'ClusterRole',
            'metadata': {
                'name': f"{config.name}-controller"
            },
            'rules': config.rbac_rules or self._default_rbac_rules()
        }
        
        # Cluster Role Binding
        cluster_role_binding = {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'ClusterRoleBinding',
            'metadata': {
                'name': f"{config.name}-controller"
            },
            'roleRef': {
                'apiGroup': 'rbac.authorization.k8s.io',
                'kind': 'ClusterRole',
                'name': f"{config.name}-controller"
            },
            'subjects': [{
                'kind': 'ServiceAccount',
                'name': f"{config.name}-controller",
                'namespace': 'default'
            }]
        }
    
    def _default_rbac_rules(self) -> List[Dict[str, Any]]:
        """Default RBAC rules for controller"""
        return [
            {
                'apiGroups': [''],
                'resources': ['pods', 'services', 'configmaps', 'secrets'],
                'verbs': ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']
            },
            {
                'apiGroups': ['apps'],
                'resources': ['deployments', 'statefulsets'],
                'verbs': ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']
            },
            {
                'apiGroups': ['ainflue.io'],
                'resources': ['*'],
                'verbs': ['get', 'list', 'watch', 'create', 'update', 'patch', 'delete']
            }
        ]

class OperatorLifecycleManager:
    """Operator Lifecycle Manager (OLM) integration"""
    
    def __init__(self):
        self.operator_packages = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_operator_package(self, 
                                    name: str, 
                                    version: str,
                                    operator_config: OperatorConfig,
                                    crd_configs: List[CRDConfig]) -> bool:
        """Create operator package for OLM"""
        try:
            self.logger.info(f"Creating operator package: {name}")
            
            # Create CSV (ClusterServiceVersion)
            csv = self._create_csv(name, version, operator_config, crd_configs)
            
            # Create package manifest
            package_manifest = {
                'packageName': name,
                'channels': [{
                    'name': 'stable',
                    'currentCSV': f"{name}.v{version}"
                }],
                'defaultChannel': 'stable'
            }
            
            self.operator_packages[name] = {
                'csv': csv,
                'package': package_manifest,
                'crds': crd_configs
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create operator package: {e}")
            return False
    
    def _create_csv(self, 
                   name: str, 
                   version: str,
                   operator_config: OperatorConfig,
                   crd_configs: List[CRDConfig]) -> Dict[str, Any]:
        """Create ClusterServiceVersion"""
        
        csv = {
            'apiVersion': 'operators.coreos.com/v1alpha1',
            'kind': 'ClusterServiceVersion',
            'metadata': {
                'name': f"{name}.v{version}",
                'annotations': {
                    'alm-examples': '[]',
                    'categories': 'AI/ML,Developer Tools',
                    'description': f"{name} operator for IA-Influencer-Agent platform"
                }
            },
            'spec': {
                'displayName': name.title(),
                'description': f"{name} operator manages {name} resources",
                'version': version,
                'maturity': 'stable',
                'provider': {
                    'name': 'IA-Influencer-Agent'
                },
                'maintainers': [{
                    'name': 'Fahed Mlaiel',
                    'email': 'mlaiel@live.de'
                }],
                'labels': {
                    'alm-owner-ainflue': name,
                    'alm-status-descriptors': name
                },
                'selector': {
                    'matchLabels': {
                        'alm-owner-ainflue': name
                    }
                },
                'links': [{
                    'name': 'Documentation',
                    'url': 'https://github.com/Mlaiel/Ainflue'
                }],
                'icon': [{
                    'base64data': '',
                    'mediatype': 'image/png'
                }],
                'customresourcedefinitions': {
                    'owned': [
                        {
                            'name': f"{crd.plural}.{crd.group}",
                            'version': crd.version,
                            'kind': crd.kind,
                            'displayName': crd.kind,
                            'description': f"{crd.kind} resource"
                        }
                        for crd in crd_configs
                    ]
                },
                'install': {
                    'strategy': 'deployment',
                    'spec': {
                        'deployments': [{
                            'name': f"{name}-controller",
                            'spec': {
                                'replicas': operator_config.replicas,
                                'selector': {
                                    'matchLabels': {
                                        'app': f"{name}-controller"
                                    }
                                },
                                'template': {
                                    'metadata': {
                                        'labels': {
                                            'app': f"{name}-controller"
                                        }
                                    },
                                    'spec': {
                                        'containers': [{
                                            'name': 'controller',
                                            'image': operator_config.image,
                                            'resources': operator_config.resources
                                        }]
                                    }
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        return csv

# Global instances
operator_manager = OperatorManager()
crd_manager = CRDManager()
custom_controller_manager = CustomControllerManager()
operator_lifecycle_manager = OperatorLifecycleManager()

__all__ = [
    "OperatorManager",
    "CRDManager",
    "CustomControllerManager",
    "OperatorLifecycleManager",
    "CRDConfig",
    "OperatorConfig",
    "OperatorType",
    "CRDScope",
    "operator_manager",
    "crd_manager",
    "custom_controller_manager",
    "operator_lifecycle_manager"
]