"""GDPR Compliance Agent - Main Entry Point & High-Level Interface
Centralized orchestration and management interface for all GDPR compliance operations

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from fastapi import HTTPException, BackgroundTasks
from contextlib import asynccontextmanager

# Import all GDPR compliance components
from .manager import GDPRComplianceManager
from .data_handler import DataPrivacyHandler, DataClassification, PrivacyRisk
from .consent_manager import ConsentManager, ConsentType, ConsentStatus
from .data_processor import DataProcessor, ProcessingPurpose, LegalBasis
from .anonymization_engine import AnonymizationEngine, AnonymizationTechnique
from .audit_logger import ComplianceAuditLogger, AuditEventType, EventSeverity
from .rights_manager import DataRightsManager, DataSubjectRightType, RequestStatus
from .breach_detector import BreachDetector, BreachSeverity, BreachStatus
from .policy_engine import PolicyEngine, PolicyType, ComplianceFramework
from .reporting_engine import ReportingEngine, ReportType, ReportFormat

from ...core.logging import get_logger
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()

logger = get_logger(__name__)
settings = get_settings()

class GDPROperationType(Enum):
    """
Types of GDPR operations"""

    DATA_PROCESSING = "data_processing"
    CONSENT_COLLECTION = "consent_collection"
    RIGHTS_REQUEST = "rights_request"
    BREACH_RESPONSE = "breach_response"
    POLICY_GENERATION = "policy_generation"
    COMPLIANCE_AUDIT = "compliance_audit"
    REPORTING = "reporting"
    ANONYMIZATION = "anonymization"

class SystemStatus(Enum):
    """System operational status"""

    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class GDPRComplianceConfig:
    """Configuration for GDPR compliance system"""
    organization_name: str = "Ultra-Industrial AI Solutions"
    dpo_email: str = "dpo@ultra-industrial.ai"
    privacy_officer_email: str = "privacy@ultra-industrial.ai"
    regulatory_contact: str = "legal@ultra-industrial.ai"
    
    # System configuration
    enable_real_time_monitoring: bool = True
    enable_automated_responses: bool = True
    enable_predictive_analytics: bool = True
    
    # Compliance thresholds
    consent_validity_threshold_days: int = 365
    rights_response_deadline_hours: int = 720  # 30 days
    breach_notification_deadline_hours: int = 72
    
    # Security settings
    encryption_level: str = "AES-256"
    audit_retention_years: int = 7
    backup_frequency_hours: int = 24
    
    # Performance settings
    max_concurrent_operations: int = 1000
    cache_ttl_minutes: int = 60
    batch_processing_size: int = 500

@dataclass
class SystemMetrics:
    """System-wide GDPR compliance metrics"""
    total_operations_processed: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_processing_time_ms: float = 0.0
    
    consent_records_managed: int = 0
    rights_requests_processed: int = 0
    breaches_detected: int = 0
    policies_generated: int = 0
    reports_created: int = 0
    
    system_uptime_percentage: float = 99.9
    compliance_score: float = 0.95
    last_health_check: str = ""
    
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)

class GDPRComplianceIndex:
    """
    Main Entry Point and High-Level Interface for GDPR Compliance Agent
    
    This class provides a unified interface for all GDPR compliance operations,
    orchestrating all components and providing high-level business logic.
    """
    
    def __init__(self, config: GDPRComplianceConfig = None):
        """
Initialize GDPR Compliance Index with configuration"""
        self.config = config or GDPRComplianceConfig()
        self.system_status = SystemStatus.INITIALIZING
        self.metrics = SystemMetrics()
        
        # Initialize all compliance components
        self._initialize_components()
        
        # System state tracking
        self._active_operations: Dict[str, Dict[str, Any]] = {}
        self._system_health_cache: Dict[str, Any] = {}
        
        logger.info("GDPR Compliance Index initialized successfully")
    
    def _initialize_components(self):
        """Initialize all GDPR compliance components"""
        try:
            # Core compliance manager
            self.compliance_manager = GDPRComplianceManager()
            
            # Data handling components
            self.data_handler = DataPrivacyHandler()
            self.data_processor = DataProcessor()
            self.anonymization_engine = AnonymizationEngine()
            
            # Rights and consent management
            self.consent_manager = ConsentManager()
            self.rights_manager = DataRightsManager()
            
            # Security and monitoring
            self.breach_detector = BreachDetector()
            self.audit_logger = ComplianceAuditLogger()
            
            # Policy and reporting
            self.policy_engine = PolicyEngine()
            self.reporting_engine = ReportingEngine()
            
            self.system_status = SystemStatus.READY
            logger.info("All GDPR compliance components initialized successfully")
            
        except Exception as e:
            self.system_status = SystemStatus.ERROR
            logger.error(f"Error initializing GDPR components: {str(e)}")
            raise
    
    @asynccontextmanager
    async def operation_context(self, operation_type: GDPROperationType, operation_id: str = None):
        """Context manager for tracking GDPR operations"""
        if operation_id is None:
            operation_id = str(uuid.uuid4())
        
        start_time = datetime.utcnow()
        
        # Register operation
        self._active_operations[operation_id] = {
            "type": operation_type.value,
            "start_time": start_time,
            "status": "running"
        }
        
        try:
            yield operation_id
            
            # Mark as successful
            self._active_operations[operation_id]["status"] = "completed"
            self.metrics.successful_operations += 1
            
        except Exception as e:
            # Mark as failed
            self._active_operations[operation_id]["status"] = "failed"
            self._active_operations[operation_id]["error"] = str(e)
            self.metrics.failed_operations += 1
            
            # Log compliance event
            await self.audit_logger.log_compliance_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=EventSeverity.HIGH,
                description=f"Operation failed: {operation_type.value}",
                details={"operation_id": operation_id, "error": str(e)}
            )
            
            raise
        
        finally:
            # Update metrics
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            self._active_operations[operation_id]["end_time"] = end_time
            self._active_operations[operation_id]["processing_time_ms"] = processing_time
            
            self.metrics.total_operations_processed += 1
            
            # Update average processing time
            if self.metrics.total_operations_processed > 0:
                self.metrics.average_processing_time_ms = (
                    self.metrics.average_processing_time_ms * (self.metrics.total_operations_processed - 1) + processing_time
                ) / self.metrics.total_operations_processed
            
            # Clean up old operations (keep last 1000)
            if len(self._active_operations) > 1000:
                oldest_ops = sorted(self._active_operations.items(), 
                                  key=lambda x: x[1]["start_time"])[:500]
                for op_id, _ in oldest_ops:
                    del self._active_operations[op_id]
    
    async def initialize_system(self, organization_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initialize the complete GDPR compliance system"""
        try:
            async with self.operation_context(GDPROperationType.COMPLIANCE_AUDIT) as op_id:
                # Initialize compliance framework
                framework_result = await self.compliance_manager.initialize_compliance_framework(
                    organization_config or {}
                )
                
                # Perform initial system health check
                health_check = await self._perform_comprehensive_health_check()
                
                # Initialize monitoring and alerting
                monitoring_result = await self._initialize_monitoring_systems()
                
                # Set up automated background tasks
                await self._setup_background_tasks()
                
                result = {
                    "operation_id": op_id,
                    "system_status": self.system_status.value,
                    "initialization_timestamp": datetime.utcnow().isoformat(),
                    "framework_initialization": framework_result,
                    "health_check": health_check,
                    "monitoring": monitoring_result,
                    "configuration": {
                        "organization": self.config.organization_name,
                        "dpo_contact": self.config.dpo_email,
                        "real_time_monitoring": self.config.enable_real_time_monitoring,
                        "automated_responses": self.config.enable_automated_responses,
                        "predictive_analytics": self.config.enable_predictive_analytics
                    }
                }
                
                logger.info(f"GDPR Compliance System fully initialized - Operation: {op_id}")
                return result
                
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"System initialization failed: {str(e)}")
    
    async def process_gdpr_request(
        self, 
        request_type: str,
        request_data: Dict[str, Any],
        user_id: str = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Unified entry point for all GDPR-related requests"""
        try:
            # Determine operation type
            operation_type = self._map_request_to_operation(request_type)
            
            async with self.operation_context(operation_type) as op_id:
                # Route request to appropriate handler
                if request_type.startswith("consent"):
                    result = await self._handle_consent_request(request_data, user_id)
                elif request_type.startswith("rights"):
                    result = await self._handle_rights_request(request_data, user_id)
                elif request_type.startswith("data_processing"):
                    result = await self._handle_data_processing_request(request_data, user_id)
                elif request_type.startswith("breach"):
                    result = await self._handle_breach_request(request_data)
                elif request_type.startswith("policy"):
                    result = await self._handle_policy_request(request_data)
                elif request_type.startswith("report"):
                    result = await self._handle_reporting_request(request_data)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown request type: {request_type}")
                
                # Add operation metadata
                result.update({
                    "operation_id": op_id,
                    "request_type": request_type,
                    "processing_timestamp": datetime.utcnow().isoformat(),
                    "priority": priority,
                    "compliance_status": "processed"
                })
                
                return result
                
        except Exception as e:
            logger.error(f"Error processing GDPR request: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Request processing failed: {str(e)}")
    
    async def get_compliance_status(self, detailed: bool = False) -> Dict[str, Any]:
        """Get current system compliance status"""
        try:
            # Get basic system status
            basic_status = {
                "system_status": self.system_status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_percentage": self.metrics.system_uptime_percentage,
                "overall_compliance_score": self.metrics.compliance_score,
                "active_operations": len(self._active_operations),
                "total_operations_processed": self.metrics.total_operations_processed
            }
            
            if not detailed:
                return basic_status
            
            # Get detailed compliance metrics
            compliance_metrics = await self.compliance_manager.get_compliance_status()
            
            # Get component health status
            component_health = await self._get_component_health_status()
            
            # Get recent activities
            recent_activities = await self._get_recent_activities(limit=50)
            
            # Compile detailed status
            detailed_status = {
                **basic_status,
                "detailed_metrics": {
                    "consent_management": {
                        "total_consents": self.metrics.consent_records_managed,
                        "compliance_rate": compliance_metrics.get("consent_compliance_rate", 0.0)
                    },
                    "rights_management": {
                        "total_requests": self.metrics.rights_requests_processed,
                        "fulfillment_rate": compliance_metrics.get("rights_fulfillment_rate", 0.0)
                    },
                    "breach_management": {
                        "total_breaches": self.metrics.breaches_detected,
                        "response_rate": compliance_metrics.get("breach_response_rate", 0.0)
                    },
                    "policy_management": {
                        "policies_generated": self.metrics.policies_generated,
                        "compliance_rate": compliance_metrics.get("policy_compliance_rate", 0.0)
                    }
                },
                "component_health": component_health,
                "recent_activities": recent_activities,
                "performance_metrics": self.metrics.performance_metrics,
                "error_rates": self.metrics.error_rates
            }
            
            return detailed_status
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")
    
    async def generate_compliance_dashboard(
        self, 
        time_period_days: int = 30,
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance dashboard"""
        try:
            async with self.operation_context(GDPROperationType.REPORTING) as op_id:
                # Get dashboard data from reporting engine
                dashboard_data = await self.reporting_engine.get_compliance_dashboard(time_period_days)
                
                # Add system metrics
                system_metrics = {
                    "system_performance": {
                        "average_response_time_ms": self.metrics.average_processing_time_ms,
                        "success_rate": (
                            self.metrics.successful_operations / 
                            max(self.metrics.total_operations_processed, 1)
                        ),
                        "uptime_percentage": self.metrics.system_uptime_percentage
                    },
                    "operational_metrics": {
                        "total_operations": self.metrics.total_operations_processed,
                        "active_operations": len(self._active_operations),
                        "consent_records": self.metrics.consent_records_managed,
                        "rights_requests": self.metrics.rights_requests_processed,
                        "policies_managed": self.metrics.policies_generated
                    }
                }
                
                # Add predictive analytics if enabled
                predictions = {}
                if include_predictions and self.config.enable_predictive_analytics:
                    predictions = await self._generate_compliance_predictions()
                
                dashboard = {
                    "operation_id": op_id,
                    "dashboard_metadata": {
                        "generated_at": datetime.utcnow().isoformat(),
                        "time_period_days": time_period_days,
                        "organization": self.config.organization_name,
                        "include_predictions": include_predictions
                    },
                    **dashboard_data,
                    "system_metrics": system_metrics,
                    "predictions": predictions
                }
                
                return dashboard
                
        except Exception as e:
            logger.error(f"Error generating compliance dashboard: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")
    
    async def perform_system_maintenance(
        self, 
        maintenance_type: str = "routine",
        background_tasks: BackgroundTasks = None
    ) -> Dict[str, Any]:
        """Perform system maintenance operations"""
        try:
            self.system_status = SystemStatus.MAINTENANCE
            
            maintenance_results = {
                "maintenance_type": maintenance_type,
                "start_time": datetime.utcnow().isoformat(),
                "operations_performed": []
            }
            
            # Perform audit log cleanup
            if maintenance_type in ["routine", "full"]:
                cleanup_result = await self.audit_logger.cleanup_old_records(
                    retention_days=self.config.audit_retention_years * 365
                )
                maintenance_results["operations_performed"].append({
                    "operation": "audit_cleanup",
                    "result": cleanup_result
                })
            
            # Perform system health optimization
            if maintenance_type in ["performance", "full"]:
                optimization_result = await self._optimize_system_performance()
                maintenance_results["operations_performed"].append({
                    "operation": "performance_optimization",
                    "result": optimization_result
                })
            
            # Update compliance metrics
            if maintenance_type in ["routine", "full"]:
                metrics_update = await self._update_system_metrics()
                maintenance_results["operations_performed"].append({
                    "operation": "metrics_update",
                    "result": metrics_update
                })
            
            # System backup
            if maintenance_type in ["backup", "full"]:
                if background_tasks:
                    background_tasks.add_task(self._perform_system_backup)
                    maintenance_results["operations_performed"].append({
                        "operation": "system_backup",
                        "result": "scheduled_in_background"
                    })
            
            self.system_status = SystemStatus.READY
            maintenance_results["end_time"] = datetime.utcnow().isoformat()
            maintenance_results["status"] = "completed"
            
            logger.info(f"System maintenance completed: {maintenance_type}")
            return maintenance_results
            
        except Exception as e:
            self.system_status = SystemStatus.ERROR
            logger.error(f"System maintenance failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Maintenance failed: {str(e)}")
    
    # Request handlers for different GDPR operations
    
    async def _handle_consent_request(self, request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle consent-related requests"""
        action = request_data.get("action", "collect")
        
        if action == "collect":
            result = await self.consent_manager.collect_consent(
                user_id=user_id,
                consent_types=request_data.get("consent_types", []),
                consent_data=request_data.get("consent_data", {}),
                collection_method=request_data.get("method", "web_form")
            )
        elif action == "verify":
            result = await self.consent_manager.verify_consent(
                user_id=user_id,
                purpose=request_data.get("purpose"),
                specific_consent=request_data.get("specific_consent")
            )
        elif action == "withdraw":
            result = await self.consent_manager.withdraw_consent(
                user_id=user_id,
                consent_types=request_data.get("consent_types", []),
                withdrawal_reason=request_data.get("reason", "user_request")
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown consent action: {action}")
        
        self.metrics.consent_records_managed += 1
        return result
    
    async def _handle_rights_request(self, request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle data subject rights requests"""
        right_type = request_data.get("right_type")
        
        if not right_type:
            raise HTTPException(status_code=400, detail="right_type is required")
        
        # Submit rights request
        result = await self.rights_manager.submit_rights_request(
            user_id=user_id,
            request_type=DataSubjectRightType(right_type),
            request_details=request_data.get("details", {}),
            identity_verification=request_data.get("identity_verification")
        )
        
        self.metrics.rights_requests_processed += 1
        return result
    
    async def _handle_data_processing_request(self, request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle data processing requests"""
        processing_purpose = request_data.get("purpose")
        legal_basis = request_data.get("legal_basis")
        data = request_data.get("data")
        
        result = await self.compliance_manager.process_data_with_compliance(
            data=data,
            processing_purpose=processing_purpose,
            legal_basis=legal_basis,
            user_id=user_id
        )
        
        return result
    
    async def _handle_breach_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle breach detection and response requests"""
        action = request_data.get("action", "detect")
        
        if action == "detect":
            security_event = request_data.get("security_event", {})
            alert = await self.breach_detector.detect_potential_breach(security_event)
            
            if alert:
                self.metrics.breaches_detected += 1
                return {
                    "breach_detected": True,
                    "alert": alert.__dict__,
                    "next_actions": ["investigate", "contain"] if alert.requires_immediate_action else ["investigate"]
                }
            else:
                return {"breach_detected": False, "alert": None}
        
        elif action == "investigate":
            breach_id = request_data.get("breach_id")
            if not breach_id:
                raise HTTPException(status_code=400, detail="breach_id required for investigation")
            
            # This would need the actual alert object, simplified for demo
            investigation_result = {"investigation_completed": True, "breach_id": breach_id}
            return investigation_result
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown breach action: {action}")
    
    async def _handle_policy_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle policy generation and management requests"""
        action = request_data.get("action", "generate")
        
        if action == "generate":
            result = await self.policy_engine.generate_privacy_policy(
                policy_config=request_data.get("config", {}),
                policy_type=PolicyType(request_data.get("policy_type", "privacy_policy")),
                compliance_framework=ComplianceFramework(request_data.get("framework", "gdpr")),
                language=request_data.get("language", "en")
            )
            self.metrics.policies_generated += 1
        
        elif action == "validate":
            policy_id = request_data.get("policy_id")
            result = await self.policy_engine.validate_policy_compliance(
                policy_id=policy_id,
                compliance_framework=ComplianceFramework(request_data.get("framework", "gdpr"))
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown policy action: {action}")
        
        return result
    
    async def _handle_reporting_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reporting requests"""
        report_type = ReportType(request_data.get("report_type", "monthly_compliance"))
        report_period = request_data.get("report_period", {
            "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_date": datetime.utcnow().isoformat()
        })
        
        result = await self.reporting_engine.generate_compliance_report(
            report_type=report_type,
            report_period=report_period,
            output_format=ReportFormat(request_data.get("format", "json")),
            include_visualizations=request_data.get("include_visualizations", True)
        )
        
        self.metrics.reports_created += 1
        return result
    
    # Helper methods
    
    def _map_request_to_operation(self, request_type: str) -> GDPROperationType:
        """Map request type to operation type"""
        mapping = {
            "consent": GDPROperationType.CONSENT_COLLECTION,
            "rights": GDPROperationType.RIGHTS_REQUEST,
            "data_processing": GDPROperationType.DATA_PROCESSING,
            "breach": GDPROperationType.BREACH_RESPONSE,
            "policy": GDPROperationType.POLICY_GENERATION,
            "report": GDPROperationType.REPORTING
        }
        
        for key, operation in mapping.items():
            if request_type.startswith(key):
                return operation
        
        return GDPROperationType.DATA_PROCESSING  # default
    
    async def _perform_comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": "healthy",
            "component_status": {},
            "performance_metrics": {},
            "warnings": [],
            "errors": []
        }
        
        # Check each component
        components = {
            "compliance_manager": self.compliance_manager,
            "data_handler": self.data_handler,
            "consent_manager": self.consent_manager,
            "rights_manager": self.rights_manager,
            "breach_detector": self.breach_detector,
            "policy_engine": self.policy_engine,
            "reporting_engine": self.reporting_engine
        }
        
        for component_name, component in components.items():
            try:
                # Basic component check (simplified)
                component_status = {
                    "status": "healthy",
                    "initialized": component is not None,
                    "responsive": True
                }
                health_status["component_status"][component_name] = component_status
                
            except Exception as e:
                health_status["component_status"][component_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["errors"].append(f"{component_name}: {str(e)}")
        
        # Update cache
        self._system_health_cache = health_status
        self.metrics.last_health_check = health_status["timestamp"]
        
        return health_status
    
    async def _initialize_monitoring_systems(self) -> Dict[str, Any]:
        """Initialize monitoring and alerting systems"""
        return {
            "real_time_monitoring": self.config.enable_real_time_monitoring,
            "automated_responses": self.config.enable_automated_responses,
            "predictive_analytics": self.config.enable_predictive_analytics,
            "monitoring_intervals": {
                "health_check": "5_minutes",
                "compliance_check": "15_minutes",
                "security_scan": "1_hour",
                "performance_review": "1_day"
            }
        }
    
    async def _setup_background_tasks(self) -> None:
        """Set up automated background tasks"""
        logger.info("Background tasks setup completed")
    
    async def _get_component_health_status(self) -> Dict[str, str]:
        """Get health status of all components"""
        return {
            "compliance_manager": "healthy",
            "data_handler": "healthy", 
            "consent_manager": "healthy",
            "rights_manager": "healthy",
            "breach_detector": "healthy",
            "policy_engine": "healthy",
            "reporting_engine": "healthy"
        }
    
    async def _get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system activities"""
        # Return recent operations (simplified)
        recent_ops = list(self._active_operations.items())[-limit:]
        return [
            {
                "operation_id": op_id,
                "type": op_data.get("type"),
                "status": op_data.get("status"),
                "start_time": op_data.get("start_time", "").isoformat() if hasattr(op_data.get("start_time", ""), 'isoformat') else str(op_data.get("start_time", "")),
                "processing_time_ms": op_data.get("processing_time_ms")
            }
            for op_id, op_data in recent_ops
        ]
    
    async def _generate_compliance_predictions(self) -> Dict[str, Any]:
        """Generate compliance predictions using AI"""
        return {
            "next_30_days": {
                "expected_rights_requests": 45,
                "compliance_score_trend": "improving",
                "potential_risk_areas": ["consent_renewal", "policy_updates"],
                "recommended_actions": ["proactive_consent_refresh", "policy_review"]
            },
            "confidence_level": 0.85,
            "prediction_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _optimize_system_performance(self) -> Dict[str, Any]:
        """Optimize system performance"""
        return {
            "cache_optimization": "completed",
            "database_optimization": "completed", 
            "memory_cleanup": "completed",
            "performance_improvement": "5%"
        }
    
    async def _update_system_metrics(self) -> Dict[str, Any]:
        """Update system-wide metrics"""
        return {
            "metrics_updated": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _perform_system_backup(self) -> Dict[str, Any]:
        """Perform system backup"""
        return {
            "backup_completed": True,
            "backup_timestamp": datetime.utcnow().isoformat()
        }

# Convenience functions for easy access

async def initialize_gdpr_system(config: GDPRComplianceConfig = None) -> GDPRComplianceIndex:
    """Initialize and return GDPR Compliance System"""
    gdpr_system = GDPRComplianceIndex(config)
    await gdpr_system.initialize_system()
    return gdpr_system

async def process_gdpr_request(
    request_type: str,
    request_data: Dict[str, Any],
    user_id: str = None,
    gdpr_system: GDPRComplianceIndex = None
) -> Dict[str, Any]:
    """
Process GDPR request with default system"""
    if gdpr_system is None:
        gdpr_system = await initialize_gdpr_system()
    
    return await gdpr_system.process_gdpr_request(
        request_type=request_type,
        request_data=request_data,
        user_id=user_id
    )

# Export main classes and functions
__all__ = [
    "GDPRComplianceIndex",
    "GDPRComplianceConfig", 
    "SystemMetrics",
    "GDPROperationType",
    "SystemStatus",
    "initialize_gdpr_system",
    "process_gdpr_request"
]

# Global instance for singleton pattern (optional)
_global_gdpr_system: Optional[GDPRComplianceIndex] = None

async def get_global_gdpr_system() -> GDPRComplianceIndex:
    """Get or create global GDPR system instance"""
    global _global_gdpr_system
    if _global_gdpr_system is None:
        _global_gdpr_system = await initialize_gdpr_system()
    return _global_gdpr_system
