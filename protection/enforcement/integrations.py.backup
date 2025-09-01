"""External Service Integrations for Copyright Enforcement
Professional integrations with external services, APIs, and platforms
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import aiohttp
import hashlib
from pathlib import Path
import base64
from urllib.parse import urlencode

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of external services"""
    BLOCKCHAIN_TIMESTAMP = "blockchain_timestamp"
    LEGAL_DATABASE = "legal_database"
    COPYRIGHT_REGISTRY = "copyright_registry"
    PAYMENT_PROCESSOR = "payment_processor"
    EVIDENCE_ARCHIVE = "evidence_archive"
    TRANSLATION_SERVICE = "translation_service"
    CONTENT_ANALYSIS = "content_analysis"
    REPUTATION_TRACKER = "reputation_tracker"
    DMCA_SERVICE = "dmca_service"
    LITIGATION_SUPPORT = "litigation_support"


class IntegrationStatus(Enum):
    """Status of service integrations"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class RequestMethod(Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ServiceCredentials:
    """Credentials for external service"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class ServiceConfig:
    """Configuration for external service"""
    service_name: str
    service_type: ServiceType
    base_url: str
    credentials: ServiceCredentials
    
    # Request settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5
    rate_limit_per_minute: int = 60
    
    # Features
    supports_webhooks: bool = False
    supports_batch_operations: bool = False
    requires_authentication: bool = True
    
    # Health check
    health_check_endpoint: Optional[str] = None
    health_check_interval: int = 300  # 5 minutes
    
    # Metadata
    enabled: bool = True
    last_health_check: Optional[datetime] = None
    status: IntegrationStatus = IntegrationStatus.INACTIVE


@dataclass
class ServiceRequest:
    """Request to external service"""
    id: str
    service_name: str
    method: RequestMethod
    endpoint: str
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Response
    status_code: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Retry handling
    retry_count: int = 0
    max_retries: int = 3


class BlockchainTimestampService:
    """Integration with blockchain timestamping services"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.service_name = "blockchain_timestamp"
        self.last_request_time = None
    
    async def create_timestamp(self, content_hash: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create blockchain timestamp for content"""
        try:
            request_data = {
                'hash': content_hash,
                'algorithm': 'sha256',
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = await self._make_request(
                RequestMethod.POST,
                '/timestamp',
                data=request_data
            )
            
            if response.get('success'):
                return {
                    'timestamp_id': response.get('id'),
                    'transaction_hash': response.get('tx_hash'),
                    'block_number': response.get('block_number'),
                    'confirmation_url': response.get('proof_url'),
                    'estimated_confirmation_time': response.get('confirmation_time'),
                    'cost': response.get('cost', 0)
                }
            else:
                raise Exception(f"Timestamp creation failed: {response.get('error')}")
                
        except Exception as e:
            logger.error(f"Error creating blockchain timestamp: {e}")
            raise
    
    async def verify_timestamp(self, timestamp_id: str) -> Dict[str, Any]:
        """Verify blockchain timestamp"""
        try:
            response = await self._make_request(
                RequestMethod.GET,
                f'/timestamp/{timestamp_id}/verify'
            )
            
            return {
                'verified': response.get('verified', False),
                'confirmation_count': response.get('confirmations', 0),
                'block_timestamp': response.get('block_timestamp'),
                'proof_url': response.get('proof_url')
            }
            
        except Exception as e:
            logger.error(f"Error verifying timestamp: {e}")
            return {'verified': False, 'error': str(e)}
    
    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to blockchain service"""
        try:
            # Rate limiting
            await self._apply_rate_limit()
            
            url = f"{self.config.base_url.rstrip('/')}{endpoint}"
            headers = {
                'Authorization': f"Bearer {self.config.credentials.api_key}",
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.request(
                    method.value,
                    url,
                    json=data,
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return response_data
                    else:
                        raise Exception(f"HTTP {response.status}: {response_data}")
        
        except Exception as e:
            logger.error(f"Blockchain service request failed: {e}")
            raise
    
    async def _apply_rate_limit(self):
        """Apply rate limiting"""
        if self.last_request_time:
            min_interval = 60.0 / self.config.rate_limit_per_minute
            elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
        
        self.last_request_time = datetime.utcnow()


class CopyrightRegistryService:
    """Integration with copyright registration services"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.service_name = "copyright_registry"
    
    async def search_registration(self, title: str, author: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for copyright registrations"""
        try:
            params = {
                'title': title,
                'author': author,
                'year': year
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = await self._make_request(
                RequestMethod.GET,
                f'/search?{urlencode(params)}'
            )
            
            registrations = []
            for item in response.get('results', []):
                registrations.append({
                    'registration_number': item.get('reg_number'),
                    'title': item.get('title'),
                    'author': item.get('author'),
                    'registration_date': item.get('reg_date'),
                    'publication_date': item.get('pub_date'),
                    'copyright_claimant': item.get('claimant'),
                    'work_type': item.get('work_type'),
                    'url': item.get('record_url')
                })
            
            return registrations
            
        except Exception as e:
            logger.error(f"Error searching copyright registry: {e}")
            return []
    
    async def get_registration_details(self, registration_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a copyright registration"""
        try:
            response = await self._make_request(
                RequestMethod.GET,
                f'/registration/{registration_number}'
            )
            
            if response.get('found'):
                return {
                    'registration_number': response.get('reg_number'),
                    'title': response.get('title'),
                    'author': response.get('author'),
                    'copyright_claimant': response.get('claimant'),
                    'registration_date': response.get('reg_date'),
                    'publication_date': response.get('pub_date'),
                    'work_type': response.get('work_type'),
                    'description': response.get('description'),
                    'rights_and_permissions': response.get('rights'),
                    'previous_registrations': response.get('previous_regs', []),
                    'related_works': response.get('related_works', []),
                    'record_url': response.get('record_url')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting registration details: {e}")
            return None
    
    async def _make_request(self, method: RequestMethod, endpoint: str) -> Dict[str, Any]:
        """Make request to copyright registry API"""
        try:
            url = f"{self.config.base_url.rstrip('/')}{endpoint}"
            headers = {
                'X-API-Key': self.config.credentials.api_key,
                'Accept': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.request(method.value, url, headers=headers) as response:
                    return await response.json()
        
        except Exception as e:
            logger.error(f"Copyright registry request failed: {e}")
            raise


class DMCAServiceIntegration:
    """Integration with professional DMCA service providers"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.service_name = "dmca_service"
    
    async def submit_takedown_notice(
        self,
        case_id: str,
        notice_content: str,
        recipient_info: Dict[str, Any],
        urgency: str = "normal"
    ) -> Dict[str, Any]:
        """Submit DMCA takedown notice through service"""
        try:
            request_data = {
                'case_reference': case_id,
                'notice_content': notice_content,
                'recipient': recipient_info,
                'urgency_level': urgency,
                'delivery_method': 'email',
                'tracking_enabled': True,
                'response_deadline': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
            response = await self._make_request(
                RequestMethod.POST,
                '/dmca/submit',
                data=request_data
            )
            
            return {
                'notice_id': response.get('id'),
                'tracking_number': response.get('tracking_number'),
                'delivery_status': response.get('status'),
                'estimated_delivery': response.get('estimated_delivery'),
                'cost': response.get('cost', 0),
                'tracking_url': response.get('tracking_url')
            }
            
        except Exception as e:
            logger.error(f"Error submitting DMCA notice: {e}")
            raise
    
    async def check_notice_status(self, notice_id: str) -> Dict[str, Any]:
        """Check status of submitted DMCA notice"""
        try:
            response = await self._make_request(
                RequestMethod.GET,
                f'/dmca/{notice_id}/status'
            )
            
            return {
                'notice_id': notice_id,
                'status': response.get('status'),
                'delivered_at': response.get('delivered_at'),
                'opened_at': response.get('opened_at'),
                'response_received': response.get('response_received', False),
                'response_type': response.get('response_type'),
                'response_content': response.get('response_content'),
                'compliance_status': response.get('compliance_status'),
                'next_action_recommended': response.get('next_action')
            }
            
        except Exception as e:
            logger.error(f"Error checking notice status: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to DMCA service"""
        try:
            url = f"{self.config.base_url.rstrip('/')}{endpoint}"
            headers = {
                'Authorization': f"Bearer {self.config.credentials.access_token}",
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.request(
                    method.value,
                    url,
                    json=data,
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 201]:
                        return response_data
                    else:
                        raise Exception(f"HTTP {response.status}: {response_data}")
        
        except Exception as e:
            logger.error(f"DMCA service request failed: {e}")
            raise


class PaymentProcessorIntegration:
    """Integration with payment processing services"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.service_name = "payment_processor"
    
    async def create_invoice(
        self,
        case_id: str,
        amount: float,
        currency: str,
        description: str,
        recipient_email: str
    ) -> Dict[str, Any]:
        """Create invoice for damages or settlement"""
        try:
            request_data = {
                'reference': f"CASE-{case_id}",
                'amount': amount,
                'currency': currency,
                'description': description,
                'recipient_email': recipient_email,
                'due_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'payment_methods': ['card', 'bank_transfer'],
                'webhook_url': f"{self.config.base_url}/webhooks/payment"
            }
            
            response = await self._make_request(
                RequestMethod.POST,
                '/invoices',
                data=request_data
            )
            
            return {
                'invoice_id': response.get('id'),
                'invoice_url': response.get('hosted_url'),
                'payment_link': response.get('payment_link'),
                'qr_code_url': response.get('qr_code'),
                'status': response.get('status'),
                'created_at': response.get('created_at')
            }
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            raise
    
    async def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check payment status of invoice"""
        try:
            response = await self._make_request(
                RequestMethod.GET,
                f'/invoices/{invoice_id}'
            )
            
            return {
                'invoice_id': invoice_id,
                'status': response.get('status'),
                'amount_paid': response.get('amount_paid', 0),
                'amount_due': response.get('amount_due'),
                'currency': response.get('currency'),
                'paid_at': response.get('paid_at'),
                'payment_method': response.get('payment_method'),
                'transaction_id': response.get('transaction_id'),
                'refundable': response.get('refundable', False)
            }
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {'status': 'unknown', 'error': str(e)}
    
    async def process_refund(self, invoice_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Process refund for payment"""
        try:
            request_data = {
                'invoice_id': invoice_id,
                'amount': amount,  # None for full refund
                'reason': 'Case resolution'
            }
            
            response = await self._make_request(
                RequestMethod.POST,
                f'/invoices/{invoice_id}/refund',
                data=request_data
            )
            
            return {
                'refund_id': response.get('id'),
                'status': response.get('status'),
                'amount_refunded': response.get('amount'),
                'currency': response.get('currency'),
                'estimated_arrival': response.get('estimated_arrival')
            }
            
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            raise
    
    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to payment processor"""
        try:
            url = f"{self.config.base_url.rstrip('/')}{endpoint}"
            
            # Create basic auth header
            auth_string = f"{self.config.credentials.api_key}:{self.config.credentials.api_secret}"
            auth_bytes = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f"Basic {auth_bytes}",
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.request(
                    method.value,
                    url,
                    json=data,
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status in [200, 201]:
                        return response_data
                    else:
                        raise Exception(f"HTTP {response.status}: {response_data}")
        
        except Exception as e:
            logger.error(f"Payment processor request failed: {e}")
            raise


class TranslationServiceIntegration:
    """Integration with professional translation services"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.service_name = "translation_service"
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh', 'ru']
    
    async def translate_document(
        self,
        content: str,
        source_language: str,
        target_language: str,
        document_type: str = "legal"
    ) -> Dict[str, Any]:
        """Translate legal document to target language"""
        try:
            if target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            request_data = {
                'text': content,
                'source_lang': source_language,
                'target_lang': target_language,
                'domain': document_type,
                'preserve_formatting': True,
                'quality_level': 'professional'
            }
            
            response = await self._make_request(
                RequestMethod.POST,
                '/translate',
                data=request_data
            )
            
            return {
                'translated_text': response.get('translated_text'),
                'source_language': response.get('detected_source_lang'),
                'target_language': target_language,
                'confidence_score': response.get('confidence', 0),
                'word_count': response.get('word_count'),
                'cost': response.get('cost', 0),
                'quality_score': response.get('quality_score', 0)
            }
            
        except Exception as e:
            logger.error(f"Error translating document: {e}")
            raise
    
    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        try:
            response = await self._make_request(
                RequestMethod.GET,
                '/languages'
            )
            
            return response.get('languages', [])
            
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            return []
    
    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to translation service"""
        try:
            url = f"{self.config.base_url.rstrip('/')}{endpoint}"
            headers = {
                'Authorization': f"Bearer {self.config.credentials.api_key}",
                'Content-Type': 'application/json',
                'User-Agent': 'IA-Influencer-Agent/2.0'
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.request(
                    method.value,
                    url,
                    json=data,
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return response_data
                    else:
                        raise Exception(f"HTTP {response.status}: {response_data}")
        
        except Exception as e:
            logger.error(f"Translation service request failed: {e}")
            raise


class ExternalIntegrationsManager:
    """Manager for all external service integrations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.services: Dict[str, Any] = {}
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        self.request_tracking: Dict[str, ServiceRequest] = {}
        
        # Initialize default services
        self._initialize_services()
        
        logger.info("External integrations manager initialized")
    
    def _initialize_services(self):
        """Initialize configured external services"""
        try:
            # Blockchain timestamp service
            if 'blockchain_timestamp' in self.config:
                blockchain_config = self._create_service_config(
                    'blockchain_timestamp',
                    ServiceType.BLOCKCHAIN_TIMESTAMP,
                    self.config['blockchain_timestamp']
                )
                self.service_configs['blockchain_timestamp'] = blockchain_config
                self.services['blockchain_timestamp'] = BlockchainTimestampService(blockchain_config)
            
            # Copyright registry service
            if 'copyright_registry' in self.config:
                registry_config = self._create_service_config(
                    'copyright_registry',
                    ServiceType.COPYRIGHT_REGISTRY,
                    self.config['copyright_registry']
                )
                self.service_configs['copyright_registry'] = registry_config
                self.services['copyright_registry'] = CopyrightRegistryService(registry_config)
            
            # DMCA service
            if 'dmca_service' in self.config:
                dmca_config = self._create_service_config(
                    'dmca_service',
                    ServiceType.DMCA_SERVICE,
                    self.config['dmca_service']
                )
                self.service_configs['dmca_service'] = dmca_config
                self.services['dmca_service'] = DMCAServiceIntegration(dmca_config)
            
            # Payment processor
            if 'payment_processor' in self.config:
                payment_config = self._create_service_config(
                    'payment_processor',
                    ServiceType.PAYMENT_PROCESSOR,
                    self.config['payment_processor']
                )
                self.service_configs['payment_processor'] = payment_config
                self.services['payment_processor'] = PaymentProcessorIntegration(payment_config)
            
            # Translation service
            if 'translation_service' in self.config:
                translation_config = self._create_service_config(
                    'translation_service',
                    ServiceType.TRANSLATION_SERVICE,
                    self.config['translation_service']
                )
                self.service_configs['translation_service'] = translation_config
                self.services['translation_service'] = TranslationServiceIntegration(translation_config)
            
            logger.info(f"Initialized {len(self.services)} external service integrations")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
    
    def _create_service_config(
        self,
        service_name: str,
        service_type: ServiceType,
        config_dict: Dict[str, Any]
    ) -> ServiceConfig:
        """Create service configuration from dictionary"""
        credentials = ServiceCredentials(
            api_key=config_dict.get('api_key'),
            api_secret=config_dict.get('api_secret'),
            access_token=config_dict.get('access_token'),
            client_id=config_dict.get('client_id'),
            client_secret=config_dict.get('client_secret'),
            username=config_dict.get('username'),
            password=config_dict.get('password')
        )
        
        return ServiceConfig(
            service_name=service_name,
            service_type=service_type,
            base_url=config_dict['base_url'],
            credentials=credentials,
            timeout=config_dict.get('timeout', 30),
            max_retries=config_dict.get('max_retries', 3),
            rate_limit_per_minute=config_dict.get('rate_limit_per_minute', 60),
            enabled=config_dict.get('enabled', True),
            health_check_endpoint=config_dict.get('health_check_endpoint')
        )
    
    async def start_health_monitoring(self):
        """Start health monitoring for all services"""
        if self.health_check_task:
            return
        
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Started health monitoring for external services")
    
    async def stop_health_monitoring(self):
        """Stop health monitoring"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
        
        logger.info("Stopped health monitoring")
    
    async def _health_check_loop(self):
        """Health check monitoring loop"""
        while True:
            try:
                for service_name, config in self.service_configs.items():
                    if config.enabled and config.health_check_endpoint:
                        await self._check_service_health(service_name, config)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_service_health(self, service_name: str, config: ServiceConfig):
        """Check health of individual service"""
        try:
            url = f"{config.base_url.rstrip('/')}{config.health_check_endpoint}"
            headers = {
                'User-Agent': 'IA-Influencer-Agent/2.0',
                'Accept': 'application/json'
            }
            
            # Add authentication if required
            if config.requires_authentication and config.credentials.api_key:
                headers['Authorization'] = f"Bearer {config.credentials.api_key}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        config.status = IntegrationStatus.ACTIVE
                        logger.debug(f"Service {service_name} is healthy")
                    else:
                        config.status = IntegrationStatus.ERROR
                        logger.warning(f"Service {service_name} health check failed: {response.status}")
            
            config.last_health_check = datetime.utcnow()
            
        except Exception as e:
            config.status = IntegrationStatus.ERROR
            config.last_health_check = datetime.utcnow()
            logger.error(f"Health check failed for {service_name}: {e}")
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get service instance by name"""
        return self.services.get(service_name)
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if service is available and healthy"""
        config = self.service_configs.get(service_name)
        if not config:
            return False
        
        return (
            config.enabled and
            config.status == IntegrationStatus.ACTIVE
        )
    
    async def create_blockchain_timestamp(self, content_hash: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create blockchain timestamp using configured service"""
        try:
            if not self.is_service_available('blockchain_timestamp'):
                logger.warning("Blockchain timestamp service not available")
                return None
            
            service = self.get_service('blockchain_timestamp')
            return await service.create_timestamp(content_hash, metadata)
            
        except Exception as e:
            logger.error(f"Error creating blockchain timestamp: {e}")
            return None
    
    async def search_copyright_registration(
        self,
        title: str,
        author: str,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search copyright registrations using configured service"""
        try:
            if not self.is_service_available('copyright_registry'):
                logger.warning("Copyright registry service not available")
                return []
            
            service = self.get_service('copyright_registry')
            return await service.search_registration(title, author, year)
            
        except Exception as e:
            logger.error(f"Error searching copyright registry: {e}")
            return []
    
    async def submit_dmca_notice(
        self,
        case_id: str,
        notice_content: str,
        recipient_info: Dict[str, Any],
        urgency: str = "normal"
    ) -> Optional[Dict[str, Any]]:
        """Submit DMCA notice using configured service"""
        try:
            if not self.is_service_available('dmca_service'):
                logger.warning("DMCA service not available")
                return None
            
            service = self.get_service('dmca_service')
            return await service.submit_takedown_notice(case_id, notice_content, recipient_info, urgency)
            
        except Exception as e:
            logger.error(f"Error submitting DMCA notice: {e}")
            return None
    
    async def create_payment_invoice(
        self,
        case_id: str,
        amount: float,
        currency: str,
        description: str,
        recipient_email: str
    ) -> Optional[Dict[str, Any]]:
        """Create payment invoice using configured service"""
        try:
            if not self.is_service_available('payment_processor'):
                logger.warning("Payment processor service not available")
                return None
            
            service = self.get_service('payment_processor')
            return await service.create_invoice(case_id, amount, currency, description, recipient_email)
            
        except Exception as e:
            logger.error(f"Error creating payment invoice: {e}")
            return None
    
    async def translate_document(
        self,
        content: str,
        source_language: str,
        target_language: str,
        document_type: str = "legal"
    ) -> Optional[Dict[str, Any]]:
        """Translate document using configured service"""
        try:
            if not self.is_service_available('translation_service'):
                logger.warning("Translation service not available")
                return None
            
            service = self.get_service('translation_service')
            return await service.translate_document(content, source_language, target_language, document_type)
            
        except Exception as e:
            logger.error(f"Error translating document: {e}")
            return None
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        try:
            status = {
                'total_services': len(self.service_configs),
                'active_services': 0,
                'services': {}
            }
            
            for service_name, config in self.service_configs.items():
                service_status = {
                    'name': service_name,
                    'type': config.service_type.value,
                    'status': config.status.value,
                    'enabled': config.enabled,
                    'last_health_check': config.last_health_check.isoformat() if config.last_health_check else None,
                    'base_url': config.base_url,
                    'rate_limit': config.rate_limit_per_minute
                }
                
                if config.status == IntegrationStatus.ACTIVE:
                    status['active_services'] += 1
                
                status['services'][service_name] = service_status
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting integration status: {e}")
            return {}
    
    async def disable_service(self, service_name: str):
        """Disable specific service"""
        config = self.service_configs.get(service_name)
        if config:
            config.enabled = False
            config.status = IntegrationStatus.DISABLED
            logger.info(f"Disabled service: {service_name}")
    
    async def enable_service(self, service_name: str):
        """Enable specific service"""
        config = self.service_configs.get(service_name)
        if config:
            config.enabled = True
            config.status = IntegrationStatus.INACTIVE
            logger.info(f"Enabled service: {service_name}")
            
            # Trigger immediate health check
            if config.health_check_endpoint:
                await self._check_service_health(service_name, config)
    
    async def shutdown(self):
        """Shutdown all integrations"""
        try:
            await self.stop_health_monitoring()
            
            # Clear service instances
            self.services.clear()
            self.service_configs.clear()
            
            logger.info("External integrations manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down integrations manager: {e}")


# Global instance
integrations_manager = ExternalIntegrationsManager()


async def get_integrations_manager() -> ExternalIntegrationsManager:
    """Get the global integrations manager instance"""
    return integrations_manager


__all__ = [
    'ExternalIntegrationsManager',
    'ServiceConfig',
    'ServiceCredentials',
    'ServiceRequest',
    'ServiceType',
    'IntegrationStatus',
    'RequestMethod',
    'BlockchainTimestampService',
    'CopyrightRegistryService',
    'DMCAServiceIntegration',
    'PaymentProcessorIntegration',
    'TranslationServiceIntegration',
    'get_integrations_manager'
]
