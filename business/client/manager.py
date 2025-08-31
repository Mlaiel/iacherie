"""Client Manager - Core client management functionality.

Handles client onboarding, profile management, and core business operations
for multi-format content creators on the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import logging
from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator, EmailStr

from ...core.database import get_db
from ...core.exceptions import (
    ClientNotFoundError,
    DuplicateClientError,
    InvalidClientDataError,
    ClientServiceError
)
from ...models.client import Client, ClientStatus, CreatorType, SubscriptionTier
from ...services.notification.email import EmailService
from ...services.analytics.tracking import AnalyticsTracker
from ...utils.security import SecurityUtils
from ...utils.validation import ValidationUtils


logger = logging.getLogger(__name__)


class ClientType(str, Enum):
    """Client creator types supported by the platform."""    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"


class OnboardingStage(str, Enum):
    """Client onboarding stages."""    REGISTRATION = "registration"
    EMAIL_VERIFICATION = "email_verification"
    PROFILE_SETUP = "profile_setup"
    CONTENT_UPLOAD = "content_upload"
    PAYMENT_SETUP = "payment_setup"
    COMPLETED = "completed"


class ClientRegistrationData(BaseModel):
    """Client registration data validation model."""    email: EmailStr
    password: str
    first_name: str
    last_name: str
    creator_type: ClientType
    country_code: str
    language_preference: str = "en"
    marketing_consent: bool = False
    terms_accepted: bool
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('terms_accepted')
    def validate_terms(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v


class ClientUpdateData(BaseModel):
    """Client profile update data validation model."""    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    country_code: Optional[str] = None
    timezone: Optional[str] = None
    language_preference: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None


class ClientManager:
    """    Core client management system for IA Influencer platform.
    
    Provides comprehensive client lifecycle management including:
    - Registration and onboarding
    - Profile management and updates
    - Authentication and security
    - Subscription and billing integration
    - Analytics and tracking
    """    
    def __init__(
        self,
        db: Session,
        email_service: EmailService,
        analytics_tracker: AnalyticsTracker
    ):
        self.db = db
        self.email_service = email_service
        self.analytics_tracker = analytics_tracker
        self.security_utils = SecurityUtils()
        self.validation_utils = ValidationUtils()
        
    async def register_client(
        self,
        registration_data: ClientRegistrationData,
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """        Register a new client on the platform.
        
        Args:
            registration_data: Validated registration information
            ip_address: Client IP address for security
            user_agent: Client user agent for tracking
            
        Returns:
            Dict containing client ID and registration status
            
        Raises:
            DuplicateClientError: If email already exists
            InvalidClientDataError: If registration data is invalid
        """        try:
            # Check if email already exists
            existing_client = self.db.query(Client).filter(
                Client.email == registration_data.email.lower()
            ).first()
            
            if existing_client:
                raise DuplicateClientError(
                    f"Client with email {registration_data.email} already exists"
                )
            
            # Hash password securely
            password_hash = self.security_utils.hash_password(registration_data.password)
            
            # Create new client record
            client = Client(
                email=registration_data.email.lower(),
                password_hash=password_hash,
                first_name=registration_data.first_name.strip(),
                last_name=registration_data.last_name.strip(),
                creator_type=CreatorType(registration_data.creator_type.value),
                country_code=registration_data.country_code.upper(),
                language_preference=registration_data.language_preference,
                marketing_consent=registration_data.marketing_consent,
                terms_accepted_at=datetime.utcnow(),
                status=ClientStatus.PENDING_EMAIL_VERIFICATION,
                onboarding_stage=OnboardingStage.EMAIL_VERIFICATION.value,
                registration_ip=ip_address,
                registration_user_agent=user_agent
            )
            
            self.db.add(client)
            self.db.commit()
            self.db.refresh(client)
            
            # Send verification email
            verification_token = self.security_utils.generate_verification_token(
                client.id, client.email
            )
            
            await self.email_service.send_verification_email(
                client.email,
                client.first_name,
                verification_token
            )
            
            # Track registration event
            await self.analytics_tracker.track_event(
                user_id=str(client.id),
                event_name="client_registered",
                properties={
                    "creator_type": client.creator_type.value,
                    "country": client.country_code,
                    "marketing_consent": client.marketing_consent
                }
            )
            
            logger.info(f"Client registered successfully: {client.id}")
            
            return {
                "client_id": str(client.id),
                "email": client.email,
                "status": "registration_successful",
                "verification_required": True,
                "onboarding_stage": client.onboarding_stage
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during client registration: {e}")
            raise ClientServiceError("Failed to register client") from e
            
    async def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """        Verify client email address using verification token.
        
        Args:
            verification_token: JWT verification token
            
        Returns:
            Dict containing verification status
            
        Raises:
            ClientNotFoundError: If token is invalid or client not found
        """        try:
            # Decode and validate token
            payload = self.security_utils.decode_verification_token(verification_token)
            client_id = UUID(payload['client_id'])
            
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise ClientNotFoundError(f"Client not found: {client_id}")
                
            # Update client verification status
            client.email_verified_at = datetime.utcnow()
            client.status = ClientStatus.ACTIVE
            client.onboarding_stage = OnboardingStage.PROFILE_SETUP.value
            
            self.db.commit()
            
            # Send welcome email
            await self.email_service.send_welcome_email(
                client.email,
                client.first_name,
                client.creator_type.value
            )
            
            # Track verification event
            await self.analytics_tracker.track_event(
                user_id=str(client.id),
                event_name="email_verified",
                properties={"verification_time": datetime.utcnow().isoformat()}
            )
            
            logger.info(f"Email verified for client: {client.id}")
            
            return {
                "client_id": str(client.id),
                "status": "email_verified",
                "onboarding_stage": client.onboarding_stage
            }
            
        except Exception as e:
            logger.error(f"Email verification failed: {e}")
            raise ClientServiceError("Email verification failed") from e
            
    async def get_client_by_id(self, client_id: UUID) -> Optional[Dict[str, Any]]:
        """        Retrieve client information by ID.
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            Client data dictionary or None if not found
        """        try:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if not client:
                return None
                
            return self._format_client_data(client)
            
        except Exception as e:
            logger.error(f"Error retrieving client {client_id}: {e}")
            return None
            
    async def update_client_profile(
        self,
        client_id: UUID,
        update_data: ClientUpdateData
    ) -> Dict[str, Any]:
        """        Update client profile information.
        
        Args:
            client_id: Client identifier
            update_data: Validated update information
            
        Returns:
            Updated client data
            
        Raises:
            ClientNotFoundError: If client doesn't exist
        """        try:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise ClientNotFoundError(f"Client not found: {client_id}")
                
            # Update provided fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(client, field):
                    setattr(client, field, value)
                    
            client.updated_at = datetime.utcnow()
            self.db.commit()
            
            # Track profile update
            await self.analytics_tracker.track_event(
                user_id=str(client.id),
                event_name="profile_updated",
                properties={"updated_fields": list(update_dict.keys())}
            )
            
            logger.info(f"Profile updated for client: {client.id}")
            
            return self._format_client_data(client)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating client profile: {e}")
            raise ClientServiceError("Failed to update profile") from e
            
    async def deactivate_client(
        self,
        client_id: UUID,
        reason: str,
        admin_id: Optional[UUID] = None
    ) -> bool:
        """        Deactivate a client account.
        
        Args:
            client_id: Client identifier
            reason: Deactivation reason
            admin_id: Admin performing the action (if applicable)
            
        Returns:
            True if successful
        """        try:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if not client:
                raise ClientNotFoundError(f"Client not found: {client_id}")
                
            client.status = ClientStatus.DEACTIVATED
            client.deactivated_at = datetime.utcnow()
            client.deactivation_reason = reason
            
            if admin_id:
                client.deactivated_by_admin_id = admin_id
                
            self.db.commit()
            
            # Send deactivation notification
            await self.email_service.send_account_deactivation_email(
                client.email,
                client.first_name,
                reason
            )
            
            # Track deactivation
            await self.analytics_tracker.track_event(
                user_id=str(client.id),
                event_name="account_deactivated",
                properties={
                    "reason": reason,
                    "deactivated_by_admin": admin_id is not None
                }
            )
            
            logger.info(f"Client deactivated: {client.id}, reason: {reason}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating client {client_id}: {e}")
            return False
            
    def _format_client_data(self, client: Client) -> Dict[str, Any]:
        """Format client data for API response."""        return {
            "id": str(client.id),
            "email": client.email,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "display_name": client.display_name,
            "creator_type": client.creator_type.value if client.creator_type else None,
            "status": client.status.value if client.status else None,
            "onboarding_stage": client.onboarding_stage,
            "subscription_tier": client.subscription_tier.value if client.subscription_tier else None,
            "country_code": client.country_code,
            "language_preference": client.language_preference,
            "email_verified": client.email_verified_at is not None,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "last_login_at": client.last_login_at.isoformat() if client.last_login_at else None,
            "profile_completion": self._calculate_profile_completion(client)
        }
        
    def _calculate_profile_completion(self, client: Client) -> int:
        """Calculate profile completion percentage."""        completion_fields = [
            client.first_name,
            client.last_name,
            client.display_name,
            client.bio,
            client.creator_type,
            client.email_verified_at
        ]
        
        completed = sum(1 for field in completion_fields if field)
        return int((completed / len(completion_fields)) * 100)
