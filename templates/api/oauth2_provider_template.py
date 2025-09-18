"""
🔒 OAUTH2 PROVIDER TEMPLATE - ENTERPRISE OAUTH2 IMPLEMENTATION
=============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade OAuth2 provider template with:
- OAuth2 Authorization Code flow
- PKCE support for security
- JWT token management
- Creator economy scopes
- Enterprise security standards

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import secrets
import hashlib
import base64
import jwt

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..template_registry import TemplateInterface, TemplateMetadata, TemplateType, TemplateCategory, SecurityLevel

logger = logging.getLogger(__name__)


class GrantType(Enum):
    """OAuth2 grant types."""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"


class OAuth2Scope(Enum):
    """OAuth2 scopes for creator economy."""
    READ_PROFILE = "read:profile"
    WRITE_PROFILE = "write:profile"
    READ_CONTENT = "read:content"
    WRITE_CONTENT = "write:content"
    READ_ANALYTICS = "read:analytics"
    MANAGE_MONETIZATION = "manage:monetization"
    READ_COLLABORATIONS = "read:collaborations"
    WRITE_COLLABORATIONS = "write:collaborations"
    ADMIN = "admin"


class OAuth2ProviderConfig(BaseModel):
    """Configuration for OAuth2 provider generation."""
    
    provider_name: str = Field(..., description="Name of the OAuth2 provider")
    description: str = Field("", description="Provider description")
    
    # Server configuration
    server_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "issuer": "https://auth.ainflue.com",
            "authorization_endpoint": "/oauth2/authorize",
            "token_endpoint": "/oauth2/token",
            "userinfo_endpoint": "/oauth2/userinfo",
            "jwks_uri": "/oauth2/jwks",
            "introspection_endpoint": "/oauth2/introspect"
        }
    )
    
    # Security configuration
    security_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "jwt_algorithm": "RS256",
            "access_token_lifetime": 3600,
            "refresh_token_lifetime": 604800,
            "authorization_code_lifetime": 600,
            "enable_pkce": True,
            "require_pkce": True
        }
    )
    
    # Creator economy scopes
    creator_scopes: List[str] = Field(
        default_factory=lambda: [
            "read:profile", "write:profile", "read:content", "write:content",
            "read:analytics", "manage:monetization", "read:collaborations", "write:collaborations"
        ]
    )
    
    # Client management
    client_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_register": False,
            "require_approval": True,
            "default_scopes": ["read:profile"],
            "allowed_grant_types": ["authorization_code", "refresh_token"]
        }
    )


class OAuth2ProviderTemplate(TemplateInterface):
    """Enterprise OAuth2 provider template."""
    
    @property
    def metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="oauth2_provider_template",
            template_type=TemplateType.AUTHENTICATION,
            category=TemplateCategory.SECURITY,
            version="1.0.0",
            author="Fahed Mlaiel",
            description="Enterprise OAuth2 provider template with creator economy integration",
            security_level=SecurityLevel.ENTERPRISE,
            dependencies=["fastapi", "pyjwt", "redis", "sqlalchemy", "cryptography"],
            tags=["oauth2", "authentication", "security", "provider"],
            compliance_standards=["OAuth2", "OIDC", "RFC6749", "RFC7636"],
            enterprise_features=[
                "OAuth2 Authorization Code flow",
                "PKCE support",
                "JWT token management",
                "Creator economy scopes",
                "Enterprise client management"
            ]
        )
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate OAuth2 provider based on configuration."""
        try:
            provider_config = OAuth2ProviderConfig(**config)
            return self._generate_provider_code(provider_config)
        except Exception as e:
            logger.error(f"Failed to generate OAuth2 provider: {e}")
            raise
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate provider configuration."""
        try:
            OAuth2ProviderConfig(**config)
            return True
        except Exception as e:
            logger.error(f"Invalid OAuth2 provider config: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return OAuth2ProviderConfig.schema()
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return [
            {
                "provider_name": "AinflueOAuth2Provider",
                "description": "OAuth2 provider for Ainflue creator economy platform",
                "server_config": {
                    "issuer": "https://auth.ainflue.com",
                    "authorization_endpoint": "/oauth2/authorize",
                    "token_endpoint": "/oauth2/token"
                }
            }
        ]
    
    def _generate_provider_code(self, config: OAuth2ProviderConfig) -> str:
        """Generate the actual OAuth2 provider code."""
        
        # Generate imports
        imports = self._generate_imports()
        
        # Generate models
        models = self._generate_models(config)
        
        # Generate OAuth2 provider class
        provider_class = self._generate_provider_class(config)
        
        # Generate endpoints
        endpoints = self._generate_endpoints(config)
        
        # Generate client management
        client_management = self._generate_client_management(config)
        
        # Generate token management
        token_management = self._generate_token_management(config)
        
        # Generate configuration
        provider_config_code = self._generate_provider_config(config)
        
        code = f'''"""
{config.provider_name} OAuth2 Provider
Generated by Ainflue OAuth2 Provider Template

{config.description}

🔒 PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

{imports}

{models}

{provider_class}

{client_management}

{token_management}

{endpoints}

{provider_config_code}

# Provider factory
def create_oauth2_provider() -> OAuth2Provider:
    """Create OAuth2 provider with configuration."""
    provider = OAuth2Provider()
    
    # Apply security policies
    provider = apply_security_policies(provider)
    
    # Apply monitoring
    provider = apply_oauth2_monitoring(provider)
    
    return provider

# Export provider instance
oauth2_provider = create_oauth2_provider()

if __name__ == "__main__":
    print(f"✅ {config.provider_name} initialized successfully")
    print(f"📊 OAuth2 Provider statistics:")
    print(f"   - Issuer: {config.server_config['issuer']}")
    print(f"   - PKCE enabled: {config.security_config['enable_pkce']}")
    print(f"   - Creator scopes: {len(config.creator_scopes)}")
    print(f"   - Token lifetime: {config.security_config['access_token_lifetime']}s")
'''
        
        return code
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return '''from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import secrets
import hashlib
import base64
import uuid
import json

import jwt
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete

# Core imports
from core.database import get_db_session
from core.auth import get_current_user
from core.caching import cache_response
from monitoring.oauth2_metrics import OAuth2MetricsCollector
from utils.security import generate_secure_token, verify_pkce_challenge
from models import User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token

logger = logging.getLogger(__name__)'''
    
    def _generate_models(self, config: OAuth2ProviderConfig) -> str:
        """Generate OAuth2 data models."""
        return '''# OAuth2 Data Models

class GrantType(Enum):
    """OAuth2 grant types."""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"

class OAuth2Scope(Enum):
    """OAuth2 scopes for creator economy."""
    READ_PROFILE = "read:profile"
    WRITE_PROFILE = "write:profile"
    READ_CONTENT = "read:content"
    WRITE_CONTENT = "write:content"
    READ_ANALYTICS = "read:analytics"
    MANAGE_MONETIZATION = "manage:monetization"
    READ_COLLABORATIONS = "read:collaborations"
    WRITE_COLLABORATIONS = "write:collaborations"
    ADMIN = "admin"

@dataclass
class AuthorizationRequest:
    """OAuth2 authorization request."""
    client_id: str
    response_type: str
    redirect_uri: str
    scope: str
    state: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate authorization request."""
        if self.response_type != "code":
            return False
        if not self.client_id or not self.redirect_uri:
            return False
        return True

@dataclass
class TokenRequest:
    """OAuth2 token request."""
    grant_type: str
    client_id: str
    client_secret: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    code_verifier: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate token request."""
        if self.grant_type not in [gt.value for gt in GrantType]:
            return False
        if not self.client_id:
            return False
        return True

class TokenResponse(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

class UserInfoResponse(BaseModel):
    """OAuth2 userinfo response."""
    sub: str
    username: str
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    is_creator: Optional[bool] = None
    creator_id: Optional[str] = None'''
    
    def _generate_provider_class(self, config: OAuth2ProviderConfig) -> str:
        """Generate OAuth2 provider class."""
        return f'''# OAuth2 Provider Implementation

class OAuth2Provider:
    """Enterprise OAuth2 provider."""
    
    def __init__(self):
        self.config = {config.dict()}
        self.redis_client = None
        self.jwt_algorithm = self.config['security_config']['jwt_algorithm']
        self.access_token_lifetime = self.config['security_config']['access_token_lifetime']
        self.refresh_token_lifetime = self.config['security_config']['refresh_token_lifetime']
        self.authorization_code_lifetime = self.config['security_config']['authorization_code_lifetime']
        self.enable_pkce = self.config['security_config']['enable_pkce']
        self.require_pkce = self.config['security_config']['require_pkce']
    
    async def connect_redis(self):
        """Connect to Redis for token storage."""
        if not self.redis_client:
            self.redis_client = redis.Redis.from_url("redis://localhost:6379")
            await self.redis_client.ping()
    
    async def validate_client(self, client_id: str, client_secret: Optional[str] = None, db: AsyncSession = None) -> Optional[OAuth2Client]:
        """Validate OAuth2 client."""
        query = select(OAuth2Client).where(OAuth2Client.client_id == client_id)
        result = await db.execute(query)
        client = result.scalar_one_or_none()
        
        if not client or not client.is_active:
            return None
        
        # Validate client secret for confidential clients
        if client.is_confidential and client_secret:
            if not self._verify_client_secret(client_secret, client.client_secret_hash):
                return None
        
        return client
    
    def _verify_client_secret(self, secret: str, secret_hash: str) -> bool:
        """Verify client secret."""
        return hashlib.sha256(secret.encode()).hexdigest() == secret_hash
    
    async def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scope: str,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        db: AsyncSession = None
    ) -> str:
        """Create authorization code."""
        code = generate_secure_token(32)
        
        # Store authorization code
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=datetime.now() + timedelta(seconds=self.authorization_code_lifetime)
        )
        
        db.add(auth_code)
        await db.commit()
        
        return code
    
    async def exchange_authorization_code(
        self,
        code: str,
        client_id: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None,
        db: AsyncSession = None
    ) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for tokens."""
        # Get authorization code
        query = select(OAuth2AuthorizationCode).where(
            OAuth2AuthorizationCode.code == code,
            OAuth2AuthorizationCode.client_id == client_id
        )
        result = await db.execute(query)
        auth_code = result.scalar_one_or_none()
        
        if not auth_code or auth_code.expires_at < datetime.now():
            return None
        
        # Validate redirect URI
        if auth_code.redirect_uri != redirect_uri:
            return None
        
        # Validate PKCE if required
        if self.enable_pkce and auth_code.code_challenge:
            if not code_verifier:
                return None
            if not verify_pkce_challenge(code_verifier, auth_code.code_challenge, auth_code.code_challenge_method):
                return None
        elif self.require_pkce:
            return None
        
        # Create tokens
        tokens = await self.create_tokens(
            client_id=client_id,
            user_id=auth_code.user_id,
            scope=auth_code.scope,
            db=db
        )
        
        # Delete used authorization code
        await db.delete(auth_code)
        await db.commit()
        
        return tokens
    
    async def create_tokens(
        self,
        client_id: str,
        user_id: str,
        scope: str,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Create access and refresh tokens."""
        await self.connect_redis()
        
        # Create access token
        access_token_payload = {{
            "sub": user_id,
            "client_id": client_id,
            "scope": scope,
            "iat": datetime.now().timestamp(),
            "exp": (datetime.now() + timedelta(seconds=self.access_token_lifetime)).timestamp(),
            "iss": self.config['server_config']['issuer'],
            "aud": "ainflue-api"
        }}
        
        access_token = jwt.encode(access_token_payload, "your-secret-key", algorithm=self.jwt_algorithm)
        
        # Create refresh token
        refresh_token = generate_secure_token(64)
        
        # Store refresh token in Redis
        refresh_token_data = {{
            "client_id": client_id,
            "user_id": user_id,
            "scope": scope,
            "created_at": datetime.now().isoformat()
        }}
        
        await self.redis_client.setex(
            f"refresh_token:{{refresh_token}}",
            self.refresh_token_lifetime,
            json.dumps(refresh_token_data)
        )
        
        # Store token in database
        token_record = OAuth2Token(
            access_token_hash=hashlib.sha256(access_token.encode()).hexdigest(),
            refresh_token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            client_id=client_id,
            user_id=user_id,
            scope=scope,
            expires_at=datetime.now() + timedelta(seconds=self.access_token_lifetime)
        )
        
        db.add(token_record)
        await db.commit()
        
        return {{
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_lifetime,
            "refresh_token": refresh_token,
            "scope": scope
        }}
    
    async def refresh_access_token(
        self,
        refresh_token: str,
        client_id: str,
        db: AsyncSession = None
    ) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        await self.connect_redis()
        
        # Get refresh token data
        token_data = await self.redis_client.get(f"refresh_token:{{refresh_token}}")
        if not token_data:
            return None
        
        token_info = json.loads(token_data)
        
        # Validate client
        if token_info["client_id"] != client_id:
            return None
        
        # Create new tokens
        new_tokens = await self.create_tokens(
            client_id=token_info["client_id"],
            user_id=token_info["user_id"],
            scope=token_info["scope"],
            db=db
        )
        
        # Revoke old refresh token
        await self.redis_client.delete(f"refresh_token:{{refresh_token}}")
        
        return new_tokens
    
    async def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify access token."""
        try:
            payload = jwt.decode(token, "your-secret-key", algorithms=[self.jwt_algorithm])
            return payload
        except jwt.InvalidTokenError:
            return None
    
    async def get_user_info(self, user_id: str, db: AsyncSession = None) -> Optional[UserInfoResponse]:
        """Get user information for userinfo endpoint."""
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        return UserInfoResponse(
            sub=str(user.id),
            username=user.username,
            email=user.email,
            email_verified=user.email_verified,
            name=user.full_name,
            picture=user.avatar_url,
            is_creator=user.is_creator,
            creator_id=str(user.creator_id) if user.creator_id else None
        )'''
    
    def _generate_endpoints(self, config: OAuth2ProviderConfig) -> str:
        """Generate OAuth2 endpoints."""
        return f'''# OAuth2 Endpoints

app = FastAPI(title="{config.provider_name}", version="1.0.0")
oauth2_provider = OAuth2Provider()
templates = Jinja2Templates(directory="templates")

@app.get("/oauth2/authorize")
async def authorize_endpoint(
    request: Request,
    client_id: str = Query(...),
    response_type: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(""),
    state: Optional[str] = Query(None),
    code_challenge: Optional[str] = Query(None),
    code_challenge_method: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """OAuth2 authorization endpoint."""
    
    # Create authorization request
    auth_request = AuthorizationRequest(
        client_id=client_id,
        response_type=response_type,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method
    )
    
    # Validate request
    if not auth_request.validate():
        raise HTTPException(status_code=400, detail="Invalid authorization request")
    
    # Validate client
    client = await oauth2_provider.validate_client(client_id, db=db)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client")
    
    # Validate redirect URI
    if redirect_uri not in client.redirect_uris:
        raise HTTPException(status_code=400, detail="Invalid redirect URI")
    
    # Check if user is authenticated
    user = request.session.get("user")
    if not user:
        # Redirect to login with return URL
        login_url = f"/login?return_to={{request.url}}"
        return RedirectResponse(login_url)
    
    # Check if user has already granted consent
    # For demo purposes, we'll show consent form
    return templates.TemplateResponse("consent.html", {{
        "request": request,
        "client": client,
        "scopes": scope.split(" ") if scope else [],
        "auth_request": auth_request
    }})

@app.post("/oauth2/authorize")
async def authorize_consent(
    request: Request,
    client_id: str = Form(...),
    response_type: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(""),
    state: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
    consent: str = Form(...),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle authorization consent."""
    
    if consent != "allow":
        error_params = "error=access_denied"
        if state:
            error_params += f"&state={{state}}"
        return RedirectResponse(f"{{redirect_uri}}?{{error_params}}")
    
    # Get authenticated user
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # Create authorization code
    code = await oauth2_provider.create_authorization_code(
        client_id=client_id,
        user_id=user["id"],
        redirect_uri=redirect_uri,
        scope=scope,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        db=db
    )
    
    # Redirect back to client with authorization code
    success_params = f"code={{code}}"
    if state:
        success_params += f"&state={{state}}"
    
    return RedirectResponse(f"{{redirect_uri}}?{{success_params}}")

@app.post("/oauth2/token")
async def token_endpoint(
    request: Request,
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: Optional[str] = Form(None),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db_session)
):
    """OAuth2 token endpoint."""
    
    # Create token request
    token_request = TokenRequest(
        grant_type=grant_type,
        client_id=client_id,
        client_secret=client_secret,
        code=code,
        redirect_uri=redirect_uri,
        refresh_token=refresh_token,
        code_verifier=code_verifier
    )
    
    # Validate request
    if not token_request.validate():
        raise HTTPException(status_code=400, detail="Invalid token request")
    
    # Validate client
    client = await oauth2_provider.validate_client(client_id, client_secret, db=db)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client")
    
    # Handle different grant types
    if grant_type == GrantType.AUTHORIZATION_CODE.value:
        tokens = await oauth2_provider.exchange_authorization_code(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            db=db
        )
    elif grant_type == GrantType.REFRESH_TOKEN.value:
        tokens = await oauth2_provider.refresh_access_token(
            refresh_token=refresh_token,
            client_id=client_id,
            db=db
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")
    
    if not tokens:
        raise HTTPException(status_code=400, detail="Invalid grant")
    
    return JSONResponse(tokens)

@app.get("/oauth2/userinfo")
async def userinfo_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db_session)
):
    """OAuth2 userinfo endpoint."""
    
    # Verify access token
    token_payload = await oauth2_provider.verify_access_token(credentials.credentials)
    if not token_payload:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    # Check scope
    scopes = token_payload.get("scope", "").split(" ")
    if "read:profile" not in scopes:
        raise HTTPException(status_code=403, detail="Insufficient scope")
    
    # Get user info
    user_info = await oauth2_provider.get_user_info(token_payload["sub"], db=db)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_info.dict()

@app.get("/oauth2/jwks")
async def jwks_endpoint():
    """OAuth2 JWKS endpoint."""
    # Return public keys for token verification
    return {{
        "keys": [
            # Add your public keys here
        ]
    }}

@app.get("/.well-known/oauth-authorization-server")
async def discovery_endpoint():
    """OAuth2 discovery endpoint."""
    return {{
        "issuer": oauth2_provider.config['server_config']['issuer'],
        "authorization_endpoint": f"{{oauth2_provider.config['server_config']['issuer']}}{{oauth2_provider.config['server_config']['authorization_endpoint']}}",
        "token_endpoint": f"{{oauth2_provider.config['server_config']['issuer']}}{{oauth2_provider.config['server_config']['token_endpoint']}}",
        "userinfo_endpoint": f"{{oauth2_provider.config['server_config']['issuer']}}{{oauth2_provider.config['server_config']['userinfo_endpoint']}}",
        "jwks_uri": f"{{oauth2_provider.config['server_config']['issuer']}}{{oauth2_provider.config['server_config']['jwks_uri']}}",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"] if oauth2_provider.enable_pkce else [],
        "scopes_supported": oauth2_provider.config['creator_scopes']
    }}'''
    
    def _generate_client_management(self, config: OAuth2ProviderConfig) -> str:
        """Generate client management functionality."""
        return '''# OAuth2 Client Management

class OAuth2ClientManager:
    """Manage OAuth2 clients."""
    
    @staticmethod
    async def create_client(
        name: str,
        redirect_uris: List[str],
        is_confidential: bool = True,
        scopes: Optional[List[str]] = None,
        db: AsyncSession = None
    ) -> OAuth2Client:
        """Create new OAuth2 client."""
        
        client_id = f"client_{generate_secure_token(16)}"
        client_secret = generate_secure_token(32) if is_confidential else None
        client_secret_hash = hashlib.sha256(client_secret.encode()).hexdigest() if client_secret else None
        
        client = OAuth2Client(
            client_id=client_id,
            client_secret_hash=client_secret_hash,
            name=name,
            redirect_uris=redirect_uris,
            is_confidential=is_confidential,
            is_active=True,
            scopes=scopes or ["read:profile"],
            created_at=datetime.now()
        )
        
        db.add(client)
        await db.commit()
        
        return client, client_secret
    
    @staticmethod
    async def get_client(client_id: str, db: AsyncSession = None) -> Optional[OAuth2Client]:
        """Get OAuth2 client by ID."""
        query = select(OAuth2Client).where(OAuth2Client.client_id == client_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_client(
        client_id: str,
        updates: Dict[str, Any],
        db: AsyncSession = None
    ) -> bool:
        """Update OAuth2 client."""
        query = update(OAuth2Client).where(OAuth2Client.client_id == client_id).values(**updates)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def delete_client(client_id: str, db: AsyncSession = None) -> bool:
        """Delete OAuth2 client."""
        query = delete(OAuth2Client).where(OAuth2Client.client_id == client_id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0'''
    
    def _generate_token_management(self, config: OAuth2ProviderConfig) -> str:
        """Generate token management functionality."""
        return '''# OAuth2 Token Management

class OAuth2TokenManager:
    """Manage OAuth2 tokens."""
    
    @staticmethod
    async def introspect_token(token: str, db: AsyncSession = None) -> Dict[str, Any]:
        """Introspect OAuth2 token."""
        try:
            payload = jwt.decode(token, "your-secret-key", algorithms=["RS256"])
            
            # Check if token exists in database
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            query = select(OAuth2Token).where(OAuth2Token.access_token_hash == token_hash)
            result = await db.execute(query)
            token_record = result.scalar_one_or_none()
            
            if not token_record or token_record.expires_at < datetime.now():
                return {"active": False}
            
            return {
                "active": True,
                "client_id": payload.get("client_id"),
                "username": payload.get("sub"),
                "scope": payload.get("scope"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "sub": payload.get("sub"),
                "aud": payload.get("aud"),
                "iss": payload.get("iss")
            }
            
        except jwt.InvalidTokenError:
            return {"active": False}
    
    @staticmethod
    async def revoke_token(token: str, db: AsyncSession = None) -> bool:
        """Revoke OAuth2 token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Remove from database
        query = delete(OAuth2Token).where(OAuth2Token.access_token_hash == token_hash)
        result = await db.execute(query)
        await db.commit()
        
        return result.rowcount > 0
    
    @staticmethod
    async def cleanup_expired_tokens(db: AsyncSession = None):
        """Clean up expired tokens."""
        query = delete(OAuth2Token).where(OAuth2Token.expires_at < datetime.now())
        result = await db.execute(query)
        await db.commit()
        
        logger.info(f"Cleaned up {result.rowcount} expired tokens")'''
    
    def _generate_provider_config(self, config: OAuth2ProviderConfig) -> str:
        """Generate provider configuration."""
        return f'''# OAuth2 Provider Configuration

OAUTH2_CONFIG = {config.dict()}

def apply_security_policies(provider: OAuth2Provider) -> OAuth2Provider:
    """Apply security policies to OAuth2 provider."""
    # Add additional security validations
    # Add rate limiting
    # Add audit logging
    return provider

def apply_oauth2_monitoring(provider: OAuth2Provider) -> OAuth2Provider:
    """Apply monitoring to OAuth2 provider."""
    # Add metrics collection
    # Add performance tracking
    # Add security monitoring
    return provider

# Security utilities
def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure token."""
    return secrets.token_urlsafe(length)

def verify_pkce_challenge(verifier: str, challenge: str, method: str = "S256") -> bool:
    """Verify PKCE challenge."""
    if method == "S256":
        computed_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        return computed_challenge == challenge
    elif method == "plain":
        return verifier == challenge
    return False'''


# Register template
from .template_registry import register_template

register_template(
    OAuth2ProviderTemplate,
    OAuth2ProviderTemplate().metadata
)