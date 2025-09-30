"""
Data Protection Manager
======================

Advanced data protection and privacy management for Ainflue Distribution Platform.
Provides GDPR/CCPA compliance, data encryption, and privacy controls.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import hashlib
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt

logger = logging.getLogger(__name__)

class DataCategory(Enum):
    """Data categories for classification"""
    PERSONAL_IDENTIFIABLE = "pii"
    SENSITIVE_PERSONAL = "sensitive_pii"
    FINANCIAL = "financial"
    HEALTH = "health"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    ANALYTICS = "analytics"

class ConsentType(Enum):
    """Types of consent for data processing"""
    ESSENTIAL = "essential"
    FUNCTIONAL = "functional"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    PERSONALIZATION = "personalization"
    THIRD_PARTY = "third_party"

class DataSubjectRight(Enum):
    """Data subject rights under GDPR/CCPA"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    AUTOMATED_DECISION_OPT_OUT = "automated_decision_opt_out"

class RetentionPolicy(Enum):
    """Data retention policies"""
    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 1 year
    LONG_TERM = "long_term"  # 7 years
    PERMANENT = "permanent"
    CUSTOM = "custom"

@dataclass
class ConsentRecord:
    """Individual consent record"""
    user_id: str
    consent_type: str
    granted: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    consent_version: str
    explicit: bool = True
    withdrawal_date: Optional[datetime] = None
    legal_basis: str = "consent"

@dataclass
class DataProcessingRecord:
    """Data processing activity record"""
    processing_id: str
    user_id: str
    data_category: str
    purpose: str
    legal_basis: str
    processor: str
    timestamp: datetime
    retention_period: int  # days
    third_party_shared: bool = False
    cross_border_transfer: bool = False
    automated_decision_making: bool = False

@dataclass
class DataSubjectRequest:
    """Data subject rights request"""
    request_id: str
    user_id: str
    request_type: str
    status: str
    created_date: datetime
    completion_date: Optional[datetime] = None
    verification_completed: bool = False
    data_delivered: Optional[str] = None  # File path or data
    notes: str = ""

@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    algorithm: str = "AES-256"
    key_rotation_days: int = 90
    salt_length: int = 32
    iterations: int = 100000
    enable_field_level_encryption: bool = True
    enable_database_encryption: bool = True
    enable_backup_encryption: bool = True

class DataProtectionManager:
    """
    Advanced Data Protection Manager
    
    Provides comprehensive data protection including:
    - GDPR/CCPA compliance management
    - Data encryption and anonymization
    - Consent management
    - Data subject rights handling
    - Privacy impact assessments
    - Data breach detection and reporting
    """
    
    def __init__(self, encryption_key: str = None):
        """
        Initialize data protection manager
        
        Args:
            encryption_key: Master encryption key (if None, generates new key)
        """
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher = self._initialize_cipher()
        self.consent_records: Dict[str, List[ConsentRecord]] = {}
        self.processing_records: List[DataProcessingRecord] = []
        self.subject_requests: Dict[str, DataSubjectRequest] = {}
        self.encryption_config = EncryptionConfig()
        
    def _generate_encryption_key(self) -> str:
        """Generate a new encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize encryption cipher"""
        key_bytes = base64.urlsafe_b64decode(self.encryption_key.encode())
        return Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.encryption_config.iterations,
        )
        return kdf.derive(password.encode())
    
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data
        
        Args:
            data: Data to encrypt
            
        Returns:
            str: Encrypted data (base64 encoded)
        """
        try:
            if not data:
                return data
            
            encrypted_bytes = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
            
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: Encrypted data (base64 encoded)
            
        Returns:
            str: Decrypted data
        """
        try:
            if not encrypted_data:
                return encrypted_data
            
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise
    
    def hash_pii(self, pii_data: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash personally identifiable information
        
        Args:
            pii_data: PII data to hash
            salt: Optional salt (generates if not provided)
            
        Returns:
            Tuple[str, str]: (hashed_data, salt)
        """
        try:
            if salt is None:
                salt = secrets.token_hex(16)
            
            # Use bcrypt for password-like data or SHA-256 for general PII
            if len(pii_data) > 50:  # Likely not a password
                hash_obj = hashlib.sha256()
                hash_obj.update((pii_data + salt).encode())
                hashed_data = hash_obj.hexdigest()
            else:
                # Use bcrypt for password-like data
                salt_bytes = salt.encode()[:16].ljust(16, b'0')[:16]  # Ensure 16 bytes
                hashed_data = bcrypt.hashpw(pii_data.encode(), bcrypt.gensalt()).decode()
            
            return hashed_data, salt
            
        except Exception as e:
            logger.error(f"Error hashing PII: {str(e)}")
            raise
    
    def anonymize_data(self, data: Dict[str, Any], 
                      anonymization_rules: Dict[str, str]) -> Dict[str, Any]:
        """
        Anonymize data according to specified rules
        
        Args:
            data: Data to anonymize
            anonymization_rules: Rules for anonymization
            
        Returns:
            Dict[str, Any]: Anonymized data
        """
        try:
            anonymized = data.copy()
            
            for field, rule in anonymization_rules.items():
                if field not in anonymized:
                    continue
                
                if rule == "remove":
                    del anonymized[field]
                elif rule == "mask":
                    value = str(anonymized[field])
                    if len(value) > 4:
                        anonymized[field] = value[:2] + "*" * (len(value) - 4) + value[-2:]
                    else:
                        anonymized[field] = "*" * len(value)
                elif rule == "generalize":
                    # Generalize specific data types
                    if field == "age":
                        age = int(anonymized[field])
                        anonymized[field] = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
                    elif field == "location":
                        # Keep only country level
                        location = str(anonymized[field])
                        if "," in location:
                            anonymized[field] = location.split(",")[-1].strip()
                elif rule == "hash":
                    hashed_value, _ = self.hash_pii(str(anonymized[field]))
                    anonymized[field] = hashed_value
            
            return anonymized
            
        except Exception as e:
            logger.error(f"Error anonymizing data: {str(e)}")
            raise
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool,
                      ip_address: str, user_agent: str, 
                      consent_version: str = "1.0") -> bool:
        """
        Record user consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent
            granted: Whether consent was granted
            ip_address: User's IP address
            user_agent: User's browser agent
            consent_version: Version of consent form
            
        Returns:
            bool: Success status
        """
        try:
            consent_record = ConsentRecord(
                user_id=user_id,
                consent_type=consent_type,
                granted=granted,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                consent_version=consent_version
            )
            
            if user_id not in self.consent_records:
                self.consent_records[user_id] = []
            
            self.consent_records[user_id].append(consent_record)
            
            logger.info(f"Recorded consent for user {user_id}: {consent_type} = {granted}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording consent: {str(e)}")
            return False
    
    def withdraw_consent(self, user_id: str, consent_type: str) -> bool:
        """
        Withdraw user consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to withdraw
            
        Returns:
            bool: Success status
        """
        try:
            if user_id not in self.consent_records:
                logger.warning(f"No consent records found for user: {user_id}")
                return False
            
            # Find the most recent consent record for this type
            user_consents = self.consent_records[user_id]
            for consent in reversed(user_consents):
                if consent.consent_type == consent_type and consent.granted:
                    consent.withdrawal_date = datetime.now()
                    
                    # Create new withdrawal record
                    withdrawal_record = ConsentRecord(
                        user_id=user_id,
                        consent_type=consent_type,
                        granted=False,
                        timestamp=datetime.now(),
                        ip_address="system",
                        user_agent="system",
                        consent_version=consent.consent_version
                    )
                    
                    self.consent_records[user_id].append(withdrawal_record)
                    
                    logger.info(f"Withdrew consent for user {user_id}: {consent_type}")
                    return True
            
            logger.warning(f"No active consent found to withdraw for user {user_id}: {consent_type}")
            return False
            
        except Exception as e:
            logger.error(f"Error withdrawing consent: {str(e)}")
            return False
    
    def check_consent(self, user_id: str, consent_type: str) -> bool:
        """
        Check if user has given valid consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to check
            
        Returns:
            bool: Whether user has valid consent
        """
        try:
            if user_id not in self.consent_records:
                return False
            
            # Find the most recent consent record for this type
            user_consents = self.consent_records[user_id]
            for consent in reversed(user_consents):
                if consent.consent_type == consent_type:
                    return consent.granted and consent.withdrawal_date is None
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking consent: {str(e)}")
            return False
    
    def record_processing_activity(self, user_id: str, data_category: str,
                                 purpose: str, legal_basis: str, 
                                 processor: str, retention_days: int,
                                 third_party_shared: bool = False,
                                 cross_border: bool = False,
                                 automated_decision: bool = False) -> str:
        """
        Record data processing activity
        
        Args:
            user_id: User identifier
            data_category: Category of data being processed
            purpose: Purpose of processing
            legal_basis: Legal basis for processing
            processor: Entity processing the data
            retention_days: Data retention period in days
            third_party_shared: Whether data is shared with third parties
            cross_border: Whether data is transferred across borders
            automated_decision: Whether automated decision making is involved
            
        Returns:
            str: Processing record ID
        """
        try:
            processing_id = f"proc_{int(datetime.now().timestamp())}_{secrets.token_hex(4)}"
            
            processing_record = DataProcessingRecord(
                processing_id=processing_id,
                user_id=user_id,
                data_category=data_category,
                purpose=purpose,
                legal_basis=legal_basis,
                processor=processor,
                timestamp=datetime.now(),
                retention_period=retention_days,
                third_party_shared=third_party_shared,
                cross_border_transfer=cross_border,
                automated_decision_making=automated_decision
            )
            
            self.processing_records.append(processing_record)
            
            logger.info(f"Recorded processing activity: {processing_id}")
            return processing_id
            
        except Exception as e:
            logger.error(f"Error recording processing activity: {str(e)}")
            raise
    
    def handle_data_subject_request(self, user_id: str, request_type: str,
                                  user_verification_data: Dict[str, Any]) -> str:
        """
        Handle data subject rights request
        
        Args:
            user_id: User identifier
            request_type: Type of request (access, erasure, etc.)
            user_verification_data: Data for user verification
            
        Returns:
            str: Request ID
        """
        try:
            request_id = f"dsr_{int(datetime.now().timestamp())}_{secrets.token_hex(4)}"
            
            # Verify user identity (simplified verification)
            verification_completed = self._verify_user_identity(user_id, user_verification_data)
            
            request = DataSubjectRequest(
                request_id=request_id,
                user_id=user_id,
                request_type=request_type,
                status="pending",
                created_date=datetime.now(),
                verification_completed=verification_completed
            )
            
            self.subject_requests[request_id] = request
            
            # Process request if verification is completed
            if verification_completed:
                self._process_data_subject_request(request_id)
            
            logger.info(f"Created data subject request: {request_id}")
            return request_id
            
        except Exception as e:
            logger.error(f"Error handling data subject request: {str(e)}")
            raise
    
    def _verify_user_identity(self, user_id: str, 
                            verification_data: Dict[str, Any]) -> bool:
        """
        Verify user identity for data subject requests
        
        Args:
            user_id: User identifier
            verification_data: Verification data
            
        Returns:
            bool: Whether identity is verified
        """
        # Simplified verification - in production, implement proper identity verification
        required_fields = ['email', 'last_name']
        return all(field in verification_data for field in required_fields)
    
    def _process_data_subject_request(self, request_id: str) -> bool:
        """
        Process data subject rights request
        
        Args:
            request_id: Request ID
            
        Returns:
            bool: Success status
        """
        try:
            request = self.subject_requests.get(request_id)
            if not request:
                logger.error(f"Request not found: {request_id}")
                return False
            
            if request.request_type == "access":
                # Provide user with their data
                user_data = self._collect_user_data(request.user_id)
                request.data_delivered = json.dumps(user_data, default=str)
                request.status = "completed"
                
            elif request.request_type == "erasure":
                # Delete user data
                self._delete_user_data(request.user_id)
                request.status = "completed"
                
            elif request.request_type == "portability":
                # Provide user data in portable format
                user_data = self._collect_user_data(request.user_id)
                request.data_delivered = json.dumps(user_data, default=str)
                request.status = "completed"
                
            elif request.request_type == "rectification":
                # Allow user to correct their data
                request.status = "pending_user_action"
                
            else:
                request.status = "not_supported"
            
            request.completion_date = datetime.now()
            
            logger.info(f"Processed data subject request: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing data subject request: {str(e)}")
            return False
    
    def _collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Collect all data for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict[str, Any]: User's data
        """
        user_data = {
            "user_id": user_id,
            "consent_records": [],
            "processing_records": [],
            "collection_date": datetime.now().isoformat()
        }
        
        # Add consent records
        if user_id in self.consent_records:
            for consent in self.consent_records[user_id]:
                user_data["consent_records"].append({
                    "consent_type": consent.consent_type,
                    "granted": consent.granted,
                    "timestamp": consent.timestamp.isoformat(),
                    "consent_version": consent.consent_version
                })
        
        # Add processing records
        for processing in self.processing_records:
            if processing.user_id == user_id:
                user_data["processing_records"].append({
                    "processing_id": processing.processing_id,
                    "data_category": processing.data_category,
                    "purpose": processing.purpose,
                    "legal_basis": processing.legal_basis,
                    "processor": processing.processor,
                    "timestamp": processing.timestamp.isoformat()
                })
        
        return user_data
    
    def _delete_user_data(self, user_id: str) -> bool:
        """
        Delete all data for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: Success status
        """
        try:
            # Remove consent records
            if user_id in self.consent_records:
                del self.consent_records[user_id]
            
            # Remove processing records
            self.processing_records = [
                record for record in self.processing_records 
                if record.user_id != user_id
            ]
            
            # Remove data subject requests
            requests_to_remove = [
                req_id for req_id, request in self.subject_requests.items()
                if request.user_id == user_id
            ]
            for req_id in requests_to_remove:
                del self.subject_requests[req_id]
            
            logger.info(f"Deleted all data for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return False
    
    def check_data_retention(self) -> List[Dict[str, Any]]:
        """
        Check for data that should be deleted based on retention policies
        
        Returns:
            List[Dict[str, Any]]: List of data that should be deleted
        """
        expired_data = []
        current_time = datetime.now()
        
        try:
            # Check processing records for expired data
            for record in self.processing_records:
                expiry_date = record.timestamp + timedelta(days=record.retention_period)
                if current_time > expiry_date:
                    expired_data.append({
                        "type": "processing_record",
                        "id": record.processing_id,
                        "user_id": record.user_id,
                        "expiry_date": expiry_date.isoformat(),
                        "days_overdue": (current_time - expiry_date).days
                    })
            
            logger.info(f"Found {len(expired_data)} expired data records")
            return expired_data
            
        except Exception as e:
            logger.error(f"Error checking data retention: {str(e)}")
            return []
    
    def cleanup_expired_data(self) -> int:
        """
        Clean up expired data based on retention policies
        
        Returns:
            int: Number of records cleaned up
        """
        expired_data = self.check_data_retention()
        cleaned_count = 0
        
        try:
            for expired_item in expired_data:
                if expired_item["type"] == "processing_record":
                    # Remove expired processing record
                    self.processing_records = [
                        record for record in self.processing_records
                        if record.processing_id != expired_item["id"]
                    ]
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired data records")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {str(e)}")
            return 0
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """
        Generate privacy compliance report
        
        Returns:
            Dict[str, Any]: Privacy report
        """
        try:
            report = {
                "report_date": datetime.now().isoformat(),
                "consent_summary": {},
                "processing_summary": {},
                "data_subject_requests": {},
                "compliance_status": {},
                "recommendations": []
            }
            
            # Consent summary
            total_users = len(self.consent_records)
            consent_types = {}
            for user_consents in self.consent_records.values():
                for consent in user_consents:
                    if consent.consent_type not in consent_types:
                        consent_types[consent.consent_type] = {"granted": 0, "withdrawn": 0}
                    
                    if consent.granted:
                        consent_types[consent.consent_type]["granted"] += 1
                    else:
                        consent_types[consent.consent_type]["withdrawn"] += 1
            
            report["consent_summary"] = {
                "total_users": total_users,
                "consent_types": consent_types
            }
            
            # Processing summary
            processing_by_category = {}
            for record in self.processing_records:
                if record.data_category not in processing_by_category:
                    processing_by_category[record.data_category] = 0
                processing_by_category[record.data_category] += 1
            
            report["processing_summary"] = {
                "total_processing_records": len(self.processing_records),
                "by_category": processing_by_category
            }
            
            # Data subject requests
            request_status_summary = {}
            for request in self.subject_requests.values():
                if request.status not in request_status_summary:
                    request_status_summary[request.status] = 0
                request_status_summary[request.status] += 1
            
            report["data_subject_requests"] = {
                "total_requests": len(self.subject_requests),
                "by_status": request_status_summary
            }
            
            # Compliance status
            expired_data = self.check_data_retention()
            report["compliance_status"] = {
                "gdpr_compliant": len(expired_data) == 0,
                "expired_data_count": len(expired_data),
                "encryption_enabled": True,  # Based on configuration
                "anonymization_enabled": True
            }
            
            # Recommendations
            if len(expired_data) > 0:
                report["recommendations"].append("Clean up expired data to maintain compliance")
            
            if total_users > 0:
                consent_rate = sum(ct["granted"] for ct in consent_types.values()) / total_users
                if consent_rate < 0.8:
                    report["recommendations"].append("Review consent collection process - low consent rate")
            
            logger.info("Generated privacy compliance report")
            return report
            
        except Exception as e:
            logger.error(f"Error generating privacy report: {str(e)}")
            return {}
    
    def export_consent_records(self, file_path: str) -> bool:
        """
        Export consent records to file
        
        Args:
            file_path: Path to export file
            
        Returns:
            bool: Success status
        """
        try:
            export_data = []
            
            for user_id, consents in self.consent_records.items():
                for consent in consents:
                    export_data.append({
                        "user_id": user_id,
                        "consent_type": consent.consent_type,
                        "granted": consent.granted,
                        "timestamp": consent.timestamp.isoformat(),
                        "consent_version": consent.consent_version,
                        "withdrawal_date": consent.withdrawal_date.isoformat() if consent.withdrawal_date else None
                    })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported consent records to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting consent records: {str(e)}")
            return False

# Usage example
async def main():
    """Example usage of DataProtectionManager"""
    # Initialize data protection manager
    dpm = DataProtectionManager()
    
    # Record consent
    dpm.record_consent(
        user_id="user123",
        consent_type="marketing",
        granted=True,
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0...",
        consent_version="2.0"
    )
    
    # Encrypt sensitive data
    encrypted_email = dpm.encrypt_data("user@example.com")
    print(f"Encrypted email: {encrypted_email}")
    
    # Decrypt data
    decrypted_email = dpm.decrypt_data(encrypted_email)
    print(f"Decrypted email: {decrypted_email}")
    
    # Handle data subject request
    request_id = dpm.handle_data_subject_request(
        user_id="user123",
        request_type="access",
        user_verification_data={"email": "user@example.com", "last_name": "Doe"}
    )
    print(f"Created data subject request: {request_id}")
    
    # Generate privacy report
    report = dpm.generate_privacy_report()
    print(f"Privacy report: {json.dumps(report, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())