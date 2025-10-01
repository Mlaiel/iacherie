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

JWT Authentication Template for iacherie Creator Economy Platform
Enterprise-grade JWT authentication microservice with advanced security features
"""

import asyncio
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
import jwt
from passlib.context import CryptContext
from redis import Redis
import logging
from prometheus_client import Counter, Histogram, Gauge, start_http_server


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    API_KEY = "api_key"


class UserRole(str, Enum):
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    API_USER = "api_user"


@dataclass
class SecurityConfig:
    """Configuration sécurité JWT enterprise"""
    jwt_secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(64))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    token_blacklist_enabled: bool = True
    rate_limit_per_minute: int = 60
    require_email_verification: bool = True
    password_min_length: int = 12
    password_require_special: bool = True
    mfa_enabled: bool = True
    api_key_rotation_days: int = 90


class TokenPayload(BaseModel):
    """Token payload structure"""
    sub: str  # user_id
    email: str
    role: UserRole
    token_type: TokenType
    exp: int
    iat: int
    jti: str  # JWT ID for blacklisting
    scopes: List[str] = []
    creator_id: Optional[str] = None
    session_id: Optional[str] = None


class LoginRequest(BaseModel):
    """Demande connexion utilisateur"""
    email: EmailStr
    password: str
    remember_me: bool = False
    mfa_token: Optional[str] = None
    device_fingerprint: Optional[str] = None


class TokenResponse(BaseModel):
    """Réponse avec tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: UserRole
    scopes: List[str]


class UserRegistration(BaseModel):
    """Enregistrement utilisateur"""
    email: EmailStr
    password: str
    confirm_password: str
    role: UserRole = UserRole.CREATOR
    creator_name: Optional[str] = None
    accept_terms: bool
    marketing_consent: bool = False

    @validator('password')
    def validate_password(cls, v, values):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError('Password must contain special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class JWTAuthTemplate:
    """
    Template d'authentification JWT enterprise pour iacherie Creator Economy
    
    Fonctionnalités:
    - JWT avec rotation automatique
    - Rate limiting intelligent
    - Blacklist tokens Redis
    - MFA support
    - Device fingerprinting
    - Session management
    - Audit complet
    - Protection brute force
    """
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.app = FastAPI(
            title="iacherie JWT Auth Service",
            description="Enterprise JWT authentication microservice",
            version="1.0.0"
        )
        
        # Security components
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer()
        
        # Redis pour blacklist et sessions
        self.redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Métriques Prometheus
        self.login_attempts = Counter('auth_login_attempts_total', ['status', 'role'])
        self.token_validations = Counter('auth_token_validations_total', ['status'])
        self.auth_duration = Histogram('auth_operation_duration_seconds', ['operation'])
        self.active_sessions = Gauge('auth_active_sessions_total', ['role'])
        
        # Setup
        self._setup_middleware()
        self._setup_routes()
        self._setup_monitoring()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_middleware(self):
        """Configuration middleware sécurité"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://iacherie.com", "https://app.iacherie.com"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

    def _setup_monitoring(self):
        """Setup monitoring Prometheus"""
        start_http_server(8001)

    def _setup_routes(self):
        """Configuration routes authentification"""
        
        @self.app.post("/auth/register", response_model=Dict[str, str])
        async def register_user(user_data: UserRegistration):
            """Enregistrement utilisateur sécurisé"""
            with self.auth_duration.labels(operation='register').time():
                try:
                    # Vérifier email unique
                    if await self._email_exists(user_data.email):
                        raise HTTPException(status_code=400, detail="Email already registered")
                    
                    # Hash password
                    password_hash = self.pwd_context.hash(user_data.password)
                    
                    # Créer utilisateur
                    user_id = await self._create_user({
                        "email": user_data.email,
                        "password_hash": password_hash,
                        "role": user_data.role,
                        "creator_name": user_data.creator_name,
                        "email_verified": False,
                        "created_at": datetime.utcnow().isoformat()
                    })
                    
                    # Envoyer email vérification
                    verification_token = await self._create_verification_token(user_id)
                    await self._send_verification_email(user_data.email, verification_token)
                    
                    self.logger.info(f"User registered: {user_id}")
                    return {"message": "Registration successful", "user_id": user_id}
                    
                except Exception as e:
                    self.logger.error(f"Registration error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Registration failed")

        @self.app.post("/auth/login", response_model=TokenResponse)
        async def login_user(login_data: LoginRequest, request: Request):
            """Connexion utilisateur avec protection brute force"""
            client_ip = request.client.host
            
            with self.auth_duration.labels(operation='login').time():
                try:
                    # Vérifier rate limiting
                    if await self._is_rate_limited(client_ip):
                        self.login_attempts.labels(status='rate_limited', role='unknown').inc()
                        raise HTTPException(status_code=429, detail="Too many login attempts")
                    
                    # Vérifier lockout utilisateur
                    if await self._is_user_locked(login_data.email):
                        self.login_attempts.labels(status='locked', role='unknown').inc()
                        raise HTTPException(status_code=423, detail="Account locked")
                    
                    # Valider credentials
                    user = await self._validate_credentials(login_data.email, login_data.password)
                    if not user:
                        await self._record_failed_login(login_data.email, client_ip)
                        self.login_attempts.labels(status='failed', role='unknown').inc()
                        raise HTTPException(status_code=401, detail="Invalid credentials")
                    
                    # Vérifier MFA si activé
                    if self.config.mfa_enabled and user.get('mfa_enabled'):
                        if not login_data.mfa_token or not await self._verify_mfa(user['id'], login_data.mfa_token):
                            self.login_attempts.labels(status='mfa_failed', role=user['role']).inc()
                            raise HTTPException(status_code=401, detail="Invalid MFA token")
                    
                    # Créer session
                    session_id = await self._create_session(user['id'], login_data.device_fingerprint)
                    
                    # Générer tokens
                    tokens = await self._generate_token_pair(user, session_id)
                    
                    # Reset failed attempts
                    await self._reset_failed_attempts(login_data.email)
                    
                    self.login_attempts.labels(status='success', role=user['role']).inc()
                    self.active_sessions.labels(role=user['role']).inc()
                    
                    self.logger.info(f"User logged in: {user['id']}")
                    return tokens
                    
                except HTTPException:
                    raise
                except Exception as e:
                    self.logger.error(f"Login error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Login failed")

        @self.app.post("/auth/refresh", response_model=TokenResponse)
        async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Rafraîchissement token"""
            with self.auth_duration.labels(operation='refresh').time():
                try:
                    # Valider refresh token
                    payload = await self._validate_token(credentials.credentials, TokenType.REFRESH)
                    
                    # Vérifier session active
                    if not await self._is_session_active(payload.session_id):
                        raise HTTPException(status_code=401, detail="Session expired")
                    
                    # Blacklist ancien token
                    await self._blacklist_token(payload.jti)
                    
                    # Récupérer utilisateur
                    user = await self._get_user(payload.sub)
                    
                    # Générer nouveaux tokens
                    tokens = await self._generate_token_pair(user, payload.session_id)
                    
                    self.token_validations.labels(status='success').inc()
                    return tokens
                    
                except Exception as e:
                    self.token_validations.labels(status='failed').inc()
                    raise HTTPException(status_code=401, detail="Invalid refresh token")

        @self.app.post("/auth/logout")
        async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Déconnexion utilisateur"""
            try:
                payload = await self._validate_token(credentials.credentials, TokenType.ACCESS)
                
                # Blacklist tous les tokens de la session
                await self._invalidate_session(payload.session_id)
                
                self.active_sessions.labels(role=payload.role).dec()
                self.logger.info(f"User logged out: {payload.sub}")
                
                return {"message": "Logout successful"}
                
            except Exception as e:
                raise HTTPException(status_code=401, detail="Invalid token")

        @self.app.get("/auth/verify")
        async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Vérification token pour autres services"""
            try:
                payload = await self._validate_token(credentials.credentials, TokenType.ACCESS)
                
                self.token_validations.labels(status='success').inc()
                return {
                    "valid": True,
                    "user_id": payload.sub,
                    "role": payload.role,
                    "scopes": payload.scopes,
                    "creator_id": payload.creator_id
                }
                
            except Exception as e:
                self.token_validations.labels(status='failed').inc()
                return {"valid": False}

        @self.app.get("/auth/health")
        async def health_check():
            """Health check"""
            try:
                # Test Redis connection
                await self.redis.ping()
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "redis": "connected"
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _generate_token_pair(self, user: Dict, session_id: str) -> TokenResponse:
        """Génère paire access/refresh tokens"""
        now = datetime.now(timezone.utc)
        
        # Access token
        access_payload = TokenPayload(
            sub=user['id'],
            email=user['email'],
            role=user['role'],
            token_type=TokenType.ACCESS,
            exp=int((now + timedelta(minutes=self.config.access_token_expire_minutes)).timestamp()),
            iat=int(now.timestamp()),
            jti=secrets.token_urlsafe(32),
            scopes=user.get('scopes', []),
            creator_id=user.get('creator_id'),
            session_id=session_id
        )
        
        # Refresh token
        refresh_payload = TokenPayload(
            sub=user['id'],
            email=user['email'],
            role=user['role'],
            token_type=TokenType.REFRESH,
            exp=int((now + timedelta(days=self.config.refresh_token_expire_days)).timestamp()),
            iat=int(now.timestamp()),
            jti=secrets.token_urlsafe(32),
            session_id=session_id
        )
        
        access_token = jwt.encode(
            access_payload.dict(), 
            self.config.jwt_secret_key, 
            algorithm=self.config.jwt_algorithm
        )
        
        refresh_token = jwt.encode(
            refresh_payload.dict(),
            self.config.jwt_secret_key,
            algorithm=self.config.jwt_algorithm
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_expire_minutes * 60,
            user_id=user['id'],
            role=user['role'],
            scopes=access_payload.scopes
        )

    async def _validate_token(self, token: str, expected_type: TokenType) -> TokenPayload:
        """Valide et decode JWT token"""
        try:
            # Decode token
            payload_dict = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=[self.config.jwt_algorithm]
            )
            
            payload = TokenPayload(**payload_dict)
            
            # Vérifier type token
            if payload.token_type != expected_type:
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            # Vérifier blacklist
            if await self._is_token_blacklisted(payload.jti):
                raise HTTPException(status_code=401, detail="Token revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def _is_token_blacklisted(self, jti: str) -> bool:
        """Vérifie si token est blacklisté"""
        return await self.redis.sismember("blacklisted_tokens", jti)

    async def _blacklist_token(self, jti: str):
        """Ajoute token à la blacklist"""
        await self.redis.sadd("blacklisted_tokens", jti)
        # TTL égal à la durée max des tokens
        await self.redis.expire("blacklisted_tokens", self.config.refresh_token_expire_days * 24 * 3600)

    async def _is_rate_limited(self, client_ip: str) -> bool:
        """Vérifie rate limiting par IP"""
        key = f"rate_limit:{client_ip}"
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, 60, 1)
            return False
        elif int(current) >= self.config.rate_limit_per_minute:
            return True
        else:
            await self.redis.incr(key)
            return False

    async def _create_session(self, user_id: str, device_fingerprint: str = None) -> str:
        """Crée nouvelle session utilisateur"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "device_fingerprint": device_fingerprint,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(
            f"session:{session_id}",
            self.config.refresh_token_expire_days * 24 * 3600,
            json.dumps(session_data)
        )
        
        return session_id

    async def _is_session_active(self, session_id: str) -> bool:
        """Vérifie si session est active"""
        return await self.redis.exists(f"session:{session_id}")

    async def _invalidate_session(self, session_id: str):
        """Invalide session et tous ses tokens"""
        await self.redis.delete(f"session:{session_id}")

    # Méthodes utilitaires (à implémenter selon base de données)
    async def _email_exists(self, email: str) -> bool:
        """Vérifie si email existe déjà"""
        # Implementation depends on database
        return False

    async def _create_user(self, user_data: Dict) -> str:
        """Crée nouvel utilisateur"""
        # Implementation depends on database
        return secrets.token_urlsafe(16)

    async def _validate_credentials(self, email: str, password: str) -> Optional[Dict]:
        """Valide credentials utilisateur"""
        # Implementation depends on database
        return None

    async def _get_user(self, user_id: str) -> Dict:
        """Récupère utilisateur par ID"""
        # Implementation depends on database
        return {}

    async def _record_failed_login(self, email: str, client_ip: str):
        """Enregistre tentative connexion échouée"""
        pass

    async def _is_user_locked(self, email: str) -> bool:
        """Vérifie si utilisateur est verrouillé"""
        return False

    async def _reset_failed_attempts(self, email: str):
        """Reset compteur tentatives échouées"""
        pass

    async def _create_verification_token(self, user_id: str) -> str:
        """Crée token vérification email"""
        return secrets.token_urlsafe(32)

    async def _send_verification_email(self, email: str, token: str):
        """Envoie email de vérification"""
        pass

    async def _verify_mfa(self, user_id: str, mfa_token: str) -> bool:
        """Vérifie token MFA"""
        return True

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


# Factory function pour faciliter l'utilisation
def create_jwt_auth_service(config: SecurityConfig = None) -> FastAPI:
    """
    Factory pour créer service d'authentification JWT
    
    Args:
        config: Configuration sécurité personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    auth_service = JWTAuthTemplate(config)
    return auth_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    # Configuration pour développement
    config = SecurityConfig(
        access_token_expire_minutes=15,
        refresh_token_expire_days=1,
        mfa_enabled=False  # Désactiver MFA en dev
    )
    
    app = create_jwt_auth_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )