#!/usr/bin/env python3
"""
⚡ Audit Logging Template - Enterprise Security & Compliance
🏗️ Architecture: IA Chéries Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import json
import time
import hashlib
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import logging.handlers
import asyncio
import gzip
import base64
from urllib.parse import urlparse, parse_qs

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + Compliance Expert
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class AuditLevel(str, Enum):
    """Audit logging levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    FORENSIC = "forensic"


class EventType(str, Enum):
    """Audit event types"""
    REQUEST = "request"
    RESPONSE = "response"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_EVENT = "security_event"
    ERROR = "error"
    ADMIN_ACTION = "admin_action"
    CREATOR_ACTION = "creator_action"
    PAYMENT = "payment"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"


class DataClassification(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"  # Personally Identifiable Information
    PHI = "phi"  # Protected Health Information
    PAYMENT_DATA = "payment_data"


class ComplianceFramework(str, Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    SOC2 = "soc2"


@dataclass
class AuditEvent:
    """Comprehensive audit event structure"""
    # Core event data
    event_id: str
    timestamp: datetime
    event_type: EventType
    actor_id: Optional[str]
    actor_type: str  # user, system, api_client, admin
    source_ip: str
    user_agent: str
    session_id: Optional[str]
    
    # Request/Response data
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    request_body_hash: Optional[str]
    response_status: Optional[int]
    response_size: int
    duration_ms: float
    
    # Security context
    authentication_method: Optional[str]
    authorization_granted: bool
    security_events: List[str] = field(default_factory=list)
    risk_score: int = 0
    
    # Data classification
    data_classification: DataClassification = DataClassification.PUBLIC
    sensitive_data_accessed: List[str] = field(default_factory=list)
    data_retention_period: Optional[int] = None
    
    # Business context
    business_process: Optional[str] = None
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    transaction_id: Optional[str] = None
    
    # Compliance
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    gdpr_lawful_basis: Optional[str] = None
    data_subject_id: Optional[str] = None
    
    # Technical context
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    service_name: str = "ainflue-api"
    environment: str = "production"
    
    # Error information
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace_hash: Optional[str] = None
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['data_classification'] = self.data_classification.value
        data['compliance_frameworks'] = [f.value for f in self.compliance_frameworks]
        return data


@dataclass
class AuditConfig:
    """Enterprise audit logging configuration"""
    # Basic settings
    audit_level: AuditLevel = AuditLevel.STANDARD
    enable_audit_logging: bool = True
    
    # Event filtering
    log_all_requests: bool = True
    log_responses: bool = True
    log_request_bodies: bool = False  # Security consideration
    log_response_bodies: bool = False
    excluded_paths: Set[str] = field(default_factory=lambda: {"/health", "/metrics"})
    excluded_methods: Set[str] = field(default_factory=set)
    
    # Data sensitivity
    log_sensitive_data: bool = False
    sensitive_headers: Set[str] = field(default_factory=lambda: {
        "authorization", "cookie", "x-api-key", "x-auth-token"
    })
    sensitive_params: Set[str] = field(default_factory=lambda: {
        "password", "secret", "token", "key", "ssn", "credit_card"
    })
    
    # PII handling
    mask_pii: bool = True
    pii_fields: Set[str] = field(default_factory=lambda: {
        "email", "phone", "address", "name", "ssn", "passport", "license"
    })
    hash_pii: bool = True
    
    # Compliance settings
    enable_gdpr_compliance: bool = True
    enable_ccpa_compliance: bool = True
    retention_period_days: int = 2555  # 7 years default
    auto_deletion_enabled: bool = True
    
    # Storage settings
    use_structured_logging: bool = True
    compress_logs: bool = True
    encrypt_logs: bool = True
    log_rotation_size: str = "100MB"
    log_rotation_count: int = 10
    
    # Real-time features
    enable_real_time_alerts: bool = True
    enable_anomaly_detection: bool = True
    alert_on_high_risk: bool = True
    high_risk_threshold: int = 80
    
    # External integrations
    siem_integration: bool = False
    siem_endpoint: Optional[str] = None
    elasticsearch_enabled: bool = False
    elasticsearch_index: str = "audit-logs"
    
    # Creator-specific settings
    enable_creator_audit: bool = True
    log_content_operations: bool = True
    log_monetization_events: bool = True
    creator_retention_period: int = 2555  # 7 years for financial records
    
    # Performance settings
    async_logging: bool = True
    batch_size: int = 100
    flush_interval: int = 5  # seconds
    max_queue_size: int = 10000


@dataclass
class AuditMetrics:
    """Audit logging metrics"""
    total_events: int = 0
    events_logged: int = 0
    events_filtered: int = 0
    pii_events_masked: int = 0
    high_risk_events: int = 0
    compliance_events: int = 0
    errors_logged: int = 0
    queue_overflows: int = 0
    
    # Per-type metrics
    event_type_counts: Dict[str, int] = field(default_factory=dict)
    classification_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def logging_rate(self) -> float:
        if self.total_events == 0:
            return 0.0
        return (self.events_logged / self.total_events) * 100


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise Audit Logging Middleware
    
    Features:
    - Comprehensive audit trail
    - GDPR/CCPA compliance
    - PII masking and hashing
    - Real-time security monitoring
    - Anomaly detection
    - Creator-specific auditing
    - Structured logging
    - SIEM integration
    - Encrypted storage
    - Auto-retention management
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[AuditConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or AuditConfig()
        self.logger = logger or self._setup_logger()
        
        # Audit event queue for async processing
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        
        # Metrics
        self.metrics = AuditMetrics()
        
        # Risk analysis
        self.risk_patterns: Dict[str, int] = {}
        self.anomaly_baselines: Dict[str, float] = {}
        
        # Start background workers
        if self.config.async_logging:
            asyncio.create_task(self._audit_worker())
            asyncio.create_task(self._cleanup_worker())
        
        self.logger.info(f"Audit Logging initialized with level: {self.config.audit_level}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive audit logger"""
        logger = logging.getLogger("audit")
        logger.setLevel(logging.INFO)
        
        # Create formatters
        if self.config.use_structured_logging:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )
        
        # Rotating file handler
        if not logger.handlers:
            handler = logging.handlers.RotatingFileHandler(
                filename="audit.log",
                maxBytes=self._parse_size(self.config.log_rotation_size),
                backupCount=self.config.log_rotation_count
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Console handler for development
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        return int(size_str)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with comprehensive auditing"""
        start_time = time.time()
        
        try:
            self.metrics.total_events += 1
            
            # Skip audit for excluded paths
            if await self._should_skip_audit(request):
                return await call_next(request)
            
            # Generate event ID and trace context
            event_id = str(uuid.uuid4())
            trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
            
            # Extract actor information
            actor_info = await self._extract_actor_info(request)
            
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Create audit event
            event = await self._create_audit_event(
                event_id, trace_id, request, response, actor_info, duration_ms
            )
            
            # Log the event
            await self._log_audit_event(event)
            
            # Real-time analysis
            if self.config.enable_anomaly_detection:
                await self._analyze_for_anomalies(event)
            
            if self.config.enable_real_time_alerts:
                await self._check_alert_conditions(event)
            
            return response
            
        except Exception as e:
            # Log the error but don't break the request flow
            self.logger.error(f"Audit logging error: {e}")
            self.metrics.errors_logged += 1
            return await call_next(request)
    
    async def _should_skip_audit(self, request: Request) -> bool:
        """Check if request should skip auditing"""
        if not self.config.enable_audit_logging:
            return True
        
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.config.excluded_paths):
            return True
        
        # Skip excluded methods
        if request.method in self.config.excluded_methods:
            return True
        
        return False
    
    async def _extract_actor_info(self, request: Request) -> Dict[str, Any]:
        """Extract actor information from request"""
        auth_header = request.headers.get("authorization", "")
        api_key = request.headers.get("x-api-key")
        session_id = request.headers.get("x-session-id")
        
        actor_info = {
            "actor_id": None,
            "actor_type": "anonymous",
            "authentication_method": None,
            "session_id": session_id
        }
        
        # Extract from JWT token (simplified)
        if auth_header.startswith("Bearer "):
            actor_info.update({
                "actor_id": "user_from_jwt",  # Extract from actual JWT
                "actor_type": "user",
                "authentication_method": "jwt"
            })
        
        # Extract from API key
        elif api_key:
            actor_info.update({
                "actor_id": hashlib.sha256(api_key.encode()).hexdigest()[:16],
                "actor_type": "api_client",
                "authentication_method": "api_key"
            })
        
        return actor_info
    
    async def _create_audit_event(
        self,
        event_id: str,
        trace_id: str,
        request: Request,
        response: Response,
        actor_info: Dict[str, Any],
        duration_ms: float
    ) -> AuditEvent:
        """Create comprehensive audit event"""
        
        # Determine event type
        event_type = self._determine_event_type(request, response)
        
        # Extract and sanitize headers
        headers = await self._sanitize_headers(dict(request.headers))
        
        # Extract and sanitize query parameters
        query_params = await self._sanitize_query_params(dict(request.query_params))
        
        # Hash request body if needed
        request_body_hash = None
        if self.config.log_request_bodies:
            body = await request.body()
            if body:
                request_body_hash = hashlib.sha256(body).hexdigest()
        
        # Determine data classification
        data_classification = await self._classify_data(request, response)
        
        # Extract business context
        business_context = await self._extract_business_context(request, response)
        
        # Calculate risk score
        risk_score = await self._calculate_risk_score(request, response, actor_info)
        
        # Create event
        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            actor_id=actor_info.get("actor_id"),
            actor_type=actor_info.get("actor_type", "unknown"),
            source_ip=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent", ""),
            session_id=actor_info.get("session_id"),
            
            method=request.method,
            path=request.url.path,
            query_params=query_params,
            headers=headers,
            request_body_hash=request_body_hash,
            response_status=response.status_code,
            response_size=len(response.body) if hasattr(response, 'body') else 0,
            duration_ms=duration_ms,
            
            authentication_method=actor_info.get("authentication_method"),
            authorization_granted=response.status_code < 400,
            risk_score=risk_score,
            
            data_classification=data_classification,
            sensitive_data_accessed=await self._detect_sensitive_data_access(request, response),
            
            business_process=business_context.get("process"),
            creator_id=business_context.get("creator_id"),
            content_id=business_context.get("content_id"),
            transaction_id=business_context.get("transaction_id"),
            
            compliance_frameworks=await self._determine_compliance_frameworks(request),
            gdpr_lawful_basis=business_context.get("gdpr_basis"),
            data_subject_id=business_context.get("data_subject_id"),
            
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            service_name="ainflue-api",
            environment=self._get_environment(),
            
            tags=await self._generate_tags(request, response),
            custom_fields=business_context.get("custom_fields", {})
        )
        
        # Add error information if applicable
        if response.status_code >= 400:
            event.error_code = str(response.status_code)
            event.error_message = response.headers.get("x-error-message", "")
        
        return event
    
    def _determine_event_type(self, request: Request, response: Response) -> EventType:
        """Determine the type of audit event"""
        path = request.url.path.lower()
        method = request.method.upper()
        
        # Authentication events
        if "/auth/" in path:
            return EventType.AUTHENTICATION
        
        # Creator-specific events
        if "/creator/" in path or "/content/" in path:
            if method in ["POST", "PUT", "PATCH"]:
                return EventType.CREATOR_ACTION
            elif "upload" in path:
                return EventType.UPLOAD
        
        # Payment events
        if "/payment/" in path or "/billing/" in path:
            return EventType.PAYMENT
        
        # Data modification events
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            if method == "DELETE":
                return EventType.DELETE
            return EventType.DATA_MODIFICATION
        
        # Data access events
        if method == "GET":
            return EventType.DATA_ACCESS
        
        # Error events
        if response.status_code >= 400:
            return EventType.ERROR
        
        return EventType.REQUEST
    
    async def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive headers"""
        sanitized = {}
        
        for key, value in headers.items():
            key_lower = key.lower()
            
            if key_lower in self.config.sensitive_headers:
                if self.config.mask_pii:
                    sanitized[key] = self._mask_value(value)
                elif self.config.hash_pii:
                    sanitized[key] = self._hash_value(value)
                else:
                    # Skip sensitive headers entirely
                    continue
            else:
                sanitized[key] = value
        
        return sanitized
    
    async def _sanitize_query_params(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Sanitize sensitive query parameters"""
        sanitized = {}
        
        for key, value in params.items():
            key_lower = key.lower()
            
            if any(sensitive in key_lower for sensitive in self.config.sensitive_params):
                if self.config.mask_pii:
                    sanitized[key] = self._mask_value(str(value))
                elif self.config.hash_pii:
                    sanitized[key] = self._hash_value(str(value))
                # Skip if not masking/hashing
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _mask_value(self, value: str) -> str:
        """Mask sensitive value"""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    
    def _hash_value(self, value: str) -> str:
        """Hash sensitive value"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    async def _classify_data(self, request: Request, response: Response) -> DataClassification:
        """Classify data sensitivity level"""
        path = request.url.path.lower()
        
        # Payment data
        if "/payment/" in path or "/billing/" in path:
            return DataClassification.PAYMENT_DATA
        
        # PII data
        if any(pii in path for pii in ["profile", "personal", "contact"]):
            return DataClassification.PII
        
        # Confidential creator data
        if "/creator/" in path and request.method != "GET":
            return DataClassification.CONFIDENTIAL
        
        # Internal API data
        if "/admin/" in path:
            return DataClassification.RESTRICTED
        
        # Default to internal
        return DataClassification.INTERNAL
    
    async def _extract_business_context(self, request: Request, response: Response) -> Dict[str, Any]:
        """Extract business-specific context"""
        context = {}
        
        # Extract creator ID from path or headers
        creator_id = request.headers.get("x-creator-id")
        if not creator_id and "/creator/" in request.url.path:
            # Extract from URL pattern
            path_parts = request.url.path.split("/")
            if "creator" in path_parts:
                idx = path_parts.index("creator")
                if idx + 1 < len(path_parts):
                    creator_id = path_parts[idx + 1]
        
        if creator_id:
            context["creator_id"] = creator_id
            context["process"] = "creator_management"
            
            # GDPR lawful basis for creator data
            if request.method in ["POST", "PUT", "PATCH"]:
                context["gdpr_basis"] = "legitimate_interest"
            else:
                context["gdpr_basis"] = "consent"
            
            context["data_subject_id"] = creator_id
        
        # Extract content ID
        content_id = request.headers.get("x-content-id")
        if content_id:
            context["content_id"] = content_id
        
        # Extract transaction ID for payments
        transaction_id = request.headers.get("x-transaction-id")
        if transaction_id:
            context["transaction_id"] = transaction_id
            context["process"] = "payment_processing"
        
        return context
    
    async def _calculate_risk_score(
        self, 
        request: Request, 
        response: Response, 
        actor_info: Dict[str, Any]
    ) -> int:
        """Calculate risk score for the event"""
        score = 0
        
        # High risk for failed authentication
        if "/auth/" in request.url.path and response.status_code >= 400:
            score += 40
        
        # High risk for admin actions
        if "/admin/" in request.url.path:
            score += 30
        
        # Medium risk for data modification
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            score += 20
        
        # Risk based on actor type
        if actor_info.get("actor_type") == "anonymous":
            score += 15
        
        # Risk for sensitive endpoints
        sensitive_paths = ["/payment/", "/billing/", "/export/", "/backup/"]
        if any(path in request.url.path for path in sensitive_paths):
            score += 25
        
        # Risk for error responses
        if response.status_code >= 400:
            score += 10
        
        # Risk for unusual user agents
        user_agent = request.headers.get("user-agent", "").lower()
        if any(bot in user_agent for bot in ["bot", "crawler", "scanner"]):
            score += 15
        
        return min(score, 100)  # Cap at 100
    
    async def _detect_sensitive_data_access(
        self, 
        request: Request, 
        response: Response
    ) -> List[str]:
        """Detect what sensitive data was accessed"""
        sensitive_data = []
        
        path = request.url.path.lower()
        
        # PII data access
        if any(pii in path for pii in self.config.pii_fields):
            sensitive_data.append("pii")
        
        # Payment data access
        if "/payment/" in path or "/billing/" in path:
            sensitive_data.append("payment_data")
        
        # Creator content access
        if "/content/" in path:
            sensitive_data.append("creator_content")
        
        return sensitive_data
    
    async def _determine_compliance_frameworks(self, request: Request) -> List[ComplianceFramework]:
        """Determine applicable compliance frameworks"""
        frameworks = []
        
        # GDPR for EU users
        eu_headers = ["x-forwarded-for", "cf-ipcountry"]
        for header in eu_headers:
            value = request.headers.get(header, "").upper()
            if any(country in value for country in ["EU", "DE", "FR", "ES", "IT"]):
                frameworks.append(ComplianceFramework.GDPR)
                break
        
        # CCPA for California users
        if "CA" in request.headers.get("cf-region", ""):
            frameworks.append(ComplianceFramework.CCPA)
        
        # PCI DSS for payment processing
        if "/payment/" in request.url.path:
            frameworks.append(ComplianceFramework.PCI_DSS)
        
        # SOX for financial reporting
        if "/financial/" in request.url.path or "/reporting/" in request.url.path:
            frameworks.append(ComplianceFramework.SOX)
        
        return frameworks
    
    def _get_environment(self) -> str:
        """Get current environment"""
        import os
        return os.getenv("ENVIRONMENT", "production")
    
    async def _generate_tags(self, request: Request, response: Response) -> Dict[str, str]:
        """Generate contextual tags for the event"""
        tags = {}
        
        # API version
        if "/v1/" in request.url.path:
            tags["api_version"] = "v1"
        elif "/v2/" in request.url.path:
            tags["api_version"] = "v2"
        
        # Request type
        if "upload" in request.url.path:
            tags["request_type"] = "upload"
        elif "download" in request.url.path:
            tags["request_type"] = "download"
        
        # Platform
        user_agent = request.headers.get("user-agent", "").lower()
        if "mobile" in user_agent:
            tags["platform"] = "mobile"
        elif "desktop" in user_agent:
            tags["platform"] = "desktop"
        
        return tags
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _log_audit_event(self, event: AuditEvent):
        """Log audit event with appropriate handling"""
        try:
            if self.config.async_logging:
                # Add to queue for async processing
                await self.event_queue.put(event)
            else:
                # Log immediately
                await self._write_audit_log(event)
            
            self.metrics.events_logged += 1
            
            # Update type-specific metrics
            event_type = event.event_type.value
            if event_type not in self.metrics.event_type_counts:
                self.metrics.event_type_counts[event_type] = 0
            self.metrics.event_type_counts[event_type] += 1
            
            # Update classification metrics
            classification = event.data_classification.value
            if classification not in self.metrics.classification_counts:
                self.metrics.classification_counts[classification] = 0
            self.metrics.classification_counts[classification] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            self.metrics.errors_logged += 1
    
    async def _write_audit_log(self, event: AuditEvent):
        """Write audit event to storage"""
        if self.config.use_structured_logging:
            # Structured JSON logging
            log_data = event.to_dict()
            
            if self.config.encrypt_logs:
                log_data = await self._encrypt_log_data(log_data)
            
            self.logger.info(json.dumps(log_data, default=str))
        else:
            # Simple text logging
            log_message = (
                f"[{event.event_type.value}] "
                f"{event.actor_type}:{event.actor_id} "
                f"{event.method} {event.path} "
                f"-> {event.response_status} "
                f"({event.duration_ms:.2f}ms)"
            )
            self.logger.info(log_message)
        
        # Send to external systems
        if self.config.siem_integration and self.config.siem_endpoint:
            await self._send_to_siem(event)
        
        if self.config.elasticsearch_enabled:
            await self._send_to_elasticsearch(event)
    
    async def _encrypt_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive log data"""
        # Simplified encryption - use proper encryption in production
        encrypted_data = data.copy()
        
        # Encrypt specific fields
        sensitive_fields = ["actor_id", "source_ip", "headers", "query_params"]
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = base64.b64encode(
                    str(encrypted_data[field]).encode()
                ).decode()
        
        return encrypted_data
    
    async def _send_to_siem(self, event: AuditEvent):
        """Send audit event to SIEM system"""
        try:
            # Implementation would depend on your SIEM system
            # This is a placeholder
            siem_payload = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "source": "ainflue-api",
                "severity": self._calculate_siem_severity(event),
                "message": f"{event.actor_type} {event.method} {event.path}",
                "metadata": event.to_dict()
            }
            
            # Send to SIEM endpoint
            self.logger.debug(f"Sending to SIEM: {siem_payload}")
            
        except Exception as e:
            self.logger.error(f"Failed to send to SIEM: {e}")
    
    async def _send_to_elasticsearch(self, event: AuditEvent):
        """Send audit event to Elasticsearch"""
        try:
            # Implementation would use elasticsearch-py
            # This is a placeholder
            es_document = event.to_dict()
            
            self.logger.debug(f"Sending to Elasticsearch: {es_document}")
            
        except Exception as e:
            self.logger.error(f"Failed to send to Elasticsearch: {e}")
    
    def _calculate_siem_severity(self, event: AuditEvent) -> str:
        """Calculate SIEM severity level"""
        if event.risk_score >= 80:
            return "critical"
        elif event.risk_score >= 60:
            return "high"
        elif event.risk_score >= 40:
            return "medium"
        elif event.risk_score >= 20:
            return "low"
        return "info"
    
    async def _analyze_for_anomalies(self, event: AuditEvent):
        """Analyze event for anomalies"""
        # Simplified anomaly detection
        key = f"{event.actor_id}:{event.path}"
        
        if key not in self.anomaly_baselines:
            self.anomaly_baselines[key] = event.duration_ms
        else:
            baseline = self.anomaly_baselines[key]
            deviation = abs(event.duration_ms - baseline) / baseline
            
            if deviation > 3.0:  # 300% deviation
                await self._report_anomaly(event, "response_time_anomaly", deviation)
            
            # Update baseline with exponential moving average
            self.anomaly_baselines[key] = 0.9 * baseline + 0.1 * event.duration_ms
    
    async def _check_alert_conditions(self, event: AuditEvent):
        """Check if event should trigger alerts"""
        if event.risk_score >= self.config.high_risk_threshold:
            await self._send_alert("high_risk_event", event)
        
        # Alert on sensitive data access
        if event.sensitive_data_accessed and event.actor_type == "anonymous":
            await self._send_alert("anonymous_sensitive_access", event)
        
        # Alert on admin actions
        if event.event_type == EventType.ADMIN_ACTION:
            await self._send_alert("admin_action", event)
        
        # Alert on payment events with errors
        if event.event_type == EventType.PAYMENT and event.response_status >= 400:
            await self._send_alert("payment_error", event)
    
    async def _report_anomaly(self, event: AuditEvent, anomaly_type: str, deviation: float):
        """Report detected anomaly"""
        self.logger.warning(
            f"Anomaly detected: {anomaly_type} for {event.actor_id} "
            f"on {event.path} - deviation: {deviation:.2f}"
        )
        
        await self._send_alert("anomaly_detected", event, {
            "anomaly_type": anomaly_type,
            "deviation": deviation
        })
    
    async def _send_alert(self, alert_type: str, event: AuditEvent, extra_data: Optional[Dict] = None):
        """Send real-time alert"""
        alert_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_type": alert_type,
            "event_id": event.event_id,
            "risk_score": event.risk_score,
            "actor_id": event.actor_id,
            "path": event.path,
            "source_ip": event.source_ip
        }
        
        if extra_data:
            alert_data.update(extra_data)
        
        # TODO: Implement your alerting mechanism
        self.logger.error(f"ALERT: {alert_type} - {alert_data}")
    
    async def _audit_worker(self):
        """Background worker for async audit logging"""
        batch = []
        last_flush = time.time()
        
        while True:
            try:
                # Wait for events with timeout
                try:
                    event = await asyncio.wait_for(
                        self.event_queue.get(), 
                        timeout=self.config.flush_interval
                    )
                    batch.append(event)
                except asyncio.TimeoutError:
                    # Flush on timeout
                    pass
                
                # Flush if batch is full or time interval reached
                current_time = time.time()
                should_flush = (
                    len(batch) >= self.config.batch_size or
                    current_time - last_flush >= self.config.flush_interval
                )
                
                if should_flush and batch:
                    await self._flush_batch(batch)
                    batch.clear()
                    last_flush = current_time
            
            except Exception as e:
                self.logger.error(f"Audit worker error: {e}")
                await asyncio.sleep(1)
    
    async def _flush_batch(self, batch: List[AuditEvent]):
        """Flush batch of audit events"""
        try:
            for event in batch:
                await self._write_audit_log(event)
        except Exception as e:
            self.logger.error(f"Failed to flush audit batch: {e}")
    
    async def _cleanup_worker(self):
        """Background worker for log cleanup and retention"""
        while True:
            try:
                if self.config.auto_deletion_enabled:
                    await self._cleanup_old_logs()
                
                # Run cleanup daily
                await asyncio.sleep(86400)  # 24 hours
                
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _cleanup_old_logs(self):
        """Clean up logs older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_period_days)
        
        # This would implement actual log cleanup based on your storage system
        self.logger.info(f"Cleaning up audit logs older than {cutoff_date}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current audit metrics"""
        return {
            "total_events": self.metrics.total_events,
            "events_logged": self.metrics.events_logged,
            "events_filtered": self.metrics.events_filtered,
            "logging_rate": self.metrics.logging_rate,
            "pii_events_masked": self.metrics.pii_events_masked,
            "high_risk_events": self.metrics.high_risk_events,
            "compliance_events": self.metrics.compliance_events,
            "errors_logged": self.metrics.errors_logged,
            "queue_size": self.event_queue.qsize(),
            "queue_overflows": self.metrics.queue_overflows,
            "event_type_counts": self.metrics.event_type_counts,
            "classification_counts": self.metrics.classification_counts,
            "anomaly_baselines_count": len(self.anomaly_baselines)
        }
    
    def get_compliance_report(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate compliance report for specific framework"""
        # This would generate detailed compliance reports
        return {
            "framework": framework.value,
            "period": "last_30_days",
            "events_covered": self.metrics.compliance_events,
            "pii_protection_rate": 100.0 if self.config.mask_pii else 0.0,
            "retention_policy": f"{self.config.retention_period_days} days",
            "encryption_enabled": self.config.encrypt_logs,
            "audit_coverage": self.metrics.logging_rate
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = AuditMetrics()
        self.logger.info("Audit metrics reset")


# Factory function for easy integration
def create_audit_logging_middleware(
    app: FastAPI,
    audit_level: AuditLevel = AuditLevel.STANDARD,
    **kwargs
) -> AuditLoggingMiddleware:
    """
    🏭 Factory function to create audit logging middleware
    
    Args:
        app: FastAPI application
        audit_level: Audit logging level
        **kwargs: Additional configuration options
    
    Returns:
        Configured audit logging middleware instance
    """
    config = AuditConfig(
        audit_level=audit_level,
        **kwargs
    )
    
    return AuditLoggingMiddleware(app, config)


def setup_creator_audit_logging(app: FastAPI) -> AuditLoggingMiddleware:
    """
    🎯 Creator-specific audit logging setup
    Optimized for content creation platforms with enhanced compliance
    """
    config = AuditConfig(
        audit_level=AuditLevel.DETAILED,
        
        # Enhanced logging for creators
        log_all_requests=True,
        log_responses=True,
        log_request_bodies=False,  # Privacy consideration
        
        # PII protection
        mask_pii=True,
        hash_pii=True,
        pii_fields={
            "email", "phone", "address", "name", "ssn", "passport", "license",
            "creator_name", "real_name", "bank_account", "routing_number"
        },
        
        # Enhanced compliance
        enable_gdpr_compliance=True,
        enable_ccpa_compliance=True,
        retention_period_days=2555,  # 7 years for financial records
        
        # Creator-specific settings
        enable_creator_audit=True,
        log_content_operations=True,
        log_monetization_events=True,
        creator_retention_period=2555,
        
        # Enhanced security monitoring
        enable_real_time_alerts=True,
        enable_anomaly_detection=True,
        high_risk_threshold=70,  # Lower threshold for creator platforms
        
        # External integrations
        siem_integration=True,
        elasticsearch_enabled=True,
        elasticsearch_index="ainflue-audit-logs",
        
        # Performance optimization
        async_logging=True,
        batch_size=50,  # Smaller batches for real-time processing
        flush_interval=3,  # More frequent flushing
        
        # Storage security
        compress_logs=True,
        encrypt_logs=True,
        
        # Creator-specific sensitive fields
        sensitive_headers={
            "authorization", "cookie", "x-api-key", "x-auth-token",
            "x-creator-token", "x-payment-token", "x-bank-details"
        },
        
        sensitive_params={
            "password", "secret", "token", "key", "ssn", "credit_card",
            "bank_account", "routing_number", "tax_id", "ein"
        }
    )
    
    return AuditLoggingMiddleware(app, config)


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI(title="Audit Logging Demo")
    
    # Setup audit logging
    audit_logger = create_audit_logging_middleware(
        app,
        audit_level=AuditLevel.DETAILED
    )
    
    app.add_middleware(AuditLoggingMiddleware, middleware=audit_logger)
    
    @app.get("/")
    async def root():
        return {"message": "Audit Logging Template Active"}
    
    @app.post("/creator/content")
    async def create_content(data: dict):
        return {"message": "Content created", "id": "123"}
    
    @app.get("/metrics")
    async def get_metrics():
        return audit_logger.get_metrics()
    
    @app.get("/compliance/{framework}")
    async def get_compliance_report(framework: str):
        framework_enum = ComplianceFramework(framework)
        return audit_logger.get_compliance_report(framework_enum)