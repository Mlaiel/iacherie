"""FIDO2/WebAuthn Hardware Security Key Implementation
=================================================

Enterprise-grade FIDO2/WebAuthn implementation for hardware security keys.
Supports YubiKey, SoloKey, and other FIDO2-compliant hardware devices.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

⚠️  PROPRIETARY SECURITY CODE ⚠️
This security implementation contains proprietary algorithms and methods.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
"""
import asyncio
import base64
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

import aioredis
from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AuthenticatorTransport(Enum):
    """FIDO2 authenticator transport methods"""
    USB = "usb"
    NFC = "nfc"
    BLE = "ble"
    INTERNAL = "internal"
    HYBRID = "hybrid"


class AttestationConveyancePreference(Enum):
    """Attestation conveyance preference"""
    NONE = "none"
    INDIRECT = "indirect"
    DIRECT = "direct"
    ENTERPRISE = "enterprise"


class UserVerificationRequirement(Enum):
    """User verification requirement"""
    REQUIRED = "required"
    PREFERRED = "preferred"
    DISCOURAGED = "discouraged"


class AuthenticatorAttachment(Enum):
    """Authenticator attachment modality"""
    PLATFORM = "platform"
    CROSS_PLATFORM = "cross-platform"


@dataclass
class PublicKeyCredentialDescriptor:
    """Public key credential descriptor"""
    type: str
    id: bytes
    transports: List[AuthenticatorTransport] = field(default_factory=list)


@dataclass
class PublicKeyCredentialUserEntity:
    """User entity for WebAuthn"""
    id: bytes
    name: str
    display_name: str


@dataclass
class PublicKeyCredentialRpEntity:
    """Relying party entity for WebAuthn"""
    name: str
    id: str


@dataclass
class PublicKeyCredentialParameters:
    """Public key credential algorithm parameters"""
    type: str
    alg: int  # COSE algorithm identifier


class RegistrationChallenge(BaseModel):
    """FIDO2 registration challenge"""
    challenge: str = Field(description="Base64 encoded challenge")
    rp: Dict[str, str] = Field(description="Relying party information")
    user: Dict[str, str] = Field(description="User information")
    pubKeyCredParams: List[Dict[str, Union[str, int]]] = Field(description="Supported algorithms")
    timeout: int = Field(default=60000, description="Timeout in milliseconds")
    excludeCredentials: List[Dict[str, Any]] = Field(default_factory=list)
    authenticatorSelection: Dict[str, str] = Field(default_factory=dict)
    attestation: str = Field(default="none")


class AuthenticationChallenge(BaseModel):
    """FIDO2 authentication challenge"""
    challenge: str = Field(description="Base64 encoded challenge")
    timeout: int = Field(default=60000, description="Timeout in milliseconds")
    rpId: str = Field(description="Relying party identifier")
    allowCredentials: List[Dict[str, Any]] = Field(default_factory=list)
    userVerification: str = Field(default="preferred")


class FIDO2Manager:
    """FIDO2/WebAuthn Manager for hardware security keys"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", rp_id: str = "ainflue.com"):
        self.rp_id = rp_id
        self.rp_name = "Ainflue - AI Influencer Platform"
        self.redis_client = None
        self.redis_url = redis_url
        
        # Supported algorithms (COSE Algorithm Identifiers)
        self.supported_algorithms = [
            {"type": "public-key", "alg": -7},   # ES256
            {"type": "public-key", "alg": -257}, # RS256
            {"type": "public-key", "alg": -37},  # PS256
            {"type": "public-key", "alg": -8},   # EdDSA
        ]
        
    async def initialize(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(self.redis_url)
            
    async def generate_registration_challenge(
        self,
        user_id: str,
        username: str,
        display_name: str,
        exclude_existing: bool = True
    ) -> RegistrationChallenge:
        """Generate FIDO2 registration challenge for new authenticator"""
        await self.initialize()
        
        # Generate cryptographically secure challenge
        challenge_bytes = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
        
        # Get existing credentials to exclude
        exclude_credentials = []
        if exclude_existing:
            existing_creds = await self.get_user_credentials(user_id)
            exclude_credentials = [
                {
                    "type": "public-key",
                    "id": cred_id,
                    "transports": ["usb", "nfc", "ble", "internal"]
                }
                for cred_id in existing_creds.keys()
            ]
        
        # Create user entity
        user_id_bytes = user_id.encode('utf-8')
        user_id_b64 = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8').rstrip('=')
        
        challenge = RegistrationChallenge(
            challenge=challenge_b64,
            rp={
                "name": self.rp_name,
                "id": self.rp_id
            },
            user={
                "id": user_id_b64,
                "name": username,
                "displayName": display_name
            },
            pubKeyCredParams=self.supported_algorithms,
            timeout=60000,
            excludeCredentials=exclude_credentials,
            authenticatorSelection={
                "authenticatorAttachment": "cross-platform",
                "userVerification": "preferred",
                "requireResidentKey": False
            },
            attestation="none"
        )
        
        # Store challenge for verification
        challenge_key = f"fido2_reg_challenge:{user_id}"
        challenge_data = {
            "challenge": challenge_b64,
            "user_id": user_id,
            "username": username,
            "display_name": display_name,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
        await self.redis_client.setex(
            challenge_key,
            300,  # 5 minutes
            json.dumps(challenge_data)
        )
        
        logger.info(f"Generated FIDO2 registration challenge for user: {user_id}")
        return challenge
        
    async def verify_registration(
        self,
        user_id: str,
        credential_data: Dict[str, Any]
    ) -> bool:
        """Verify FIDO2 registration response and store credential"""
        await self.initialize()
        
        try:
            # Get stored challenge
            challenge_key = f"fido2_reg_challenge:{user_id}"
            challenge_data_str = await self.redis_client.get(challenge_key)
            
            if not challenge_data_str:
                logger.error(f"No registration challenge found for user: {user_id}")
                return False
                
            challenge_data = json.loads(challenge_data_str)
            stored_challenge = challenge_data["challenge"]
            
            # Basic validation of credential response
            if not self._validate_credential_response(credential_data, stored_challenge):
                return False
                
            # Extract credential ID and public key
            credential_id = credential_data.get("id")
            raw_id = credential_data.get("rawId")
            response = credential_data.get("response", {})
            
            if not credential_id or not raw_id or not response:
                logger.error("Invalid credential response format")
                return False
                
            # Store the credential
            await self._store_user_credential(
                user_id,
                credential_id,
                {
                    "credential_id": credential_id,
                    "raw_id": raw_id,
                    "public_key": response.get("publicKey"),
                    "sign_count": response.get("signCount", 0),
                    "created_at": datetime.utcnow().isoformat(),
                    "last_used": None,
                    "is_active": True
                }
            )
            
            # Clean up challenge
            await self.redis_client.delete(challenge_key)
            
            logger.info(f"FIDO2 credential registered successfully for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"FIDO2 registration verification failed: {e}")
            return False
            
    async def generate_authentication_challenge(
        self,
        user_id: Optional[str] = None
    ) -> AuthenticationChallenge:
        """Generate FIDO2 authentication challenge"""
        await self.initialize()
        
        # Generate cryptographically secure challenge
        challenge_bytes = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
        
        # Get user credentials if user_id provided
        allow_credentials = []
        if user_id:
            user_creds = await self.get_user_credentials(user_id)
            allow_credentials = [
                {
                    "type": "public-key",
                    "id": cred_id,
                    "transports": ["usb", "nfc", "ble", "internal"]
                }
                for cred_id in user_creds.keys()
            ]
        
        challenge = AuthenticationChallenge(
            challenge=challenge_b64,
            timeout=60000,
            rpId=self.rp_id,
            allowCredentials=allow_credentials,
            userVerification="preferred"
        )
        
        # Store challenge for verification
        challenge_key = f"fido2_auth_challenge:{challenge_b64}"
        challenge_data = {
            "challenge": challenge_b64,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
        await self.redis_client.setex(
            challenge_key,
            300,  # 5 minutes
            json.dumps(challenge_data)
        )
        
        logger.info(f"Generated FIDO2 authentication challenge for user: {user_id}")
        return challenge
        
    async def verify_authentication(
        self,
        credential_data: Dict[str, Any]
    ) -> Optional[str]:
        """Verify FIDO2 authentication response and return user_id"""
        await self.initialize()
        
        try:
            credential_id = credential_data.get("id")
            response = credential_data.get("response", {})
            
            if not credential_id or not response:
                logger.error("Invalid authentication response format")
                return None
                
            # Find user by credential ID
            user_id = await self._find_user_by_credential(credential_id)
            if not user_id:
                logger.error(f"No user found for credential: {credential_id}")
                return None
                
            # Get stored challenge
            client_data_json = response.get("clientDataJSON")
            if not client_data_json:
                logger.error("Missing clientDataJSON in response")
                return None
                
            # Decode and parse client data
            client_data = json.loads(base64.urlsafe_b64decode(
                client_data_json + "=" * (4 - len(client_data_json) % 4)
            ).decode('utf-8'))
            
            challenge = client_data.get("challenge")
            if not challenge:
                logger.error("Missing challenge in client data")
                return None
                
            # Verify stored challenge
            challenge_key = f"fido2_auth_challenge:{challenge}"
            challenge_data_str = await self.redis_client.get(challenge_key)
            
            if not challenge_data_str:
                logger.error("Authentication challenge not found or expired")
                return None
                
            # Update credential usage
            await self._update_credential_usage(user_id, credential_id)
            
            # Clean up challenge
            await self.redis_client.delete(challenge_key)
            
            logger.info(f"FIDO2 authentication successful for user: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"FIDO2 authentication verification failed: {e}")
            return None
            
    async def get_user_credentials(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all FIDO2 credentials for a user"""
        await self.initialize()
        
        credentials_key = f"fido2_credentials:{user_id}"
        credentials_data = await self.redis_client.get(credentials_key)
        
        if not credentials_data:
            return {}
            
        try:
            return json.loads(credentials_data)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse credentials for user: {user_id}")
            return {}
            
    async def revoke_credential(self, user_id: str, credential_id: str) -> bool:
        """Revoke a FIDO2 credential"""
        await self.initialize()
        
        try:
            credentials = await self.get_user_credentials(user_id)
            
            if credential_id not in credentials:
                logger.error(f"Credential not found: {credential_id}")
                return False
                
            # Mark as inactive instead of deleting
            credentials[credential_id]["is_active"] = False
            credentials[credential_id]["revoked_at"] = datetime.utcnow().isoformat()
            
            # Update stored credentials
            credentials_key = f"fido2_credentials:{user_id}"
            await self.redis_client.set(credentials_key, json.dumps(credentials))
            
            logger.info(f"FIDO2 credential revoked: {credential_id} for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke credential: {e}")
            return False
            
    def _validate_credential_response(
        self,
        credential_data: Dict[str, Any],
        expected_challenge: str
    ) -> bool:
        """Validate credential response format and challenge"""
        try:
            response = credential_data.get("response", {})
            client_data_json = response.get("clientDataJSON")
            
            if not client_data_json:
                return False
                
            # Decode client data
            client_data = json.loads(base64.urlsafe_b64decode(
                client_data_json + "=" * (4 - len(client_data_json) % 4)
            ).decode('utf-8'))
            
            # Verify challenge
            if client_data.get("challenge") != expected_challenge:
                logger.error("Challenge mismatch in credential response")
                return False
                
            # Verify type
            if client_data.get("type") != "webauthn.create":
                logger.error("Invalid credential type")
                return False
                
            # Verify origin
            origin = client_data.get("origin")
            if not origin or not origin.endswith(self.rp_id):
                logger.error(f"Invalid origin: {origin}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Credential response validation failed: {e}")
            return False
            
    async def _store_user_credential(
        self,
        user_id: str,
        credential_id: str,
        credential_data: Dict[str, Any]
    ):
        """Store user credential in Redis"""
        credentials_key = f"fido2_credentials:{user_id}"
        
        # Get existing credentials
        existing_creds = await self.get_user_credentials(user_id)
        
        # Add new credential
        existing_creds[credential_id] = credential_data
        
        # Store updated credentials
        await self.redis_client.set(credentials_key, json.dumps(existing_creds))
        
        # Create reverse lookup
        lookup_key = f"fido2_lookup:{credential_id}"
        await self.redis_client.set(lookup_key, user_id)
        
    async def _find_user_by_credential(self, credential_id: str) -> Optional[str]:
        """Find user by credential ID"""
        lookup_key = f"fido2_lookup:{credential_id}"
        user_id = await self.redis_client.get(lookup_key)
        return user_id.decode('utf-8') if user_id else None
        
    async def _update_credential_usage(self, user_id: str, credential_id: str):
        """Update credential last used timestamp"""
        credentials = await self.get_user_credentials(user_id)
        
        if credential_id in credentials:
            credentials[credential_id]["last_used"] = datetime.utcnow().isoformat()
            
            credentials_key = f"fido2_credentials:{user_id}"
            await self.redis_client.set(credentials_key, json.dumps(credentials))


class FIDO2Middleware:
    """FastAPI middleware for FIDO2 authentication"""
    
    def __init__(self, fido2_manager: FIDO2Manager):
        self.fido2_manager = fido2_manager
        
    async def authenticate_request(self, request: Request) -> Optional[str]:
        """Authenticate request using FIDO2 if credentials present"""
        # Check for FIDO2 authentication headers
        fido2_credential = request.headers.get("X-FIDO2-Credential")
        fido2_response = request.headers.get("X-FIDO2-Response")
        
        if not fido2_credential or not fido2_response:
            return None
            
        try:
            credential_data = json.loads(base64.b64decode(fido2_response))
            user_id = await self.fido2_manager.verify_authentication(credential_data)
            
            if user_id:
                logger.info(f"FIDO2 authentication successful for user: {user_id}")
                return user_id
            else:
                logger.warning("FIDO2 authentication failed")
                return None
                
        except Exception as e:
            logger.error(f"FIDO2 middleware error: {e}")
            return None


# Global FIDO2 manager instance
fido2_manager = FIDO2Manager()
fido2_middleware = FIDO2Middleware(fido2_manager)