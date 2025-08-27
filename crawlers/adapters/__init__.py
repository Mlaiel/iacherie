"""
Crawlers Adapters - Enterprise Multi-backend Integration System
==============================================================

Industrial-grade adapters for comprehensive multi-platform, multi-protocol, 
and multi-format integration in the IA-Influencer Agent platform.

This module provides enterprise-level abstraction layers for seamless 
integration with external services, platforms, and data sources.

Business Logic Flow:
User Content Upload → Format Detection → Platform Integration → 
Data Processing → Authentication → Storage → Protection → Distribution

Core Components:
- Content Adapters: Multi-format content processing and transformation
- Platform Adapters: Social media and platform integrations  
- Authentication Adapters: Enterprise security and access control
- Data Adapters: ETL/ELT processing and transformation pipelines
- Storage Adapters: Multi-backend storage with vector database support
- Format Adapters: Universal format detection and processing
- Protocol Adapters: Network protocol communication
- API Adapters: REST/GraphQL API integration and management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
   - Binary data with compression and encryption
   - Protocol Buffers for efficient serialization
   - MessagePack for compact data exchange
   - YAML for configuration management
   - TOML for structured configuration
   - Parquet for analytical data storage
   - Avro for schema evolution support
   - HDF5 for scientific data
   - SQLite for embedded databases

6. **Protocol Adapters** - Multi-protocol network communication
   - HTTP/1.1, HTTP/2, HTTP/3 with advanced features
   - WebSocket with real-time bidirectional communication
   - FTP/SFTP for secure file transfer operations
   - TCP/UDP for low-level network communication
   - MQTT for IoT and real-time messaging
   - CoAP for lightweight IoT communication
   - SSH for secure remote operations
   - WebRTC for peer-to-peer media streaming

7. **Authentication Adapters** - Enterprise security systems
   - OAuth2 2.0/2.1 with PKCE and refresh tokens
   - JWT with RS256/HS256/ES256 and custom claims
   - API key rotation and lifecycle management
   - Certificate-based mutual TLS authentication
   - Multi-Factor Authentication (TOTP, SMS, Email, Hardware keys)
   - Single Sign-On with SAML 2.0 and OpenID Connect
   - Passwordless authentication (WebAuthn, Magic links)
   - Social authentication (Google, Facebook, GitHub)
   - Enterprise directory integration (LDAP, Active Directory)

8. **Format Adapters** - Advanced format processing and conversion
   - Universal format detection with magic number analysis
   - High-performance compression (GZIP, BZIP2, LZMA, Brotli, LZ4, Zstandard)
   - Enterprise-grade encryption (AES-256, RSA-4096, ChaCha20-Poly1305)
   - Professional media transcoding and optimization
   - Schema validation and data integrity verification
   - Memory-efficient streaming for large files
   - Content fingerprinting and duplicate detection
   - Advanced error handling and recovery mechanisms

9. **Validation Adapters** - Enterprise testing and quality assurance
   - Comprehensive import verification
   - Functional testing of core capabilities
   - Security validation and vulnerability scanning
   - Performance benchmarking and optimization
   - Compatibility testing across environments
   - Memory leak detection and resource management
   - Integration testing with external services
   - Load testing and stress testing capabilities

Enterprise Features:
- **Security**: End-to-end encryption, secure authentication, audit logging
- **Performance**: Async/await optimization, connection pooling, intelligent caching
- **Scalability**: Horizontal scaling, load balancing, distributed processing
- **Reliability**: Circuit breakers, retry logic, failover mechanisms
- **Monitoring**: Real-time metrics, performance tracking, health checks
- **Compliance**: SOC2, GDPR, HIPAA compliance ready

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import logging
from typing import Dict, List, Optional, Any, Type, Union
from enum import Enum
import importlib
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class AdapterType(Enum):
    """Supported adapter types."""
    CONTENT = "content"
    PLATFORM = "platform" 
    API = "api"
    STORAGE = "storage"
    DATA = "data"
    PROTOCOL = "protocol"
    AUTHENTICATION = "authentication"
    FORMAT = "format"
    VALIDATION = "validation"

@dataclass
class AdapterInfo:
    """Adapter information container."""
    name: str
    adapter_type: AdapterType
    description: str
    supported_formats: List[str]
    requires_auth: bool = False
    enterprise_features: List[str] = None
    dependencies: List[str] = None

class AdapterManager:
    """Central manager for all adapter types."""
    
    def __init__(self):
        """Initialize the adapter manager."""
        self._adapters: Dict[str, Type] = {}
        self._adapter_info: Dict[str, AdapterInfo] = {}
        self._initialized = False
        
    def initialize(self):
        """Initialize all available adapters."""
        if self._initialized:
            return
            
        logger.info("Initializing enterprise adapter system...")
        
        # Register content adapters
        self._register_content_adapters()
        
        # Register platform adapters
        self._register_platform_adapters()
        
        # Register API adapters
        self._register_api_adapters()
        
        # Register storage adapters
        self._register_storage_adapters()
        
        # Register data adapters
        self._register_data_adapters()
        
        # Register protocol adapters
        self._register_protocol_adapters()
        
        # Register authentication adapters
        self._register_authentication_adapters()
        
        # Register format adapters
        self._register_format_adapters()
        
        self._initialized = True
        logger.info(f"✅ Adapter system initialized with {len(self._adapters)} adapters")
    
    def _register_content_adapters(self):
        """Register content processing adapters."""
        content_adapters = [
            AdapterInfo(
                name="audio_content",
                adapter_type=AdapterType.CONTENT,
                description="Advanced audio processing with fingerprinting",
                supported_formats=["mp3", "wav", "flac", "aac", "ogg", "m4a"],
                enterprise_features=["chromaprint", "mfcc_analysis", "spectral_features"]
            ),
            AdapterInfo(
                name="video_content", 
                adapter_type=AdapterType.CONTENT,
                description="Professional video processing and analysis",
                supported_formats=["mp4", "avi", "mov", "webm", "mkv", "flv"],
                enterprise_features=["frame_extraction", "object_detection", "scene_analysis"]
            ),
            AdapterInfo(
                name="image_content",
                adapter_type=AdapterType.CONTENT, 
                description="Image processing with perceptual hashing",
                supported_formats=["jpg", "png", "webp", "bmp", "tiff", "svg"],
                enterprise_features=["perceptual_hash", "face_detection", "ocr"]
            ),
            AdapterInfo(
                name="text_content",
                adapter_type=AdapterType.CONTENT,
                description="NLP and text analysis capabilities", 
                supported_formats=["txt", "md", "rtf", "html"],
                enterprise_features=["sentiment_analysis", "entity_extraction", "language_detection"]
            ),
            AdapterInfo(
                name="document_content",
                adapter_type=AdapterType.CONTENT,
                description="Document processing and OCR",
                supported_formats=["pdf", "docx", "xlsx", "pptx", "odt"],
                enterprise_features=["ocr", "metadata_extraction", "text_extraction"]
            )
        ]
        
        for adapter_info in content_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_platform_adapters(self):
        """Register social media platform adapters."""
        platform_adapters = [
            AdapterInfo(
                name="youtube",
                adapter_type=AdapterType.PLATFORM,
                description="YouTube API integration with analytics",
                supported_formats=["video", "audio", "metadata"],
                requires_auth=True,
                enterprise_features=["content_id", "analytics", "monetization"]
            ),
            AdapterInfo(
                name="spotify",
                adapter_type=AdapterType.PLATFORM, 
                description="Spotify API with creator tools",
                supported_formats=["audio", "metadata"],
                requires_auth=True,
                enterprise_features=["track_analysis", "playlist_management", "royalties"]
            ),
            AdapterInfo(
                name="instagram",
                adapter_type=AdapterType.PLATFORM,
                description="Instagram content crawling and API",
                supported_formats=["image", "video", "story"],
                requires_auth=True,
                enterprise_features=["hashtag_analysis", "engagement_metrics", "content_discovery"]
            ),
            AdapterInfo(
                name="tiktok",
                adapter_type=AdapterType.PLATFORM,
                description="TikTok content extraction and trends",
                supported_formats=["video", "audio", "metadata"],
                requires_auth=True,
                enterprise_features=["trend_analysis", "hashtag_tracking", "viral_prediction"]
            ),
            AdapterInfo(
                name="twitter",
                adapter_type=AdapterType.PLATFORM,
                description="Twitter/X API v2 with real-time streaming",
                supported_formats=["text", "image", "video"],
                requires_auth=True, 
                enterprise_features=["real_time_streaming", "sentiment_tracking", "viral_detection"]
            )
        ]
        
        for adapter_info in platform_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_api_adapters(self):
        """Register API communication adapters."""
        api_adapters = [
            AdapterInfo(
                name="rest_api",
                adapter_type=AdapterType.API,
                description="REST API with advanced features",
                supported_formats=["json", "xml", "form"],
                enterprise_features=["pagination", "rate_limiting", "retry_logic"]
            ),
            AdapterInfo(
                name="graphql",
                adapter_type=AdapterType.API,
                description="GraphQL with query optimization",
                supported_formats=["json"],
                enterprise_features=["query_optimization", "caching", "introspection"]
            ),
            AdapterInfo(
                name="websocket",
                adapter_type=AdapterType.API,
                description="Real-time WebSocket communication",
                supported_formats=["json", "binary"],
                enterprise_features=["multiplexing", "heartbeat", "reconnection"]
            )
        ]
        
        for adapter_info in api_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_storage_adapters(self):
        """Register storage system adapters."""
        storage_adapters = [
            AdapterInfo(
                name="postgresql",
                adapter_type=AdapterType.STORAGE,
                description="PostgreSQL with vector extensions",
                supported_formats=["sql", "jsonb", "vector"],
                enterprise_features=["vector_similarity", "full_text_search", "partitioning"]
            ),
            AdapterInfo(
                name="redis",
                adapter_type=AdapterType.STORAGE,
                description="High-performance caching and sessions",
                supported_formats=["string", "hash", "list", "set"],
                enterprise_features=["clustering", "persistence", "pub_sub"]
            ),
            AdapterInfo(
                name="s3_storage",
                adapter_type=AdapterType.STORAGE,
                description="AWS S3 and MinIO object storage",
                supported_formats=["binary", "any"],
                enterprise_features=["versioning", "encryption", "lifecycle_management"]
            ),
            AdapterInfo(
                name="elasticsearch",
                adapter_type=AdapterType.STORAGE,
                description="Full-text search and analytics",
                supported_formats=["json", "text"],
                enterprise_features=["full_text_search", "aggregations", "machine_learning"]
            )
        ]
        
        for adapter_info in storage_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_data_adapters(self):
        """Register data format adapters."""
        data_adapters = [
            AdapterInfo(
                name="json",
                adapter_type=AdapterType.DATA,
                description="JSON with schema validation",
                supported_formats=["json", "jsonl"],
                enterprise_features=["schema_validation", "streaming", "compression"]
            ),
            AdapterInfo(
                name="xml",
                adapter_type=AdapterType.DATA,
                description="XML with XPath and namespaces",
                supported_formats=["xml", "xhtml"],
                enterprise_features=["xpath_queries", "namespace_support", "validation"]
            ),
            AdapterInfo(
                name="csv",
                adapter_type=AdapterType.DATA,
                description="CSV with auto-detection and streaming",
                supported_formats=["csv", "tsv"],
                enterprise_features=["auto_detection", "streaming", "large_file_support"]
            ),
            AdapterInfo(
                name="parquet",
                adapter_type=AdapterType.DATA,
                description="Columnar analytics data format",
                supported_formats=["parquet"],
                enterprise_features=["columnar_storage", "compression", "metadata"]
            )
        ]
        
        for adapter_info in data_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_protocol_adapters(self):
        """Register network protocol adapters."""
        protocol_adapters = [
            AdapterInfo(
                name="http",
                adapter_type=AdapterType.PROTOCOL,
                description="HTTP/1.1, HTTP/2, HTTP/3 support",
                supported_formats=["any"],
                enterprise_features=["http2", "http3", "compression", "ssl_tls"]
            ),
            AdapterInfo(
                name="websocket_protocol",
                adapter_type=AdapterType.PROTOCOL,
                description="WebSocket with advanced features",
                supported_formats=["text", "binary"],
                enterprise_features=["multiplexing", "compression", "extensions"]
            ),
            AdapterInfo(
                name="ftp",
                adapter_type=AdapterType.PROTOCOL,
                description="FTP and SFTP file transfer",
                supported_formats=["any"],
                enterprise_features=["sftp", "ssl_tls", "resume", "parallel_transfer"]
            )
        ]
        
        for adapter_info in protocol_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_authentication_adapters(self):
        """Register authentication and security adapters."""
        auth_adapters = [
            AdapterInfo(
                name="oauth2",
                adapter_type=AdapterType.AUTHENTICATION,
                description="OAuth2 2.0/2.1 with PKCE",
                supported_formats=["json"],
                enterprise_features=["pkce", "refresh_tokens", "token_rotation"]
            ),
            AdapterInfo(
                name="jwt",
                adapter_type=AdapterType.AUTHENTICATION,
                description="JWT with multiple algorithms",
                supported_formats=["jwt"],
                enterprise_features=["rs256", "es256", "custom_claims", "validation"]
            ),
            AdapterInfo(
                name="mfa",
                adapter_type=AdapterType.AUTHENTICATION,
                description="Multi-Factor Authentication",
                supported_formats=["totp", "sms", "email"],
                enterprise_features=["totp", "sms", "email", "hardware_keys", "webauthn"]
            )
        ]
        
        for adapter_info in auth_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def _register_format_adapters(self):
        """Register format processing adapters."""
        format_adapters = [
            AdapterInfo(
                name="compression",
                adapter_type=AdapterType.FORMAT,
                description="Advanced compression algorithms",
                supported_formats=["any"],
                enterprise_features=["gzip", "brotli", "lz4", "zstd", "snappy"]
            ),
            AdapterInfo(
                name="encryption",
                adapter_type=AdapterType.FORMAT,
                description="Enterprise-grade encryption",
                supported_formats=["any"],
                enterprise_features=["aes256", "rsa4096", "chacha20", "fernet"]
            ),
            AdapterInfo(
                name="media_transcoding",
                adapter_type=AdapterType.FORMAT,
                description="Professional media transcoding",
                supported_formats=["audio", "video", "image"],
                enterprise_features=["ffmpeg", "quality_control", "batch_processing"]
            )
        ]
        
        for adapter_info in format_adapters:
            self._adapter_info[adapter_info.name] = adapter_info
    
    def get_adapter(self, name: str) -> Optional[Type]:
        """Get adapter class by name."""
        if not self._initialized:
            self.initialize()
        return self._adapters.get(name)
    
    def get_adapters_by_type(self, adapter_type: AdapterType) -> List[str]:
        """Get all adapters of a specific type."""
        if not self._initialized:
            self.initialize()
        return [
            name for name, info in self._adapter_info.items()
            if info.adapter_type == adapter_type
        ]
    
    def get_adapter_info(self, name: str) -> Optional[AdapterInfo]:
        """Get adapter information."""
        if not self._initialized:
            self.initialize()
        return self._adapter_info.get(name)
    
    def list_all_adapters(self) -> Dict[str, AdapterInfo]:
        """List all available adapters."""
        if not self._initialized:
            self.initialize()
        return self._adapter_info.copy()

# Global adapter manager instance
adapter_manager = AdapterManager()

def get_available_adapters() -> List[str]:
    """Get list of all available adapter names."""
    adapter_manager.initialize()
    return list(adapter_manager.list_all_adapters().keys())

def get_adapter_by_name(name: str) -> Optional[Type]:
    """Get adapter class by name."""
    return adapter_manager.get_adapter(name)

def get_adapters_by_type(adapter_type: AdapterType) -> List[str]:
    """Get adapters of specific type."""
    return adapter_manager.get_adapters_by_type(adapter_type)

# Export main components
__all__ = [
    'AdapterManager',
    'AdapterType', 
    'AdapterInfo',
    'adapter_manager',
    'get_available_adapters',
    'get_adapter_by_name',
    'get_adapters_by_type'
]

6. **Protocol Adapters** - Network communication protocols
   - HTTP/HTTPS with connection pooling
   - WebSocket with auto-reconnection
   - FTP/SFTP for file transfer
   - TCP/UDP for low-level communication
   - MQTT for IoT messaging
   - gRPC for high-performance RPC
   - CoAP for constrained environments

7. **Authentication Adapters** - Security and access control
   - OAuth2 with PKCE and refresh tokens
   - JWT with signature validation
   - API key management and rotation
   - Basic authentication with secure storage
   - Certificate-based authentication
   - Multi-factor authentication (MFA)
   - Single Sign-On (SSO) integration

8. **Format Adapters** - Content format conversion and optimization
   - Media transcoding (FFmpeg, PIL)
   - Compression algorithms (GZIP, BZIP2, LZMA, Brotli, LZ4, Zstandard)
   - Encryption (AES, RSA, Fernet, ChaCha20)
   - Format validation and sanitization
   - Metadata extraction and preservation
   - Quality optimization and lossy compression

Enterprise Features:
- **High Performance**: Async/await architecture with connection pooling
- **Scalability**: Horizontal scaling with load balancing
- **Security**: Enterprise-grade encryption and authentication
- **Monitoring**: Real-time metrics and performance tracking
- **Resilience**: Circuit breaker pattern and auto-retry logic
- **Caching**: Multi-level caching for optimal performance
- **Rate Limiting**: Intelligent throttling and backpressure
- **Error Handling**: Comprehensive error recovery and logging

Business Logic Integration:
The adapter system supports the complete IA-Influencer business flow:
Content Creator → Multi-format Upload → AI Processing → Rights Protection → 
SEO Optimization → Collaboration Matching → Multi-platform Distribution → Monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type
from dataclasses import dataclass
from datetime import datetime
import json
from abc import ABC, abstractmethod

# Import all content adapters
from .content_adapters import (
    # Base classes
    ContentAdapter,
    ContentConfig,
    ContentResult,
    ContentMetrics,
    
    # Specialized adapters
    AudioContentAdapter,
    VideoContentAdapter,
    ImageContentAdapter,
    TextContentAdapter,
    DocumentAdapter,
    
    # Advanced features
    ContentAnalyzer,
    FingerprintGenerator,
    QualityAnalyzer,
    MetadataExtractor,
    
    # Factory
    ContentAdapterFactory
)

# Import all platform adapters
from .platform_adapters import (
    # Base classes
    PlatformAdapter,
    PlatformCredentials,
    ContentItem,
    PlatformConfig,
    PlatformResponse,
    
    # Social media platforms
    YouTubeAdapter,
    SpotifyAdapter,
    InstagramAdapter,
    TikTokAdapter,
    TwitterAdapter,
    FacebookAdapter,
    LinkedInAdapter,
    
    # Streaming platforms
    TwitchAdapter,
    SoundCloudAdapter,
    VimeoAdapter,
    
    # Professional platforms
    BehanceAdapter,
    DribbbleAdapter,
    GitHubAdapter,
    
    # Factory and utilities
    PlatformAdapterFactory,
    PlatformMetrics
)

# Import all API adapters
from .api_adapters import (
    # Base classes
    APIAdapter,
    APIConfig,
    APIResponse,
    APIMetrics,
    
    # Protocol adapters
    RESTAPIAdapter,
    GraphQLAdapter,
    WebSocketAdapter,
    WebhookAdapter,
    StreamingAdapter,
    
    # Advanced features
    RateLimiter,
    CircuitBreaker,
    RetryHandler,
    
    # Factory
    APIAdapterFactory
)

# Import all storage adapters
from .storage_adapters import (
    # Base classes
    StorageAdapter,
    StorageConfig,
    StorageResult,
    StorageMetrics,
    
    # Database adapters
    DatabaseAdapter,
    PostgreSQLAdapter,
    RedisAdapter,
    ElasticsearchAdapter,
    
    # File storage adapters
    FileSystemAdapter,
    CloudStorageAdapter,
    S3Adapter,
    MinIOAdapter,
    
    # Vector storage
    VectorStoreAdapter,
    FAISSAdapter,
    PineconeAdapter,
    
    # Cache adapters
    CacheAdapter,
    MemcachedAdapter,
    
    # Factory
    StorageAdapterFactory
)

# Import all data adapters
from .data_adapters import (
    # Base classes
    DataAdapter,
    DataFormatConfig,
    ProcessingResult,
    DataProcessingMetrics,
    CompressionType,
    EncryptionType,
    
    # Format adapters
    JSONAdapter,
    XMLAdapter,
    CSVAdapter,
    BinaryAdapter,
    ProtocolBufferAdapter,
    MessagePackAdapter,
    YAMLAdapter,
    TOMLAdapter,
    ParquetAdapter,
    AvroAdapter,
    
    # Factory
    DataAdapterFactory
)

# Import all protocol adapters
from .protocol_adapters import (
    # Base classes
    ProtocolAdapter,
    ProtocolConfig,
    ProtocolResponse,
    ProtocolType,
    AuthenticationType,
    ConnectionMetrics,
    
    # Network protocols
    HTTPAdapter,
    HTTPSAdapter,
    WebSocketProtocolAdapter,
    FTPAdapter,
    SFTPAdapter,
    TCPAdapter,
    UDPAdapter,
    
    # Messaging protocols
    MQTTAdapter,
    gRPCAdapter,
    CoAPAdapter,
    
    # Enterprise features
    CircuitBreaker,
    RateLimiter,
    
    # Factory
    ProtocolAdapterFactory
)

# Import all authentication adapters
from .authentication_adapters import (
    # Base classes
    AuthenticationAdapter,
    AuthConfig,
    AuthResult,
    AuthMetrics,
    
    # Authentication methods
    OAuth2Adapter,
    JWTAdapter,
    APIKeyAdapter,
    BasicAuthAdapter,
    CertificateAdapter,
    
    # Advanced auth
    MFAAdapter,
    SSOAdapter,
    SAMLAdapter,
    
    # Security features
    TokenManager,
    SessionManager,
    SecurityValidator,
    
    # Factory
    AuthAdapterFactory
)

# Import all format adapters
from .format_adapters import (
    # Base classes
    FormatAdapter,
    FormatConfig,
    FormatResult,
    FormatType,
    ProcessingMetrics,
    CompressionAlgorithm,
    EncryptionAlgorithm,
    
    # Specialized adapters
    ImageFormatAdapter,
    AudioFormatAdapter,
    VideoFormatAdapter,
    DocumentFormatAdapter,
    ArchiveAdapter,
    
    # Utilities
    FormatDetector,
    FormatConverter,
    QualityOptimizer,
    
    # Factory
    FormatAdapterFactory
)

# Define adapter manager for centralized control
@dataclass
class AdapterManagerConfig:
    """Configuration for the adapter manager."""
    enable_metrics: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600
    max_concurrent_operations: int = 100
    default_timeout: float = 30.0
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True

class AdapterManager:
    """Enterprise adapter manager for centralized control and monitoring."""
    
    def __init__(self, config: Optional[AdapterManagerConfig] = None):
        """Initialize adapter manager."""
        self.config = config or AdapterManagerConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Adapter registries
        self._content_adapters: Dict[str, ContentAdapter] = {}
        self._platform_adapters: Dict[str, PlatformAdapter] = {}
        self._api_adapters: Dict[str, APIAdapter] = {}
        self._storage_adapters: Dict[str, StorageAdapter] = {}
        self._data_adapters: Dict[str, DataAdapter] = {}
        self._protocol_adapters: Dict[str, ProtocolAdapter] = {}
        self._auth_adapters: Dict[str, AuthenticationAdapter] = {}
        self._format_adapters: Dict[str, FormatAdapter] = {}
        
        # Metrics tracking
        self._metrics: Dict[str, Any] = {}
        self._performance_stats: Dict[str, List[float]] = {}
        
    async def register_adapter(self, adapter_type: str, name: str, adapter: Any):
        """Register an adapter with the manager."""
        registry = getattr(self, f'_{adapter_type}_adapters', None)
        if registry is not None:
            registry[name] = adapter
            self.logger.info(f"Registered {adapter_type} adapter: {name}")
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    async def get_adapter(self, adapter_type: str, name: str) -> Optional[Any]:
        """Get an adapter by type and name."""
        registry = getattr(self, f'_{adapter_type}_adapters', None)
        if registry is not None:
            return registry.get(name)
        return None
    
    async def initialize_all(self):
        """Initialize all registered adapters."""
        for adapter_type in ['content', 'platform', 'api', 'storage', 'data', 'protocol', 'auth', 'format']:
            registry = getattr(self, f'_{adapter_type}_adapters')
            for name, adapter in registry.items():
                try:
                    if hasattr(adapter, 'initialize'):
                        await adapter.initialize()
                    self.logger.info(f"Initialized {adapter_type} adapter: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {adapter_type} adapter {name}: {e}")
    
    async def shutdown_all(self):
        """Shutdown all registered adapters."""
        for adapter_type in ['content', 'platform', 'api', 'storage', 'data', 'protocol', 'auth', 'format']:
            registry = getattr(self, f'_{adapter_type}_adapters')
            for name, adapter in registry.items():
                try:
                    if hasattr(adapter, 'disconnect'):
                        await adapter.disconnect()
                    elif hasattr(adapter, 'shutdown'):
                        await adapter.shutdown()
                    self.logger.info(f"Shutdown {adapter_type} adapter: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to shutdown {adapter_type} adapter {name}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all adapters."""
        metrics = {
            'adapter_counts': {
                'content': len(self._content_adapters),
                'platform': len(self._platform_adapters),
                'api': len(self._api_adapters),
                'storage': len(self._storage_adapters),
                'data': len(self._data_adapters),
                'protocol': len(self._protocol_adapters),
                'auth': len(self._auth_adapters),
                'format': len(self._format_adapters),
            },
            'performance': self._performance_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # Collect metrics from individual adapters
        for adapter_type in ['content', 'platform', 'api', 'storage', 'data', 'protocol', 'auth', 'format']:
            registry = getattr(self, f'_{adapter_type}_adapters')
            adapter_metrics = {}
            for name, adapter in registry.items():
                if hasattr(adapter, 'get_metrics'):
                    try:
                        adapter_metrics[name] = adapter.get_metrics()
                    except Exception as e:
                        self.logger.error(f"Failed to get metrics from {name}: {e}")
            metrics[f'{adapter_type}_metrics'] = adapter_metrics
        
        return metrics

# Create global adapter manager instance
adapter_manager = AdapterManager()

# Utility functions for adapter discovery and management
def get_available_adapters() -> Dict[str, List[str]]:
    """Get list of all available adapters by category."""
    return {
        'content': ['audio', 'video', 'image', 'text', 'document'],
        'platform': ['youtube', 'spotify', 'instagram', 'tiktok', 'twitter', 'facebook', 'linkedin'],
        'api': ['rest', 'graphql', 'websocket', 'webhook', 'streaming'],
        'storage': ['database', 'filesystem', 'cloud', 'cache', 'vector'],
        'data': ['json', 'xml', 'csv', 'binary', 'protobuf', 'msgpack', 'yaml', 'toml', 'parquet', 'avro'],
        'protocol': ['http', 'https', 'websocket', 'ftp', 'sftp', 'tcp', 'udp', 'mqtt', 'grpc'],
        'auth': ['oauth2', 'jwt', 'apikey', 'basic', 'certificate', 'mfa', 'sso'],
        'format': ['image', 'audio', 'video', 'document', 'archive']
    }

def create_adapter_from_config(adapter_type: str, adapter_name: str, config: Dict[str, Any]) -> Any:
    """Create an adapter instance from configuration."""
    factories = {
        'content': ContentAdapterFactory,
        'platform': PlatformAdapterFactory,
        'api': APIAdapterFactory,
        'storage': StorageAdapterFactory,
        'data': DataAdapterFactory,
        'protocol': ProtocolAdapterFactory,
        'auth': AuthAdapterFactory,
        'format': FormatAdapterFactory
    }
    
    factory = factories.get(adapter_type)
    if not factory:
        raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    return factory.create_adapter(adapter_name, config)

# Export all adapter classes and utilities
__all__ = [
    # Manager and utilities
    'AdapterManager',
    'AdapterManagerConfig',
    'adapter_manager',
    'get_available_adapters',
    'create_adapter_from_config',
    
    # Content adapters
    'ContentAdapter',
    'ContentConfig',
    'ContentResult',
    'AudioContentAdapter',
    'VideoContentAdapter',
    'ImageContentAdapter',
    'TextContentAdapter',
    'DocumentAdapter',
    'ContentAdapterFactory',
    
    # Platform adapters
    'PlatformAdapter',
    'PlatformCredentials',
    'ContentItem',
    'YouTubeAdapter',
    'SpotifyAdapter',
    'InstagramAdapter',
    'TikTokAdapter',
    'TwitterAdapter',
    'FacebookAdapter',
    'LinkedInAdapter',
    'PlatformAdapterFactory',
    
    # API adapters
    'APIAdapter',
    'APIConfig',
    'APIResponse',
    'RESTAPIAdapter',
    'GraphQLAdapter',
    'WebSocketAdapter',
    'WebhookAdapter',
    'StreamingAdapter',
    'APIAdapterFactory',
    
    # Storage adapters
    'StorageAdapter',
    'StorageConfig',
    'DatabaseAdapter',
    'FileSystemAdapter',
    'CloudStorageAdapter',
    'CacheAdapter',
    'VectorStoreAdapter',
    'StorageAdapterFactory',
    
    # Data adapters
    'DataAdapter',
    'DataFormatConfig',
    'JSONAdapter',
    'XMLAdapter',
    'CSVAdapter',
    'BinaryAdapter',
    'ProtocolBufferAdapter',
    'MessagePackAdapter',
    'YAMLAdapter',
    'TOMLAdapter',
    'ParquetAdapter',
    'AvroAdapter',
    'DataAdapterFactory',
    
    # Protocol adapters
    'ProtocolAdapter',
    'ProtocolConfig',
    'ProtocolResponse',
    'HTTPAdapter',
    'WebSocketProtocolAdapter',
    'FTPAdapter',
    'SFTPAdapter',
    'TCPAdapter',
    'UDPAdapter',
    'ProtocolAdapterFactory',
    
    # Authentication adapters
    'AuthenticationAdapter',
    'AuthConfig',
    'OAuth2Adapter',
    'JWTAdapter',
    'APIKeyAdapter',
    'BasicAuthAdapter',
    'CertificateAdapter',
    'AuthAdapterFactory',
    
    # Format adapters
    'FormatAdapter',
    'FormatConfig',
    'FormatResult',
    'ImageFormatAdapter',
    'AudioFormatAdapter',
    'VideoFormatAdapter',
    'DocumentFormatAdapter',
    'FormatAdapterFactory',
    
    # Common enums and types
    'ProtocolType',
    'AuthenticationType',
    'CompressionType',
    'EncryptionType',
    'CompressionAlgorithm',
    'EncryptionAlgorithm',
    'FormatType'
]
from .data_adapters import (
    JSONAdapter, XMLAdapter, CSVAdapter, BinaryAdapter,
    ProtocolBufferAdapter, MessagePackAdapter
)
from .protocol_adapters import (
    HTTPAdapter, HTTPSAdapter, WebSocketSecureAdapter,
    FTPAdapter, SFTPAdapter, TCPAdapter
)
from .authentication_adapters import (
    OAuth2Adapter, JWTAdapter, APIKeyAdapter,
    BasicAuthAdapter, CertificateAdapter, AuthenticationManager
)
from .format_adapters import (
    MediaFormatAdapter, CompressionAdapter, EncryptionAdapter,
    SerializationAdapter, ValidationAdapter
)
from .protocol_adapters import (
    HTTPAdapter, HTTPSAdapter, WebSocketSecureAdapter,
    FTPAdapter, SFTPAdapter, TCPAdapter
)
from .authentication_adapters import (
    OAuth2Adapter, JWTAdapter, APIKeyAdapter, 
    BasicAuthAdapter, CertificateAdapter
)
from .format_adapters import (
    MediaFormatAdapter, CompressionAdapter, EncryptionAdapter,
    SerializationAdapter, ValidationAdapter
)

logger = logging.getLogger(__name__)

@dataclass
class AdapterConfig:
    """Configuration for adapter system."""
    max_concurrent_adapters: int = 100
    default_timeout: float = 30.0
    enable_caching: bool = True
    enable_retry: bool = True
    max_retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"

class AdapterRegistry:
    """Central registry for all adapter types."""
    
    def __init__(self):
        """Initialize adapter registry."""
        self._content_adapters: Dict[str, Type] = {}
        self._platform_adapters: Dict[str, Type] = {}
        self._api_adapters: Dict[str, Type] = {}
        self._storage_adapters: Dict[str, Type] = {}
        self._data_adapters: Dict[str, Type] = {}
        self._protocol_adapters: Dict[str, Type] = {}
        self._auth_adapters: Dict[str, Type] = {}
        self._format_adapters: Dict[str, Type] = {}
        
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """Register all default adapters."""
        # Content adapters
        self._content_adapters.update({
            'audio': AudioContentAdapter,
            'video': VideoContentAdapter,
            'image': ImageContentAdapter,
            'text': TextContentAdapter,
            'document': DocumentAdapter
        })
        
        # Platform adapters
        self._platform_adapters.update({
            'youtube': YouTubeAdapter,
            'spotify': SpotifyAdapter,
            'instagram': InstagramAdapter,
            'tiktok': TikTokAdapter,
            'twitter': TwitterAdapter,
            'facebook': FacebookAdapter,
            'linkedin': LinkedInAdapter
        })
        
        # API adapters
        self._api_adapters.update({
            'rest': RESTAPIAdapter,
            'graphql': GraphQLAdapter,
            'websocket': WebSocketAdapter,
            'webhook': WebhookAdapter,
            'streaming': StreamingAdapter
        })
        
        # Storage adapters
        self._storage_adapters.update({
            'database': DatabaseAdapter,
            'filesystem': FileSystemAdapter,
            'cloud': CloudStorageAdapter,
            'cache': CacheAdapter,
            'vector': VectorStoreAdapter
        })
        
        # Data adapters
        self._data_adapters.update({
            'json': JSONAdapter,
            'xml': XMLAdapter,
            'csv': CSVAdapter,
            'binary': BinaryAdapter,
            'protobuf': ProtocolBufferAdapter,
            'msgpack': MessagePackAdapter
        })
        
        # Protocol adapters
        self._protocol_adapters.update({
            'http': HTTPAdapter,
            'https': HTTPSAdapter,
            'wss': WebSocketSecureAdapter,
            'ftp': FTPAdapter,
            'sftp': SFTPAdapter,
            'tcp': TCPAdapter
        })
        
        # Authentication adapters
        self._auth_adapters.update({
            'oauth2': OAuth2Adapter,
            'jwt': JWTAdapter,
            'apikey': APIKeyAdapter,
            'basic': BasicAuthAdapter,
            'certificate': CertificateAdapter
        })
        
        # Format adapters
        self._format_adapters.update({
            'media': MediaFormatAdapter,
            'compression': CompressionAdapter,
            'encryption': EncryptionAdapter,
            'serialization': SerializationAdapter,
            'validation': ValidationAdapter
        })
    
    def get_content_adapter(self, content_type: str) -> Optional[Type]:
        """Get content adapter by type."""
        return self._content_adapters.get(content_type.lower())
    
    def get_platform_adapter(self, platform: str) -> Optional[Type]:
        """Get platform adapter by name."""
        return self._platform_adapters.get(platform.lower())
    
    def get_api_adapter(self, api_type: str) -> Optional[Type]:
        """Get API adapter by type."""
        return self._api_adapters.get(api_type.lower())
    
    def get_storage_adapter(self, storage_type: str) -> Optional[Type]:
        """Get storage adapter by type."""
        return self._storage_adapters.get(storage_type.lower())
    
    def get_data_adapter(self, data_format: str) -> Optional[Type]:
        """Get data adapter by format."""
        return self._data_adapters.get(data_format.lower())
    
    def get_protocol_adapter(self, protocol: str) -> Optional[Type]:
        """Get protocol adapter by name."""
        return self._protocol_adapters.get(protocol.lower())
    
    def get_auth_adapter(self, auth_type: str) -> Optional[Type]:
        """Get authentication adapter by type."""
        return self._auth_adapters.get(auth_type.lower())
    
    def get_format_adapter(self, format_type: str) -> Optional[Type]:
        """Get format adapter by type."""
        return self._format_adapters.get(format_type.lower())
    
    def register_adapter(
        self,
        category: str,
        name: str,
        adapter_class: Type
    ) -> bool:
        """Register custom adapter."""
        try:
            registry = getattr(self, f"_{category}_adapters", None)
            if registry is None:
                logger.error(f"Unknown adapter category: {category}")
                return False
            
            registry[name.lower()] = adapter_class
            logger.info(f"Registered custom adapter: {category}.{name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register adapter {category}.{name}: {e}")
            return False
    
    def list_adapters(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """List all available adapters."""
        if category:
            registry = getattr(self, f"_{category}_adapters", {})
            return {category: list(registry.keys())}
        
        return {
            'content': list(self._content_adapters.keys()),
            'platform': list(self._platform_adapters.keys()),
            'api': list(self._api_adapters.keys()),
            'storage': list(self._storage_adapters.keys()),
            'data': list(self._data_adapters.keys()),
            'protocol': list(self._protocol_adapters.keys()),
            'auth': list(self._auth_adapters.keys()),
            'format': list(self._format_adapters.keys())
        }

class AdapterManager:
    """
    Central adapter management system.
    
    Coordinates all adapter operations including initialization,
    configuration, lifecycle management, and performance monitoring.
    """
    
    def __init__(self, config: Optional[AdapterConfig] = None):
        """Initialize adapter manager."""
        self.config = config or AdapterConfig()
        
        # Setup logging
        logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        # Initialize registry
        self.registry = AdapterRegistry()
        
        # Active adapter instances
        self._active_adapters: Dict[str, Any] = {}
        
        # Performance metrics
        self._metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'total_adapters_created': 0,
            'active_adapters_count': 0
        }
        
        logger.info("Adapter manager initialized successfully")
    
    async def create_adapter(
        self,
        category: str,
        adapter_type: str,
        config: Optional[Dict[str, Any]] = None,
        instance_id: Optional[str] = None
    ) -> Optional[Any]:
        """Create and configure adapter instance."""
        try:
            # Get adapter class from registry
            adapter_class = None
            
            if category == 'content':
                adapter_class = self.registry.get_content_adapter(adapter_type)
            elif category == 'platform':
                adapter_class = self.registry.get_platform_adapter(adapter_type)
            elif category == 'api':
                adapter_class = self.registry.get_api_adapter(adapter_type)
            elif category == 'storage':
                adapter_class = self.registry.get_storage_adapter(adapter_type)
            elif category == 'data':
                adapter_class = self.registry.get_data_adapter(adapter_type)
            elif category == 'protocol':
                adapter_class = self.registry.get_protocol_adapter(adapter_type)
            elif category == 'auth':
                adapter_class = self.registry.get_auth_adapter(adapter_type)
            elif category == 'format':
                adapter_class = self.registry.get_format_adapter(adapter_type)
            
            if not adapter_class:
                logger.error(f"Adapter not found: {category}.{adapter_type}")
                return None
            
            # Create adapter instance
            adapter_config = config or {}
            adapter = adapter_class(**adapter_config)
            
            # Initialize adapter if needed
            if hasattr(adapter, 'initialize'):
                await adapter.initialize()
            
            # Register active adapter
            if instance_id:
                self._active_adapters[instance_id] = adapter
            
            self._metrics['total_adapters_created'] += 1
            self._metrics['active_adapters_count'] = len(self._active_adapters)
            
            logger.info(f"Created adapter: {category}.{adapter_type}")
            return adapter
            
        except Exception as e:
            logger.error(f"Failed to create adapter {category}.{adapter_type}: {e}")
            return None
    
    async def get_adapter(self, instance_id: str) -> Optional[Any]:
        """Get active adapter by instance ID."""
        return self._active_adapters.get(instance_id)
    
    async def destroy_adapter(self, instance_id: str) -> bool:
        """Destroy adapter instance."""
        try:
            adapter = self._active_adapters.get(instance_id)
            if not adapter:
                logger.warning(f"Adapter not found: {instance_id}")
                return False
            
            # Cleanup adapter if needed
            if hasattr(adapter, 'cleanup'):
                await adapter.cleanup()
            
            # Remove from active adapters
            del self._active_adapters[instance_id]
            
            self._metrics['active_adapters_count'] = len(self._active_adapters)
            
            logger.info(f"Destroyed adapter: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy adapter {instance_id}: {e}")
            return False
    
    async def execute_adapter_operation(
        self,
        instance_id: str,
        operation: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation on adapter instance."""
        start_time = datetime.now()
        
        try:
            adapter = self._active_adapters.get(instance_id)
            if not adapter:
                raise ValueError(f"Adapter not found: {instance_id}")
            
            if not hasattr(adapter, operation):
                raise ValueError(f"Operation not supported: {operation}")
            
            method = getattr(adapter, operation)
            result = await method(*args, **kwargs)
            
            # Update metrics
            self._update_success_metrics(start_time)
            
            return result
            
        except Exception as e:
            self._update_error_metrics(start_time)
            logger.error(f"Adapter operation failed {instance_id}.{operation}: {e}")
            raise
    
    def _update_success_metrics(self, start_time: datetime):
        """Update metrics for successful operation."""
        response_time = (datetime.now() - start_time).total_seconds()
        
        self._metrics['total_requests'] += 1
        self._metrics['successful_requests'] += 1
        
        # Update average response time
        current_avg = self._metrics['avg_response_time']
        total_requests = self._metrics['total_requests']
        self._metrics['avg_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def _update_error_metrics(self, start_time: datetime):
        """Update metrics for failed operation."""
        self._metrics['total_requests'] += 1
        self._metrics['failed_requests'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get adapter system metrics."""
        return self._metrics.copy()
    
    def get_active_adapters(self) -> List[str]:
        """Get list of active adapter instance IDs."""
        return list(self._active_adapters.keys())
    
    async def shutdown(self):
        """Shutdown adapter manager and cleanup resources."""
        logger.info("Shutting down adapter manager...")
        
        # Cleanup all active adapters
        for instance_id in list(self._active_adapters.keys()):
            await self.destroy_adapter(instance_id)
        
        logger.info("Adapter manager shutdown complete")

# Global adapter manager instance
_adapter_manager = None

def get_adapter_manager(config: Optional[AdapterConfig] = None) -> AdapterManager:
    """Get global adapter manager instance."""
    global _adapter_manager
    if _adapter_manager is None:
        _adapter_manager = AdapterManager(config)
    return _adapter_manager

# Export public interface
__all__ = [
    'AdapterConfig',
    'AdapterRegistry', 
    'AdapterManager',
    'get_adapter_manager',
    # Content adapters
    'AudioContentAdapter', 'VideoContentAdapter', 'ImageContentAdapter',
    'TextContentAdapter', 'DocumentAdapter',
    # Platform adapters
    'YouTubeAdapter', 'SpotifyAdapter', 'InstagramAdapter', 'TikTokAdapter',
    'TwitterAdapter', 'FacebookAdapter', 'LinkedInAdapter',
    # API adapters
    'RESTAPIAdapter', 'GraphQLAdapter', 'WebSocketAdapter',
    'WebhookAdapter', 'StreamingAdapter',
    # Storage adapters
    'DatabaseAdapter', 'FileSystemAdapter', 'CloudStorageAdapter',
    'CacheAdapter', 'VectorStoreAdapter',
    # Data adapters
    'JSONAdapter', 'XMLAdapter', 'CSVAdapter', 'BinaryAdapter',
    'ProtocolBufferAdapter', 'MessagePackAdapter',
    # Protocol adapters
    'HTTPAdapter', 'HTTPSAdapter', 'WebSocketSecureAdapter',
    'FTPAdapter', 'SFTPAdapter', 'TCPAdapter',
    # Authentication adapters
    'OAuth2Adapter', 'JWTAdapter', 'APIKeyAdapter',
    'BasicAuthAdapter', 'CertificateAdapter',
    # Format adapters
    'MediaFormatAdapter', 'CompressionAdapter', 'EncryptionAdapter',
    'SerializationAdapter', 'ValidationAdapter'
]
