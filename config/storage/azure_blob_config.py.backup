"""Azure Blob Storage Configuration for IA-Influencer Agent Platform
================================================================

Professional Azure Blob storage configuration for enterprise content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import AzureError

@dataclass
class AzureContainerConfig:
    """Azure container configuration for specific content types."""
    
    name: str
    public_access: str = 'off'  # 'blob', 'container', 'off'
    metadata: Optional[Dict[str, str]] = None
    tier: str = 'hot'  # 'hot', 'cool', 'archive'

@dataclass
class AzureBlobConfig:
    """
    Comprehensive Azure Blob Storage configuration for IA-Influencer Agent platform.
    Provides enterprise-grade blob storage with multi-tier optimization.
    """
    
    # Azure Storage Account
    account_name: str = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', '')
    account_key: str = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '')
    connection_string: str = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
    
    # Service URLs
    blob_service_url: str = f"https://{account_name}.blob.core.windows.net"
    
    # Container configurations
    containers: Dict[str, AzureContainerConfig] = None
    
    # Performance settings
    max_block_size: int = 100 * 1024 * 1024  # 100MB
    max_single_put_size: int = 256 * 1024 * 1024  # 256MB
    max_concurrency: int = 6
    
    # Security settings
    enable_https: bool = True
    enable_encryption: bool = True
    enable_soft_delete: bool = True
    soft_delete_retention_days: int = 30
    
    # Content delivery
    enable_cdn: bool = True
    cdn_endpoint: Optional[str] = None
    
    def __post_init__(self):
        """Initialize container configurations if not provided."""
        if self.containers is None:
            self.containers = self._get_default_container_config()
        
        if not self.connection_string and self.account_name and self.account_key:
            self.connection_string = (
                f"DefaultEndpointsProtocol=https;"
                f"AccountName={self.account_name};"
                f"AccountKey={self.account_key};"
                f"EndpointSuffix=core.windows.net"
            )
    
    def _get_default_container_config(self) -> Dict[str, AzureContainerConfig]:
        """Default container configuration for different content types."""
        env = os.getenv('ENVIRONMENT', 'development')
        
        return {
            'audio-files': AzureContainerConfig(
                name=f"audio-{env}",
                public_access='off',
                tier='hot',
                metadata={'content_type': 'audio', 'environment': env}
            ),
            'video-files': AzureContainerConfig(
                name=f"video-{env}",
                public_access='off',
                tier='cool',  # Videos accessed less frequently
                metadata={'content_type': 'video', 'environment': env}
            ),
            'image-files': AzureContainerConfig(
                name=f"images-{env}",
                public_access='blob',  # Public read for CDN
                tier='hot',
                metadata={'content_type': 'image', 'environment': env}
            ),
            'document-files': AzureContainerConfig(
                name=f"documents-{env}",
                public_access='off',
                tier='cool',
                metadata={'content_type': 'document', 'environment': env}
            ),
            'ml-models': AzureContainerConfig(
                name=f"ml-models-{env}",
                public_access='off',
                tier='cool',
                metadata={'content_type': 'model', 'environment': env}
            ),
            'fingerprint-data': AzureContainerConfig(
                name=f"fingerprints-{env}",
                public_access='off',
                tier='archive',  # Long-term storage
                metadata={'content_type': 'fingerprint', 'environment': env}
            ),
            'user-uploads': AzureContainerConfig(
                name=f"uploads-{env}",
                public_access='off',
                tier='hot',
                metadata={'content_type': 'upload', 'environment': env}
            ),
            'processed-content': AzureContainerConfig(
                name=f"processed-{env}",
                public_access='off',
                tier='hot',
                metadata={'content_type': 'processed', 'environment': env}
            )
        }
    
    def get_blob_service_client(self) -> BlobServiceClient:
        """Create and configure Azure Blob Service client."""
        try:
            if self.connection_string:
                return BlobServiceClient.from_connection_string(
                    conn_str=self.connection_string
                )
            else:
                return BlobServiceClient(
                    account_url=self.blob_service_url,
                    credential=self.account_key
                )
        except Exception as e:
            raise AzureError(f"Failed to create Blob Service client: {e}")
    
    def get_container_client(self, container_name: str) -> ContainerClient:
        """Get container client for specific container."""
        blob_service_client = self.get_blob_service_client()
        return blob_service_client.get_container_client(container_name)
    
    def validate_configuration(self) -> bool:
        """Validate Azure Blob Storage configuration and connectivity."""
        try:
            client = self.get_blob_service_client()
            # Test connectivity by listing containers
            list(client.list_containers(max_results=1))
            return True
        except Exception as e:
            print(f"Azure Blob configuration validation failed: {e}")
            return False
    
    def get_container_name(self, content_type: str) -> str:
        """Get container name for specific content type."""
        container_key = f"{content_type}-files"
        if container_key not in self.containers:
            # Fallback to user-uploads for unknown types
            container_key = "user-uploads"
        return self.containers[container_key].name
    
    def get_content_types(self) -> List[str]:
        """Get list of supported content types."""
        return [key.replace('-files', '') for key in self.containers.keys() 
                if key.endswith('-files')]
    
    def get_access_tier_for_content(self, content_type: str) -> str:
        """Get appropriate access tier for content type."""
        container_key = f"{content_type}-files"
        if container_key in self.containers:
            return self.containers[container_key].tier
        return 'hot'  # Default tier
    
    def get_sas_url_config(self) -> Dict[str, Any]:
        """Get configuration for SAS URL generation."""
        return {
            'account_name': self.account_name,
            'account_key': self.account_key,
            'protocol': 'https' if self.enable_https else 'http'
        }
    
    def get_lifecycle_management_policy(self) -> Dict[str, Any]:
        """Get lifecycle management policy for blob storage optimization."""
        return {
            'rules': [
                {
                    'name': 'audio_lifecycle',
                    'enabled': True,
                    'type': 'Lifecycle',
                    'definition': {
                        'filters': {
                            'blobTypes': ['blockBlob'],
                            'prefixMatch': ['audio/']
                        },
                        'actions': {
                            'baseBlob': {
                                'tierToCool': {'daysAfterModificationGreaterThan': 30},
                                'tierToArchive': {'daysAfterModificationGreaterThan': 365}
                            }
                        }
                    }
                },
                {
                    'name': 'video_lifecycle',
                    'enabled': True,
                    'type': 'Lifecycle',
                    'definition': {
                        'filters': {
                            'blobTypes': ['blockBlob'],
                            'prefixMatch': ['video/']
                        },
                        'actions': {
                            'baseBlob': {
                                'tierToCool': {'daysAfterModificationGreaterThan': 90},
                                'tierToArchive': {'daysAfterModificationGreaterThan': 730}
                            }
                        }
                    }
                },
                {
                    'name': 'fingerprint_lifecycle',
                    'enabled': True,
                    'type': 'Lifecycle',
                    'definition': {
                        'filters': {
                            'blobTypes': ['blockBlob'],
                            'prefixMatch': ['fingerprints/']
                        },
                        'actions': {
                            'baseBlob': {
                                'tierToArchive': {'daysAfterModificationGreaterThan': 30}
                            }
                        }
                    }
                }
            ]
        }

# Global Azure Blob configuration instance
azure_blob_config = AzureBlobConfig()
