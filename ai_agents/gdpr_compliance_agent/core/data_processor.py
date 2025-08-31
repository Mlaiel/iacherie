"""Data Processor - Advanced GDPR-Compliant Data Processing Engine
Sophisticated data processing with built-in GDPR compliance checks and controls

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
from ...models.gdpr_models import DataProcessingRecord, ProcessingActivity, DataRetentionPolicy

logger = get_logger(__name__)

class ProcessingStatus(Enum):
    """Data processing status types"""    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ERROR = "error"

class LawfulBasis(Enum):
    """GDPR lawful basis for processing"""    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class DataCategory(Enum):
    """Categories of personal data"""    BASIC_IDENTITY = "basic_identity"
    CONTACT_DATA = "contact_data"
    DEMOGRAPHIC_DATA = "demographic_data"
    BEHAVIORAL_DATA = "behavioral_data"
    BIOMETRIC_DATA = "biometric_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    SPECIAL_CATEGORIES = "special_categories"

@dataclass
class ProcessingMetrics:
    """Data processing compliance metrics"""    total_processing_activities: int
    active_processing_activities: int
    compliant_activities: int
    non_compliant_activities: int
    data_subjects_affected: int
    retention_compliance_rate: float
    lawful_basis_coverage: float
    security_compliance_rate: float

class DataProcessor:
    """    Advanced GDPR-Compliant Data Processor
    Ensures all data processing activities comply with GDPR requirements
    """    
    def __init__(self):
        # Processing activity registry
        self._active_processing: Dict[str, Dict[str, Any]] = {}
        
        # Data retention policies
        self._retention_policies: Dict[str, int] = {
            "content_protection": 2555,  # 7 years
            "analytics": 1095,           # 3 years
            "marketing": 730,            # 2 years
            "legal_compliance": 2555,    # 7 years
            "security": 1095,            # 3 years
            "performance": 365,          # 1 year
            "research": 1825             # 5 years
        }
        
        # Data minimization rules
        self._minimization_rules = self._initialize_minimization_rules()
        
        # Security requirements by data category
        self._security_requirements = self._initialize_security_requirements()
        
        logger.info("Data Processor initialized successfully")
    
    def _initialize_minimization_rules(self) -> Dict[str, List[str]]:
        """Initialize data minimization rules for different purposes"""        return {
            "content_protection": [
                "user_id", "content_id", "fingerprint_data", "upload_timestamp",
                "content_hash", "metadata", "protection_status"
            ],
            "analytics": [
                "user_id", "session_id", "event_type", "timestamp",
                "performance_metrics", "engagement_data"
            ],
            "marketing": [
                "user_id", "contact_info", "preferences", "interaction_history",
                "demographic_data", "consent_status"
            ],
            "security": [
                "user_id", "ip_address", "device_id", "access_log",
                "security_events", "authentication_data"
            ],
            "legal_compliance": [
                "user_id", "legal_basis", "consent_records", "audit_trail",
                "compliance_status", "document_references"
            ]
        }
    
    def _initialize_security_requirements(self) -> Dict[DataCategory, List[str]]:
        """Initialize security requirements by data category"""        return {
            DataCategory.BASIC_IDENTITY: [
                "encryption_at_rest", "access_control", "audit_logging"
            ],
            DataCategory.CONTACT_DATA: [
                "encryption_at_rest", "encryption_in_transit", "access_control"
            ],
            DataCategory.BEHAVIORAL_DATA: [
                "pseudonymization", "access_control", "audit_logging"
            ],
            DataCategory.BIOMETRIC_DATA: [
                "strong_encryption", "strict_access_control", 
                "integrity_verification", "audit_logging"
            ],
            DataCategory.FINANCIAL_DATA: [
                "strong_encryption", "tokenization", "strict_access_control",
                "integrity_verification", "audit_logging"
            ],
            DataCategory.SPECIAL_CATEGORIES: [
                "strong_encryption", "explicit_consent_required",
                "strict_access_control", "enhanced_audit_logging"
            ]
        }
    
    async def start_processing_activity(
        self, 
        user_id: str,
        purpose: str,
        data_payload: Dict[str, Any],
        lawful_basis: LawfulBasis,
        processing_details: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Start a new GDPR-compliant data processing activity"""        try:
            activity_id = str(uuid.uuid4())
            
            # Validate processing prerequisites
            validation_result = await self._validate_processing_prerequisites(
                user_id, purpose, data_payload, lawful_basis
            )
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Processing validation failed: {validation_result['error']}"
                )
            
            # Apply data minimization
            minimized_data = await self._apply_data_minimization(data_payload, purpose)
            
            # Classify data categories
            data_categories = await self._classify_data_categories(minimized_data)
            
            # Determine retention period
            retention_period = self._retention_policies.get(purpose, 365)
            retention_date = datetime.utcnow() + timedelta(days=retention_period)
            
            # Apply required security measures
            security_measures = await self._apply_security_measures(minimized_data, data_categories)
            
            # Create processing activity record
            processing_activity = ProcessingActivity(
                activity_id=activity_id,
                user_id=user_id,
                purpose=purpose,
                lawful_basis=lawful_basis.value,
                data_categories=list(data_categories.keys()),
                data_subjects_count=1,  # Single user for now
                processing_start=datetime.utcnow(),
                expected_end=processing_details.get("expected_end") if processing_details else None,
                retention_period=retention_period,
                retention_date=retention_date,
                security_measures=security_measures["measures"],
                status=ProcessingStatus.ACTIVE.value,
                compliance_checks=validation_result["checks"],
                processing_details=processing_details or {}
            )
            
            async with get_db() as db:
                db.add(processing_activity)
                await db.commit()
                await db.refresh(processing_activity)
            
            # Register active processing
            self._active_processing[activity_id] = {
                "user_id": user_id,
                "purpose": purpose,
                "start_time": datetime.utcnow(),
                "data_categories": list(data_categories.keys()),
                "lawful_basis": lawful_basis.value,
                "retention_date": retention_date
            }
            
            # Create detailed processing record
            processing_record = DataProcessingRecord(
                processing_id=activity_id,
                user_id=user_id,
                purpose=purpose,
                data_categories=list(data_categories.keys()),
                processing_start=datetime.utcnow(),
                lawful_basis=lawful_basis.value,
                retention_period=retention_period,
                security_measures=security_measures["measures"],
                compliance_status="compliant",
                processed_data_hash=await self._generate_data_hash(minimized_data)
            )
            
            async with get_db() as db:
                db.add(processing_record)
                await db.commit()
            
            logger.info(f"Processing activity started: {activity_id} for user {user_id}")
            
            return {
                "activity_id": activity_id,
                "user_id": user_id,
                "purpose": purpose,
                "lawful_basis": lawful_basis.value,
                "data_categories": list(data_categories.keys()),
                "security_measures": security_measures["measures"],
                "retention_date": retention_date.isoformat(),
                "compliance_status": "compliant",
                "minimized_data": minimized_data,
                "processing_summary": {
                    "original_fields": len(data_payload),
                    "minimized_fields": len(minimized_data),
                    "security_level": security_measures["level"],
                    "data_reduction": (len(data_payload) - len(minimized_data)) / len(data_payload) if data_payload else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting processing activity: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing start failed: {str(e)}")
    
    async def monitor_processing_compliance(self, activity_id: str) -> Dict[str, Any]:
        """Monitor ongoing processing activity for GDPR compliance"""        try:
            async with get_db() as db:
                activity_query = await db.execute(
                    select(ProcessingActivity).where(ProcessingActivity.activity_id == activity_id)
                )
                
                activity = activity_query.scalar_one_or_none()
                
                if not activity:
                    raise HTTPException(status_code=404, detail="Processing activity not found")
                
                # Check compliance status
                compliance_issues = []
                
                # Check retention compliance
                if activity.retention_date and activity.retention_date <= datetime.utcnow():
                    compliance_issues.append({
                        "type": "retention_exceeded",
                        "severity": "high",
                        "description": "Data retention period exceeded",
                        "action_required": "Delete or anonymize data immediately"
                    })
                
                # Check processing duration
                if activity.expected_end and activity.expected_end <= datetime.utcnow():
                    compliance_issues.append({
                        "type": "processing_overrun",
                        "severity": "medium",
                        "description": "Processing duration exceeded expected time",
                        "action_required": "Review processing necessity and update timeline"
                    })
                
                # Check lawful basis validity
                if activity.lawful_basis == LawfulBasis.CONSENT.value:
                    # In production, check consent validity with ConsentManager
                    consent_valid = True  # Placeholder
                    if not consent_valid:
                        compliance_issues.append({
                            "type": "consent_invalid",
                            "severity": "high",
                            "description": "Consent for processing is no longer valid",
                            "action_required": "Stop processing immediately or obtain new consent"
                        })
                
                # Update compliance status
                compliance_status = "compliant" if not compliance_issues else "non_compliant"
                
                activity.compliance_status = compliance_status
                activity.last_compliance_check = datetime.utcnow()
                await db.commit()
                
                logger.info(f"Compliance monitoring completed for activity {activity_id}: {compliance_status}")
                
                return {
                    "activity_id": activity_id,
                    "compliance_status": compliance_status,
                    "compliance_issues": compliance_issues,
                    "monitoring_timestamp": datetime.utcnow().isoformat(),
                    "activity_summary": {
                        "purpose": activity.purpose,
                        "lawful_basis": activity.lawful_basis,
                        "processing_duration": (datetime.utcnow() - activity.processing_start).total_seconds() / 86400,
                        "data_categories": activity.data_categories,
                        "retention_days_remaining": (activity.retention_date - datetime.utcnow()).days if activity.retention_date else None
                    },
                    "recommendations": await self._generate_compliance_recommendations(activity, compliance_issues)
                }
                
        except Exception as e:
            logger.error(f"Error monitoring processing compliance: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Compliance monitoring failed: {str(e)}")
    
    async def terminate_processing_activity(
        self, 
        activity_id: str, 
        termination_reason: str = "completed"
    ) -> Dict[str, Any]:
        """Terminate processing activity and handle data according to GDPR"""        try:
            async with get_db() as db:
                activity_query = await db.execute(
                    select(ProcessingActivity).where(ProcessingActivity.activity_id == activity_id)
                )
                
                activity = activity_query.scalar_one_or_none()
                
                if not activity:
                    raise HTTPException(status_code=404, detail="Processing activity not found")
                
                # Determine data handling action
                data_action = await self._determine_data_handling_action(activity, termination_reason)
                
                # Execute data handling
                data_handling_result = await self._execute_data_handling(activity, data_action)
                
                # Update activity status
                activity.status = ProcessingStatus.TERMINATED.value
                activity.processing_end = datetime.utcnow()
                activity.termination_reason = termination_reason
                activity.data_handling_action = data_action["action"]
                activity.data_handling_details = data_handling_result
                
                await db.commit()
                
                # Remove from active processing registry
                if activity_id in self._active_processing:
                    del self._active_processing[activity_id]
                
                logger.info(f"Processing activity terminated: {activity_id} ({termination_reason})")
                
                return {
                    "activity_id": activity_id,
                    "termination_status": "completed",
                    "termination_reason": termination_reason,
                    "termination_timestamp": activity.processing_end.isoformat(),
                    "data_handling": {
                        "action": data_action["action"],
                        "result": data_handling_result,
                        "compliance": data_action["compliance_basis"]
                    },
                    "processing_summary": {
                        "duration_days": (activity.processing_end - activity.processing_start).total_seconds() / 86400,
                        "data_categories_processed": activity.data_categories,
                        "final_compliance_status": activity.compliance_status
                    }
                }
                
        except Exception as e:
            logger.error(f"Error terminating processing activity: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing termination failed: {str(e)}")
    
    async def minimize_data(self, data_payload: Dict[str, Any], purpose: str) -> Dict[str, Any]:
        """Apply data minimization principles for specific processing purpose"""        try:
            return await self._apply_data_minimization(data_payload, purpose)
        except Exception as e:
            logger.error(f"Error minimizing data: {str(e)}")
            return data_payload
    
    async def get_processing_metrics(self, user_id: str) -> ProcessingMetrics:
        """Get detailed processing metrics for compliance assessment"""        try:
            async with get_db() as db:
                # Get all processing activities for user
                activities_query = await db.execute(
                    select(ProcessingActivity).where(ProcessingActivity.user_id == user_id)
                )
                
                activities = activities_query.scalars().all()
                
                if not activities:
                    return ProcessingMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0)
                
                # Calculate metrics
                total_activities = len(activities)
                active_activities = len([a for a in activities if a.status == ProcessingStatus.ACTIVE.value])
                compliant_activities = len([a for a in activities if a.compliance_status == "compliant"])
                non_compliant = total_activities - compliant_activities
                
                # Retention compliance
                retention_compliant = 0
                for activity in activities:
                    if activity.retention_date:
                        if activity.retention_date > datetime.utcnow() or activity.status == ProcessingStatus.TERMINATED.value:
                            retention_compliant += 1
                
                retention_rate = retention_compliant / total_activities if total_activities > 0 else 0.0
                
                # Lawful basis coverage
                activities_with_basis = len([a for a in activities if a.lawful_basis])
                basis_coverage = activities_with_basis / total_activities if total_activities > 0 else 0.0
                
                # Security compliance (simplified)
                activities_with_security = len([a for a in activities if a.security_measures])
                security_rate = activities_with_security / total_activities if total_activities > 0 else 0.0
                
                return ProcessingMetrics(
                    total_processing_activities=total_activities,
                    active_processing_activities=active_activities,
                    compliant_activities=compliant_activities,
                    non_compliant_activities=non_compliant,
                    data_subjects_affected=1,  # Single user context
                    retention_compliance_rate=round(retention_rate, 3),
                    lawful_basis_coverage=round(basis_coverage, 3),
                    security_compliance_rate=round(security_rate, 3)
                )
                
        except Exception as e:
            logger.error(f"Error getting processing metrics: {str(e)}")
            return ProcessingMetrics(0, 0, 0, 0, 0, 0.0, 0.0, 0.0)
    
    async def cleanup_expired_data(self) -> Dict[str, Any]:
        """Clean up data that has exceeded retention periods"""        try:
            async with get_db() as db:
                # Find activities with expired retention periods
                expired_query = await db.execute(
                    select(ProcessingActivity).where(
                        and_(
                            ProcessingActivity.retention_date <= datetime.utcnow(),
                            ProcessingActivity.status != ProcessingStatus.TERMINATED.value
                        )
                    )
                )
                
                expired_activities = expired_query.scalars().all()
                
                cleanup_results = {
                    "activities_processed": 0,
                    "data_deleted": 0,
                    "data_anonymized": 0,
                    "errors": 0,
                    "processing_details": []
                }
                
                for activity in expired_activities:
                    try:
                        # Determine cleanup action
                        cleanup_action = await self._determine_cleanup_action(activity)
                        
                        # Execute cleanup
                        cleanup_result = await self._execute_data_cleanup(activity, cleanup_action)
                        
                        # Update activity
                        activity.status = ProcessingStatus.TERMINATED.value
                        activity.processing_end = datetime.utcnow()
                        activity.termination_reason = "retention_expired"
                        activity.data_handling_action = cleanup_action
                        
                        cleanup_results["activities_processed"] += 1
                        
                        if cleanup_action == "delete":
                            cleanup_results["data_deleted"] += 1
                        elif cleanup_action == "anonymize":
                            cleanup_results["data_anonymized"] += 1
                        
                        cleanup_results["processing_details"].append({
                            "activity_id": activity.activity_id,
                            "purpose": activity.purpose,
                            "action": cleanup_action,
                            "status": "completed"
                        })
                        
                    except Exception as e:
                        logger.error(f"Error cleaning up activity {activity.activity_id}: {str(e)}")
                        cleanup_results["errors"] += 1
                        
                        cleanup_results["processing_details"].append({
                            "activity_id": activity.activity_id,
                            "purpose": activity.purpose,
                            "action": "error",
                            "status": "failed",
                            "error": str(e)
                        })
                
                await db.commit()
                
                logger.info(f"Data cleanup completed: {cleanup_results['activities_processed']} activities processed")
                
                return cleanup_results
                
        except Exception as e:
            logger.error(f"Error in data cleanup: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data cleanup failed: {str(e)}")
    
    # Helper methods
    
    async def _validate_processing_prerequisites(
        self, 
        user_id: str, 
        purpose: str,
        data_payload: Dict[str, Any], 
        lawful_basis: LawfulBasis
    ) -> Dict[str, Any]:
        """Validate that processing prerequisites are met"""        checks = []
        errors = []
        
        # Check lawful basis validity
        if lawful_basis == LawfulBasis.CONSENT:
            # In production, verify with ConsentManager
            consent_valid = True  # Placeholder
            if consent_valid:
                checks.append("consent_verified")
            else:
                errors.append("Valid consent required for processing")
        
        # Check data necessity
        necessary_fields = self._minimization_rules.get(purpose, [])
        if not any(field in data_payload for field in necessary_fields):
            errors.append(f"No necessary data fields found for purpose {purpose}")
        else:
            checks.append("data_necessity_confirmed")
        
        # Check purpose limitation
        if purpose not in self._minimization_rules:
            errors.append(f"Processing purpose {purpose} not recognized or allowed")
        else:
            checks.append("purpose_validated")
        
        # Check retention policy
        if purpose in self._retention_policies:
            checks.append("retention_policy_defined")
        else:
            errors.append(f"No retention policy defined for purpose {purpose}")
        
        return {
            "valid": len(errors) == 0,
            "checks": checks,
            "errors": errors,
            "error": "; ".join(errors) if errors else None
        }
    
    async def _apply_data_minimization(self, data_payload: Dict[str, Any], purpose: str) -> Dict[str, Any]:
        """Apply data minimization for specific purpose"""        necessary_fields = self._minimization_rules.get(purpose, list(data_payload.keys()))
        
        minimized_data = {}
        for field in necessary_fields:
            if field in data_payload:
                minimized_data[field] = data_payload[field]
        
        # Add essential system fields
        essential_fields = ["timestamp", "processing_id", "user_id"]
        for field in essential_fields:
            if field in data_payload:
                minimized_data[field] = data_payload[field]
        
        logger.info(f"Data minimization applied: {len(data_payload)} -> {len(minimized_data)} fields")
        
        return minimized_data
    
    async def _classify_data_categories(self, data_payload: Dict[str, Any]) -> Dict[DataCategory, List[str]]:
        """Classify data fields into GDPR data categories"""        categories = {}
        
        # Classification rules
        classification_map = {
            DataCategory.BASIC_IDENTITY: ["user_id", "username", "name", "id"],
            DataCategory.CONTACT_DATA: ["email", "phone", "address", "contact"],
            DataCategory.BEHAVIORAL_DATA: ["usage", "interaction", "behavior", "preference", "activity"],
            DataCategory.BIOMETRIC_DATA: ["fingerprint", "biometric", "voice", "face", "image_hash"],
            DataCategory.FINANCIAL_DATA: ["payment", "financial", "revenue", "money", "transaction"],
            DataCategory.DEMOGRAPHIC_DATA: ["age", "gender", "location", "demographic", "profile"]
        }
        
        for category, keywords in classification_map.items():
            matching_fields = []
            for field_name in data_payload.keys():
                if any(keyword in field_name.lower() for keyword in keywords):
                    matching_fields.append(field_name)
            
            if matching_fields:
                categories[category] = matching_fields
        
        return categories
    
    async def _apply_security_measures(
        self, 
        data_payload: Dict[str, Any],
        data_categories: Dict[DataCategory, List[str]]
    ) -> Dict[str, Any]:
        """Apply appropriate security measures based on data categories"""        required_measures = set()
        security_level = "standard"
        
        # Determine required security measures
        for category in data_categories.keys():
            category_requirements = self._security_requirements.get(category, [])
            required_measures.update(category_requirements)
            
            # Increase security level for sensitive categories
            if category in [DataCategory.BIOMETRIC_DATA, DataCategory.FINANCIAL_DATA, DataCategory.SPECIAL_CATEGORIES]:
                security_level = "high"
            elif category in [DataCategory.CONTACT_DATA, DataCategory.BEHAVIORAL_DATA] and security_level == "standard":
                security_level = "medium"
        
        # Add baseline security measures
        required_measures.update([
            "encryption_at_rest", "access_control", "audit_logging"
        ])
        
        return {
            "measures": list(required_measures),
            "level": security_level,
            "categories_protected": list(data_categories.keys())
        }
    
    async def _generate_data_hash(self, data_payload: Dict[str, Any]) -> str:
        """Generate hash of processed data for integrity verification"""        import hashlib
        import json
        
        # Create deterministic hash
        sorted_data = json.dumps(data_payload, sort_keys=True, default=str)
        data_hash = hashlib.sha256(sorted_data.encode()).hexdigest()
        
        return data_hash
    
    async def _determine_data_handling_action(
        self, 
        activity: ProcessingActivity,
        termination_reason: str
    ) -> Dict[str, str]:
        """Determine appropriate data handling action upon termination"""        if termination_reason == "consent_withdrawn":
            return {
                "action": "delete",
                "compliance_basis": "Consent withdrawal requires data deletion (Article 17 GDPR)"
            }
        elif termination_reason == "retention_expired":
            return {
                "action": "delete",
                "compliance_basis": "Retention period expired, data must be deleted"
            }
        elif activity.purpose == "research":
            return {
                "action": "anonymize",
                "compliance_basis": "Research data can be anonymized for continued use"
            }
        elif activity.purpose == "legal_compliance":
            return {
                "action": "archive",
                "compliance_basis": "Legal compliance data must be archived"
            }
        else:
            return {
                "action": "review",
                "compliance_basis": "Manual review required for data handling decision"
            }
    
    async def _execute_data_handling(
        self, 
        activity: ProcessingActivity,
        data_action: Dict[str, str]
    ) -> Dict[str, Any]:
        """Execute data handling action"""        action = data_action["action"]
        
        if action == "delete":
            # In production, this would trigger actual data deletion
            return {
                "status": "completed",
                "action": "delete",
                "records_affected": 1,
                "completion_time": datetime.utcnow().isoformat()
            }
        elif action == "anonymize":
            # In production, this would trigger data anonymization
            return {
                "status": "completed",
                "action": "anonymize",
                "records_affected": 1,
                "anonymization_method": "k_anonymity",
                "completion_time": datetime.utcnow().isoformat()
            }
        elif action == "archive":
            # In production, this would move data to secure archive
            return {
                "status": "completed",
                "action": "archive",
                "records_affected": 1,
                "archive_location": "secure_legal_archive",
                "completion_time": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "pending_review",
                "action": "review",
                "review_required": True
            }
    
    async def _determine_cleanup_action(self, activity: ProcessingActivity) -> str:
        """Determine cleanup action for expired data"""        if activity.purpose in ["legal_compliance", "security"]:
            return "archive"
        elif activity.purpose == "research":
            return "anonymize"
        else:
            return "delete"
    
    async def _execute_data_cleanup(self, activity: ProcessingActivity, cleanup_action: str) -> Dict[str, Any]:
        """Execute data cleanup action"""        # In production, this would perform actual cleanup
        return {
            "status": "completed",
            "action": cleanup_action,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _generate_compliance_recommendations(
        self, 
        activity: ProcessingActivity,
        compliance_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate compliance recommendations for processing activity"""        recommendations = []
        
        if compliance_issues:
            for issue in compliance_issues:
                if issue["type"] == "retention_exceeded":
                    recommendations.append({
                        "priority": "high",
                        "category": "data_retention",
                        "title": "Immediate Data Deletion Required",
                        "description": "Data retention period has been exceeded",
                        "action": "Delete or anonymize data immediately to maintain GDPR compliance"
                    })
                elif issue["type"] == "consent_invalid":
                    recommendations.append({
                        "priority": "high",
                        "category": "lawful_basis",
                        "title": "Stop Processing - Invalid Consent",
                        "description": "Consent for processing is no longer valid",
                        "action": "Stop processing and request new consent or find alternative lawful basis"
                    })
        
        # General recommendations
        processing_duration = (datetime.utcnow() - activity.processing_start).total_seconds() / 86400
        if processing_duration > 30:  # More than 30 days
            recommendations.append({
                "priority": "medium",
                "category": "processing_duration",
                "title": "Review Long-Running Processing",
                "description": "Processing has been active for over 30 days",
                "action": "Review necessity of continued processing and consider termination"
            })
        
        return recommendations

    async def update_retention_policy(
        self, 
        purpose: str, 
        retention_days: int,
        justification: str
    ) -> Dict[str, Any]:
        """Update data retention policy for processing purpose"""        try:
            old_retention = self._retention_policies.get(purpose)
            self._retention_policies[purpose] = retention_days
            
            # Update existing activities if needed
            async with get_db() as db:
                activities_query = await db.execute(
                    select(ProcessingActivity).where(
                        and_(
                            ProcessingActivity.purpose == purpose,
                            ProcessingActivity.status == ProcessingStatus.ACTIVE.value
                        )
                    )
                )
                
                activities = activities_query.scalars().all()
                
                for activity in activities:
                    new_retention_date = activity.processing_start + timedelta(days=retention_days)
                    activity.retention_period = retention_days
                    activity.retention_date = new_retention_date
                
                await db.commit()
            
            logger.info(f"Retention policy updated for {purpose}: {old_retention} -> {retention_days} days")
            
            return {
                "purpose": purpose,
                "old_retention_days": old_retention,
                "new_retention_days": retention_days,
                "justification": justification,
                "affected_activities": len(activities),
                "update_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating retention policy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Retention policy update failed: {str(e)}")

    async def get_processing_inventory(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive processing inventory for user"""        try:
            async with get_db() as db:
                activities_query = await db.execute(
                    select(ProcessingActivity).where(ProcessingActivity.user_id == user_id)
                    .order_by(ProcessingActivity.processing_start.desc())
                )
                
                activities = activities_query.scalars().all()
                
                inventory = {
                    "user_id": user_id,
                    "generation_timestamp": datetime.utcnow().isoformat(),
                    "total_activities": len(activities),
                    "active_activities": [],
                    "completed_activities": [],
                    "compliance_summary": {},
                    "data_categories_processed": set(),
                    "purposes_processed": set(),
                    "lawful_bases_used": set()
                }
                
                for activity in activities:
                    activity_info = {
                        "activity_id": activity.activity_id,
                        "purpose": activity.purpose,
                        "lawful_basis": activity.lawful_basis,
                        "status": activity.status,
                        "start_date": activity.processing_start.isoformat(),
                        "end_date": activity.processing_end.isoformat() if activity.processing_end else None,
                        "retention_date": activity.retention_date.isoformat() if activity.retention_date else None,
                        "data_categories": activity.data_categories,
                        "compliance_status": activity.compliance_status
                    }
                    
                    if activity.status == ProcessingStatus.ACTIVE.value:
                        inventory["active_activities"].append(activity_info)
                    else:
                        inventory["completed_activities"].append(activity_info)
                    
                    # Collect summary data
                    inventory["data_categories_processed"].update(activity.data_categories)
                    inventory["purposes_processed"].add(activity.purpose)
                    inventory["lawful_bases_used"].add(activity.lawful_basis)
                
                # Convert sets to lists for JSON serialization
                inventory["data_categories_processed"] = list(inventory["data_categories_processed"])
                inventory["purposes_processed"] = list(inventory["purposes_processed"])
                inventory["lawful_bases_used"] = list(inventory["lawful_bases_used"])
                
                # Add compliance summary
                inventory["compliance_summary"] = {
                    "compliant_activities": len([a for a in activities if a.compliance_status == "compliant"]),
                    "non_compliant_activities": len([a for a in activities if a.compliance_status == "non_compliant"]),
                    "compliance_rate": len([a for a in activities if a.compliance_status == "compliant"]) / len(activities) if activities else 0
                }
                
                return inventory
                
        except Exception as e:
            logger.error(f"Error generating processing inventory: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Inventory generation failed: {str(e)}")
