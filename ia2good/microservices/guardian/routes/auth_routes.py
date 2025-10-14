"""
Authentication Routes pour Guardian
Login, Register, Refresh Token
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional

from guardian_utils.jwt_utils import (
    create_access_token, 
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token
)
from middleware.auth_middleware import get_current_user, security

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# MODELS
# ============================================================================

class UserRegister(BaseModel):
    """Registration data"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    preferred_language: str = "EN"


class UserLogin(BaseModel):
    """Login credentials"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 10080  # minutes


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# ============================================================================
# STORAGE TEMPORAIRE (En attendant PostgreSQL)
# ============================================================================

# Stockage in-memory temporaire
USERS_DB = {}


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Enregistre un nouvel utilisateur
    Support multilingue: 644 langues
    """
    # Vérifier si email existe déjà
    if user_data.email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà enregistré"
        )
    
    # Hasher le mot de passe
    hashed_password = get_password_hash(user_data.password)
    
    # Créer l'utilisateur
    user_id = f"user_{len(USERS_DB) + 1}"
    USERS_DB[user_data.email] = {
        "user_id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "preferred_language": user_data.preferred_language,
        "role": "volunteer",
        "permissions": ["read_missions", "apply_volunteer"],
        "is_active": True
    }
    
    # Générer les tokens
    access_token = create_access_token(
        data={
            "sub": user_id,
            "email": user_data.email,
            "role": "volunteer",
            "permissions": ["read_missions", "apply_volunteer"],
            "language": user_data.preferred_language
        }
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user_id, "email": user_data.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Connexion utilisateur
    """
    # Vérifier si l'utilisateur existe
    user = USERS_DB.get(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier le mot de passe
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier si le compte est actif
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Générer les tokens
    access_token = create_access_token(
        data={
            "sub": user["user_id"],
            "email": user["email"],
            "role": user.get("role", "volunteer"),
            "permissions": user.get("permissions", []),
            "language": user.get("preferred_language", "EN")
        }
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user["user_id"], "email": user["email"]}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Rafraîchit l'access token avec un refresh token
    """
    payload = verify_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré"
        )
    
    # Vérifier que c'est bien un refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    # Retrouver l'utilisateur
    user = USERS_DB.get(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé"
        )
    
    # Générer un nouveau access token
    access_token = create_access_token(
        data={
            "sub": user_id,
            "email": email,
            "role": user.get("role", "volunteer"),
            "permissions": user.get("permissions", []),
            "language": user.get("preferred_language", "EN")
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token  # On garde le même refresh token
    )


@router.get("/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtient les informations de l'utilisateur connecté
    """
    user = await get_current_user(credentials)
    
    # Retrouver les détails complets
    user_details = USERS_DB.get(user["email"], {})
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "first_name": user_details.get("first_name"),
        "last_name": user_details.get("last_name"),
        "role": user["role"],
        "permissions": user["permissions"],
        "preferred_language": user_details.get("preferred_language", "EN")
    }


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Déconnexion (invalide le token côté client)
    """
    user = await get_current_user(credentials)
    
    # En production, on ajouterait le token à une blacklist Redis
    # Pour l'instant, on retourne juste un succès
    
    return {
        "message": "Déconnexion réussie",
        "user_id": user["user_id"]
    }


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Change le mot de passe de l'utilisateur
    """
    user = await get_current_user(credentials)
    
    user_data = USERS_DB.get(user["email"])
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier l'ancien mot de passe
    if not verify_password(old_password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ancien mot de passe incorrect"
        )
    
    # Hasher et sauvegarder le nouveau mot de passe
    user_data["password_hash"] = get_password_hash(new_password)
    
    return {"message": "Mot de passe changé avec succès"}
