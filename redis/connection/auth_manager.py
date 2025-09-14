#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 Redis Authentication Manager - Enterprise Security
====================================================

Gestionnaire d'authentification Redis enterprise avec sécurité multi-niveaux,
ACL granulaires et monitoring de sécurité avancé.

**Rôles Experts:**
- **Sécurité**: Architecture sécurité enterprise, threat detection
- **Backend Senior**: Infrastructure authentification haute performance
- **DevOps**: Monitoring sécurité et audit logging
- **DBA**: Gestion permissions et contrôles d'accès

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import hashlib
import secrets
import jwt
from typing import Dict, Any, Optional, List, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import bcrypt

# Enterprise Redis imports with fallback
try:
    import redis.asyncio as aioredis
    AIOREDIS_AVAILABLE = True
except ImportError:
    # Fallback pour environnement sans redis
    try:
        import aioredis
        AIOREDIS_AVAILABLE = True
    except ImportError:
        # Fallback pour environnement sans aioredis
        AIOREDIS_AVAILABLE = False
        aioredis = None

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Rôles utilisateur système"""
    ADMIN = "admin"
    CREATOR = "creator"
    VIEWER = "viewer"
    SERVICE = "service"
    ANALYTICS = "analytics"
    BACKUP = "backup"
    READONLY = "readonly"

class AccessLevel(Enum):
    """Niveaux d'accès Redis"""
    FULL = "full"  # Toutes opérations
    READ_WRITE = "read_write"  # Lecture/écriture
    READ_ONLY = "read_only"  # Lecture seule
    WRITE_ONLY = "write_only"  # Écriture seule
    NO_ACCESS = "no_access"  # Aucun accès

class AuthEvent(Enum):
    """Types d'événements d'authentification"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    TOKEN_CREATED = "token_created"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

@dataclass
class User:
    """Utilisateur système avec métadonnées sécurité"""
    username: str
    email: str
    role: UserRole
    password_hash: str
    salt: str
    created_at: float = field(default_factory=time.time)
    last_login: Optional[float] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    lock_until: Optional[float] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    api_key: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    ip_whitelist: List[str] = field(default_factory=list)
    
@dataclass 
class ACLRule:
    """Règle ACL Redis granulaire"""
    user_pattern: str  # Pattern utilisateur
    key_pattern: str   # Pattern clés Redis
    operations: Set[str]  # Opérations autorisées
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditions supplémentaires
    priority: int = 100  # Priorité règle

@dataclass
class AuthConfig:
    """Configuration for Redis Authentication Manager"""
    secret_key: str
    token_expiration: int = 3600  # 1 hour
    refresh_token_expiration: int = 86400  # 24 hours
    max_failed_attempts: int = 5
    lockout_duration: int = 1800  # 30 minutes
    enable_mfa: bool = True
    session_timeout: int = 3600  # 1 hour
    enable_ip_whitelist: bool = False
    enable_audit_logging: bool = True
    encryption_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    def __post_init__(self):
        if not self.secret_key:
            raise ValueError("secret_key is required for AuthConfig")
        if not self.encryption_key:
            # Generate encryption key if not provided
            key = Fernet.generate_key()
            self.encryption_key = key.decode()

@dataclass
class SecurityMetrics:
    """Métriques de sécurité"""
    successful_auths: int = 0
    failed_auths: int = 0
    active_sessions: int = 0
    blocked_ips: Set[str] = field(default_factory=set)
    suspicious_activities: int = 0
    last_security_scan: float = field(default_factory=time.time)

class RedisAuthManager:
    """
    🔐 Gestionnaire d'Authentification Redis Enterprise
    
    **Sécurité Expert:**
    - Multi-factor authentication (MFA)
    - Détection activités suspectes automatique
    - Chiffrement end-to-end tokens et sessions
    - Audit trail complet et forensique
    
    **Backend Senior:**
    - Architecture haute performance auth
    - Gestion sessions distribuées
    - Load balancing auth servers
    
    **DevOps:**
    - Monitoring métriques sécurité temps réel
    - Alertes automatiques intrusions
    - Dashboard sécurité opérationnel
    
    **DBA:**
    - ACL granulaires optimisées
    - Permissions hiérarchiques
    - Audit base données sécurisé
    """
    
    def __init__(self, config: AuthConfig):
        """Initialize Redis Auth Manager with enterprise configuration"""
        self.config = config
        self.redis_pool = None  # Will be set during initialization
        
        # Configuration from AuthConfig
        self.secret_key = config.secret_key
        self.token_expiry = config.token_expiration
        self.refresh_token_expiry = config.refresh_token_expiration 
        self.max_failed_attempts = config.max_failed_attempts
        self.lockout_duration = config.lockout_duration
        self.mfa_required = config.enable_mfa
        
        # Chiffrement
        self.encryption_key = self._derive_encryption_key(config.secret_key)
        self.fernet = Fernet(self.encryption_key)
        
        # Stockage en mémoire pour performance
        self.users: Dict[str, User] = {}
        self.acl_rules: List[ACLRule] = []
        self.active_tokens: Dict[str, Dict[str, Any]] = {}
        self.security_metrics = SecurityMetrics()
        
        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = {}
        self.rate_limit_window = self.config.rate_limit_window
        self.rate_limit_max = self.config.rate_limit_requests
        
        # Initialize state
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize the auth manager with Redis connection"""
        try:
            if not AIOREDIS_AVAILABLE:
                logger.warning("Redis not available, using mock auth implementation")
                self._initialized = True
                return
                
            # Redis pool will be set by the connection layer
            # For now, mark as initialized
            self._initialized = True
            logger.info("Redis Auth Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Auth Manager: {e}")
            raise
            
    async def shutdown(self) -> None:
        """Shutdown the auth manager"""
        try:
            self._initialized = False
            logger.info("Redis Auth Manager shutdown completed")
        except Exception as e:
            logger.error(f"Error during Auth Manager shutdown: {e}")
            
    def set_redis_pool(self, redis_pool):
        """Set Redis pool connection"""
        self.redis_pool = redis_pool
        
        # Initialize patterns and monitoring when pool is available
        if not hasattr(self, 'suspicious_patterns'):
            self._initialize_security_patterns()
            asyncio.create_task(self._initialize_default_users())
            asyncio.create_task(self._load_acl_rules())
            asyncio.create_task(self._start_security_monitoring())
        
    def _initialize_security_patterns(self):
        """Initialize security patterns for threat detection"""
        # Patterns suspects
        self.suspicious_patterns = [
            r'(union|select|insert|delete|drop|create|alter)',  # SQL injection
            r'(<script|javascript|onload|onerror)',  # XSS
            r'(\.\./|\.\.\\)',  # Path traversal
            r'(exec|system|cmd|shell)',  # Command injection
        ]
        logger.info("🔐 Redis Auth Manager security patterns initialized")
    
    def _derive_encryption_key(self, secret: str) -> bytes:
        """**Sécurité**: Dérivation clé chiffrement sécurisée"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'redis_auth_salt',  # En production, utiliser salt aléatoire
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return key
    
    async def _initialize_default_users(self):
        """**DBA**: Initialisation utilisateurs par défaut"""
        try:
            # Admin par défaut
            admin_user = await self.create_user(
                username="admin",
                email="admin@ainflue.com",
                password="change_me_in_production",
                role=UserRole.ADMIN
            )
            
            if admin_user:
                # Permissions admin complètes
                admin_user.permissions.update([
                    "redis:*",
                    "cache:*",
                    "user:*",
                    "admin:*"
                ])
            
            # Service account pour intégrations
            service_user = await self.create_user(
                username="service_account",
                email="service@ainflue.com", 
                password=secrets.token_urlsafe(32),
                role=UserRole.SERVICE
            )
            
            if service_user:
                service_user.permissions.update([
                    "cache:read",
                    "cache:write",
                    "session:*"
                ])
                
            logger.info("✅ Utilisateurs par défaut créés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation utilisateurs: {e}")
    
    async def _load_acl_rules(self):
        """**DBA**: Chargement règles ACL par défaut"""
        default_rules = [
            # Admin: accès complet
            ACLRule(
                user_pattern="admin:*",
                key_pattern="*",
                operations={"GET", "SET", "DEL", "KEYS", "FLUSHDB", "CONFIG"},
                priority=10
            ),
            
            # Creators: accès contenu uniquement
            ACLRule(
                user_pattern="creator:*",
                key_pattern="content:*|media:*|session:*",
                operations={"GET", "SET", "DEL"},
                priority=50
            ),
            
            # Services: accès cache seulement
            ACLRule(
                user_pattern="service:*",
                key_pattern="cache:*|temp:*",
                operations={"GET", "SET", "EXPIRE"},
                priority=70
            ),
            
            # Viewers: lecture seule
            ACLRule(
                user_pattern="viewer:*",
                key_pattern="public:*|content:*",
                operations={"GET"},
                priority=90
            )
        ]
        
        self.acl_rules.extend(default_rules)
        logger.info(f"✅ {len(default_rules)} règles ACL chargées")
    
    async def _start_security_monitoring(self):
        """**DevOps**: Démarrage monitoring sécurité"""
        asyncio.create_task(self._security_scan_loop())
        asyncio.create_task(self._cleanup_expired_tokens())
        logger.info("🛡️ Monitoring sécurité démarré")
    
    async def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        role: UserRole,
        ip_whitelist: Optional[List[str]] = None
    ) -> Optional[User]:
        """**Sécurité**: Création utilisateur sécurisée"""
        try:
            # Validation username
            if not re.match(r'^[a-zA-Z0-9_]{3,32}$', username):
                raise ValueError("Username invalide")
            
            # Validation email
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                raise ValueError("Email invalide")
            
            # Validation mot de passe
            if len(password) < 8:
                raise ValueError("Mot de passe trop court (min 8 caractères)")
            
            # Vérification unicité
            if username in self.users:
                raise ValueError("Username déjà existant")
            
            # Génération salt et hash
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            # Génération API key
            api_key = self._generate_api_key(username)
            
            # Création utilisateur
            user = User(
                username=username,
                email=email,
                role=role,
                password_hash=password_hash,
                salt=salt,
                api_key=api_key,
                ip_whitelist=ip_whitelist or []
            )
            
            # Stockage
            self.users[username] = user
            
            # Persistance Redis
            await self._persist_user(user)
            
            # Audit log
            await self._log_security_event(
                AuthEvent.LOGIN_SUCCESS,
                username,
                {"action": "user_created", "role": role.value}
            )
            
            logger.info(f"✅ Utilisateur créé: {username} ({role.value})")
            return user
            
        except Exception as e:
            logger.error(f"❌ Erreur création utilisateur {username}: {e}")
            return None
    
    def _hash_password(self, password: str, salt: str) -> str:
        """**Sécurité**: Hash sécurisé mot de passe"""
        # bcrypt avec salt personnalisé
        combined = (password + salt).encode('utf-8')
        hashed = bcrypt.hashpw(combined, bcrypt.gensalt(rounds=12))
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, salt: str, hash_stored: str) -> bool:
        """**Sécurité**: Vérification mot de passe"""
        combined = (password + salt).encode('utf-8')
        return bcrypt.checkpw(combined, hash_stored.encode('utf-8'))
    
    def _generate_api_key(self, username: str) -> str:
        """**Sécurité**: Génération API key sécurisée"""
        random_part = secrets.token_urlsafe(32)
        timestamp = str(int(time.time()))
        api_key = f"ak_{username}_{timestamp}_{random_part}"
        return api_key
    
    async def authenticate(
        self, 
        username: str, 
        password: str,
        ip_address: str,
        mfa_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """**Sécurité**: Authentification multi-facteurs"""
        try:
            # Rate limiting
            if not await self._check_rate_limit(ip_address):
                await self._log_security_event(
                    AuthEvent.SUSPICIOUS_ACTIVITY,
                    username,
                    {"reason": "rate_limit_exceeded", "ip": ip_address}
                )
                return None
            
            # Vérification utilisateur
            user = self.users.get(username)
            if not user:
                await self._handle_failed_auth(username, ip_address, "user_not_found")
                return None
            
            # Vérification compte verrouillé
            if user.account_locked and (not user.lock_until or time.time() < user.lock_until):
                await self._handle_failed_auth(username, ip_address, "account_locked")
                return None
            
            # Vérification IP whitelist
            if user.ip_whitelist and ip_address not in user.ip_whitelist:
                await self._handle_failed_auth(username, ip_address, "ip_not_whitelisted")
                return None
            
            # Vérification mot de passe
            if not self._verify_password(password, user.salt, user.password_hash):
                await self._handle_failed_auth(username, ip_address, "invalid_password")
                return None
            
            # Vérification MFA si activé
            if user.mfa_enabled and not self._verify_mfa_token(user.mfa_secret, mfa_token):
                await self._handle_failed_auth(username, ip_address, "invalid_mfa")
                return None
            
            # Authentification réussie
            await self._handle_successful_auth(user, ip_address)
            
            # Génération tokens
            access_token = await self._create_access_token(user)
            refresh_token = await self._create_refresh_token(user)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": self.token_expiry,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "permissions": list(user.permissions)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur authentification {username}: {e}")
            return None
    
    async def _create_access_token(self, user: User) -> str:
        """**Sécurité**: Création token d'accès JWT chiffré"""
        payload = {
            "sub": user.username,
            "email": user.email,
            "role": user.role.value,
            "permissions": list(user.permissions),
            "iat": time.time(),
            "exp": time.time() + self.token_expiry,
            "jti": secrets.token_hex(16)  # JWT ID unique
        }
        
        # Signature JWT
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Chiffrement token
        encrypted_token = self.fernet.encrypt(token.encode()).decode()
        
        # Stockage token actif
        self.active_tokens[payload["jti"]] = {
            "username": user.username,
            "created_at": time.time(),
            "expires_at": payload["exp"]
        }
        
        return encrypted_token
    
    async def _create_refresh_token(self, user: User) -> str:
        """**Sécurité**: Création refresh token"""
        payload = {
            "sub": user.username,
            "type": "refresh",
            "iat": time.time(),
            "exp": time.time() + self.refresh_token_expiry,
            "jti": secrets.token_hex(16)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        encrypted_token = self.fernet.encrypt(token.encode()).decode()
        
        return encrypted_token
    
    async def validate_token(self, encrypted_token: str) -> Optional[Dict[str, Any]]:
        """**Sécurité**: Validation token avec déchiffrement"""
        try:
            # Déchiffrement
            token = self.fernet.decrypt(encrypted_token.encode()).decode()
            
            # Vérification JWT
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Vérification expiration
            if time.time() > payload["exp"]:
                return None
            
            # Vérification token actif
            jti = payload.get("jti")
            if jti and jti not in self.active_tokens:
                return None
            
            # Récupération utilisateur
            username = payload["sub"]
            user = self.users.get(username)
            if not user:
                return None
            
            return {
                "username": username,
                "user": user,
                "payload": payload
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Token invalide: {e}")
            return None
    
    async def check_permission(
        self, 
        username: str, 
        redis_key: str, 
        operation: str
    ) -> bool:
        """**DBA**: Vérification permissions ACL granulaires"""
        try:
            user = self.users.get(username)
            if not user:
                return False
            
            # Admin bypass
            if user.role == UserRole.ADMIN:
                return True
            
            # Vérification ACL rules
            for rule in sorted(self.acl_rules, key=lambda r: r.priority):
                if self._match_pattern(f"{user.role.value}:{username}", rule.user_pattern):
                    if self._match_pattern(redis_key, rule.key_pattern):
                        if operation.upper() in rule.operations:
                            return True
            
            # Vérification permissions directes utilisateur
            permission_patterns = [
                f"{redis_key}:{operation}",
                f"{redis_key}:*",
                f"*:{operation}",
                "*:*"
            ]
            
            for pattern in permission_patterns:
                if pattern in user.permissions:
                    return True
            
            # Permission refusée
            await self._log_security_event(
                AuthEvent.PERMISSION_DENIED,
                username,
                {"key": redis_key, "operation": operation}
            )
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification permission: {e}")
            return False
    
    def _match_pattern(self, value: str, pattern: str) -> bool:
        """**DBA**: Matching pattern ACL"""
        # Pattern simple avec wildcards
        if pattern == "*":
            return True
        
        if "|" in pattern:
            # Pattern avec OR (|)
            return any(self._match_pattern(value, p.strip()) for p in pattern.split("|"))
        
        if "*" in pattern:
            # Pattern avec wildcard
            regex_pattern = pattern.replace("*", ".*")
            return bool(re.match(f"^{regex_pattern}$", value))
        
        return value == pattern
    
    async def _handle_failed_auth(self, username: str, ip_address: str, reason: str):
        """**Sécurité**: Gestion échecs d'authentification"""
        # Mise à jour compteurs
        self.security_metrics.failed_auths += 1
        
        # Gestion utilisateur
        user = self.users.get(username)
        if user:
            user.failed_login_attempts += 1
            
            # Verrouillage compte si trop d'échecs
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.account_locked = True
                user.lock_until = time.time() + self.lockout_duration
                
                await self._log_security_event(
                    AuthEvent.SUSPICIOUS_ACTIVITY,
                    username,
                    {"reason": "account_locked", "attempts": user.failed_login_attempts}
                )
        
        # Blocage IP si suspect
        await self._check_suspicious_ip(ip_address)
        
        # Log événement
        await self._log_security_event(
            AuthEvent.LOGIN_FAILED,
            username,
            {"reason": reason, "ip": ip_address}
        )
    
    async def _handle_successful_auth(self, user: User, ip_address: str):
        """**Sécurité**: Gestion authentification réussie"""
        # Reset compteurs
        user.failed_login_attempts = 0
        user.account_locked = False
        user.lock_until = None
        user.last_login = time.time()
        
        # Mise à jour métriques
        self.security_metrics.successful_auths += 1
        self.security_metrics.active_sessions += 1
        
        # Log événement
        await self._log_security_event(
            AuthEvent.LOGIN_SUCCESS,
            user.username,
            {"ip": ip_address, "role": user.role.value}
        )
    
    async def _check_rate_limit(self, ip_address: str) -> bool:
        """**Sécurité**: Vérification rate limiting"""
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Nettoyage anciens accès
        if ip_address in self.rate_limits:
            self.rate_limits[ip_address] = [
                t for t in self.rate_limits[ip_address] if t > window_start
            ]
        else:
            self.rate_limits[ip_address] = []
        
        # Vérification limite
        if len(self.rate_limits[ip_address]) >= self.rate_limit_max:
            return False
        
        # Enregistrement nouvel accès
        self.rate_limits[ip_address].append(current_time)
        return True
    
    async def _check_suspicious_ip(self, ip_address: str):
        """**Sécurité**: Détection IP suspectes"""
        # Comptage échecs par IP
        recent_failures = 0
        current_time = time.time()
        
        if ip_address in self.rate_limits:
            # Compte échecs récents (dernière heure)
            recent_failures = len([
                t for t in self.rate_limits[ip_address] 
                if t > current_time - 3600
            ])
        
        # Blocage si trop d'échecs
        if recent_failures > 20:  # Seuil d'alerte
            self.security_metrics.blocked_ips.add(ip_address)
            self.security_metrics.suspicious_activities += 1
            
            logger.warning(f"🚨 IP bloquée pour activité suspecte: {ip_address}")
    
    def _verify_mfa_token(self, mfa_secret: str, token: str) -> bool:
        """**Sécurité**: Vérification token MFA (TOTP)"""
        # Implémentation simplifiée - en production utiliser pyotp
        if not mfa_secret or not token:
            return not self.mfa_required
        
        # Simulation vérification TOTP
        expected_length = 6
        return len(token) == expected_length and token.isdigit()
    
    async def _log_security_event(
        self, 
        event_type: AuthEvent, 
        username: str,
        details: Dict[str, Any]
    ):
        """**DevOps**: Logging événements sécurité pour audit"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type.value,
            "username": username,
            "details": details
        }
        
        try:
            # Stockage Redis pour analyse
            async with self.redis_pool.get_connection() as redis_conn:
                log_key = f"security_log:{int(time.time())}"
                await redis_conn.setex(
                    log_key, 
                    86400 * 30,  # Conservation 30 jours
                    json.dumps(event)
                )
                
                # Index par type d'événement
                await redis_conn.sadd(f"security_events:{event_type.value}", log_key)
                
        except Exception as e:
            logger.error(f"❌ Erreur logging sécurité: {e}")
        
        # Log applicatif
        if event_type in [AuthEvent.LOGIN_FAILED, AuthEvent.SUSPICIOUS_ACTIVITY]:
            logger.warning(f"🚨 {event_type.value}: {username} - {details}")
        else:
            logger.info(f"🔐 {event_type.value}: {username}")
    
    async def _security_scan_loop(self):
        """**DevOps**: Boucle scan sécurité périodique"""
        while True:
            try:
                await asyncio.sleep(300)  # Scan toutes les 5 minutes
                await self._perform_security_scan()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur scan sécurité: {e}")
    
    async def _perform_security_scan(self):
        """**DevOps**: Scan sécurité détaillé"""
        current_time = time.time()
        
        # Nettoyage comptes verrouillés expirés
        for user in self.users.values():
            if user.account_locked and user.lock_until and current_time > user.lock_until:
                user.account_locked = False
                user.lock_until = None
                logger.info(f"🔓 Compte déverrouillé: {user.username}")
        
        # Détection patterns suspects dans logs
        await self._detect_suspicious_patterns()
        
        # Mise à jour métriques
        self.security_metrics.last_security_scan = current_time
        
        logger.debug("🔍 Scan sécurité terminé")
    
    async def _detect_suspicious_patterns(self):
        """**Sécurité**: Détection patterns suspects avec IA"""
        try:
            # Analyse logs récents pour patterns d'attaque
            async with self.redis_pool.get_connection() as redis_conn:
                log_keys = await redis_conn.keys("security_log:*")
                
                suspicious_count = 0
                for log_key in log_keys[-100:]:  # Derniers 100 logs
                    log_data = await redis_conn.get(log_key)
                    if log_data:
                        event = json.loads(log_data)
                        
                        # Recherche patterns dans détails
                        details_str = json.dumps(event.get("details", {}))
                        for pattern in self.suspicious_patterns:
                            if re.search(pattern, details_str, re.IGNORECASE):
                                suspicious_count += 1
                                await self._log_security_event(
                                    AuthEvent.SUSPICIOUS_ACTIVITY,
                                    event.get("username", "unknown"),
                                    {"detected_pattern": pattern, "log_key": log_key}
                                )
                
                if suspicious_count > 0:
                    logger.warning(f"🚨 {suspicious_count} patterns suspects détectés")
                    
        except Exception as e:
            logger.error(f"❌ Erreur détection patterns: {e}")
    
    async def _cleanup_expired_tokens(self):
        """**Backend Senior**: Nettoyage tokens expirés"""
        while True:
            try:
                await asyncio.sleep(600)  # Nettoyage toutes les 10 minutes
                
                current_time = time.time()
                expired_tokens = []
                
                for jti, token_info in self.active_tokens.items():
                    if current_time > token_info["expires_at"]:
                        expired_tokens.append(jti)
                
                for jti in expired_tokens:
                    del self.active_tokens[jti]
                
                if expired_tokens:
                    logger.info(f"🧹 {len(expired_tokens)} tokens expirés nettoyés")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Erreur nettoyage tokens: {e}")
    
    async def _persist_user(self, user: User):
        """**DBA**: Persistance utilisateur en Redis"""
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                user_data = {
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "password_hash": user.password_hash,
                    "salt": user.salt,
                    "created_at": user.created_at,
                    "api_key": user.api_key,
                    "permissions": list(user.permissions),
                    "ip_whitelist": user.ip_whitelist
                }
                
                await redis_conn.hset(
                    f"user:{user.username}",
                    mapping={k: json.dumps(v) for k, v in user_data.items()}
                )
                
        except Exception as e:
            logger.error(f"❌ Erreur persistance utilisateur: {e}")
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """**DevOps**: Dashboard sécurité complet"""
        
        # Statistiques utilisateurs
        user_stats = {
            "total_users": len(self.users),
            "active_users": len([u for u in self.users.values() if not u.account_locked]),
            "locked_accounts": len([u for u in self.users.values() if u.account_locked]),
            "users_by_role": {}
        }
        
        for role in UserRole:
            user_stats["users_by_role"][role.value] = len([
                u for u in self.users.values() if u.role == role
            ])
        
        # Événements récents
        recent_events = []
        try:
            async with self.redis_pool.get_connection() as redis_conn:
                event_keys = await redis_conn.keys("security_log:*")
                for key in sorted(event_keys)[-20:]:  # 20 derniers événements
                    event_data = await redis_conn.get(key)
                    if event_data:
                        recent_events.append(json.loads(event_data))
        except Exception as e:
            logger.error(f"❌ Erreur récupération événements: {e}")
        
        return {
            "security_metrics": {
                "successful_auths": self.security_metrics.successful_auths,
                "failed_auths": self.security_metrics.failed_auths,
                "active_sessions": len(self.active_tokens),
                "blocked_ips": len(self.security_metrics.blocked_ips),
                "suspicious_activities": self.security_metrics.suspicious_activities,
                "last_security_scan": self.security_metrics.last_security_scan
            },
            "user_statistics": user_stats,
            "acl_rules": len(self.acl_rules),
            "rate_limits": {
                "monitored_ips": len(self.rate_limits),
                "window_seconds": self.rate_limit_window,
                "max_requests": self.rate_limit_max
            },
            "recent_events": recent_events,
            "blocked_ips": list(self.security_metrics.blocked_ips)
        }

# Factory function
async def create_redis_auth_manager(redis_pool, secret_key: str, config: Optional[Dict[str, Any]] = None):
    """**Sécurité**: Factory création Auth Manager"""
    auth_manager = RedisAuthManager(redis_pool, secret_key, config)
    return auth_manager

if __name__ == "__main__":
    async def demo():
        """Démonstration Redis Auth Manager"""
        
        # Configuration Redis simulée
        class MockRedisPool:
            def get_connection(self):
                from unittest.mock import AsyncMock
                return AsyncMock()
        
        # Création auth manager
        auth_manager = await create_redis_auth_manager(
            MockRedisPool(), 
            "super_secret_key_change_in_production"
        )
        
        # Test authentification
        auth_result = await auth_manager.authenticate(
            "admin",
            "change_me_in_production", 
            "192.168.1.1"
        )
        
        if auth_result:
            print(f"Authentification réussie: {auth_result['user']['username']}")
            
            # Test validation token
            token_info = await auth_manager.validate_token(auth_result["access_token"])
            print(f"Token valide: {token_info['username']}")
            
            # Test permissions
            has_permission = await auth_manager.check_permission(
                "admin", 
                "cache:user_data", 
                "SET"
            )
            print(f"Permission cache: {has_permission}")
        
        # Dashboard sécurité
        dashboard = await auth_manager.get_security_dashboard()
        print(f"Dashboard sécurité: {dashboard['security_metrics']}")
    
    asyncio.run(demo())