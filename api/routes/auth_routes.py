"""
Authentication Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    """User login"""
    return {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": "user_123",
            "email": request.email,
            "name": "Demo User",
            "plan": "pro"
        }
    }

@router.post("/logout")
async def logout():
    """User logout"""
    return {"message": "Logged out successfully"}

__all__ = ["router"]
