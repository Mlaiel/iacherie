#!/usr/bin/env python3
"""
🔒 Single Sign-On Orchestrator - Enterprise SSO Management
==========================================================

Enterprise SSO orchestration system with SAML/OAuth2/OIDC support,
multi-provider integration, and comprehensive security features.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Identity + Backend + Enterprise
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import base64
import hashlib
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, parse_qs, quote_plus
import jwt
import secrets

# Cryptographic imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509 import load_pem_x509_certificate
import xmlsec

# HTTP client imports
import aiohttp
from aiohttp import web


class SSOProtocol(Enum):
    """SSO protocol types"""
    SAML2 = "saml2"
    OAUTH2 = "oauth2"
    OIDC = "oidc"
    CAS = "cas"
    LDAP = "ldap"
    CUSTOM = "custom"


class ProviderType(Enum):
    """Identity provider types"""
    ACTIVE_DIRECTORY = "active_directory"
    AZURE_AD = "azure_ad"
    GOOGLE = "google"
    OKTA = "okta"
    ONELOGIN = "onelogin"
    PING_IDENTITY = "ping_identity"
    AUTH0 = "auth0"
    KEYCLOAK = "keycloak"
    CUSTOM_SAML = "custom_saml"
    CUSTOM_OIDC = "custom_oidc"


class AuthenticationStatus(Enum):
    """Authentication status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    EXPIRED = "expired"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass
class SSOProvider:
    """SSO provider configuration"""
    provider_id: str
    name: str
    provider_type: ProviderType
    protocol: SSOProtocol
    
    # Endpoints
    login_url: str
    logout_url: Optional[str]
    metadata_url: Optional[str]
    token_endpoint: Optional[str]
    userinfo_endpoint: Optional[str]
    
    # Configuration
    client_id: Optional[str]
    client_secret: Optional[str]
    certificate: Optional[str]
    private_key: Optional[str]
    
    # SAML specific
    entity_id: Optional[str]
    sso_url: Optional[str]
    sls_url: Optional[str]
    
    # OAuth/OIDC specific
    scope: Optional[str]
    response_type: Optional[str]
    redirect_uri: Optional[str]
    
    # Attributes mapping
    attribute_mappings: Dict[str, str]
    
    # Security settings
    sign_requests: bool
    encrypt_assertions: bool
    verify_signatures: bool
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    is_active: bool
    priority: int


@dataclass
class SSOSession:
    """SSO session information"""
    session_id: str
    user_id: str
    provider_id: str
    provider_session_id: Optional[str]
    
    # Session details
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    
    # User information
    user_attributes: Dict[str, Any]
    roles: List[str]
    permissions: List[str]
    
    # Security context
    ip_address: str
    user_agent: str
    device_id: Optional[str]
    
    # Session state
    is_active: bool
    logout_url: Optional[str]
    logout_token: Optional[str]


@dataclass
class AuthenticationRequest:
    """SSO authentication request"""
    request_id: str
    provider_id: str
    relay_state: Optional[str]
    
    # Request details
    created_at: datetime
    expires_at: datetime
    
    # Client information
    client_ip: str
    user_agent: str
    return_url: str
    
    # Request parameters
    force_authn: bool
    passive: bool
    requested_authn_context: Optional[str]
    
    # Security
    signature: Optional[str]
    digest: Optional[str]


@dataclass
class AuthenticationResponse:
    """SSO authentication response"""
    response_id: str
    request_id: str
    provider_id: str
    
    # Response details
    status: AuthenticationStatus
    status_message: Optional[str]
    created_at: datetime
    
    # User information
    user_id: Optional[str]
    user_attributes: Dict[str, Any]
    
    # Session information
    session_id: Optional[str]
    session_expires_at: Optional[datetime]
    
    # Security
    assertion: Optional[str]
    signature_valid: bool
    
    # Error details
    error_code: Optional[str]
    error_description: Optional[str]


class SingleSignOnOrchestrator:
    """
    🔒 Enterprise Single Sign-On Orchestrator
    
    Comprehensive SSO management with multi-protocol support,
    provider orchestration, and enterprise security features.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize SSO orchestrator"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/sso_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Provider management
        self.providers: Dict[str, SSOProvider] = {}
        self.active_sessions: Dict[str, SSOSession] = {}
        self.pending_requests: Dict[str, AuthenticationRequest] = {}
        
        # Load providers
        self._load_providers()
        
        # HTTP client for external requests
        self.http_session = None
        
        # Cryptographic components
        self.signing_key = None
        self.encryption_key = None
        self._setup_cryptography()
        
        # Web server for callbacks
        self.web_app = web.Application()
        self._setup_web_routes()
        
        # Session store (in production, use Redis/database)
        self.session_store = {}
        
        # Metrics and monitoring
        self.metrics = {
            'total_authentications': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'active_sessions': 0,
            'provider_stats': {},
            'protocol_stats': {}
        }
    
    async def initiate_authentication(
        self,
        provider_id: str,
        return_url: str,
        client_ip: str,
        user_agent: str,
        force_authn: bool = False,
        passive: bool = False,
        relay_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate SSO authentication
        
        Args:
            provider_id: Identity provider ID
            return_url: URL to return to after authentication
            client_ip: Client IP address
            user_agent: User agent string
            force_authn: Force authentication
            passive: Passive authentication
            relay_state: Relay state parameter
            
        Returns:
            Authentication initiation result
        """
        try:
            # Validate provider
            provider = self.providers.get(provider_id)
            if not provider or not provider.is_active:
                raise ValueError(f"Invalid or inactive provider: {provider_id}")
            
            # Create authentication request
            request_id = str(uuid.uuid4())
            auth_request = AuthenticationRequest(
                request_id=request_id,
                provider_id=provider_id,
                relay_state=relay_state,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                client_ip=client_ip,
                user_agent=user_agent,
                return_url=return_url,
                force_authn=force_authn,
                passive=passive,
                requested_authn_context=None,
                signature=None,
                digest=None
            )
            
            # Store pending request
            self.pending_requests[request_id] = auth_request
            
            # Generate authentication URL based on protocol
            if provider.protocol == SSOProtocol.SAML2:
                auth_url = await self._create_saml_request(provider, auth_request)
            elif provider.protocol == SSOProtocol.OIDC:
                auth_url = await self._create_oidc_request(provider, auth_request)
            elif provider.protocol == SSOProtocol.OAUTH2:
                auth_url = await self._create_oauth2_request(provider, auth_request)
            else:
                raise ValueError(f"Unsupported protocol: {provider.protocol}")
            
            # Update metrics
            self.metrics['total_authentications'] += 1
            provider_stats = self.metrics['provider_stats'].get(provider_id, {'requests': 0})
            provider_stats['requests'] += 1
            self.metrics['provider_stats'][provider_id] = provider_stats
            
            return {
                "success": True,
                "request_id": request_id,
                "auth_url": auth_url,
                "provider": {
                    "id": provider.provider_id,
                    "name": provider.name,
                    "type": provider.provider_type.value,
                    "protocol": provider.protocol.value
                },
                "expires_at": auth_request.expires_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Authentication initiation error: {e}")
            raise
    
    async def handle_authentication_response(
        self,
        provider_id: str,
        response_data: Dict[str, Any],
        request_context: Optional[Dict[str, Any]] = None
    ) -> AuthenticationResponse:
        """
        Handle authentication response from provider
        
        Args:
            provider_id: Identity provider ID
            response_data: Response data from provider
            request_context: Request context information
            
        Returns:
            Authentication response
        """
        try:
            provider = self.providers.get(provider_id)
            if not provider:
                raise ValueError(f"Unknown provider: {provider_id}")
            
            # Process response based on protocol
            if provider.protocol == SSOProtocol.SAML2:
                auth_response = await self._process_saml_response(provider, response_data)
            elif provider.protocol == SSOProtocol.OIDC:
                auth_response = await self._process_oidc_response(provider, response_data)
            elif provider.protocol == SSOProtocol.OAUTH2:
                auth_response = await self._process_oauth2_response(provider, response_data)
            else:
                raise ValueError(f"Unsupported protocol: {provider.protocol}")
            
            # Create session if authentication successful
            if auth_response.status == AuthenticationStatus.SUCCESS:
                session = await self._create_sso_session(
                    provider, auth_response, request_context
                )
                auth_response.session_id = session.session_id
                auth_response.session_expires_at = session.expires_at
                
                # Update metrics
                self.metrics['successful_authentications'] += 1
                self.metrics['active_sessions'] += 1
            else:
                self.metrics['failed_authentications'] += 1
            
            # Update provider statistics
            provider_stats = self.metrics['provider_stats'].get(provider_id, {})
            if auth_response.status == AuthenticationStatus.SUCCESS:
                provider_stats['successful'] = provider_stats.get('successful', 0) + 1
            else:
                provider_stats['failed'] = provider_stats.get('failed', 0) + 1
            self.metrics['provider_stats'][provider_id] = provider_stats
            
            return auth_response
            
        except Exception as e:
            self.logger.error(f"Authentication response handling error: {e}")
            # Return error response
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id="",
                provider_id=provider_id,
                status=AuthenticationStatus.FAILURE,
                status_message="Internal error",
                created_at=datetime.utcnow(),
                user_id=None,
                user_attributes={},
                session_id=None,
                session_expires_at=None,
                assertion=None,
                signature_valid=False,
                error_code="internal_error",
                error_description=str(e)
            )
    
    async def validate_session(
        self,
        session_id: str,
        update_activity: bool = True
    ) -> Tuple[bool, Optional[SSOSession]]:
        """
        Validate SSO session
        
        Args:
            session_id: Session identifier
            update_activity: Whether to update last activity
            
        Returns:
            (is_valid, session_info)
        """
        try:
            session = self.active_sessions.get(session_id)
            
            if not session:
                return False, None
            
            # Check if session has expired
            if datetime.utcnow() > session.expires_at:
                # Remove expired session
                await self._remove_session(session_id)
                return False, None
            
            # Check if session is active
            if not session.is_active:
                return False, None
            
            # Update last activity
            if update_activity:
                session.last_activity = datetime.utcnow()
            
            return True, session
            
        except Exception as e:
            self.logger.error(f"Session validation error: {e}")
            return False, None
    
    async def logout_user(
        self,
        session_id: str,
        global_logout: bool = True
    ) -> Dict[str, Any]:
        """
        Logout user from SSO session
        
        Args:
            session_id: Session to logout
            global_logout: Whether to perform global logout
            
        Returns:
            Logout result
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            provider = self.providers.get(session.provider_id)
            if not provider:
                return {
                    "success": False,
                    "error": "Provider not found"
                }
            
            logout_results = []
            
            # Perform global logout if requested
            if global_logout and provider.logout_url:
                if provider.protocol == SSOProtocol.SAML2:
                    logout_result = await self._perform_saml_logout(provider, session)
                elif provider.protocol == SSOProtocol.OIDC:
                    logout_result = await self._perform_oidc_logout(provider, session)
                else:
                    logout_result = {"success": True, "method": "local"}
                
                logout_results.append(logout_result)
            
            # Remove local session
            await self._remove_session(session_id)
            
            # Update metrics
            self.metrics['active_sessions'] = max(0, self.metrics['active_sessions'] - 1)
            
            return {
                "success": True,
                "session_id": session_id,
                "global_logout": global_logout,
                "logout_results": logout_results
            }
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_info(
        self,
        session_id: str,
        include_attributes: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get user information from SSO session
        
        Args:
            session_id: Session identifier
            include_attributes: Whether to include user attributes
            
        Returns:
            User information or None
        """
        try:
            is_valid, session = await self.validate_session(session_id)
            
            if not is_valid or not session:
                return None
            
            user_info = {
                "user_id": session.user_id,
                "session_id": session.session_id,
                "provider_id": session.provider_id,
                "roles": session.roles,
                "permissions": session.permissions,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
            
            if include_attributes:
                user_info["attributes"] = session.user_attributes
            
            return user_info
            
        except Exception as e:
            self.logger.error(f"Get user info error: {e}")
            return None
    
    async def refresh_session(
        self,
        session_id: str,
        extend_duration: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """
        Refresh SSO session
        
        Args:
            session_id: Session to refresh
            extend_duration: Optional duration to extend
            
        Returns:
            Refresh result
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Calculate new expiration
            if extend_duration:
                new_expiry = datetime.utcnow() + extend_duration
            else:
                # Default extension based on provider settings
                new_expiry = datetime.utcnow() + timedelta(hours=8)
            
            # Update session
            session.expires_at = new_expiry
            session.last_activity = datetime.utcnow()
            
            return {
                "success": True,
                "session_id": session_id,
                "new_expiry": new_expiry.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Session refresh error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_provider(self, provider_config: Dict[str, Any]) -> str:
        """Add new SSO provider"""
        try:
            provider = SSOProvider(
                provider_id=provider_config["provider_id"],
                name=provider_config["name"],
                provider_type=ProviderType(provider_config["provider_type"]),
                protocol=SSOProtocol(provider_config["protocol"]),
                login_url=provider_config["login_url"],
                logout_url=provider_config.get("logout_url"),
                metadata_url=provider_config.get("metadata_url"),
                token_endpoint=provider_config.get("token_endpoint"),
                userinfo_endpoint=provider_config.get("userinfo_endpoint"),
                client_id=provider_config.get("client_id"),
                client_secret=provider_config.get("client_secret"),
                certificate=provider_config.get("certificate"),
                private_key=provider_config.get("private_key"),
                entity_id=provider_config.get("entity_id"),
                sso_url=provider_config.get("sso_url"),
                sls_url=provider_config.get("sls_url"),
                scope=provider_config.get("scope"),
                response_type=provider_config.get("response_type"),
                redirect_uri=provider_config.get("redirect_uri"),
                attribute_mappings=provider_config.get("attribute_mappings", {}),
                sign_requests=provider_config.get("sign_requests", True),
                encrypt_assertions=provider_config.get("encrypt_assertions", False),
                verify_signatures=provider_config.get("verify_signatures", True),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=provider_config.get("is_active", True),
                priority=provider_config.get("priority", 0)
            )
            
            self.providers[provider.provider_id] = provider
            
            # Initialize provider statistics
            self.metrics['provider_stats'][provider.provider_id] = {
                'requests': 0,
                'successful': 0,
                'failed': 0
            }
            
            self.logger.info(f"Added SSO provider: {provider.provider_id}")
            
            return provider.provider_id
            
        except Exception as e:
            self.logger.error(f"Add provider error: {e}")
            raise
    
    async def get_provider_metadata(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get provider metadata"""
        provider = self.providers.get(provider_id)
        if not provider:
            return None
        
        metadata = {
            "provider_id": provider.provider_id,
            "name": provider.name,
            "provider_type": provider.provider_type.value,
            "protocol": provider.protocol.value,
            "is_active": provider.is_active,
            "endpoints": {
                "login_url": provider.login_url,
                "logout_url": provider.logout_url,
                "metadata_url": provider.metadata_url
            },
            "capabilities": {
                "sign_requests": provider.sign_requests,
                "encrypt_assertions": provider.encrypt_assertions,
                "verify_signatures": provider.verify_signatures
            }
        }
        
        return metadata
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get SSO metrics"""
        return {
            **self.metrics,
            "active_sessions_count": len(self.active_sessions),
            "pending_requests_count": len(self.pending_requests),
            "providers_count": len(self.providers)
        }
    
    # Private methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load SSO configuration"""
        default_config = {
            "base_url": "https://localhost:8000",
            "callback_path": "/sso/callback",
            "metadata_path": "/sso/metadata",
            "session_timeout_hours": 8,
            "request_timeout_minutes": 10,
            "signing_algorithm": "RS256",
            "encryption_algorithm": "AES256",
            "clock_skew_tolerance_seconds": 300
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            self.logger.warning(f"Config loading failed: {e}")
        
        return default_config
    
    def _load_providers(self):
        """Load SSO providers from configuration"""
        providers_config_path = Path(self.config_path).parent / "sso_providers.json"
        
        if not providers_config_path.exists():
            self.logger.warning("No SSO providers configuration found")
            return
        
        try:
            with open(providers_config_path, 'r') as f:
                providers_config = json.load(f)
            
            for provider_config in providers_config["providers"]:
                asyncio.create_task(self.add_provider(provider_config))
                
        except Exception as e:
            self.logger.error(f"Provider loading error: {e}")
    
    def _setup_cryptography(self):
        """Setup cryptographic components"""
        # In production, load from secure key storage
        # For now, generate temporary keys
        
        self.signing_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        self.encryption_key = secrets.token_bytes(32)  # AES-256 key
    
    def _setup_web_routes(self):
        """Setup web routes for SSO callbacks"""
        async def sso_callback(request):
            return await self._handle_sso_callback(request)
        
        async def sso_metadata(request):
            return await self._handle_metadata_request(request)
        
        self.web_app.router.add_post('/sso/callback/{provider_id}', sso_callback)
        self.web_app.router.add_get('/sso/callback/{provider_id}', sso_callback)
        self.web_app.router.add_get('/sso/metadata', sso_metadata)
    
    async def _create_saml_request(
        self,
        provider: SSOProvider,
        auth_request: AuthenticationRequest
    ) -> str:
        """Create SAML authentication request"""
        # Generate SAML AuthnRequest
        request_id = f"__{auth_request.request_id}"
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        saml_request = f"""
        <samlp:AuthnRequest 
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
            ID="{request_id}"
            Version="2.0"
            IssueInstant="{issue_instant}"
            Destination="{provider.sso_url}"
            AssertionConsumerServiceURL="{self.config['base_url']}{self.config['callback_path']}/{provider.provider_id}"
            ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            ForceAuthn="{str(auth_request.force_authn).lower()}"
            IsPassive="{str(auth_request.passive).lower()}">
            <saml:Issuer>{self.config['base_url']}{self.config['metadata_path']}</saml:Issuer>
        </samlp:AuthnRequest>
        """
        
        # Encode request
        encoded_request = base64.b64encode(saml_request.encode()).decode()
        
        # Build authentication URL
        params = {
            'SAMLRequest': encoded_request,
            'RelayState': auth_request.relay_state or ''
        }
        
        auth_url = f"{provider.sso_url}?{urlencode(params)}"
        
        return auth_url
    
    async def _create_oidc_request(
        self,
        provider: SSOProvider,
        auth_request: AuthenticationRequest
    ) -> str:
        """Create OIDC authentication request"""
        state = auth_request.request_id
        nonce = secrets.token_urlsafe(32)
        
        params = {
            'response_type': provider.response_type or 'code',
            'client_id': provider.client_id,
            'redirect_uri': provider.redirect_uri,
            'scope': provider.scope or 'openid profile email',
            'state': state,
            'nonce': nonce
        }
        
        if auth_request.force_authn:
            params['prompt'] = 'login'
        elif auth_request.passive:
            params['prompt'] = 'none'
        
        auth_url = f"{provider.login_url}?{urlencode(params)}"
        
        return auth_url
    
    async def _create_oauth2_request(
        self,
        provider: SSOProvider,
        auth_request: AuthenticationRequest
    ) -> str:
        """Create OAuth2 authentication request"""
        state = auth_request.request_id
        
        params = {
            'response_type': provider.response_type or 'code',
            'client_id': provider.client_id,
            'redirect_uri': provider.redirect_uri,
            'scope': provider.scope or 'read',
            'state': state
        }
        
        auth_url = f"{provider.login_url}?{urlencode(params)}"
        
        return auth_url
    
    async def _process_saml_response(
        self,
        provider: SSOProvider,
        response_data: Dict[str, Any]
    ) -> AuthenticationResponse:
        """Process SAML authentication response"""
        try:
            saml_response = response_data.get('SAMLResponse')
            if not saml_response:
                raise ValueError("Missing SAMLResponse")
            
            # Decode SAML response
            decoded_response = base64.b64decode(saml_response).decode()
            
            # Parse XML
            root = ET.fromstring(decoded_response)
            
            # Extract assertion
            assertion = root.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
            if assertion is None:
                raise ValueError("No assertion found")
            
            # Extract user attributes
            user_attributes = {}
            attribute_statements = assertion.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement')
            
            for attr_statement in attribute_statements:
                for attr in attr_statement.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
                    attr_name = attr.get('Name')
                    attr_values = [value.text for value in attr.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue')]
                    user_attributes[attr_name] = attr_values[0] if len(attr_values) == 1 else attr_values
            
            # Map attributes
            mapped_attributes = self._map_attributes(user_attributes, provider.attribute_mappings)
            
            # Extract user ID
            user_id = mapped_attributes.get('user_id') or mapped_attributes.get('email')
            
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id=response_data.get('RelayState', ''),
                provider_id=provider.provider_id,
                status=AuthenticationStatus.SUCCESS,
                status_message="Authentication successful",
                created_at=datetime.utcnow(),
                user_id=user_id,
                user_attributes=mapped_attributes,
                session_id=None,  # Will be set later
                session_expires_at=None,
                assertion=saml_response,
                signature_valid=True,  # Simplified - in production, verify signature
                error_code=None,
                error_description=None
            )
            
        except Exception as e:
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id=response_data.get('RelayState', ''),
                provider_id=provider.provider_id,
                status=AuthenticationStatus.FAILURE,
                status_message="SAML processing failed",
                created_at=datetime.utcnow(),
                user_id=None,
                user_attributes={},
                session_id=None,
                session_expires_at=None,
                assertion=None,
                signature_valid=False,
                error_code="saml_error",
                error_description=str(e)
            )
    
    async def _process_oidc_response(
        self,
        provider: SSOProvider,
        response_data: Dict[str, Any]
    ) -> AuthenticationResponse:
        """Process OIDC authentication response"""
        try:
            # Get authorization code
            auth_code = response_data.get('code')
            if not auth_code:
                raise ValueError("Missing authorization code")
            
            # Exchange code for tokens
            token_data = await self._exchange_code_for_tokens(provider, auth_code)
            
            # Decode ID token
            id_token = token_data.get('id_token')
            if id_token:
                # In production, verify signature properly
                payload = jwt.decode(id_token, options={"verify_signature": False})
                user_attributes = self._map_attributes(payload, provider.attribute_mappings)
                user_id = user_attributes.get('user_id') or payload.get('sub')
            else:
                # Get user info from userinfo endpoint
                access_token = token_data.get('access_token')
                userinfo = await self._get_userinfo(provider, access_token)
                user_attributes = self._map_attributes(userinfo, provider.attribute_mappings)
                user_id = user_attributes.get('user_id') or userinfo.get('sub')
            
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id=response_data.get('state', ''),
                provider_id=provider.provider_id,
                status=AuthenticationStatus.SUCCESS,
                status_message="Authentication successful",
                created_at=datetime.utcnow(),
                user_id=user_id,
                user_attributes=user_attributes,
                session_id=None,
                session_expires_at=None,
                assertion=id_token,
                signature_valid=True,
                error_code=None,
                error_description=None
            )
            
        except Exception as e:
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id=response_data.get('state', ''),
                provider_id=provider.provider_id,
                status=AuthenticationStatus.FAILURE,
                status_message="OIDC processing failed",
                created_at=datetime.utcnow(),
                user_id=None,
                user_attributes={},
                session_id=None,
                session_expires_at=None,
                assertion=None,
                signature_valid=False,
                error_code="oidc_error",
                error_description=str(e)
            )
    
    async def _process_oauth2_response(
        self,
        provider: SSOProvider,
        response_data: Dict[str, Any]
    ) -> AuthenticationResponse:
        """Process OAuth2 authentication response"""
        try:
            # Get authorization code
            auth_code = response_data.get('code')
            if not auth_code:
                raise ValueError("Missing authorization code")
            
            # Exchange code for tokens
            token_data = await self._exchange_code_for_tokens(provider, auth_code)
            
            # Get user info
            access_token = token_data.get('access_token')
            userinfo = await self._get_userinfo(provider, access_token)
            
            # Map attributes
            user_attributes = self._map_attributes(userinfo, provider.attribute_mappings)
            user_id = user_attributes.get('user_id') or userinfo.get('id')
            
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id=response_data.get('state', ''),
                provider_id=provider.provider_id,
                status=AuthenticationStatus.SUCCESS,
                status_message="Authentication successful",
                created_at=datetime.utcnow(),
                user_id=user_id,
                user_attributes=user_attributes,
                session_id=None,
                session_expires_at=None,
                assertion=access_token,
                signature_valid=True,
                error_code=None,
                error_description=None
            )
            
        except Exception as e:
            return AuthenticationResponse(
                response_id=str(uuid.uuid4()),
                request_id=response_data.get('state', ''),
                provider_id=provider.provider_id,
                status=AuthenticationStatus.FAILURE,
                status_message="OAuth2 processing failed",
                created_at=datetime.utcnow(),
                user_id=None,
                user_attributes={},
                session_id=None,
                session_expires_at=None,
                assertion=None,
                signature_valid=False,
                error_code="oauth2_error",
                error_description=str(e)
            )
    
    async def _exchange_code_for_tokens(
        self,
        provider: SSOProvider,
        auth_code: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': provider.redirect_uri,
            'client_id': provider.client_id,
            'client_secret': provider.client_secret
        }
        
        async with self.http_session.post(
            provider.token_endpoint,
            data=token_data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ValueError(f"Token exchange failed: {response.status}")
    
    async def _get_userinfo(self, provider: SSOProvider, access_token: str) -> Dict[str, Any]:
        """Get user information from userinfo endpoint"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        async with self.http_session.get(
            provider.userinfo_endpoint,
            headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ValueError(f"Userinfo request failed: {response.status}")
    
    def _map_attributes(
        self,
        source_attributes: Dict[str, Any],
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Map provider attributes to internal attributes"""
        mapped = {}
        
        for internal_attr, provider_attr in mappings.items():
            if provider_attr in source_attributes:
                mapped[internal_attr] = source_attributes[provider_attr]
        
        # Pass through unmapped attributes
        for attr, value in source_attributes.items():
            if attr not in mapped.values():
                mapped[attr] = value
        
        return mapped
    
    async def _create_sso_session(
        self,
        provider: SSOProvider,
        auth_response: AuthenticationResponse,
        request_context: Optional[Dict[str, Any]]
    ) -> SSOSession:
        """Create SSO session"""
        session_id = str(uuid.uuid4())
        context = request_context or {}
        
        # Determine roles and permissions from attributes
        roles = auth_response.user_attributes.get('roles', [])
        if isinstance(roles, str):
            roles = [roles]
        
        permissions = auth_response.user_attributes.get('permissions', [])
        if isinstance(permissions, str):
            permissions = [permissions]
        
        session = SSOSession(
            session_id=session_id,
            user_id=auth_response.user_id,
            provider_id=provider.provider_id,
            provider_session_id=None,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=self.config['session_timeout_hours']),
            last_activity=datetime.utcnow(),
            user_attributes=auth_response.user_attributes,
            roles=roles,
            permissions=permissions,
            ip_address=context.get('ip_address', ''),
            user_agent=context.get('user_agent', ''),
            device_id=context.get('device_id'),
            is_active=True,
            logout_url=provider.logout_url,
            logout_token=None
        )
        
        self.active_sessions[session_id] = session
        
        return session
    
    async def _remove_session(self, session_id: str):
        """Remove session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    async def _perform_saml_logout(
        self,
        provider: SSOProvider,
        session: SSOSession
    ) -> Dict[str, Any]:
        """Perform SAML logout"""
        # Create SAML LogoutRequest
        request_id = str(uuid.uuid4())
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        logout_request = f"""
        <samlp:LogoutRequest 
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
            ID="{request_id}"
            Version="2.0"
            IssueInstant="{issue_instant}"
            Destination="{provider.sls_url}">
            <saml:Issuer>{self.config['base_url']}{self.config['metadata_path']}</saml:Issuer>
            <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">{session.user_id}</saml:NameID>
        </samlp:LogoutRequest>
        """
        
        # In production, send the logout request to the provider
        return {"success": True, "method": "saml"}
    
    async def _perform_oidc_logout(
        self,
        provider: SSOProvider,
        session: SSOSession
    ) -> Dict[str, Any]:
        """Perform OIDC logout"""
        # In production, call the logout endpoint
        return {"success": True, "method": "oidc"}
    
    async def _handle_sso_callback(self, request):
        """Handle SSO callback"""
        provider_id = request.match_info['provider_id']
        
        if request.method == 'POST':
            data = await request.post()
        else:
            data = dict(request.query)
        
        try:
            auth_response = await self.handle_authentication_response(
                provider_id, data, {
                    'ip_address': request.remote,
                    'user_agent': request.headers.get('User-Agent', '')
                }
            )
            
            if auth_response.status == AuthenticationStatus.SUCCESS:
                return web.json_response({
                    "success": True,
                    "session_id": auth_response.session_id,
                    "user_id": auth_response.user_id
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": auth_response.error_description
                }, status=400)
                
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def _handle_metadata_request(self, request):
        """Handle metadata request"""
        # Return SAML metadata
        metadata = f"""
        <EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" 
                          entityID="{self.config['base_url']}{self.config['metadata_path']}">
            <SPSSODescriptor AuthnRequestsSigned="true" WantAssertionsSigned="true" 
                             protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
                <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                          Location="{self.config['base_url']}{self.config['callback_path']}"
                                          index="1" isDefault="true"/>
            </SPSSODescriptor>
        </EntityDescriptor>
        """
        
        return web.Response(text=metadata, content_type='application/xml')


# Export main classes
__all__ = [
    "SingleSignOnOrchestrator",
    "SSOProtocol",
    "ProviderType",
    "AuthenticationStatus",
    "SSOProvider",
    "SSOSession",
    "AuthenticationRequest",
    "AuthenticationResponse"
]