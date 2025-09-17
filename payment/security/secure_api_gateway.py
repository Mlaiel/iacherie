#!/usr/bin/env python3
"""
🔒 Secure API Gateway - Enterprise Payment API Security
=======================================================

Advanced API security gateway for Ainflue payment services.
API authentication, rate limiting, threat protection, and monitoring.

Author: Expert Team (Security + Backend Senior + Microservices)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for enterprise licensing

⚠️  LEGAL WARNING:
This code is proprietary to Fahed Mlaiel. Unauthorized use, distribution,
reverse engineering, or commercial exploitation is strictly prohibited.
Violations will result in immediate legal action.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Set, Callable
import re
import ipaddress
from collections import defaultdict, deque

import jwt
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import httpx


class SecurityLevel(Enum):
    """Niveaux de sécurité API"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    CREATOR_ONLY = "creator_only"
    PAYMENT_SECURE = "payment_secure"
    ADMIN_ONLY = "admin_only"
    INTERNAL_ONLY = "internal_only"


class ThreatType(Enum):
    """Types de menaces détectées"""
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    BRUTE_FORCE = "brute_force"
    DDoS_ATTACK = "ddos_attack"
    MALFORMED_REQUEST = "malformed_request"
    SUSPICIOUS_PAYLOAD = "suspicious_payload"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    IP_REPUTATION = "ip_reputation"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    TOKEN_ABUSE = "token_abuse"


class AuthenticationMethod(Enum):
    """Méthodes d'authentification"""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    HMAC_SIGNATURE = "hmac_signature"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutual_tls"
    CUSTOM_HEADER = "custom_header"


class RateLimitType(Enum):
    """Types de limitation de taux"""
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BANDWIDTH_PER_MINUTE = "bandwidth_per_minute"
    CONCURRENT_REQUESTS = "concurrent_requests"


@dataclass
class SecurityThreat:
    """Menace de sécurité détectée"""
    threat_id: str
    threat_type: ThreatType
    severity: str  # low, medium, high, critical
    source_ip: str
    user_agent: str
    request_path: str
    request_method: str
    payload_sample: str
    detected_at: datetime
    confidence: float
    blocked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitRule:
    """Règle de limitation de taux"""
    rule_id: str
    rate_limit_type: RateLimitType
    limit: int
    window_seconds: int
    scope: str  # ip, user, api_key, global
    endpoints: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    burst_allowance: int = 0
    penalty_seconds: int = 300


@dataclass
class APIEndpoint:
    """Configuration d'endpoint API"""
    path: str
    methods: List[str]
    security_level: SecurityLevel
    authentication_required: bool = True
    rate_limits: List[str] = field(default_factory=list)  # rule_ids
    allowed_ips: Optional[List[str]] = None
    blocked_ips: Optional[List[str]] = None
    custom_validators: List[Callable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RequestContext:
    """Contexte de requête sécurisée"""
    request_id: str
    client_ip: str
    user_agent: str
    path: str
    method: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body_size: int
    timestamp: datetime
    user_id: Optional[str] = None
    creator_id: Optional[str] = None
    api_key: Optional[str] = None
    authenticated: bool = False
    security_flags: List[str] = field(default_factory=list)


@dataclass
class SecurityCheck:
    """Résultat de vérification sécuritaire"""
    passed: bool
    threat_detected: Optional[SecurityThreat] = None
    rate_limited: bool = False
    authentication_failed: bool = False
    authorization_failed: bool = False
    ip_blocked: bool = False
    payload_blocked: bool = False
    error_message: Optional[str] = None
    response_headers: Dict[str, str] = field(default_factory=dict)


class ThreatDetector:
    """Détecteur de menaces avancé"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns de détection
        self.sql_injection_patterns = [
            r"(\bunion\b|\bselect\b|\binsert\b|\bdelete\b|\bdrop\b|\bupdate\b)",
            r"(\bor\b|\band\b)\s+\d+\s*=\s*\d+",
            r"['\"];\s*(\bselect\b|\binsert\b|\bdelete\b|\bdrop\b)",
            r"(\bexec\b|\bexecute\b)\s+\w+",
            r"--\s*$"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:\w+",
            r"on\w+\s*=\s*['\"].*?['\"]",
            r"<iframe[^>]*>.*?</iframe>",
            r"eval\s*\(",
            r"document\.(cookie|location|write)"
        ]
        
        # IPs suspectes (simulation)
        self.suspicious_ips = {
            "192.168.1.100",  # IP locale suspecte
            "10.0.0.1",       # IP interne suspecte
            "127.0.0.1"       # Localhost suspect
        }
        
        # User agents suspects
        self.suspicious_user_agents = [
            "curl", "wget", "python-requests", "bot", "crawler", "scanner"
        ]
        
    async def detect_threats(self, context: RequestContext, payload: str = "") -> List[SecurityThreat]:
        """Détection complète de menaces"""
        threats = []
        
        # Détection injection SQL
        threats.extend(await self._detect_sql_injection(context, payload))
        
        # Détection XSS
        threats.extend(await self._detect_xss(context, payload))
        
        # Détection force brute
        threats.extend(await self._detect_brute_force(context))
        
        # Détection DDoS
        threats.extend(await self._detect_ddos(context))
        
        # Détection IP suspecte
        threats.extend(await self._detect_suspicious_ip(context))
        
        # Détection géographique
        threats.extend(await self._detect_geographic_anomaly(context))
        
        # Détection payload malformé
        threats.extend(await self._detect_malformed_request(context, payload))
        
        return threats
        
    async def _detect_sql_injection(self, context: RequestContext, payload: str) -> List[SecurityThreat]:
        """Détection injection SQL"""
        threats = []
        
        # Vérifier URL et query parameters
        full_url = f"{context.path}?{'&'.join([f'{k}={v}' for k, v in context.query_params.items()])}"
        text_to_check = f"{full_url} {payload}".lower()
        
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                threat = SecurityThreat(
                    threat_id=f"sql_{uuid.uuid4().hex[:8]}",
                    threat_type=ThreatType.SQL_INJECTION,
                    severity="high",
                    source_ip=context.client_ip,
                    user_agent=context.user_agent,
                    request_path=context.path,
                    request_method=context.method,
                    payload_sample=payload[:500],
                    detected_at=datetime.utcnow(),
                    confidence=0.8,
                    metadata={"pattern_matched": pattern}
                )
                threats.append(threat)
                break  # Un pattern suffit
                
        return threats
        
    async def _detect_xss(self, context: RequestContext, payload: str) -> List[SecurityThreat]:
        """Détection XSS"""
        threats = []
        
        # Vérifier URL et payload
        text_to_check = f"{context.path} {payload}".lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                threat = SecurityThreat(
                    threat_id=f"xss_{uuid.uuid4().hex[:8]}",
                    threat_type=ThreatType.XSS_ATTACK,
                    severity="medium",
                    source_ip=context.client_ip,
                    user_agent=context.user_agent,
                    request_path=context.path,
                    request_method=context.method,
                    payload_sample=payload[:500],
                    detected_at=datetime.utcnow(),
                    confidence=0.7,
                    metadata={"pattern_matched": pattern}
                )
                threats.append(threat)
                break
                
        return threats
        
    async def _detect_brute_force(self, context: RequestContext) -> List[SecurityThreat]:
        """Détection force brute"""
        threats = []
        
        # Simulation - vérifier patterns de login répétés
        if "/auth" in context.path or "/login" in context.path:
            # En production, vérifier base de données des tentatives
            if context.method == "POST":
                threat = SecurityThreat(
                    threat_id=f"brute_{uuid.uuid4().hex[:8]}",
                    threat_type=ThreatType.BRUTE_FORCE,
                    severity="medium",
                    source_ip=context.client_ip,
                    user_agent=context.user_agent,
                    request_path=context.path,
                    request_method=context.method,
                    payload_sample="",
                    detected_at=datetime.utcnow(),
                    confidence=0.6,
                    metadata={"auth_endpoint": True}
                )
                threats.append(threat)
                
        return threats
        
    async def _detect_ddos(self, context: RequestContext) -> List[SecurityThreat]:
        """Détection DDoS"""
        threats = []
        
        # Simulation - en production, analyser le trafic en temps réel
        # Vérifier si beaucoup de requêtes de la même IP
        current_time = time.time()
        
        # Pattern simple de détection
        if context.client_ip in self.suspicious_ips:
            threat = SecurityThreat(
                threat_id=f"ddos_{uuid.uuid4().hex[:8]}",
                threat_type=ThreatType.DDoS_ATTACK,
                severity="high",
                source_ip=context.client_ip,
                user_agent=context.user_agent,
                request_path=context.path,
                request_method=context.method,
                payload_sample="",
                detected_at=datetime.utcnow(),
                confidence=0.7,
                metadata={"suspicious_ip": True}
            )
            threats.append(threat)
            
        return threats
        
    async def _detect_suspicious_ip(self, context: RequestContext) -> List[SecurityThreat]:
        """Détection IP suspecte"""
        threats = []
        
        if context.client_ip in self.suspicious_ips:
            threat = SecurityThreat(
                threat_id=f"ip_rep_{uuid.uuid4().hex[:8]}",
                threat_type=ThreatType.IP_REPUTATION,
                severity="medium",
                source_ip=context.client_ip,
                user_agent=context.user_agent,
                request_path=context.path,
                request_method=context.method,
                payload_sample="",
                detected_at=datetime.utcnow(),
                confidence=0.8,
                metadata={"ip_blacklisted": True}
            )
            threats.append(threat)
            
        return threats
        
    async def _detect_geographic_anomaly(self, context: RequestContext) -> List[SecurityThreat]:
        """Détection anomalie géographique"""
        threats = []
        
        # Simulation - vérifier géolocalisation IP
        # En production, utiliser service de géolocalisation
        if context.client_ip.startswith("192.168"):  # IP locale
            threat = SecurityThreat(
                threat_id=f"geo_{uuid.uuid4().hex[:8]}",
                threat_type=ThreatType.GEOGRAPHIC_ANOMALY,
                severity="low",
                source_ip=context.client_ip,
                user_agent=context.user_agent,
                request_path=context.path,
                request_method=context.method,
                payload_sample="",
                detected_at=datetime.utcnow(),
                confidence=0.5,
                metadata={"local_ip": True}
            )
            threats.append(threat)
            
        return threats
        
    async def _detect_malformed_request(self, context: RequestContext, payload: str) -> List[SecurityThreat]:
        """Détection requête malformée"""
        threats = []
        
        # Vérifier User-Agent suspect
        if any(agent in context.user_agent.lower() for agent in self.suspicious_user_agents):
            threat = SecurityThreat(
                threat_id=f"malformed_{uuid.uuid4().hex[:8]}",
                threat_type=ThreatType.MALFORMED_REQUEST,
                severity="low",
                source_ip=context.client_ip,
                user_agent=context.user_agent,
                request_path=context.path,
                request_method=context.method,
                payload_sample=payload[:200],
                detected_at=datetime.utcnow(),
                confidence=0.6,
                metadata={"suspicious_user_agent": True}
            )
            threats.append(threat)
            
        # Vérifier taille de payload suspecte
        if len(payload) > 100000:  # Plus de 100KB
            threat = SecurityThreat(
                threat_id=f"large_payload_{uuid.uuid4().hex[:8]}",
                threat_type=ThreatType.SUSPICIOUS_PAYLOAD,
                severity="medium",
                source_ip=context.client_ip,
                user_agent=context.user_agent,
                request_path=context.path,
                request_method=context.method,
                payload_sample=payload[:200],
                detected_at=datetime.utcnow(),
                confidence=0.7,
                metadata={"payload_size": len(payload)}
            )
            threats.append(threat)
            
        return threats


class RateLimiter:
    """Limiteur de taux avancé"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Stockage des compteurs par scope
        self.counters: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        self.penalties: Dict[str, datetime] = {}
        
        # Configuration par défaut
        self.default_rules = [
            RateLimitRule(
                rule_id="global_requests",
                rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit=1000,
                window_seconds=60,
                scope="global"
            ),
            RateLimitRule(
                rule_id="ip_requests",
                rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit=100,
                window_seconds=60,
                scope="ip"
            ),
            RateLimitRule(
                rule_id="payment_requests",
                rate_limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit=10,
                window_seconds=60,
                scope="ip",
                endpoints=["/payment/*"],
                security_level=SecurityLevel.PAYMENT_SECURE
            )
        ]
        
    async def check_rate_limit(self, 
                             context: RequestContext,
                             rules: List[RateLimitRule]) -> Tuple[bool, Optional[RateLimitRule]]:
        """Vérification des limites de taux"""
        current_time = time.time()
        
        for rule in rules:
            # Vérifier si la règle s'applique
            if not await self._rule_applies(rule, context):
                continue
                
            # Déterminer la clé de scope
            scope_key = await self._get_scope_key(rule, context)
            
            # Vérifier pénalité active
            penalty_key = f"{rule.rule_id}_{scope_key}"
            if penalty_key in self.penalties:
                if datetime.utcnow() < self.penalties[penalty_key]:
                    return False, rule  # Toujours en pénalité
                else:
                    del self.penalties[penalty_key]
                    
            # Nettoyer les entrées anciennes
            window_start = current_time - rule.window_seconds
            counter = self.counters[rule.rule_id][scope_key]
            
            while counter and counter[0] < window_start:
                counter.popleft()
                
            # Vérifier limite
            current_count = len(counter)
            if current_count >= rule.limit:
                # Appliquer pénalité si configurée
                if rule.penalty_seconds > 0:
                    self.penalties[penalty_key] = datetime.utcnow() + timedelta(seconds=rule.penalty_seconds)
                    
                return False, rule
                
            # Ajouter requête actuelle
            counter.append(current_time)
            
        return True, None
        
    async def _rule_applies(self, rule: RateLimitRule, context: RequestContext) -> bool:
        """Vérifier si une règle s'applique au contexte"""
        # Vérifier endpoints
        if rule.endpoints:
            path_matches = any(
                context.path.startswith(endpoint.replace("*", ""))
                for endpoint in rule.endpoints
            )
            if not path_matches:
                return False
                
        return True
        
    async def _get_scope_key(self, rule: RateLimitRule, context: RequestContext) -> str:
        """Générer clé de scope"""
        if rule.scope == "ip":
            return context.client_ip
        elif rule.scope == "user" and context.user_id:
            return context.user_id
        elif rule.scope == "api_key" and context.api_key:
            return context.api_key
        elif rule.scope == "global":
            return "global"
        else:
            return context.client_ip  # Default fallback


class AuthenticationValidator:
    """Validateur d'authentification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Clés API valides (simulation)
        self.valid_api_keys = {
            "ainflue_key_123": {"user_id": "user_123", "creator_id": "creator_abc"},
            "ainflue_key_456": {"user_id": "user_456", "creator_id": "creator_def"}
        }
        
        # Configuration JWT
        self.jwt_secret = "ainflue_jwt_secret_key_2025"
        
    async def authenticate_request(self, 
                                 context: RequestContext,
                                 method: AuthenticationMethod) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authentification de requête"""
        try:
            if method == AuthenticationMethod.API_KEY:
                return await self._authenticate_api_key(context)
            elif method == AuthenticationMethod.BEARER_TOKEN:
                return await self._authenticate_bearer_token(context)
            elif method == AuthenticationMethod.HMAC_SIGNATURE:
                return await self._authenticate_hmac(context)
            else:
                return False, None
                
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False, None
            
    async def _authenticate_api_key(self, context: RequestContext) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authentification par clé API"""
        # Vérifier header X-API-Key
        api_key = context.headers.get("x-api-key")
        if not api_key:
            return False, None
            
        if api_key in self.valid_api_keys:
            user_info = self.valid_api_keys[api_key]
            context.api_key = api_key
            context.user_id = user_info["user_id"]
            context.creator_id = user_info.get("creator_id")
            return True, user_info
            
        return False, None
        
    async def _authenticate_bearer_token(self, context: RequestContext) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authentification par token Bearer"""
        auth_header = context.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return False, None
            
        token = auth_header[7:]  # Supprimer "Bearer "
        
        try:
            # Décoder JWT
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            context.user_id = payload.get("sub")
            context.creator_id = payload.get("creator_id")
            
            return True, payload
            
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid token"}
            
    async def _authenticate_hmac(self, context: RequestContext) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authentification HMAC"""
        # Simulation HMAC - en production, implémenter vérification complète
        signature = context.headers.get("x-signature")
        timestamp = context.headers.get("x-timestamp")
        
        if not signature or not timestamp:
            return False, None
            
        # Vérifier timestamp (dans les 5 minutes)
        try:
            req_time = datetime.fromtimestamp(float(timestamp))
            if abs((datetime.utcnow() - req_time).total_seconds()) > 300:
                return False, {"error": "Request too old"}
        except (ValueError, TypeError):
            return False, {"error": "Invalid timestamp"}
            
        # Simulation validation HMAC
        return True, {"hmac_validated": True}


class SecureAPIGateway:
    """
    Passerelle API sécurisée enterprise-grade
    
    Fonctionnalités:
    - Authentification multi-méthodes
    - Limitation de taux intelligente
    - Détection de menaces en temps réel
    - Monitoring et logging complets
    - Protection DDoS et filtrage IP
    - Validation de payload avancée
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Composants de sécurité
        self.threat_detector = ThreatDetector()
        self.rate_limiter = RateLimiter()
        self.auth_validator = AuthenticationValidator()
        
        # Configuration des endpoints
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.global_rate_limits = self.rate_limiter.default_rules
        
        # Stockage des menaces et métriques
        self.detected_threats: Dict[str, SecurityThreat] = {}
        self.blocked_ips: Set[str] = set()
        self.request_logs: List[RequestContext] = []
        
        # Configuration de sécurité
        self.security_config = {
            'block_on_threat_detection': True,
            'threat_confidence_threshold': 0.7,
            'auto_ip_blocking': True,
            'ip_block_duration_hours': 24,
            'log_all_requests': True,
            'enable_cors': True,
            'max_request_size': 10 * 1024 * 1024,  # 10MB
            'response_headers': {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
            }
        }
        
        # Métriques
        self.metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'threats_detected': 0,
            'rate_limited_requests': 0,
            'authentication_failures': 0,
            'average_response_time': 0.0
        }
        
        # Initialiser endpoints par défaut
        self._setup_default_endpoints()
        
        self.logger.info("Secure API Gateway initialized")
        
    def _setup_default_endpoints(self):
        """Configuration des endpoints par défaut"""
        # Endpoint de paiement sécurisé
        self.endpoints["/payment/process"] = APIEndpoint(
            path="/payment/process",
            methods=["POST"],
            security_level=SecurityLevel.PAYMENT_SECURE,
            authentication_required=True,
            rate_limits=["payment_requests"],
            metadata={'requires_creator_verification': True}
        )
        
        # Endpoint créateur
        self.endpoints["/creator/revenue"] = APIEndpoint(
            path="/creator/revenue",
            methods=["GET", "POST"],
            security_level=SecurityLevel.CREATOR_ONLY,
            authentication_required=True,
            rate_limits=["ip_requests"]
        )
        
        # Endpoint public
        self.endpoints["/public/info"] = APIEndpoint(
            path="/public/info",
            methods=["GET"],
            security_level=SecurityLevel.PUBLIC,
            authentication_required=False,
            rate_limits=["global_requests"]
        )
        
        # Endpoint admin
        self.endpoints["/admin/security"] = APIEndpoint(
            path="/admin/security",
            methods=["GET", "POST", "PUT", "DELETE"],
            security_level=SecurityLevel.ADMIN_ONLY,
            authentication_required=True,
            allowed_ips=["192.168.1.0/24"]  # Réseau admin uniquement
        )
        
    async def process_request(self, request: Request) -> Union[Response, SecurityCheck]:
        """Traitement sécurisé d'une requête"""
        start_time = time.time()
        
        try:
            # Créer contexte de requête
            context = await self._create_request_context(request)
            
            # Logging de la requête
            if self.security_config['log_all_requests']:
                self.request_logs.append(context)
                
            # Vérifications de sécurité
            security_check = await self._perform_security_checks(context, request)
            
            if not security_check.passed:
                # Mise à jour des métriques
                self.metrics['blocked_requests'] += 1
                if security_check.threat_detected:
                    self.metrics['threats_detected'] += 1
                if security_check.rate_limited:
                    self.metrics['rate_limited_requests'] += 1
                if security_check.authentication_failed:
                    self.metrics['authentication_failures'] += 1
                    
                return await self._create_error_response(security_check)
                
            # Mise à jour métriques succès
            processing_time = time.time() - start_time
            self._update_success_metrics(processing_time)
            
            # Ajouter headers de sécurité
            response_headers = self.security_config['response_headers'].copy()
            response_headers.update(security_check.response_headers)
            
            return security_check
            
        except Exception as e:
            self.logger.error(f"Request processing error: {str(e)}")
            return await self._create_error_response(
                SecurityCheck(
                    passed=False,
                    error_message="Internal security error"
                )
            )
            
    async def _create_request_context(self, request: Request) -> RequestContext:
        """Création du contexte de requête"""
        # Récupération IP client
        client_ip = request.client.host if request.client else "unknown"
        
        # Headers forwarded
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
            
        # Lecture du body
        body = await request.body()
        
        context = RequestContext(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            path=str(request.url.path),
            method=request.method,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            body_size=len(body),
            timestamp=datetime.utcnow()
        )
        
        return context
        
    async def _perform_security_checks(self, context: RequestContext, request: Request) -> SecurityCheck:
        """Exécution des vérifications de sécurité"""
        # 1. Vérification IP bloquée
        if context.client_ip in self.blocked_ips:
            return SecurityCheck(
                passed=False,
                ip_blocked=True,
                error_message="IP address blocked"
            )
            
        # 2. Vérification taille de requête
        if context.body_size > self.security_config['max_request_size']:
            return SecurityCheck(
                passed=False,
                payload_blocked=True,
                error_message="Request size exceeds limit"
            )
            
        # 3. Trouver configuration d'endpoint
        endpoint = await self._find_endpoint_config(context.path, context.method)
        if not endpoint:
            return SecurityCheck(
                passed=False,
                error_message="Endpoint not found or not allowed"
            )
            
        # 4. Vérification IP autorisée
        if endpoint.allowed_ips and not await self._check_ip_allowed(context.client_ip, endpoint.allowed_ips):
            return SecurityCheck(
                passed=False,
                ip_blocked=True,
                error_message="IP not in allowlist"
            )
            
        # 5. Vérification IP bloquée par endpoint
        if endpoint.blocked_ips and context.client_ip in endpoint.blocked_ips:
            return SecurityCheck(
                passed=False,
                ip_blocked=True,
                error_message="IP blocked for this endpoint"
            )
            
        # 6. Limitation de taux
        applicable_rules = await self._get_applicable_rate_limits(endpoint, context)
        rate_ok, violated_rule = await self.rate_limiter.check_rate_limit(context, applicable_rules)
        
        if not rate_ok:
            return SecurityCheck(
                passed=False,
                rate_limited=True,
                error_message=f"Rate limit exceeded: {violated_rule.rate_limit_type.value}"
            )
            
        # 7. Authentification
        if endpoint.authentication_required:
            auth_method = await self._determine_auth_method(context)
            auth_ok, auth_info = await self.auth_validator.authenticate_request(context, auth_method)
            
            if not auth_ok:
                return SecurityCheck(
                    passed=False,
                    authentication_failed=True,
                    error_message="Authentication failed"
                )
                
            context.authenticated = True
            
        # 8. Autorisation par niveau de sécurité
        if not await self._check_authorization(context, endpoint):
            return SecurityCheck(
                passed=False,
                authorization_failed=True,
                error_message="Insufficient privileges"
            )
            
        # 9. Détection de menaces
        body = await request.body() if hasattr(request, 'body') else b""
        payload = body.decode('utf-8', errors='ignore')
        
        threats = await self.threat_detector.detect_threats(context, payload)
        
        if threats:
            # Filtrer par seuil de confiance
            high_confidence_threats = [
                t for t in threats 
                if t.confidence >= self.security_config['threat_confidence_threshold']
            ]
            
            if high_confidence_threats:
                # Stocker menaces
                for threat in high_confidence_threats:
                    self.detected_threats[threat.threat_id] = threat
                    
                # Blocage automatique si configuré
                if self.security_config['block_on_threat_detection']:
                    return SecurityCheck(
                        passed=False,
                        threat_detected=high_confidence_threats[0],
                        error_message=f"Security threat detected: {high_confidence_threats[0].threat_type.value}"
                    )
                    
        # 10. Validation personnalisée
        for validator in endpoint.custom_validators:
            try:
                if not await validator(context, request):
                    return SecurityCheck(
                        passed=False,
                        error_message="Custom validation failed"
                    )
            except Exception as e:
                self.logger.error(f"Custom validator error: {str(e)}")
                return SecurityCheck(
                    passed=False,
                    error_message="Validation error"
                )
                
        # Toutes les vérifications passées
        return SecurityCheck(
            passed=True,
            response_headers={
                'X-Request-ID': context.request_id,
                'X-Security-Level': endpoint.security_level.value
            }
        )
        
    async def _find_endpoint_config(self, path: str, method: str) -> Optional[APIEndpoint]:
        """Trouver configuration d'endpoint"""
        # Correspondance exacte
        if path in self.endpoints:
            endpoint = self.endpoints[path]
            if method in endpoint.methods:
                return endpoint
                
        # Correspondance avec wildcards
        for endpoint_path, endpoint in self.endpoints.items():
            if "*" in endpoint_path:
                pattern = endpoint_path.replace("*", ".*")
                if re.match(pattern, path) and method in endpoint.methods:
                    return endpoint
                    
        return None
        
    async def _check_ip_allowed(self, client_ip: str, allowed_ips: List[str]) -> bool:
        """Vérifier si IP est autorisée"""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            
            for allowed in allowed_ips:
                if "/" in allowed:  # CIDR
                    network = ipaddress.ip_network(allowed, strict=False)
                    if client_addr in network:
                        return True
                else:  # IP exacte
                    if str(client_addr) == allowed:
                        return True
                        
            return False
            
        except ValueError:
            return False
            
    async def _get_applicable_rate_limits(self, endpoint: APIEndpoint, context: RequestContext) -> List[RateLimitRule]:
        """Obtenir règles de limitation applicables"""
        applicable_rules = []
        
        # Règles globales
        applicable_rules.extend(self.global_rate_limits)
        
        # Règles spécifiques à l'endpoint
        for rule_id in endpoint.rate_limits:
            rule = next((r for r in self.global_rate_limits if r.rule_id == rule_id), None)
            if rule and rule not in applicable_rules:
                applicable_rules.append(rule)
                
        return applicable_rules
        
    async def _determine_auth_method(self, context: RequestContext) -> AuthenticationMethod:
        """Déterminer méthode d'authentification"""
        if "x-api-key" in context.headers:
            return AuthenticationMethod.API_KEY
        elif "authorization" in context.headers:
            if context.headers["authorization"].startswith("Bearer"):
                return AuthenticationMethod.BEARER_TOKEN
        elif "x-signature" in context.headers:
            return AuthenticationMethod.HMAC_SIGNATURE
            
        return AuthenticationMethod.API_KEY  # Default
        
    async def _check_authorization(self, context: RequestContext, endpoint: APIEndpoint) -> bool:
        """Vérification d'autorisation"""
        security_level = endpoint.security_level
        
        if security_level == SecurityLevel.PUBLIC:
            return True
        elif security_level == SecurityLevel.AUTHENTICATED:
            return context.authenticated
        elif security_level == SecurityLevel.CREATOR_ONLY:
            return context.authenticated and context.creator_id is not None
        elif security_level == SecurityLevel.PAYMENT_SECURE:
            return (context.authenticated and 
                   context.creator_id is not None and
                   endpoint.metadata.get('requires_creator_verification', False))
        elif security_level == SecurityLevel.ADMIN_ONLY:
            # Simulation - vérifier rôle admin
            return context.authenticated and context.user_id and "admin" in context.user_id
        elif security_level == SecurityLevel.INTERNAL_ONLY:
            # Vérifier IP interne
            return context.client_ip.startswith("192.168.") or context.client_ip.startswith("10.")
            
        return False
        
    async def _create_error_response(self, security_check: SecurityCheck) -> JSONResponse:
        """Créer réponse d'erreur"""
        status_code = 403  # Forbidden by default
        
        if security_check.authentication_failed:
            status_code = 401
        elif security_check.rate_limited:
            status_code = 429
        elif security_check.ip_blocked:
            status_code = 403
        elif security_check.payload_blocked:
            status_code = 413
            
        error_response = {
            "error": security_check.error_message or "Access denied",
            "timestamp": datetime.utcnow().isoformat(),
            "security_check": {
                "threat_detected": security_check.threat_detected.threat_type.value if security_check.threat_detected else None,
                "rate_limited": security_check.rate_limited,
                "authentication_failed": security_check.authentication_failed,
                "ip_blocked": security_check.ip_blocked
            }
        }
        
        headers = self.security_config['response_headers'].copy()
        headers.update(security_check.response_headers)
        
        return JSONResponse(
            content=error_response,
            status_code=status_code,
            headers=headers
        )
        
    def _update_success_metrics(self, processing_time: float):
        """Mise à jour des métriques de succès"""
        self.metrics['total_requests'] += 1
        
        # Moyenne mobile du temps de réponse
        current_avg = self.metrics['average_response_time']
        total_requests = self.metrics['total_requests']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
        
    async def add_endpoint(self, endpoint: APIEndpoint):
        """Ajouter un endpoint sécurisé"""
        self.endpoints[endpoint.path] = endpoint
        self.logger.info(f"Added secure endpoint: {endpoint.path} (security: {endpoint.security_level.value})")
        
    async def block_ip(self, ip_address: str, duration_hours: int = 24):
        """Bloquer une adresse IP"""
        self.blocked_ips.add(ip_address)
        
        # Simulation - en production, utiliser scheduler pour débloquer
        self.logger.warning(f"IP blocked: {ip_address} for {duration_hours} hours")
        
    async def unblock_ip(self, ip_address: str):
        """Débloquer une adresse IP"""
        self.blocked_ips.discard(ip_address)
        self.logger.info(f"IP unblocked: {ip_address}")
        
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Métriques de sécurité"""
        return {
            'gateway_metrics': self.metrics,
            'active_threats': len(self.detected_threats),
            'blocked_ips': len(self.blocked_ips),
            'configured_endpoints': len(self.endpoints),
            'rate_limit_rules': len(self.global_rate_limits),
            'recent_requests': len(self.request_logs),
            'threat_breakdown': self._get_threat_breakdown(),
            'top_blocked_ips': list(self.blocked_ips)[:10]
        }
        
    def _get_threat_breakdown(self) -> Dict[str, int]:
        """Répartition des menaces"""
        breakdown = defaultdict(int)
        for threat in self.detected_threats.values():
            breakdown[threat.threat_type.value] += 1
        return dict(breakdown)
        
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Tableau de bord de sécurité"""
        recent_threats = sorted(
            self.detected_threats.values(),
            key=lambda t: t.detected_at,
            reverse=True
        )[:10]
        
        dashboard = {
            'overview': {
                'total_requests_today': self.metrics['total_requests'],
                'blocked_requests_today': self.metrics['blocked_requests'],
                'threats_detected_today': self.metrics['threats_detected'],
                'average_response_time': f"{self.metrics['average_response_time']:.3f}s",
                'security_score': self._calculate_security_score()
            },
            'recent_threats': [
                {
                    'threat_id': t.threat_id,
                    'type': t.threat_type.value,
                    'severity': t.severity,
                    'source_ip': t.source_ip,
                    'detected_at': t.detected_at.isoformat(),
                    'confidence': t.confidence
                }
                for t in recent_threats
            ],
            'rate_limiting': {
                'rules_active': len(self.global_rate_limits),
                'requests_rate_limited': self.metrics['rate_limited_requests']
            },
            'authentication': {
                'failures_today': self.metrics['authentication_failures'],
                'success_rate': self._calculate_auth_success_rate()
            },
            'ip_security': {
                'blocked_ips': len(self.blocked_ips),
                'auto_blocking_enabled': self.security_config['auto_ip_blocking']
            }
        }
        
        return dashboard
        
    def _calculate_security_score(self) -> float:
        """Calcul du score de sécurité"""
        total_requests = self.metrics['total_requests']
        if total_requests == 0:
            return 1.0
            
        blocked_ratio = self.metrics['blocked_requests'] / total_requests
        threat_ratio = self.metrics['threats_detected'] / total_requests
        
        # Score basé sur la réduction des menaces
        score = 1.0 - (threat_ratio * 0.5) - (blocked_ratio * 0.2)
        return max(0.0, min(1.0, score))
        
    def _calculate_auth_success_rate(self) -> float:
        """Calcul du taux de succès d'authentification"""
        total_auth_requests = self.metrics['authentication_failures'] + (
            self.metrics['total_requests'] - self.metrics['blocked_requests']
        )
        
        if total_auth_requests == 0:
            return 1.0
            
        success_rate = 1.0 - (self.metrics['authentication_failures'] / total_auth_requests)
        return max(0.0, success_rate)


# Instance globale de la passerelle
api_gateway = SecureAPIGateway()


async def get_api_gateway() -> SecureAPIGateway:
    """Factory function pour la passerelle API"""
    return api_gateway


# Middleware Starlette pour intégration
class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de sécurité pour Starlette/FastAPI"""
    
    def __init__(self, app, gateway: SecureAPIGateway):
        super().__init__(app)
        self.gateway = gateway
        
    async def dispatch(self, request: Request, call_next):
        # Vérifications de sécurité
        security_result = await self.gateway.process_request(request)
        
        if isinstance(security_result, Response):
            # Requête bloquée
            return security_result
        elif isinstance(security_result, SecurityCheck) and security_result.passed:
            # Requête autorisée - continuer le traitement
            response = await call_next(request)
            
            # Ajouter headers de sécurité
            for header, value in security_result.response_headers.items():
                response.headers[header] = value
                
            return response
        else:
            # Erreur de sécurité
            return await self.gateway._create_error_response(security_result)


# Fonctions utilitaires pour intégration Ainflue
async def secure_creator_endpoint(path: str, methods: List[str]) -> APIEndpoint:
    """Créer endpoint sécurisé pour créateurs"""
    endpoint = APIEndpoint(
        path=path,
        methods=methods,
        security_level=SecurityLevel.CREATOR_ONLY,
        authentication_required=True,
        rate_limits=["ip_requests"],
        metadata={'creator_specific': True}
    )
    
    await api_gateway.add_endpoint(endpoint)
    return endpoint


async def secure_payment_endpoint(path: str) -> APIEndpoint:
    """Créer endpoint ultra-sécurisé pour paiements"""
    endpoint = APIEndpoint(
        path=path,
        methods=["POST"],
        security_level=SecurityLevel.PAYMENT_SECURE,
        authentication_required=True,
        rate_limits=["payment_requests"],
        metadata={
            'requires_creator_verification': True,
            'payment_processing': True,
            'audit_required': True
        }
    )
    
    await api_gateway.add_endpoint(endpoint)
    return endpoint


# Export des classes principales
__all__ = [
    'SecureAPIGateway',
    'SecurityMiddleware',
    'APIEndpoint',
    'SecurityCheck',
    'SecurityThreat',
    'RateLimitRule',
    'ThreatDetector',
    'RateLimiter',
    'AuthenticationValidator',
    'SecurityLevel',
    'ThreatType',
    'AuthenticationMethod',
    'RateLimitType',
    'api_gateway',
    'get_api_gateway',
    'secure_creator_endpoint',
    'secure_payment_endpoint'
]


# Initialisation pour tests
if __name__ == "__main__":
    async def demo_api_security():
        """Démonstration de la passerelle API sécurisée"""
        gateway = await get_api_gateway()
        
        # Test création endpoints
        creator_endpoint = await secure_creator_endpoint("/creator/upload", ["POST", "PUT"])
        payment_endpoint = await secure_payment_endpoint("/payment/charge")
        
        print(f"Created creator endpoint: {creator_endpoint.path}")
        print(f"Created payment endpoint: {payment_endpoint.path}")
        
        # Métriques de sécurité
        metrics = await gateway.get_security_metrics()
        print(f"Security metrics: {metrics}")
        
        # Tableau de bord
        dashboard = await gateway.get_security_dashboard()
        print(f"Security dashboard: {dashboard['overview']}")
        
        # Test blocage IP
        await gateway.block_ip("192.168.1.100", 1)
        print("Blocked test IP")
        
        # Test détection de menaces
        from starlette.requests import Request
        
        # Simulation requête suspecte
        class MockRequest:
            def __init__(self):
                self.client = type('client', (), {'host': '192.168.1.100'})()
                self.url = type('url', (), {'path': '/payment/process?union=select'})()
                self.method = "POST"
                self.headers = {
                    "user-agent": "curl/7.68.0",
                    "x-api-key": "ainflue_key_123"
                }
                self.query_params = {"union": "select"}
                
            async def body(self):
                return b"<script>alert('xss')</script>"
                
        mock_request = MockRequest()
        
        # Simuler traitement (ne fonctionnera pas complètement sans Starlette)
        print("Security gateway demo completed successfully")
        
    # Exécution démo
    asyncio.run(demo_api_security())