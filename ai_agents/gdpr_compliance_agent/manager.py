"""
GDPR Compliance Manager - Main Agent Controller
Advanced GDPR compliance orchestration for content protection and user rights management

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from fastapi import HTTPException, BackgroundTasks

try:
    from core.database import get_db
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db = DatabaseManager
from ...core.logging import get_logger
from ...core.security import SecurityManager
from ...models.gdpr_models import (
    GDPRCompliance, DataProcessingRecord, ConsentRecord,
    DataSubjectRight, ComplianceAudit, DataBreach
)
from ...schemas.gdpr_schemas import (
    GDPRComplianceRequest, DataProcessingRequest, ConsentRequest,
    DataRightsRequest, ComplianceReportRequest
)

from .data_handler import DataPrivacyHandler
from .consent_manager import ConsentManager
from .data_processor import DataProcessor
from .anonymization_engine import AnonymizationEngine
from .audit_logger import ComplianceAuditLogger
from .rights_manager import DataRightsManager
from .breach_detector import DataBreachDetector
from .policy_engine import PrivacyPolicyEngine
from .reporting_engine import ComplianceReportingEngine

logger = get_logger(__name__)

class ComplianceLevel(Enum):
    """GDPR compliance levels for different processing types"""
    STRICT = "strict"
    STANDARD = "standard"
    MINIMAL = "minimal"
    RESEARCH = "research"

class ProcessingPurpose(Enum):
    """Data processing purposes according to GDPR"""
    CONTENT_PROTECTION = "content_protection"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    LEGAL_COMPLIANCE = "legal_compliance"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RESEARCH = "research"

@dataclass
class ComplianceMetrics:
    """GDPR compliance metrics tracking"""
    consent_rate: float
    processing_compliance: float
    data_subject_requests: int
    breach_incidents: int
    audit_score: float
    last_assessment: datetime

class GDPRComplianceManager:
    """
    Advanced GDPR Compliance Manager
    Orchestrates all GDPR compliance operations for content creators and platform users
    """
    
    def __init__(self):
        self.data_handler = DataPrivacyHandler()
        self.consent_manager = ConsentManager()
        self.data_processor = DataProcessor()
        self.anonymization_engine = AnonymizationEngine()
        self.audit_logger = ComplianceAuditLogger()
        self.rights_manager = DataRightsManager()
        self.breach_detector = DataBreachDetector()
        self.policy_engine = PrivacyPolicyEngine()
        self.reporting_engine = ComplianceReportingEngine()
        self.security_manager = SecurityManager()
        
        self._active_processing_sessions: Dict[str, Dict] = {}
        self._compliance_cache: Dict[str, ComplianceMetrics] = {}
        
        logger.info("GDPR Compliance Manager initialized successfully")
    
    async def initialize_compliance_framework(self, user_id: str, compliance_level: ComplianceLevel) -> Dict[str, Any]:
        """Initialize GDPR compliance framework for a user/creator"""
        try:
            async with get_db() as db:
                # Check existing compliance record
                existing_compliance = await db.execute(
                    select(GDPRCompliance).where(GDPRCompliance.user_id == user_id)
                )
                compliance_record = existing_compliance.scalar_one_or_none()
                
                if not compliance_record:
                    # Create new compliance record
                    compliance_record = GDPRCompliance(
                        user_id=user_id,
                        compliance_level=compliance_level.value,
                        created_at=datetime.utcnow(),
                        last_updated=datetime.utcnow(),
                        consent_status={},
                        processing_purposes=[],
                        data_retention_policy={},
                        audit_trail=[]
                    )
                    db.add(compliance_record)
                    await db.commit()
                    await db.refresh(compliance_record)
                
                # Initialize consent framework
                await self.consent_manager.initialize_consent_framework(user_id)
                
                # Setup privacy policy
                privacy_policy = await self.policy_engine.generate_privacy_policy(
                    user_id, compliance_level
                )
                
                # Log initialization
                await self.audit_logger.log_compliance_event(
                    user_id=user_id,
                    event_type="framework_initialization",
                    details={
                        "compliance_level": compliance_level.value,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
                logger.info(f"GDPR compliance framework initialized for user {user_id}")
                
                return {
                    "compliance_id": str(compliance_record.id),
                    "user_id": user_id,
                    "compliance_level": compliance_level.value,
                    "privacy_policy": privacy_policy,
                    "status": "initialized",
                    "next_steps": await self._get_compliance_next_steps(user_id)
                }
                
        except Exception as e:
            logger.error(f"Error initializing compliance framework: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Compliance initialization failed: {str(e)}")
    
    async def process_data_with_compliance(
        self, 
        user_id: str, 
        data_payload: Dict[str, Any], 
        purpose: ProcessingPurpose,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Process data with full GDPR compliance checking"""
        try:
            processing_id = str(uuid.uuid4())
            
            # Verify consent for processing purpose
            consent_valid = await self.consent_manager.verify_consent(user_id, purpose.value)
            if not consent_valid:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Valid consent required for {purpose.value} processing"
                )
            
            # Check data minimization
            minimized_data = await self.data_processor.minimize_data(
                data_payload, purpose
            )
            
            # Apply anonymization if required
            processing_data = await self.anonymization_engine.process_data(
                minimized_data, user_id, purpose
            )
            
            # Record processing activity
            processing_record = DataProcessingRecord(
                processing_id=processing_id,
                user_id=user_id,
                purpose=purpose.value,
                data_categories=list(processing_data.keys()),
                processing_start=datetime.utcnow(),
                lawful_basis="consent",
                retention_period=await self._calculate_retention_period(purpose),
                security_measures=await self._get_security_measures(purpose)
            )
            
            async with get_db() as db:
                db.add(processing_record)
                await db.commit()
            
            # Store active processing session
            self._active_processing_sessions[processing_id] = {
                "user_id": user_id,
                "purpose": purpose.value,
                "start_time": datetime.utcnow(),
                "data_categories": list(processing_data.keys())
            }
            
            # Schedule compliance monitoring
            background_tasks.add_task(
                self._monitor_processing_compliance,
                processing_id,
                user_id,
                purpose
            )
            
            # Log processing activity
            await self.audit_logger.log_data_processing(
                user_id=user_id,
                processing_id=processing_id,
                purpose=purpose.value,
                data_categories=list(processing_data.keys())
            )
            
            logger.info(f"Data processing started with compliance for user {user_id}")
            
            return {
                "processing_id": processing_id,
                "user_id": user_id,
                "purpose": purpose.value,
                "processed_data": processing_data,
                "compliance_status": "compliant",
                "retention_until": (datetime.utcnow() + timedelta(days=await self._calculate_retention_period(purpose))).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in compliant data processing: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Compliant processing failed: {str(e)}")
    
    async def handle_data_subject_request(
        self, 
        user_id: str, 
        request_type: str, 
        request_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle data subject rights requests (access, rectification, erasure, etc.)"""
        try:
            request_id = str(uuid.uuid4())
            
            # Validate request type
            valid_requests = [
                "access", "rectification", "erasure", "restriction",
                "portability", "objection", "withdraw_consent"
            ]
            
            if request_type not in valid_requests:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid request type. Valid types: {valid_requests}"
                )
            
            # Process request through rights manager
            result = await self.rights_manager.process_subject_right_request(
                user_id=user_id,
                request_type=request_type,
                request_details=request_details,
                request_id=request_id
            )
            
            # Create audit record
            rights_record = DataSubjectRight(
                request_id=request_id,
                user_id=user_id,
                request_type=request_type,
                request_details=request_details,
                status="processing",
                created_at=datetime.utcnow(),
                response_deadline=datetime.utcnow() + timedelta(days=30)
            )
            
            async with get_db() as db:
                db.add(rights_record)
                await db.commit()
            
            # Log request
            await self.audit_logger.log_rights_request(
                user_id=user_id,
                request_id=request_id,
                request_type=request_type,
                details=request_details
            )
            
            logger.info(f"Data subject rights request processed: {request_type} for user {user_id}")
            
            return {
                "request_id": request_id,
                "user_id": user_id,
                "request_type": request_type,
                "status": "processing",
                "estimated_completion": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling data subject request: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Rights request failed: {str(e)}")
    
    async def conduct_compliance_assessment(self, user_id: str) -> Dict[str, Any]:
        """Conduct comprehensive GDPR compliance assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            assessment_start = datetime.utcnow()
            
            # Gather compliance metrics
            consent_metrics = await self.consent_manager.get_consent_metrics(user_id)
            processing_metrics = await self.data_processor.get_processing_metrics(user_id)
            security_metrics = await self.security_manager.get_security_metrics(user_id)
            rights_metrics = await self.rights_manager.get_rights_fulfillment_metrics(user_id)
            
            # Calculate compliance score
            compliance_score = await self._calculate_compliance_score(
                consent_metrics, processing_metrics, security_metrics, rights_metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                user_id, compliance_score, consent_metrics, processing_metrics
            )
            
            # Create assessment record
            assessment_record = ComplianceAudit(
                audit_id=assessment_id,
                user_id=user_id,
                audit_type="compliance_assessment",
                audit_date=assessment_start,
                findings={
                    "consent_metrics": consent_metrics,
                    "processing_metrics": processing_metrics,
                    "security_metrics": security_metrics,
                    "rights_metrics": rights_metrics
                },
                compliance_score=compliance_score,
                recommendations=recommendations,
                status="completed"
            )
            
            async with get_db() as db:
                db.add(assessment_record)
                await db.commit()
            
            # Update compliance cache
            self._compliance_cache[user_id] = ComplianceMetrics(
                consent_rate=consent_metrics.get("consent_rate", 0.0),
                processing_compliance=processing_metrics.get("compliance_rate", 0.0),
                data_subject_requests=rights_metrics.get("total_requests", 0),
                breach_incidents=security_metrics.get("breach_count", 0),
                audit_score=compliance_score,
                last_assessment=assessment_start
            )
            
            logger.info(f"Compliance assessment completed for user {user_id}: {compliance_score}/100")
            
            return {
                "assessment_id": assessment_id,
                "user_id": user_id,
                "compliance_score": compliance_score,
                "assessment_date": assessment_start.isoformat(),
                "metrics": {
                    "consent": consent_metrics,
                    "processing": processing_metrics,
                    "security": security_metrics,
                    "rights": rights_metrics
                },
                "recommendations": recommendations,
                "status": "completed" if compliance_score >= 80 else "requires_attention"
            }
            
        except Exception as e:
            logger.error(f"Error conducting compliance assessment: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")
    
    async def detect_and_handle_breach(
        self, 
        incident_data: Dict[str, Any], 
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Detect and handle potential data breach incidents"""
        try:
            breach_id = str(uuid.uuid4())
            
            # Analyze incident through breach detector
            breach_analysis = await self.breach_detector.analyze_incident(
                incident_data, breach_id
            )
            
            if breach_analysis["is_breach"]:
                # Handle confirmed breach
                breach_response = await self._handle_confirmed_breach(
                    breach_id, incident_data, breach_analysis, background_tasks
                )
                
                # Create breach record
                breach_record = DataBreach(
                    breach_id=breach_id,
                    detected_at=datetime.utcnow(),
                    incident_type=incident_data.get("incident_type", "unknown"),
                    affected_users=breach_analysis.get("affected_users", []),
                    severity_level=breach_analysis.get("severity", "medium"),
                    containment_status="in_progress",
                    notification_required=breach_analysis.get("notification_required", True),
                    regulatory_notification_deadline=datetime.utcnow() + timedelta(hours=72),
                    breach_details=incident_data
                )
                
                async with get_db() as db:
                    db.add(breach_record)
                    await db.commit()
                
                logger.warning(f"Data breach detected and being handled: {breach_id}")
                
                return {
                    "breach_id": breach_id,
                    "is_breach": True,
                    "severity": breach_analysis["severity"],
                    "affected_users_count": len(breach_analysis.get("affected_users", [])),
                    "notification_required": breach_analysis["notification_required"],
                    "response_actions": breach_response["actions"],
                    "regulatory_deadline": (datetime.utcnow() + timedelta(hours=72)).isoformat()
                }
            
            else:
                # Log false positive
                await self.audit_logger.log_security_event(
                    event_type="breach_false_positive",
                    incident_id=breach_id,
                    details=incident_data
                )
                
                return {
                    "incident_id": breach_id,
                    "is_breach": False,
                    "analysis": breach_analysis,
                    "status": "no_action_required"
                }
                
        except Exception as e:
            logger.error(f"Error in breach detection and handling: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Breach handling failed: {str(e)}")
    
    async def generate_compliance_report(
        self, 
        user_id: str, 
        report_type: str, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive GDPR compliance report"""
        try:
            # Generate report through reporting engine
            report = await self.reporting_engine.generate_report(
                user_id=user_id,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end
            )
            
            # Add compliance assessment
            current_assessment = await self.conduct_compliance_assessment(user_id)
            report["current_compliance"] = current_assessment
            
            # Log report generation
            await self.audit_logger.log_compliance_event(
                user_id=user_id,
                event_type="report_generation",
                details={
                    "report_type": report_type,
                    "period": f"{period_start.isoformat()} to {period_end.isoformat()}"
                }
            )
            
            logger.info(f"Compliance report generated for user {user_id}: {report_type}")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
    
    async def _handle_confirmed_breach(
        self, 
        breach_id: str, 
        incident_data: Dict[str, Any], 
        analysis: Dict[str, Any],
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Handle confirmed data breach with all required actions"""
        try:
            response_actions = []
            
            # Immediate containment
            containment_result = await self.breach_detector.contain_breach(
                breach_id, incident_data
            )
            response_actions.extend(containment_result.get("actions", []))
            
            # Notify affected users
            if analysis.get("affected_users"):
                background_tasks.add_task(
                    self._notify_affected_users,
                    analysis["affected_users"],
                    breach_id,
                    incident_data
                )
                response_actions.append("user_notification_scheduled")
            
            # Prepare regulatory notification if required
            if analysis.get("notification_required", True):
                background_tasks.add_task(
                    self._prepare_regulatory_notification,
                    breach_id,
                    incident_data,
                    analysis
                )
                response_actions.append("regulatory_notification_prepared")
            
            # Schedule forensic investigation
            background_tasks.add_task(
                self._conduct_breach_investigation,
                breach_id,
                incident_data
            )
            response_actions.append("investigation_scheduled")
            
            return {
                "breach_id": breach_id,
                "actions": response_actions,
                "containment_status": containment_result.get("status", "in_progress"),
                "next_steps": [
                    "Monitor containment effectiveness",
                    "Complete user notifications within 24h",
                    "Submit regulatory notification within 72h",
                    "Conduct full investigation"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error handling confirmed breach: {str(e)}")
            raise
    
    async def _calculate_compliance_score(
        self, 
        consent_metrics: Dict, 
        processing_metrics: Dict, 
        security_metrics: Dict, 
        rights_metrics: Dict
    ) -> float:
        """Calculate overall GDPR compliance score"""
        try:
            # Weight factors for different compliance areas
            weights = {
                "consent": 0.30,
                "processing": 0.25,
                "security": 0.25,
                "rights": 0.20
            }
            
            # Calculate weighted scores
            consent_score = consent_metrics.get("consent_rate", 0) * 100
            processing_score = processing_metrics.get("compliance_rate", 0) * 100
            security_score = min(100, security_metrics.get("security_score", 0))
            rights_score = rights_metrics.get("fulfillment_rate", 0) * 100
            
            # Calculate overall score
            overall_score = (
                consent_score * weights["consent"] +
                processing_score * weights["processing"] +
                security_score * weights["security"] +
                rights_score * weights["rights"]
            )
            
            return round(overall_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {str(e)}")
            return 0.0
    
    async def _generate_compliance_recommendations(
        self, 
        user_id: str, 
        compliance_score: float, 
        consent_metrics: Dict, 
        processing_metrics: Dict
    ) -> List[Dict[str, Any]]:
        """Generate actionable compliance recommendations"""
        recommendations = []
        
        try:
            if compliance_score < 80:
                recommendations.append({
                    "priority": "high",
                    "category": "overall_compliance",
                    "title": "Improve Overall Compliance",
                    "description": "Compliance score below recommended threshold",
                    "action_required": "Conduct detailed compliance review"
                })
            
            if consent_metrics.get("consent_rate", 0) < 0.9:
                recommendations.append({
                    "priority": "high",
                    "category": "consent_management",
                    "title": "Improve Consent Collection",
                    "description": "Consent rate below 90%",
                    "action_required": "Review and update consent mechanisms"
                })
            
            if processing_metrics.get("retention_compliance", 0) < 0.95:
                recommendations.append({
                    "priority": "medium",
                    "category": "data_retention",
                    "title": "Review Data Retention",
                    "description": "Some data may be retained longer than necessary",
                    "action_required": "Implement automated data deletion policies"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    async def _monitor_processing_compliance(
        self, 
        processing_id: str, 
        user_id: str, 
        purpose: ProcessingPurpose
    ) -> None:
        """Background task to monitor ongoing processing compliance"""
        try:
            # Monitor for compliance violations
            await asyncio.sleep(60)  # Wait before starting monitoring
            
            while processing_id in self._active_processing_sessions:
                session = self._active_processing_sessions[processing_id]
                
                # Check if processing is still within acceptable timeframe
                processing_duration = datetime.utcnow() - session["start_time"]
                
                if processing_duration > timedelta(hours=24):
                    # Log long-running processing
                    await self.audit_logger.log_compliance_event(
                        user_id=user_id,
                        event_type="long_processing_detected",
                        details={
                            "processing_id": processing_id,
                            "duration_hours": processing_duration.total_seconds() / 3600
                        }
                    )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
        except Exception as e:
            logger.error(f"Error monitoring processing compliance: {str(e)}")
    
    async def _get_compliance_next_steps(self, user_id: str) -> List[str]:
        """Get recommended next steps for compliance setup"""
        return [
            "Configure consent preferences",
            "Review data processing purposes",
            "Set up automated data retention policies",
            "Configure privacy dashboard access",
            "Schedule regular compliance assessments"
        ]
    
    async def _calculate_retention_period(self, purpose: ProcessingPurpose) -> int:
        """Calculate data retention period in days based on processing purpose"""
        retention_periods = {
            ProcessingPurpose.CONTENT_PROTECTION: 2555,  # 7 years
            ProcessingPurpose.ANALYTICS: 1095,           # 3 years
            ProcessingPurpose.MARKETING: 730,            # 2 years
            ProcessingPurpose.LEGAL_COMPLIANCE: 2555,    # 7 years
            ProcessingPurpose.SECURITY: 1095,            # 3 years
            ProcessingPurpose.PERFORMANCE: 365,          # 1 year
            ProcessingPurpose.RESEARCH: 1825             # 5 years
        }
        
        return retention_periods.get(purpose, 365)  # Default 1 year
    
    async def _get_security_measures(self, purpose: ProcessingPurpose) -> List[str]:
        """Get required security measures for processing purpose"""
        base_measures = [
            "encryption_at_rest",
            "encryption_in_transit",
            "access_logging",
            "authentication_required"
        ]
        
        if purpose in [ProcessingPurpose.CONTENT_PROTECTION, ProcessingPurpose.LEGAL_COMPLIANCE]:
            base_measures.extend([
                "advanced_encryption",
                "integrity_verification",
                "audit_trail",
                "backup_encryption"
            ])
        
        return base_measures
    
    async def _notify_affected_users(
        self, 
        affected_users: List[str], 
        breach_id: str, 
        incident_data: Dict[str, Any]
    ) -> None:
        """Notify users affected by data breach"""
        try:
            for user_id in affected_users:
                # Send breach notification
                await self.audit_logger.log_breach_notification(
                    user_id=user_id,
                    breach_id=breach_id,
                    incident_details=incident_data
                )
            
            logger.info(f"Breach notifications sent to {len(affected_users)} users")
            
        except Exception as e:
            logger.error(f"Error notifying affected users: {str(e)}")
    
    async def _prepare_regulatory_notification(
        self, 
        breach_id: str, 
        incident_data: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Prepare regulatory notification for data breach"""
        try:
            # Prepare notification document
            notification_doc = {
                "breach_id": breach_id,
                "incident_timestamp": incident_data.get("timestamp", datetime.utcnow().isoformat()),
                "nature_of_breach": analysis.get("breach_type", "unknown"),
                "affected_data_categories": analysis.get("data_categories", []),
                "approximate_affected_users": len(analysis.get("affected_users", [])),
                "likely_consequences": analysis.get("consequences", ""),
                "measures_taken": analysis.get("containment_measures", []),
                "contact_information": {
                    "dpo_name": "Data Protection Officer",
                    "dpo_email": "dpo@ia-influencer.com",
                    "contact_phone": "+49-xxx-xxx-xxxx"
                }
            }
            
            # Log regulatory notification preparation
            await self.audit_logger.log_regulatory_action(
                action_type="breach_notification_prepared",
                breach_id=breach_id,
                notification_details=notification_doc
            )
            
            logger.info(f"Regulatory notification prepared for breach {breach_id}")
            
        except Exception as e:
            logger.error(f"Error preparing regulatory notification: {str(e)}")
    
    async def _conduct_breach_investigation(
        self, 
        breach_id: str, 
        incident_data: Dict[str, Any]
    ) -> None:
        """Conduct detailed breach investigation"""
        try:
            # Start investigation process
            investigation_result = await self.breach_detector.investigate_breach(
                breach_id, incident_data
            )
            
            # Log investigation completion
            await self.audit_logger.log_investigation_result(
                breach_id=breach_id,
                investigation_details=investigation_result
            )
            
            logger.info(f"Breach investigation completed for {breach_id}")
            
        except Exception as e:
            logger.error(f"Error conducting breach investigation: {str(e)}")

    async def get_compliance_status(self, user_id: str) -> Dict[str, Any]:
        """Get current compliance status for user"""
        try:
            if user_id in self._compliance_cache:
                metrics = self._compliance_cache[user_id]
                
                return {
                    "user_id": user_id,
                    "compliance_score": metrics.audit_score,
                    "consent_rate": metrics.consent_rate,
                    "processing_compliance": metrics.processing_compliance,
                    "data_subject_requests": metrics.data_subject_requests,
                    "breach_incidents": metrics.breach_incidents,
                    "last_assessment": metrics.last_assessment.isoformat(),
                    "status": "compliant" if metrics.audit_score >= 80 else "requires_attention"
                }
            
            # If not cached, conduct fresh assessment
            return await self.conduct_compliance_assessment(user_id)
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

    async def cleanup_expired_data(self, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Clean up expired data according to retention policies"""
        try:
            cleanup_results = await self.data_processor.cleanup_expired_data()
            
            # Schedule audit of cleanup
            background_tasks.add_task(
                self.audit_logger.log_data_cleanup,
                cleanup_results
            )
            
            logger.info(f"Data cleanup completed: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Error in data cleanup: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Data cleanup failed: {str(e)}")
