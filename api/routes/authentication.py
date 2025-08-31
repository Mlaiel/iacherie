"""
Enterprise Authentication API Routes
Comprehensive authentication endpoints with MFA, OAuth2, SAML, and FIDO2 support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import secrets
import logging

# Import our authentication managers
try:
    from ..security.auth import (
        AuthenticationManager,
        AuthenticationMethod,
        AuthenticationStatus,
        UserCredentials,
        AuthenticationResult,
        AuthenticationError
    )
except ImportError:
    # Fallback import structure
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from security.auth import (
        AuthenticationManager,
        AuthenticationMethod,
        AuthenticationStatus,
        UserCredentials,
        AuthenticationResult,
        AuthenticationError
    )

logger = logging.getLogger(__name__)

# Initialize authentication manager
auth_manager = AuthenticationManager()

# Router setup
router = APIRouter(prefix="/auth", tags=["Authentication & Security"])
security = HTTPBearer()

# === Pydantic Models === #

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: Optional[str] = Field(None, description="Password (for password auth)")
    auth_methods: List[str] = Field(default=["password"], description="Authentication methods to use")
    remember_me: bool = Field(default=False, description="Create persistent session")
    
class LoginResponse(BaseModel):
    status: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    requires_mfa: bool = False
    mfa_methods: List[str] = []
    error_message: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class OAuth2AuthRequest(BaseModel):
    provider: str = Field(..., description="OAuth2 provider (google, facebook, apple, twitter, etc.)")
    redirect_uri: str = Field(..., description="Redirect URI after authentication")
    
class OAuth2CallbackRequest(BaseModel):
    provider: str = Field(..., description="OAuth2 provider")
    code: str = Field(..., description="Authorization code")
    state: str = Field(..., description="State parameter")
    redirect_uri: str = Field(..., description="Redirect URI")

class SAMLAuthRequest(BaseModel):
    enterprise_id: str = Field(..., description="Enterprise identifier")
    relay_state: Optional[str] = Field(None, description="RelayState parameter")

class SAMLCallbackRequest(BaseModel):
    enterprise_id: str = Field(..., description="Enterprise identifier")
    saml_response: str = Field(..., description="Base64 encoded SAML response")
    relay_state: Optional[str] = Field(None, description="RelayState parameter")

class FIDO2RegistrationRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    display_name: Optional[str] = Field(None, description="Display name")

class FIDO2RegistrationVerifyRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    credential_data: Dict[str, Any] = Field(..., description="WebAuthn credential data")

class FIDO2AuthRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID (optional for passwordless)")

class FIDO2AuthVerifyRequest(BaseModel):
    credential_data: Dict[str, Any] = Field(..., description="WebAuthn assertion data")

class MFASetupRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    
class MFAVerifyRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    token: str = Field(..., description="TOTP token or backup code")

class BiometricRegisterRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    biometric_type: str = Field(..., description="Type: face, fingerprint, voice")
    biometric_data: str = Field(..., description="Base64 encoded biometric data")

class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    permissions: List[str] = []
    expires_at: Optional[datetime] = None
    token_type: Optional[str] = None

# === Authentication Routes === #

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request, background_tasks: BackgroundTasks):
    """
    Comprehensive user authentication with multiple methods support
    Supports: Password, OAuth2, SAML, MFA, Biometric, FIDO2
    """
    try:
        # Convert string auth methods to enum
        auth_methods = []
        for method in request.auth_methods:
            try:
                auth_methods.append(AuthenticationMethod(method.lower()))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported authentication method: {method}"
                )
        
        # Create credentials object
        credentials = UserCredentials(
            username=request.username,
            password=request.password
        )
        
        # Extract request metadata
        metadata = {
            'user_agent': req.headers.get('user-agent'),
            'ip_address': req.client.host if req.client else None,
            'remember_me': request.remember_me
        }
        
        # Authenticate user
        result = await auth_manager.authenticate_user(
            credentials=credentials,
            authentication_methods=auth_methods,
            metadata=metadata
        )
        
        if result.status == AuthenticationStatus.SUCCESS:
            return LoginResponse(
                status="success",
                access_token=result.metadata.get('access_token'),
                refresh_token=result.metadata.get('refresh_token'),
                session_id=result.metadata.get('session_id'),
                user_id=result.user_id,
                expires_at=result.expires_at
            )
        elif result.status == AuthenticationStatus.LOCKED:
            raise HTTPException(status_code=423, detail=result.error_message)
        else:
            raise HTTPException(status_code=401, detail=result.error_message)
            
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        result = await auth_manager.refresh_authentication(request.refresh_token)
        
        if result.status == AuthenticationStatus.SUCCESS:
            return LoginResponse(
                status="success",
                access_token=result.metadata.get('new_access_token'),
                user_id=result.user_id,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
        else:
            raise HTTPException(status_code=401, detail=result.error_message)
            
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session_id: Optional[str] = None,
    refresh_token: Optional[str] = None
):
    """Logout user and revoke tokens/sessions"""
    try:
        access_token = credentials.credentials if credentials else None
        
        success = await auth_manager.logout_user(
            session_id=session_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        if success:
            return {"status": "success", "message": "Logged out successfully"}
        else:
            return {"status": "warning", "message": "No active sessions found"}
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout service error")

@router.get("/validate")
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenValidationResponse:
    """Validate JWT access token"""
    try:
        result = await auth_manager.validate_token(credentials.credentials)
        
        return TokenValidationResponse(
            valid=result.status == AuthenticationStatus.SUCCESS,
            user_id=result.user_id,
            permissions=result.permissions or [],
            token_type="access"
        )
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return TokenValidationResponse(valid=False)

# === OAuth2 Routes === #

@router.post("/oauth2/authorize")
async def oauth2_authorize(request: OAuth2AuthRequest):
    """Initiate OAuth2 authentication flow"""
    try:
        auth_url = auth_manager.oauth2_manager.generate_auth_url(
            provider=request.provider,
            redirect_uri=request.redirect_uri
        )
        
        return {
            "status": "success",
            "auth_url": auth_url,
            "provider": request.provider
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"OAuth2 authorization error: {e}")
        raise HTTPException(status_code=500, detail="OAuth2 service error")

@router.post("/oauth2/callback", response_model=LoginResponse)
async def oauth2_callback(request: OAuth2CallbackRequest, req: Request):
    """Handle OAuth2 callback and complete authentication"""
    try:
        # Exchange code for token
        token_data = await auth_manager.oauth2_manager.exchange_code_for_token(
            provider=request.provider,
            code=request.code,
            redirect_uri=request.redirect_uri,
            state=request.state
        )
        
        # Get user info from provider
        user_info = await auth_manager.oauth2_manager.get_user_info(
            provider=request.provider,
            access_token=token_data['access_token']
        )
        
        # Create user session
        user_id = user_info['id']
        session_id = await auth_manager.session_manager.create_session(
            user_id=user_id,
            user_agent=req.headers.get('user-agent'),
            ip_address=req.client.host if req.client else None,
            metadata={'oauth2_provider': request.provider, 'user_info': user_info}
        )
        
        # Generate JWT tokens
        permissions = auth_manager._get_user_permissions(user_id)
        access_token, refresh_token = auth_manager.jwt_manager.generate_token(
            user_id=user_id,
            permissions=permissions
        )
        
        return LoginResponse(
            status="success",
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session_id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"OAuth2 callback error: {e}")
        raise HTTPException(status_code=500, detail="OAuth2 callback processing error")

# === SAML Routes === #

@router.post("/saml/authorize")
async def saml_authorize(request: SAMLAuthRequest):
    """Initiate SAML SSO authentication"""
    try:
        auth_url = auth_manager.saml_manager.generate_auth_request(
            enterprise_id=request.enterprise_id,
            relay_state=request.relay_state
        )
        
        return {
            "status": "success",
            "auth_url": auth_url,
            "enterprise_id": request.enterprise_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SAML authorization error: {e}")
        raise HTTPException(status_code=500, detail="SAML service error")

@router.post("/saml/acs", response_model=LoginResponse)
async def saml_acs(request: SAMLCallbackRequest, req: Request):
    """SAML Assertion Consumer Service - handle SAML response"""
    try:
        # Process SAML response
        user_data = await auth_manager.saml_manager.process_saml_response(
            enterprise_id=request.enterprise_id,
            saml_response=request.saml_response,
            relay_state=request.relay_state
        )
        
        # Create user session
        user_id = user_data['user_id']
        session_id = await auth_manager.session_manager.create_session(
            user_id=user_id,
            user_agent=req.headers.get('user-agent'),
            ip_address=req.client.host if req.client else None,
            metadata={'saml_enterprise': request.enterprise_id, 'user_data': user_data}
        )
        
        # Generate JWT tokens
        permissions = auth_manager._get_user_permissions(user_id)
        access_token, refresh_token = auth_manager.jwt_manager.generate_token(
            user_id=user_id,
            permissions=permissions
        )
        
        return LoginResponse(
            status="success",
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session_id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"SAML ACS error: {e}")
        raise HTTPException(status_code=500, detail="SAML response processing error")

@router.get("/saml/metadata")
async def saml_metadata():
    """Get SAML SP metadata"""
    try:
        metadata = auth_manager.saml_manager.generate_metadata()
        return Response(content=metadata, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"SAML metadata error: {e}")
        raise HTTPException(status_code=500, detail="SAML metadata generation error")

# === FIDO2/WebAuthn Routes === #

@router.post("/fido2/register/begin")
async def fido2_register_begin(request: FIDO2RegistrationRequest):
    """Begin FIDO2 credential registration"""
    try:
        options = auth_manager.fido2_manager.generate_registration_options(
            user_id=request.user_id,
            username=request.username,
            display_name=request.display_name
        )
        
        return {
            "status": "success",
            "options": options
        }
        
    except Exception as e:
        logger.error(f"FIDO2 registration begin error: {e}")
        raise HTTPException(status_code=500, detail="FIDO2 registration service error")

@router.post("/fido2/register/complete")
async def fido2_register_complete(request: FIDO2RegistrationVerifyRequest):
    """Complete FIDO2 credential registration"""
    try:
        success = auth_manager.fido2_manager.verify_registration(
            user_id=request.user_id,
            credential_data=request.credential_data
        )
        
        if success:
            return {"status": "success", "message": "FIDO2 credential registered successfully"}
        else:
            raise HTTPException(status_code=400, detail="FIDO2 registration verification failed")
            
    except Exception as e:
        logger.error(f"FIDO2 registration complete error: {e}")
        raise HTTPException(status_code=500, detail="FIDO2 registration verification error")

@router.post("/fido2/authenticate/begin")
async def fido2_auth_begin(request: FIDO2AuthRequest):
    """Begin FIDO2 authentication"""
    try:
        options = auth_manager.fido2_manager.generate_authentication_options(
            user_id=request.user_id
        )
        
        return {
            "status": "success",
            "options": options
        }
        
    except Exception as e:
        logger.error(f"FIDO2 authentication begin error: {e}")
        raise HTTPException(status_code=500, detail="FIDO2 authentication service error")

@router.post("/fido2/authenticate/complete", response_model=LoginResponse)
async def fido2_auth_complete(request: FIDO2AuthVerifyRequest, req: Request):
    """Complete FIDO2 authentication"""
    try:
        user_id = auth_manager.fido2_manager.verify_authentication(
            credential_data=request.credential_data
        )
        
        if not user_id:
            raise HTTPException(status_code=401, detail="FIDO2 authentication failed")
        
        # Create user session
        session_id = await auth_manager.session_manager.create_session(
            user_id=user_id,
            user_agent=req.headers.get('user-agent'),
            ip_address=req.client.host if req.client else None,
            metadata={'auth_method': 'fido2'}
        )
        
        # Generate JWT tokens
        permissions = auth_manager._get_user_permissions(user_id)
        access_token, refresh_token = auth_manager.jwt_manager.generate_token(
            user_id=user_id,
            permissions=permissions
        )
        
        return LoginResponse(
            status="success",
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session_id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
    except Exception as e:
        logger.error(f"FIDO2 authentication complete error: {e}")
        raise HTTPException(status_code=500, detail="FIDO2 authentication verification error")

@router.get("/fido2/credentials/{user_id}")
async def get_fido2_credentials(user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user's registered FIDO2 credentials"""
    try:
        # Validate token and check user permissions
        validation = await auth_manager.validate_token(credentials.credentials)
        if validation.status != AuthenticationStatus.SUCCESS:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        if validation.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        user_credentials = auth_manager.fido2_manager.get_user_credentials(user_id)
        
        return {
            "status": "success",
            "credentials": user_credentials
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get FIDO2 credentials error: {e}")
        raise HTTPException(status_code=500, detail="FIDO2 credentials service error")

# === Multi-Factor Authentication Routes === #

@router.post("/mfa/setup")
async def mfa_setup(request: MFASetupRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Setup Multi-Factor Authentication"""
    try:
        # Validate token
        validation = await auth_manager.validate_token(credentials.credentials)
        if validation.status != AuthenticationStatus.SUCCESS:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Generate TOTP secret
        secret = auth_manager.two_factor_manager.generate_secret_key(request.user_id)
        
        # Generate QR code
        qr_code = auth_manager.two_factor_manager.generate_qr_code(
            user_id=request.user_id,
            user_email=f"{request.user_id}@ainflue.ai",  # In production: get from database
            secret=secret
        )
        
        # Generate backup codes
        backup_codes = auth_manager.two_factor_manager.generate_backup_codes(request.user_id)
        
        import base64
        return {
            "status": "success",
            "secret": secret,
            "qr_code": base64.b64encode(qr_code).decode(),
            "backup_codes": backup_codes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA setup error: {e}")
        raise HTTPException(status_code=500, detail="MFA setup service error")

@router.post("/mfa/verify")
async def mfa_verify(request: MFAVerifyRequest):
    """Verify MFA token or backup code"""
    try:
        # Try TOTP token first
        if auth_manager.two_factor_manager.verify_totp_token(request.user_id, request.token):
            return {"status": "success", "method": "totp"}
        
        # Try backup code
        if auth_manager.two_factor_manager.verify_backup_code(request.user_id, request.token):
            return {"status": "success", "method": "backup_code"}
        
        raise HTTPException(status_code=401, detail="Invalid MFA token")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verification error: {e}")
        raise HTTPException(status_code=500, detail="MFA verification service error")

# === Biometric Authentication Routes === #

@router.post("/biometric/register")
async def biometric_register(request: BiometricRegisterRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Register biometric data for authentication"""
    try:
        # Validate token
        validation = await auth_manager.validate_token(credentials.credentials)
        if validation.status != AuthenticationStatus.SUCCESS:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        import base64
        import numpy as np
        
        # Decode biometric data
        biometric_data = base64.b64decode(request.biometric_data)
        
        success = False
        if request.biometric_type == "face":
            # Convert to numpy array (simplified)
            image_array = np.frombuffer(biometric_data, dtype=np.uint8)
            success = auth_manager.biometric_manager.register_face(request.user_id, image_array)
        elif request.biometric_type == "fingerprint":
            success = auth_manager.biometric_manager.register_fingerprint(request.user_id, biometric_data)
        elif request.biometric_type == "voice":
            voice_array = np.frombuffer(biometric_data, dtype=np.float32)
            success = auth_manager.biometric_manager.register_voice_print(request.user_id, voice_array)
        else:
            raise HTTPException(status_code=400, detail="Unsupported biometric type")
        
        if success:
            return {"status": "success", "message": f"{request.biometric_type} biometric registered"}
        else:
            raise HTTPException(status_code=400, detail="Biometric registration failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Biometric registration error: {e}")
        raise HTTPException(status_code=500, detail="Biometric registration service error")

# === Enterprise Configuration Routes === #

@router.post("/enterprise/saml/configure")
async def configure_enterprise_saml(
    enterprise_id: str,
    idp_config: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Configure SAML IdP for enterprise"""
    try:
        # Validate admin token
        validation = await auth_manager.validate_token(credentials.credentials)
        if validation.status != AuthenticationStatus.SUCCESS:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check admin permissions (simplified)
        if 'admin' not in validation.permissions:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        auth_manager.saml_manager.configure_enterprise_idp(enterprise_id, idp_config)
        
        return {
            "status": "success",
            "message": f"SAML IdP configured for enterprise: {enterprise_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enterprise SAML configuration error: {e}")
        raise HTTPException(status_code=500, detail="Enterprise SAML configuration error")

# === Security Status Routes === #

@router.get("/security/status")
async def security_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get security status and configuration"""
    try:
        validation = await auth_manager.validate_token(credentials.credentials)
        if validation.status != AuthenticationStatus.SUCCESS:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "status": "operational",
            "supported_auth_methods": [method.value for method in AuthenticationMethod],
            "oauth2_providers": list(auth_manager.oauth2_manager.providers.keys()),
            "security_features": {
                "mfa_enabled": True,
                "biometric_enabled": True,
                "fido2_enabled": True,
                "saml_enabled": True,
                "session_management": True,
                "jwt_refresh": True
            },
            "session_timeout": auth_manager.session_manager.session_timeout,
            "max_failed_attempts": auth_manager.max_attempts,
            "lockout_duration": auth_manager.lockout_duration
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Security status error: {e}")
        raise HTTPException(status_code=500, detail="Security status service error")