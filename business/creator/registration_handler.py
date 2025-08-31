"""Creator Registration Handler - Advanced Registration & Onboarding System

Ultra-sophisticated creator registration and onboarding system with multi-step verification,
KYC compliance, and intelligent onboarding workflows for multi-format content creators.

Business Logic Flow:
Initial Registration → Email Verification → Profile Setup → KYC Verification → 
Platform Integration → Content Preferences → Monetization Setup → Go Live

Project: IA Influencer Agent + Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING:
This code, concept, and intellectual property are exclusively owned by Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED
and will result in immediate legal action under German and International copyright laws.
"""import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import secrets
import hashlib
import json
from pathlib import Path
import re

# Third-party imports
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, validator
import bcrypt
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException
import jwt
from datetime import datetime, timedelta

# Internal imports
from ...core.database import get_db_session
from ...core.config import get_settings
from ...core.security import SecurityManager
from ...core.cache import CacheManager
from ...core.logging import get_logger
from ...core.email import EmailService
from ...core.sms import SMSService
from .profile_manager import (
    CreatorProfileManager, CreatorProfile, CreatorType, 
    VerificationLevel, ProfessionalTier, CreatorPreferences
)

# Configure logging
logger = get_logger(__name__)


class RegistrationStage(Enum):
    """Registration workflow stages"""    INITIATED = "initiated"
    EMAIL_SENT = "email_sent"
    EMAIL_VERIFIED = "email_verified"
    PROFILE_SETUP = "profile_setup"
    PHONE_VERIFICATION = "phone_verification"
    IDENTITY_VERIFICATION = "identity_verification"
    PLATFORM_INTEGRATION = "platform_integration"
    MONETIZATION_SETUP = "monetization_setup"
    COMPLETED = "completed"
    FAILED = "failed"


class KYCStatus(Enum):
    """KYC verification status"""    NOT_STARTED = "not_started"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_ADDITIONAL_INFO = "requires_additional_info"


class OnboardingType(Enum):
    """Onboarding workflow types"""    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    EXPEDITED = "expedited"
    INFLUENCER = "influencer"


@dataclass
class RegistrationData:
    """Registration form data"""    email: str
    username: str
    display_name: str
    password: str
    creator_type: CreatorType
    agree_to_terms: bool = False
    subscribe_to_newsletter: bool = False
    referral_code: Optional[str] = None
    
    # Optional initial data
    bio: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Business information
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    
    # Social media handles
    social_handles: Dict[str, str] = field(default_factory=dict)


@dataclass
class OnboardingProgress:
    """Onboarding progress tracking"""    user_id: str
    creator_id: str
    current_stage: RegistrationStage
    completed_stages: List[str] = field(default_factory=list)
    failed_stages: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    estimated_completion_time: Optional[datetime] = None
    
    # Stage-specific data
    verification_data: Dict[str, Any] = field(default_factory=dict)
    integration_data: Dict[str, Any] = field(default_factory=dict)
    setup_preferences: Dict[str, Any] = field(default_factory=dict)


class RegistrationRequest(BaseModel):
    """Registration request validation model"""    email: EmailStr
    username: str
    display_name: str
    password: str
    creator_type: str
    agree_to_terms: bool
    subscribe_to_newsletter: bool = False
    referral_code: Optional[str] = None
    
    # Optional fields
    bio: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    phone_number: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores and hyphens')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('creator_type')
    def validate_creator_type(cls, v):
        try:
            CreatorType(v)
        except ValueError:
            raise ValueError('Invalid creator type')
        return v
    
    @validator('agree_to_terms')
    def validate_terms_agreement(cls, v):
        if not v:
            raise ValueError('Must agree to terms and conditions')
        return v


class PhoneVerificationRequest(BaseModel):
    """Phone verification request model"""    phone_number: str
    country_code: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v, values):
        try:
            country_code = values.get('country_code', 'US')
            parsed_number = phonenumbers.parse(v, country_code)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            raise ValueError('Invalid phone number format')


class KYCProcessor:
    """    KYC (Know Your Customer) compliance processor
    
    Handles identity verification, document processing, and compliance checks
    for creator monetization and professional features.
    """    
    def __init__(self, security_manager: SecurityManager, cache_manager: CacheManager):
        self.security = security_manager
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        
        # KYC configuration
        self.document_types = {
            'passport', 'drivers_license', 'national_id', 'residence_permit'
        }
        self.max_document_size = 10 * 1024 * 1024  # 10MB
        self.supported_formats = {'jpg', 'jpeg', 'png', 'pdf'}
    
    async def initiate_kyc_verification(
        self,
        creator_id: str,
        verification_level: VerificationLevel,
        documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Initiate KYC verification process
        
        Args:
            creator_id: Creator identifier
            verification_level: Target verification level
            documents: Uploaded verification documents
            
        Returns:
            KYC verification result
        """        try:
            self.logger.info(f"Initiating KYC verification for creator {creator_id}")
            
            # Validate documents
            validation_result = await self._validate_kyc_documents(documents)
            if not validation_result['valid']:
                return {
                    'status': KYCStatus.REJECTED.value,
                    'errors': validation_result['errors'],
                    'verification_id': None
                }
            
            # Create verification record
            verification_id = str(uuid.uuid4())
            verification_data = {
                'verification_id': verification_id,
                'creator_id': creator_id,
                'verification_level': verification_level.value,
                'status': KYCStatus.UNDER_REVIEW.value,
                'submitted_at': datetime.utcnow().isoformat(),
                'documents': documents,
                'validation_results': validation_result
            }
            
            # Store in cache for processing
            await self.cache.set(
                f"kyc_verification:{verification_id}",
                json.dumps(verification_data, default=str),
                ttl=86400 * 7  # 7 days
            )
            
            # In production, this would trigger external KYC service integration
            # For now, we'll simulate the process
            await self._process_kyc_verification(verification_data)
            
            return {
                'status': KYCStatus.UNDER_REVIEW.value,
                'verification_id': verification_id,
                'estimated_completion': '2-5 business days',
                'next_steps': [
                    'Documents are being reviewed',
                    'You will receive an email with the results',
                    'Additional information may be requested'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"KYC verification initiation failed: {e}")
            return {
                'status': KYCStatus.FAILED.value,
                'error': str(e),
                'verification_id': None
            }
    
    async def check_kyc_status(self, verification_id: str) -> Dict[str, Any]:
        """Check KYC verification status"""        try:
            verification_data = await self.cache.get(f"kyc_verification:{verification_id}")
            if not verification_data:
                return {'status': 'not_found'}
            
            data = json.loads(verification_data)
            return {
                'verification_id': verification_id,
                'status': data['status'],
                'submitted_at': data['submitted_at'],
                'last_updated': data.get('last_updated'),
                'completion_percentage': data.get('completion_percentage', 0),
                'next_steps': data.get('next_steps', [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check KYC status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _validate_kyc_documents(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """Validate KYC documents"""        try:
            errors = []
            warnings = []
            
            # Check required documents
            if 'identity_document' not in documents:
                errors.append('Identity document is required')
            
            if 'proof_of_address' not in documents:
                warnings.append('Proof of address recommended but not required')
            
            # Validate each document
            for doc_type, doc_data in documents.items():
                # Check file size
                if doc_data.get('size', 0) > self.max_document_size:
                    errors.append(f'{doc_type}: File size exceeds limit')
                
                # Check format
                file_extension = doc_data.get('filename', '').split('.')[-1].lower()
                if file_extension not in self.supported_formats:
                    errors.append(f'{doc_type}: Unsupported file format')
                
                # Check content type
                if not doc_data.get('content_type', '').startswith(('image/', 'application/pdf')):
                    errors.append(f'{doc_type}: Invalid content type')
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'validated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Document validation failed: {e}")
            return {
                'valid': False,
                'errors': [f'Validation error: {str(e)}'],
                'warnings': []
            }
    
    async def _process_kyc_verification(self, verification_data: Dict[str, Any]) -> None:
        """Process KYC verification (simulated)"""        try:
            # In production, this would integrate with external KYC providers
            # like Jumio, Onfido, or similar services
            
            # Simulate processing delay
            await asyncio.sleep(1)
            
            # Update status to approved (simplified)
            verification_data['status'] = KYCStatus.APPROVED.value
            verification_data['last_updated'] = datetime.utcnow().isoformat()
            verification_data['completion_percentage'] = 100
            verification_data['approved_at'] = datetime.utcnow().isoformat()
            
            # Store updated data
            await self.cache.set(
                f"kyc_verification:{verification_data['verification_id']}",
                json.dumps(verification_data, default=str),
                ttl=86400 * 30  # 30 days
            )
            
        except Exception as e:
            self.logger.error(f"KYC processing failed: {e}")


class OnboardingPipeline:
    """    Intelligent onboarding pipeline for creators
    
    Provides personalized onboarding experiences based on creator type,
    experience level, and business requirements.
    """    
    def __init__(self, profile_manager: CreatorProfileManager, cache_manager: CacheManager):
        self.profile_manager = profile_manager
        self.cache = cache_manager
        self.logger = get_logger(self.__class__.__name__)
        
        # Onboarding configuration
        self.stage_weights = {
            RegistrationStage.EMAIL_VERIFIED: 15,
            RegistrationStage.PROFILE_SETUP: 25,
            RegistrationStage.PHONE_VERIFICATION: 10,
            RegistrationStage.IDENTITY_VERIFICATION: 20,
            RegistrationStage.PLATFORM_INTEGRATION: 20,
            RegistrationStage.MONETIZATION_SETUP: 10
        }
    
    async def create_onboarding_workflow(
        self,
        creator_id: str,
        onboarding_type: OnboardingType = OnboardingType.STANDARD
    ) -> OnboardingProgress:
        """        Create personalized onboarding workflow
        
        Args:
            creator_id: Creator identifier
            onboarding_type: Type of onboarding workflow
            
        Returns:
            OnboardingProgress tracking object
        """        try:
            profile = await self.profile_manager.get_creator_profile(creator_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Creator profile not found"
                )
            
            # Create onboarding progress tracker
            progress = OnboardingProgress(
                user_id=profile.user_id,
                creator_id=creator_id,
                current_stage=RegistrationStage.EMAIL_VERIFIED,
                estimated_completion_time=datetime.utcnow() + timedelta(hours=2)
            )
            
            # Customize workflow based on creator type and onboarding type
            workflow_steps = await self._generate_workflow_steps(profile, onboarding_type)
            progress.setup_preferences = {'workflow_steps': workflow_steps}
            
            # Calculate initial progress
            progress.progress_percentage = await self._calculate_progress_percentage(progress)
            
            # Cache progress
            await self._cache_onboarding_progress(progress)
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Failed to create onboarding workflow: {e}")
            raise
    
    async def update_onboarding_progress(
        self,
        creator_id: str,
        stage: RegistrationStage,
        stage_data: Optional[Dict[str, Any]] = None
    ) -> OnboardingProgress:
        """        Update onboarding progress
        
        Args:
            creator_id: Creator identifier
            stage: Completed stage
            stage_data: Stage-specific data
            
        Returns:
            Updated OnboardingProgress
        """        try:
            # Get current progress
            progress = await self._get_onboarding_progress(creator_id)
            if not progress:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Onboarding progress not found"
                )
            
            # Update progress
            if stage.value not in progress.completed_stages:
                progress.completed_stages.append(stage.value)
            
            # Store stage data
            if stage_data:
                progress.verification_data[stage.value] = stage_data
            
            # Determine next stage
            next_stage = await self._get_next_stage(progress)
            progress.current_stage = next_stage
            
            # Update progress percentage
            progress.progress_percentage = await self._calculate_progress_percentage(progress)
            
            # Update estimated completion time
            remaining_stages = await self._get_remaining_stages(progress)
            if remaining_stages:
                estimated_time = len(remaining_stages) * 30  # 30 minutes per stage
                progress.estimated_completion_time = datetime.utcnow() + timedelta(minutes=estimated_time)
            else:
                progress.current_stage = RegistrationStage.COMPLETED
                progress.progress_percentage = 100.0
            
            # Cache updated progress
            await self._cache_onboarding_progress(progress)
            
            return progress
            
        except Exception as e:
            self.logger.error(f"Failed to update onboarding progress: {e}")
            raise
    
    async def get_onboarding_status(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive onboarding status"""        try:
            progress = await self._get_onboarding_progress(creator_id)
            if not progress:
                return {'status': 'not_found'}
            
            profile = await self.profile_manager.get_creator_profile(creator_id)
            
            return {
                'creator_id': creator_id,
                'current_stage': progress.current_stage.value,
                'progress_percentage': progress.progress_percentage,
                'completed_stages': progress.completed_stages,
                'failed_stages': progress.failed_stages,
                'estimated_completion': progress.estimated_completion_time.isoformat() if progress.estimated_completion_time else None,
                'next_steps': await self._get_next_steps(progress),
                'profile_completion': profile.profile_completion_score if profile else 0.0,
                'can_monetize': await self._check_monetization_eligibility(progress, profile)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get onboarding status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # Private helper methods
    
    async def _generate_workflow_steps(
        self,
        profile: CreatorProfile,
        onboarding_type: OnboardingType
    ) -> List[Dict[str, Any]]:
        """Generate personalized workflow steps"""        steps = [
            {
                'stage': RegistrationStage.PROFILE_SETUP.value,
                'title': 'Complete Your Profile',
                'description': 'Add bio, skills, and showcase your work',
                'required': True,
                'estimated_time': 15
            }
        ]
        
        # Add phone verification for professionals
        if onboarding_type in [OnboardingType.PROFESSIONAL, OnboardingType.ENTERPRISE]:
            steps.append({
                'stage': RegistrationStage.PHONE_VERIFICATION.value,
                'title': 'Verify Phone Number',
                'description': 'Secure your account with phone verification',
                'required': True,
                'estimated_time': 5
            })
        
        # Add KYC for monetization
        if onboarding_type != OnboardingType.STANDARD:
            steps.append({
                'stage': RegistrationStage.IDENTITY_VERIFICATION.value,
                'title': 'Identity Verification',
                'description': 'Complete KYC for monetization features',
                'required': False,
                'estimated_time': 10
            })
        
        # Add platform integration
        steps.append({
            'stage': RegistrationStage.PLATFORM_INTEGRATION.value,
            'title': 'Connect Social Platforms',
            'description': 'Link your social media accounts',
            'required': False,
            'estimated_time': 10
        })
        
        # Add monetization setup
        steps.append({
            'stage': RegistrationStage.MONETIZATION_SETUP.value,
            'title': 'Set Up Monetization',
            'description': 'Configure payment and tax information',
            'required': False,
            'estimated_time': 15
        })
        
        return steps
    
    async def _calculate_progress_percentage(self, progress: OnboardingProgress) -> float:
        """Calculate onboarding progress percentage"""        try:
            total_weight = sum(self.stage_weights.values())
            completed_weight = sum(
                self.stage_weights.get(RegistrationStage(stage), 0)
                for stage in progress.completed_stages
                if stage in [s.value for s in RegistrationStage]
            )
            
            return min((completed_weight / total_weight) * 100, 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate progress percentage: {e}")
            return 0.0
    
    async def _get_next_stage(self, progress: OnboardingProgress) -> RegistrationStage:
        """Determine next onboarding stage"""        stage_order = [
            RegistrationStage.EMAIL_VERIFIED,
            RegistrationStage.PROFILE_SETUP,
            RegistrationStage.PHONE_VERIFICATION,
            RegistrationStage.IDENTITY_VERIFICATION,
            RegistrationStage.PLATFORM_INTEGRATION,
            RegistrationStage.MONETIZATION_SETUP,
            RegistrationStage.COMPLETED
        ]
        
        for stage in stage_order:
            if stage.value not in progress.completed_stages:
                return stage
        
        return RegistrationStage.COMPLETED
    
    async def _get_remaining_stages(self, progress: OnboardingProgress) -> List[RegistrationStage]:
        """Get remaining onboarding stages"""        all_stages = list(RegistrationStage)
        return [stage for stage in all_stages if stage.value not in progress.completed_stages]
    
    async def _get_next_steps(self, progress: OnboardingProgress) -> List[str]:
        """Get next steps for onboarding"""        next_steps = []
        
        if progress.current_stage == RegistrationStage.PROFILE_SETUP:
            next_steps = [
                'Upload a profile picture',
                'Write a compelling bio',
                'Add your skills and expertise',
                'Set your location and timezone'
            ]
        elif progress.current_stage == RegistrationStage.PHONE_VERIFICATION:
            next_steps = [
                'Enter your phone number',
                'Verify the SMS code sent to your phone'
            ]
        elif progress.current_stage == RegistrationStage.IDENTITY_VERIFICATION:
            next_steps = [
                'Upload a government-issued ID',
                'Take a selfie for verification',
                'Provide proof of address (optional)'
            ]
        elif progress.current_stage == RegistrationStage.PLATFORM_INTEGRATION:
            next_steps = [
                'Connect your social media accounts',
                'Sync your content and analytics',
                'Set up cross-platform posting'
            ]
        elif progress.current_stage == RegistrationStage.MONETIZATION_SETUP:
            next_steps = [
                'Add payment method',
                'Complete tax information',
                'Set up revenue sharing preferences'
            ]
        
        return next_steps
    
    async def _check_monetization_eligibility(
        self,
        progress: OnboardingProgress,
        profile: Optional[CreatorProfile]
    ) -> bool:
        """Check if creator is eligible for monetization"""        if not profile:
            return False
        
        # Check minimum requirements
        required_stages = [
            RegistrationStage.EMAIL_VERIFIED.value,
            RegistrationStage.PROFILE_SETUP.value
        ]
        
        # For monetization, identity verification is required
        if RegistrationStage.MONETIZATION_SETUP.value in progress.completed_stages:
            required_stages.append(RegistrationStage.IDENTITY_VERIFICATION.value)
        
        return all(stage in progress.completed_stages for stage in required_stages)
    
    async def _cache_onboarding_progress(self, progress: OnboardingProgress) -> None:
        """Cache onboarding progress"""        try:
            await self.cache.set(
                f"onboarding_progress:{progress.creator_id}",
                json.dumps(asdict(progress), default=str),
                ttl=86400 * 30  # 30 days
            )
        except Exception as e:
            self.logger.warning(f"Failed to cache onboarding progress: {e}")
    
    async def _get_onboarding_progress(self, creator_id: str) -> Optional[OnboardingProgress]:
        """Get cached onboarding progress"""        try:
            cached_data = await self.cache.get(f"onboarding_progress:{creator_id}")
            if cached_data:
                data = json.loads(cached_data)
                data['current_stage'] = RegistrationStage(data['current_stage'])
                return OnboardingProgress(**data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get onboarding progress: {e}")
            return None


class RegistrationWorkflow:
    """    Complete registration workflow orchestrator
    
    Manages the entire creator registration process from initial signup
    to completed onboarding with all verification steps.
    """    
    def __init__(
        self,
        db_session: AsyncSession,
        profile_manager: CreatorProfileManager,
        kyc_processor: KYCProcessor,
        onboarding_pipeline: OnboardingPipeline,
        email_service: EmailService,
        sms_service: SMSService,
        cache_manager: CacheManager,
        security_manager: SecurityManager
    ):
        self.db = db_session
        self.profile_manager = profile_manager
        self.kyc_processor = kyc_processor
        self.onboarding_pipeline = onboarding_pipeline
        self.email_service = email_service
        self.sms_service = sms_service
        self.cache = cache_manager
        self.security = security_manager
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
    
    async def initiate_registration(
        self,
        registration_data: RegistrationRequest
    ) -> Dict[str, Any]:
        """        Initiate creator registration process
        
        Args:
            registration_data: Registration form data
            
        Returns:
            Registration initiation result
        """        try:
            self.logger.info(f"Initiating registration for {registration_data.email}")
            
            # Validate registration data
            await self._validate_registration_data(registration_data)
            
            # Check for existing users
            existing_profile = await self.profile_manager.get_creator_profile(
                registration_data.email, 
                "email"
            )
            if existing_profile:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            
            # Generate user ID and hash password
            user_id = str(uuid.uuid4())
            hashed_password = bcrypt.hashpw(
                registration_data.password.encode('utf-8'), 
                bcrypt.gensalt()
            )
            
            # Create initial profile
            profile = await self.profile_manager.create_creator_profile(
                user_id=user_id,
                email=registration_data.email,
                username=registration_data.username,
                display_name=registration_data.display_name,
                creator_type=CreatorType(registration_data.creator_type),
                initial_data={
                    'bio': registration_data.bio,
                    'location': registration_data.location,
                    'website_url': registration_data.website_url,
                    'phone_number': registration_data.phone_number,
                    'business_name': registration_data.business_name,
                    'social_handles': getattr(registration_data, 'social_handles', {})
                }
            )
            
            # Store password hash (in production, this would be in a separate auth service)
            await self._store_password_hash(user_id, hashed_password)
            
            # Send email verification
            verification_token = await self._generate_email_verification_token(user_id)
            await self.email_service.send_verification_email(
                email=registration_data.email,
                display_name=registration_data.display_name,
                verification_token=verification_token
            )
            
            # Create onboarding workflow
            onboarding_type = self._determine_onboarding_type(registration_data)
            onboarding_progress = await self.onboarding_pipeline.create_onboarding_workflow(
                profile.creator_id,
                onboarding_type
            )
            
            # Process referral if provided
            if registration_data.referral_code:
                await self._process_referral(profile.creator_id, registration_data.referral_code)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'creator_id': profile.creator_id,
                'message': 'Registration initiated successfully',
                'next_steps': [
                    'Check your email for verification link',
                    'Complete your profile setup',
                    'Connect your social media accounts'
                ],
                'onboarding': {
                    'current_stage': onboarding_progress.current_stage.value,
                    'progress_percentage': onboarding_progress.progress_percentage,
                    'estimated_completion': onboarding_progress.estimated_completion_time.isoformat() if onboarding_progress.estimated_completion_time else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Registration initiation failed: {e}")
            await self.db.rollback()
            raise
    
    async def verify_email(
        self,
        verification_token: str
    ) -> Dict[str, Any]:
        """        Verify creator email address
        
        Args:
            verification_token: Email verification token
            
        Returns:
            Verification result
        """        try:
            # Validate and decode token
            token_data = await self._validate_verification_token(verification_token)
            user_id = token_data['user_id']
            
            # Get profile
            profile = await self.profile_manager.get_creator_profile(user_id, "user_id")
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )
            
            # Update verification level
            await self.profile_manager.verify_creator(
                profile.creator_id,
                VerificationLevel.EMAIL_VERIFIED,
                {
                    'email_verified': True,
                    'verified_at': datetime.utcnow().isoformat(),
                    'verification_method': 'email_token'
                }
            )
            
            # Update onboarding progress
            await self.onboarding_pipeline.update_onboarding_progress(
                profile.creator_id,
                RegistrationStage.EMAIL_VERIFIED
            )
            
            # Generate access token for immediate login
            access_token = await self._generate_access_token(user_id, profile.creator_id)
            
            return {
                'status': 'success',
                'message': 'Email verified successfully',
                'access_token': access_token,
                'creator_profile': profile.to_dict(),
                'next_steps': [
                    'Complete your profile setup',
                    'Add skills and expertise',
                    'Upload profile picture'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Email verification failed: {e}")
            raise
    
    async def initiate_phone_verification(
        self,
        creator_id: str,
        phone_request: PhoneVerificationRequest
    ) -> Dict[str, Any]:
        """        Initiate phone number verification
        
        Args:
            creator_id: Creator identifier
            phone_request: Phone verification request
            
        Returns:
            Phone verification initiation result
        """        try:
            # Get profile
            profile = await self.profile_manager.get_creator_profile(creator_id)
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )
            
            # Generate verification code
            verification_code = secrets.randbelow(900000) + 100000  # 6-digit code
            
            # Store verification data
            verification_data = {
                'creator_id': creator_id,
                'phone_number': phone_request.phone_number,
                'verification_code': str(verification_code),
                'created_at': datetime.utcnow().isoformat(),
                'attempts': 0,
                'max_attempts': 3
            }
            
            await self.cache.set(
                f"phone_verification:{creator_id}",
                json.dumps(verification_data),
                ttl=600  # 10 minutes
            )
            
            # Send SMS
            await self.sms_service.send_verification_sms(
                phone_number=phone_request.phone_number,
                verification_code=str(verification_code)
            )
            
            # Update profile with phone number
            await self.profile_manager.update_creator_profile(
                creator_id,
                {'phone_number': phone_request.phone_number}
            )
            
            return {
                'status': 'success',
                'message': 'Verification code sent to your phone',
                'phone_number': phone_request.phone_number[-4:].rjust(len(phone_request.phone_number), '*'),
                'expires_in': 600
            }
            
        except Exception as e:
            self.logger.error(f"Phone verification initiation failed: {e}")
            raise
    
    async def verify_phone(
        self,
        creator_id: str,
        verification_code: str
    ) -> Dict[str, Any]:
        """        Verify phone number with code
        
        Args:
            creator_id: Creator identifier
            verification_code: SMS verification code
            
        Returns:
            Phone verification result
        """        try:
            # Get verification data
            cached_data = await self.cache.get(f"phone_verification:{creator_id}")
            if not cached_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification code expired or not found"
                )
            
            verification_data = json.loads(cached_data)
            
            # Check attempts
            if verification_data['attempts'] >= verification_data['max_attempts']:
                await self.cache.delete(f"phone_verification:{creator_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many verification attempts"
                )
            
            # Verify code
            if verification_code != verification_data['verification_code']:
                verification_data['attempts'] += 1
                await self.cache.set(
                    f"phone_verification:{creator_id}",
                    json.dumps(verification_data),
                    ttl=600
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code"
                )
            
            # Update profile verification
            await self.profile_manager.verify_creator(
                creator_id,
                VerificationLevel.PHONE_VERIFIED,
                {
                    'phone_verified': True,
                    'phone_number': verification_data['phone_number'],
                    'verified_at': datetime.utcnow().isoformat()
                }
            )
            
            # Update onboarding progress
            await self.onboarding_pipeline.update_onboarding_progress(
                creator_id,
                RegistrationStage.PHONE_VERIFICATION
            )
            
            # Clean up verification data
            await self.cache.delete(f"phone_verification:{creator_id}")
            
            return {
                'status': 'success',
                'message': 'Phone number verified successfully',
                'verification_level': VerificationLevel.PHONE_VERIFIED.value
            }
            
        except Exception as e:
            self.logger.error(f"Phone verification failed: {e}")
            raise
    
    # Private helper methods
    
    async def _validate_registration_data(self, data: RegistrationRequest) -> None:
        """Validate registration data"""        # Email validation
        try:
            validate_email(data.email)
        except EmailNotValidError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid email address"
            )
        
        # Username uniqueness check would be done in profile manager
        
        # Password strength is validated by the Pydantic model
        
        # Terms agreement check
        if not data.agree_to_terms:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Must agree to terms and conditions"
            )
    
    def _determine_onboarding_type(self, data: RegistrationRequest) -> OnboardingType:
        """Determine appropriate onboarding type"""        # Business users get professional onboarding
        if data.business_name or data.creator_type in ['influencer', 'enterprise']:
            return OnboardingType.PROFESSIONAL
        
        # High-value creators get expedited onboarding
        if hasattr(data, 'social_handles') and len(getattr(data, 'social_handles', {})) > 2:
            return OnboardingType.EXPEDITED
        
        return OnboardingType.STANDARD
    
    async def _generate_email_verification_token(self, user_id: str) -> str:
        """Generate email verification token"""        payload = {
            'user_id': user_id,
            'type': 'email_verification',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm='HS256')
    
    async def _validate_verification_token(self, token: str) -> Dict[str, Any]:
        """Validate and decode verification token"""        try:
            payload = jwt.decode(token, self.settings.SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
    
    async def _generate_access_token(self, user_id: str, creator_id: str) -> str:
        """Generate access token for authenticated sessions"""        payload = {
            'user_id': user_id,
            'creator_id': creator_id,
            'type': 'access_token',
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.settings.SECRET_KEY, algorithm='HS256')
    
    async def _store_password_hash(self, user_id: str, password_hash: bytes) -> None:
        """Store password hash securely"""        # In production, this would be stored in a separate auth service/table
        await self.cache.set(
            f"password_hash:{user_id}",
            password_hash.decode('utf-8'),
            ttl=86400 * 365  # 1 year
        )
    
    async def _process_referral(self, creator_id: str, referral_code: str) -> None:
        """Process referral code"""        try:
            # In production, this would track referrals and provide rewards
            self.logger.info(f"Processing referral {referral_code} for creator {creator_id}")
        except Exception as e:
            self.logger.warning(f"Failed to process referral: {e}")


class CreatorRegistrationHandler:
    """    Main creator registration handler
    
    Orchestrates all registration-related operations and provides
    a unified interface for creator registration and onboarding.
    """    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize dependent services
        self.settings = get_settings()
        self.cache = CacheManager()
        self.security = SecurityManager()
        self.email_service = EmailService()
        self.sms_service = SMSService()
        
        # Initialize core components
        self.profile_manager = CreatorProfileManager(db_session, self.cache, self.security)
        self.kyc_processor = KYCProcessor(self.security, self.cache)
        self.onboarding_pipeline = OnboardingPipeline(self.profile_manager, self.cache)
        self.registration_workflow = RegistrationWorkflow(
            db_session, self.profile_manager, self.kyc_processor,
            self.onboarding_pipeline, self.email_service, self.sms_service,
            self.cache, self.security
        )
    
    async def register_creator(
        self,
        registration_data: RegistrationRequest
    ) -> Dict[str, Any]:
        """Main creator registration entry point"""        return await self.registration_workflow.initiate_registration(registration_data)
    
    async def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """Verify creator email"""        return await self.registration_workflow.verify_email(verification_token)
    
    async def initiate_phone_verification(
        self,
        creator_id: str,
        phone_request: PhoneVerificationRequest
    ) -> Dict[str, Any]:
        """Initiate phone verification"""        return await self.registration_workflow.initiate_phone_verification(
            creator_id, phone_request
        )
    
    async def verify_phone(
        self,
        creator_id: str,
        verification_code: str
    ) -> Dict[str, Any]:
        """Verify phone number"""        return await self.registration_workflow.verify_phone(creator_id, verification_code)
    
    async def initiate_kyc(
        self,
        creator_id: str,
        verification_level: VerificationLevel,
        documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate KYC verification"""        return await self.kyc_processor.initiate_kyc_verification(
            creator_id, verification_level, documents
        )
    
    async def get_onboarding_status(self, creator_id: str) -> Dict[str, Any]:
        """Get onboarding status"""        return await self.onboarding_pipeline.get_onboarding_status(creator_id)
    
    async def update_onboarding_progress(
        self,
        creator_id: str,
        stage: RegistrationStage,
        stage_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update onboarding progress"""        progress = await self.onboarding_pipeline.update_onboarding_progress(
            creator_id, stage, stage_data
        )
        return {
            'creator_id': creator_id,
            'current_stage': progress.current_stage.value,
            'progress_percentage': progress.progress_percentage,
            'completed_stages': progress.completed_stages
        }


# Export classes for use in other modules
__all__ = [
    'CreatorRegistrationHandler',
    'RegistrationWorkflow',
    'OnboardingPipeline',
    'KYCProcessor',
    'RegistrationRequest',
    'PhoneVerificationRequest',
    'RegistrationStage',
    'KYCStatus',
    'OnboardingType'
]
