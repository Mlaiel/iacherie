"""
Authentication and Authorization utilities
Integrates with iacherie's JWT authentication system
"""
import os
import jwt
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
import logging
import httpx

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
IACHERIE_AUTH_URL = os.getenv("IACHERIE_AUTH_URL", "http://localhost:8000/api/auth/verify")


async def verify_token(token: str) -> dict:
    """
    Verify JWT token
    
    Can verify locally or delegate to iacherie service
    """
    try:
        # Try local verification first
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        # If local verification fails, try iacherie service
        return await verify_token_with_iacherie(token)


async def verify_token_with_iacherie(token: str) -> dict:
    """
    Verify token with iacherie authentication service
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IACHERIE_AUTH_URL,
                json={"token": token},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
    except httpx.RequestError as e:
        logger.warning(f"Cannot reach iacherie auth service: {e}")
        # Fallback: reject token if service is unreachable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from JWT token
    
    Returns:
        dict with user info: {
            "id": UUID,
            "email": str,
            "role": str,  # patient, doctor, specialist, pharmacist, admin
            "name": str,
            ...
        }
    
    Usage:
        @router.get("/me")
        async def get_me(user: dict = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    payload = await verify_token(token)
    
    # Extract user info from payload
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {
        "id": UUID(user_id) if isinstance(user_id, str) else user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "patient"),
        "name": payload.get("name"),
        "verified": payload.get("verified", False),
        "permissions": payload.get("permissions", [])
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Get current user if authenticated, None otherwise
    Useful for optional authentication
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_roles: List[str]):
    """
    Decorator to require specific roles
    
    Usage:
        @router.post("/admin/users")
        async def create_user(
            user: dict = Depends(require_role(["admin"]))
        ):
            ...
    """
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role")
        
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        
        return user
    
    return role_checker


def require_permission(required_permission: str):
    """
    Decorator to require specific permission
    
    Usage:
        @router.delete("/cases/{case_id}")
        async def delete_case(
            user: dict = Depends(require_permission("cases:delete"))
        ):
            ...
    """
    async def permission_checker(user: dict = Depends(get_current_user)) -> dict:
        permissions = user.get("permissions", [])
        
        if required_permission not in permissions and "admin" not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        
        return user
    
    return permission_checker


def require_verified():
    """
    Require user to be verified (e.g., email verified, doctor credentials verified)
    """
    async def verified_checker(user: dict = Depends(get_current_user)) -> dict:
        if not user.get("verified", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account verification required"
            )
        
        return user
    
    return verified_checker


async def get_patient_id(user: dict = Depends(get_current_user)) -> UUID:
    """
    Get patient ID for the current user
    Useful for patient-specific endpoints
    """
    if user.get("role") != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for patients only"
        )
    
    return user.get("id")


async def get_doctor_id(user: dict = Depends(require_role(["doctor", "specialist"]))) -> UUID:
    """
    Get doctor ID for the current user
    Useful for doctor-specific endpoints
    """
    return user.get("id")


def check_resource_ownership(user: dict, resource_user_id: UUID) -> bool:
    """
    Check if user owns the resource
    Admins bypass this check
    """
    if user.get("role") == "admin":
        return True
    
    return str(user.get("id")) == str(resource_user_id)


def require_ownership(resource_user_id: UUID):
    """
    Require user to own the resource or be admin
    
    Usage:
        @router.get("/documents/{document_id}")
        async def get_document(
            document_id: UUID,
            db: AsyncSession = Depends(get_db)
        ):
            document = await get_document_from_db(document_id)
            user = Depends(require_ownership(document.patient_id))
            return document
    """
    async def ownership_checker(user: dict = Depends(get_current_user)) -> dict:
        if not check_resource_ownership(user, resource_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
        
        return user
    
    return ownership_checker


# For testing/development: create a mock user
def get_mock_user_for_testing():
    """
    Returns a mock user for testing purposes
    Only use in development!
    """
    if os.getenv("ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mock authentication only available in development"
        )
    
    return {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "email": "test@medcare.com",
        "role": "patient",
        "name": "Test User",
        "verified": True,
        "permissions": []
    }
