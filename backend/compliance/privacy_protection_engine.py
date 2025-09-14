"""
Privacy Protection Engine - Consolidated Privacy Protection System

Comprehensive privacy protection system consolidating all privacy functionality
from privacy/ subdirectory into unified enterprise-grade privacy management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import hashlib
import json
import logging
import re
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from urllib.parse import urlparse

import aioredis
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Text, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class PIIType(Enum):
    """Personally Identifiable Information types"""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    NAME = "name"
    IP_ADDRESS = "ip_address"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"
    MEDICAL_ID = "medical_id"
    BIOMETRIC = "biometric"


class DataCategory(Enum):
    """Data classification categories"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ConsentType(Enum):
    """User consent types"""
    EXPLICIT = "explicit"
    IMPLIED = "implied"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    WITHDRAWN = "withdrawn"


class ProcessingPurpose(Enum):
    """Data processing purposes"""
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PERSONALIZATION = "personalization"
    SECURITY = "security"
    LEGAL_COMPLIANCE = "legal_compliance"
    RESEARCH = "research"


class RetentionPeriod(Enum):
    """Data retention periods"""
    SESSION = "session"
    DAYS_30 = "30_days"
    MONTHS_6 = "6_months"
    YEAR_1 = "1_year"
    YEARS_3 = "3_years"
    YEARS_7 = "7_years"
    INDEFINITE = "indefinite"


@dataclass
class PIIDetectionResult:
    """PII detection result data structure"""
    pii_type: PIIType
    value: str
    confidence: float
    location: Tuple[int, int]
    masked_value: str
    context: str


@dataclass
class ConsentRecord:
    """User consent record"""
    user_id: str
    consent_type: ConsentType
    purpose: ProcessingPurpose
    granted_at: datetime
    expires_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    consent_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataProcessingRecord:
    """Data processing activity record"""
    processing_id: str
    user_id: str
    data_types: List[PIIType]
    purpose: ProcessingPurpose
    legal_basis: str
    processor: str
    processed_at: datetime
    retention_period: RetentionPeriod
    location: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PIIRecord(Base):
    """Database model for PII detection records"""
    __tablename__ = "pii_records"
    
    record_id = Column(String, primary_key=True)
    content_id = Column(String, nullable=False)
    pii_type = Column(String, nullable=False)
    masked_value = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    detection_timestamp = Column(DateTime, default=datetime.utcnow)
    location_start = Column(Integer, nullable=False)
    location_end = Column(Integer, nullable=False)
    context = Column(Text)
    processed_by = Column(String, default="automated_system")


class ConsentManagementRecord(Base):
    """Database model for consent management"""
    __tablename__ = "consent_management"
    
    consent_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    consent_type = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    granted_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime)
    withdrawn_at = Column(DateTime)
    consent_version = Column(String, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class DataProcessingLog(Base):
    """Database model for data processing logs"""
    __tablename__ = "data_processing_logs"
    
    log_id = Column(String, primary_key=True)
    processing_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    data_types = Column(JSON, default=[])
    purpose = Column(String, nullable=False)
    legal_basis = Column(String, nullable=False)
    processor = Column(String, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    retention_period = Column(String, nullable=False)
    processing_location = Column(String, nullable=False)
    metadata = Column(JSON, default={})


class EncryptionKey(Base):
    """Database model for encryption keys"""
    __tablename__ = "encryption_keys"
    
    key_id = Column(String, primary_key=True)
    key_type = Column(String, nullable=False)
    key_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    purpose = Column(String, nullable=False)
    metadata = Column(JSON, default={})


class PIIDetector:
    """Advanced PII detection and classification"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.pii_patterns = self._compile_pii_patterns()
        
    async def detect_pii(self, content: str) -> List[PIIDetectionResult]:
        """Detect PII in content"""
        try:
            detection_results = []
            
            for pii_type, pattern in self.pii_patterns.items():
                matches = pattern.finditer(content)
                
                for match in matches:
                    confidence = await self._calculate_confidence(match.group(), pii_type)
                    
                    if confidence >= 0.5:  # Confidence threshold
                        masked_value = await self._mask_pii(match.group(), pii_type)
                        context = await self._extract_context(content, match.start(), match.end())
                        
                        result = PIIDetectionResult(
                            pii_type=pii_type,
                            value=match.group(),
                            confidence=confidence,
                            location=(match.start(), match.end()),
                            masked_value=masked_value,
                            context=context
                        )
                        
                        detection_results.append(result)
            
            # Remove duplicates and overlapping detections
            detection_results = await self._deduplicate_detections(detection_results)
            
            return detection_results
            
        except Exception as e:
            logger.error(f"PII detection failed: {str(e)}")
            raise
    
    def _compile_pii_patterns(self) -> Dict[PIIType, re.Pattern]:
        """Compile regex patterns for PII detection"""
        patterns = {
            PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            PIIType.PHONE: re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'),
            PIIType.SSN: re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            PIIType.CREDIT_CARD: re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            PIIType.IP_ADDRESS: re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            PIIType.ADDRESS: re.compile(r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)', re.IGNORECASE)
        }
        
        return patterns
    
    async def _calculate_confidence(self, value: str, pii_type: PIIType) -> float:
        """Calculate confidence score for PII detection"""
        confidence_rules = {
            PIIType.EMAIL: self._validate_email,
            PIIType.PHONE: self._validate_phone,
            PIIType.SSN: self._validate_ssn,
            PIIType.CREDIT_CARD: self._validate_credit_card,
            PIIType.IP_ADDRESS: self._validate_ip_address
        }
        
        validator = confidence_rules.get(pii_type, lambda x: 0.7)
        return validator(value)
    
    def _validate_email(self, email: str) -> float:
        """Validate email and return confidence score"""
        # Basic email validation
        if '@' in email and '.' in email.split('@')[1]:
            return 0.9
        return 0.3
    
    def _validate_phone(self, phone: str) -> float:
        """Validate phone number and return confidence score"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10 or len(digits) == 11:
            return 0.8
        return 0.4
    
    def _validate_ssn(self, ssn: str) -> float:
        """Validate SSN and return confidence score"""
        if re.match(r'^\d{3}-\d{2}-\d{4}$', ssn):
            return 0.95
        return 0.5
    
    def _validate_credit_card(self, cc: str) -> float:
        """Validate credit card using Luhn algorithm"""
        digits = re.sub(r'\D', '', cc)
        
        if len(digits) < 13 or len(digits) > 19:
            return 0.3
        
        # Luhn algorithm
        checksum = 0
        is_even = False
        
        for digit in reversed(digits):
            d = int(digit)
            if is_even:
                d *= 2
                if d > 9:
                    d = d // 10 + d % 10
            checksum += d
            is_even = not is_even
        
        return 0.9 if checksum % 10 == 0 else 0.4
    
    def _validate_ip_address(self, ip: str) -> float:
        """Validate IP address and return confidence score"""
        parts = ip.split('.')
        if len(parts) == 4:
            try:
                if all(0 <= int(part) <= 255 for part in parts):
                    return 0.95
            except ValueError:
                pass
        return 0.3
    
    async def _mask_pii(self, value: str, pii_type: PIIType) -> str:
        """Mask PII value based on type"""
        masking_strategies = {
            PIIType.EMAIL: lambda x: f"{x[:2]}***@{x.split('@')[1]}",
            PIIType.PHONE: lambda x: f"***-***-{x[-4:]}",
            PIIType.SSN: lambda x: f"***-**-{x[-4:]}",
            PIIType.CREDIT_CARD: lambda x: f"****-****-****-{x[-4:]}",
            PIIType.IP_ADDRESS: lambda x: f"{x.split('.')[0]}.***.***.***"
        }
        
        masker = masking_strategies.get(pii_type, lambda x: "***REDACTED***")
        return masker(value)
    
    async def _extract_context(self, content: str, start: int, end: int) -> str:
        """Extract context around PII detection"""
        context_start = max(0, start - 50)
        context_end = min(len(content), end + 50)
        return content[context_start:context_end]
    
    async def _deduplicate_detections(self, results: List[PIIDetectionResult]) -> List[PIIDetectionResult]:
        """Remove duplicate and overlapping PII detections"""
        if not results:
            return results
        
        # Sort by location
        results.sort(key=lambda x: x.location[0])
        
        deduplicated = []
        last_end = -1
        
        for result in results:
            if result.location[0] > last_end:
                deduplicated.append(result)
                last_end = result.location[1]
            elif result.confidence > deduplicated[-1].confidence:
                # Replace with higher confidence detection
                deduplicated[-1] = result
                last_end = result.location[1]
        
        return deduplicated


class DataAnonymizer:
    """Advanced data anonymization and pseudonymization"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        self.encryption_key = self._get_encryption_key()
        
    async def anonymize_data(self, data: Dict[str, Any], anonymization_level: str = "standard") -> Dict[str, Any]:
        """Anonymize data based on specified level"""
        try:
            anonymized_data = data.copy()
            
            if anonymization_level == "minimal":
                anonymized_data = await self._minimal_anonymization(anonymized_data)
            elif anonymization_level == "standard":
                anonymized_data = await self._standard_anonymization(anonymized_data)
            elif anonymization_level == "aggressive":
                anonymized_data = await self._aggressive_anonymization(anonymized_data)
            
            return anonymized_data
            
        except Exception as e:
            logger.error(f"Data anonymization failed: {str(e)}")
            raise
    
    async def pseudonymize_data(self, data: Dict[str, Any], pseudonym_key: str = None) -> Dict[str, Any]:
        """Pseudonymize data with reversible anonymization"""
        try:
            pseudonymized_data = data.copy()
            pseudonym_key = pseudonym_key or self._generate_pseudonym_key()
            
            # Identify PII fields
            pii_fields = await self._identify_pii_fields(data)
            
            # Apply pseudonymization
            for field in pii_fields:
                if field in pseudonymized_data:
                    original_value = str(pseudonymized_data[field])
                    pseudonym = await self._generate_pseudonym(original_value, pseudonym_key)
                    pseudonymized_data[field] = pseudonym
                    
                    # Store mapping for reversal
                    await self._store_pseudonym_mapping(original_value, pseudonym, pseudonym_key)
            
            return pseudonymized_data
            
        except Exception as e:
            logger.error(f"Data pseudonymization failed: {str(e)}")
            raise
    
    async def k_anonymize(self, dataset: List[Dict[str, Any]], k: int = 5, 
                         quasi_identifiers: List[str] = None) -> List[Dict[str, Any]]:
        """Apply k-anonymity to dataset"""
        try:
            if not quasi_identifiers:
                quasi_identifiers = await self._identify_quasi_identifiers(dataset)
            
            # Group records by quasi-identifier combinations
            groups = defaultdict(list)
            
            for record in dataset:
                key = tuple(record.get(qi, '') for qi in quasi_identifiers)
                groups[key].append(record)
            
            # Generalize groups with fewer than k records
            anonymized_dataset = []
            
            for group_key, records in groups.items():
                if len(records) < k:
                    # Generalize this group
                    generalized_records = await self._generalize_group(records, quasi_identifiers)
                    anonymized_dataset.extend(generalized_records)
                else:
                    anonymized_dataset.extend(records)
            
            return anonymized_dataset
            
        except Exception as e:
            logger.error(f"K-anonymization failed: {str(e)}")
            raise
    
    async def differential_privacy(self, query_result: float, epsilon: float = 1.0) -> float:
        """Apply differential privacy noise to query result"""
        try:
            import numpy as np
            
            # Laplace mechanism for differential privacy
            sensitivity = 1.0  # This should be calculated based on the specific query
            noise = np.random.laplace(0, sensitivity / epsilon)
            
            noisy_result = query_result + noise
            return noisy_result
            
        except Exception as e:
            logger.error(f"Differential privacy application failed: {str(e)}")
            raise
    
    async def _minimal_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply minimal anonymization (basic masking)"""
        sensitive_fields = ['email', 'phone', 'ssn']
        
        for field in sensitive_fields:
            if field in data:
                value = str(data[field])
                if field == 'email' and '@' in value:
                    data[field] = f"{value[:2]}***@{value.split('@')[1]}"
                elif field == 'phone':
                    data[field] = f"***-***-{value[-4:]}"
                elif field == 'ssn':
                    data[field] = f"***-**-{value[-4:]}"
        
        return data
    
    async def _standard_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply standard anonymization (replace with generic values)"""
        anonymization_map = {
            'name': 'User',
            'email': 'user@example.com',
            'phone': '***-***-****',
            'address': 'Redacted Address',
            'ip_address': '***.***.***.**'
        }
        
        for field, replacement in anonymization_map.items():
            if field in data:
                data[field] = replacement
        
        return data
    
    async def _aggressive_anonymization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply aggressive anonymization (remove sensitive fields)"""
        sensitive_fields = [
            'name', 'email', 'phone', 'address', 'ssn', 'ip_address',
            'credit_card', 'passport', 'driver_license', 'bank_account'
        ]
        
        for field in sensitive_fields:
            if field in data:
                del data[field]
        
        return data
    
    async def _identify_pii_fields(self, data: Dict[str, Any]) -> List[str]:
        """Identify fields containing PII"""
        pii_field_patterns = [
            'email', 'phone', 'ssn', 'social_security', 'address',
            'name', 'first_name', 'last_name', 'ip', 'credit_card'
        ]
        
        pii_fields = []
        for field in data.keys():
            field_lower = field.lower()
            if any(pattern in field_lower for pattern in pii_field_patterns):
                pii_fields.append(field)
        
        return pii_fields
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key"""
        # In production, this would be retrieved from secure key management
        return Fernet.generate_key()
    
    def _generate_pseudonym_key(self) -> str:
        """Generate pseudonym key"""
        return str(uuid.uuid4())
    
    async def _generate_pseudonym(self, original_value: str, pseudonym_key: str) -> str:
        """Generate pseudonym for original value"""
        # Create deterministic pseudonym using hash
        combined = f"{original_value}:{pseudonym_key}"
        hash_object = hashlib.sha256(combined.encode())
        return f"pseudo_{hash_object.hexdigest()[:8]}"
    
    async def _store_pseudonym_mapping(self, original: str, pseudonym: str, key: str) -> None:
        """Store pseudonym mapping for reversal"""
        mapping = {
            "original": original,
            "pseudonym": pseudonym,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await self.redis.setex(f"pseudonym:{key}:{pseudonym}", 3600 * 24 * 30, 
                              json.dumps(mapping))
    
    async def _identify_quasi_identifiers(self, dataset: List[Dict[str, Any]]) -> List[str]:
        """Identify quasi-identifier fields in dataset"""
        # Mock implementation - would use more sophisticated analysis
        common_quasi_identifiers = ['age', 'gender', 'zip_code', 'occupation']
        
        if not dataset:
            return common_quasi_identifiers
        
        available_fields = dataset[0].keys()
        return [qi for qi in common_quasi_identifiers if qi in available_fields]
    
    async def _generalize_group(self, records: List[Dict[str, Any]], 
                               quasi_identifiers: List[str]) -> List[Dict[str, Any]]:
        """Generalize group of records to achieve k-anonymity"""
        if not records:
            return records
        
        generalized_records = []
        
        for record in records:
            generalized_record = record.copy()
            
            # Apply generalization to quasi-identifiers
            for qi in quasi_identifiers:
                if qi in generalized_record:
                    if qi == 'age':
                        age = generalized_record[qi]
                        if isinstance(age, int):
                            # Generalize age to age range
                            age_range = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
                            generalized_record[qi] = age_range
                    elif qi == 'zip_code':
                        zip_code = str(generalized_record[qi])
                        # Generalize zip code to first 3 digits
                        generalized_record[qi] = zip_code[:3] + "**"
            
            generalized_records.append(generalized_record)
        
        return generalized_records


class ConsentManager:
    """Comprehensive consent management system"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def request_consent(self, user_id: str, purposes: List[ProcessingPurpose],
                            consent_version: str = "1.0") -> str:
        """Request user consent for data processing"""
        try:
            consent_id = str(uuid.uuid4())
            
            # Create consent request
            consent_request = {
                "consent_id": consent_id,
                "user_id": user_id,
                "purposes": [p.value for p in purposes],
                "consent_version": consent_version,
                "requested_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            # Store consent request
            await self.redis.setex(f"consent_request:{consent_id}", 3600 * 24, 
                                  json.dumps(consent_request))
            
            # Send consent request to user (mock implementation)
            await self._send_consent_request(user_id, consent_request)
            
            return consent_id
            
        except Exception as e:
            logger.error(f"Consent request failed: {str(e)}")
            raise
    
    async def grant_consent(self, consent_id: str, granted_purposes: List[ProcessingPurpose],
                          expires_at: Optional[datetime] = None) -> ConsentRecord:
        """Grant consent for specified purposes"""
        try:
            # Retrieve consent request
            request_data = await self.redis.get(f"consent_request:{consent_id}")
            if not request_data:
                raise ValueError(f"Consent request {consent_id} not found")
            
            request = json.loads(request_data)
            
            # Create consent record
            consent_record = ConsentRecord(
                user_id=request["user_id"],
                consent_type=ConsentType.EXPLICIT,
                purpose=granted_purposes[0] if granted_purposes else ProcessingPurpose.SERVICE_PROVISION,
                granted_at=datetime.utcnow(),
                expires_at=expires_at,
                withdrawn_at=None,
                consent_version=request["consent_version"],
                metadata={
                    "consent_id": consent_id,
                    "granted_purposes": [p.value for p in granted_purposes],
                    "original_request": request
                }
            )
            
            # Store in database
            await self._store_consent_record(consent_record)
            
            # Update cache
            await self._cache_user_consents(request["user_id"])
            
            return consent_record
            
        except Exception as e:
            logger.error(f"Consent granting failed: {str(e)}")
            raise
    
    async def withdraw_consent(self, user_id: str, purpose: ProcessingPurpose) -> bool:
        """Withdraw user consent for specific purpose"""
        try:
            # Find active consent records
            consent_records = await self._get_user_consents(user_id)
            
            withdrawn = False
            for record in consent_records:
                if record.purpose == purpose and not record.withdrawn_at:
                    # Mark as withdrawn
                    record.withdrawn_at = datetime.utcnow()
                    await self._update_consent_record(record)
                    withdrawn = True
            
            if withdrawn:
                # Trigger data processing cleanup
                await self._trigger_consent_withdrawal_cleanup(user_id, purpose)
                
                # Update cache
                await self._cache_user_consents(user_id)
            
            return withdrawn
            
        except Exception as e:
            logger.error(f"Consent withdrawal failed: {str(e)}")
            raise
    
    async def check_consent(self, user_id: str, purpose: ProcessingPurpose) -> bool:
        """Check if user has valid consent for purpose"""
        try:
            consent_records = await self._get_user_consents(user_id)
            
            for record in consent_records:
                if (record.purpose == purpose and 
                    not record.withdrawn_at and
                    (not record.expires_at or record.expires_at > datetime.utcnow())):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Consent check failed: {str(e)}")
            return False
    
    async def get_consent_history(self, user_id: str) -> List[ConsentRecord]:
        """Get complete consent history for user"""
        try:
            return await self._get_user_consents(user_id, include_withdrawn=True)
            
        except Exception as e:
            logger.error(f"Getting consent history failed: {str(e)}")
            raise
    
    async def _send_consent_request(self, user_id: str, request: Dict[str, Any]) -> None:
        """Send consent request to user"""
        # Mock implementation - would integrate with notification system
        logger.info(f"Consent request sent to user {user_id}: {request['consent_id']}")
    
    async def _store_consent_record(self, record: ConsentRecord) -> None:
        """Store consent record in database"""
        try:
            consent_db_record = ConsentManagementRecord(
                consent_id=str(uuid.uuid4()),
                user_id=record.user_id,
                consent_type=record.consent_type.value,
                purpose=record.purpose.value,
                granted_at=record.granted_at,
                expires_at=record.expires_at,
                withdrawn_at=record.withdrawn_at,
                consent_version=record.consent_version,
                metadata=record.metadata
            )
            
            self.db.add(consent_db_record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store consent record: {str(e)}")
            raise
    
    async def _update_consent_record(self, record: ConsentRecord) -> None:
        """Update existing consent record"""
        # Implementation would update database record
        pass
    
    async def _get_user_consents(self, user_id: str, include_withdrawn: bool = False) -> List[ConsentRecord]:
        """Get user consent records"""
        # Implementation would query database
        return []
    
    async def _cache_user_consents(self, user_id: str) -> None:
        """Cache user consents for quick access"""
        consents = await self._get_user_consents(user_id)
        consent_data = [
            {
                "purpose": c.purpose.value,
                "granted_at": c.granted_at.isoformat(),
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None
            }
            for c in consents
        ]
        
        await self.redis.setex(f"user_consents:{user_id}", 3600, 
                              json.dumps(consent_data))
    
    async def _trigger_consent_withdrawal_cleanup(self, user_id: str, purpose: ProcessingPurpose) -> None:
        """Trigger cleanup when consent is withdrawn"""
        # Implementation would trigger data deletion/anonymization
        logger.info(f"Consent withdrawal cleanup triggered for user {user_id}, purpose {purpose.value}")


class EncryptionManager:
    """Advanced encryption and key management"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def encrypt_data(self, data: str, key_id: str = None, algorithm: str = "AES-GCM") -> Dict[str, Any]:
        """Encrypt data using specified algorithm"""
        try:
            if not key_id:
                key_id = await self._generate_encryption_key(algorithm)
            
            key_data = await self._get_encryption_key(key_id)
            
            if algorithm == "AES-GCM":
                encrypted_data = await self._encrypt_aes_gcm(data, key_data)
            elif algorithm == "RSA":
                encrypted_data = await self._encrypt_rsa(data, key_data)
            elif algorithm == "Fernet":
                encrypted_data = await self._encrypt_fernet(data, key_data)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
            
            return {
                "encrypted_data": encrypted_data,
                "key_id": key_id,
                "algorithm": algorithm,
                "encrypted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data encryption failed: {str(e)}")
            raise
    
    async def decrypt_data(self, encrypted_data: str, key_id: str, algorithm: str) -> str:
        """Decrypt data using specified algorithm and key"""
        try:
            key_data = await self._get_encryption_key(key_id)
            
            if algorithm == "AES-GCM":
                decrypted_data = await self._decrypt_aes_gcm(encrypted_data, key_data)
            elif algorithm == "RSA":
                decrypted_data = await self._decrypt_rsa(encrypted_data, key_data)
            elif algorithm == "Fernet":
                decrypted_data = await self._decrypt_fernet(encrypted_data, key_data)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {algorithm}")
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Data decryption failed: {str(e)}")
            raise
    
    async def rotate_encryption_key(self, old_key_id: str) -> str:
        """Rotate encryption key and re-encrypt data"""
        try:
            # Generate new key
            new_key_id = await self._generate_encryption_key("AES-GCM")
            
            # Mark old key for rotation
            await self._mark_key_for_rotation(old_key_id, new_key_id)
            
            # Trigger background re-encryption process
            await self._trigger_key_rotation_process(old_key_id, new_key_id)
            
            return new_key_id
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise
    
    async def _generate_encryption_key(self, algorithm: str) -> str:
        """Generate new encryption key"""
        try:
            key_id = str(uuid.uuid4())
            
            if algorithm == "AES-GCM":
                key_data = self._generate_aes_key()
            elif algorithm == "RSA":
                key_data = self._generate_rsa_key_pair()
            elif algorithm == "Fernet":
                key_data = Fernet.generate_key()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Store key in database
            key_record = EncryptionKey(
                key_id=key_id,
                key_type=algorithm,
                key_data=key_data,
                purpose="data_encryption",
                metadata={"generated_at": datetime.utcnow().isoformat()}
            )
            
            self.db.add(key_record)
            await self.db.commit()
            
            return key_id
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Key generation failed: {str(e)}")
            raise
    
    async def _get_encryption_key(self, key_id: str) -> bytes:
        """Retrieve encryption key from storage"""
        # Implementation would query database
        # Mock return for now
        return b"mock_key_data"
    
    def _generate_aes_key(self) -> bytes:
        """Generate AES key"""
        import os
        return os.urandom(32)  # 256-bit key
    
    def _generate_rsa_key_pair(self) -> bytes:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return private_pem
    
    async def _encrypt_aes_gcm(self, data: str, key: bytes) -> str:
        """Encrypt using AES-GCM"""
        import os
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        aes_gcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        
        ciphertext = aes_gcm.encrypt(nonce, data.encode(), None)
        
        # Combine nonce and ciphertext
        encrypted = nonce + ciphertext
        
        import base64
        return base64.b64encode(encrypted).decode()
    
    async def _decrypt_aes_gcm(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt using AES-GCM"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import base64
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Extract nonce and ciphertext
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        
        aes_gcm = AESGCM(key)
        plaintext = aes_gcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode()
    
    async def _encrypt_rsa(self, data: str, private_key_pem: bytes) -> str:
        """Encrypt using RSA"""
        # Load private key and extract public key
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        public_key = private_key.public_key()
        
        # Encrypt with public key
        ciphertext = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        import base64
        return base64.b64encode(ciphertext).decode()
    
    async def _decrypt_rsa(self, encrypted_data: str, private_key_pem: bytes) -> str:
        """Decrypt using RSA"""
        import base64
        
        # Load private key
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        
        # Decrypt
        ciphertext = base64.b64decode(encrypted_data)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext.decode()
    
    async def _encrypt_fernet(self, data: str, key: bytes) -> str:
        """Encrypt using Fernet"""
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    
    async def _decrypt_fernet(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt using Fernet"""
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    async def _mark_key_for_rotation(self, old_key_id: str, new_key_id: str) -> None:
        """Mark key for rotation"""
        # Implementation would update database
        pass
    
    async def _trigger_key_rotation_process(self, old_key_id: str, new_key_id: str) -> None:
        """Trigger background key rotation process"""
        # Implementation would queue background job
        logger.info(f"Key rotation process triggered: {old_key_id} -> {new_key_id}")


class DataRetentionManager:
    """Data retention and lifecycle management"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def set_retention_policy(self, data_type: str, retention_period: RetentionPeriod,
                                  deletion_method: str = "secure_delete") -> str:
        """Set data retention policy"""
        try:
            policy_id = str(uuid.uuid4())
            
            policy = {
                "policy_id": policy_id,
                "data_type": data_type,
                "retention_period": retention_period.value,
                "deletion_method": deletion_method,
                "created_at": datetime.utcnow().isoformat(),
                "active": True
            }
            
            # Store policy
            await self.redis.setex(f"retention_policy:{policy_id}", 3600 * 24 * 365, 
                                  json.dumps(policy))
            
            return policy_id
            
        except Exception as e:
            logger.error(f"Setting retention policy failed: {str(e)}")
            raise
    
    async def check_data_expiration(self, data_id: str, data_type: str) -> Dict[str, Any]:
        """Check if data has expired based on retention policy"""
        try:
            # Get retention policy for data type
            policy = await self._get_retention_policy(data_type)
            
            if not policy:
                return {"expired": False, "reason": "No retention policy found"}
            
            # Get data creation/last access time
            data_info = await self._get_data_info(data_id)
            
            if not data_info:
                return {"expired": False, "reason": "Data info not found"}
            
            # Calculate expiration
            retention_days = self._get_retention_days(policy["retention_period"])
            creation_date = datetime.fromisoformat(data_info["created_at"])
            expiration_date = creation_date + timedelta(days=retention_days)
            
            expired = datetime.utcnow() > expiration_date
            
            return {
                "expired": expired,
                "expiration_date": expiration_date.isoformat(),
                "retention_period": policy["retention_period"],
                "days_remaining": (expiration_date - datetime.utcnow()).days if not expired else 0
            }
            
        except Exception as e:
            logger.error(f"Data expiration check failed: {str(e)}")
            raise
    
    async def schedule_data_deletion(self, data_id: str, deletion_date: datetime) -> str:
        """Schedule data for deletion"""
        try:
            deletion_job_id = str(uuid.uuid4())
            
            deletion_job = {
                "job_id": deletion_job_id,
                "data_id": data_id,
                "scheduled_deletion": deletion_date.isoformat(),
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store deletion job
            await self.redis.zadd("scheduled_deletions", 
                                 {deletion_job_id: deletion_date.timestamp()})
            
            await self.redis.setex(f"deletion_job:{deletion_job_id}", 
                                  3600 * 24 * 30, json.dumps(deletion_job))
            
            return deletion_job_id
            
        except Exception as e:
            logger.error(f"Scheduling data deletion failed: {str(e)}")
            raise
    
    async def execute_data_deletion(self, data_id: str, deletion_method: str = "secure_delete") -> bool:
        """Execute data deletion"""
        try:
            if deletion_method == "secure_delete":
                success = await self._secure_delete_data(data_id)
            elif deletion_method == "anonymize":
                success = await self._anonymize_data_for_deletion(data_id)
            elif deletion_method == "archive":
                success = await self._archive_data(data_id)
            else:
                raise ValueError(f"Unknown deletion method: {deletion_method}")
            
            if success:
                # Log deletion
                await self._log_data_deletion(data_id, deletion_method)
            
            return success
            
        except Exception as e:
            logger.error(f"Data deletion execution failed: {str(e)}")
            raise
    
    async def _get_retention_policy(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Get retention policy for data type"""
        # Implementation would query policies
        return {
            "retention_period": "1_year",
            "deletion_method": "secure_delete"
        }
    
    async def _get_data_info(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Get data information"""
        # Implementation would query data metadata
        return {
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat()
        }
    
    def _get_retention_days(self, retention_period: str) -> int:
        """Convert retention period to days"""
        period_map = {
            "session": 1,
            "30_days": 30,
            "6_months": 180,
            "1_year": 365,
            "3_years": 1095,
            "7_years": 2555,
            "indefinite": 36500  # 100 years
        }
        
        return period_map.get(retention_period, 365)
    
    async def _secure_delete_data(self, data_id: str) -> bool:
        """Securely delete data"""
        # Implementation would perform secure deletion
        logger.info(f"Securely deleting data: {data_id}")
        return True
    
    async def _anonymize_data_for_deletion(self, data_id: str) -> bool:
        """Anonymize data instead of deletion"""
        # Implementation would anonymize data
        logger.info(f"Anonymizing data for deletion: {data_id}")
        return True
    
    async def _archive_data(self, data_id: str) -> bool:
        """Archive data to long-term storage"""
        # Implementation would move data to archive
        logger.info(f"Archiving data: {data_id}")
        return True
    
    async def _log_data_deletion(self, data_id: str, method: str) -> None:
        """Log data deletion for audit"""
        deletion_log = {
            "data_id": data_id,
            "deletion_method": method,
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted_by": "automated_system"
        }
        
        await self.redis.lpush("deletion_audit_log", json.dumps(deletion_log))


# Main Privacy Protection Orchestrator
class PrivacyProtectionEngine:
    """Main privacy protection engine orchestrator"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
        # Initialize all privacy components
        self.pii_detector = PIIDetector(redis_client)
        self.data_anonymizer = DataAnonymizer(redis_client)
        self.consent_manager = ConsentManager(db_session, redis_client)
        self.encryption_manager = EncryptionManager(db_session, redis_client)
        self.retention_manager = DataRetentionManager(db_session, redis_client)
        
    async def comprehensive_privacy_analysis(self, content: str, user_id: str = None) -> Dict[str, Any]:
        """Perform comprehensive privacy analysis"""
        try:
            analysis_id = str(uuid.uuid4())
            
            # Detect PII
            pii_detections = await self.pii_detector.detect_pii(content)
            
            # Check consent if user provided
            consent_status = {}
            if user_id:
                for purpose in ProcessingPurpose:
                    consent_status[purpose.value] = await self.consent_manager.check_consent(user_id, purpose)
            
            # Generate privacy risk assessment
            privacy_risk = await self._assess_privacy_risk(pii_detections, consent_status)
            
            # Provide privacy recommendations
            recommendations = await self._generate_privacy_recommendations(pii_detections, privacy_risk)
            
            analysis_result = {
                "analysis_id": analysis_id,
                "pii_detections": [
                    {
                        "type": detection.pii_type.value,
                        "masked_value": detection.masked_value,
                        "confidence": detection.confidence,
                        "location": detection.location
                    }
                    for detection in pii_detections
                ],
                "consent_status": consent_status,
                "privacy_risk_score": privacy_risk["score"],
                "privacy_risk_level": privacy_risk["level"],
                "risk_factors": privacy_risk["factors"],
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Store analysis result
            await self.redis.setex(f"privacy_analysis:{analysis_id}", 3600, 
                                  json.dumps(analysis_result, default=str))
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Comprehensive privacy analysis failed: {str(e)}")
            raise
    
    async def _assess_privacy_risk(self, pii_detections: List[PIIDetectionResult], 
                                  consent_status: Dict[str, bool]) -> Dict[str, Any]:
        """Assess privacy risk based on PII and consent"""
        risk_score = 0.0
        risk_factors = []
        
        # Risk from PII detection
        high_risk_pii = [PIIType.SSN, PIIType.CREDIT_CARD, PIIType.PASSPORT]
        medium_risk_pii = [PIIType.EMAIL, PIIType.PHONE, PIIType.ADDRESS]
        
        for detection in pii_detections:
            if detection.pii_type in high_risk_pii:
                risk_score += 0.4 * detection.confidence
                risk_factors.append(f"High-risk PII detected: {detection.pii_type.value}")
            elif detection.pii_type in medium_risk_pii:
                risk_score += 0.2 * detection.confidence
                risk_factors.append(f"Medium-risk PII detected: {detection.pii_type.value}")
            else:
                risk_score += 0.1 * detection.confidence
                risk_factors.append(f"Low-risk PII detected: {detection.pii_type.value}")
        
        # Risk from missing consent
        missing_consents = [purpose for purpose, granted in consent_status.items() if not granted]
        if missing_consents:
            risk_score += 0.3 * len(missing_consents) / len(consent_status)
            risk_factors.append(f"Missing consent for: {', '.join(missing_consents)}")
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        elif risk_score >= 0.2:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "score": min(risk_score, 1.0),
            "level": risk_level,
            "factors": risk_factors
        }
    
    async def _generate_privacy_recommendations(self, pii_detections: List[PIIDetectionResult], 
                                               privacy_risk: Dict[str, Any]) -> List[str]:
        """Generate privacy protection recommendations"""
        recommendations = []
        
        if pii_detections:
            recommendations.append("Consider anonymizing or masking detected PII")
            recommendations.append("Implement encryption for sensitive data")
            recommendations.append("Review data retention policies")
        
        if privacy_risk["level"] in ["high", "critical"]:
            recommendations.append("Obtain explicit user consent before processing")
            recommendations.append("Implement additional security measures")
            recommendations.append("Consider data minimization techniques")
        
        if privacy_risk["score"] > 0.5:
            recommendations.append("Conduct privacy impact assessment")
            recommendations.append("Review data sharing agreements")
        
        return recommendations


# Export main classes for privacy protection engine consolidation
__all__ = [
    "PrivacyProtectionEngine",
    "PIIDetector",
    "DataAnonymizer",
    "ConsentManager",
    "EncryptionManager",
    "DataRetentionManager",
    "PIIType",
    "DataCategory",
    "ConsentType",
    "ProcessingPurpose",
    "RetentionPeriod",
    "PIIDetectionResult",
    "ConsentRecord",
    "DataProcessingRecord"
]
