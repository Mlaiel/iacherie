"""Authentication Middleware Module
===============================

Enterprise-grade authentication middleware for crawler pipeline.
Implements JWT validation, API key management, and multi-factor authentication.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from uuid import uuid4
import hashlib
import hmac
import jwt
import redis
import pyotp
import secrets
import aioredis
from fastapi import HTTPException, status
from pydantic import BaseModel, Field
import logging

from ...core.security import SecurityManager
from ...config.settings import get_settings
from ...utils.cache import CacheManager

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthenticationRequest(BaseModel):
    """
Authentication request model"""
    token: Optional[str] = Field(None, description="JWT token")
    api_key: Optional[str] = Field(None, description="API key")
    user_id: Optional[str] = Field(None, description="User identifier")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    content_type: Optional[str] = Field(None, description="Content type being processed")


class AuthenticationResult(BaseModel):
    """Authentication result model"""
    success: bool = Field(description="Authentication success status")
    user_id: Optional[str] = Field(None, description="Authenticated user ID")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    rate_limit: Dict[str, int] = Field(default_factory=dict, description="Rate limit info")
    expires_at: Optional[datetime] = Field(None, description="Token expiration")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TokenManager:
    """Advanced JWT token management"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        
    async def validate_jwt_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token with advanced security checks"""
        try:
            # Check if token is blacklisted
            if await self.is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # Decode and validate token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # Additional security checks
            if not await self.validate_token_integrity(token, payload):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token integrity validation failed"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is in blacklist"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return await self.redis_client.sismember("blacklisted_tokens", token_hash)
    
    async def validate_token_integrity(self, token: str, payload: Dict[str, Any]) -> bool:
        """Validate token integrity and anti-tampering measures"""
        try:
            # Check token fingerprint
            expected_fingerprint = self.generate_token_fingerprint(payload)
            actual_fingerprint = payload.get("fingerprint")
            
            if expected_fingerprint != actual_fingerprint:
                return False
            
            # Validate issuer and audience
            if payload.get("iss") != settings.TOKEN_ISSUER:
                return False
                
            if payload.get("aud") != settings.TOKEN_AUDIENCE:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Token integrity validation error: {e}")
            return False
    
    def generate_token_fingerprint(self, payload: Dict[str, Any]) -> str:
        """Generate security fingerprint for token"""
        fingerprint_data = {
            "user_id": payload.get("user_id"),
            "issued_at": payload.get("iat"),
            "issuer": payload.get("iss")
        }
        return hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()


class APIKeyManager:
    """Advanced API key management and validation"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
Validate API key with rate limiting and permissions"""
        try:
            # Check API key format
            if not self.is_valid_api_key_format(api_key):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key format"
                )
            
            # Get API key info from cache or database
            key_info = await self.get_api_key_info(api_key)
            if not key_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            
            # Check if key is active
            if not key_info.get("active", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key is disabled"
                )
            
            # Check expiration
            if key_info.get("expires_at"):
                expires_at = datetime.fromisoformat(key_info["expires_at"])
                if datetime.utcnow() > expires_at:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key has expired"
                    )
            
            # Update last used timestamp
            await self.update_api_key_usage(api_key)
            
            return key_info
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    def is_valid_api_key_format(self, api_key: str) -> bool:
        """Validate API key format"""
        # Check length and format (example: ia_live_1234567890abcdef)
        if not api_key or len(api_key) < 20:
            return False
        
        if not api_key.startswith("ia_"):
            return False
        
        return True
    
    async def get_api_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get API key information from cache or database"""
        cache_key = f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()}"
        
        # Try cache first
        cached_info = await self.cache.get(cache_key)
        if cached_info:
            return json.loads(cached_info)
        
        # Simulate database lookup (implement with actual database)
        # This would typically query your user database
        key_info = {
            "user_id": "user_123",
            "permissions": ["crawler.read", "crawler.write", "content.process"],
            "rate_limit": {"requests_per_minute": 1000, "concurrent_requests": 10},
            "active": True,
            "created_at": "2024-01-01T00:00:00",
            "last_used": datetime.utcnow().isoformat()
        }
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, json.dumps(key_info), expire=300)
        
        return key_info
    
    async def update_api_key_usage(self, api_key: str):
        """Update API key last used timestamp"""
        cache_key = f"api_key_usage:{hashlib.sha256(api_key.encode()).hexdigest()}"
        await self.redis_client.set(cache_key, datetime.utcnow().isoformat(), ex=3600)


class MultiFactorAuthenticator:
    """Multi-factor authentication for enhanced security"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def verify_mfa_token(self, user_id: str, mfa_token: str) -> bool:
        """
Verify multi-factor authentication token"""
        try:
            # Get stored MFA secret for user
            mfa_secret = await self.get_user_mfa_secret(user_id)
            if not mfa_secret:
                return False
            
            # Check for replay attacks
            replay_key = f"mfa_used:{user_id}:{mfa_token}"
            if await self.redis_client.get(replay_key):
                logger.warning(f"MFA token replay attempt detected for user: {user_id}")
                return False
            
            # Verify TOTP token
            if self.verify_totp_token(mfa_secret, mfa_token):
                # Mark token as used (valid for 30 seconds window)
                await self.redis_client.setex(replay_key, 30, "used")
                logger.info(f"MFA verification successful for user: {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"MFA verification error: {e}")
            return False
    
    async def get_user_mfa_secret(self, user_id: str) -> Optional[str]:
        """Get user's MFA secret"""
        try:
            # Check cache first
            cache_key = f"mfa_secret:{user_id}"
            cached_secret = await self.redis_client.get(cache_key)
            
            if cached_secret:
                return cached_secret.decode() if isinstance(cached_secret, bytes) else cached_secret
            
            # In production, this would query the user database
            # For now, use file-based storage
            import os
            mfa_secrets_file = "/tmp/mfa_secrets.json"
            
            if os.path.exists(mfa_secrets_file):
                with open(mfa_secrets_file, 'r') as f:
                    mfa_secrets = json.load(f)
                    
                    secret = mfa_secrets.get(user_id)
                    if secret:
                        # Cache for 1 hour
                        await self.redis_client.setex(cache_key, 3600, secret)
                        return secret
            
            # Generate new secret if none exists
            import pyotp
            new_secret = pyotp.random_base32()
            
            # Store the new secret
            await self.store_user_mfa_secret(user_id, new_secret)
            
            return new_secret
            
        except Exception as e:
            logger.error(f"Failed to get MFA secret for user {user_id}: {e}")
            return None
    
    async def store_user_mfa_secret(self, user_id: str, secret: str):
        """Store user's MFA secret"""
        try:
            # Cache the secret
            cache_key = f"mfa_secret:{user_id}"
            await self.redis_client.setex(cache_key, 3600, secret)
            
            # Store in file (in production would use encrypted database)
            import os
            mfa_secrets_file = "/tmp/mfa_secrets.json"
            
            # Load existing secrets
            mfa_secrets = {}
            if os.path.exists(mfa_secrets_file):
                with open(mfa_secrets_file, 'r') as f:
                    mfa_secrets = json.load(f)
            
            # Add/update the secret
            mfa_secrets[user_id] = secret
            
            # Save back to file
            with open(mfa_secrets_file, 'w') as f:
                json.dump(mfa_secrets, f)
                
            logger.info(f"MFA secret stored for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to store MFA secret for user {user_id}: {e}")
            raise
    
    def verify_totp_token(self, secret: str, token: str) -> bool:
        """Verify Time-based One-Time Password"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    async def send_sms_mfa_code(self, user_id: str, phone_number: str) -> bool:
        """
Send SMS MFA code to user's phone"""
        try:
            # Generate 6-digit code
            mfa_code = f"{secrets.randbelow(900000) + 100000:06d}"
            
            # Store code for verification (valid for 5 minutes)
            cache_key = f"sms_mfa:{user_id}"
            await self.redis_client.setex(cache_key, 300, mfa_code)
            
            # In production, integrate with SMS service like Twilio
            # For now, log the code (REMOVE IN PRODUCTION)
            logger.info(f"SMS MFA code for {user_id}: {mfa_code}")
            
            # Store attempt for rate limiting
            attempt_key = f"sms_attempts:{user_id}"
            attempts = await self.redis_client.get(attempt_key)
            attempts = int(attempts) if attempts else 0
            
            if attempts >= 3:
                logger.warning(f"SMS MFA rate limit exceeded for user: {user_id}")
                return False
                
            await self.redis_client.setex(attempt_key, 3600, attempts + 1)
            
            logger.info(f"SMS MFA code sent to user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS MFA code: {e}")
            return False
    
    async def verify_sms_mfa_code(self, user_id: str, code: str) -> bool:
        """Verify SMS MFA code"""
        try:
            cache_key = f"sms_mfa:{user_id}"
            stored_code = await self.redis_client.get(cache_key)
            
            if not stored_code:
                logger.warning(f"No SMS MFA code found for user: {user_id}")
                return False
                
            stored_code = stored_code.decode() if isinstance(stored_code, bytes) else stored_code
            
            if stored_code == code:
                # Code is valid, remove it to prevent reuse
                await self.redis_client.delete(cache_key)
                
                # Reset attempt counter
                attempt_key = f"sms_attempts:{user_id}"
                await self.redis_client.delete(attempt_key)
                
                logger.info(f"SMS MFA verification successful for user: {user_id}")
                return True
            else:
                logger.warning(f"Invalid SMS MFA code for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"SMS MFA verification error: {e}")
            return False
    
    async def verify_hardware_key_mfa(self, user_id: str, fido2_response: Dict[str, Any]) -> bool:
        """Verify hardware key MFA using FIDO2"""
        try:
            # Import here to avoid circular dependency
            from ...security.fido2_webauthn import fido2_manager
            
            # Verify FIDO2 authentication
            authenticated_user = await fido2_manager.verify_authentication(fido2_response)
            
            if authenticated_user == user_id:
                logger.info(f"Hardware key MFA verification successful for user: {user_id}")
                return True
            else:
                logger.warning(f"Hardware key MFA verification failed for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Hardware key MFA verification error: {e}")
            return False
    
    async def verify_any_mfa(self, user_id: str, mfa_data: Dict[str, Any]) -> bool:
        """Verify any supported MFA method"""
        try:
            # Check TOTP token
            if "totp_token" in mfa_data:
                if await self.verify_mfa_token(user_id, mfa_data["totp_token"]):
                    return True
            
            # Check SMS code
            if "sms_code" in mfa_data:
                if await self.verify_sms_mfa_code(user_id, mfa_data["sms_code"]):
                    return True
            
            # Check hardware key
            if "fido2_response" in mfa_data:
                if await self.verify_hardware_key_mfa(user_id, mfa_data["fido2_response"]):
                    return True
            
            logger.warning(f"All MFA methods failed for user: {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"MFA verification error: {e}")
            return False


class AuthenticationMiddleware:
    """Main authentication middleware orchestrator"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.api_key_manager = APIKeyManager()
        self.mfa_authenticator = MultiFactorAuthenticator()
        self.security_manager = SecurityManager()
        self.redis_client = redis.from_url(settings.REDIS_URL)
        
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        """
Main authentication method"""
        try:
            start_time = time.time()
            
            # Initialize result
            result = AuthenticationResult(success=False)
            
            # JWT Token Authentication
            if request.token:
                jwt_result = await self.authenticate_with_jwt(request)
                if jwt_result.success:
                    result = jwt_result
                else:
                    return jwt_result
            
            # API Key Authentication
            elif request.api_key:
                api_result = await self.authenticate_with_api_key(request)
                if api_result.success:
                    result = api_result
                else:
                    return api_result
            
            else:
                return AuthenticationResult(
                    success=False,
                    error="No authentication credentials provided"
                )
            
            # Validate permissions
            if not await self.validate_permissions(result.user_id, request.permissions):
                return AuthenticationResult(
                    success=False,
                    error="Insufficient permissions"
                )
            
            # Log successful authentication
            await self.log_authentication_event(result.user_id, "success", 
                                              time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self.log_authentication_event(request.user_id, "error", 
                                              time.time() - start_time)
            return AuthenticationResult(
                success=False,
                error=f"Authentication failed: {str(e)}"
            )
    
    async def authenticate_with_jwt(self, request: AuthenticationRequest) -> AuthenticationResult:
        """Authenticate using JWT token"""
        try:
            payload = await self.token_manager.validate_jwt_token(request.token)
            
            return AuthenticationResult(
                success=True,
                user_id=payload.get("user_id"),
                permissions=payload.get("permissions", []),
                expires_at=datetime.fromtimestamp(payload.get("exp")),
                metadata={"auth_method": "jwt", "token_id": payload.get("jti")}
            )
            
        except HTTPException as e:
            return AuthenticationResult(
                success=False,
                error=e.detail
            )
    
    async def authenticate_with_api_key(self, request: AuthenticationRequest) -> AuthenticationResult:
        """Authenticate using API key"""
        try:
            key_info = await self.api_key_manager.validate_api_key(request.api_key)
            
            return AuthenticationResult(
                success=True,
                user_id=key_info.get("user_id"),
                permissions=key_info.get("permissions", []),
                rate_limit=key_info.get("rate_limit", {}),
                metadata={"auth_method": "api_key"}
            )
            
        except HTTPException as e:
            return AuthenticationResult(
                success=False,
                error=e.detail
            )
    
    async def validate_permissions(self, user_id: str, required_permissions: List[str]) -> bool:
        """Validate user permissions"""
        if not required_permissions:
            return True
        
        try:
            # Get user permissions from cache or database
            user_permissions = await self.get_user_permissions(user_id)
            
            # Check if user has all required permissions
            for permission in required_permissions:
                if permission not in user_permissions:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Permission validation error: {e}")
            return False
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        cache_key = f"user_permissions:{user_id}"
        
        # Try cache first
        cached_permissions = await self.redis_client.get(cache_key)
        if cached_permissions:
            return json.loads(cached_permissions)
        
        # Simulate database lookup
        permissions = [
            "crawler.read", "crawler.write", "content.process",
            "content.protect", "content.monetize", "fingerprint.generate",
            "monitoring.view", "security.access", "rate_limit.priority",
            "validation.execute", "error_handling.view"
        ]
        
        # Cache for 10 minutes
        await self.redis_client.set(cache_key, json.dumps(permissions), ex=600)
        
        return permissions


class BiometricAuthenticator:
    """Advanced biometric authentication for high-security scenarios"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.logger = logging.getLogger(__name__)
        
    async def validate_biometric_signature(self, user_id: str, 
                                         signature_data: Dict[str, Any]) -> bool:
        """
Validate biometric signatures (typing patterns, mouse movement, etc.)"""
        try:
            # Retrieve stored biometric profile
            profile_key = f"biometric_profile:{user_id}"
            stored_profile = await self.redis_client.get(profile_key)
            
            if not stored_profile:
                # First-time user, store the signature
                await self.redis_client.set(
                    profile_key, 
                    json.dumps(signature_data), 
                    ex=86400 * 30  # 30 days
                )
                return True
            
            stored_data = json.loads(stored_profile)
            
            # Calculate similarity between signatures
            similarity_score = await self._calculate_biometric_similarity(
                stored_data, signature_data
            )
            
            # Update profile with new data (weighted average)
            if similarity_score > 0.8:  # 80% similarity threshold
                updated_profile = await self._update_biometric_profile(
                    stored_data, signature_data
                )
                await self.redis_client.set(
                    profile_key, 
                    json.dumps(updated_profile), 
                    ex=86400 * 30
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Biometric validation error: {str(e)}")
            return False
    
    async def _calculate_biometric_similarity(self, profile1: Dict, 
                                           profile2: Dict) -> float:
        """Calculate similarity between biometric profiles"""
        # Implementation of biometric similarity algorithm
        # This is a simplified version - real implementation would be more complex
        features = ['typing_speed', 'mouse_movement', 'click_patterns']
        similarities = []
        
        for feature in features:
            if feature in profile1 and feature in profile2:
                val1 = profile1[feature]
                val2 = profile2[feature]
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Normalize and calculate similarity
                    diff = abs(val1 - val2) / max(val1, val2, 1)
                    similarity = 1 - min(diff, 1)
                    similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    async def _update_biometric_profile(self, old_profile: Dict, 
                                      new_data: Dict) -> Dict:
        """
Update biometric profile with weighted average"""
        weight_old = 0.7
        weight_new = 0.3
        
        updated = {}
        for key in set(old_profile.keys()) | set(new_data.keys()):
            if key in old_profile and key in new_data:
                if isinstance(old_profile[key], (int, float)):
                    updated[key] = (
                        old_profile[key] * weight_old + 
                        new_data[key] * weight_new
                    )
                else:
                    updated[key] = new_data[key]
            elif key in old_profile:
                updated[key] = old_profile[key]
            else:
                updated[key] = new_data[key]
        
        return updated


class BehavioralAnalyzer:
    """
Behavioral analysis for anomaly detection"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        
    async def analyze_user_behavior(self, user_id: str, 
                                  request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Analyze user behavior patterns for anomaly detection"""
        behavior_key = f"behavior:{user_id}"
        
        # Get recent behavior history
        recent_behavior = await self.redis_client.lrange(behavior_key, 0, 100)
        behavior_history = [json.loads(b) for b in recent_behavior]
        
        # Extract features from current request
        current_features = await self._extract_behavioral_features(request_data)
        
        # Analyze for anomalies
        anomaly_score = await self._calculate_anomaly_score(
            behavior_history, current_features
        )
        
        # Store current behavior
        await self.redis_client.lpush(
            behavior_key, 
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "features": current_features
            })
        )
        await self.redis_client.ltrim(behavior_key, 0, 1000)  # Keep last 1000
        await self.redis_client.expire(behavior_key, 86400 * 7)  # 7 days
        
        return {
            "anomaly_score": anomaly_score,
            "is_suspicious": anomaly_score > 0.7,
            "risk_level": self._calculate_risk_level(anomaly_score),
            "features": current_features
        }
    
    async def _extract_behavioral_features(self, request_data: Dict) -> Dict:
        """Extract behavioral features from request"""
        return {
            "request_time": datetime.utcnow().hour,
            "user_agent": request_data.get("user_agent", ""),
            "ip_address": request_data.get("ip_address", ""),
            "request_size": len(str(request_data)),
            "content_type": request_data.get("content_type", ""),
            "processing_flags": request_data.get("processing_options", {})
        }
    
    async def _calculate_anomaly_score(self, history: List[Dict], 
                                     current: Dict) -> float:
        """Calculate anomaly score based on historical behavior"""
        if not history:
            return 0.0
        
        # Simple anomaly detection based on feature deviations
        scores = []
        
        for feature, value in current.items():
            if feature == "request_time" and isinstance(value, int):
                # Check time pattern deviation
                historical_times = [h["features"].get("request_time", 12) 
                                  for h in history if "features" in h]
                if historical_times:
                    avg_time = sum(historical_times) / len(historical_times)
                    time_deviation = abs(value - avg_time) / 12  # Normalize to 0-1
                    scores.append(min(time_deviation, 1.0))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_risk_level(self, anomaly_score: float) -> str:
        """Calculate risk level based on anomaly score"""
        if anomaly_score < 0.3:
            return "low"
        elif anomaly_score < 0.7:
            return "medium"
        else:
            return "high"


class GeolocationValidator:
    """Geolocation-based authentication validation"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.allowed_countries = settings.ALLOWED_COUNTRIES or []
        self.blocked_countries = settings.BLOCKED_COUNTRIES or []
        
    async def validate_geolocation(self, ip_address: str, user_id: str) -> Dict[str, Any]:
        """
Validate user geolocation"""
        try:
            # Get geolocation data (simplified - would use real GeoIP service)
            geo_data = await self._get_geolocation_data(ip_address)
            
            # Check against allowed/blocked lists
            country_code = geo_data.get("country_code", "")
            is_allowed = True
            
            if self.blocked_countries and country_code in self.blocked_countries:
                is_allowed = False
            
            if self.allowed_countries and country_code not in self.allowed_countries:
                is_allowed = False
            
            # Check for location changes
            previous_location = await self._get_previous_location(user_id)
            location_changed = await self._check_location_change(
                previous_location, geo_data
            )
            
            # Store current location
            await self._store_location(user_id, geo_data)
            
            return {
                "is_allowed": is_allowed,
                "country_code": country_code,
                "city": geo_data.get("city", ""),
                "location_changed": location_changed,
                "requires_additional_verification": location_changed and is_allowed
            }
            
        except Exception as e:
            logger.error(f"Geolocation validation error: {str(e)}")
            return {"is_allowed": True, "error": str(e)}
    
    async def _get_geolocation_data(self, ip_address: str) -> Dict[str, Any]:
        """Get geolocation data for IP address"""
        # Simplified implementation - would use real GeoIP service
        cache_key = f"geo:{ip_address}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # Mock geolocation data
        geo_data = {
            "country_code": "DE",
            "country": "Germany",
            "city": "Berlin",
            "latitude": 52.5200,
            "longitude": 13.4050
        }
        
        await self.redis_client.set(cache_key, json.dumps(geo_data), ex=3600)
        return geo_data
    
    async def _get_previous_location(self, user_id: str) -> Optional[Dict]:
        """Get user's previous location"""
        location_key = f"user_location:{user_id}"
        data = await self.redis_client.get(location_key)
        return json.loads(data) if data else None
    
    async def _check_location_change(self, previous: Optional[Dict], 
                                   current: Dict) -> bool:
        """Check if location has significantly changed"""
        if not previous:
            return False
        
        # Simple distance calculation
        prev_lat = previous.get("latitude", 0)
        prev_lon = previous.get("longitude", 0)
        curr_lat = current.get("latitude", 0)
        curr_lon = current.get("longitude", 0)
        
        # Rough distance calculation (simplified)
        lat_diff = abs(prev_lat - curr_lat)
        lon_diff = abs(prev_lon - curr_lon)
        
        # Consider significant if difference > 1 degree (~111km)
        return lat_diff > 1.0 or lon_diff > 1.0
    
    async def _store_location(self, user_id: str, geo_data: Dict):
        """Store user's current location"""
        location_key = f"user_location:{user_id}"
        await self.redis_client.set(
            location_key, 
            json.dumps(geo_data), 
            ex=86400 * 30  # 30 days
        )
    
    async def log_authentication_event(self, user_id: Optional[str], event_type: str, 
                                     duration: float, additional_data: Optional[Dict] = None):
        """Log authentication events for monitoring"""
        event = {
            "user_id": user_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "source": "crawler_middleware",
            "additional_data": additional_data or {}
        }
        
        # Log to Redis for real-time monitoring
        await self.redis_client.lpush("auth_events", json.dumps(event))
        await self.redis_client.ltrim("auth_events", 0, 1000)  # Keep last 1000 events


# Factory functions for dependency injection
def get_authentication_middleware() -> AuthenticationMiddleware:
    """Get authentication middleware instance"""
    return AuthenticationMiddleware()


def get_biometric_authenticator() -> BiometricAuthenticator:
    """
Get biometric authenticator instance"""
    return BiometricAuthenticator()


def get_behavioral_analyzer() -> BehavioralAnalyzer:
    """
Get behavioral analyzer instance"""
    return BehavioralAnalyzer()


def get_geolocation_validator() -> GeolocationValidator:
    """
Get geolocation validator instance"""
    return GeolocationValidator()


# Utility functions
async def require_auth(request: AuthenticationRequest) -> AuthenticationResult:
    """
Convenience function for authentication requirement"""
    middleware = get_authentication_middleware()
    return await middleware.authenticate(request)


async def require_api_key(api_key: str) -> bool:
    """
Convenience function for API key validation"""
    middleware = get_authentication_middleware()
    api_manager = APIKeyManager()
    return await api_manager.validate_api_key(api_key)


async def require_mfa(user_id: str, mfa_code: str) -> bool:
    """
Convenience function for MFA validation"""
    mfa_auth = MultiFactorAuthenticator()
    return await mfa_auth.validate_mfa_code(user_id, mfa_code)


async def require_permissions(user_id: str, permissions: List[str]) -> bool:
    """
Convenience function for permission checking"""
    middleware = get_authentication_middleware()
    return await middleware.validate_permissions(user_id, permissions)
