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

OAuth2 Service Template for Ainflue Creator Economy Platform
Enterprise OAuth2/OpenID Connect implementation for secure third-party integrations
"""

import asyncio
import secrets
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import urllib.parse

from fastapi import FastAPI, HTTPException, Depends, Request, Response, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, EmailStr, validator, HttpUrl
import jwt
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2 import OAuth2Token
from redis import Redis
import httpx
import logging
from prometheus_client import Counter, Histogram, Gauge


class GrantType(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    DEVICE_CODE = "device_code"


class ResponseType(str, Enum):
    CODE = "code"
    TOKEN = "token"
    ID_TOKEN = "id_token"


class Scope(str, Enum):
    OPENID = "openid"
    PROFILE = "profile"
    EMAIL = "email"
    CREATOR_READ = "creator:read"
    CREATOR_WRITE = "creator:write"
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    ANALYTICS_READ = "analytics:read"
    MONETIZATION_WRITE = "monetization:write"


class ClientType(str, Enum):
    CONFIDENTIAL = "confidential"
    PUBLIC = "public"


@dataclass
class OAuth2Config:
    """Configuration OAuth2 enterprise"""
    authorization_code_lifetime: int = 600  # 10 minutes
    access_token_lifetime: int = 3600  # 1 hour
    refresh_token_lifetime: int = 2592000  # 30 days
    device_code_lifetime: int = 600  # 10 minutes
    require_pkce: bool = True
    require_state: bool = True
    issuer_url: str = "https://auth.ainflue.com"
    supported_scopes: List[str] = field(default_factory=lambda: [scope.value for scope in Scope])
    supported_grant_types: List[str] = field(default_factory=lambda: [grant.value for grant in GrantType])
    jwks_uri: str = "https://auth.ainflue.com/.well-known/jwks.json"


class OAuth2Client(BaseModel):
    """Client OAuth2 enregistré"""
    client_id: str
    client_secret: Optional[str] = None
    client_name: str
    client_type: ClientType
    redirect_uris: List[HttpUrl]
    allowed_scopes: List[str]
    allowed_grant_types: List[str]
    creator_id: Optional[str] = None
    webhook_url: Optional[HttpUrl] = None
    created_at: datetime
    last_used: Optional[datetime] = None
    is_active: bool = True


class AuthorizationRequest(BaseModel):
    """Demande d'autorisation OAuth2"""
    response_type: ResponseType
    client_id: str
    redirect_uri: HttpUrl
    scope: str
    state: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = "S256"
    nonce: Optional[str] = None


class TokenRequest(BaseModel):
    """Demande de token OAuth2"""
    grant_type: GrantType
    code: Optional[str] = None
    redirect_uri: Optional[HttpUrl] = None
    client_id: str
    client_secret: Optional[str] = None
    refresh_token: Optional[str] = None
    code_verifier: Optional[str] = None
    scope: Optional[str] = None


class TokenResponse(BaseModel):
    """Réponse token OAuth2"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str
    id_token: Optional[str] = None


class DeviceAuthRequest(BaseModel):
    """Demande device authorization"""
    client_id: str
    scope: str


class DeviceAuthResponse(BaseModel):
    """Réponse device authorization"""
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int = 5


class OAuth2ServiceTemplate:
    """
    Template de service OAuth2/OpenID Connect enterprise pour Ainflue
    
    Fonctionnalités:
    - OAuth2 Authorization Code Flow avec PKCE
    - Client Credentials Flow
    - Device Authorization Flow
    - OpenID Connect
    - Token introspection et révocation
    - Dynamic client registration
    - Rate limiting et sécurité avancée
    - Audit complet
    """
    
    def __init__(self, config: OAuth2Config = None):
        self.config = config or OAuth2Config()
        self.app = FastAPI(
            title="Ainflue OAuth2 Service",
            description="Enterprise OAuth2/OpenID Connect service",
            version="1.0.0"
        )
        
        # Redis pour codes et tokens
        self.redis = Redis(host='localhost', port=6379, db=1, decode_responses=True)
        
        # Métriques Prometheus
        self.auth_requests = Counter('oauth2_auth_requests_total', ['client_id', 'grant_type', 'status'])
        self.token_grants = Counter('oauth2_token_grants_total', ['grant_type', 'client_type'])
        self.auth_duration = Histogram('oauth2_operation_duration_seconds', ['operation'])
        self.active_tokens = Gauge('oauth2_active_tokens_total', ['client_id'])
        
        # OAuth2 clients storage
        self.oauth_clients: Dict[str, OAuth2Client] = {}
        
        # Setup
        self._setup_routes()
        self._load_clients()
        
        # Logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _load_clients(self):
        """Charge les clients OAuth2 depuis la base"""
        # En production, charger depuis database
        # Client example pour démonstration
        demo_client = OAuth2Client(
            client_id="ainflue_web_app",
            client_secret=self._hash_secret("demo_secret_2025"),
            client_name="Ainflue Web Application",
            client_type=ClientType.CONFIDENTIAL,
            redirect_uris=["https://app.ainflue.com/auth/callback"],
            allowed_scopes=["openid", "profile", "email", "creator:read", "creator:write"],
            allowed_grant_types=["authorization_code", "refresh_token"],
            created_at=datetime.utcnow()
        )
        self.oauth_clients[demo_client.client_id] = demo_client

    def _setup_routes(self):
        """Configuration routes OAuth2"""
        
        @self.app.get("/.well-known/openid-configuration")
        async def openid_configuration():
            """OpenID Connect Discovery endpoint"""
            return {
                "issuer": self.config.issuer_url,
                "authorization_endpoint": f"{self.config.issuer_url}/oauth2/authorize",
                "token_endpoint": f"{self.config.issuer_url}/oauth2/token",
                "userinfo_endpoint": f"{self.config.issuer_url}/oauth2/userinfo",
                "revocation_endpoint": f"{self.config.issuer_url}/oauth2/revoke",
                "introspection_endpoint": f"{self.config.issuer_url}/oauth2/introspect",
                "device_authorization_endpoint": f"{self.config.issuer_url}/oauth2/device",
                "jwks_uri": self.config.jwks_uri,
                "scopes_supported": self.config.supported_scopes,
                "response_types_supported": ["code", "token", "id_token", "code token", "code id_token"],
                "grant_types_supported": self.config.supported_grant_types,
                "subject_types_supported": ["public"],
                "id_token_signing_alg_values_supported": ["HS256", "RS256"],
                "code_challenge_methods_supported": ["S256"],
                "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"]
            }

        @self.app.get("/oauth2/authorize")
        async def authorize(
            response_type: str,
            client_id: str,
            redirect_uri: str,
            scope: str = "openid",
            state: Optional[str] = None,
            code_challenge: Optional[str] = None,
            code_challenge_method: str = "S256",
            nonce: Optional[str] = None,
            request: Request = None
        ):
            """Endpoint d'autorisation OAuth2"""
            with self.auth_duration.labels(operation='authorize').time():
                try:
                    # Valider client
                    client = await self._validate_client(client_id)
                    if not client:
                        self.auth_requests.labels(client_id=client_id, grant_type='authorization_code', status='invalid_client').inc()
                        raise HTTPException(status_code=400, detail="Invalid client")
                    
                    # Valider redirect_uri
                    if not await self._validate_redirect_uri(client, redirect_uri):
                        self.auth_requests.labels(client_id=client_id, grant_type='authorization_code', status='invalid_redirect').inc()
                        raise HTTPException(status_code=400, detail="Invalid redirect URI")
                    
                    # Valider scopes
                    requested_scopes = scope.split()
                    if not await self._validate_scopes(client, requested_scopes):
                        self.auth_requests.labels(client_id=client_id, grant_type='authorization_code', status='invalid_scope').inc()
                        return self._error_redirect(redirect_uri, "invalid_scope", state)
                    
                    # Valider PKCE si requis
                    if self.config.require_pkce and not code_challenge:
                        self.auth_requests.labels(client_id=client_id, grant_type='authorization_code', status='missing_pkce').inc()
                        return self._error_redirect(redirect_uri, "invalid_request", state, "PKCE required")
                    
                    # Vérifier si utilisateur authentifié
                    user_id = await self._get_authenticated_user(request)
                    if not user_id:
                        # Rediriger vers login avec return URL
                        login_url = f"/auth/login?return_to=" + urllib.parse.quote(str(request.url))
                        return RedirectResponse(login_url)
                    
                    # Vérifier consentement utilisateur
                    consent_required = await self._check_consent_required(user_id, client_id, requested_scopes)
                    if consent_required:
                        # Afficher page de consentement
                        return await self._show_consent_page(user_id, client, requested_scopes, request.url.query)
                    
                    # Générer code d'autorisation
                    auth_code = await self._generate_authorization_code(
                        user_id, client_id, redirect_uri, requested_scopes,
                        code_challenge, code_challenge_method, nonce
                    )
                    
                    # Rediriger avec code
                    callback_url = f"{redirect_uri}?code={auth_code}"
                    if state:
                        callback_url += f"&state={state}"
                    
                    self.auth_requests.labels(client_id=client_id, grant_type='authorization_code', status='success').inc()
                    return RedirectResponse(callback_url)
                    
                except HTTPException:
                    raise
                except Exception as e:
                    self.logger.error(f"Authorization error: {str(e)}")
                    return self._error_redirect(redirect_uri, "server_error", state)

        @self.app.post("/oauth2/token", response_model=TokenResponse)
        async def token_endpoint(
            grant_type: str = Form(...),
            code: Optional[str] = Form(None),
            redirect_uri: Optional[str] = Form(None),
            client_id: str = Form(...),
            client_secret: Optional[str] = Form(None),
            refresh_token: Optional[str] = Form(None),
            code_verifier: Optional[str] = Form(None),
            scope: Optional[str] = Form(None),
            request: Request = None
        ):
            """Endpoint d'échange de tokens"""
            with self.auth_duration.labels(operation='token').time():
                try:
                    # Authentifier client
                    client = await self._authenticate_client(client_id, client_secret, request)
                    if not client:
                        self.token_grants.labels(grant_type=grant_type, client_type='unknown').inc()
                        raise HTTPException(status_code=401, detail="Invalid client credentials")
                    
                    if grant_type == GrantType.AUTHORIZATION_CODE:
                        return await self._handle_authorization_code_grant(
                            code, redirect_uri, client, code_verifier
                        )
                    elif grant_type == GrantType.REFRESH_TOKEN:
                        return await self._handle_refresh_token_grant(
                            refresh_token, client, scope
                        )
                    elif grant_type == GrantType.CLIENT_CREDENTIALS:
                        return await self._handle_client_credentials_grant(
                            client, scope
                        )
                    else:
                        raise HTTPException(status_code=400, detail="Unsupported grant type")
                        
                except HTTPException:
                    raise
                except Exception as e:
                    self.logger.error(f"Token error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.post("/oauth2/device")
        async def device_authorization(device_request: DeviceAuthRequest):
            """Device Authorization Flow"""
            with self.auth_duration.labels(operation='device_auth').time():
                try:
                    # Valider client
                    client = await self._validate_client(device_request.client_id)
                    if not client or "device_code" not in client.allowed_grant_types:
                        raise HTTPException(status_code=400, detail="Invalid client or unsupported grant type")
                    
                    # Valider scopes
                    requested_scopes = device_request.scope.split()
                    if not await self._validate_scopes(client, requested_scopes):
                        raise HTTPException(status_code=400, detail="Invalid scope")
                    
                    # Générer codes
                    device_code = secrets.token_urlsafe(32)
                    user_code = self._generate_user_code()
                    
                    # Stocker dans Redis
                    device_data = {
                        "client_id": device_request.client_id,
                        "scope": device_request.scope,
                        "user_code": user_code,
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "pending"
                    }
                    
                    await self.redis.setex(
                        f"device_code:{device_code}",
                        self.config.device_code_lifetime,
                        json.dumps(device_data)
                    )
                    
                    await self.redis.setex(
                        f"user_code:{user_code}",
                        self.config.device_code_lifetime,
                        device_code
                    )
                    
                    return DeviceAuthResponse(
                        device_code=device_code,
                        user_code=user_code,
                        verification_uri=f"{self.config.issuer_url}/device",
                        verification_uri_complete=f"{self.config.issuer_url}/device?user_code={user_code}",
                        expires_in=self.config.device_code_lifetime
                    )
                    
                except Exception as e:
                    self.logger.error(f"Device authorization error: {str(e)}")
                    raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.post("/oauth2/introspect")
        async def introspect_token(
            token: str = Form(...),
            token_type_hint: Optional[str] = Form(None),
            request: Request = None
        ):
            """Token introspection endpoint"""
            try:
                # Authentifier client
                client_id, client_secret = await self._extract_client_credentials(request)
                client = await self._authenticate_client(client_id, client_secret, request)
                if not client:
                    raise HTTPException(status_code=401, detail="Invalid client credentials")
                
                # Introspect token
                token_info = await self._introspect_token(token)
                return token_info
                
            except Exception as e:
                self.logger.error(f"Token introspection error: {str(e)}")
                return {"active": False}

        @self.app.post("/oauth2/revoke")
        async def revoke_token(
            token: str = Form(...),
            token_type_hint: Optional[str] = Form(None),
            request: Request = None
        ):
            """Token revocation endpoint"""
            try:
                # Authentifier client
                client_id, client_secret = await self._extract_client_credentials(request)
                client = await self._authenticate_client(client_id, client_secret, request)
                if not client:
                    raise HTTPException(status_code=401, detail="Invalid client credentials")
                
                # Révoquer token
                await self._revoke_token(token)
                return Response(status_code=200)
                
            except Exception as e:
                self.logger.error(f"Token revocation error: {str(e)}")
                return Response(status_code=200)  # RFC recommends 200 even on error

        @self.app.get("/oauth2/userinfo")
        async def userinfo_endpoint(
            authorization: str = Depends(OAuth2PasswordBearer(tokenUrl="/oauth2/token"))
        ):
            """OpenID Connect UserInfo endpoint"""
            try:
                # Valider access token
                token_data = await self._validate_access_token(authorization.replace("Bearer ", ""))
                if not token_data:
                    raise HTTPException(status_code=401, detail="Invalid token")
                
                # Vérifier scope openid
                if "openid" not in token_data.get("scope", "").split():
                    raise HTTPException(status_code=403, detail="Insufficient scope")
                
                # Récupérer infos utilisateur
                user_info = await self._get_user_info(token_data["sub"], token_data.get("scope", "").split())
                return user_info
                
            except Exception as e:
                self.logger.error(f"UserInfo error: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal server error")

        @self.app.get("/health")
        async def health_check():
            """Health check"""
            try:
                await self.redis.ping()
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "redis": "connected",
                    "active_clients": len(self.oauth_clients)
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _generate_authorization_code(
        self, user_id: str, client_id: str, redirect_uri: str, 
        scopes: List[str], code_challenge: str = None, 
        code_challenge_method: str = None, nonce: str = None
    ) -> str:
        """Génère code d'autorisation"""
        auth_code = secrets.token_urlsafe(32)
        
        code_data = {
            "user_id": user_id,
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
            "nonce": nonce,
            "created_at": datetime.utcnow().isoformat(),
            "used": False
        }
        
        await self.redis.setex(
            f"auth_code:{auth_code}",
            self.config.authorization_code_lifetime,
            json.dumps(code_data)
        )
        
        return auth_code

    async def _handle_authorization_code_grant(
        self, code: str, redirect_uri: str, client: OAuth2Client, code_verifier: str = None
    ) -> TokenResponse:
        """Traite grant type authorization_code"""
        if not code:
            raise HTTPException(status_code=400, detail="Missing authorization code")
        
        # Récupérer et valider code
        code_data_str = await self.redis.get(f"auth_code:{code}")
        if not code_data_str:
            raise HTTPException(status_code=400, detail="Invalid or expired authorization code")
        
        code_data = json.loads(code_data_str)
        
        # Vérifier que le code n'a pas été utilisé
        if code_data.get("used"):
            raise HTTPException(status_code=400, detail="Authorization code already used")
        
        # Valider client_id
        if code_data["client_id"] != client.client_id:
            raise HTTPException(status_code=400, detail="Invalid client")
        
        # Valider redirect_uri
        if code_data["redirect_uri"] != redirect_uri:
            raise HTTPException(status_code=400, detail="Invalid redirect URI")
        
        # Valider PKCE si présent
        if code_data.get("code_challenge"):
            if not code_verifier:
                raise HTTPException(status_code=400, detail="Missing code verifier")
            
            if not await self._verify_pkce(code_data["code_challenge"], code_verifier, code_data.get("code_challenge_method", "S256")):
                raise HTTPException(status_code=400, detail="Invalid code verifier")
        
        # Marquer code comme utilisé
        code_data["used"] = True
        await self.redis.setex(
            f"auth_code:{code}",
            self.config.authorization_code_lifetime,
            json.dumps(code_data)
        )
        
        # Générer tokens
        tokens = await self._generate_tokens(
            client,
            code_data["user_id"],
            code_data["scope"].split(),
            code_data.get("nonce")
        )
        
        self.token_grants.labels(grant_type='authorization_code', client_type=client.client_type).inc()
        return tokens

    async def _generate_tokens(
        self, client: OAuth2Client, user_id: str, scopes: List[str], nonce: str = None
    ) -> TokenResponse:
        """Génère access et refresh tokens"""
        now = datetime.now(timezone.utc)
        
        # Access token payload
        access_payload = {
            "sub": user_id,
            "client_id": client.client_id,
            "scope": " ".join(scopes),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.config.access_token_lifetime)).timestamp()),
            "aud": client.client_id,
            "iss": self.config.issuer_url,
            "jti": secrets.token_urlsafe(32)
        }
        
        # Refresh token payload
        refresh_payload = {
            "sub": user_id,
            "client_id": client.client_id,
            "scope": " ".join(scopes),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.config.refresh_token_lifetime)).timestamp()),
            "jti": secrets.token_urlsafe(32),
            "token_type": "refresh"
        }
        
        # Générer access token
        access_token = jwt.encode(access_payload, self._get_signing_key(), algorithm="HS256")
        
        # Générer refresh token
        refresh_token = jwt.encode(refresh_payload, self._get_signing_key(), algorithm="HS256")
        
        # ID token si OpenID Connect
        id_token = None
        if "openid" in scopes:
            id_payload = {
                "sub": user_id,
                "aud": client.client_id,
                "iss": self.config.issuer_url,
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(seconds=self.config.access_token_lifetime)).timestamp()),
                "nonce": nonce
            }
            
            # Ajouter claims selon scopes
            if "email" in scopes:
                user_data = await self._get_user_data(user_id)
                id_payload["email"] = user_data.get("email")
                id_payload["email_verified"] = user_data.get("email_verified", False)
            
            if "profile" in scopes:
                user_data = await self._get_user_data(user_id)
                id_payload.update({
                    "name": user_data.get("name"),
                    "picture": user_data.get("avatar_url"),
                    "preferred_username": user_data.get("username")
                })
            
            id_token = jwt.encode(id_payload, self._get_signing_key(), algorithm="HS256")
        
        # Stocker tokens pour introspection
        await self._store_token(access_payload["jti"], access_payload)
        await self._store_token(refresh_payload["jti"], refresh_payload)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_lifetime,
            scope=" ".join(scopes),
            id_token=id_token
        )

    # Méthodes utilitaires
    def _hash_secret(self, secret: str) -> str:
        """Hash secret client"""
        return hashlib.sha256(secret.encode()).hexdigest()

    def _get_signing_key(self) -> str:
        """Récupère clé de signature JWT"""
        return "your-secret-key-here"  # En production, utiliser HSM ou vault

    def _generate_user_code(self) -> str:
        """Génère code utilisateur lisible"""
        import string
        import random
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=8))

    async def _validate_client(self, client_id: str) -> Optional[OAuth2Client]:
        """Valide client OAuth2"""
        return self.oauth_clients.get(client_id)

    async def _authenticate_client(self, client_id: str, client_secret: str, request: Request) -> Optional[OAuth2Client]:
        """Authentifie client OAuth2"""
        client = await self._validate_client(client_id)
        if not client or not client.is_active:
            return None
        
        if client.client_type == ClientType.PUBLIC:
            return client
        
        # Vérifier secret pour clients confidentiels
        if client.client_secret and self._hash_secret(client_secret or "") == client.client_secret:
            return client
        
        return None

    async def _validate_redirect_uri(self, client: OAuth2Client, redirect_uri: str) -> bool:
        """Valide redirect URI"""
        return redirect_uri in [str(uri) for uri in client.redirect_uris]

    async def _validate_scopes(self, client: OAuth2Client, scopes: List[str]) -> bool:
        """Valide scopes demandés"""
        return all(scope in client.allowed_scopes for scope in scopes)

    async def _verify_pkce(self, code_challenge: str, code_verifier: str, method: str = "S256") -> bool:
        """Vérifie PKCE"""
        if method == "S256":
            import base64
            digest = hashlib.sha256(code_verifier.encode()).digest()
            computed_challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
            return computed_challenge == code_challenge
        return False

    def _error_redirect(self, redirect_uri: str, error: str, state: str = None, description: str = None) -> RedirectResponse:
        """Redirige avec erreur OAuth2"""
        url = f"{redirect_uri}?error={error}"
        if state:
            url += f"&state={state}"
        if description:
            url += f"&error_description={urllib.parse.quote(description)}"
        return RedirectResponse(url)

    async def _get_authenticated_user(self, request: Request) -> Optional[str]:
        """Récupère utilisateur authentifié depuis session"""
        # Implementation depends on session management
        return None

    async def _get_user_data(self, user_id: str) -> Dict:
        """Récupère données utilisateur"""
        # Implementation depends on database
        return {}

    async def _store_token(self, jti: str, payload: Dict):
        """Stocke token pour introspection"""
        await self.redis.setex(
            f"token:{jti}",
            payload["exp"] - payload["iat"],
            json.dumps(payload)
        )

    async def _extract_client_credentials(self, request: Request) -> Tuple[str, str]:
        """Extrait credentials client de la requête"""
        # Implementation for Basic auth, form data, etc.
        return "", ""

    def get_app(self) -> FastAPI:
        """Retourne instance FastAPI"""
        return self.app


def create_oauth2_service(config: OAuth2Config = None) -> FastAPI:
    """
    Factory pour créer service OAuth2
    
    Args:
        config: Configuration OAuth2 personnalisée
        
    Returns:
        FastAPI: Instance du service configuré
    """
    oauth2_service = OAuth2ServiceTemplate(config)
    return oauth2_service.get_app()


if __name__ == "__main__":
    import uvicorn
    
    config = OAuth2Config(
        issuer_url="http://localhost:8000",
        access_token_lifetime=3600,
        refresh_token_lifetime=86400
    )
    
    app = create_oauth2_service(config)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )