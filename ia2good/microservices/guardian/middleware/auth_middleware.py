"""
Authentication Middleware pour Guardian
Protège les routes avec JWT

Note: Uses guardian_utils (renamed from utils) to avoid conflicts with workspace/utils
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from guardian_utils.jwt_utils import verify_token

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials) -> dict:
    """
    Extrait et vérifie le user depuis le token JWT
    
    Args:
        credentials: Credentials HTTP Bearer
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: Si token invalide
    """
    token = credentials.credentials
    
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide: user_id manquant",
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "volunteer"),
        "permissions": payload.get("permissions", [])
    }


async def require_role(required_role: str):
    """
    Decorator pour vérifier le rôle de l'utilisateur
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: dict = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(credentials: HTTPAuthorizationCredentials = security):
        user = await get_current_user(credentials)
        
        role_hierarchy = {
            "guest": 1,
            "volunteer": 2,
            "coordinator": 3,
            "moderator": 4,
            "admin": 5
        }
        
        user_level = role_hierarchy.get(user["role"], 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission refusée. Rôle requis: {required_role}"
            )
        
        return user
    
    return role_checker


async def require_permission(required_permission: str):
    """
    Decorator pour vérifier une permission spécifique
    """
    async def permission_checker(credentials: HTTPAuthorizationCredentials = security):
        user = await get_current_user(credentials)
        
        if required_permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission manquante: {required_permission}"
            )
        
        return user
    
    return permission_checker
