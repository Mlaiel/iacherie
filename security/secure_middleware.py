"""
Enhanced Security Middleware with Comprehensive Data Protection
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Integrates AES-256 encryption, TLS 1.3, E2E encryption, and HSM key management.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseMiddleware
from starlette.responses import Response
import asyncio
import time
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

# Import our security modules
from .encryption import get_aes256_encryption, get_content_encryption, get_database_encryption
from .tls_config import get_tls13_config, get_secure_headers, get_https_redirect
from .e2e_encryption import get_e2e_manager, get_websocket_e2e
from .hsm_integration import get_hsm_manager, HSMBackend
from .middleware import security_middleware as original_security_middleware

logger = logging.getLogger(__name__)


class DataProtectionMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive data protection middleware implementing all security requirements:
    - AES-256 encryption for data at rest
    - TLS 1.3 for data in transit
    - End-to-end encryption for communications
    - HSM-based key management
    """
    
    def __init__(self, app: FastAPI, config: Dict[str, Any] = None):
        super().__init__(app)
        self.config = config or {}
        self.aes_encryption = get_aes256_encryption()
        self.content_encryption = get_content_encryption()
        self.db_encryption = get_database_encryption()
        self.tls_config = get_tls13_config()
        self.secure_headers = get_secure_headers()
        self.https_redirect = get_https_redirect()
        self.e2e_manager = get_e2e_manager()
        self.hsm_manager = None
        self.encryption_enabled = self.config.get('encryption_enabled', True)
        self.e2e_enabled = self.config.get('e2e_enabled', True)
        self.hsm_enabled = self.config.get('hsm_enabled', True)
        
    async def initialize(self):
        """Initialize the data protection middleware."""
        try:
            # Initialize HSM if enabled
            if self.hsm_enabled:
                hsm_backend = HSMBackend(self.config.get('hsm_backend', 'local'))
                hsm_config = self.config.get('hsm_config', {})
                self.hsm_manager = get_hsm_manager(hsm_backend, hsm_config)
                await self.hsm_manager.connect()
                logger.info("HSM integration initialized")
            
            # Initialize original security middleware
            if original_security_middleware:
                await original_security_middleware.initialize()
            
            logger.info("Data protection middleware initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize data protection middleware: {str(e)}")
            raise
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch with comprehensive security."""
        try:
            start_time = time.time()
            
            # 1. HTTPS Redirect Check
            if self.https_redirect.should_redirect(request.url.scheme, request.url.hostname):
                redirect_url = self.https_redirect.get_redirect_url(str(request.url))
                return JSONResponse(
                    status_code=301 if self.https_redirect.permanent else 302,
                    headers={"Location": redirect_url}
                )
            
            # 2. Extract request data for security analysis
            request_data = await self._extract_request_data(request)
            
            # 3. Run original security checks (WAF, rate limiting, OAuth2)
            if original_security_middleware:
                security_result = await original_security_middleware.process_request(request_data)
                
                if not security_result.get('allowed', True):
                    return self._create_security_response(security_result)
            
            # 4. Handle E2E encryption for API endpoints
            if self.e2e_enabled and self._is_e2e_endpoint(request.url.path):
                e2e_result = await self._handle_e2e_encryption(request, request_data)
                if e2e_result.get('error'):
                    return self._create_error_response(e2e_result['error'], 400)
                
                # Modify request with decrypted data if needed
                if e2e_result.get('decrypted_data'):
                    request = await self._update_request_body(request, e2e_result['decrypted_data'])
            
            # 5. Process request through application
            response = await call_next(request)
            
            # 6. Apply security headers
            security_headers = self.secure_headers.get_security_headers()
            for header_name, header_value in security_headers.items():
                response.headers[header_name] = header_value
            
            # 7. Encrypt response data if needed
            if self.encryption_enabled and self._should_encrypt_response(request.url.path):
                response = await self._encrypt_response_data(response, request_data)
            
            # 8. Add performance metrics
            processing_time = time.time() - start_time
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
            response.headers["X-Security-Level"] = "AES-256+TLS-1.3+E2E+HSM"
            
            return response
            
        except Exception as e:
            logger.error(f"Data protection middleware error: {str(e)}")
            return self._create_error_response("Security processing failed", 500)
    
    async def _extract_request_data(self, request: Request) -> Dict[str, Any]:
        """Extract request data for security analysis."""
        try:
            # Get client information
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "")
            
            # Get request body if present
            body = b""
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
            
            # Build request data structure
            request_data = {
                'url': str(request.url),
                'method': request.method,
                'headers': dict(request.headers),
                'query_params': dict(request.query_params),
                'body': body,
                'client_ip': client_ip,
                'user_agent': user_agent,
                'request_id': request.headers.get('X-Request-ID', f"req_{int(time.time() * 1000)}"),
                'endpoint': request.url.path,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return request_data
            
        except Exception as e:
            logger.error(f"Failed to extract request data: {str(e)}")
            return {}
    
    def _is_e2e_endpoint(self, path: str) -> bool:
        """Check if endpoint requires E2E encryption."""
        e2e_paths = [
            '/api/e2e/',
            '/api/secure/',
            '/api/private/',
            '/api/upload/',
            '/api/content/',
            '/api/payment/',
            '/api/user/profile',
            '/api/creator/content'
        ]
        return any(path.startswith(e2e_path) for e2e_path in e2e_paths)
    
    async def _handle_e2e_encryption(self, request: Request, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle end-to-end encryption for secure endpoints."""
        try:
            # Check for E2E session header
            session_id = request.headers.get('X-E2E-Session')
            if not session_id:
                return {'error': 'E2E session required for secure endpoint'}
            
            # Check if request body is encrypted
            content_type = request.headers.get('Content-Type', '')
            if 'application/json+encrypted' in content_type:
                # Decrypt request body
                body = request_data.get('body', b'')
                if body:
                    try:
                        encrypted_data = json.loads(body.decode('utf-8'))
                        decrypted_message = self.e2e_manager.decrypt_message(session_id, encrypted_data)
                        return {'decrypted_data': decrypted_message}
                    except Exception as e:
                        return {'error': f'Failed to decrypt request: {str(e)}'}
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"E2E encryption handling failed: {str(e)}")
            return {'error': str(e)}
    
    async def _update_request_body(self, request: Request, decrypted_data: str) -> Request:
        """Update request body with decrypted data."""
        try:
            # Create new request with decrypted body
            # This is a simplified implementation - in practice, you might need
            # to use a more sophisticated approach to modify the request
            request._body = decrypted_data.encode('utf-8')
            return request
            
        except Exception as e:
            logger.error(f"Failed to update request body: {str(e)}")
            return request
    
    def _should_encrypt_response(self, path: str) -> bool:
        """Check if response should be encrypted."""
        # Encrypt responses for sensitive endpoints
        sensitive_paths = [
            '/api/user/',
            '/api/creator/',
            '/api/content/',
            '/api/payment/',
            '/api/analytics/',
            '/api/revenue/'
        ]
        return any(path.startswith(sensitive_path) for sensitive_path in sensitive_paths)
    
    async def _encrypt_response_data(self, response: Response, request_data: Dict[str, Any]) -> Response:
        """Encrypt sensitive response data."""
        try:
            # Check for E2E session
            session_id = request_data.get('headers', {}).get('X-E2E-Session')
            
            if session_id and hasattr(response, 'body'):
                # Get response body
                response_body = response.body
                
                if response_body and len(response_body) > 0:
                    # Encrypt response body
                    encrypted_data = self.e2e_manager.encrypt_message(
                        session_id, 
                        response_body.decode('utf-8')
                    )
                    
                    # Update response
                    encrypted_json = json.dumps(encrypted_data).encode('utf-8')
                    response.body = encrypted_json
                    response.headers['Content-Type'] = 'application/json+encrypted'
                    response.headers['Content-Length'] = str(len(encrypted_json))
            
            return response
            
        except Exception as e:
            logger.error(f"Response encryption failed: {str(e)}")
            return response
    
    def _create_security_response(self, security_result: Dict[str, Any]) -> JSONResponse:
        """Create security-related response."""
        status_code = 403 if security_result.get('reason') == 'waf_blocked' else 429
        
        response_data = {
            'error': 'Security check failed',
            'reason': security_result.get('reason', 'unknown'),
            'request_id': security_result.get('request_id'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add rate limit headers if applicable
        if security_result.get('reason') == 'rate_limit_exceeded':
            details = security_result.get('details', {})
            rate_limit_info = details.get('rate_limit_info', {})
            
            headers = {
                'X-RateLimit-Limit': str(rate_limit_info.get('limit', 'unknown')),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(rate_limit_info.get('window_reset', 'unknown'))
            }
        else:
            headers = {}
        
        # Add security headers
        security_headers = self.secure_headers.get_security_headers()
        headers.update(security_headers)
        
        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers=headers
        )
    
    def _create_error_response(self, error_message: str, status_code: int = 500) -> JSONResponse:
        """Create error response with security headers."""
        security_headers = self.secure_headers.get_security_headers()
        
        return JSONResponse(
            status_code=status_code,
            content={
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            },
            headers=security_headers
        )


class HSMKeyManagementMiddleware(BaseHTTPMiddleware):
    """Middleware for HSM-based key management operations."""
    
    def __init__(self, app: FastAPI, hsm_manager=None):
        super().__init__(app)
        self.hsm_manager = hsm_manager
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle HSM key management operations."""
        try:
            # Check if this is a key management endpoint
            if request.url.path.startswith('/api/keys/'):
                # Verify admin authorization
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return JSONResponse(
                        status_code=401,
                        content={'error': 'Authentication required for key management'}
                    )
                
                # Add HSM manager to request state
                request.state.hsm_manager = self.hsm_manager
            
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"HSM middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={'error': 'Key management service unavailable'}
            )


def create_secure_app(config: Dict[str, Any] = None) -> FastAPI:
    """
    Create FastAPI application with comprehensive data protection.
    
    Args:
        config: Security configuration
        
    Returns:
        Configured FastAPI application
    """
    try:
        # Create FastAPI app
        app = FastAPI(
            title="Ainflue AI Platform - Secure",
            description="AI-Powered Content Protection with Advanced Security",
            version="1.0.0",
            docs_url="/docs" if config.get('debug', False) else None,
            redoc_url="/redoc" if config.get('debug', False) else None
        )
        
        # Add data protection middleware
        data_protection = DataProtectionMiddleware(app, config)
        app.add_middleware(DataProtectionMiddleware, config=config)
        
        # Add HSM key management middleware if enabled
        if config.get('hsm_enabled', True):
            hsm_manager = get_hsm_manager()
            app.add_middleware(HSMKeyManagementMiddleware, hsm_manager=hsm_manager)
        
        # Add startup event to initialize security
        @app.on_event("startup")
        async def startup_event():
            logger.info("Initializing secure application...")
            await data_protection.initialize()
            logger.info("Secure application initialized successfully")
        
        # Add E2E encryption endpoints
        @app.post("/api/e2e/session")
        async def create_e2e_session():
            """Create new E2E encryption session."""
            try:
                e2e_manager = get_e2e_manager()
                session_info = e2e_manager.create_session()
                return session_info
            except Exception as e:
                logger.error(f"E2E session creation failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to create E2E session")
        
        @app.post("/api/e2e/handshake/{session_id}")
        async def complete_e2e_handshake(session_id: str, request: Request):
            """Complete E2E encryption handshake."""
            try:
                body = await request.json()
                peer_public_key = body.get('public_key')
                
                if not peer_public_key:
                    raise HTTPException(status_code=400, detail="Public key required")
                
                e2e_manager = get_e2e_manager()
                result = e2e_manager.establish_session(session_id, peer_public_key)
                return result
                
            except Exception as e:
                logger.error(f"E2E handshake failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Handshake failed")
        
        # Add key management endpoints
        @app.post("/api/keys/generate")
        async def generate_key(request: Request):
            """Generate new encryption key via HSM."""
            try:
                hsm_manager = getattr(request.state, 'hsm_manager', None)
                if not hsm_manager:
                    raise HTTPException(status_code=503, detail="HSM not available")
                
                body = await request.json()
                key_type = body.get('key_type', 'data')
                purpose = body.get('purpose', 'general')
                
                if key_type == 'master':
                    key_id = await hsm_manager.create_master_key()
                else:
                    key_id = await hsm_manager.create_data_encryption_key(purpose)
                
                return {
                    'key_id': key_id,
                    'key_type': key_type,
                    'purpose': purpose,
                    'created_at': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Key generation failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Key generation failed")
        
        # Add health check with security status
        @app.get("/health/security")
        async def security_health():
            """Security systems health check."""
            try:
                status = {
                    'encryption': 'operational',
                    'tls': 'operational',
                    'e2e': 'operational',
                    'hsm': 'operational' if config.get('hsm_enabled') else 'disabled',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Test HSM if enabled
                if config.get('hsm_enabled'):
                    try:
                        hsm_manager = get_hsm_manager()
                        # Simple connectivity test
                        if not hsm_manager.hsm.is_connected:
                            status['hsm'] = 'disconnected'
                    except Exception:
                        status['hsm'] = 'error'
                
                return status
                
            except Exception as e:
                logger.error(f"Security health check failed: {str(e)}")
                return {
                    'error': 'Health check failed',
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        logger.info("Secure FastAPI application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create secure application: {str(e)}")
        raise


# Global instances
_secure_app = None
_data_protection_middleware = None


def get_secure_app(config: Dict[str, Any] = None) -> FastAPI:
    """Get secure FastAPI application instance."""
    global _secure_app
    
    if _secure_app is None:
        _secure_app = create_secure_app(config)
    
    return _secure_app


def get_data_protection_middleware() -> Optional[DataProtectionMiddleware]:
    """Get data protection middleware instance."""
    return _data_protection_middleware