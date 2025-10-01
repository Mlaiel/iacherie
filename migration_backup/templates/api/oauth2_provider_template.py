"""OAuth2 Provider Template for IA Chéries Platform
Enterprise-grade OAuth2 server implementation with PKCE and security

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import secrets
import hashlib
import base64
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import urllib.parse

from fastapi import APIRouter, HTTPException, Depends, status, Form, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from core.config import get_settings
from core.database import get_db_session
from core.auth import verify_password, hash_password, create_jwt_token
from core.rate_limiting import oauth2_rate_limit
from core.logging import log_oauth2_event
from utils.exceptions import OAuth2Exception, AuthenticationException
from monitoring.api_metrics import OAuth2Metrics

logger = logging.getLogger(__name__)
settings = get_settings()


class OAuth2ResponseType(Enum):
    """OAuth2 response types"""
    CODE = "code"
    TOKEN = "token"  # Implicit flow (deprecated)


class OAuth2GrantType(Enum):
    """OAuth2 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"  # Resource owner password credentials


class OAuth2TokenType(Enum):
    """OAuth2 token types"""
    BEARER = "Bearer"


class OAuth2CodeChallengeMethod(Enum):
    """PKCE code challenge methods"""
    PLAIN = "plain"
    S256 = "S256"


@dataclass
class OAuth2Client:
    """OAuth2 client configuration"""
    client_id: str
    client_secret: str
    name: str
    description: str
    redirect_uris: List[str]
    scopes: List[str]
    grant_types: List[str]
    is_confidential: bool = True
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class OAuth2AuthorizationCode:
    """OAuth2 authorization code"""
    code: str
    client_id: str
    user_id: str
    redirect_uri: str
    scopes: List[str]
    expires_at: datetime
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    used: bool = False


@dataclass
class OAuth2AccessToken:
    """OAuth2 access token"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    scopes: List[str]
    client_id: str
    user_id: Optional[str] = None
    created_at: datetime = None


class OAuth2AuthorizationRequest(BaseModel):
    """OAuth2 authorization request model"""
    response_type: str = Field(..., description="Response type (code)")
    client_id: str = Field(..., description="Client identifier")
    redirect_uri: str = Field(..., description="Redirect URI")
    scope: Optional[str] = Field(None, description="Requested scopes")
    state: Optional[str] = Field(None, description="State parameter")
    code_challenge: Optional[str] = Field(None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field("S256", description="PKCE challenge method")
    
    @validator('response_type')
    def validate_response_type(cls, v):
        if v not in [rt.value for rt in OAuth2ResponseType]:
            raise ValueError('Invalid response type')
        return v
    
    @validator('code_challenge_method')
    def validate_challenge_method(cls, v):
        if v and v not in [cm.value for cm in OAuth2CodeChallengeMethod]:
            raise ValueError('Invalid code challenge method')
        return v


class OAuth2TokenRequest(BaseModel):
    """OAuth2 token request model"""
    grant_type: str = Field(..., description="Grant type")
    code: Optional[str] = Field(None, description="Authorization code")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI")
    client_id: Optional[str] = Field(None, description="Client identifier")
    client_secret: Optional[str] = Field(None, description="Client secret")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    code_verifier: Optional[str] = Field(None, description="PKCE code verifier")
    username: Optional[str] = Field(None, description="Username (password grant)")
    password: Optional[str] = Field(None, description="Password (password grant)")
    scope: Optional[str] = Field(None, description="Requested scopes")
    
    @validator('grant_type')
    def validate_grant_type(cls, v):
        if v not in [gt.value for gt in OAuth2GrantType]:
            raise ValueError('Invalid grant type')
        return v


class OAuth2TokenResponse(BaseModel):
    """OAuth2 token response model"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class OAuth2ErrorResponse(BaseModel):
    """OAuth2 error response model"""
    error: str
    error_description: Optional[str] = None
    error_uri: Optional[str] = None
    state: Optional[str] = None


class OAuth2Provider:
    """Enterprise OAuth2 provider implementation"""
    
    def __init__(self):
        self.redis_client = None
        self.metrics = OAuth2Metrics()
        self.code_ttl = 600  # 10 minutes
        self.access_token_ttl = 3600  # 1 hour
        self.refresh_token_ttl = 2592000  # 30 days
    
    async def initialize(self):
        """Initialize OAuth2 provider"""
        if not self.redis_client:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get_client(self, client_id: str) -> Optional[OAuth2Client]:
        """Get OAuth2 client by ID"""
        async with get_db_session() as session:
            # Query from database
            result = await session.execute(
                "SELECT * FROM oauth2_clients WHERE client_id = :client_id AND is_active = true",
                {"client_id": client_id}
            )
            row = result.fetchone()
            
            if not row:
                return None
            
            return OAuth2Client(
                client_id=row.client_id,
                client_secret=row.client_secret,
                name=row.name,
                description=row.description,
                redirect_uris=json.loads(row.redirect_uris),
                scopes=json.loads(row.scopes),
                grant_types=json.loads(row.grant_types),
                is_confidential=row.is_confidential,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
    
    async def validate_redirect_uri(self, client: OAuth2Client, redirect_uri: str) -> bool:
        """Validate redirect URI against registered URIs"""
        return redirect_uri in client.redirect_uris
    
    async def validate_scopes(self, client: OAuth2Client, requested_scopes: List[str]) -> bool:
        """Validate requested scopes against client allowed scopes"""
        return all(scope in client.scopes for scope in requested_scopes)
    
    def generate_authorization_code(self) -> str:
        """Generate secure authorization code"""
        return secrets.token_urlsafe(32)
    
    def generate_access_token(self) -> str:
        """Generate secure access token"""
        return secrets.token_urlsafe(32)
    
    def generate_refresh_token(self) -> str:
        """Generate secure refresh token"""
        return secrets.token_urlsafe(32)
    
    def verify_code_challenge(self, code_verifier: str, code_challenge: str, method: str) -> bool:
        """Verify PKCE code challenge"""
        if method == OAuth2CodeChallengeMethod.PLAIN.value:
            return code_verifier == code_challenge
        elif method == OAuth2CodeChallengeMethod.S256.value:
            digest = hashlib.sha256(code_verifier.encode()).digest()
            challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
            return challenge == code_challenge
        return False
    
    async def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        redirect_uri: str,
        scopes: List[str],
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None
    ) -> str:
        """Create and store authorization code"""
        await self.initialize()
        
        code = self.generate_authorization_code()
        
        auth_code = OAuth2AuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            expires_at=datetime.utcnow() + timedelta(seconds=self.code_ttl),
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )
        
        # Store in Redis with TTL
        await self.redis_client.setex(
            f"oauth2:code:{code}",
            self.code_ttl,
            json.dumps({
                "client_id": auth_code.client_id,
                "user_id": auth_code.user_id,
                "redirect_uri": auth_code.redirect_uri,
                "scopes": auth_code.scopes,
                "expires_at": auth_code.expires_at.isoformat(),
                "code_challenge": auth_code.code_challenge,
                "code_challenge_method": auth_code.code_challenge_method,
                "used": auth_code.used
            })
        )
        
        return code
    
    async def get_authorization_code(self, code: str) -> Optional[OAuth2AuthorizationCode]:
        """Get authorization code"""
        await self.initialize()
        
        data = await self.redis_client.get(f"oauth2:code:{code}")
        if not data:
            return None
        
        code_data = json.loads(data)
        
        return OAuth2AuthorizationCode(
            code=code,
            client_id=code_data["client_id"],
            user_id=code_data["user_id"],
            redirect_uri=code_data["redirect_uri"],
            scopes=code_data["scopes"],
            expires_at=datetime.fromisoformat(code_data["expires_at"]),
            code_challenge=code_data.get("code_challenge"),
            code_challenge_method=code_data.get("code_challenge_method"),
            used=code_data.get("used", False)
        )
    
    async def use_authorization_code(self, code: str) -> bool:
        """Mark authorization code as used"""
        await self.initialize()
        
        # Delete the code to prevent reuse
        result = await self.redis_client.delete(f"oauth2:code:{code}")
        return result > 0
    
    async def create_access_token(
        self,
        client_id: str,
        scopes: List[str],
        user_id: Optional[str] = None
    ) -> OAuth2AccessToken:
        """Create access and refresh tokens"""
        await self.initialize()
        
        access_token = self.generate_access_token()
        refresh_token = self.generate_refresh_token()
        
        token_data = OAuth2AccessToken(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=OAuth2TokenType.BEARER.value,
            expires_in=self.access_token_ttl,
            scopes=scopes,
            client_id=client_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        
        # Store access token
        await self.redis_client.setex(
            f"oauth2:access_token:{access_token}",
            self.access_token_ttl,
            json.dumps({
                "client_id": token_data.client_id,
                "user_id": token_data.user_id,
                "scopes": token_data.scopes,
                "created_at": token_data.created_at.isoformat()
            })
        )
        
        # Store refresh token
        await self.redis_client.setex(
            f"oauth2:refresh_token:{refresh_token}",
            self.refresh_token_ttl,
            json.dumps({
                "access_token": access_token,
                "client_id": token_data.client_id,
                "user_id": token_data.user_id,
                "scopes": token_data.scopes,
                "created_at": token_data.created_at.isoformat()
            })
        )
        
        return token_data
    
    async def get_access_token(self, token: str) -> Optional[OAuth2AccessToken]:
        """Get access token information"""
        await self.initialize()
        
        data = await self.redis_client.get(f"oauth2:access_token:{token}")
        if not data:
            return None
        
        token_data = json.loads(data)
        
        return OAuth2AccessToken(
            access_token=token,
            refresh_token=None,  # Don't return refresh token
            token_type=OAuth2TokenType.BEARER.value,
            expires_in=self.access_token_ttl,
            scopes=token_data["scopes"],
            client_id=token_data["client_id"],
            user_id=token_data.get("user_id"),
            created_at=datetime.fromisoformat(token_data["created_at"])
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[OAuth2AccessToken]:
        """Refresh access token"""
        await self.initialize()
        
        # Get refresh token data
        data = await self.redis_client.get(f"oauth2:refresh_token:{refresh_token}")
        if not data:
            return None
        
        token_data = json.loads(data)
        
        # Revoke old tokens
        old_access_token = token_data["access_token"]
        await self.redis_client.delete(f"oauth2:access_token:{old_access_token}")
        await self.redis_client.delete(f"oauth2:refresh_token:{refresh_token}")
        
        # Create new tokens
        return await self.create_access_token(
            client_id=token_data["client_id"],
            scopes=token_data["scopes"],
            user_id=token_data.get("user_id")
        )
    
    async def revoke_token(self, token: str, token_type_hint: Optional[str] = None) -> bool:
        """Revoke access or refresh token"""
        await self.initialize()
        
        revoked = False
        
        # Try access token
        if await self.redis_client.delete(f"oauth2:access_token:{token}") > 0:
            revoked = True
        
        # Try refresh token
        if await self.redis_client.delete(f"oauth2:refresh_token:{token}") > 0:
            revoked = True
        
        return revoked


# Create OAuth2 provider instance
oauth2_provider = OAuth2Provider()

# Create router
router = APIRouter(prefix="/oauth2", tags=["OAuth2"])


@router.get("/authorize")
async def authorize(
    request: Request,
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    code_challenge: Optional[str] = Query(None),
    code_challenge_method: Optional[str] = Query("S256")
):
    """OAuth2 authorization endpoint"""
    
    try:
        # Rate limiting
        client_ip = request.client.host
        if not await oauth2_rate_limit(f"oauth2:authorize:{client_ip}", calls=10, period=60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Validate request
        auth_request = OAuth2AuthorizationRequest(
            response_type=response_type,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )
        
        # Get and validate client
        client = await oauth2_provider.get_client(client_id)
        if not client:
            raise OAuth2Exception("invalid_client", "Invalid client")
        
        # Validate redirect URI
        if not await oauth2_provider.validate_redirect_uri(client, redirect_uri):
            raise OAuth2Exception("invalid_request", "Invalid redirect URI")
        
        # Validate grant type
        if OAuth2GrantType.AUTHORIZATION_CODE.value not in client.grant_types:
            raise OAuth2Exception("unsupported_grant_type", "Authorization code grant not supported")
        
        # Parse and validate scopes
        requested_scopes = scope.split() if scope else []
        if not await oauth2_provider.validate_scopes(client, requested_scopes):
            raise OAuth2Exception("invalid_scope", "Invalid scope")
        
        # PKCE validation for public clients
        if not client.is_confidential and not code_challenge:
            raise OAuth2Exception("invalid_request", "PKCE required for public clients")
        
        # Check if user is authenticated
        # This would typically check session or redirect to login
        user_id = request.session.get("user_id")
        if not user_id:
            # Redirect to login with return URL
            login_url = f"/auth/login?return_url={urllib.parse.quote(str(request.url))}"
            return RedirectResponse(url=login_url)
        
        # Generate authorization code
        code = await oauth2_provider.create_authorization_code(
            client_id=client_id,
            user_id=user_id,
            redirect_uri=redirect_uri,
            scopes=requested_scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )
        
        # Build redirect URL
        redirect_params = {"code": code}
        if state:
            redirect_params["state"] = state
        
        redirect_url = f"{redirect_uri}?{urllib.parse.urlencode(redirect_params)}"
        
        # Log event
        log_oauth2_event(
            event_type="authorization_granted",
            client_id=client_id,
            user_id=user_id,
            scopes=requested_scopes
        )
        
        # Record metrics
        oauth2_provider.metrics.record_authorization(client_id, user_id)
        
        return RedirectResponse(url=redirect_url)
        
    except OAuth2Exception as e:
        # Redirect with error
        error_params = {
            "error": e.error,
            "error_description": e.description
        }
        if state:
            error_params["state"] = state
        
        error_url = f"{redirect_uri}?{urllib.parse.urlencode(error_params)}"
        return RedirectResponse(url=error_url)
    
    except Exception as e:
        logger.error(f"Authorization error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/token", response_model=OAuth2TokenResponse)
async def token(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    scope: Optional[str] = Form(None)
):
    """OAuth2 token endpoint"""
    
    try:
        # Rate limiting
        client_ip = request.client.host
        if not await oauth2_rate_limit(f"oauth2:token:{client_ip}", calls=20, period=60):
            raise OAuth2Exception("temporarily_unavailable", "Rate limit exceeded")
        
        # Parse request
        token_request = OAuth2TokenRequest(
            grant_type=grant_type,
            code=code,
            redirect_uri=redirect_uri,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            code_verifier=code_verifier,
            username=username,
            password=password,
            scope=scope
        )
        
        # Handle different grant types
        if grant_type == OAuth2GrantType.AUTHORIZATION_CODE.value:
            return await handle_authorization_code_grant(token_request)
        elif grant_type == OAuth2GrantType.REFRESH_TOKEN.value:
            return await handle_refresh_token_grant(token_request)
        elif grant_type == OAuth2GrantType.CLIENT_CREDENTIALS.value:
            return await handle_client_credentials_grant(token_request)
        elif grant_type == OAuth2GrantType.PASSWORD.value:
            return await handle_password_grant(token_request)
        else:
            raise OAuth2Exception("unsupported_grant_type", "Grant type not supported")
        
    except OAuth2Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.error,
                "error_description": e.description
            }
        )
    
    except Exception as e:
        logger.error(f"Token error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "server_error", "error_description": "Internal server error"}
        )


async def handle_authorization_code_grant(token_request: OAuth2TokenRequest) -> OAuth2TokenResponse:
    """Handle authorization code grant"""
    
    if not token_request.code:
        raise OAuth2Exception("invalid_request", "Code is required")
    
    # Get client
    client = await oauth2_provider.get_client(token_request.client_id)
    if not client:
        raise OAuth2Exception("invalid_client", "Invalid client")
    
    # Authenticate client
    if client.is_confidential:
        if not token_request.client_secret or client.client_secret != token_request.client_secret:
            raise OAuth2Exception("invalid_client", "Invalid client credentials")
    
    # Get authorization code
    auth_code = await oauth2_provider.get_authorization_code(token_request.code)
    if not auth_code:
        raise OAuth2Exception("invalid_grant", "Invalid authorization code")
    
    # Validate code
    if auth_code.used or datetime.utcnow() > auth_code.expires_at:
        raise OAuth2Exception("invalid_grant", "Authorization code expired or used")
    
    if auth_code.client_id != token_request.client_id:
        raise OAuth2Exception("invalid_grant", "Client mismatch")
    
    if auth_code.redirect_uri != token_request.redirect_uri:
        raise OAuth2Exception("invalid_grant", "Redirect URI mismatch")
    
    # PKCE verification
    if auth_code.code_challenge:
        if not token_request.code_verifier:
            raise OAuth2Exception("invalid_request", "Code verifier required")
        
        if not oauth2_provider.verify_code_challenge(
            token_request.code_verifier,
            auth_code.code_challenge,
            auth_code.code_challenge_method
        ):
            raise OAuth2Exception("invalid_grant", "Invalid code verifier")
    
    # Use the code (delete it)
    await oauth2_provider.use_authorization_code(token_request.code)
    
    # Create access token
    access_token = await oauth2_provider.create_access_token(
        client_id=auth_code.client_id,
        scopes=auth_code.scopes,
        user_id=auth_code.user_id
    )
    
    # Log event
    log_oauth2_event(
        event_type="token_issued",
        client_id=auth_code.client_id,
        user_id=auth_code.user_id,
        grant_type="authorization_code"
    )
    
    # Record metrics
    oauth2_provider.metrics.record_token_issued("authorization_code", auth_code.client_id)
    
    return OAuth2TokenResponse(
        access_token=access_token.access_token,
        token_type=access_token.token_type,
        expires_in=access_token.expires_in,
        refresh_token=access_token.refresh_token,
        scope=" ".join(access_token.scopes)
    )


async def handle_refresh_token_grant(token_request: OAuth2TokenRequest) -> OAuth2TokenResponse:
    """Handle refresh token grant"""
    
    if not token_request.refresh_token:
        raise OAuth2Exception("invalid_request", "Refresh token is required")
    
    # Refresh access token
    access_token = await oauth2_provider.refresh_access_token(token_request.refresh_token)
    if not access_token:
        raise OAuth2Exception("invalid_grant", "Invalid refresh token")
    
    # Log event
    log_oauth2_event(
        event_type="token_refreshed",
        client_id=access_token.client_id,
        user_id=access_token.user_id
    )
    
    # Record metrics
    oauth2_provider.metrics.record_token_refreshed(access_token.client_id)
    
    return OAuth2TokenResponse(
        access_token=access_token.access_token,
        token_type=access_token.token_type,
        expires_in=access_token.expires_in,
        refresh_token=access_token.refresh_token,
        scope=" ".join(access_token.scopes)
    )


async def handle_client_credentials_grant(token_request: OAuth2TokenRequest) -> OAuth2TokenResponse:
    """Handle client credentials grant"""
    
    # Get and authenticate client
    client = await oauth2_provider.get_client(token_request.client_id)
    if not client:
        raise OAuth2Exception("invalid_client", "Invalid client")
    
    if not token_request.client_secret or client.client_secret != token_request.client_secret:
        raise OAuth2Exception("invalid_client", "Invalid client credentials")
    
    # Check if client credentials grant is allowed
    if OAuth2GrantType.CLIENT_CREDENTIALS.value not in client.grant_types:
        raise OAuth2Exception("unauthorized_client", "Client credentials grant not allowed")
    
    # Parse scopes
    requested_scopes = token_request.scope.split() if token_request.scope else client.scopes
    if not await oauth2_provider.validate_scopes(client, requested_scopes):
        raise OAuth2Exception("invalid_scope", "Invalid scope")
    
    # Create access token (no refresh token for client credentials)
    access_token = await oauth2_provider.create_access_token(
        client_id=client.client_id,
        scopes=requested_scopes
    )
    
    # Log event
    log_oauth2_event(
        event_type="token_issued",
        client_id=client.client_id,
        grant_type="client_credentials"
    )
    
    # Record metrics
    oauth2_provider.metrics.record_token_issued("client_credentials", client.client_id)
    
    return OAuth2TokenResponse(
        access_token=access_token.access_token,
        token_type=access_token.token_type,
        expires_in=access_token.expires_in,
        scope=" ".join(access_token.scopes)
    )


async def handle_password_grant(token_request: OAuth2TokenRequest) -> OAuth2TokenResponse:
    """Handle resource owner password credentials grant (discouraged)"""
    
    if not token_request.username or not token_request.password:
        raise OAuth2Exception("invalid_request", "Username and password are required")
    
    # Get and authenticate client
    client = await oauth2_provider.get_client(token_request.client_id)
    if not client:
        raise OAuth2Exception("invalid_client", "Invalid client")
    
    # Check if password grant is allowed
    if OAuth2GrantType.PASSWORD.value not in client.grant_types:
        raise OAuth2Exception("unauthorized_client", "Password grant not allowed")
    
    # Authenticate user
    async with get_db_session() as session:
        # Query user
        result = await session.execute(
            "SELECT id, password_hash, is_active FROM users WHERE email = :email OR username = :username",
            {"email": token_request.username, "username": token_request.username}
        )
        user = result.fetchone()
        
        if not user or not user.is_active:
            raise OAuth2Exception("invalid_grant", "Invalid credentials")
        
        if not verify_password(token_request.password, user.password_hash):
            raise OAuth2Exception("invalid_grant", "Invalid credentials")
        
        user_id = str(user.id)
    
    # Parse scopes
    requested_scopes = token_request.scope.split() if token_request.scope else []
    if not await oauth2_provider.validate_scopes(client, requested_scopes):
        raise OAuth2Exception("invalid_scope", "Invalid scope")
    
    # Create access token
    access_token = await oauth2_provider.create_access_token(
        client_id=client.client_id,
        scopes=requested_scopes,
        user_id=user_id
    )
    
    # Log event
    log_oauth2_event(
        event_type="token_issued",
        client_id=client.client_id,
        user_id=user_id,
        grant_type="password"
    )
    
    # Record metrics
    oauth2_provider.metrics.record_token_issued("password", client.client_id)
    
    return OAuth2TokenResponse(
        access_token=access_token.access_token,
        token_type=access_token.token_type,
        expires_in=access_token.expires_in,
        refresh_token=access_token.refresh_token,
        scope=" ".join(access_token.scopes)
    )


@router.post("/revoke")
async def revoke(
    request: Request,
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None)
):
    """OAuth2 token revocation endpoint"""
    
    try:
        # Rate limiting
        client_ip = request.client.host
        if not await oauth2_rate_limit(f"oauth2:revoke:{client_ip}", calls=10, period=60):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Authenticate client if provided
        if client_id:
            client = await oauth2_provider.get_client(client_id)
            if not client:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            
            if client.is_confidential and client.client_secret != client_secret:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Revoke token
        revoked = await oauth2_provider.revoke_token(token, token_type_hint)
        
        # Log event
        log_oauth2_event(
            event_type="token_revoked",
            client_id=client_id,
            metadata={"token_type_hint": token_type_hint}
        )
        
        # Record metrics
        oauth2_provider.metrics.record_token_revoked(client_id)
        
        return JSONResponse(content={}, status_code=200)
        
    except Exception as e:
        logger.error(f"Token revocation error: {str(e)}")
        return JSONResponse(content={}, status_code=200)  # Always return 200 per spec


# Export for template system
__all__ = [
    "OAuth2Provider",
    "OAuth2Client",
    "OAuth2AuthorizationCode",
    "OAuth2AccessToken",
    "OAuth2AuthorizationRequest",
    "OAuth2TokenRequest",
    "OAuth2TokenResponse",
    "OAuth2ErrorResponse",
    "oauth2_provider",
    "router"
]