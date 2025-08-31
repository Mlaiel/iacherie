"""Verification Manager - Identity and creator verification system.

Handles comprehensive verification processes including identity verification,
creator authenticity, social media validation, and business verification.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
import logging
from enum import Enum
import base64
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator, EmailStr

from ...core.database import get_db
from ...core.exceptions import (
    VerificationNotFoundError,
    VerificationServiceError,
    InvalidDocumentError
)
from ...models.verification import (
    IdentityVerification, VerificationStatus, VerificationType, 
    DocumentType, SocialVerification
)
from ...services.verification.document import DocumentVerificationService
from ...services.verification.social_media import SocialMediaVerificationService
from ...services.verification.ai_detection import AIDetectionService
from ...services.storage.document import DocumentStorageService
from ...services.notification.email import EmailService
from ...utils.image_processing import ImageProcessor
from ...utils.encryption import EncryptionUtils


logger = logging.getLogger(__name__)


class VerificationLevel(str, Enum):
    """Verification levels for creators."""    UNVERIFIED = "unverified"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    IDENTITY_VERIFIED = "identity_verified"
    CREATOR_VERIFIED = "creator_verified"
    BUSINESS_VERIFIED = "business_verified"
    PREMIUM_VERIFIED = "premium_verified"


class DocumentSubmissionData(BaseModel):
    """Document submission data for identity verification."""    document_type: DocumentType
    front_image: str  # Base64 encoded image
    back_image: Optional[str] = None  # For documents with back side
    selfie_image: str  # Selfie for comparison
    document_number: Optional[str] = None
    expiry_date: Optional[str] = None
    issuing_country: str
    
    @validator('front_image', 'back_image', 'selfie_image')
    def validate_base64_image(cls, v):
        if v:
            try:
                base64.b64decode(v)
                return v
            except Exception:
                raise ValueError('Invalid base64 image format')
        return v


class SocialMediaVerificationData(BaseModel):
    """Social media account verification data."""    platform: str  # instagram, youtube, tiktok, twitter, etc.
    username: str
    profile_url: str
    follower_count: Optional[int] = None
    verification_post_id: Optional[str] = None  # For post-based verification
    
    @validator('platform')
    def validate_platform(cls, v):
        allowed_platforms = [
            'instagram', 'youtube', 'tiktok', 'twitter', 
            'facebook', 'linkedin', 'twitch', 'spotify'
        ]
        if v.lower() not in allowed_platforms:
            raise ValueError(f'Platform must be one of: {", ".join(allowed_platforms)}')
        return v.lower()


class BusinessVerificationData(BaseModel):
    """Business verification data."""    business_name: str
    business_type: str  # sole_proprietorship, llc, corporation, etc.
    tax_id: str
    business_address: Dict[str, str]
    business_registration_document: str  # Base64 encoded
    tax_document: Optional[str] = None  # Base64 encoded
    
    @validator('business_name')
    def validate_business_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Business name must be at least 2 characters')
        return v.strip()


class VerificationManager:
    """    Comprehensive verification system for content creators.
    
    Features:
    - Multi-level identity verification
    - Document verification with AI validation
    - Social media account verification
    - Creator authenticity checks
    - Business verification for commercial accounts
    - Fraud detection and prevention
    - Automated verification workflows
    """    
    def __init__(
        self,
        db: Session,
        document_verification: DocumentVerificationService,
        social_verification: SocialMediaVerificationService,
        ai_detection: AIDetectionService,
        document_storage: DocumentStorageService,
        email_service: EmailService
    ):
        self.db = db
        self.document_verification = document_verification
        self.social_verification = social_verification
        self.ai_detection = ai_detection
        self.document_storage = document_storage
        self.email_service = email_service
        self.image_processor = ImageProcessor()
        self.encryption_utils = EncryptionUtils()
        
    async def submit_identity_verification(
        self,
        client_id: UUID,
        document_data: DocumentSubmissionData
    ) -> Dict[str, Any]:
        """        Submit identity documents for verification.
        
        Args:
            client_id: Client identifier
            document_data: Document submission data
            
        Returns:
            Verification submission result
            
        Raises:
            InvalidDocumentError: If document format is invalid
        """        try:
            # Check for existing pending verification
            existing_verification = self.db.query(IdentityVerification).filter(
                IdentityVerification.client_id == client_id,
                IdentityVerification.status == VerificationStatus.PENDING
            ).first()
            
            if existing_verification:
                raise VerificationServiceError("Verification already in progress")
                
            # Decode and validate images
            front_image = base64.b64decode(document_data.front_image)
            selfie_image = base64.b64decode(document_data.selfie_image)
            back_image = base64.b64decode(document_data.back_image) if document_data.back_image else None
            
            # Validate image quality and format
            front_validation = await self.image_processor.validate_document_image(front_image)
            selfie_validation = await self.image_processor.validate_selfie_image(selfie_image)
            
            if not front_validation['valid'] or not selfie_validation['valid']:
                raise InvalidDocumentError("Image quality insufficient for verification")
                
            # Store encrypted documents
            verification_id = uuid4()
            
            front_path = await self._store_encrypted_document(
                verification_id, "front", front_image
            )
            selfie_path = await self._store_encrypted_document(
                verification_id, "selfie", selfie_image
            )
            back_path = None
            if back_image:
                back_path = await self._store_encrypted_document(
                    verification_id, "back", back_image
                )
                
            # Create verification record
            verification = IdentityVerification(
                id=verification_id,
                client_id=client_id,
                verification_type=VerificationType.IDENTITY,
                document_type=document_data.document_type,
                status=VerificationStatus.PENDING,
                document_front_path=front_path,
                document_back_path=back_path,
                selfie_path=selfie_path,
                document_number_hash=self._hash_sensitive_data(document_data.document_number) 
                    if document_data.document_number else None,
                expiry_date=datetime.fromisoformat(document_data.expiry_date) 
                    if document_data.expiry_date else None,
                issuing_country=document_data.issuing_country,
                submitted_at=datetime.utcnow()
            )
            
            self.db.add(verification)
            self.db.commit()
            self.db.refresh(verification)
            
            # Start automated verification process
            verification_task = await self._start_document_verification_process(verification)
            
            # Send confirmation email
            await self.email_service.send_verification_submitted_email(
                verification.client.email,
                verification.client.first_name,
                "Identity Verification"
            )
            
            logger.info(f"Identity verification submitted for client: {client_id}")
            
            return {
                "verification_id": str(verification.id),
                "status": verification.status.value,
                "estimated_completion": self._estimate_verification_time(),
                "required_documents": self._get_required_documents(document_data.document_type)
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error submitting identity verification: {e}")
            raise VerificationServiceError("Failed to submit verification") from e
            
    async def submit_social_media_verification(
        self,
        client_id: UUID,
        social_data: SocialMediaVerificationData
    ) -> Dict[str, Any]:
        """        Submit social media account for verification.
        
        Args:
            client_id: Client identifier
            social_data: Social media verification data
            
        Returns:
            Social verification result
        """        try:
            # Check for existing verification for this platform
            existing_verification = self.db.query(SocialVerification).filter(
                SocialVerification.client_id == client_id,
                SocialVerification.platform == social_data.platform,
                SocialVerification.status.in_([
                    VerificationStatus.PENDING,
                    VerificationStatus.APPROVED
                ])
            ).first()
            
            if existing_verification:
                if existing_verification.status == VerificationStatus.APPROVED:
                    raise VerificationServiceError(f"Already verified on {social_data.platform}")
                else:
                    raise VerificationServiceError(f"Verification pending for {social_data.platform}")
                    
            # Validate social media account
            account_validation = await self.social_verification.validate_account(
                social_data.platform,
                social_data.username,
                social_data.profile_url
            )
            
            if not account_validation['valid']:
                raise VerificationServiceError(f"Invalid {social_data.platform} account")
                
            # Create social verification record
            social_verification = SocialVerification(
                client_id=client_id,
                platform=social_data.platform,
                username=social_data.username,
                profile_url=social_data.profile_url,
                follower_count=social_data.follower_count or account_validation.get('follower_count', 0),
                verification_post_id=social_data.verification_post_id,
                status=VerificationStatus.PENDING,
                platform_data=account_validation.get('platform_data', {}),
                submitted_at=datetime.utcnow()
            )
            
            self.db.add(social_verification)
            self.db.commit()
            self.db.refresh(social_verification)
            
            # Start verification process
            if social_data.verification_post_id:
                # Post-based verification
                verification_result = await self._verify_social_media_post(social_verification)
            else:
                # Manual verification required
                verification_result = await self._queue_manual_social_verification(social_verification)
                
            logger.info(f"Social media verification submitted for client {client_id}: {social_data.platform}")
            
            return {
                "verification_id": str(social_verification.id),
                "platform": social_data.platform,
                "status": social_verification.status.value,
                "verification_method": "post" if social_data.verification_post_id else "manual",
                "estimated_completion": self._estimate_social_verification_time()
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error submitting social verification: {e}")
            raise VerificationServiceError("Failed to submit social verification") from e
            
    async def submit_business_verification(
        self,
        client_id: UUID,
        business_data: BusinessVerificationData
    ) -> Dict[str, Any]:
        """        Submit business documents for verification.
        
        Args:
            client_id: Client identifier
            business_data: Business verification data
            
        Returns:
            Business verification result
        """        try:
            # Check for existing business verification
            existing_verification = self.db.query(IdentityVerification).filter(
                IdentityVerification.client_id == client_id,
                IdentityVerification.verification_type == VerificationType.BUSINESS,
                IdentityVerification.status == VerificationStatus.PENDING
            ).first()
            
            if existing_verification:
                raise VerificationServiceError("Business verification already in progress")
                
            # Decode and validate business documents
            registration_doc = base64.b64decode(business_data.business_registration_document)
            tax_doc = base64.b64decode(business_data.tax_document) if business_data.tax_document else None
            
            # Store encrypted business documents
            verification_id = uuid4()
            
            registration_path = await self._store_encrypted_document(
                verification_id, "business_registration", registration_doc
            )
            tax_path = None
            if tax_doc:
                tax_path = await self._store_encrypted_document(
                    verification_id, "tax_document", tax_doc
                )
                
            # Create business verification record
            verification = IdentityVerification(
                id=verification_id,
                client_id=client_id,
                verification_type=VerificationType.BUSINESS,
                status=VerificationStatus.PENDING,
                business_name=business_data.business_name,
                business_type=business_data.business_type,
                tax_id_hash=self._hash_sensitive_data(business_data.tax_id),
                business_address=business_data.business_address,
                document_front_path=registration_path,
                document_back_path=tax_path,
                submitted_at=datetime.utcnow()
            )
            
            self.db.add(verification)
            self.db.commit()
            self.db.refresh(verification)
            
            # Start business verification process
            await self._start_business_verification_process(verification)
            
            # Send confirmation email
            await self.email_service.send_verification_submitted_email(
                verification.client.email,
                verification.client.first_name,
                "Business Verification"
            )
            
            logger.info(f"Business verification submitted for client: {client_id}")
            
            return {
                "verification_id": str(verification.id),
                "business_name": business_data.business_name,
                "status": verification.status.value,
                "estimated_completion": self._estimate_business_verification_time()
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error submitting business verification: {e}")
            raise VerificationServiceError("Failed to submit business verification") from e
            
    async def get_verification_status(
        self,
        client_id: UUID,
        verification_type: Optional[VerificationType] = None
    ) -> Dict[str, Any]:
        """        Get verification status for client.
        
        Args:
            client_id: Client identifier
            verification_type: Optional specific verification type
            
        Returns:
            Comprehensive verification status
        """        try:
            # Get all verifications for client
            query = self.db.query(IdentityVerification).filter(
                IdentityVerification.client_id == client_id
            )
            
            if verification_type:
                query = query.filter(IdentityVerification.verification_type == verification_type)
                
            verifications = query.order_by(IdentityVerification.created_at.desc()).all()
            
            # Get social verifications
            social_verifications = self.db.query(SocialVerification).filter(
                SocialVerification.client_id == client_id
            ).all()
            
            # Calculate overall verification level
            verification_level = await self._calculate_verification_level(
                client_id, verifications, social_verifications
            )
            
            return {
                "verification_level": verification_level.value,
                "identity_verification": self._format_verification_data(
                    next((v for v in verifications if v.verification_type == VerificationType.IDENTITY), None)
                ),
                "business_verification": self._format_verification_data(
                    next((v for v in verifications if v.verification_type == VerificationType.BUSINESS), None)
                ),
                "social_verifications": [
                    self._format_social_verification_data(sv) for sv in social_verifications
                ],
                "verification_badges": await self._get_verification_badges(client_id),
                "next_steps": await self._get_verification_next_steps(verification_level)
            }
            
        except Exception as e:
            logger.error(f"Error getting verification status: {e}")
            raise VerificationServiceError("Failed to retrieve verification status") from e
            
    async def approve_verification(
        self,
        verification_id: UUID,
        admin_id: UUID,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Approve pending verification (admin function).
        
        Args:
            verification_id: Verification identifier
            admin_id: Admin approving the verification
            notes: Optional approval notes
            
        Returns:
            Approval result
        """        try:
            verification = self.db.query(IdentityVerification).filter(
                IdentityVerification.id == verification_id
            ).first()
            
            if not verification:
                raise VerificationNotFoundError(f"Verification not found: {verification_id}")
                
            if verification.status != VerificationStatus.PENDING:
                raise VerificationServiceError("Only pending verifications can be approved")
                
            # Update verification status
            verification.status = VerificationStatus.APPROVED
            verification.approved_at = datetime.utcnow()
            verification.approved_by_admin_id = admin_id
            verification.admin_notes = notes
            
            self.db.commit()
            
            # Send approval notification
            await self.email_service.send_verification_approved_email(
                verification.client.email,
                verification.client.first_name,
                verification.verification_type.value
            )
            
            # Update client verification level
            await self._update_client_verification_level(verification.client_id)
            
            logger.info(f"Verification approved: {verification_id} by admin: {admin_id}")
            
            return {
                "success": True,
                "verification_id": str(verification.id),
                "status": verification.status.value,
                "approved_at": verification.approved_at.isoformat()
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error approving verification: {e}")
            raise VerificationServiceError("Failed to approve verification") from e
            
    async def reject_verification(
        self,
        verification_id: UUID,
        admin_id: UUID,
        rejection_reason: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Reject pending verification (admin function).
        
        Args:
            verification_id: Verification identifier
            admin_id: Admin rejecting the verification
            rejection_reason: Reason for rejection
            notes: Optional rejection notes
            
        Returns:
            Rejection result
        """        try:
            verification = self.db.query(IdentityVerification).filter(
                IdentityVerification.id == verification_id
            ).first()
            
            if not verification:
                raise VerificationNotFoundError(f"Verification not found: {verification_id}")
                
            if verification.status != VerificationStatus.PENDING:
                raise VerificationServiceError("Only pending verifications can be rejected")
                
            # Update verification status
            verification.status = VerificationStatus.REJECTED
            verification.rejected_at = datetime.utcnow()
            verification.rejected_by_admin_id = admin_id
            verification.rejection_reason = rejection_reason
            verification.admin_notes = notes
            
            self.db.commit()
            
            # Send rejection notification
            await self.email_service.send_verification_rejected_email(
                verification.client.email,
                verification.client.first_name,
                verification.verification_type.value,
                rejection_reason
            )
            
            logger.info(f"Verification rejected: {verification_id} by admin: {admin_id}")
            
            return {
                "success": True,
                "verification_id": str(verification.id),
                "status": verification.status.value,
                "rejection_reason": rejection_reason,
                "rejected_at": verification.rejected_at.isoformat()
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error rejecting verification: {e}")
            raise VerificationServiceError("Failed to reject verification") from e
            
    async def _store_encrypted_document(
        self,
        verification_id: UUID,
        document_type: str,
        document_data: bytes
    ) -> str:
        """Store document with encryption."""        encrypted_data = self.encryption_utils.encrypt_data(document_data)
        storage_path = f"verifications/{verification_id}/{document_type}.enc"
        
        upload_result = await self.document_storage.upload_encrypted_document(
            encrypted_data, storage_path
        )
        
        if not upload_result.get('success'):
            raise VerificationServiceError("Failed to store verification document")
            
        return storage_path
        
    def _hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage."""        return hashlib.sha256(data.encode()).hexdigest()
        
    def _estimate_verification_time(self) -> str:
        """Estimate identity verification completion time."""        return "2-5 business days"
        
    def _estimate_social_verification_time(self) -> str:
        """Estimate social media verification completion time."""        return "1-3 business days"
        
    def _estimate_business_verification_time(self) -> str:
        """Estimate business verification completion time."""        return "5-10 business days"
        
    def _get_required_documents(self, document_type: DocumentType) -> List[str]:
        """Get list of required documents for verification type."""        requirements = {
            DocumentType.PASSPORT: ["passport_front", "selfie"],
            DocumentType.DRIVERS_LICENSE: ["license_front", "license_back", "selfie"],
            DocumentType.NATIONAL_ID: ["id_front", "id_back", "selfie"]
        }
        return requirements.get(document_type, ["document", "selfie"])
        
    async def _calculate_verification_level(
        self,
        client_id: UUID,
        verifications: List[IdentityVerification],
        social_verifications: List[SocialVerification]
    ) -> VerificationLevel:
        """Calculate overall verification level for client."""        has_identity = any(
            v.status == VerificationStatus.APPROVED 
            and v.verification_type == VerificationType.IDENTITY 
            for v in verifications
        )
        
        has_business = any(
            v.status == VerificationStatus.APPROVED 
            and v.verification_type == VerificationType.BUSINESS 
            for v in verifications
        )
        
        approved_socials = len([
            sv for sv in social_verifications 
            if sv.status == VerificationStatus.APPROVED
        ])
        
        if has_business and has_identity and approved_socials >= 3:
            return VerificationLevel.PREMIUM_VERIFIED
        elif has_business:
            return VerificationLevel.BUSINESS_VERIFIED
        elif has_identity and approved_socials >= 2:
            return VerificationLevel.CREATOR_VERIFIED
        elif has_identity:
            return VerificationLevel.IDENTITY_VERIFIED
        elif approved_socials >= 1:
            return VerificationLevel.PHONE_VERIFIED  # Assuming social verification implies phone
        else:
            return VerificationLevel.EMAIL_VERIFIED  # Default for registered users
            
    def _format_verification_data(self, verification: Optional[IdentityVerification]) -> Optional[Dict[str, Any]]:
        """Format verification data for API response."""        if not verification:
            return None
            
        return {
            "id": str(verification.id),
            "type": verification.verification_type.value,
            "status": verification.status.value,
            "submitted_at": verification.submitted_at.isoformat(),
            "approved_at": verification.approved_at.isoformat() if verification.approved_at else None,
            "rejected_at": verification.rejected_at.isoformat() if verification.rejected_at else None,
            "rejection_reason": verification.rejection_reason,
            "business_name": verification.business_name,
            "issuing_country": verification.issuing_country
        }
        
    def _format_social_verification_data(self, verification: SocialVerification) -> Dict[str, Any]:
        """Format social verification data for API response."""        return {
            "id": str(verification.id),
            "platform": verification.platform,
            "username": verification.username,
            "follower_count": verification.follower_count,
            "status": verification.status.value,
            "submitted_at": verification.submitted_at.isoformat(),
            "approved_at": verification.approved_at.isoformat() if verification.approved_at else None
        }
        
    async def _get_verification_badges(self, client_id: UUID) -> List[str]:
        """Get verification badges for client."""        # Implementation would return list of earned badges
        return []
        
    async def _get_verification_next_steps(self, current_level: VerificationLevel) -> List[str]:
        """Get next steps for improving verification level."""        next_steps = {
            VerificationLevel.EMAIL_VERIFIED: [
                "Complete identity verification",
                "Verify social media accounts"
            ],
            VerificationLevel.IDENTITY_VERIFIED: [
                "Verify social media accounts",
                "Consider business verification"
            ],
            VerificationLevel.CREATOR_VERIFIED: [
                "Submit business verification for commercial features"
            ]
        }
        return next_steps.get(current_level, [])
        
    async def _start_document_verification_process(self, verification: IdentityVerification) -> Dict[str, Any]:
        """Start automated document verification process."""        # Implementation would start AI-powered document verification
        return {"status": "started"}
        
    async def _start_business_verification_process(self, verification: IdentityVerification) -> Dict[str, Any]:
        """Start business verification process."""        # Implementation would start business document verification
        return {"status": "started"}
        
    async def _verify_social_media_post(self, verification: SocialVerification) -> Dict[str, Any]:
        """Verify social media post for account verification."""        # Implementation would verify social media post
        return {"status": "verified"}
        
    async def _queue_manual_social_verification(self, verification: SocialVerification) -> Dict[str, Any]:
        """Queue social verification for manual review."""        # Implementation would queue for manual review
        return {"status": "queued"}
        
    async def _update_client_verification_level(self, client_id: UUID) -> None:
        """Update client's overall verification level."""        # Implementation would update client verification level
        pass
