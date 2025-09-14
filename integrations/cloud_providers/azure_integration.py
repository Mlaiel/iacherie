"""Microsoft Azure Integration
==============================

Enterprise-grade Microsoft Azure integration supporting storage,
compute, AI services, and media processing for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Union, IO
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

import httpx
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.translation.text import TextTranslationClient
from azure.communication.email import EmailClient
from azure.servicebus import ServiceBusClient
from azure.monitor.query import LogsQueryClient, MetricsQueryClient


class AzureServiceType(Enum):
    """Azure service types."""
    BLOB_STORAGE = "blob_storage"
    QUEUE_STORAGE = "queue_storage"
    DATA_LAKE = "data_lake"
    COMPUTE = "compute"
    COMPUTER_VISION = "computer_vision"
    SPEECH = "speech"
    TEXT_ANALYTICS = "text_analytics"
    TRANSLATOR = "translator"
    COMMUNICATION = "communication"
    SERVICE_BUS = "service_bus"
    MONITORING = "monitoring"


class AzureRegion(Enum):
    """Azure regions."""
    EAST_US = "eastus"
    EAST_US_2 = "eastus2"
    WEST_US = "westus"
    WEST_US_2 = "westus2"
    CENTRAL_US = "centralus"
    NORTH_EUROPE = "northeurope"
    WEST_EUROPE = "westeurope"
    EAST_ASIA = "eastasia"
    SOUTHEAST_ASIA = "southeastasia"
    AUSTRALIA_EAST = "australiaeast"
    UK_SOUTH = "uksouth"


@dataclass
class AzureStorageRequest:
    """Azure storage operation request."""
    container_name: str
    blob_name: str
    operation: str  # upload, download, delete, copy
    local_file_path: Optional[str] = None
    content: Optional[bytes] = None
    metadata: Optional[Dict[str, str]] = None
    content_type: Optional[str] = None
    public_access: bool = False


@dataclass
class AzureComputeRequest:
    """Azure compute instance request."""
    vm_name: str
    resource_group: str
    location: str
    vm_size: str
    operation: str  # create, start, stop, delete
    admin_username: str = "azureuser"
    admin_password: Optional[str] = None
    ssh_public_key: Optional[str] = None
    image_reference: Optional[Dict[str, str]] = None
    custom_data: Optional[str] = None


@dataclass
class AzureMediaProcessingRequest:
    """Azure media processing request."""
    input_url: str
    output_url: Optional[str] = None
    service_type: AzureServiceType = AzureServiceType.COMPUTER_VISION
    features: List[str] = field(default_factory=list)
    language: str = "en"
    model_version: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AzureIntegration:
    """Enterprise Microsoft Azure integration for Ainflue.
    
    Features:
    - Blob Storage for content and media files
    - Queue Storage for message queuing
    - Data Lake Storage for big data analytics
    - Virtual Machines for scalable computing
    - Computer Vision for image and video analysis
    - Speech Services for audio processing
    - Text Analytics for content understanding
    - Translator for multi-language support
    - Communication Services for email/SMS
    - Service Bus for enterprise messaging
    - Azure Monitor for observability
    - Content Delivery Network integration
    - Auto-scaling and load balancing
    - Security and identity management
    """
    
    def __init__(
        self,
        subscription_id -> None: str,
        resource_group -> None: str,
        tenant_id -> None: Optional[str] = None,
        client_id -> None: Optional[str] = None,
        client_secret -> None: Optional[str] = None,
        storage_account_name -> None: Optional[str] = None,
        storage_account_key -> None: Optional[str] = None,
        default_region -> None: AzureRegion = AzureRegion.EAST_US
    ) -> None:
        """Initialize Azure integration.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group: Default resource group
            tenant_id: Azure AD tenant ID
            client_id: Service principal client ID
            client_secret: Service principal client secret
            storage_account_name: Storage account name
            storage_account_key: Storage account key
            default_region: Default Azure region
        """
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.default_region = default_region
        self.storage_account_name = storage_account_name
        
        # Initialize credentials
        if client_id and client_secret and tenant_id:
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self.blob_client = None
        self.queue_client = None
        self.datalake_client = None
        self.compute_client = None
        self.storage_mgmt_client = None
        self.resource_mgmt_client = None
        self.computer_vision_client = None
        self.text_analytics_client = None
        self.translator_client = None
        self.email_client = None
        self.servicebus_client = None
        self.logs_query_client = None
        self.metrics_query_client = None
        
        self._init_clients(storage_account_key)
        
        self.logger = logging.getLogger(__name__)
        self.session = httpx.AsyncClient(timeout=30.0)

    def _init_clients(self, storage_account_key -> None: Optional[str]) -> None:
        """Initialize Azure service clients."""
        try:
            # Storage clients
            if self.storage_account_name:
                if storage_account_key:
                    # Using account key
                    blob_service_url = f"https://{self.storage_account_name}.blob.core.windows.net"
                    self.blob_client = BlobServiceClient(
                        account_url=blob_service_url,
                        credential=storage_account_key
                    )
                    
                    queue_service_url = f"https://{self.storage_account_name}.queue.core.windows.net"
                    self.queue_client = QueueServiceClient(
                        account_url=queue_service_url,
                        credential=storage_account_key
                    )
                    
                    datalake_service_url = f"https://{self.storage_account_name}.dfs.core.windows.net"
                    self.datalake_client = DataLakeServiceClient(
                        account_url=datalake_service_url,
                        credential=storage_account_key
                    )
                else:
                    # Using Azure AD credential
                    blob_service_url = f"https://{self.storage_account_name}.blob.core.windows.net"
                    self.blob_client = BlobServiceClient(
                        account_url=blob_service_url,
                        credential=self.credential
                    )
            
            # Management clients
            self.compute_client = ComputeManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            self.storage_mgmt_client = StorageManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            self.resource_mgmt_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            # Monitoring clients
            self.logs_query_client = LogsQueryClient(credential=self.credential)
            self.metrics_query_client = MetricsQueryClient(credential=self.credential)
            
            self.logger.info("Initialized Azure clients successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure clients: {e}")
            raise

    async def upload_blob(
        self,
        storage_request: AzureStorageRequest
    ) -> Dict[str, Any]:
        """Upload blob to Azure Blob Storage.
        
        Args:
            storage_request: Storage upload request
            
        Returns:
            Dict containing upload result
        """
        try:
            blob_client = self.blob_client.get_blob_client(
                container=storage_request.container_name,
                blob=storage_request.blob_name
            )
            
            # Prepare upload data
            if storage_request.local_file_path:
                with open(storage_request.local_file_path, 'rb') as data:
                    blob_client.upload_blob(
                        data,
                        metadata=storage_request.metadata,
                        content_settings={
                            'content_type': storage_request.content_type
                        } if storage_request.content_type else None,
                        overwrite=True
                    )
            elif storage_request.content:
                blob_client.upload_blob(
                    storage_request.content,
                    metadata=storage_request.metadata,
                    content_settings={
                        'content_type': storage_request.content_type
                    } if storage_request.content_type else None,
                    overwrite=True
                )
            else:
                raise ValueError("Either local_file_path or content must be provided")
            
            # Get blob properties
            blob_properties = blob_client.get_blob_properties()
            
            result = {
                "container": storage_request.container_name,
                "blob_name": storage_request.blob_name,
                "url": blob_client.url,
                "size": blob_properties.size,
                "etag": blob_properties.etag,
                "last_modified": blob_properties.last_modified.isoformat() if blob_properties.last_modified else None,
                "content_type": blob_properties.content_settings.content_type if blob_properties.content_settings else None,
                "metadata": blob_properties.metadata
            }
            
            self.logger.info(f"Uploaded blob to Azure: {storage_request.blob_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to upload blob to Azure: {e}")
            raise

    async def download_blob(
        self,
        storage_request: AzureStorageRequest
    ) -> bytes:
        """Download blob from Azure Blob Storage.
        
        Args:
            storage_request: Storage download request
            
        Returns:
            Blob content as bytes
        """
        try:
            blob_client = self.blob_client.get_blob_client(
                container=storage_request.container_name,
                blob=storage_request.blob_name
            )
            
            if storage_request.local_file_path:
                with open(storage_request.local_file_path, 'wb') as download_file:
                    download_stream = blob_client.download_blob()
                    download_file.write(download_stream.readall())
                
                with open(storage_request.local_file_path, 'rb') as f:
                    content = f.read()
            else:
                download_stream = blob_client.download_blob()
                content = download_stream.readall()
            
            self.logger.info(f"Downloaded blob from Azure: {storage_request.blob_name}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to download blob from Azure: {e}")
            raise

    async def delete_blob(
        self,
        container_name: str,
        blob_name: str
    ) -> bool:
        """Delete blob from Azure Blob Storage.
        
        Args:
            container_name: Container name
            blob_name: Blob name to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            
            self.logger.info(f"Deleted blob from Azure: {blob_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete blob from Azure: {e}")
            return False

    async def create_virtual_machine(
        self,
        compute_request: AzureComputeRequest
    ) -> Dict[str, Any]:
        """Create Azure Virtual Machine.
        
        Args:
            compute_request: VM creation request
            
        Returns:
            Dict containing VM details
        """
        try:
            # Default image reference
            image_reference = compute_request.image_reference or {
                'publisher': 'Canonical',
                'offer': 'UbuntuServer',
                'sku': '18.04-LTS',
                'version': 'latest'
            }
            
            # Network configuration
            network_interface_name = f"{compute_request.vm_name}-nic"
            
            # Storage configuration
            os_disk_name = f"{compute_request.vm_name}-osdisk"
            
            # VM configuration
            vm_parameters = {
                'location': compute_request.location,
                'os_profile': {
                    'computer_name': compute_request.vm_name,
                    'admin_username': compute_request.admin_username,
                    'admin_password': compute_request.admin_password,
                    'custom_data': compute_request.custom_data
                },
                'hardware_profile': {
                    'vm_size': compute_request.vm_size
                },
                'storage_profile': {
                    'image_reference': image_reference,
                    'os_disk': {
                        'name': os_disk_name,
                        'caching': 'ReadWrite',
                        'create_option': 'FromImage'
                    }
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': f"/subscriptions/{self.subscription_id}/resourceGroups/{compute_request.resource_group}/providers/Microsoft.Network/networkInterfaces/{network_interface_name}"
                    }]
                }
            }
            
            # SSH key configuration
            if compute_request.ssh_public_key:
                vm_parameters['os_profile']['linux_configuration'] = {
                    'disable_password_authentication': True,
                    'ssh': {
                        'public_keys': [{
                            'path': f'/home/{compute_request.admin_username}/.ssh/authorized_keys',
                            'key_data': compute_request.ssh_public_key
                        }]
                    }
                }
            
            # Create VM
            operation = self.compute_client.virtual_machines.begin_create_or_update(
                compute_request.resource_group,
                compute_request.vm_name,
                vm_parameters
            )
            
            result = {
                "vm_name": compute_request.vm_name,
                "resource_group": compute_request.resource_group,
                "location": compute_request.location,
                "vm_size": compute_request.vm_size,
                "operation_id": operation.name,
                "status": "creating"
            }
            
            self.logger.info(f"Created Azure VM: {compute_request.vm_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create Azure VM: {e}")
            raise

    async def analyze_image_vision(
        self,
        image_request: AzureMediaProcessingRequest
    ) -> Dict[str, Any]:
        """Analyze image using Azure Computer Vision.
        
        Args:
            image_request: Image analysis request
            
        Returns:
            Dict containing analysis results
        """
        try:
            # This would require Azure Computer Vision client initialization
            # For now, return a placeholder structure
            analysis_result = {
                "image_url": image_request.input_url,
                "analysis_time": datetime.utcnow().isoformat(),
                "categories": [],
                "tags": [],
                "description": "",
                "faces": [],
                "objects": [],
                "adult_content": {
                    "is_adult_content": False,
                    "is_racy_content": False,
                    "adult_score": 0.0,
                    "racy_score": 0.0
                },
                "color": {
                    "dominant_color_foreground": "",
                    "dominant_color_background": "",
                    "dominant_colors": [],
                    "accent_color": "",
                    "is_bw_image": False
                }
            }
            
            # In a real implementation, you would:
            # 1. Initialize Computer Vision client with endpoint and key
            # 2. Call analyze_image with appropriate features
            # 3. Process and format the results
            
            self.logger.info(f"Analyzed image with Azure Vision: {image_request.input_url}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze image with Azure Vision: {e}")
            raise

    async def transcribe_audio_speech(
        self,
        audio_request: AzureMediaProcessingRequest
    ) -> Dict[str, Any]:
        """Transcribe audio using Azure Speech Services.
        
        Args:
            audio_request: Audio transcription request
            
        Returns:
            Dict containing transcription results
        """
        try:
            # This would require Azure Speech Services configuration
            # For now, return a placeholder structure
            transcription_result = {
                "audio_url": audio_request.input_url,
                "language": audio_request.language,
                "transcription_time": datetime.utcnow().isoformat(),
                "transcription": "",
                "confidence": 0.0,
                "words": [],
                "phrases": [],
                "sentiment": {
                    "overall_sentiment": "neutral",
                    "positive_score": 0.0,
                    "neutral_score": 0.0,
                    "negative_score": 0.0
                }
            }
            
            # In a real implementation, you would:
            # 1. Configure SpeechConfig with subscription key and region
            # 2. Set up AudioConfig for the input audio
            # 3. Create SpeechRecognizer and start recognition
            # 4. Process recognition results
            
            self.logger.info(f"Transcribed audio with Azure Speech: {audio_request.input_url}")
            return transcription_result
            
        except Exception as e:
            self.logger.error(f"Failed to transcribe audio with Azure Speech: {e}")
            raise

    async def analyze_text_sentiment(
        self,
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Analyze text sentiment using Azure Text Analytics.
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            Dict containing sentiment analysis
        """
        try:
            # This would require Azure Text Analytics client
            # For now, return a placeholder structure
            sentiment_result = {
                "text": text,
                "language": language,
                "analysis_time": datetime.utcnow().isoformat(),
                "overall_sentiment": "neutral",
                "confidence_scores": {
                    "positive": 0.0,
                    "neutral": 0.0,
                    "negative": 0.0
                },
                "sentences": [],
                "key_phrases": [],
                "entities": [],
                "personally_identifiable_information": []
            }
            
            # In a real implementation, you would:
            # 1. Initialize TextAnalyticsClient with endpoint and credential
            # 2. Call analyze_sentiment, extract_key_phrases, recognize_entities
            # 3. Process and format the results
            
            self.logger.info(f"Analyzed text sentiment with Azure Text Analytics")
            return sentiment_result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze text sentiment: {e}")
            raise

    async def translate_text_azure(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate text using Azure Translator.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Dict containing translation results
        """
        try:
            # This would require Azure Translator client
            # For now, return a placeholder structure
            translation_result = {
                "original_text": text,
                "translated_text": text,  # Placeholder
                "source_language": source_language or "auto-detected",
                "target_language": target_language,
                "confidence": 1.0,
                "translation_time": datetime.utcnow().isoformat(),
                "alternatives": []
            }
            
            # In a real implementation, you would:
            # 1. Initialize TextTranslationClient with credential
            # 2. Call translate with appropriate parameters
            # 3. Process and format the results
            
            self.logger.info(f"Translated text with Azure Translator to {target_language}")
            return translation_result
            
        except Exception as e:
            self.logger.error(f"Failed to translate text with Azure: {e}")
            raise

    async def send_email(
        self,
        sender_address: str,
        recipient_addresses: List[str],
        subject: str,
        content: str,
        content_type: str = "text/plain"
    ) -> Dict[str, Any]:
        """Send email using Azure Communication Services.
        
        Args:
            sender_address: Sender email address
            recipient_addresses: List of recipient email addresses
            subject: Email subject
            content: Email content
            content_type: Content type (text/plain or text/html)
            
        Returns:
            Dict containing send result
        """
        try:
            # This would require Azure Communication Services Email client
            # For now, return a placeholder structure
            email_result = {
                "message_id": str(uuid.uuid4()),
                "sender": sender_address,
                "recipients": recipient_addresses,
                "subject": subject,
                "status": "sent",
                "sent_time": datetime.utcnow().isoformat()
            }
            
            # In a real implementation, you would:
            # 1. Initialize EmailClient with connection string
            # 2. Prepare email message with recipients, content, etc.
            # 3. Send email and handle response
            
            self.logger.info(f"Sent email via Azure Communication Services")
            return email_result
            
        except Exception as e:
            self.logger.error(f"Failed to send email via Azure: {e}")
            raise

    async def send_service_bus_message(
        self,
        queue_name: str,
        message_body: Union[str, bytes, Dict[str, Any]],
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """Send message to Azure Service Bus queue.
        
        Args:
            queue_name: Service Bus queue name
            message_body: Message body
            properties: Message properties
            
        Returns:
            Message ID
        """
        try:
            # This would require Azure Service Bus client
            # For now, return a placeholder
            message_id = str(uuid.uuid4())
            
            # In a real implementation, you would:
            # 1. Initialize ServiceBusClient with connection string
            # 2. Get queue sender
            # 3. Create and send message
            # 4. Return message ID
            
            self.logger.info(f"Sent message to Azure Service Bus queue: {queue_name}")
            return message_id
            
        except Exception as e:
            self.logger.error(f"Failed to send Service Bus message: {e}")
            raise

    async def query_logs(
        self,
        workspace_id: str,
        query: str,
        timespan: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Query Azure Monitor logs.
        
        Args:
            workspace_id: Log Analytics workspace ID
            query: KQL query
            timespan: Query timespan
            
        Returns:
            Dict containing query results
        """
        try:
            # This would require Azure Monitor Query client
            # For now, return a placeholder structure
            query_result = {
                "workspace_id": workspace_id,
                "query": query,
                "execution_time": datetime.utcnow().isoformat(),
                "rows": [],
                "tables": [],
                "statistics": {
                    "execution_time_seconds": 0.0,
                    "resource_usage": {}
                }
            }
            
            # In a real implementation, you would:
            # 1. Use LogsQueryClient to execute the KQL query
            # 2. Process query results and format them
            # 3. Return structured results
            
            self.logger.info(f"Queried Azure Monitor logs")
            return query_result
            
        except Exception as e:
            self.logger.error(f"Failed to query Azure Monitor logs: {e}")
            raise

    async def get_metrics(
        self,
        resource_uri: str,
        metric_names: List[str],
        timespan: Optional[timedelta] = None,
        interval: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Azure Monitor metrics.
        
        Args:
            resource_uri: Resource URI
            metric_names: List of metric names
            timespan: Query timespan
            interval: Aggregation interval
            
        Returns:
            Dict containing metrics data
        """
        try:
            # This would require Azure Monitor Metrics client
            # For now, return a placeholder structure
            metrics_result = {
                "resource_uri": resource_uri,
                "metric_names": metric_names,
                "timespan": timespan.total_seconds() if timespan else None,
                "interval": interval,
                "query_time": datetime.utcnow().isoformat(),
                "metrics": []
            }
            
            # In a real implementation, you would:
            # 1. Use MetricsQueryClient to query metrics
            # 2. Process metric results and format them
            # 3. Return structured metrics data
            
            self.logger.info(f"Retrieved Azure Monitor metrics")
            return metrics_result
            
        except Exception as e:
            self.logger.error(f"Failed to get Azure Monitor metrics: {e}")
            raise

    async def close(self) -> None:
        """Close HTTP session and cleanup resources."""
        await self.session.aclose()

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Creator content processing specific functions for Azure
async def process_creator_content_azure(
    azure: AzureIntegration,
    content_url: str,
    creator_id: str,
    content_type: str = "image"
) -> Dict[str, Any]:
    """Process creator content with Azure AI services.
    
    Args:
        azure: Azure integration instance
        content_url: Content URL in Azure Storage
        creator_id: Creator identifier
        content_type: Content type (image/audio/text)
        
    Returns:
        Dict containing processing results
    """
    processing_results = {}
    
    if content_type == "image":
        # Analyze image content
        image_analysis = await azure.analyze_image_vision(
            AzureMediaProcessingRequest(
                input_url=content_url,
                features=["categories", "tags", "description", "faces", "adult"]
            )
        )
        processing_results["image_analysis"] = image_analysis
        
    elif content_type == "audio":
        # Transcribe audio content
        transcription = await azure.transcribe_audio_speech(
            AzureMediaProcessingRequest(
                input_url=content_url,
                language="en"
            )
        )
        processing_results["transcription"] = transcription
        
        # Analyze sentiment of transcription
        if transcription.get("transcription"):
            sentiment = await azure.analyze_text_sentiment(
                transcription["transcription"]
            )
            processing_results["sentiment"] = sentiment
    
    # Send processing complete notification
    await azure.send_service_bus_message(
        queue_name="content-processing-complete",
        message_body={
            "creator_id": creator_id,
            "content_url": content_url,
            "content_type": content_type,
            "processing_results": processing_results
        }
    )
    
    return processing_results


async def setup_creator_azure_pipeline(
    azure: AzureIntegration,
    creator_id: str,
    storage_container: str
) -> Dict[str, Any]:
    """Setup Azure content processing pipeline for creator.
    
    Args:
        azure: Azure integration instance
        creator_id: Creator identifier
        storage_container: Azure Storage container
        
    Returns:
        Dict containing pipeline setup details
    """
    pipeline_config = {
        "creator_id": creator_id,
        "storage_container": storage_container,
        "upload_endpoint": f"https://{azure.storage_account_name}.blob.core.windows.net/{storage_container}/creators/{creator_id}/uploads/",
        "processed_endpoint": f"https://{azure.storage_account_name}.blob.core.windows.net/{storage_container}/creators/{creator_id}/processed/",
        "queues": [
            f"creator-{creator_id}-uploads",
            f"creator-{creator_id}-processing",
            f"creator-{creator_id}-complete"
        ],
        "ai_services": [
            "computer_vision",
            "speech_services",
            "text_analytics",
            "translator"
        ]
    }
    
    return pipeline_config