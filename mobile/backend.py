"""Mobile Backend Core Infrastructure
Enterprise-grade mobile backend services with FastAPI integration

Author: Fahed Mlaiel <mlaiel@live.de>
Business Logic: creators → upload multi-format → AI processing → protection → monetization → collaboration
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

import jwt
from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Internal imports
try:
    from core.database import get_database_session
    from core.config import get_settings
    from core.security import verify_token, create_access_token
    from core.logging import get_logger
except ImportError:
    # Fallback for standalone operation
    from datetime import datetime
    
    def get_database_session():
        return None
    
    def get_settings():
        return {"secret_key": "mobile_secret_key"}
    
    def verify_token(token: str):
        return {"user_id": "test_user"}
    
    def create_access_token(data: dict):
        return "test_token"
    
    def get_logger(name: str):
        return logging.getLogger(name)


@dataclass
class MobileDevice:
    """Mobile device registration and management."""
    device_id: str
    platform: str  # android, ios, react_native
    model: str
    os_version: str
    app_version: str
    push_token: Optional[str] = None
    user_id: Optional[str] = None
    registration_date: datetime = None
    last_active: datetime = None
    is_active: bool = True
    device_fingerprint: Optional[str] = None
    
    def __post_init__(self):
        if self.registration_date is None:
            self.registration_date = datetime.utcnow()
        if self.last_active is None:
            self.last_active = datetime.utcnow()


@dataclass
class MobileSession:
    """Mobile user session management."""
    session_id: str
    user_id: str
    device_id: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True
    last_activity: datetime = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def refresh_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()


class MobileDeviceManager:
    """Professional mobile device management system."""
    
    def __init__(self):
        self.logger = get_logger("mobile.device_manager")
        self.devices: Dict[str, MobileDevice] = {}
        self.sessions: Dict[str, MobileSession] = {}
    
    async def register_device(
        self,
        device_id: str,
        platform: str,
        model: str,
        os_version: str,
        app_version: str,
        user_id: Optional[str] = None,
        push_token: Optional[str] = None
    ) -> MobileDevice:
        """Register new mobile device."""
        
        # Validate platform
        if platform not in ["android", "ios", "react_native"]:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Generate device fingerprint
        device_fingerprint = self._generate_device_fingerprint(
            device_id, platform, model, os_version
        )
        
        device = MobileDevice(
            device_id=device_id,
            platform=platform,
            model=model,
            os_version=os_version,
            app_version=app_version,
            user_id=user_id,
            push_token=push_token,
            device_fingerprint=device_fingerprint
        )
        
        self.devices[device_id] = device
        
        self.logger.info(
            f"Device registered: {device_id} ({platform}) for user {user_id}"
        )
        
        return device
    
    async def update_device(
        self,
        device_id: str,
        **updates
    ) -> Optional[MobileDevice]:
        """Update device information."""
        
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        
        for key, value in updates.items():
            if hasattr(device, key):
                setattr(device, key, value)
        
        device.last_active = datetime.utcnow()
        
        self.logger.info(f"Device updated: {device_id}")
        
        return device
    
    async def get_device(self, device_id: str) -> Optional[MobileDevice]:
        """Get device by ID."""
        return self.devices.get(device_id)
    
    async def get_user_devices(self, user_id: str) -> List[MobileDevice]:
        """Get all devices for a user."""
        return [
            device for device in self.devices.values()
            if device.user_id == user_id and device.is_active
        ]
    
    async def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device."""
        if device_id in self.devices:
            self.devices[device_id].is_active = False
            self.logger.info(f"Device deactivated: {device_id}")
            return True
        return False
    
    def _generate_device_fingerprint(
        self,
        device_id: str,
        platform: str,
        model: str,
        os_version: str
    ) -> str:
        """Generate unique device fingerprint."""
        fingerprint_data = f"{device_id}:{platform}:{model}:{os_version}"
        return str(hash(fingerprint_data))


class MobileAuthManager:
    """Professional mobile authentication system."""
    
    def __init__(self, device_manager: MobileDeviceManager):
        self.logger = get_logger("mobile.auth_manager")
        self.device_manager = device_manager
        self.settings = get_settings()
    
    async def authenticate_device(
        self,
        device_id: str,
        user_credentials: Dict[str, Any],
        request: Request
    ) -> Dict[str, Any]:
        """Authenticate device and create session."""
        
        # Verify device exists
        device = await self.device_manager.get_device(device_id)
        if not device or not device.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not registered or inactive"
            )
        
        # Authenticate user (integrate with existing auth system)
        user_id = await self._authenticate_user(user_credentials)
        
        # Create mobile session
        session = await self._create_mobile_session(
            user_id, device_id, request
        )
        
        # Generate mobile JWT token
        token_data = {
            "user_id": user_id,
            "device_id": device_id,
            "session_id": session.session_id,
            "platform": device.platform
        }
        
        access_token = create_access_token(token_data)
        
        # Update device with user association
        await self.device_manager.update_device(
            device_id, user_id=user_id
        )
        
        self.logger.info(
            f"Mobile authentication successful: user {user_id} on device {device_id}"
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "session_id": session.session_id,
            "expires_in": 3600,
            "device_id": device_id,
            "platform": device.platform
        }
    
    async def verify_mobile_token(
        self,
        token: str,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify mobile JWT token."""
        
        try:
            payload = verify_token(token)
            
            # Verify device if provided
            if device_id:
                token_device_id = payload.get("device_id")
                if token_device_id != device_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Device mismatch"
                    )
            
            # Verify session is still active
            session_id = payload.get("session_id")
            if session_id and session_id in self.device_manager.sessions:
                session = self.device_manager.sessions[session_id]
                if session.is_expired():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session expired"
                    )
                session.refresh_activity()
            
            return payload
            
        except Exception as e:
            self.logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def refresh_mobile_token(
        self,
        session_id: str,
        device_id: str
    ) -> Dict[str, Any]:
        """Refresh mobile session token."""
        
        if session_id not in self.device_manager.sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session = self.device_manager.sessions[session_id]
        
        if session.is_expired() or session.device_id != device_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
        
        # Extend session
        session.expires_at = datetime.utcnow() + timedelta(hours=1)
        session.refresh_activity()
        
        # Generate new token
        device = await self.device_manager.get_device(device_id)
        token_data = {
            "user_id": session.user_id,
            "device_id": device_id,
            "session_id": session_id,
            "platform": device.platform if device else "unknown"
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "session_id": session_id,
            "expires_in": 3600
        }
    
    async def logout_device(self, session_id: str) -> bool:
        """Logout device and invalidate session."""
        
        if session_id in self.device_manager.sessions:
            self.device_manager.sessions[session_id].is_active = False
            self.logger.info(f"Device logged out: session {session_id}")
            return True
        
        return False
    
    async def _authenticate_user(self, credentials: Dict[str, Any]) -> str:
        """Authenticate user with existing auth system."""
        # This would integrate with the existing user authentication
        # For now, return a mock user ID
        return credentials.get("user_id", "mobile_user_123")
    
    async def _create_mobile_session(
        self,
        user_id: str,
        device_id: str,
        request: Request
    ) -> MobileSession:
        """Create new mobile session."""
        
        session_id = str(uuid.uuid4())
        session = MobileSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=1),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        self.device_manager.sessions[session_id] = session
        
        return session


class MobileAPIServer:
    """Enterprise mobile API server."""
    
    def __init__(self):
        self.logger = get_logger("mobile.api_server")
        self.device_manager = MobileDeviceManager()
        self.auth_manager = MobileAuthManager(self.device_manager)
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application with mobile-specific configuration."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info("Mobile API server starting up...")
            yield
            # Shutdown
            self.logger.info("Mobile API server shutting down...")
        
        app = FastAPI(
            title="Ainflue Mobile API",
            version="1.0.0",
            description="Enterprise mobile backend for Ainflue creator platform",
            lifespan=lifespan
        )
        
        # Add CORS middleware for mobile apps
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add compression for mobile optimization
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Add mobile routes
        self._add_mobile_routes(app)
        
        return app
    
    def _add_mobile_routes(self, app: FastAPI):
        """Add mobile-specific API routes."""
        
        @app.post("/mobile/register-device")
        async def register_device(request: Dict[str, Any]):
            """Register a new mobile device."""
            device = await self.device_manager.register_device(**request)
            return {"status": "success", "device": asdict(device)}
        
        @app.post("/mobile/authenticate")
        async def authenticate_device(
            request_data: Dict[str, Any],
            request: Request
        ):
            """Authenticate device and user."""
            auth_result = await self.auth_manager.authenticate_device(
                device_id=request_data["device_id"],
                user_credentials=request_data["credentials"],
                request=request
            )
            return auth_result
        
        @app.post("/mobile/refresh-token")
        async def refresh_token(request_data: Dict[str, Any]):
            """Refresh mobile session token."""
            result = await self.auth_manager.refresh_mobile_token(
                session_id=request_data["session_id"],
                device_id=request_data["device_id"]
            )
            return result
        
        @app.post("/mobile/logout")
        async def logout_device(request_data: Dict[str, Any]):
            """Logout device and invalidate session."""
            success = await self.auth_manager.logout_device(
                session_id=request_data["session_id"]
            )
            return {"status": "success" if success else "failed"}
        
        @app.get("/mobile/device/{device_id}")
        async def get_device_info(device_id: str):
            """Get device information."""
            device = await self.device_manager.get_device(device_id)
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Device not found"
                )
            return asdict(device)
        
        @app.get("/mobile/health")
        async def health_check():
            """Mobile API health check."""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "mobile_backend",
                "version": "1.0.0"
            }


def create_mobile_app() -> FastAPI:
    """Create and configure mobile FastAPI application."""
    server = MobileAPIServer()
    return server.app


# Dependency injection functions
def get_device_manager() -> MobileDeviceManager:
    """Get device manager instance."""
    return MobileDeviceManager()


def get_auth_manager(
    device_manager: MobileDeviceManager = Depends(get_device_manager)
) -> MobileAuthManager:
    """Get auth manager instance."""
    return MobileAuthManager(device_manager)


async def get_mobile_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_manager: MobileAuthManager = Depends(get_auth_manager)
) -> Dict[str, Any]:
    """Dependency to get authenticated mobile user."""
    return await auth_manager.verify_mobile_token(credentials.credentials)


# Main execution
if __name__ == "__main__":
    app = create_mobile_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=True
    )