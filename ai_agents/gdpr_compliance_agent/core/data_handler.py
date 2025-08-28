"""
Data Privacy Handler - Advanced Data Privacy Management
Sophisticated data privacy management for GDPR compliance in content protection

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from ...core.database import get_db
from ...core.logging import get_logger
from ...core.security import SecurityManager, EncryptionManager
from ...models.gdpr_models import DataPrivacyRecord, DataCategory, ProcessingActivity

logger = get_logger(__name__)

class DataSensitivity(Enum):
    """Data sensitivity levels for privacy management"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    HIGHLY_SENSITIVE = "highly_sensitive"

class PrivacyTechnique(Enum):
    """Privacy enhancement techniques"""
    ENCRYPTION = "encryption"
    PSEUDONYMIZATION = "pseudonymization"
    ANONYMIZATION = "anonymization"
    DATA_MASKING = "data_masking"
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    SYNTHETIC_DATA = "synthetic_data"

@dataclass
class DataField:
    """Data field privacy configuration"""
    name: str
    data_type: str
    sensitivity: DataSensitivity
    required_techniques: List[PrivacyTechnique]
    retention_period: int
    access_controls: List[str]

@dataclass
class PrivacyProfile:
    """User privacy profile and preferences"""
    user_id: str
    privacy_level: str
    allowed_processing: List[str]
    restricted_techniques: List[str]
    data_minimization_enabled: bool
    anonymization_threshold: float

class DataPrivacyHandler:
    """
    Advanced Data Privacy Handler
    Manages data privacy, classification, and protection techniques
    """
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.encryption_manager = EncryptionManager()
        
        # Privacy technique implementations
        self._technique_handlers = {
            PrivacyTechnique.ENCRYPTION: self._apply_encryption,
            PrivacyTechnique.PSEUDONYMIZATION: self._apply_pseudonymization,
            PrivacyTechnique.ANONYMIZATION: self._apply_anonymization,
            PrivacyTechnique.DATA_MASKING: self._apply_data_masking,
            PrivacyTechnique.DIFFERENTIAL_PRIVACY: self._apply_differential_privacy,
            PrivacyTechnique.SYNTHETIC_DATA: self._generate_synthetic_data
        }
        
        # Data classification rules
        self._classification_rules = self._initialize_classification_rules()
        
        # Privacy profiles cache
        self._privacy_profiles: Dict[str, PrivacyProfile] = {}
        
        logger.info("Data Privacy Handler initialized successfully")
    
    def _initialize_classification_rules(self) -> Dict[str, DataSensitivity]:
        """Initialize data classification rules"""
        return {
            # Personal identifiers
            "user_id": DataSensitivity.CONFIDENTIAL,
            "email": DataSensitivity.CONFIDENTIAL,
            "phone": DataSensitivity.CONFIDENTIAL,
            "ip_address": DataSensitivity.CONFIDENTIAL,
            "device_id": DataSensitivity.CONFIDENTIAL,
            
            # Biometric and content data
            "audio_fingerprint": DataSensitivity.HIGHLY_SENSITIVE,
            "video_fingerprint": DataSensitivity.HIGHLY_SENSITIVE,
            "image_fingerprint": DataSensitivity.HIGHLY_SENSITIVE,
            "voice_pattern": DataSensitivity.HIGHLY_SENSITIVE,
            "facial_features": DataSensitivity.HIGHLY_SENSITIVE,
            
            # Financial data
            "payment_info": DataSensitivity.HIGHLY_SENSITIVE,
            "bank_account": DataSensitivity.HIGHLY_SENSITIVE,
            "revenue_data": DataSensitivity.RESTRICTED,
            
            # Behavioral data
            "usage_patterns": DataSensitivity.CONFIDENTIAL,
            "preferences": DataSensitivity.CONFIDENTIAL,
            "interaction_data": DataSensitivity.INTERNAL,
            
            # Content metadata
            "content_title": DataSensitivity.INTERNAL,
            "content_description": DataSensitivity.INTERNAL,
            "upload_timestamp": DataSensitivity.INTERNAL,
            "file_size": DataSensitivity.PUBLIC,
            
            # Analytics data
            "view_count": DataSensitivity.PUBLIC,
            "engagement_rate": DataSensitivity.INTERNAL,
            "geographic_data": DataSensitivity.CONFIDENTIAL
        }
    
    async def classify_data(self, data_payload: Dict[str, Any]) -> Dict[str, DataField]:
        """Automatically classify data fields based on content and context"""
        try:
            classified_fields = {}
            
            for field_name, field_value in data_payload.items():
                # Determine sensitivity level
                sensitivity = self._classify_field_sensitivity(field_name, field_value)
                
                # Determine required privacy techniques
                required_techniques = self._determine_required_techniques(sensitivity, field_name)
                
                # Calculate retention period
                retention_period = self._calculate_retention_period(field_name, sensitivity)
                
                # Define access controls
                access_controls = self._define_access_controls(sensitivity)
                
                classified_fields[field_name] = DataField(
                    name=field_name,
                    data_type=type(field_value).__name__,
                    sensitivity=sensitivity,
                    required_techniques=required_techniques,
                    retention_period=retention_period,
                    access_controls=access_controls
                )
            
            logger.info(f"Classified {len(classified_fields)} data fields")
            return classified_fields
            
        except Exception as e:
            logger.error(f"Error classifying data: {str(e)}")
            raise
    
    async def apply_privacy_protection(
        self, 
        data_payload: Dict[str, Any], 
        user_id: str,
        processing_context: str = "general"
    ) -> Dict[str, Any]:
        """Apply appropriate privacy protection techniques to data"""
        try:
            # Get user privacy profile
            privacy_profile = await self._get_privacy_profile(user_id)
            
            # Classify data
            classified_data = await self.classify_data(data_payload)
            
            protected_data = {}
            privacy_metadata = {}
            
            for field_name, field_info in classified_data.items():
                original_value = data_payload[field_name]
                
                # Apply required privacy techniques
                protected_value = original_value
                applied_techniques = []
                
                for technique in field_info.required_techniques:
                    if self._should_apply_technique(technique, privacy_profile, processing_context):
                        protected_value = await self._technique_handlers[technique](
                            protected_value, field_name, user_id
                        )
                        applied_techniques.append(technique.value)
                
                protected_data[field_name] = protected_value
                privacy_metadata[field_name] = {
                    "sensitivity": field_info.sensitivity.value,
                    "applied_techniques": applied_techniques,
                    "retention_until": (datetime.utcnow() + timedelta(days=field_info.retention_period)).isoformat(),
                    "access_controls": field_info.access_controls
                }
            
            # Record privacy protection activity
            await self._record_privacy_activity(
                user_id=user_id,
                processing_context=processing_context,
                data_fields=list(classified_data.keys()),
                techniques_applied=list(set([t for metadata in privacy_metadata.values() for t in metadata["applied_techniques"]]))
            )
            
            logger.info(f"Applied privacy protection to {len(protected_data)} fields for user {user_id}")
            
            return {
                "protected_data": protected_data,
                "privacy_metadata": privacy_metadata,
                "protection_summary": {
                    "total_fields": len(protected_data),
                    "highly_sensitive_fields": len([f for f in classified_data.values() if f.sensitivity == DataSensitivity.HIGHLY_SENSITIVE]),
                    "techniques_used": list(set([t for metadata in privacy_metadata.values() for t in metadata["applied_techniques"]]))
                }
            }
            
        except Exception as e:
            logger.error(f"Error applying privacy protection: {str(e)}")
            raise
    
    async def remove_privacy_protection(
        self, 
        protected_data: Dict[str, Any], 
        privacy_metadata: Dict[str, Any],
        user_id: str,
        authorized_user_id: str
    ) -> Dict[str, Any]:
        """Remove privacy protection (decrypt/de-anonymize) for authorized access"""
        try:
            # Verify authorization
            if not await self._verify_access_authorization(user_id, authorized_user_id, privacy_metadata):
                raise PermissionError("Unauthorized access to protected data")
            
            original_data = {}
            
            for field_name, protected_value in protected_data.items():
                field_metadata = privacy_metadata.get(field_name, {})
                applied_techniques = field_metadata.get("applied_techniques", [])
                
                # Reverse applied techniques in reverse order
                restored_value = protected_value
                
                for technique in reversed(applied_techniques):
                    if technique == "encryption":
                        restored_value = await self._decrypt_data(restored_value, field_name, user_id)
                    elif technique == "pseudonymization":
                        restored_value = await self._reverse_pseudonymization(restored_value, field_name, user_id)
                    elif technique == "data_masking":
                        # Data masking is typically irreversible for privacy
                        logger.warning(f"Cannot reverse data masking for field {field_name}")
                        continue
                    # Anonymization and differential privacy are generally irreversible
                
                original_data[field_name] = restored_value
            
            # Log data access
            await self._log_data_access(
                user_id=user_id,
                authorized_user_id=authorized_user_id,
                accessed_fields=list(original_data.keys()),
                access_reason="privacy_protection_removal"
            )
            
            logger.info(f"Privacy protection removed for {len(original_data)} fields")
            return original_data
            
        except Exception as e:
            logger.error(f"Error removing privacy protection: {str(e)}")
            raise
    
    async def validate_data_minimization(
        self, 
        data_payload: Dict[str, Any], 
        processing_purpose: str
    ) -> Dict[str, Any]:
        """Validate and enforce data minimization principles"""
        try:
            # Define necessary fields for each processing purpose
            purpose_field_mapping = {
                "content_protection": [
                    "user_id", "content_id", "fingerprint_data", "upload_timestamp"
                ],
                "analytics": [
                    "user_id", "content_id", "view_count", "engagement_data", "timestamp"
                ],
                "marketing": [
                    "user_id", "preferences", "engagement_data", "demographic_data"
                ],
                "security": [
                    "user_id", "ip_address", "device_id", "access_timestamp", "security_events"
                ],
                "legal_compliance": [
                    "user_id", "legal_basis", "consent_record", "processing_activity"
                ]
            }
            
            necessary_fields = purpose_field_mapping.get(processing_purpose, [])
            
            # Keep only necessary fields
            minimized_data = {}
            removed_fields = []
            
            for field_name, field_value in data_payload.items():
                if field_name in necessary_fields or self._is_field_essential(field_name, processing_purpose):
                    minimized_data[field_name] = field_value
                else:
                    removed_fields.append(field_name)
            
            # Log data minimization activity
            if removed_fields:
                logger.info(f"Data minimization applied: removed {len(removed_fields)} unnecessary fields")
            
            return {
                "minimized_data": minimized_data,
                "removed_fields": removed_fields,
                "minimization_ratio": len(removed_fields) / len(data_payload) if data_payload else 0,
                "compliance_status": "compliant" if removed_fields else "already_minimal"
            }
            
        except Exception as e:
            logger.error(f"Error in data minimization validation: {str(e)}")
            raise
    
    async def assess_privacy_impact(
        self, 
        processing_activity: Dict[str, Any],
        data_subjects_count: int
    ) -> Dict[str, Any]:
        """Conduct Privacy Impact Assessment (PIA)"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Analyze data types and sensitivity
            data_sensitivity_analysis = await self._analyze_data_sensitivity(
                processing_activity.get("data_categories", [])
            )
            
            # Assess processing risks
            processing_risks = await self._assess_processing_risks(processing_activity)
            
            # Evaluate technical and organizational measures
            protection_measures = await self._evaluate_protection_measures(processing_activity)
            
            # Calculate overall privacy risk score
            risk_score = await self._calculate_privacy_risk_score(
                data_sensitivity_analysis,
                processing_risks,
                protection_measures,
                data_subjects_count
            )
            
            # Generate recommendations
            recommendations = await self._generate_privacy_recommendations(
                risk_score, processing_risks, protection_measures
            )
            
            # Determine if DPIA is required
            dpia_required = await self._is_dpia_required(risk_score, processing_activity)
            
            assessment_result = {
                "assessment_id": assessment_id,
                "assessment_date": datetime.utcnow().isoformat(),
                "processing_activity": processing_activity.get("name", "unknown"),
                "data_subjects_count": data_subjects_count,
                "risk_analysis": {
                    "data_sensitivity": data_sensitivity_analysis,
                    "processing_risks": processing_risks,
                    "protection_measures": protection_measures
                },
                "overall_risk_score": risk_score,
                "risk_level": self._categorize_risk_level(risk_score),
                "dpia_required": dpia_required,
                "recommendations": recommendations,
                "compliance_status": "requires_review" if risk_score > 7.0 else "acceptable"
            }
            
            # Record assessment
            await self._record_privacy_assessment(assessment_result)
            
            logger.info(f"Privacy impact assessment completed: {assessment_id} (Risk: {risk_score}/10)")
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in privacy impact assessment: {str(e)}")
            raise
    
    # Privacy technique implementations
    
    async def _apply_encryption(self, data: Any, field_name: str, user_id: str) -> str:
        """Apply encryption to sensitive data"""
        try:
            # Use field-specific encryption key
            encryption_key = await self.encryption_manager.get_field_key(user_id, field_name)
            encrypted_data = await self.encryption_manager.encrypt_data(str(data), encryption_key)
            return encrypted_data
        except Exception as e:
            logger.error(f"Error applying encryption: {str(e)}")
            raise
    
    async def _apply_pseudonymization(self, data: Any, field_name: str, user_id: str) -> str:
        """Apply pseudonymization to identifiable data"""
        try:
            # Generate deterministic pseudonym
            salt = f"{user_id}_{field_name}_salt"
            pseudonym = hashlib.sha256(f"{data}_{salt}".encode()).hexdigest()[:16]
            
            # Store mapping for potential reversal
            await self._store_pseudonym_mapping(user_id, field_name, str(data), pseudonym)
            
            return f"pseudo_{pseudonym}"
        except Exception as e:
            logger.error(f"Error applying pseudonymization: {str(e)}")
            raise
    
    async def _apply_anonymization(self, data: Any, field_name: str, user_id: str) -> str:
        """Apply anonymization (irreversible)"""
        try:
            if isinstance(data, str):
                # For text data, replace with generic placeholder
                if "@" in str(data):  # Email
                    return "user@domain.com"
                elif len(str(data)) > 10:  # Long text
                    return "[ANONYMIZED_TEXT]"
                else:
                    return "[ANONYMIZED]"
            elif isinstance(data, (int, float)):
                # For numeric data, add noise or round
                import random
                noise = random.uniform(-0.1, 0.1) * abs(float(data))
                return round(float(data) + noise, 2)
            else:
                return "[ANONYMIZED]"
        except Exception as e:
            logger.error(f"Error applying anonymization: {str(e)}")
            return "[ANONYMIZED]"
    
    async def _apply_data_masking(self, data: Any, field_name: str, user_id: str) -> str:
        """Apply data masking for display purposes"""
        try:
            data_str = str(data)
            
            if "@" in data_str:  # Email masking
                parts = data_str.split("@")
                masked_user = parts[0][:2] + "*" * (len(parts[0]) - 4) + parts[0][-2:] if len(parts[0]) > 4 else parts[0][:1] + "***"
                return f"{masked_user}@{parts[1]}"
            elif len(data_str) > 8:  # General long string masking
                return data_str[:3] + "*" * (len(data_str) - 6) + data_str[-3:]
            elif len(data_str) > 4:  # Short string masking
                return data_str[:2] + "*" * (len(data_str) - 2)
            else:
                return "*" * len(data_str)
        except Exception as e:
            logger.error(f"Error applying data masking: {str(e)}")
            return "[MASKED]"
    
    async def _apply_differential_privacy(self, data: Any, field_name: str, user_id: str) -> float:
        """Apply differential privacy noise"""
        try:
            if isinstance(data, (int, float)):
                import numpy as np
                
                # Add Laplace noise for differential privacy
                epsilon = 1.0  # Privacy parameter
                sensitivity = 1.0  # Global sensitivity
                
                noise = np.random.laplace(0, sensitivity / epsilon)
                return float(data) + noise
            else:
                logger.warning(f"Differential privacy not applicable to non-numeric data: {field_name}")
                return str(data)
        except Exception as e:
            logger.error(f"Error applying differential privacy: {str(e)}")
            return data
    
    async def _generate_synthetic_data(self, data: Any, field_name: str, user_id: str) -> Any:
        """Generate synthetic data replacement"""
        try:
            # This is a simplified version - in production, use advanced ML models
            import random
            
            if isinstance(data, str):
                if "@" in str(data):  # Email
                    return f"user{random.randint(1000, 9999)}@example.com"
                else:
                    return f"synthetic_{random.randint(1000, 9999)}"
            elif isinstance(data, int):
                return random.randint(max(1, int(data) - 100), int(data) + 100)
            elif isinstance(data, float):
                return round(random.uniform(max(0.1, float(data) - 10), float(data) + 10), 2)
            else:
                return "synthetic_data"
        except Exception as e:
            logger.error(f"Error generating synthetic data: {str(e)}")
            return "synthetic_data"
    
    # Helper methods
    
    def _classify_field_sensitivity(self, field_name: str, field_value: Any) -> DataSensitivity:
        """Classify field sensitivity based on name and content"""
        # Check explicit classification rules
        if field_name in self._classification_rules:
            return self._classification_rules[field_name]
        
        # Content-based classification
        field_str = str(field_value).lower()
        
        # Check for personal identifiers
        if any(pattern in field_str for pattern in ["email", "@", "phone", "ssn", "passport"]):
            return DataSensitivity.CONFIDENTIAL
        
        # Check for financial data
        if any(pattern in field_str for pattern in ["card", "account", "payment", "bank"]):
            return DataSensitivity.HIGHLY_SENSITIVE
        
        # Check for biometric patterns
        if any(pattern in field_name.lower() for pattern in ["fingerprint", "biometric", "face", "voice"]):
            return DataSensitivity.HIGHLY_SENSITIVE
        
        # Default classification
        return DataSensitivity.INTERNAL
    
    def _determine_required_techniques(self, sensitivity: DataSensitivity, field_name: str) -> List[PrivacyTechnique]:
        """Determine required privacy techniques based on sensitivity"""
        techniques = []
        
        if sensitivity == DataSensitivity.HIGHLY_SENSITIVE:
            techniques.extend([
                PrivacyTechnique.ENCRYPTION,
                PrivacyTechnique.PSEUDONYMIZATION
            ])
        elif sensitivity == DataSensitivity.RESTRICTED:
            techniques.extend([
                PrivacyTechnique.ENCRYPTION,
                PrivacyTechnique.DATA_MASKING
            ])
        elif sensitivity == DataSensitivity.CONFIDENTIAL:
            techniques.append(PrivacyTechnique.ENCRYPTION)
        elif sensitivity == DataSensitivity.INTERNAL:
            techniques.append(PrivacyTechnique.DATA_MASKING)
        
        # Add differential privacy for analytics data
        if "analytic" in field_name.lower() or "metric" in field_name.lower():
            techniques.append(PrivacyTechnique.DIFFERENTIAL_PRIVACY)
        
        return techniques
    
    def _calculate_retention_period(self, field_name: str, sensitivity: DataSensitivity) -> int:
        """Calculate data retention period in days"""
        base_periods = {
            DataSensitivity.HIGHLY_SENSITIVE: 1095,  # 3 years
            DataSensitivity.RESTRICTED: 1825,       # 5 years
            DataSensitivity.CONFIDENTIAL: 1095,     # 3 years
            DataSensitivity.INTERNAL: 730,          # 2 years
            DataSensitivity.PUBLIC: 365             # 1 year
        }
        
        return base_periods.get(sensitivity, 365)
    
    def _define_access_controls(self, sensitivity: DataSensitivity) -> List[str]:
        """Define access controls based on sensitivity"""
        controls = ["authentication_required"]
        
        if sensitivity in [DataSensitivity.HIGHLY_SENSITIVE, DataSensitivity.RESTRICTED]:
            controls.extend([
                "authorization_required",
                "audit_logging",
                "two_factor_required",
                "encrypted_transmission"
            ])
        elif sensitivity == DataSensitivity.CONFIDENTIAL:
            controls.extend([
                "authorization_required",
                "audit_logging",
                "encrypted_transmission"
            ])
        elif sensitivity == DataSensitivity.INTERNAL:
            controls.append("audit_logging")
        
        return controls
    
    async def _get_privacy_profile(self, user_id: str) -> PrivacyProfile:
        """Get or create user privacy profile"""
        if user_id not in self._privacy_profiles:
            # Load from database or create default
            self._privacy_profiles[user_id] = PrivacyProfile(
                user_id=user_id,
                privacy_level="standard",
                allowed_processing=["content_protection", "analytics"],
                restricted_techniques=[],
                data_minimization_enabled=True,
                anonymization_threshold=0.8
            )
        
        return self._privacy_profiles[user_id]
    
    def _should_apply_technique(
        self, 
        technique: PrivacyTechnique, 
        privacy_profile: PrivacyProfile,
        context: str
    ) -> bool:
        """Determine if privacy technique should be applied"""
        if technique.value in privacy_profile.restricted_techniques:
            return False
        
        # Context-based decisions
        if context == "analytics" and technique == PrivacyTechnique.ANONYMIZATION:
            return True
        elif context == "storage" and technique == PrivacyTechnique.ENCRYPTION:
            return True
        
        return True
    
    async def _record_privacy_activity(
        self, 
        user_id: str, 
        processing_context: str,
        data_fields: List[str], 
        techniques_applied: List[str]
    ) -> None:
        """Record privacy protection activity"""
        try:
            async with get_db() as db:
                privacy_record = DataPrivacyRecord(
                    user_id=user_id,
                    processing_context=processing_context,
                    data_fields=data_fields,
                    techniques_applied=techniques_applied,
                    timestamp=datetime.utcnow(),
                    compliance_status="applied"
                )
                
                db.add(privacy_record)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error recording privacy activity: {str(e)}")
    
    def _is_field_essential(self, field_name: str, processing_purpose: str) -> bool:
        """Check if field is essential for processing purpose"""
        essential_fields = {
            "content_protection": ["fingerprint", "hash", "signature", "metadata"],
            "analytics": ["count", "rate", "score", "metric", "performance"],
            "security": ["access", "auth", "security", "log", "audit"],
            "legal": ["consent", "legal", "compliance", "basis", "record"]
        }
        
        field_lower = field_name.lower()
        purpose_keywords = essential_fields.get(processing_purpose, [])
        
        return any(keyword in field_lower for keyword in purpose_keywords)
    
    async def _verify_access_authorization(
        self, 
        data_owner_id: str, 
        requester_id: str, 
        privacy_metadata: Dict[str, Any]
    ) -> bool:
        """Verify authorization for accessing protected data"""
        # In production, this would check complex authorization rules
        # For now, simple owner check
        return data_owner_id == requester_id
    
    async def _decrypt_data(self, encrypted_data: str, field_name: str, user_id: str) -> str:
        """Decrypt encrypted data"""
        try:
            encryption_key = await self.encryption_manager.get_field_key(user_id, field_name)
            decrypted_data = await self.encryption_manager.decrypt_data(encrypted_data, encryption_key)
            return decrypted_data
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return "[DECRYPTION_FAILED]"
    
    async def _reverse_pseudonymization(self, pseudonym: str, field_name: str, user_id: str) -> str:
        """Reverse pseudonymization using stored mapping"""
        try:
            # In production, query pseudonym mapping table
            # For now, return placeholder
            return "[ORIGINAL_VALUE_RECOVERED]"
        except Exception as e:
            logger.error(f"Error reversing pseudonymization: {str(e)}")
            return pseudonym
    
    async def _store_pseudonym_mapping(
        self, 
        user_id: str, 
        field_name: str, 
        original_value: str, 
        pseudonym: str
    ) -> None:
        """Store pseudonym mapping for potential reversal"""
        # In production, store in secure pseudonym mapping table
        pass
    
    async def _log_data_access(
        self, 
        user_id: str, 
        authorized_user_id: str,
        accessed_fields: List[str], 
        access_reason: str
    ) -> None:
        """Log data access for audit purposes"""
        logger.info(f"Data access: User {authorized_user_id} accessed {len(accessed_fields)} fields for user {user_id}")
    
    async def _analyze_data_sensitivity(self, data_categories: List[str]) -> Dict[str, Any]:
        """Analyze overall sensitivity of data categories"""
        sensitivity_scores = {
            DataSensitivity.PUBLIC: 1,
            DataSensitivity.INTERNAL: 2,
            DataSensitivity.CONFIDENTIAL: 3,
            DataSensitivity.RESTRICTED: 4,
            DataSensitivity.HIGHLY_SENSITIVE: 5
        }
        
        total_score = 0
        category_analysis = {}
        
        for category in data_categories:
            sensitivity = self._classify_field_sensitivity(category, "")
            score = sensitivity_scores[sensitivity]
            total_score += score
            category_analysis[category] = {
                "sensitivity": sensitivity.value,
                "score": score
            }
        
        average_score = total_score / len(data_categories) if data_categories else 0
        
        return {
            "categories": category_analysis,
            "average_sensitivity_score": average_score,
            "max_sensitivity": max([analysis["score"] for analysis in category_analysis.values()]) if category_analysis else 0,
            "risk_level": "high" if average_score >= 4 else "medium" if average_score >= 3 else "low"
        }
    
    async def _assess_processing_risks(self, processing_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with processing activity"""
        risk_factors = []
        risk_score = 0
        
        # Check for automated decision making
        if processing_activity.get("automated_decision_making", False):
            risk_factors.append("Automated decision making")
            risk_score += 2
        
        # Check for profiling
        if processing_activity.get("profiling", False):
            risk_factors.append("Profiling activities")
            risk_score += 2
        
        # Check for large scale processing
        subject_count = processing_activity.get("data_subjects_count", 0)
        if subject_count > 10000:
            risk_factors.append("Large scale processing")
            risk_score += 1
        
        # Check for vulnerable individuals
        if "children" in processing_activity.get("data_subjects_type", []):
            risk_factors.append("Processing of children's data")
            risk_score += 3
        
        # Check for cross-border transfers
        if processing_activity.get("international_transfers", False):
            risk_factors.append("International data transfers")
            risk_score += 1
        
        return {
            "risk_factors": risk_factors,
            "risk_score": risk_score,
            "max_possible_score": 9,
            "risk_level": "high" if risk_score >= 6 else "medium" if risk_score >= 3 else "low"
        }
    
    async def _evaluate_protection_measures(self, processing_activity: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate technical and organizational protection measures"""
        measures = processing_activity.get("protection_measures", [])
        
        technical_measures = []
        organizational_measures = []
        protection_score = 0
        
        for measure in measures:
            if measure in ["encryption", "pseudonymization", "anonymization", "access_controls"]:
                technical_measures.append(measure)
                protection_score += 2
            elif measure in ["staff_training", "policies", "procedures", "audits"]:
                organizational_measures.append(measure)
                protection_score += 1
        
        return {
            "technical_measures": technical_measures,
            "organizational_measures": organizational_measures,
            "total_measures": len(measures),
            "protection_score": protection_score,
            "adequacy": "strong" if protection_score >= 8 else "adequate" if protection_score >= 4 else "weak"
        }
    
    async def _calculate_privacy_risk_score(
        self, 
        sensitivity_analysis: Dict[str, Any],
        processing_risks: Dict[str, Any], 
        protection_measures: Dict[str, Any],
        data_subjects_count: int
    ) -> float:
        """Calculate overall privacy risk score (0-10)"""
        # Base risk from data sensitivity
        sensitivity_risk = sensitivity_analysis["average_sensitivity_score"]
        
        # Processing risk
        processing_risk = processing_risks["risk_score"] / processing_risks["max_possible_score"] * 10
        
        # Scale factor based on data subjects count
        scale_factor = min(2.0, data_subjects_count / 10000)
        
        # Protection mitigation factor
        protection_factor = max(0.3, 1 - (protection_measures["protection_score"] / 20))
        
        # Calculate final risk score
        risk_score = (sensitivity_risk + processing_risk) * scale_factor * protection_factor
        
        return min(10.0, max(0.0, risk_score))
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score >= 7.0:
            return "high"
        elif risk_score >= 4.0:
            return "medium"
        else:
            return "low"
    
    async def _generate_privacy_recommendations(
        self, 
        risk_score: float, 
        processing_risks: Dict[str, Any],
        protection_measures: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate privacy recommendations"""
        recommendations = []
        
        if risk_score >= 7.0:
            recommendations.append({
                "priority": "high",
                "category": "risk_mitigation",
                "title": "Implement Additional Security Measures",
                "description": "High privacy risk detected - implement additional technical and organizational measures"
            })
        
        if len(protection_measures["technical_measures"]) < 3:
            recommendations.append({
                "priority": "medium",
                "category": "technical_measures",
                "title": "Strengthen Technical Protections",
                "description": "Implement additional technical measures such as encryption, pseudonymization, or anonymization"
            })
        
        if "Automated decision making" in processing_risks["risk_factors"]:
            recommendations.append({
                "priority": "high",
                "category": "automated_decisions",
                "title": "Review Automated Decision Making",
                "description": "Ensure appropriate safeguards for automated decision making including human oversight"
            })
        
        return recommendations
    
    async def _is_dpia_required(self, risk_score: float, processing_activity: Dict[str, Any]) -> bool:
        """Determine if Data Protection Impact Assessment is required"""
        # DPIA required for high risk processing
        if risk_score >= 7.0:
            return True
        
        # DPIA required for specific processing types
        dpia_triggers = [
            processing_activity.get("automated_decision_making", False),
            processing_activity.get("profiling", False),
            processing_activity.get("large_scale_processing", False),
            "children" in processing_activity.get("data_subjects_type", []),
            processing_activity.get("sensitive_data", False)
        ]
        
        return any(dpia_triggers)
    
    async def _record_privacy_assessment(self, assessment_result: Dict[str, Any]) -> None:
        """Record privacy impact assessment"""
        try:
            # In production, store in dedicated PIA table
            logger.info(f"Privacy assessment recorded: {assessment_result['assessment_id']}")
        except Exception as e:
            logger.error(f"Error recording privacy assessment: {str(e)}")

    async def get_user_data_inventory(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive data inventory for user"""
        try:
            async with get_db() as db:
                # Get all data categories for user
                privacy_records = await db.execute(
                    select(DataPrivacyRecord).where(DataPrivacyRecord.user_id == user_id)
                )
                
                records = privacy_records.scalars().all()
                
                # Analyze data inventory
                data_categories = set()
                processing_contexts = set()
                techniques_used = set()
                
                for record in records:
                    data_categories.update(record.data_fields)
                    processing_contexts.add(record.processing_context)
                    techniques_used.update(record.techniques_applied)
                
                return {
                    "user_id": user_id,
                    "data_categories": list(data_categories),
                    "processing_contexts": list(processing_contexts),
                    "privacy_techniques": list(techniques_used),
                    "total_records": len(records),
                    "last_updated": max([r.timestamp for r in records]).isoformat() if records else None
                }
                
        except Exception as e:
            logger.error(f"Error getting user data inventory: {str(e)}")
            raise
