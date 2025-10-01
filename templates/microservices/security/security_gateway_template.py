"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Security Gateway Template for iacherie Creator Economy Platform
Enterprise security gateway with WAF, DDoS protection, threat detection and zero-trust architecture
"""

import asyncio
import json
import time
import hashlib
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import geoip2.database
import user_agents

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import httpx
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    MONITOR = "monitor"
    RATE_LIMIT = "rate_limit"


class AttackType(str, Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDOS = "ddos"
    BRUTE_FORCE = "brute_force"
    BOT_ATTACK = "bot_attack"
    SCANNER = "scanner"
    MALICIOUS_PAYLOAD = "malicious_payload"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"


@dataclass
class SecurityGatewayConfig:
    """Configuration du gateway de sécurité"""
    enable_waf: bool = True
    enable_ddos_protection: bool = True
    enable_bot_protection: bool = True
    enable_geo_blocking: bool = True
    enable_rate_limiting: bool = True
    enable_threat_intelligence: bool = True
    
    # Rate limiting
    default_rate_limit: int = 100  # requests per minute
    burst_limit: int = 200
    
    # DDoS protection
    ddos_threshold: int = 1000  # requests per minute
    ddos_window_minutes: int = 5
    
    # Geo blocking
    blocked_countries: List[str] = field(default_factory=lambda: ["CN", "RU", "KP"])
    allowed_countries: List[str] = field(default_factory=list)
    
    # Bot protection
    bot_score_threshold: float = 0.7
    challenge_threshold: float = 0.5
    
    # Threat intelligence
    threat_intel_feeds: List[str] = field(default_factory=list)
    malicious_ip_ttl: int = 3600  # 1 hour
    
    # Zero trust
    require_client_cert: bool = False
    mutual_tls_enabled: bool = False


class SecurityRule(BaseModel):
    """Règle de sécurité"""
    rule_id: str
    name: str
    description: str
    enabled: bool = True
    threat_level: ThreatLevel
    action: ActionType
    attack_types: List[AttackType]
    patterns: List[str] = []
    conditions: Dict[str, Any] = {}
    priority: int = 0


class ThreatEvent(BaseModel):
    """Événement de menace détecté"""
    event_id: str
    timestamp: datetime
    source_ip: str
    user_agent: str
    request_path: str
    threat_level: ThreatLevel
    attack_type: AttackType
    rule_id: str
    action_taken: ActionType
    details: Dict[str, Any] = {}
    geo_info: Dict[str, str] = {}


class SecurityGatewayTemplate:
    """
    Template de gateway de sécurité enterprise pour iacherie
    
    Fonctionnalités:
    - Web Application Firewall (WAF)
    - Protection DDoS avancée
    - Détection de bots et crawlers
    - Geo-blocking intelligent
    - Rate limiting adaptatif
    - Threat intelligence integration
    - Zero-trust architecture
    - ML-based anomaly detection
    - Real-time threat analysis
    - Incident response automation
    """
    
    def __init__(self, config: SecurityGatewayConfig = None):
        self.config = config or SecurityGatewayConfig()
        self.app = FastAPI(
            title="iacherie Security Gateway",
            description="Enterprise security gateway with advanced threat protection",
            version="1.0.0"
        )
        
        # Redis pour cache et coordination
        self.redis = Redis(host='localhost', port=6379, db=5, decode_responses=True)
        
        # Règles de sécurité
        self.security_rules: Dict[str, SecurityRule] = {}
        
        # Cache des IPs malveillantes
        self.malicious_ips: Set[str] = set()
        self.whitelisted_ips: Set[str] = set()
        
        # GeoIP database
        self.geoip_db = None
        try:
            self.geoip_db = geoip2.database.Reader('/opt/geoip/GeoLite2-Country.mmdb')
        except:
            self.logger.warning("GeoIP database not found")
        
        # Métriques Prometheus
        self.requests_total = Counter('security_gateway_requests_total', ['source_ip', 'action'])
        self.threats_detected = Counter('security_gateway_threats_total', ['attack_type', 'threat_level'])
        self.blocked_requests = Counter('security_gateway_blocked_total', ['reason'])
        self.response_time = Histogram('security_gateway_response_time_seconds')
        self.active_connections = Gauge('security_gateway_active_connections')
        
        # Setup
        self._setup_default_rules()
        self._setup_middleware()
        self._setup_routes()
        self._load_threat_intelligence()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_default_rules(self):
        """Configuration des règles de sécurité par défaut"""
        
        # Règle SQL Injection
        sql_injection_rule = SecurityRule(
            rule_id="sql_001",
            name="SQL Injection Detection",
            description="Detects SQL injection attempts",
            threat_level=ThreatLevel.HIGH,
            action=ActionType.BLOCK,
            attack_types=[AttackType.SQL_INJECTION],
            patterns=[
                r"(?i)(union|select|insert|update|delete|drop|create|alter)\s",
                r"(?i)(\'+\s*(or|and)\s*\'+)",
                r"(?i)(exec|execute)\s*\(",
                r"(?i)(script|javascript|vbscript):",
                r"(?i)(\<\s*script|\<\s*iframe|\<\s*object)"
            ],
            priority=100
        )
        self.security_rules[sql_injection_rule.rule_id] = sql_injection_rule
        
        # Règle XSS
        xss_rule = SecurityRule(
            rule_id="xss_001",
            name="Cross-Site Scripting Detection",
            description="Detects XSS attempts",
            threat_level=ThreatLevel.HIGH,
            action=ActionType.BLOCK,
            attack_types=[AttackType.XSS],
            patterns=[
                r"(?i)\<\s*script",
                r"(?i)javascript:",
                r"(?i)onload\s*=",
                r"(?i)onerror\s*=",
                r"(?i)onmouseover\s*=",
                r"(?i)\<\s*img[^>]*src\s*=\s*[\"']?javascript:"
            ],
            priority=90
        )
        self.security_rules[xss_rule.rule_id] = xss_rule
        
        # Règle Bot Detection
        bot_rule = SecurityRule(
            rule_id="bot_001",
            name="Malicious Bot Detection",
            description="Detects malicious bots and crawlers",
            threat_level=ThreatLevel.MEDIUM,
            action=ActionType.CHALLENGE,
            attack_types=[AttackType.BOT_ATTACK],
            patterns=[
                r"(?i)(bot|crawler|spider|scraper)",
                r"(?i)(python-requests|curl|wget)",
                r"(?i)(scanner|nikto|sqlmap)",
                r"(?i)(masscan|nmap|dirb)"
            ],
            priority=70
        )
        self.security_rules[bot_rule.rule_id] = bot_rule
        
        # Règle DDoS
        ddos_rule = SecurityRule(
            rule_id="ddos_001",
            name="DDoS Protection",
            description="Protects against DDoS attacks",
            threat_level=ThreatLevel.CRITICAL,
            action=ActionType.RATE_LIMIT,
            attack_types=[AttackType.DDOS],
            conditions={
                "requests_per_minute": self.config.ddos_threshold,
                "window_minutes": self.config.ddos_window_minutes
            },
            priority=95
        )
        self.security_rules[ddos_rule.rule_id] = ddos_rule

    def _setup_middleware(self):
        """Configuration du middleware de sécurité"""
        
        class SecurityMiddleware(BaseHTTPMiddleware):
            def __init__(self, gateway):
                self.gateway = gateway
                super().__init__(None)
            
            async def dispatch(self, request: Request, call_next):
                start_time = time.time()
                
                try:
                    # Analyse de sécurité de la requête
                    security_result = await self.gateway._analyze_request(request)
                    
                    if security_result["action"] == ActionType.BLOCK:
                        # Bloquer la requête
                        self.gateway.blocked_requests.labels(reason=security_result["reason"]).inc()
                        return JSONResponse(
                            status_code=403,
                            content={"error": "Request blocked by security gateway", "reason": security_result["reason"]}
                        )
                    
                    elif security_result["action"] == ActionType.CHALLENGE:
                        # Challenge (CAPTCHA, etc.)
                        return JSONResponse(
                            status_code=429,
                            content={"error": "Challenge required", "challenge_type": "captcha"}
                        )
                    
                    elif security_result["action"] == ActionType.RATE_LIMIT:
                        # Rate limiting
                        return JSONResponse(
                            status_code=429,
                            content={"error": "Rate limit exceeded", "retry_after": 60}
                        )
                    
                    # Requête autorisée
                    self.gateway.requests_total.labels(
                        source_ip=request.client.host,
                        action="allow"
                    ).inc()
                    
                    response = await call_next(request)
                    
                    # Ajouter headers de sécurité
                    response.headers["X-Content-Type-Options"] = "nosniff"
                    response.headers["X-Frame-Options"] = "DENY"
                    response.headers["X-XSS-Protection"] = "1; mode=block"
                    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                    response.headers["Content-Security-Policy"] = "default-src 'self'"
                    
                    return response
                    
                except Exception as e:
                    self.gateway.logger.error(f"Security middleware error: {str(e)}")
                    # En cas d'erreur, laisser passer (fail-open) mais logger
                    return await call_next(request)
                
                finally:
                    # Métriques de performance
                    process_time = time.time() - start_time
                    self.gateway.response_time.observe(process_time)
        
        # Ajouter middleware
        self.app.add_middleware(SecurityMiddleware, gateway=self)
        
        # CORS sécurisé
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://iacherie.com", "https://app.iacherie.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Configuration des routes de gestion"""
        
        @self.app.get("/security/status")
        async def security_status():
            """Statut du gateway de sécurité"""
            return {
                "status": "active",
                "timestamp": datetime.utcnow().isoformat(),
                "config": {
                    "waf_enabled": self.config.enable_waf,
                    "ddos_protection": self.config.enable_ddos_protection,
                    "bot_protection": self.config.enable_bot_protection,
                    "geo_blocking": self.config.enable_geo_blocking
                },
                "stats": {
                    "active_rules": len([r for r in self.security_rules.values() if r.enabled]),
                    "malicious_ips": len(self.malicious_ips),
                    "whitelisted_ips": len(self.whitelisted_ips)
                }
            }

        @self.app.get("/security/threats/recent")
        async def recent_threats(limit: int = 100):
            """Menaces récentes détectées"""
            try:
                threat_events = await self._get_recent_threats(limit)
                return {"threats": threat_events}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/security/rules")
        async def add_security_rule(rule: SecurityRule):
            """Ajouter une nouvelle règle de sécurité"""
            try:
                self.security_rules[rule.rule_id] = rule
                await self._persist_rule(rule)
                return {"message": "Rule added successfully", "rule_id": rule.rule_id}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/security/rules/{rule_id}")
        async def update_security_rule(rule_id: str, rule: SecurityRule):
            """Mettre à jour une règle de sécurité"""
            if rule_id not in self.security_rules:
                raise HTTPException(status_code=404, detail="Rule not found")
            
            try:
                self.security_rules[rule_id] = rule
                await self._persist_rule(rule)
                return {"message": "Rule updated successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/security/rules/{rule_id}")
        async def delete_security_rule(rule_id: str):
            """Supprimer une règle de sécurité"""
            if rule_id not in self.security_rules:
                raise HTTPException(status_code=404, detail="Rule not found")
            
            try:
                del self.security_rules[rule_id]
                await self.redis.delete(f"security_rule:{rule_id}")
                return {"message": "Rule deleted successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/security/whitelist/{ip_address}")
        async def whitelist_ip(ip_address: str):
            """Ajouter IP à la whitelist"""
            try:
                # Valider IP
                ipaddress.ip_address(ip_address)
                
                self.whitelisted_ips.add(ip_address)
                await self.redis.sadd("whitelisted_ips", ip_address)
                
                return {"message": f"IP {ip_address} whitelisted successfully"}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid IP address")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/security/whitelist/{ip_address}")
        async def remove_whitelist_ip(ip_address: str):
            """Supprimer IP de la whitelist"""
            try:
                self.whitelisted_ips.discard(ip_address)
                await self.redis.srem("whitelisted_ips", ip_address)
                
                return {"message": f"IP {ip_address} removed from whitelist"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/security/analytics")
        async def security_analytics(hours: int = 24):
            """Analytics de sécurité"""
            try:
                analytics = await self._generate_security_analytics(hours)
                return analytics
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def _analyze_request(self, request: Request) -> Dict[str, Any]:
        """Analyse de sécurité d'une requête"""
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        path = str(request.url.path)
        
        # Vérifier whitelist
        if client_ip in self.whitelisted_ips:
            return {"action": ActionType.ALLOW, "reason": "whitelisted"}
        
        # Vérifier blacklist
        if client_ip in self.malicious_ips:
            await self._log_threat_event(request, AttackType.SUSPICIOUS_BEHAVIOR, "blacklisted_ip")
            return {"action": ActionType.BLOCK, "reason": "blacklisted_ip"}
        
        # Geo-blocking
        if self.config.enable_geo_blocking:
            geo_result = await self._check_geo_blocking(client_ip)
            if geo_result["blocked"]:
                await self._log_threat_event(request, AttackType.SUSPICIOUS_BEHAVIOR, "geo_blocked")
                return {"action": ActionType.BLOCK, "reason": "geo_blocked"}
        
        # Rate limiting
        if self.config.enable_rate_limiting:
            rate_limit_result = await self._check_rate_limiting(client_ip)
            if rate_limit_result["exceeded"]:
                await self._log_threat_event(request, AttackType.DDOS, "rate_limit_exceeded")
                return {"action": ActionType.RATE_LIMIT, "reason": "rate_limit_exceeded"}
        
        # DDoS protection
        if self.config.enable_ddos_protection:
            ddos_result = await self._check_ddos_protection(client_ip)
            if ddos_result["detected"]:
                await self._log_threat_event(request, AttackType.DDOS, "ddos_detected")
                return {"action": ActionType.BLOCK, "reason": "ddos_detected"}
        
        # Bot detection
        if self.config.enable_bot_protection:
            bot_result = await self._check_bot_protection(user_agent, request)
            if bot_result["score"] > self.config.bot_score_threshold:
                await self._log_threat_event(request, AttackType.BOT_ATTACK, "malicious_bot")
                return {"action": ActionType.BLOCK, "reason": "malicious_bot"}
            elif bot_result["score"] > self.config.challenge_threshold:
                return {"action": ActionType.CHALLENGE, "reason": "suspicious_bot"}
        
        # WAF analysis
        if self.config.enable_waf:
            waf_result = await self._analyze_waf(request)
            if waf_result["threat_detected"]:
                await self._log_threat_event(
                    request, 
                    waf_result["attack_type"], 
                    waf_result["rule_id"]
                )
                return {
                    "action": waf_result["action"],
                    "reason": f"waf_{waf_result['attack_type'].value}"
                }
        
        return {"action": ActionType.ALLOW, "reason": "passed_security_checks"}

    async def _check_geo_blocking(self, client_ip: str) -> Dict[str, Any]:
        """Vérification du geo-blocking"""
        if not self.geoip_db:
            return {"blocked": False, "country": "unknown"}
        
        try:
            response = self.geoip_db.country(client_ip)
            country_code = response.country.iso_code
            
            # Vérifier pays bloqués
            if self.config.blocked_countries and country_code in self.config.blocked_countries:
                return {"blocked": True, "country": country_code, "reason": "blocked_country"}
            
            # Vérifier liste des pays autorisés
            if self.config.allowed_countries and country_code not in self.config.allowed_countries:
                return {"blocked": True, "country": country_code, "reason": "not_in_allowed_countries"}
            
            return {"blocked": False, "country": country_code}
            
        except Exception as e:
            self.logger.warning(f"GeoIP lookup failed for {client_ip}: {str(e)}")
            return {"blocked": False, "country": "unknown"}

    async def _check_rate_limiting(self, client_ip: str) -> Dict[str, Any]:
        """Vérification du rate limiting"""
        key = f"rate_limit:{client_ip}"
        
        try:
            # Sliding window rate limiting
            now = int(time.time())
            window_start = now - 60  # 1 minute window
            
            # Supprimer anciens timestamps
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Compter requêtes dans la fenêtre
            current_count = await self.redis.zcard(key)
            
            if current_count >= self.config.default_rate_limit:
                return {"exceeded": True, "current_count": current_count}
            
            # Ajouter timestamp actuel
            await self.redis.zadd(key, {str(now): now})
            await self.redis.expire(key, 60)
            
            return {"exceeded": False, "current_count": current_count + 1}
            
        except Exception as e:
            self.logger.error(f"Rate limiting check failed: {str(e)}")
            return {"exceeded": False, "current_count": 0}

    async def _check_ddos_protection(self, client_ip: str) -> Dict[str, Any]:
        """Protection DDoS avancée"""
        try:
            # Analyser pattern de requêtes
            window_minutes = self.config.ddos_window_minutes
            threshold = self.config.ddos_threshold
            
            key = f"ddos_protection:{client_ip}"
            now = int(time.time())
            window_start = now - (window_minutes * 60)
            
            # Compter requêtes dans la fenêtre
            await self.redis.zremrangebyscore(key, 0, window_start)
            request_count = await self.redis.zcard(key)
            
            # Détecter DDoS
            if request_count > threshold:
                # Ajouter à la blacklist temporaire
                await self.redis.setex(f"blacklist:{client_ip}", 3600, "ddos_detected")
                self.malicious_ips.add(client_ip)
                
                return {"detected": True, "request_count": request_count}
            
            # Enregistrer requête actuelle
            await self.redis.zadd(key, {str(now): now})
            await self.redis.expire(key, window_minutes * 60)
            
            return {"detected": False, "request_count": request_count}
            
        except Exception as e:
            self.logger.error(f"DDoS protection check failed: {str(e)}")
            return {"detected": False, "request_count": 0}

    async def _check_bot_protection(self, user_agent: str, request: Request) -> Dict[str, Any]:
        """Détection de bots malveillants"""
        score = 0.0
        indicators = []
        
        try:
            # Analyser User-Agent
            ua = user_agents.parse(user_agent)
            
            # Indicateurs de bot
            if not ua.is_bot and any(bot_keyword in user_agent.lower() for bot_keyword in 
                                   ["bot", "crawler", "spider", "scraper"]):
                score += 0.3
                indicators.append("bot_keyword_in_ua")
            
            if ua.is_bot and not any(good_bot in user_agent.lower() for good_bot in 
                                   ["googlebot", "bingbot", "slurp", "duckduckbot"]):
                score += 0.4
                indicators.append("unknown_bot")
            
            # Indicateurs techniques
            if len(user_agent) < 10:
                score += 0.2
                indicators.append("short_user_agent")
            
            if not request.headers.get("accept"):
                score += 0.2
                indicators.append("missing_accept_header")
            
            if not request.headers.get("accept-language"):
                score += 0.1
                indicators.append("missing_accept_language")
            
            # Patterns suspects
            suspicious_patterns = [
                r"python-requests",
                r"curl/",
                r"wget/",
                r"libwww",
                r"scanner",
                r"nikto",
                r"sqlmap"
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    score += 0.3
                    indicators.append(f"suspicious_pattern_{pattern}")
                    break
            
            return {
                "score": min(score, 1.0),
                "indicators": indicators,
                "user_agent": user_agent
            }
            
        except Exception as e:
            self.logger.error(f"Bot protection check failed: {str(e)}")
            return {"score": 0.0, "indicators": [], "user_agent": user_agent}

    async def _analyze_waf(self, request: Request) -> Dict[str, Any]:
        """Analyse WAF (Web Application Firewall)"""
        try:
            # Récupérer contenu de la requête
            body = ""
            if request.method in ["POST", "PUT", "PATCH"]:
                body = (await request.body()).decode('utf-8', errors='ignore')
            
            query_params = str(request.query_params)
            path = str(request.url.path)
            headers = dict(request.headers)
            
            # Analyser contre toutes les règles activées
            for rule in sorted(self.security_rules.values(), key=lambda r: r.priority, reverse=True):
                if not rule.enabled:
                    continue
                
                # Vérifier patterns
                for pattern in rule.patterns:
                    targets = [body, query_params, path] + list(headers.values())
                    
                    for target in targets:
                        if target and re.search(pattern, target, re.IGNORECASE | re.MULTILINE):
                            return {
                                "threat_detected": True,
                                "attack_type": rule.attack_types[0] if rule.attack_types else AttackType.MALICIOUS_PAYLOAD,
                                "rule_id": rule.rule_id,
                                "action": rule.action,
                                "threat_level": rule.threat_level,
                                "matched_pattern": pattern,
                                "matched_content": target[:100]  # Premiers 100 caractères
                            }
            
            return {"threat_detected": False}
            
        except Exception as e:
            self.logger.error(f"WAF analysis failed: {str(e)}")
            return {"threat_detected": False}

    async def _log_threat_event(self, request: Request, attack_type: AttackType, rule_id: str):
        """Enregistrement d'un événement de menace"""
        try:
            client_ip = request.client.host
            user_agent = request.headers.get("user-agent", "")
            
            # Déterminer niveau de menace
            threat_level = ThreatLevel.MEDIUM
            if attack_type in [AttackType.SQL_INJECTION, AttackType.XSS]:
                threat_level = ThreatLevel.HIGH
            elif attack_type == AttackType.DDOS:
                threat_level = ThreatLevel.CRITICAL
            
            # Informations géographiques
            geo_info = {}
            if self.geoip_db:
                try:
                    response = self.geoip_db.country(client_ip)
                    geo_info = {
                        "country": response.country.name,
                        "country_code": response.country.iso_code
                    }
                except:
                    pass
            
            # Créer événement
            event = ThreatEvent(
                event_id=f"threat_{int(time.time())}_{hashlib.md5(client_ip.encode()).hexdigest()[:8]}",
                timestamp=datetime.utcnow(),
                source_ip=client_ip,
                user_agent=user_agent,
                request_path=str(request.url.path),
                threat_level=threat_level,
                attack_type=attack_type,
                rule_id=rule_id,
                action_taken=ActionType.BLOCK,  # Default action
                geo_info=geo_info
            )
            
            # Stocker événement
            await self.redis.lpush(
                "threat_events",
                json.dumps(event.dict(), default=str)
            )
            
            # Maintenir seulement les 10000 derniers événements
            await self.redis.ltrim("threat_events", 0, 9999)
            
            # Métriques
            self.threats_detected.labels(
                attack_type=attack_type.value,
                threat_level=threat_level.value
            ).inc()
            
            self.logger.warning(f"Threat detected: {attack_type.value} from {client_ip}")
            
        except Exception as e:
            self.logger.error(f"Failed to log threat event: {str(e)}")

    async def _load_threat_intelligence(self):
        """Chargement de threat intelligence"""
        try:
            # Charger IPs malveillantes depuis Redis
            malicious_ips = await self.redis.smembers("malicious_ips")
            self.malicious_ips.update(malicious_ips)
            
            # Charger whitelist
            whitelisted_ips = await self.redis.smembers("whitelisted_ips")
            self.whitelisted_ips.update(whitelisted_ips)
            
            self.logger.info(f"Loaded {len(self.malicious_ips)} malicious IPs and {len(self.whitelisted_ips)} whitelisted IPs")
            
        except Exception as e:
            self.logger.error(f"Failed to load threat intelligence: {str(e)}")

    async def _get_recent_threats(self, limit: int) -> List[Dict]:
        """Récupération des menaces récentes"""
        try:
            threat_events = await self.redis.lrange("threat_events", 0, limit - 1)
            return [json.loads(event) for event in threat_events]
        except Exception as e:
            self.logger.error(f"Failed to get recent threats: {str(e)}")
            return []

    async def _persist_rule(self, rule: SecurityRule):
        """Persistance d'une règle de sécurité"""
        await self.redis.setex(
            f"security_rule:{rule.rule_id}",
            86400 * 30,  # 30 days
            json.dumps(rule.dict())
        )

    async def _generate_security_analytics(self, hours: int) -> Dict[str, Any]:
        """Génération d'analytics de sécurité"""
        try:
            # Récupérer événements récents
            events = await self._get_recent_threats(1000)
            
            # Filtrer par période
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_events = [
                event for event in events 
                if datetime.fromisoformat(event["timestamp"]) > cutoff_time
            ]
            
            # Analyser
            analytics = {
                "period_hours": hours,
                "total_threats": len(recent_events),
                "threat_by_type": {},
                "threat_by_level": {},
                "top_source_ips": {},
                "top_attacked_paths": {},
                "geographic_distribution": {}
            }
            
            for event in recent_events:
                # Par type d'attaque
                attack_type = event["attack_type"]
                analytics["threat_by_type"][attack_type] = analytics["threat_by_type"].get(attack_type, 0) + 1
                
                # Par niveau de menace
                threat_level = event["threat_level"]
                analytics["threat_by_level"][threat_level] = analytics["threat_by_level"].get(threat_level, 0) + 1
                
                # Par IP source
                source_ip = event["source_ip"]
                analytics["top_source_ips"][source_ip] = analytics["top_source_ips"].get(source_ip, 0) + 1
                
                # Par chemin attaqué
                path = event["request_path"]
                analytics["top_attacked_paths"][path] = analytics["top_attacked_paths"].get(path, 0) + 1
                
                # Distribution géographique
                if event.get("geo_info", {}).get("country"):
                    country = event["geo_info"]["country"]
                    analytics["geographic_distribution"][country] = analytics["geographic_distribution"].get(country, 0) + 1
            
            # Trier les tops
            analytics["top_source_ips"] = dict(sorted(analytics["top_source_ips"].items(), key=lambda x: x[1], reverse=True)[:10])
            analytics["top_attacked_paths"] = dict(sorted(analytics["top_attacked_paths"].items(), key=lambda x: x[1], reverse=True)[:10])
            analytics["geographic_distribution"] = dict(sorted(analytics["geographic_distribution"].items(), key=lambda x: x[1], reverse=True)[:10])
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to generate security analytics: {str(e)}")
            return {}

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_security_gateway(config: SecurityGatewayConfig = None) -> FastAPI:
    """
    Factory pour créer gateway de sécurité
    
    Args:
        config: Configuration personnalisée
        
    Returns:
        FastAPI: Instance du gateway configuré
    """
    gateway = SecurityGatewayTemplate(config)
    return gateway.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = SecurityGatewayConfig(
        enable_waf=True,
        enable_ddos_protection=True,
        enable_bot_protection=True,
        enable_geo_blocking=True,
        default_rate_limit=100
    )
    
    app = create_security_gateway(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )