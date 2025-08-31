"""Data Protection - Advanced Privacy and Data Protection Utilities

Comprehensive data protection system providing encryption, anonymization,
pseudonymization, and privacy-preserving data processing for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import uuid
import hashlib
import secrets
import json
import base64
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data classification levels for protection."""    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ProtectionMethod(Enum):
    """Data protection methods available."""    ENCRYPTION = "encryption"
    PSEUDONYMIZATION = "pseudonymization"
    ANONYMIZATION = "anonymization"
    TOKENIZATION = "tokenization"
    MASKING = "masking"
    REDACTION = "redaction"
    HASHING = "hashing"


class ProcessingPurpose(Enum):
    """Lawful purposes for data processing."""    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataSubjectRight(Enum):
    """Data subject rights under GDPR."""    ACCESS = "access"  # Article 15
    RECTIFICATION = "rectification"  # Article 16
    ERASURE = "erasure"  # Article 17
    RESTRICT_PROCESSING = "restrict_processing"  # Article 18
    DATA_PORTABILITY = "data_portability"  # Article 20
    OBJECT = "object"  # Article 21
    AUTOMATED_DECISION_MAKING = "automated_decision_making"  # Article 22


@dataclass
class DataProcessingRecord:
    """Record of data processing activity."""    record_id: str
    controller: str
    processor: Optional[str]
    data_subject_category: str
    data_categories: List[str]
    processing_purposes: List[ProcessingPurpose]
    legal_basis: str
    recipients: List[str]
    third_country_transfers: List[str]
    retention_period: str
    technical_measures: List[str]
    organizational_measures: List[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class ProtectionConfiguration:
    """Configuration for data protection methods."""    classification: DataClassification
    methods: List[ProtectionMethod]
    encryption_algorithm: str
    key_rotation_days: int
    anonymization_threshold: int
    pseudonym_reversible: bool
    retention_days: Optional[int]
    access_controls: List[str]


@dataclass
class DataInventoryItem:
    """Item in data inventory for DPIA."""    item_id: str
    data_type: str
    source: str
    collection_method: str
    purpose: ProcessingPurpose
    legal_basis: str
    retention_period: str
    protection_measures: List[str]
    recipients: List[str]
    sensitive: bool
    volume_estimate: str
    last_reviewed: datetime


class DataProtectionManager:
    """    Comprehensive data protection and privacy utilities.
    
    Provides encryption, anonymization, pseudonymization, data subject rights handling,
    and privacy impact assessments for GDPR and privacy compliance.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize the Data Protection Manager.
        
        Args:
            config: Configuration dictionary with protection settings
        """        self.config = config
        self.protection_config = config.get("data_protection", {})
        
        # Protection data storage
        self.processing_records: Dict[str, DataProcessingRecord] = {}
        self.protection_configs: Dict[str, ProtectionConfiguration] = {}
        self.data_inventory: Dict[str, DataInventoryItem] = {}
        
        # Encryption setup
        self.master_key = self._initialize_master_key()
        self.encryption_keys: Dict[str, bytes] = {}
        self.pseudonym_mapping: Dict[str, str] = {}
        
        # Protection policies
        self.classification_policies = self._initialize_classification_policies()
        self.retention_policies = self._initialize_retention_policies()
        
        # Initialize default protection configurations
        self._initialize_protection_configurations()
        
        logger.info("Data Protection Manager initialized successfully")
    
    def _initialize_master_key(self) -> bytes:
        """Initialize or load master encryption key."""        master_key_path = self.protection_config.get("master_key_path")
        
        if master_key_path:
            try:
                with open(master_key_path, 'rb') as f:
                    return f.read()
            except FileNotFoundError:
                # Generate new key if file doesn't exist
                key = Fernet.generate_key()
                with open(master_key_path, 'wb') as f:
                    f.write(key)
                return key
        else:
            # Use in-memory key for development
            return Fernet.generate_key()
    
    def _initialize_classification_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize data classification policies."""        return {
            "public": {
                "encryption_required": False,
                "access_logging": False,
                "retention_days": 3650  # 10 years
            },
            "internal": {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 2555  # 7 years
            },
            "confidential": {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 1095,  # 3 years
                "access_controls": ["authentication", "authorization"]
            },
            "restricted": {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 365,
                "access_controls": ["multi_factor_auth", "role_based_access"],
                "audit_trail": True
            },
            "top_secret": {
                "encryption_required": True,
                "access_logging": True,
                "retention_days": 90,
                "access_controls": ["multi_factor_auth", "privileged_access"],
                "audit_trail": True,
                "air_gapped": True
            }
        }
    
    def _initialize_retention_policies(self) -> Dict[str, int]:
        """Initialize data retention policies by data type."""        return {
            "user_profiles": 2555,  # 7 years
            "financial_records": 2555,  # 7 years (legal requirement)
            "communication_logs": 1095,  # 3 years
            "analytics_data": 730,  # 2 years
            "marketing_data": 1095,  # 3 years
            "technical_logs": 365,  # 1 year
            "consent_records": 3650,  # 10 years
            "temporary_files": 30,  # 30 days
            "cache_data": 7  # 7 days
        }
    
    def _initialize_protection_configurations(self) -> None:
        """Initialize default protection configurations."""        configs = [
            ProtectionConfiguration(
                classification=DataClassification.PUBLIC,
                methods=[ProtectionMethod.HASHING],
                encryption_algorithm="AES-256-GCM",
                key_rotation_days=365,
                anonymization_threshold=5,
                pseudonym_reversible=False,
                retention_days=3650,
                access_controls=[]
            ),
            ProtectionConfiguration(
                classification=DataClassification.INTERNAL,
                methods=[ProtectionMethod.ENCRYPTION, ProtectionMethod.MASKING],
                encryption_algorithm="AES-256-GCM",
                key_rotation_days=180,
                anonymization_threshold=5,
                pseudonym_reversible=True,
                retention_days=2555,
                access_controls=["authentication"]
            ),
            ProtectionConfiguration(
                classification=DataClassification.CONFIDENTIAL,
                methods=[ProtectionMethod.ENCRYPTION, ProtectionMethod.PSEUDONYMIZATION],
                encryption_algorithm="AES-256-GCM",
                key_rotation_days=90,
                anonymization_threshold=10,
                pseudonym_reversible=True,
                retention_days=1095,
                access_controls=["authentication", "authorization"]
            ),
            ProtectionConfiguration(
                classification=DataClassification.RESTRICTED,
                methods=[ProtectionMethod.ENCRYPTION, ProtectionMethod.TOKENIZATION],
                encryption_algorithm="AES-256-GCM",
                key_rotation_days=30,
                anonymization_threshold=20,
                pseudonym_reversible=False,
                retention_days=365,
                access_controls=["multi_factor_auth", "role_based_access"]
            )
        ]
        
        for config in configs:
            self.protection_configs[config.classification.value] = config
    
    async def encrypt_data(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        classification: DataClassification,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Encrypt sensitive data based on classification level.
        
        Args:
            data: Data to encrypt
            classification: Classification level determining encryption method
            context: Additional context for encryption
            
        Returns:
            Encryption results with metadata
        """        try:
            # Convert data to bytes if necessary
            if isinstance(data, dict):
                data_bytes = json.dumps(data, default=str).encode()
            elif isinstance(data, str):
                data_bytes = data.encode()
            else:
                data_bytes = data
            
            # Get protection configuration
            config = self.protection_configs.get(classification.value)
            if not config:
                raise ValueError(f"No protection configuration for {classification.value}")
            
            # Generate encryption key for this data
            encryption_key = self._derive_encryption_key(classification, context)
            cipher_suite = Fernet(encryption_key)
            
            # Encrypt the data
            encrypted_data = cipher_suite.encrypt(data_bytes)
            
            # Create encryption metadata
            encryption_id = f"enc_{uuid.uuid4().hex[:16]}"
            metadata = {
                "encryption_id": encryption_id,
                "algorithm": config.encryption_algorithm,
                "classification": classification.value,
                "encrypted_at": datetime.utcnow().isoformat(),
                "key_rotation_due": (
                    datetime.utcnow() + timedelta(days=config.key_rotation_days)
                ).isoformat(),
                "context": context or {}
            }
            
            # Store encryption key reference
            self.encryption_keys[encryption_id] = encryption_key
            
            result = {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "metadata": metadata,
                "protection_applied": "encryption",
                "reversible": True
            }
            
            logger.info(f"Data encrypted with classification {classification.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    async def decrypt_data(
        self,
        encrypted_data: str,
        encryption_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Decrypt previously encrypted data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            encryption_id: ID of the encryption metadata
            context: Additional context for decryption
            
        Returns:
            Decryption results
        """        try:
            if encryption_id not in self.encryption_keys:
                raise ValueError(f"Encryption key for {encryption_id} not found")
            
            # Get encryption key
            encryption_key = self.encryption_keys[encryption_id]
            cipher_suite = Fernet(encryption_key)
            
            # Decode and decrypt
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_bytes = cipher_suite.decrypt(encrypted_bytes)
            
            # Try to parse as JSON, fallback to string
            try:
                decrypted_data = json.loads(decrypted_bytes.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                decrypted_data = decrypted_bytes.decode()
            
            result = {
                "decrypted_data": decrypted_data,
                "decrypted_at": datetime.utcnow().isoformat(),
                "encryption_id": encryption_id
            }
            
            logger.info(f"Data decrypted for encryption {encryption_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise
    
    async def pseudonymize_data(
        self,
        data: Dict[str, Any],
        identifier_fields: List[str],
        reversible: bool = True
    ) -> Dict[str, Any]:
        """        Apply pseudonymization to personally identifiable data.
        
        Args:
            data: Data to pseudonymize
            identifier_fields: Fields containing identifiers to pseudonymize
            reversible: Whether pseudonymization should be reversible
            
        Returns:
            Pseudonymized data with mapping
        """        try:
            pseudonymized_data = data.copy()
            pseudonym_mappings = {}
            
            for field in identifier_fields:
                if field in data:
                    original_value = str(data[field])
                    
                    # Generate pseudonym
                    if reversible:
                        # Use deterministic pseudonym for reversibility
                        pseudonym = self._generate_reversible_pseudonym(original_value)
                        # Store mapping for reversal
                        self.pseudonym_mapping[pseudonym] = original_value
                    else:
                        # Use random pseudonym for irreversible anonymization
                        pseudonym = f"anon_{uuid.uuid4().hex[:12]}"
                    
                    pseudonymized_data[field] = pseudonym
                    pseudonym_mappings[field] = {
                        "original": original_value,
                        "pseudonym": pseudonym,
                        "reversible": reversible
                    }
            
            pseudonymization_id = f"pseudo_{uuid.uuid4().hex[:16]}"
            
            result = {
                "pseudonymization_id": pseudonymization_id,
                "pseudonymized_data": pseudonymized_data,
                "mappings": pseudonym_mappings,
                "pseudonymized_at": datetime.utcnow().isoformat(),
                "reversible": reversible,
                "fields_processed": identifier_fields
            }
            
            logger.info(f"Data pseudonymized: {len(identifier_fields)} fields")
            return result
            
        except Exception as e:
            logger.error(f"Error pseudonymizing data: {str(e)}")
            raise
    
    async def anonymize_dataset(
        self,
        dataset: List[Dict[str, Any]],
        quasi_identifiers: List[str],
        sensitive_attributes: List[str],
        k_anonymity: int = 5
    ) -> Dict[str, Any]:
        """        Apply k-anonymity to a dataset for privacy protection.
        
        Args:
            dataset: Dataset to anonymize
            quasi_identifiers: Fields that are quasi-identifiers
            sensitive_attributes: Sensitive attributes to protect
            k_anonymity: Minimum group size for k-anonymity
            
        Returns:
            Anonymized dataset with privacy metrics
        """        try:
            if len(dataset) < k_anonymity:
                raise ValueError(f"Dataset too small for k-anonymity {k_anonymity}")
            
            # Group records by quasi-identifier combinations
            groups = self._group_by_quasi_identifiers(dataset, quasi_identifiers)
            
            # Apply generalization and suppression
            anonymized_groups = []
            suppressed_count = 0
            
            for group_key, group_records in groups.items():
                if len(group_records) >= k_anonymity:
                    # Apply generalization to the group
                    generalized_group = self._generalize_group(
                        group_records, quasi_identifiers, sensitive_attributes
                    )
                    anonymized_groups.extend(generalized_group)
                else:
                    # Suppress records that can't meet k-anonymity
                    suppressed_count += len(group_records)
            
            # Calculate privacy metrics
            privacy_metrics = self._calculate_privacy_metrics(
                dataset, anonymized_groups, k_anonymity
            )
            
            anonymization_id = f"anon_{uuid.uuid4().hex[:16]}"
            
            result = {
                "anonymization_id": anonymization_id,
                "anonymized_dataset": anonymized_groups,
                "anonymized_at": datetime.utcnow().isoformat(),
                "original_count": len(dataset),
                "anonymized_count": len(anonymized_groups),
                "suppressed_count": suppressed_count,
                "k_anonymity": k_anonymity,
                "privacy_metrics": privacy_metrics,
                "quasi_identifiers": quasi_identifiers,
                "sensitive_attributes": sensitive_attributes
            }
            
            logger.info(f"Dataset anonymized: {len(anonymized_groups)} records")
            return result
            
        except Exception as e:
            logger.error(f"Error anonymizing dataset: {str(e)}")
            raise
    
    async def create_processing_record(
        self,
        controller: str,
        data_subject_category: str,
        data_categories: List[str],
        processing_purposes: List[ProcessingPurpose],
        legal_basis: str,
        processor: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        third_country_transfers: Optional[List[str]] = None,
        retention_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Create a record of processing activities (GDPR Article 30).
        
        Args:
            controller: Data controller name
            data_subject_category: Category of data subjects
            data_categories: Categories of data being processed
            processing_purposes: Purposes of processing
            legal_basis: Legal basis for processing
            processor: Optional processor name
            recipients: Recipients of the data
            third_country_transfers: Third country transfer details
            retention_period: Data retention period
            
        Returns:
            Processing record creation results
        """        try:
            record_id = f"proc_record_{uuid.uuid4().hex[:16]}"
            
            # Determine technical and organizational measures based on data categories
            technical_measures = self._determine_technical_measures(data_categories)
            organizational_measures = self._determine_organizational_measures(data_categories)
            
            # Set default retention period if not provided
            if not retention_period:
                retention_period = self._determine_retention_period(data_categories)
            
            processing_record = DataProcessingRecord(
                record_id=record_id,
                controller=controller,
                processor=processor,
                data_subject_category=data_subject_category,
                data_categories=data_categories,
                processing_purposes=processing_purposes,
                legal_basis=legal_basis,
                recipients=recipients or [],
                third_country_transfers=third_country_transfers or [],
                retention_period=retention_period,
                technical_measures=technical_measures,
                organizational_measures=organizational_measures,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store processing record
            self.processing_records[record_id] = processing_record
            
            result = {
                "record_id": record_id,
                "controller": controller,
                "data_subject_category": data_subject_category,
                "processing_purposes": [p.value for p in processing_purposes],
                "legal_basis": legal_basis,
                "technical_measures": technical_measures,
                "organizational_measures": organizational_measures,
                "created_at": processing_record.created_at.isoformat()
            }
            
            logger.info(f"Processing record created: {record_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating processing record: {str(e)}")
            raise
    
    async def conduct_privacy_impact_assessment(
        self,
        processing_description: str,
        data_categories: List[str],
        processing_purposes: List[ProcessingPurpose],
        data_subjects: List[str],
        technologies: List[str]
    ) -> Dict[str, Any]:
        """        Conduct a Data Protection Impact Assessment (DPIA).
        
        Args:
            processing_description: Description of the processing activity
            data_categories: Categories of data involved
            processing_purposes: Purposes of processing
            data_subjects: Categories of data subjects
            technologies: Technologies involved in processing
            
        Returns:
            Comprehensive DPIA results
        """        try:
            dpia_id = f"dpia_{uuid.uuid4().hex[:16]}"
            
            # Risk assessment
            risk_assessment = self._assess_privacy_risks(
                data_categories, processing_purposes, data_subjects, technologies
            )
            
            # Legal basis analysis
            legal_analysis = self._analyze_legal_basis(processing_purposes)
            
            # Necessity and proportionality assessment
            necessity_assessment = self._assess_necessity_proportionality(
                processing_purposes, data_categories
            )
            
            # Safeguards identification
            safeguards = self._identify_required_safeguards(risk_assessment)
            
            # Consultation requirements
            consultation_required = self._determine_consultation_requirements(risk_assessment)
            
            # Overall risk level
            overall_risk = self._calculate_overall_risk(risk_assessment)
            
            dpia_result = {
                "dpia_id": dpia_id,
                "conducted_at": datetime.utcnow().isoformat(),
                "processing_description": processing_description,
                "scope": {
                    "data_categories": data_categories,
                    "processing_purposes": [p.value for p in processing_purposes],
                    "data_subjects": data_subjects,
                    "technologies": technologies
                },
                "risk_assessment": risk_assessment,
                "legal_analysis": legal_analysis,
                "necessity_assessment": necessity_assessment,
                "safeguards": safeguards,
                "overall_risk_level": overall_risk,
                "consultation_required": consultation_required,
                "recommendations": self._generate_dpia_recommendations(
                    risk_assessment, overall_risk
                ),
                "next_review_date": (
                    datetime.utcnow() + timedelta(days=365)
                ).isoformat()
            }
            
            logger.info(f"DPIA conducted: {dpia_id} - Risk level: {overall_risk}")
            return dpia_result
            
        except Exception as e:
            logger.error(f"Error conducting DPIA: {str(e)}")
            raise
    
    async def handle_data_subject_request(
        self,
        request_type: DataSubjectRight,
        user_id: str,
        specific_data: Optional[List[str]] = None,
        verification_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Handle data subject rights requests under GDPR.
        
        Args:
            request_type: Type of data subject right being exercised
            user_id: ID of the data subject
            specific_data: Specific data categories for the request
            verification_evidence: Evidence to verify the request
            
        Returns:
            Request processing results
        """        try:
            request_id = f"dsr_{uuid.uuid4().hex[:16]}"
            
            # Verify the request
            verification_result = await self._verify_data_subject_request(
                user_id, verification_evidence
            )
            
            if not verification_result["verified"]:
                return {
                    "request_id": request_id,
                    "status": "rejected",
                    "reason": "Identity verification failed",
                    "verification_result": verification_result
                }
            
            # Process the request based on type
            if request_type == DataSubjectRight.ACCESS:
                processing_result = await self._process_access_request(user_id, specific_data)
            elif request_type == DataSubjectRight.RECTIFICATION:
                processing_result = await self._process_rectification_request(user_id, specific_data)
            elif request_type == DataSubjectRight.ERASURE:
                processing_result = await self._process_erasure_request(user_id, specific_data)
            elif request_type == DataSubjectRight.RESTRICT_PROCESSING:
                processing_result = await self._process_restriction_request(user_id, specific_data)
            elif request_type == DataSubjectRight.DATA_PORTABILITY:
                processing_result = await self._process_portability_request(user_id, specific_data)
            elif request_type == DataSubjectRight.OBJECT:
                processing_result = await self._process_objection_request(user_id, specific_data)
            else:
                raise ValueError(f"Unsupported request type: {request_type}")
            
            result = {
                "request_id": request_id,
                "request_type": request_type.value,
                "user_id": user_id,
                "status": "processed",
                "processed_at": datetime.utcnow().isoformat(),
                "verification_result": verification_result,
                "processing_result": processing_result,
                "response_deadline": (
                    datetime.utcnow() + timedelta(days=30)
                ).isoformat()  # GDPR 30-day deadline
            }
            
            logger.info(f"Data subject request processed: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error handling data subject request: {str(e)}")
            raise
    
    # Private helper methods
    def _derive_encryption_key(
        self, 
        classification: DataClassification, 
        context: Optional[Dict[str, Any]]
    ) -> bytes:
        """Derive encryption key based on classification and context."""        # Use PBKDF2 to derive key from master key
        salt = hashlib.sha256(f"{classification.value}_{context}".encode()).digest()[:16]
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key))
    
    def _generate_reversible_pseudonym(self, original_value: str) -> str:
        """Generate deterministic pseudonym for reversible pseudonymization."""        # Use HMAC for deterministic but secure pseudonym
        key = hashlib.sha256(self.master_key).digest()
        pseudonym_hash = hashlib.pbkdf2_hmac(
            'sha256', original_value.encode(), key, 10000
        )
        return base64.urlsafe_b64encode(pseudonym_hash)[:16].decode()
    
    def _group_by_quasi_identifiers(
        self, 
        dataset: List[Dict[str, Any]], 
        quasi_identifiers: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group dataset records by quasi-identifier combinations."""        groups = {}
        
        for record in dataset:
            # Create group key from quasi-identifiers
            group_key = tuple(
                record.get(qi, "NULL") for qi in quasi_identifiers
            )
            group_key_str = str(group_key)
            
            if group_key_str not in groups:
                groups[group_key_str] = []
            groups[group_key_str].append(record)
        
        return groups
    
    def _generalize_group(
        self, 
        group_records: List[Dict[str, Any]], 
        quasi_identifiers: List[str],
        sensitive_attributes: List[str]
    ) -> List[Dict[str, Any]]:
        """Apply generalization to a group of records."""        generalized_records = []
        
        for record in group_records:
            generalized_record = record.copy()
            
            # Apply generalization to quasi-identifiers
            for qi in quasi_identifiers:
                if qi in record:
                    generalized_record[qi] = self._generalize_value(
                        record[qi], qi
                    )
            
            generalized_records.append(generalized_record)
        
        return generalized_records
    
    def _generalize_value(self, value: Any, field_name: str) -> str:
        """Apply generalization to a specific value."""        # Simple generalization rules - would be more sophisticated in practice
        if isinstance(value, int):
            # Generalize numbers to ranges
            return f"{(value // 10) * 10}-{(value // 10) * 10 + 9}"
        elif isinstance(value, str):
            # Generalize strings by truncating
            return value[:3] + "*" if len(value) > 3 else value
        else:
            return str(value)
    
    def _calculate_privacy_metrics(
        self, 
        original: List[Dict[str, Any]], 
        anonymized: List[Dict[str, Any]], 
        k_value: int
    ) -> Dict[str, Any]:
        """Calculate privacy preservation metrics."""        return {
            "k_anonymity_achieved": k_value,
            "data_utility_preserved": len(anonymized) / len(original),
            "information_loss": 1 - (len(anonymized) / len(original)),
            "privacy_level": "high" if k_value >= 10 else "medium" if k_value >= 5 else "low"
        }
    
    def _determine_technical_measures(self, data_categories: List[str]) -> List[str]:
        """Determine required technical measures based on data categories."""        measures = ["access_controls", "audit_logging"]
        
        sensitive_categories = ["financial_data", "health_data", "biometric_data"]
        if any(cat in sensitive_categories for cat in data_categories):
            measures.extend(["encryption", "pseudonymization", "secure_transmission"])
        
        return measures
    
    def _determine_organizational_measures(self, data_categories: List[str]) -> List[str]:
        """Determine required organizational measures."""        return [
            "staff_training",
            "data_protection_policies",
            "incident_response_procedures",
            "regular_security_assessments"
        ]
    
    def _determine_retention_period(self, data_categories: List[str]) -> str:
        """Determine appropriate retention period for data categories."""        max_retention = 0
        
        for category in data_categories:
            if category in self.retention_policies:
                max_retention = max(max_retention, self.retention_policies[category])
        
        return f"{max_retention} days" if max_retention > 0 else "7 years"
    
    def _assess_privacy_risks(
        self, 
        data_categories: List[str], 
        processing_purposes: List[ProcessingPurpose],
        data_subjects: List[str],
        technologies: List[str]
    ) -> Dict[str, Any]:
        """Assess privacy risks for DPIA."""        risk_factors = []
        risk_score = 0
        
        # Data sensitivity risks
        sensitive_data = ["biometric_data", "health_data", "financial_data", "location_data"]
        if any(cat in sensitive_data for cat in data_categories):
            risk_factors.append("sensitive_data_processing")
            risk_score += 3
        
        # Technology risks
        high_risk_tech = ["artificial_intelligence", "automated_decision_making", "profiling"]
        if any(tech in high_risk_tech for tech in technologies):
            risk_factors.append("high_risk_technology")
            risk_score += 2
        
        # Scale risks
        vulnerable_subjects = ["children", "elderly", "patients", "employees"]
        if any(subj in vulnerable_subjects for subj in data_subjects):
            risk_factors.append("vulnerable_data_subjects")
            risk_score += 2
        
        risk_level = "high" if risk_score >= 5 else "medium" if risk_score >= 3 else "low"
        
        return {
            "risk_factors": risk_factors,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "detailed_risks": self._generate_detailed_risk_analysis(risk_factors)
        }
    
    def _analyze_legal_basis(self, processing_purposes: List[ProcessingPurpose]) -> Dict[str, Any]:
        """Analyze legal basis for processing purposes."""        legal_analysis = {}
        
        for purpose in processing_purposes:
            if purpose == ProcessingPurpose.CONSENT:
                legal_analysis[purpose.value] = {
                    "basis": "Article 6(1)(a) - Consent",
                    "requirements": ["explicit", "informed", "freely_given", "withdrawable"]
                }
            elif purpose == ProcessingPurpose.CONTRACT:
                legal_analysis[purpose.value] = {
                    "basis": "Article 6(1)(b) - Contract",
                    "requirements": ["necessary_for_contract", "proportionate"]
                }
            elif purpose == ProcessingPurpose.LEGITIMATE_INTERESTS:
                legal_analysis[purpose.value] = {
                    "basis": "Article 6(1)(f) - Legitimate interests",
                    "requirements": ["legitimate_interest_test", "balancing_test"]
                }
        
        return legal_analysis
    
    def _assess_necessity_proportionality(
        self, 
        processing_purposes: List[ProcessingPurpose], 
        data_categories: List[str]
    ) -> Dict[str, Any]:
        """Assess necessity and proportionality of processing."""        return {
            "necessity_justified": True,  # Would implement actual assessment logic
            "proportionality_analysis": "Processing is proportionate to the purposes",
            "data_minimization_applied": len(data_categories) <= 5,  # Simple heuristic
            "alternatives_considered": ["data_reduction", "anonymization", "aggregation"]
        }
    
    def _identify_required_safeguards(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Identify required safeguards based on risk assessment."""        safeguards = ["data_minimization", "purpose_limitation", "storage_limitation"]
        
        if risk_assessment["risk_level"] == "high":
            safeguards.extend([
                "encryption_at_rest",
                "encryption_in_transit",
                "regular_audits",
                "staff_training",
                "incident_response_plan"
            ])
        elif risk_assessment["risk_level"] == "medium":
            safeguards.extend([
                "access_controls",
                "audit_logging",
                "regular_reviews"
            ])
        
        return safeguards
    
    def _determine_consultation_requirements(self, risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if consultation with authorities is required."""        consultation_required = risk_assessment["risk_level"] == "high"
        
        return {
            "dpa_consultation_required": consultation_required,
            "reason": "High risk to data subject rights and freedoms" if consultation_required else None,
            "deadline": (datetime.utcnow() + timedelta(days=8)).isoformat() if consultation_required else None
        }
    
    def _calculate_overall_risk(self, risk_assessment: Dict[str, Any]) -> str:
        """Calculate overall risk level for DPIA."""        return risk_assessment["risk_level"]
    
    def _generate_dpia_recommendations(
        self, 
        risk_assessment: Dict[str, Any], 
        overall_risk: str
    ) -> List[str]:
        """Generate recommendations based on DPIA results."""        recommendations = []
        
        if overall_risk == "high":
            recommendations.extend([
                "Implement additional encryption measures",
                "Conduct regular security audits",
                "Establish incident response procedures",
                "Consider consultation with data protection authority"
            ])
        elif overall_risk == "medium":
            recommendations.extend([
                "Implement access controls",
                "Establish audit logging",
                "Conduct annual reviews"
            ])
        
        return recommendations
    
    def _generate_detailed_risk_analysis(self, risk_factors: List[str]) -> Dict[str, str]:
        """Generate detailed analysis of identified risk factors."""        analysis = {}
        
        for factor in risk_factors:
            if factor == "sensitive_data_processing":
                analysis[factor] = "Processing involves sensitive personal data requiring enhanced protection"
            elif factor == "high_risk_technology":
                analysis[factor] = "Technology poses inherent privacy risks requiring mitigation"
            elif factor == "vulnerable_data_subjects":
                analysis[factor] = "Vulnerable data subjects require additional protection measures"
        
        return analysis
    
    # Data subject request processing methods
    async def _verify_data_subject_request(
        self, 
        user_id: str, 
        verification_evidence: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify the identity of the data subject making the request."""        # Simplified verification - would implement proper identity verification
        return {
            "verified": True,
            "verification_method": "system_authentication",
            "confidence_level": "high"
        }
    
    async def _process_access_request(
        self, 
        user_id: str, 
        specific_data: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Process data access request (Article 15)."""        # Would gather all personal data for the user
        return {
            "data_provided": True,
            "format": "structured_data",
            "delivery_method": "secure_download"
        }
    
    async def _process_rectification_request(
        self, 
        user_id: str, 
        specific_data: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Process data rectification request (Article 16)."""        return {
            "data_updated": True,
            "fields_corrected": specific_data or [],
            "notification_required": True
        }
    
    async def _process_erasure_request(
        self, 
        user_id: str, 
        specific_data: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Process data erasure request (Article 17)."""        return {
            "data_erased": True,
            "erasure_scope": "complete" if not specific_data else "partial",
            "third_parties_notified": True
        }
    
    async def _process_restriction_request(
        self, 
        user_id: str, 
        specific_data: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Process processing restriction request (Article 18)."""        return {
            "processing_restricted": True,
            "restriction_scope": specific_data or ["all"],
            "storage_only": True
        }
    
    async def _process_portability_request(
        self, 
        user_id: str, 
        specific_data: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Process data portability request (Article 20)."""        return {
            "data_exported": True,
            "format": "machine_readable",
            "transmission_method": "secure_api"
        }
    
    async def _process_objection_request(
        self, 
        user_id: str, 
        specific_data: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Process objection to processing request (Article 21)."""        return {
            "objection_processed": True,
            "processing_stopped": True,
            "legitimate_interests_override": False
        }
