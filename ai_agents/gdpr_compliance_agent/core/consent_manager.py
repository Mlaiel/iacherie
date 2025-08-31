"""Consent Manager - Advanced GDPR Consent Management
Sophisticated consent collection, validation, and lifecycle management system

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from fastapi import HTTPException

try:
    from core.database import get_db
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db = DatabaseManager
from ...core.logging import get_logger
from ...models.gdpr_models import ConsentRecord, ConsentPreference, ConsentHistory
from ...schemas.gdpr_schemas import ConsentRequest, ConsentUpdateRequest

logger = get_logger(__name__)

class ConsentStatus(Enum):
    """Consent status types"""    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"
    PENDING = "pending"

class ConsentType(Enum):
    """Types of consent according to GDPR"""    EXPLICIT = "explicit"
    IMPLIED = "implied"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"

class ProcessingPurpose(Enum):
    """Data processing purposes requiring consent"""    CONTENT_PROTECTION = "content_protection"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    RESEARCH = "research"
    SECURITY = "security"
    LEGAL_COMPLIANCE = "legal_compliance"
    THIRD_PARTY_SHARING = "third_party_sharing"

@dataclass
class ConsentDetails:
    """Detailed consent information"""    purpose: ProcessingPurpose
    status: ConsentStatus
    consent_type: ConsentType
    granted_at: Optional[datetime]
    expires_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    legal_basis: str
    consent_text: str
    collection_method: str
    granular_choices: Dict[str, bool]

@dataclass
class ConsentMetrics:
    """Consent collection and management metrics"""    total_consents: int
    granted_consents: int
    denied_consents: int
    withdrawn_consents: int
    expired_consents: int
    consent_rate: float
    withdrawal_rate: float
    average_consent_duration: float

class ConsentManager:
    """    Advanced GDPR Consent Manager
    Manages consent collection, validation, withdrawal, and compliance tracking
    """    
    def __init__(self):
        self._consent_cache: Dict[str, Dict[str, ConsentDetails]] = {}
        self._consent_templates: Dict[ProcessingPurpose, Dict[str, str]] = {}
        
        # Initialize consent templates
        self._initialize_consent_templates()
        
        # Consent validation rules
        self._validation_rules = {
            ProcessingPurpose.CONTENT_PROTECTION: {
                "required_type": ConsentType.EXPLICIT,
                "max_duration_days": 1095,  # 3 years
                "renewal_required": True
            },
            ProcessingPurpose.MARKETING: {
                "required_type": ConsentType.OPT_IN,
                "max_duration_days": 730,   # 2 years
                "renewal_required": True
            },
            ProcessingPurpose.ANALYTICS: {
                "required_type": ConsentType.IMPLIED,
                "max_duration_days": 365,   # 1 year
                "renewal_required": False
            }
        }
        
        logger.info("Consent Manager initialized successfully")
    
    def _initialize_consent_templates(self):
        """Initialize consent text templates for different purposes"""        self._consent_templates = {
            ProcessingPurpose.CONTENT_PROTECTION: {
                "title": "Content Protection Consent",
                "description": "We would like to process your content data to protect your intellectual property rights and detect unauthorized use.",
                "details": "This includes analyzing audio fingerprints, video signatures, image hashes, and metadata to identify potential copyright infringement.",
                "legal_basis": "Consent (Article 6(1)(a) GDPR)",
                "retention_period": "3 years from last use",
                "rights_info": "You can withdraw this consent at any time without affecting the lawfulness of processing based on consent before its withdrawal."
            },
            ProcessingPurpose.ANALYTICS: {
                "title": "Analytics and Performance Consent",
                "description": "We would like to analyze your usage patterns and content performance to provide insights and improve our services.",
                "details": "This includes processing view counts, engagement metrics, user behavior data, and performance statistics.",
                "legal_basis": "Consent (Article 6(1)(a) GDPR) or Legitimate Interest (Article 6(1)(f) GDPR)",
                "retention_period": "1 year from collection",
                "rights_info": "You can withdraw this consent or object to processing based on legitimate interest at any time."
            },
            ProcessingPurpose.MARKETING: {
                "title": "Marketing Communications Consent",
                "description": "We would like to send you marketing communications about our services, features, and promotional offers.",
                "details": "This includes email newsletters, product updates, promotional offers, and personalized recommendations.",
                "legal_basis": "Consent (Article 6(1)(a) GDPR)",
                "retention_period": "2 years from last interaction or until withdrawal",
                "rights_info": "You can withdraw this consent at any time by clicking unsubscribe in any email or updating your preferences."
            },
            ProcessingPurpose.PERSONALIZATION: {
                "title": "Personalization Consent",
                "description": "We would like to personalize your experience by customizing content, recommendations, and interface based on your preferences.",
                "details": "This includes analyzing your usage patterns, preferences, content interactions, and feedback to provide tailored recommendations.",
                "legal_basis": "Consent (Article 6(1)(a) GDPR)",
                "retention_period": "2 years from last use",
                "rights_info": "You can withdraw this consent at any time, though this may affect the personalization of your experience."
            },
            ProcessingPurpose.RESEARCH: {
                "title": "Research and Development Consent",
                "description": "We would like to use your data for research and development to improve AI algorithms and develop new features.",
                "details": "This includes analyzing anonymized usage patterns, content characteristics, and user interactions for research purposes.",
                "legal_basis": "Consent (Article 6(1)(a) GDPR)",
                "retention_period": "5 years for research purposes",
                "rights_info": "You can withdraw this consent at any time. Research data may be anonymized and not linked to your identity."
            },
            ProcessingPurpose.THIRD_PARTY_SHARING: {
                "title": "Third Party Sharing Consent",
                "description": "We would like to share certain data with trusted partners to provide enhanced services and integrations.",
                "details": "This includes sharing necessary data with platform partners, service providers, and integration partners under strict data protection agreements.",
                "legal_basis": "Consent (Article 6(1)(a) GDPR)",
                "retention_period": "According to partner agreements, typically 2 years",
                "rights_info": "You can withdraw this consent at any time, which may affect certain integrated features and services."
            }
        }
    
    async def initialize_consent_framework(self, user_id: str) -> Dict[str, Any]:
        """Initialize consent framework for a new user"""        try:
            consent_records = {}
            
            # Create default consent records for all purposes
            for purpose in ProcessingPurpose:
                consent_id = str(uuid.uuid4())
                
                # Create initial consent record (pending state)
                consent_record = ConsentRecord(
                    consent_id=consent_id,
                    user_id=user_id,
                    purpose=purpose.value,
                    status=ConsentStatus.PENDING.value,
                    consent_type=ConsentType.EXPLICIT.value,
                    legal_basis="consent",
                    consent_text=self._get_consent_text(purpose),
                    collection_method="initialization",
                    created_at=datetime.utcnow(),
                    granular_choices={}
                )
                
                async with get_db() as db:
                    db.add(consent_record)
                    await db.commit()
                    await db.refresh(consent_record)
                
                consent_records[purpose.value] = {
                    "consent_id": consent_id,
                    "status": ConsentStatus.PENDING.value,
                    "template": self._consent_templates[purpose]
                }
            
            logger.info(f"Consent framework initialized for user {user_id}")
            
            return {
                "user_id": user_id,
                "consent_records": consent_records,
                "initialization_date": datetime.utcnow().isoformat(),
                "next_steps": [
                    "Review consent requests",
                    "Provide or deny consent for each purpose",
                    "Configure granular preferences",
                    "Set up consent renewal reminders"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error initializing consent framework: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Consent initialization failed: {str(e)}")
    
    async def collect_consent(
        self, 
        user_id: str, 
        purpose: ProcessingPurpose,
        consent_granted: bool,
        consent_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Collect and record user consent for specific processing purpose"""        try:
            consent_id = str(uuid.uuid4())
            
            # Validate consent collection
            validation_result = await self._validate_consent_collection(
                user_id, purpose, consent_granted, consent_details or {}
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid consent collection: {validation_result['error']}"
                )
            
            # Determine consent status and expiration
            status = ConsentStatus.GRANTED if consent_granted else ConsentStatus.DENIED
            expires_at = None
            
            if consent_granted:
                purpose_rules = self._validation_rules.get(purpose, {})
                max_duration = purpose_rules.get("max_duration_days", 365)
                expires_at = datetime.utcnow() + timedelta(days=max_duration)
            
            # Create consent record
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                purpose=purpose.value,
                status=status.value,
                consent_type=consent_details.get("consent_type", ConsentType.EXPLICIT.value),
                granted_at=datetime.utcnow() if consent_granted else None,
                expires_at=expires_at,
                legal_basis="consent",
                consent_text=self._get_consent_text(purpose),
                collection_method=consent_details.get("collection_method", "explicit_request"),
                granular_choices=consent_details.get("granular_choices", {}),
                ip_address=consent_details.get("ip_address"),
                user_agent=consent_details.get("user_agent"),
                created_at=datetime.utcnow(),
                metadata=consent_details
            )
            
            async with get_db() as db:
                db.add(consent_record)
                await db.commit()
                await db.refresh(consent_record)
            
            # Update consent cache
            await self._update_consent_cache(user_id, purpose, consent_record)
            
            # Create consent history entry
            await self._record_consent_history(
                user_id, consent_id, "consent_collected", 
                {"granted": consent_granted, "purpose": purpose.value}
            )
            
            # Schedule consent renewal reminder if applicable
            if consent_granted and expires_at:
                await self._schedule_consent_renewal_reminder(user_id, consent_id, expires_at)
            
            logger.info(f"Consent collected for user {user_id}, purpose {purpose.value}: {status.value}")
            
            return {
                "consent_id": consent_id,
                "user_id": user_id,
                "purpose": purpose.value,
                "status": status.value,
                "granted_at": consent_record.granted_at.isoformat() if consent_record.granted_at else None,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "legal_basis": "consent",
                "granular_choices": consent_record.granular_choices,
                "next_actions": await self._get_consent_next_actions(user_id, purpose, status)
            }
            
        except Exception as e:
            logger.error(f"Error collecting consent: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Consent collection failed: {str(e)}")
    
    async def verify_consent(self, user_id: str, purpose: str) -> bool:
        """Verify if user has valid consent for processing purpose"""        try:
            # Check cache first
            if user_id in self._consent_cache:
                cached_consent = self._consent_cache[user_id].get(purpose)
                if cached_consent and cached_consent.status == ConsentStatus.GRANTED:
                    # Check expiration
                    if not cached_consent.expires_at or cached_consent.expires_at > datetime.utcnow():
                        return True
            
            # Query database
            async with get_db() as db:
                consent_query = await db.execute(
                    select(ConsentRecord).where(
                        and_(
                            ConsentRecord.user_id == user_id,
                            ConsentRecord.purpose == purpose,
                            ConsentRecord.status == ConsentStatus.GRANTED.value
                        )
                    ).order_by(ConsentRecord.created_at.desc())
                )
                
                consent_record = consent_query.scalar_one_or_none()
                
                if not consent_record:
                    return False
                
                # Check if consent is still valid (not expired)
                if consent_record.expires_at and consent_record.expires_at <= datetime.utcnow():
                    # Mark as expired
                    await self._expire_consent(consent_record.consent_id)
                    return False
                
                # Update cache
                await self._update_consent_cache_from_record(user_id, consent_record)
                
                return True
                
        except Exception as e:
            logger.error(f"Error verifying consent: {str(e)}")
            return False
    
    async def withdraw_consent(
        self, 
        user_id: str, 
        purpose: ProcessingPurpose,
        withdrawal_reason: str = None
    ) -> Dict[str, Any]:
        """Withdraw user consent for specific processing purpose"""        try:
            async with get_db() as db:
                # Find active consent record
                consent_query = await db.execute(
                    select(ConsentRecord).where(
                        and_(
                            ConsentRecord.user_id == user_id,
                            ConsentRecord.purpose == purpose.value,
                            ConsentRecord.status == ConsentStatus.GRANTED.value
                        )
                    ).order_by(ConsentRecord.created_at.desc())
                )
                
                consent_record = consent_query.scalar_one_or_none()
                
                if not consent_record:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No active consent found for purpose {purpose.value}"
                    )
                
                # Update consent status to withdrawn
                consent_record.status = ConsentStatus.WITHDRAWN.value
                consent_record.withdrawn_at = datetime.utcnow()
                consent_record.withdrawal_reason = withdrawal_reason
                
                await db.commit()
                
                # Update cache
                if user_id in self._consent_cache:
                    cached_consent = self._consent_cache[user_id].get(purpose.value)
                    if cached_consent:
                        cached_consent.status = ConsentStatus.WITHDRAWN
                        cached_consent.withdrawn_at = datetime.utcnow()
                
                # Record consent history
                await self._record_consent_history(
                    user_id, consent_record.consent_id, "consent_withdrawn",
                    {"reason": withdrawal_reason, "purpose": purpose.value}
                )
                
                # Trigger data processing stop for this purpose
                await self._trigger_processing_stop(user_id, purpose)
                
                logger.info(f"Consent withdrawn for user {user_id}, purpose {purpose.value}")
                
                return {
                    "consent_id": consent_record.consent_id,
                    "user_id": user_id,
                    "purpose": purpose.value,
                    "status": ConsentStatus.WITHDRAWN.value,
                    "withdrawn_at": consent_record.withdrawn_at.isoformat(),
                    "withdrawal_reason": withdrawal_reason,
                    "impact": await self._assess_withdrawal_impact(user_id, purpose),
                    "next_steps": [
                        "Processing for this purpose will stop immediately",
                        "Related data will be reviewed for retention requirements",
                        "You can re-grant consent at any time"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error withdrawing consent: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Consent withdrawal failed: {str(e)}")
    
    async def update_consent_preferences(
        self, 
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's granular consent preferences"""        try:
            updated_consents = {}
            
            for purpose_str, preference_data in preferences.items():
                try:
                    purpose = ProcessingPurpose(purpose_str)
                except ValueError:
                    logger.warning(f"Invalid processing purpose: {purpose_str}")
                    continue
                
                async with get_db() as db:
                    # Find active consent record
                    consent_query = await db.execute(
                        select(ConsentRecord).where(
                            and_(
                                ConsentRecord.user_id == user_id,
                                ConsentRecord.purpose == purpose.value,
                                ConsentRecord.status.in_([
                                    ConsentStatus.GRANTED.value, 
                                    ConsentStatus.PENDING.value
                                ])
                            )
                        ).order_by(ConsentRecord.created_at.desc())
                    )
                    
                    consent_record = consent_query.scalar_one_or_none()
                    
                    if consent_record:
                        # Update granular choices
                        consent_record.granular_choices.update(preference_data.get("granular_choices", {}))
                        
                        # Update other preferences if provided
                        if "status" in preference_data:
                            new_status = preference_data["status"]
                            if new_status != consent_record.status:
                                consent_record.status = new_status
                                if new_status == ConsentStatus.GRANTED.value:
                                    consent_record.granted_at = datetime.utcnow()
                                elif new_status == ConsentStatus.WITHDRAWN.value:
                                    consent_record.withdrawn_at = datetime.utcnow()
                        
                        await db.commit()
                        
                        updated_consents[purpose.value] = {
                            "consent_id": consent_record.consent_id,
                            "status": consent_record.status,
                            "granular_choices": consent_record.granular_choices
                        }
                        
                        # Record preference change
                        await self._record_consent_history(
                            user_id, consent_record.consent_id, "preferences_updated",
                            {"changes": preference_data}
                        )
            
            # Clear cache to force refresh
            if user_id in self._consent_cache:
                del self._consent_cache[user_id]
            
            logger.info(f"Consent preferences updated for user {user_id}: {len(updated_consents)} purposes")
            
            return {
                "user_id": user_id,
                "updated_consents": updated_consents,
                "update_timestamp": datetime.utcnow().isoformat(),
                "summary": {
                    "total_updated": len(updated_consents),
                    "purposes_updated": list(updated_consents.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating consent preferences: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Preference update failed: {str(e)}")
    
    async def get_consent_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive consent status for user"""        try:
            async with get_db() as db:
                # Get all consent records for user
                consent_query = await db.execute(
                    select(ConsentRecord).where(ConsentRecord.user_id == user_id)
                    .order_by(ConsentRecord.purpose, ConsentRecord.created_at.desc())
                )
                
                all_consents = consent_query.scalars().all()
                
                # Group by purpose (latest record per purpose)
                current_consents = {}
                consent_history = []
                
                for consent in all_consents:
                    if consent.purpose not in current_consents:
                        current_consents[consent.purpose] = {
                            "consent_id": consent.consent_id,
                            "status": consent.status,
                            "consent_type": consent.consent_type,
                            "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                            "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
                            "withdrawn_at": consent.withdrawn_at.isoformat() if consent.withdrawn_at else None,
                            "legal_basis": consent.legal_basis,
                            "granular_choices": consent.granular_choices,
                            "collection_method": consent.collection_method,
                            "is_expired": consent.expires_at and consent.expires_at <= datetime.utcnow() if consent.expires_at else False
                        }
                    
                    consent_history.append({
                        "consent_id": consent.consent_id,
                        "purpose": consent.purpose,
                        "status": consent.status,
                        "timestamp": consent.created_at.isoformat()
                    })
                
                # Calculate consent metrics
                metrics = await self.get_consent_metrics(user_id)
                
                return {
                    "user_id": user_id,
                    "current_consents": current_consents,
                    "consent_history": consent_history[:50],  # Last 50 entries
                    "metrics": metrics,
                    "compliance_status": await self._assess_consent_compliance(current_consents),
                    "recommendations": await self._generate_consent_recommendations(user_id, current_consents)
                }
                
        except Exception as e:
            logger.error(f"Error getting consent status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")
    
    async def get_consent_metrics(self, user_id: str) -> ConsentMetrics:
        """Get detailed consent metrics for user"""        try:
            async with get_db() as db:
                consent_query = await db.execute(
                    select(ConsentRecord).where(ConsentRecord.user_id == user_id)
                )
                
                all_consents = consent_query.scalars().all()
                
                if not all_consents:
                    return ConsentMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0)
                
                # Calculate metrics
                total_consents = len(all_consents)
                granted_consents = len([c for c in all_consents if c.status == ConsentStatus.GRANTED.value])
                denied_consents = len([c for c in all_consents if c.status == ConsentStatus.DENIED.value])
                withdrawn_consents = len([c for c in all_consents if c.status == ConsentStatus.WITHDRAWN.value])
                
                # Check for expired consents
                expired_consents = 0
                for consent in all_consents:
                    if consent.expires_at and consent.expires_at <= datetime.utcnow() and consent.status == ConsentStatus.GRANTED.value:
                        expired_consents += 1
                
                # Calculate rates
                consent_rate = granted_consents / total_consents if total_consents > 0 else 0.0
                withdrawal_rate = withdrawn_consents / granted_consents if granted_consents > 0 else 0.0
                
                # Calculate average consent duration
                durations = []
                for consent in all_consents:
                    if consent.granted_at:
                        end_time = consent.withdrawn_at or datetime.utcnow()
                        duration = (end_time - consent.granted_at).total_seconds() / 86400  # days
                        durations.append(duration)
                
                average_duration = sum(durations) / len(durations) if durations else 0.0
                
                return ConsentMetrics(
                    total_consents=total_consents,
                    granted_consents=granted_consents,
                    denied_consents=denied_consents,
                    withdrawn_consents=withdrawn_consents,
                    expired_consents=expired_consents,
                    consent_rate=round(consent_rate, 3),
                    withdrawal_rate=round(withdrawal_rate, 3),
                    average_consent_duration=round(average_duration, 1)
                )
                
        except Exception as e:
            logger.error(f"Error calculating consent metrics: {str(e)}")
            return ConsentMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0)
    
    async def generate_consent_receipt(self, consent_id: str) -> Dict[str, Any]:
        """Generate GDPR-compliant consent receipt"""        try:
            async with get_db() as db:
                consent_query = await db.execute(
                    select(ConsentRecord).where(ConsentRecord.consent_id == consent_id)
                )
                
                consent_record = consent_query.scalar_one_or_none()
                
                if not consent_record:
                    raise HTTPException(status_code=404, detail="Consent record not found")
                
                # Get consent template
                try:
                    purpose = ProcessingPurpose(consent_record.purpose)
                    template = self._consent_templates[purpose]
                except ValueError:
                    template = {"title": "Data Processing Consent", "description": "Consent for data processing"}
                
                receipt = {
                    "receipt_id": str(uuid.uuid4()),
                    "consent_id": consent_id,
                    "user_id": consent_record.user_id,
                    "timestamp": consent_record.created_at.isoformat(),
                    "consent_details": {
                        "purpose": consent_record.purpose,
                        "status": consent_record.status,
                        "legal_basis": consent_record.legal_basis,
                        "consent_type": consent_record.consent_type,
                        "granted_at": consent_record.granted_at.isoformat() if consent_record.granted_at else None,
                        "expires_at": consent_record.expires_at.isoformat() if consent_record.expires_at else None
                    },
                    "processing_information": {
                        "title": template.get("title", ""),
                        "description": template.get("description", ""),
                        "legal_basis": template.get("legal_basis", ""),
                        "retention_period": template.get("retention_period", ""),
                        "data_controller": {
                            "name": "IA-Influencer Agent",
                            "contact": "privacy@ia-influencer.com",
                            "address": "Privacy Office, IA-Influencer Agent"
                        }
                    },
                    "rights_information": {
                        "withdrawal": "You can withdraw consent at any time",
                        "access": "You can request access to your data",
                        "rectification": "You can request correction of your data",
                        "erasure": "You can request deletion of your data",
                        "portability": "You can request data portability",
                        "complaint": "You can lodge a complaint with supervisory authority"
                    },
                    "granular_choices": consent_record.granular_choices,
                    "collection_context": {
                        "method": consent_record.collection_method,
                        "ip_address": consent_record.ip_address,
                        "user_agent": consent_record.user_agent
                    },
                    "digital_signature": await self._generate_consent_signature(consent_record)
                }
                
                return receipt
                
        except Exception as e:
            logger.error(f"Error generating consent receipt: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Receipt generation failed: {str(e)}")
    
    # Helper methods
    
    def _get_consent_text(self, purpose: ProcessingPurpose) -> str:
        """Get consent text for processing purpose"""        template = self._consent_templates.get(purpose, {})
        return f"{template.get('title', '')}: {template.get('description', '')}"
    
    async def _validate_consent_collection(
        self, 
        user_id: str, 
        purpose: ProcessingPurpose,
        consent_granted: bool, 
        consent_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate consent collection parameters"""        try:
            validation_errors = []
            
            # Check if purpose requires specific consent type
            purpose_rules = self._validation_rules.get(purpose, {})
            required_type = purpose_rules.get("required_type")
            
            provided_type = consent_details.get("consent_type")
            if required_type and provided_type != required_type.value:
                validation_errors.append(f"Purpose {purpose.value} requires {required_type.value} consent")
            
            # Check for required granular choices
            if purpose == ProcessingPurpose.MARKETING:
                granular_choices = consent_details.get("granular_choices", {})
                required_choices = ["email_marketing", "promotional_offers"]
                
                for choice in required_choices:
                    if choice not in granular_choices:
                        validation_errors.append(f"Missing required granular choice: {choice}")
            
            # Check collection method
            valid_methods = [
                "explicit_request", "registration_form", "settings_update", 
                "cookie_banner", "api_request", "initialization"
            ]
            
            collection_method = consent_details.get("collection_method", "explicit_request")
            if collection_method not in valid_methods:
                validation_errors.append(f"Invalid collection method: {collection_method}")
            
            # Check for duplicate active consents
            if consent_granted:
                existing_consent = await self.verify_consent(user_id, purpose.value)
                if existing_consent:
                    validation_errors.append(f"Active consent already exists for purpose {purpose.value}")
            
            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "error": "; ".join(validation_errors) if validation_errors else None
            }
            
        except Exception as e:
            logger.error(f"Error validating consent collection: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def _update_consent_cache(self, user_id: str, purpose: ProcessingPurpose, consent_record: ConsentRecord):
        """Update consent cache with new consent record"""        if user_id not in self._consent_cache:
            self._consent_cache[user_id] = {}
        
        consent_details = ConsentDetails(
            purpose=purpose,
            status=ConsentStatus(consent_record.status),
            consent_type=ConsentType(consent_record.consent_type),
            granted_at=consent_record.granted_at,
            expires_at=consent_record.expires_at,
            withdrawn_at=consent_record.withdrawn_at,
            legal_basis=consent_record.legal_basis,
            consent_text=consent_record.consent_text,
            collection_method=consent_record.collection_method,
            granular_choices=consent_record.granular_choices
        )
        
        self._consent_cache[user_id][purpose.value] = consent_details
    
    async def _update_consent_cache_from_record(self, user_id: str, consent_record: ConsentRecord):
        """Update consent cache from database record"""        try:
            purpose = ProcessingPurpose(consent_record.purpose)
            await self._update_consent_cache(user_id, purpose, consent_record)
        except ValueError:
            logger.warning(f"Invalid purpose in consent record: {consent_record.purpose}")
    
    async def _record_consent_history(
        self, 
        user_id: str, 
        consent_id: str, 
        action: str,
        details: Dict[str, Any]
    ):
        """Record consent history entry"""        try:
            async with get_db() as db:
                history_entry = ConsentHistory(
                    user_id=user_id,
                    consent_id=consent_id,
                    action=action,
                    timestamp=datetime.utcnow(),
                    details=details
                )
                
                db.add(history_entry)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error recording consent history: {str(e)}")
    
    async def _expire_consent(self, consent_id: str):
        """Mark consent as expired"""        try:
            async with get_db() as db:
                await db.execute(
                    update(ConsentRecord)
                    .where(ConsentRecord.consent_id == consent_id)
                    .values(status=ConsentStatus.EXPIRED.value)
                )
                await db.commit()
                
                logger.info(f"Consent {consent_id} marked as expired")
                
        except Exception as e:
            logger.error(f"Error expiring consent: {str(e)}")
    
    async def _schedule_consent_renewal_reminder(
        self, 
        user_id: str, 
        consent_id: str,
        expires_at: datetime
    ):
        """Schedule consent renewal reminder"""        # In production, this would schedule a background task or notification
        reminder_date = expires_at - timedelta(days=30)  # 30 days before expiration
        logger.info(f"Consent renewal reminder scheduled for {user_id} on {reminder_date}")
    
    async def _get_consent_next_actions(
        self, 
        user_id: str, 
        purpose: ProcessingPurpose,
        status: ConsentStatus
    ) -> List[str]:
        """Get recommended next actions after consent collection"""        actions = []
        
        if status == ConsentStatus.GRANTED:
            actions.extend([
                "Data processing can begin for this purpose",
                "Monitor consent expiration date",
                "Ensure processing stays within consent scope"
            ])
        elif status == ConsentStatus.DENIED:
            actions.extend([
                "Data processing is not permitted for this purpose",
                "Consider alternative legal bases if applicable",
                "Consent can be re-requested in the future"
            ])
        
        return actions
    
    async def _trigger_processing_stop(self, user_id: str, purpose: ProcessingPurpose):
        """Trigger immediate stop of data processing for withdrawn consent"""        # In production, this would send signals to all processing systems
        logger.info(f"Processing stop triggered for user {user_id}, purpose {purpose.value}")
    
    async def _assess_withdrawal_impact(self, user_id: str, purpose: ProcessingPurpose) -> List[str]:
        """Assess impact of consent withdrawal on user experience"""        impacts = []
        
        if purpose == ProcessingPurpose.CONTENT_PROTECTION:
            impacts.extend([
                "Content protection monitoring will be disabled",
                "Infringement detection will stop",
                "Existing protection data will be reviewed for deletion"
            ])
        elif purpose == ProcessingPurpose.ANALYTICS:
            impacts.extend([
                "Performance analytics will no longer be collected",
                "Insights and recommendations may be limited",
                "Historical analytics data will be reviewed"
            ])
        elif purpose == ProcessingPurpose.MARKETING:
            impacts.extend([
                "Marketing communications will stop immediately",
                "Email preferences will be updated",
                "Promotional offers will no longer be sent"
            ])
        
        return impacts
    
    async def _assess_consent_compliance(self, current_consents: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall consent compliance status"""        total_purposes = len(ProcessingPurpose)
        granted_consents = len([c for c in current_consents.values() if c["status"] == ConsentStatus.GRANTED.value])
        expired_consents = len([c for c in current_consents.values() if c.get("is_expired", False)])
        
        compliance_score = (granted_consents - expired_consents) / total_purposes if total_purposes > 0 else 0
        
        return {
            "overall_status": "compliant" if compliance_score >= 0.7 else "partial" if compliance_score >= 0.5 else "non_compliant",
            "compliance_score": round(compliance_score, 2),
            "total_purposes": total_purposes,
            "granted_consents": granted_consents,
            "expired_consents": expired_consents,
            "missing_consents": total_purposes - len(current_consents)
        }
    
    async def _generate_consent_recommendations(
        self, 
        user_id: str, 
        current_consents: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate consent management recommendations"""        recommendations = []
        
        # Check for expired consents
        expired_consents = [p for p, c in current_consents.items() if c.get("is_expired", False)]
        if expired_consents:
            recommendations.append({
                "priority": "high",
                "category": "expired_consent",
                "title": "Renew Expired Consents",
                "description": f"Consents for {', '.join(expired_consents)} have expired and need renewal"
            })
        
        # Check for missing essential consents
        essential_purposes = [ProcessingPurpose.CONTENT_PROTECTION, ProcessingPurpose.SECURITY]
        missing_essential = []
        
        for purpose in essential_purposes:
            if purpose.value not in current_consents or current_consents[purpose.value]["status"] != ConsentStatus.GRANTED.value:
                missing_essential.append(purpose.value)
        
        if missing_essential:
            recommendations.append({
                "priority": "medium",
                "category": "missing_consent",
                "title": "Essential Consents Missing",
                "description": f"Consider granting consent for essential services: {', '.join(missing_essential)}"
            })
        
        return recommendations
    
    async def _generate_consent_signature(self, consent_record: ConsentRecord) -> str:
        """Generate digital signature for consent record"""        import hashlib
        
        # Create signature from consent record data
        signature_data = f"{consent_record.consent_id}_{consent_record.user_id}_{consent_record.purpose}_{consent_record.status}_{consent_record.created_at.isoformat()}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return signature
    
    async def process_consent_renewal(self, user_id: str, consent_id: str) -> Dict[str, Any]:
        """Process consent renewal for expiring consents"""        try:
            async with get_db() as db:
                consent_query = await db.execute(
                    select(ConsentRecord).where(ConsentRecord.consent_id == consent_id)
                )
                
                consent_record = consent_query.scalar_one_or_none()
                
                if not consent_record:
                    raise HTTPException(status_code=404, detail="Consent record not found")
                
                if consent_record.user_id != user_id:
                    raise HTTPException(status_code=403, detail="Unauthorized consent access")
                
                # Create new consent record for renewal
                purpose = ProcessingPurpose(consent_record.purpose)
                new_consent_result = await self.collect_consent(
                    user_id=user_id,
                    purpose=purpose,
                    consent_granted=True,
                    consent_details={
                        "consent_type": consent_record.consent_type,
                        "collection_method": "renewal",
                        "granular_choices": consent_record.granular_choices,
                        "previous_consent_id": consent_id
                    }
                )
                
                # Mark old consent as superseded
                consent_record.status = "superseded"
                await db.commit()
                
                logger.info(f"Consent renewed for user {user_id}, purpose {purpose.value}")
                
                return {
                    "renewal_status": "completed",
                    "old_consent_id": consent_id,
                    "new_consent": new_consent_result,
                    "renewal_timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing consent renewal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Consent renewal failed: {str(e)}")

    async def cleanup_expired_consents(self) -> Dict[str, Any]:
        """Clean up expired consents and related data"""        try:
            async with get_db() as db:
                # Find expired consents
                expired_query = await db.execute(
                    select(ConsentRecord).where(
                        and_(
                            ConsentRecord.expires_at <= datetime.utcnow(),
                            ConsentRecord.status == ConsentStatus.GRANTED.value
                        )
                    )
                )
                
                expired_consents = expired_query.scalars().all()
                
                # Mark as expired
                for consent in expired_consents:
                    consent.status = ConsentStatus.EXPIRED.value
                
                await db.commit()
                
                # Clear from cache
                for consent in expired_consents:
                    if consent.user_id in self._consent_cache:
                        if consent.purpose in self._consent_cache[consent.user_id]:
                            del self._consent_cache[consent.user_id][consent.purpose]
                
                logger.info(f"Cleaned up {len(expired_consents)} expired consents")
                
                return {
                    "expired_consents_processed": len(expired_consents),
                    "cleanup_timestamp": datetime.utcnow().isoformat(),
                    "affected_users": list(set([c.user_id for c in expired_consents]))
                }
                
        except Exception as e:
            logger.error(f"Error cleaning up expired consents: {str(e)}")
            raise
