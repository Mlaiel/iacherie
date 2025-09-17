#!/usr/bin/env python3
"""
🔐 Token Security Manager - Advanced JWT & Session Security
==========================================================

Enterprise-grade token and session management for Ainflue platform.
JWT management, token rotation, secure storage, and session security.

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
import secrets
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Set
import base64
import os

import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class TokenType(Enum):
    """Types de tokens"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    SESSION_TOKEN = "session_token"
    API_TOKEN = "api_token"
    CREATOR_TOKEN = "creator_token"
    PAYMENT_TOKEN = "payment_token"
    TEMPORARY_TOKEN = "temporary_token"
    WEBHOOK_TOKEN = "webhook_token"


class TokenStatus(Enum):
    """Statuts de token"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    ROTATION_PENDING = "rotation_pending"


class SecurityLevel(Enum):
    """Niveaux de sécurité"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"


class SessionState(Enum):
    """États de session"""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    CONCURRENT_LIMIT_EXCEEDED = "concurrent_limit_exceeded"


@dataclass
class TokenMetadata:
    """Métadonnées de token"""
    token_id: str
    user_id: str
    creator_id: Optional[str] = None
    token_type: TokenType = TokenType.ACCESS_TOKEN
    scopes: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    custom_claims: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecureToken:
    """Représentation sécurisée d'un token"""
    token_id: str
    token_value: str
    token_hash: str
    metadata: TokenMetadata
    status: TokenStatus = TokenStatus.ACTIVE
    security_level: SecurityLevel = SecurityLevel.STANDARD
    rotation_schedule: Optional[datetime] = None
    blacklist_reason: Optional[str] = None


@dataclass
class SessionInfo:
    """Informations de session"""
    session_id: str
    user_id: str
    creator_id: Optional[str] = None
    state: SessionState = SessionState.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    security_flags: List[str] = field(default_factory=list)
    concurrent_sessions: int = 1
    max_concurrent: int = 3
    activity_log: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TokenValidationResult:
    """Résultat de validation de token"""
    is_valid: bool
    token_id: Optional[str] = None
    user_id: Optional[str] = None
    creator_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    validation_errors: List[str] = field(default_factory=list)
    security_warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class JWTManager:
    """Gestionnaire JWT avancé"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Génération des clés RSA pour JWT
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Configuration JWT
        self.jwt_config = {
            'algorithm': 'RS256',
            'access_token_expire_minutes': 15,
            'refresh_token_expire_days': 30,
            'session_token_expire_hours': 24,
            'api_token_expire_days': 365,
            'creator_token_expire_hours': 12,
            'payment_token_expire_minutes': 5,
            'temporary_token_expire_minutes': 10,
            'webhook_token_expire_hours': 48
        }
        
        # Issuer et audience
        self.issuer = "ainflue.platform"
        self.audience = "ainflue.creators"
        
    async def create_jwt_token(self, 
                              metadata: TokenMetadata,
                              custom_claims: Optional[Dict[str, Any]] = None) -> str:
        """Création d'un token JWT"""
        try:
            now = datetime.utcnow()
            
            # Déterminer expiration selon type de token
            expire_config_key = f"{metadata.token_type.value}_expire_minutes"
            if expire_config_key.endswith('_days'):
                expire_config_key = expire_config_key.replace('_days', '_expire_days')
            elif expire_config_key.endswith('_hours'):
                expire_config_key = expire_config_key.replace('_hours', '_expire_hours')
                
            if expire_config_key in self.jwt_config:
                if 'days' in expire_config_key:
                    expire_delta = timedelta(days=self.jwt_config[expire_config_key])
                elif 'hours' in expire_config_key:
                    expire_delta = timedelta(hours=self.jwt_config[expire_config_key])
                else:
                    expire_delta = timedelta(minutes=self.jwt_config[expire_config_key])
            else:
                expire_delta = timedelta(minutes=15)  # Default
                
            expires_at = now + expire_delta
            metadata.expires_at = expires_at
            
            # Claims JWT standard
            claims = {
                'iss': self.issuer,
                'aud': self.audience,
                'sub': metadata.user_id,
                'iat': int(now.timestamp()),
                'exp': int(expires_at.timestamp()),
                'jti': metadata.token_id,
                'token_type': metadata.token_type.value,
                'scopes': metadata.scopes,
                'permissions': metadata.permissions
            }
            
            # Claims spécifiques Ainflue
            if metadata.creator_id:
                claims['creator_id'] = metadata.creator_id
                
            if metadata.ip_address:
                claims['ip'] = metadata.ip_address
                
            if metadata.device_id:
                claims['device_id'] = metadata.device_id
                
            # Claims personnalisés
            if custom_claims:
                claims.update(custom_claims)
                
            if metadata.custom_claims:
                claims.update(metadata.custom_claims)
                
            # Sérialisation de la clé privée
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Génération du token
            token = jwt.encode(claims, private_pem, algorithm=self.jwt_config['algorithm'])
            
            self.logger.debug(f"JWT token created: {metadata.token_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"JWT token creation failed: {str(e)}")
            raise
            
    async def verify_jwt_token(self, token: str) -> TokenValidationResult:
        """Vérification d'un token JWT"""
        try:
            # Sérialisation de la clé publique
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Décodage et vérification
            payload = jwt.decode(
                token,
                public_pem,
                algorithms=[self.jwt_config['algorithm']],
                audience=self.audience,
                issuer=self.issuer
            )
            
            # Extraction des informations
            result = TokenValidationResult(
                is_valid=True,
                token_id=payload.get('jti'),
                user_id=payload.get('sub'),
                creator_id=payload.get('creator_id'),
                scopes=payload.get('scopes', []),
                permissions=payload.get('permissions', []),
                expires_at=datetime.fromtimestamp(payload.get('exp', 0)),
                metadata={
                    'token_type': payload.get('token_type'),
                    'ip': payload.get('ip'),
                    'device_id': payload.get('device_id'),
                    'issued_at': datetime.fromtimestamp(payload.get('iat', 0))
                }
            )
            
            self.logger.debug(f"JWT token verified: {result.token_id}")
            return result
            
        except jwt.ExpiredSignatureError:
            return TokenValidationResult(
                is_valid=False,
                validation_errors=["Token has expired"]
            )
        except jwt.InvalidTokenError as e:
            return TokenValidationResult(
                is_valid=False,
                validation_errors=[f"Invalid token: {str(e)}"]
            )
        except Exception as e:
            self.logger.error(f"JWT token verification failed: {str(e)}")
            return TokenValidationResult(
                is_valid=False,
                validation_errors=[f"Verification error: {str(e)}"]
            )
            
    async def refresh_jwt_token(self, refresh_token: str) -> Optional[str]:
        """Rafraîchissement d'un token JWT"""
        validation_result = await self.verify_jwt_token(refresh_token)
        
        if not validation_result.is_valid:
            return None
            
        # Vérifier que c'est un refresh token
        if validation_result.metadata.get('token_type') != TokenType.REFRESH_TOKEN.value:
            return None
            
        # Créer nouveau token d'accès
        new_metadata = TokenMetadata(
            token_id=f"access_{uuid.uuid4().hex}",
            user_id=validation_result.user_id,
            creator_id=validation_result.creator_id,
            token_type=TokenType.ACCESS_TOKEN,
            scopes=validation_result.scopes,
            permissions=validation_result.permissions
        )
        
        return await self.create_jwt_token(new_metadata)


class TokenRotationManager:
    """Gestionnaire de rotation des tokens"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Politiques de rotation par type de token
        self.rotation_policies = {
            TokenType.ACCESS_TOKEN: timedelta(minutes=15),
            TokenType.REFRESH_TOKEN: timedelta(days=7),
            TokenType.SESSION_TOKEN: timedelta(hours=12),
            TokenType.API_TOKEN: timedelta(days=90),
            TokenType.CREATOR_TOKEN: timedelta(hours=6),
            TokenType.PAYMENT_TOKEN: timedelta(minutes=5),
            TokenType.TEMPORARY_TOKEN: timedelta(minutes=5),
            TokenType.WEBHOOK_TOKEN: timedelta(days=1)
        }
        
        # Tokens en cours de rotation
        self.rotation_queue: Dict[str, SecureToken] = {}
        
    async def should_rotate_token(self, token: SecureToken) -> bool:
        """Détermine si un token doit être pivoté"""
        if token.status != TokenStatus.ACTIVE:
            return False
            
        # Vérifier politique de rotation
        if token.metadata.token_type in self.rotation_policies:
            rotation_interval = self.rotation_policies[token.metadata.token_type]
            time_since_creation = datetime.utcnow() - token.metadata.created_at
            
            if time_since_creation >= rotation_interval:
                return True
                
        # Vérifier rotation programmée
        if token.rotation_schedule and datetime.utcnow() >= token.rotation_schedule:
            return True
            
        # Vérifier usage maximum
        if (token.metadata.max_usage and 
            token.metadata.usage_count >= token.metadata.max_usage):
            return True
            
        return False
        
    async def rotate_token(self, 
                          old_token: SecureToken,
                          token_manager: 'TokenSecurityManager') -> SecureToken:
        """Rotation d'un token"""
        self.logger.info(f"Rotating token {old_token.token_id}")
        
        # Créer nouveau token avec même métadonnées
        new_metadata = TokenMetadata(
            token_id=f"{old_token.metadata.token_type.value}_{uuid.uuid4().hex}",
            user_id=old_token.metadata.user_id,
            creator_id=old_token.metadata.creator_id,
            token_type=old_token.metadata.token_type,
            scopes=old_token.metadata.scopes.copy(),
            permissions=old_token.metadata.permissions.copy(),
            ip_address=old_token.metadata.ip_address,
            user_agent=old_token.metadata.user_agent,
            device_id=old_token.metadata.device_id,
            custom_claims=old_token.metadata.custom_claims.copy()
        )
        
        # Générer nouveau token
        new_token = await token_manager.create_token(
            new_metadata,
            security_level=old_token.security_level
        )
        
        # Marquer ancien token pour révocation
        old_token.status = TokenStatus.ROTATION_PENDING
        
        # Programmer révocation après période de grâce
        await self._schedule_token_revocation(old_token, timedelta(minutes=5))
        
        return new_token
        
    async def _schedule_token_revocation(self, token: SecureToken, grace_period: timedelta):
        """Programmer la révocation d'un token après période de grâce"""
        # Simulation - en production, utiliser scheduler/queue
        self.logger.info(f"Token {token.token_id} scheduled for revocation in {grace_period}")
        
        # Ajouter à la queue de rotation
        self.rotation_queue[token.token_id] = token


class SessionManager:
    """Gestionnaire de sessions sécurisées"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> session_ids
        
        # Configuration des sessions
        self.session_config = {
            'max_concurrent_sessions': 5,
            'session_timeout_minutes': 30,
            'idle_timeout_minutes': 15,
            'max_session_duration_hours': 24,
            'require_device_fingerprint': True,
            'track_geolocation': True
        }
        
    async def create_session(self, 
                           user_id: str,
                           creator_id: Optional[str] = None,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None,
                           device_fingerprint: Optional[str] = None) -> SessionInfo:
        """Création d'une session sécurisée"""
        session_id = f"session_{uuid.uuid4().hex}"
        
        # Vérifier limites de sessions concurrentes
        await self._enforce_concurrent_session_limits(user_id)
        
        # Créer session
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            creator_id=creator_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(
                hours=self.session_config['max_session_duration_hours']
            ),
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            max_concurrent=self.session_config['max_concurrent_sessions']
        )
        
        # Stocker session
        self.active_sessions[session_id] = session
        
        # Indexer par utilisateur
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session_id)
        
        # Logging d'activité
        await self._log_session_activity(session, "session_created")
        
        self.logger.info(f"Session created: {session_id} for user {user_id}")
        return session
        
    async def validate_session(self, session_id: str) -> Optional[SessionInfo]:
        """Validation d'une session"""
        if session_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[session_id]
        
        # Vérifier état
        if session.state != SessionState.ACTIVE:
            return None
            
        # Vérifier expiration
        if session.expires_at and datetime.utcnow() >= session.expires_at:
            session.state = SessionState.EXPIRED
            await self._log_session_activity(session, "session_expired")
            return None
            
        # Vérifier timeout d'inactivité
        idle_timeout = timedelta(minutes=self.session_config['idle_timeout_minutes'])
        if datetime.utcnow() - session.last_activity >= idle_timeout:
            session.state = SessionState.IDLE
            await self._log_session_activity(session, "session_idle")
            return None
            
        # Mettre à jour dernière activité
        session.last_activity = datetime.utcnow()
        await self._log_session_activity(session, "session_activity")
        
        return session
        
    async def terminate_session(self, session_id: str, reason: str = "user_logout"):
        """Terminer une session"""
        if session_id not in self.active_sessions:
            return
            
        session = self.active_sessions[session_id]
        session.state = SessionState.TERMINATED
        
        # Logging
        await self._log_session_activity(session, f"session_terminated_{reason}")
        
        # Nettoyer
        del self.active_sessions[session_id]
        if session.user_id in self.user_sessions:
            if session_id in self.user_sessions[session.user_id]:
                self.user_sessions[session.user_id].remove(session_id)
                
        self.logger.info(f"Session terminated: {session_id} - {reason}")
        
    async def terminate_all_user_sessions(self, user_id: str, reason: str = "security"):
        """Terminer toutes les sessions d'un utilisateur"""
        if user_id not in self.user_sessions:
            return
            
        session_ids = self.user_sessions[user_id].copy()
        for session_id in session_ids:
            await self.terminate_session(session_id, f"bulk_termination_{reason}")
            
        self.logger.info(f"All sessions terminated for user {user_id} - {reason}")
        
    async def _enforce_concurrent_session_limits(self, user_id: str):
        """Appliquer les limites de sessions concurrentes"""
        if user_id not in self.user_sessions:
            return
            
        active_sessions = []
        for session_id in self.user_sessions[user_id]:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if session.state == SessionState.ACTIVE:
                    active_sessions.append(session_id)
                    
        max_concurrent = self.session_config['max_concurrent_sessions']
        if len(active_sessions) >= max_concurrent:
            # Terminer la session la plus ancienne
            oldest_session_id = min(active_sessions, 
                                   key=lambda sid: self.active_sessions[sid].created_at)
            await self.terminate_session(oldest_session_id, "concurrent_limit_exceeded")
            
    async def _log_session_activity(self, session: SessionInfo, activity: str):
        """Logger l'activité de session"""
        activity_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'activity': activity,
            'ip_address': session.ip_address,
            'user_agent': session.user_agent
        }
        
        session.activity_log.append(activity_entry)
        
        # Garder seulement les 100 dernières activités
        if len(session.activity_log) > 100:
            session.activity_log = session.activity_log[-100:]


class TokenSecurityManager:
    """
    Gestionnaire de sécurité des tokens enterprise-grade
    
    Fonctionnalités:
    - Génération et gestion sécurisée des tokens
    - Rotation automatique des tokens
    - Sessions sécurisées avec suivi d'activité
    - Validation en temps réel
    - Révocation et blacklisting
    - Audit complet des activités
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jwt_manager = JWTManager()
        self.rotation_manager = TokenRotationManager()
        self.session_manager = SessionManager()
        
        # Stockage des tokens
        self.tokens: Dict[str, SecureToken] = {}
        self.token_hashes: Dict[str, str] = {}  # hash -> token_id
        self.blacklisted_tokens: Set[str] = set()
        
        # Configuration sécurité
        self.security_config = {
            'require_strong_tokens': True,
            'enable_automatic_rotation': True,
            'track_token_usage': True,
            'enable_geolocation_binding': True,
            'enable_device_binding': True,
            'max_token_lifetime_hours': 24,
            'suspicious_activity_threshold': 10
        }
        
        # Métriques
        self.metrics = {
            'tokens_created': 0,
            'tokens_validated': 0,
            'tokens_revoked': 0,
            'tokens_rotated': 0,
            'suspicious_activities': 0,
            'sessions_created': 0,
            'sessions_terminated': 0
        }
        
        self.logger.info("Token Security Manager initialized")
        
    async def create_token(self, 
                          metadata: TokenMetadata,
                          security_level: SecurityLevel = SecurityLevel.STANDARD) -> SecureToken:
        """Création d'un token sécurisé"""
        try:
            # Génération du token JWT
            token_value = await self.jwt_manager.create_jwt_token(metadata)
            
            # Calcul du hash pour stockage sécurisé
            token_hash = hashlib.sha256(token_value.encode()).hexdigest()
            
            # Création de l'objet token sécurisé
            secure_token = SecureToken(
                token_id=metadata.token_id,
                token_value=token_value,
                token_hash=token_hash,
                metadata=metadata,
                status=TokenStatus.ACTIVE,
                security_level=security_level
            )
            
            # Planifier rotation si activée
            if self.security_config['enable_automatic_rotation']:
                if metadata.token_type in self.rotation_manager.rotation_policies:
                    rotation_interval = self.rotation_manager.rotation_policies[metadata.token_type]
                    secure_token.rotation_schedule = datetime.utcnow() + rotation_interval
                    
            # Stocker token
            self.tokens[metadata.token_id] = secure_token
            self.token_hashes[token_hash] = metadata.token_id
            
            # Métriques
            self.metrics['tokens_created'] += 1
            
            self.logger.info(f"Token created: {metadata.token_id} ({metadata.token_type.value})")
            return secure_token
            
        except Exception as e:
            self.logger.error(f"Token creation failed: {str(e)}")
            raise
            
    async def validate_token(self, token_value: str) -> TokenValidationResult:
        """Validation complète d'un token"""
        try:
            # Vérifier blacklist
            token_hash = hashlib.sha256(token_value.encode()).hexdigest()
            if token_hash in self.blacklisted_tokens:
                return TokenValidationResult(
                    is_valid=False,
                    validation_errors=["Token is blacklisted"]
                )
                
            # Validation JWT
            jwt_result = await self.jwt_manager.verify_jwt_token(token_value)
            if not jwt_result.is_valid:
                return jwt_result
                
            # Vérifier existence du token
            if token_hash not in self.token_hashes:
                return TokenValidationResult(
                    is_valid=False,
                    validation_errors=["Token not found in registry"]
                )
                
            token_id = self.token_hashes[token_hash]
            if token_id not in self.tokens:
                return TokenValidationResult(
                    is_valid=False,
                    validation_errors=["Token registry inconsistency"]
                )
                
            secure_token = self.tokens[token_id]
            
            # Vérifier statut
            if secure_token.status != TokenStatus.ACTIVE:
                return TokenValidationResult(
                    is_valid=False,
                    validation_errors=[f"Token status: {secure_token.status.value}"]
                )
                
            # Vérifier rotation
            if await self.rotation_manager.should_rotate_token(secure_token):
                jwt_result.security_warnings.append("Token rotation recommended")
                
            # Mettre à jour usage
            secure_token.metadata.usage_count += 1
            secure_token.metadata.last_used = datetime.utcnow()
            
            # Métriques
            self.metrics['tokens_validated'] += 1
            
            return jwt_result
            
        except Exception as e:
            self.logger.error(f"Token validation failed: {str(e)}")
            return TokenValidationResult(
                is_valid=False,
                validation_errors=[f"Validation error: {str(e)}"]
            )
            
    async def revoke_token(self, token_id: str, reason: str = "manual_revocation"):
        """Révocation d'un token"""
        if token_id not in self.tokens:
            self.logger.warning(f"Attempted to revoke non-existent token: {token_id}")
            return
            
        token = self.tokens[token_id]
        token.status = TokenStatus.REVOKED
        token.blacklist_reason = reason
        
        # Ajouter à la blacklist
        self.blacklisted_tokens.add(token.token_hash)
        
        # Métriques
        self.metrics['tokens_revoked'] += 1
        
        self.logger.info(f"Token revoked: {token_id} - {reason}")
        
    async def rotate_token(self, token_id: str) -> Optional[SecureToken]:
        """Rotation manuelle d'un token"""
        if token_id not in self.tokens:
            return None
            
        old_token = self.tokens[token_id]
        if old_token.status != TokenStatus.ACTIVE:
            return None
            
        # Effectuer rotation
        new_token = await self.rotation_manager.rotate_token(old_token, self)
        
        # Métriques
        self.metrics['tokens_rotated'] += 1
        
        return new_token
        
    async def create_session_with_tokens(self, 
                                       user_id: str,
                                       creator_id: Optional[str] = None,
                                       scopes: Optional[List[str]] = None,
                                       ip_address: Optional[str] = None,
                                       user_agent: Optional[str] = None,
                                       device_fingerprint: Optional[str] = None) -> Tuple[SessionInfo, SecureToken, SecureToken]:
        """Création d'une session avec tokens d'accès et de rafraîchissement"""
        
        # Créer session
        session = await self.session_manager.create_session(
            user_id=user_id,
            creator_id=creator_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint
        )
        
        # Métriques
        self.metrics['sessions_created'] += 1
        
        # Créer token d'accès
        access_metadata = TokenMetadata(
            token_id=f"access_{uuid.uuid4().hex}",
            user_id=user_id,
            creator_id=creator_id,
            token_type=TokenType.ACCESS_TOKEN,
            scopes=scopes or ['read', 'write'],
            permissions=['basic_access'],
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_fingerprint,
            custom_claims={'session_id': session.session_id}
        )
        
        access_token = await self.create_token(access_metadata, SecurityLevel.HIGH)
        
        # Créer token de rafraîchissement
        refresh_metadata = TokenMetadata(
            token_id=f"refresh_{uuid.uuid4().hex}",
            user_id=user_id,
            creator_id=creator_id,
            token_type=TokenType.REFRESH_TOKEN,
            scopes=scopes or ['refresh'],
            permissions=['token_refresh'],
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_fingerprint,
            custom_claims={'session_id': session.session_id}
        )
        
        refresh_token = await self.create_token(refresh_metadata, SecurityLevel.CRITICAL)
        
        return session, access_token, refresh_token
        
    async def terminate_session_and_tokens(self, session_id: str, reason: str = "logout"):
        """Terminer session et révoquer tous ses tokens"""
        # Terminer session
        await self.session_manager.terminate_session(session_id, reason)
        
        # Trouver et révoquer tokens liés à la session
        session_tokens = [
            token for token in self.tokens.values()
            if token.metadata.custom_claims.get('session_id') == session_id
        ]
        
        for token in session_tokens:
            await self.revoke_token(token.token_id, f"session_terminated_{reason}")
            
        # Métriques
        self.metrics['sessions_terminated'] += 1
        
    async def check_token_security(self, token_id: str) -> Dict[str, Any]:
        """Vérification de sécurité approfondie d'un token"""
        if token_id not in self.tokens:
            return {'error': 'Token not found'}
            
        token = self.tokens[token_id]
        metadata = token.metadata
        
        security_assessment = {
            'token_id': token_id,
            'status': token.status.value,
            'security_level': token.security_level.value,
            'age_hours': (datetime.utcnow() - metadata.created_at).total_seconds() / 3600,
            'usage_count': metadata.usage_count,
            'last_used_hours_ago': (datetime.utcnow() - metadata.last_used).total_seconds() / 3600,
            'security_flags': [],
            'recommendations': []
        }
        
        # Vérifications de sécurité
        
        # Âge du token
        if security_assessment['age_hours'] > 24:
            security_assessment['security_flags'].append('token_age_high')
            security_assessment['recommendations'].append('Consider token rotation')
            
        # Usage excessif
        if metadata.usage_count > 1000:
            security_assessment['security_flags'].append('high_usage_count')
            security_assessment['recommendations'].append('Monitor for automated usage')
            
        # Inactivité
        if security_assessment['last_used_hours_ago'] > 1:
            security_assessment['security_flags'].append('token_inactive')
            
        # Token de paiement ancien
        if (metadata.token_type == TokenType.PAYMENT_TOKEN and 
            security_assessment['age_hours'] > 0.1):  # 6 minutes
            security_assessment['security_flags'].append('payment_token_aged')
            security_assessment['recommendations'].append('Immediate rotation required')
            
        # Score de sécurité
        security_score = 1.0
        security_score -= len(security_assessment['security_flags']) * 0.1
        security_assessment['security_score'] = max(0.0, security_score)
        
        return security_assessment
        
    async def get_user_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtenir tous les tokens d'un utilisateur"""
        user_tokens = []
        
        for token in self.tokens.values():
            if token.metadata.user_id == user_id:
                token_info = {
                    'token_id': token.token_id,
                    'token_type': token.metadata.token_type.value,
                    'status': token.status.value,
                    'created_at': token.metadata.created_at.isoformat(),
                    'expires_at': token.metadata.expires_at.isoformat() if token.metadata.expires_at else None,
                    'last_used': token.metadata.last_used.isoformat(),
                    'usage_count': token.metadata.usage_count,
                    'scopes': token.metadata.scopes,
                    'ip_address': token.metadata.ip_address,
                    'device_id': token.metadata.device_id
                }
                user_tokens.append(token_info)
                
        return user_tokens
        
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Métriques de sécurité des tokens"""
        active_tokens = sum(1 for token in self.tokens.values() if token.status == TokenStatus.ACTIVE)
        expired_tokens = sum(1 for token in self.tokens.values() if token.status == TokenStatus.EXPIRED)
        revoked_tokens = sum(1 for token in self.tokens.values() if token.status == TokenStatus.REVOKED)
        
        # Répartition par type
        token_types = {}
        for token in self.tokens.values():
            token_type = token.metadata.token_type.value
            if token_type not in token_types:
                token_types[token_type] = {'active': 0, 'total': 0}
            token_types[token_type]['total'] += 1
            if token.status == TokenStatus.ACTIVE:
                token_types[token_type]['active'] += 1
                
        # Sessions actives
        active_sessions = sum(
            1 for session in self.session_manager.active_sessions.values()
            if session.state == SessionState.ACTIVE
        )
        
        return {
            'total_tokens': len(self.tokens),
            'active_tokens': active_tokens,
            'expired_tokens': expired_tokens,
            'revoked_tokens': revoked_tokens,
            'blacklisted_tokens': len(self.blacklisted_tokens),
            'active_sessions': active_sessions,
            'token_types': token_types,
            'operations': self.metrics,
            'uptime_seconds': time.time()
        }
        
    async def cleanup_expired_tokens(self):
        """Nettoyage des tokens expirés"""
        expired_tokens = []
        
        for token_id, token in self.tokens.items():
            if (token.metadata.expires_at and 
                datetime.utcnow() >= token.metadata.expires_at):
                expired_tokens.append(token_id)
                
        for token_id in expired_tokens:
            token = self.tokens[token_id]
            token.status = TokenStatus.EXPIRED
            self.blacklisted_tokens.add(token.token_hash)
            
        self.logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        return len(expired_tokens)


# Instance globale du gestionnaire de tokens
token_manager = TokenSecurityManager()


async def get_token_manager() -> TokenSecurityManager:
    """Factory function pour le gestionnaire de tokens"""
    return token_manager


# Fonctions utilitaires pour intégration Ainflue
async def create_creator_token(creator_id: str, 
                             user_id: str,
                             permissions: List[str],
                             ip_address: Optional[str] = None) -> SecureToken:
    """Création d'un token créateur spécialisé"""
    metadata = TokenMetadata(
        token_id=f"creator_{creator_id}_{uuid.uuid4().hex}",
        user_id=user_id,
        creator_id=creator_id,
        token_type=TokenType.CREATOR_TOKEN,
        scopes=['creator_access', 'content_management', 'revenue_access'],
        permissions=permissions,
        ip_address=ip_address,
        custom_claims={
            'creator_verified': True,
            'platform': 'ainflue',
            'token_purpose': 'creator_operations'
        }
    )
    
    return await token_manager.create_token(metadata, SecurityLevel.HIGH)


async def create_payment_token(user_id: str,
                             transaction_id: str,
                             amount: float,
                             currency: str) -> SecureToken:
    """Création d'un token de paiement sécurisé"""
    metadata = TokenMetadata(
        token_id=f"payment_{transaction_id}_{uuid.uuid4().hex}",
        user_id=user_id,
        token_type=TokenType.PAYMENT_TOKEN,
        scopes=['payment_processing'],
        permissions=['payment_execute'],
        max_usage=1,  # Usage unique
        custom_claims={
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': currency,
            'payment_verified': True
        }
    )
    
    return await token_manager.create_token(metadata, SecurityLevel.MAXIMUM)


# Export des classes principales
__all__ = [
    'TokenSecurityManager',
    'TokenMetadata',
    'SecureToken',
    'SessionInfo',
    'TokenValidationResult',
    'TokenType',
    'TokenStatus',
    'SecurityLevel',
    'SessionState',
    'JWTManager',
    'TokenRotationManager',
    'SessionManager',
    'token_manager',
    'get_token_manager',
    'create_creator_token',
    'create_payment_token'
]


# Initialisation pour tests
if __name__ == "__main__":
    async def demo_token_security():
        """Démonstration du système de sécurité des tokens"""
        manager = await get_token_manager()
        
        # Test création session avec tokens
        session, access_token, refresh_token = await manager.create_session_with_tokens(
            user_id="user_123",
            creator_id="creator_abc",
            scopes=['read', 'write', 'creator_access'],
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Test Browser)",
            device_fingerprint="device_test_123"
        )
        
        print(f"Session created: {session.session_id}")
        print(f"Access token: {access_token.token_id}")
        print(f"Refresh token: {refresh_token.token_id}")
        
        # Test validation
        validation_result = await manager.validate_token(access_token.token_value)
        print(f"Token validation: {validation_result.is_valid}")
        print(f"User ID: {validation_result.user_id}")
        print(f"Creator ID: {validation_result.creator_id}")
        
        # Test création token créateur
        creator_token = await create_creator_token(
            creator_id="creator_demo",
            user_id="user_demo",
            permissions=['content_upload', 'revenue_view', 'analytics_access']
        )
        print(f"Creator token: {creator_token.token_id}")
        
        # Test création token paiement
        payment_token = await create_payment_token(
            user_id="user_payment",
            transaction_id="tx_12345",
            amount=99.99,
            currency="USD"
        )
        print(f"Payment token: {payment_token.token_id}")
        
        # Test sécurité
        security_check = await manager.check_token_security(access_token.token_id)
        print(f"Security assessment: {security_check}")
        
        # Test métriques
        metrics = await manager.get_security_metrics()
        print(f"Security metrics: {metrics}")
        
        # Test tokens utilisateur
        user_tokens = await manager.get_user_tokens("user_123")
        print(f"User tokens: {len(user_tokens)}")
        
        # Test révocation
        await manager.revoke_token(payment_token.token_id, "demo_completed")
        print("Payment token revoked")
        
        # Test nettoyage
        cleaned = await manager.cleanup_expired_tokens()
        print(f"Cleaned up {cleaned} expired tokens")
        
    # Exécution démo
    asyncio.run(demo_token_security())