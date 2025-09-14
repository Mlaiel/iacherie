"""Event Security Orchestrator for Events Security

Central coordination of all security modules for comprehensive event protection.
Orchestrates threat detection, access control, compliance, and audit processes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityDecision(Enum):
    """Security decision outcomes"""
    ALLOW = "allow"
    DENY = "deny"
    QUARANTINE = "quarantine"
    MONITOR = "monitor"
    REQUIRE_APPROVAL = "require_approval"


class SecurityLevel(Enum):
    """Security processing levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


@dataclass
class SecurityContext:
    """Security context for event processing"""
    user_id: str
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    authentication_level: str
    permissions: List[str]
    risk_factors: Dict[str, Any]
    business_context: Dict[str, Any]
    
    def __post_init__(self) -> None:
        if self.permissions is None:
            self.permissions = []
        if self.risk_factors is None:
            self.risk_factors = {}
        if self.business_context is None:
            self.business_context = {}


@dataclass
class SecurityAssessment:
    """Comprehensive security assessment result"""
    event_id: str
    decision: SecurityDecision
    confidence: float
    threat_analysis: Any  # ThreatAnalysisResult
    access_control: Any  # AuthorizationResult
    compliance_validation: Any  # ComplianceValidationResult
    audit_record: Any  # AuditRecord
    security_score: float
    recommendations: List[str]
    processing_time_ms: float
    warnings: List[str]
    
    def __post_init__(self) -> None:
        if self.recommendations is None:
            self.recommendations = []
        if self.warnings is None:
            self.warnings = []


class EventSecurityOrchestrator:
    """
    Central orchestrator for all event security processes.
    Coordinates threat detection, access control, compliance, and audit.
    """
    
    def __init__(self) -> None:
        self.enabled = True
        self.security_level = SecurityLevel.STANDARD
        self.security_modules = {}
        self.security_policies = self._initialize_security_policies()
        self.event_callbacks = {}  # event_type -> List[Callable]
        self.processing_stats = {
            'total_events': 0,
            'allowed': 0,
            'denied': 0,
            'quarantined': 0,
            'processing_times': []
        }
        logger.info("EventSecurityOrchestrator initialized")
    
    def register_security_modules(self,
                                threat_engine=None,
                                access_manager=None,
                                compliance_validator=None,
                                audit_collector=None) -> None:
        """Register security modules with the orchestrator"""
        
        if threat_engine:
            self.security_modules['threat_engine'] = threat_engine
            logger.info("Threat detection engine registered")
        
        if access_manager:
            self.security_modules['access_manager'] = access_manager
            logger.info("Access control manager registered")
        
        if compliance_validator:
            self.security_modules['compliance_validator'] = compliance_validator
            logger.info("Compliance validator registered")
        
        if audit_collector:
            self.security_modules['audit_collector'] = audit_collector
            logger.info("Audit trail collector registered")
    
    async def process_event_security(self,
                                   event: Any,
                                   security_context: SecurityContext) -> SecurityAssessment:
        """
        Process comprehensive security assessment for an event.
        
        Args:
            event: Domain event to process
            security_context: Security context for processing
            
        Returns:
            SecurityAssessment with complete security decision
        """
        start_time = datetime.utcnow()
        
        if not self.enabled:
            return self._create_permissive_assessment(event, security_context)
        
        try:
            event_id = getattr(event, 'event_id', 'unknown')
            event_type = getattr(event, 'event_type', 'unknown')
            
            logger.debug(f"Processing security for event {event_id} ({event_type})")
            
            # Step 1: Threat Detection
            threat_analysis = await self._perform_threat_analysis(event, security_context)
            
            # Step 2: Access Control (if threat level acceptable)
            access_control = await self._perform_access_control(
                event, security_context, threat_analysis
            )
            
            # Step 3: Compliance Validation
            compliance_validation = await self._perform_compliance_validation(
                event, security_context
            )
            
            # Step 4: Make Security Decision
            decision, confidence = await self._make_security_decision(
                threat_analysis, access_control, compliance_validation, security_context
            )
            
            # Step 5: Audit Trail (always execute)
            audit_record = await self._perform_audit_trail(
                event, security_context, decision, threat_analysis
            )
            
            # Step 6: Calculate Security Score
            security_score = self._calculate_security_score(
                threat_analysis, access_control, compliance_validation
            )
            
            # Step 7: Generate Recommendations
            recommendations = await self._generate_security_recommendations(
                decision, threat_analysis, access_control, compliance_validation
            )
            
            # Step 8: Collect Warnings
            warnings = self._collect_security_warnings(
                threat_analysis, access_control, compliance_validation
            )
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create assessment
            assessment = SecurityAssessment(
                event_id=event_id,
                decision=decision,
                confidence=confidence,
                threat_analysis=threat_analysis,
                access_control=access_control,
                compliance_validation=compliance_validation,
                audit_record=audit_record,
                security_score=security_score,
                recommendations=recommendations,
                processing_time_ms=processing_time,
                warnings=warnings
            )
            
            # Update statistics
            self._update_processing_stats(assessment)
            
            # Execute callbacks
            await self._execute_security_callbacks(event_type, assessment)
            
            logger.debug(f"Security processing complete for {event_id}: {decision.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error in security orchestration: {str(e)}")
            return self._create_error_assessment(event, security_context, str(e))
    
    async def _perform_threat_analysis(self,
                                     event: Any,
                                     security_context: SecurityContext) -> Any:
        """Perform threat analysis if threat engine is available"""
        
        threat_engine = self.security_modules.get('threat_engine')
        if not threat_engine:
            logger.warning("Threat engine not available - skipping threat analysis")
            return None
        
        try:
            return await threat_engine.analyze_event_security(event)
        except Exception as e:
            logger.error(f"Threat analysis failed: {str(e)}")
            return None
    
    async def _perform_access_control(self,
                                    event: Any,
                                    security_context: SecurityContext,
                                    threat_analysis: Any) -> Any:
        """Perform access control if access manager is available"""
        
        access_manager = self.security_modules.get('access_manager')
        if not access_manager:
            logger.warning("Access manager not available - skipping access control")
            return None
        
        # Skip access control if threat level is too high
        if threat_analysis and hasattr(threat_analysis, 'threat_level'):
            if threat_analysis.threat_level.value == 'critical':
                logger.info("Skipping access control due to critical threat level")
                return None
        
        try:
            return await access_manager.authorize_event_access(
                event, 
                security_context.user_id, 
                security_context.business_context
            )
        except Exception as e:
            logger.error(f"Access control failed: {str(e)}")
            return None
    
    async def _perform_compliance_validation(self,
                                           event: Any,
                                           security_context: SecurityContext) -> Any:
        """Perform compliance validation if validator is available"""
        
        compliance_validator = self.security_modules.get('compliance_validator')
        if not compliance_validator:
            logger.warning("Compliance validator not available - skipping compliance validation")
            return None
        
        try:
            return await compliance_validator.validate_event_compliance(
                event,
                security_context.user_id,
                security_context.business_context
            )
        except Exception as e:
            logger.error(f"Compliance validation failed: {str(e)}")
            return None
    
    async def _perform_audit_trail(self,
                                 event: Any,
                                 security_context: SecurityContext,
                                 decision: SecurityDecision,
                                 threat_analysis: Any) -> Any:
        """Perform audit trail collection if collector is available"""
        
        audit_collector = self.security_modules.get('audit_collector')
        if not audit_collector:
            logger.warning("Audit collector not available - skipping audit trail")
            return None
        
        try:
            # Build security context for audit
            audit_security_context = {
                'authentication_level': security_context.authentication_level,
                'risk_factors': security_context.risk_factors,
                'decision': decision.value,
                'threat_level': threat_analysis.threat_level.value if threat_analysis else 'unknown',
                'risk_score': threat_analysis.risk_score if threat_analysis else 0.0
            }
            
            # Build request metadata
            request_metadata = {
                'ip_address': security_context.ip_address,
                'user_agent': security_context.user_agent,
                'session_id': security_context.session_id
            }
            
            return await audit_collector.collect_event_audit(
                event,
                security_context.user_id,
                f"security.orchestration.{decision.value}",
                "success" if decision == SecurityDecision.ALLOW else "blocked",
                audit_security_context,
                security_context.business_context,
                request_metadata
            )
        except Exception as e:
            logger.error(f"Audit trail collection failed: {str(e)}")
            return None
    
    async def _make_security_decision(self,
                                    threat_analysis: Any,
                                    access_control: Any,
                                    compliance_validation: Any,
                                    security_context: SecurityContext) -> Tuple[SecurityDecision, float]:
        """Make comprehensive security decision based on all assessments"""
        
        decision_factors = []
        confidence_scores = []
        
        # Threat analysis factors
        if threat_analysis:
            threat_level = threat_analysis.threat_level.value
            risk_score = threat_analysis.risk_score
            
            if threat_level == 'critical':
                decision_factors.append(('DENY', 0.95))
            elif threat_level == 'high':
                decision_factors.append(('QUARANTINE', 0.85))
            elif threat_level == 'medium':
                decision_factors.append(('MONITOR', 0.60))
            else:
                decision_factors.append(('ALLOW', 0.80))
            
            confidence_scores.append(risk_score)
        
        # Access control factors
        if access_control:
            if access_control.granted:
                decision_factors.append(('ALLOW', 0.90))
            else:
                decision_factors.append(('DENY', 0.85))
            
            # Factor in temporary grants
            if access_control.temporary_grants:
                decision_factors.append(('REQUIRE_APPROVAL', 0.70))
            
            confidence_scores.append(0.85)  # Access control is generally reliable
        
        # Compliance factors
        if compliance_validation:
            if not compliance_validation.compliant:
                violation_count = len(compliance_validation.violations)
                if violation_count > 0:
                    # Critical compliance violations
                    critical_violations = [
                        v for v in compliance_validation.violations 
                        if hasattr(v, 'severity') and v.severity.value == 'critical'
                    ]
                    
                    if critical_violations:
                        decision_factors.append(('DENY', 0.95))
                    else:
                        decision_factors.append(('MONITOR', 0.70))
                
                confidence_scores.append(0.90)  # Compliance checks are reliable
            else:
                decision_factors.append(('ALLOW', 0.85))
                confidence_scores.append(0.80)
        
        # Security level factors
        if self.security_level == SecurityLevel.MAXIMUM:
            # In maximum security, be more restrictive
            if any(factor[0] in ['DENY', 'QUARANTINE'] for factor in decision_factors):
                decision_factors.append(('DENY', 0.90))
        
        # User risk factors
        user_risk_score = self._calculate_user_risk_score(security_context)
        if user_risk_score > 0.7:
            decision_factors.append(('MONITOR', 0.75))
        elif user_risk_score > 0.9:
            decision_factors.append(('QUARANTINE', 0.85))
        
        # Make final decision
        if not decision_factors:
            return SecurityDecision.ALLOW, 0.5  # Default to allow with low confidence
        
        # Priority order: DENY > QUARANTINE > REQUIRE_APPROVAL > MONITOR > ALLOW
        decision_priority = {
            'DENY': 5,
            'QUARANTINE': 4,
            'REQUIRE_APPROVAL': 3,
            'MONITOR': 2,
            'ALLOW': 1
        }
        
        # Find highest priority decision
        highest_priority = 0
        final_decision = 'ALLOW'
        final_confidence = 0.0
        
        for decision, confidence in decision_factors:
            priority = decision_priority.get(decision, 0)
            if priority > highest_priority:
                highest_priority = priority
                final_decision = decision
                final_confidence = confidence
        
        # Calculate overall confidence
        overall_confidence = final_confidence
        if confidence_scores:
            overall_confidence = (final_confidence + sum(confidence_scores) / len(confidence_scores)) / 2
        
        return SecurityDecision(final_decision.lower()), min(overall_confidence, 1.0)
    
    def _calculate_user_risk_score(self, security_context: SecurityContext) -> float:
        """Calculate user risk score based on security context"""
        
        risk_score = 0.0
        risk_factors = security_context.risk_factors
        
        # Authentication level risk
        auth_level = security_context.authentication_level
        if auth_level == 'none':
            risk_score += 0.5
        elif auth_level == 'basic':
            risk_score += 0.2
        elif auth_level == 'mfa':
            risk_score += 0.0
        
        # IP address risk
        if risk_factors.get('suspicious_ip', False):
            risk_score += 0.3
        
        # Geolocation risk
        if risk_factors.get('unusual_location', False):
            risk_score += 0.2
        
        # Time-based risk
        if risk_factors.get('unusual_time', False):
            risk_score += 0.1
        
        # Device risk
        if risk_factors.get('new_device', False):
            risk_score += 0.1
        
        # Account age risk
        account_age_days = security_context.business_context.get('account_age_days', 365)
        if account_age_days < 7:
            risk_score += 0.2
        elif account_age_days < 30:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _calculate_security_score(self,
                                threat_analysis: Any,
                                access_control: Any,
                                compliance_validation: Any) -> float:
        """Calculate overall security score (0-1, higher is better)"""
        
        scores = []
        
        # Threat analysis score (inverse of risk score)
        if threat_analysis:
            threat_score = 1.0 - threat_analysis.risk_score
            scores.append(threat_score)
        
        # Access control score
        if access_control:
            access_score = 1.0 if access_control.granted else 0.0
            # Reduce score for temporary grants
            if access_control.temporary_grants:
                access_score *= 0.8
            scores.append(access_score)
        
        # Compliance score
        if compliance_validation:
            compliance_score = 1.0 if compliance_validation.compliant else 0.0
            # Reduce score based on violation severity
            if not compliance_validation.compliant:
                violations = compliance_validation.violations
                if violations:
                    avg_severity_impact = sum(
                        0.25 if hasattr(v, 'severity') and v.severity.value == 'low' else
                        0.5 if hasattr(v, 'severity') and v.severity.value == 'medium' else
                        0.75 if hasattr(v, 'severity') and v.severity.value == 'high' else
                        1.0  # critical
                        for v in violations
                    ) / len(violations)
                    compliance_score = max(0.0, 1.0 - avg_severity_impact)
            scores.append(compliance_score)
        
        # Calculate weighted average
        if not scores:
            return 0.5  # Neutral score when no assessments available
        
        return sum(scores) / len(scores)
    
    async def _generate_security_recommendations(self,
                                               decision: SecurityDecision,
                                               threat_analysis: Any,
                                               access_control: Any,
                                               compliance_validation: Any) -> List[str]:
        """Generate security recommendations based on assessments"""
        
        recommendations = []
        
        # Decision-based recommendations
        if decision == SecurityDecision.DENY:
            recommendations.append("Event blocked due to security concerns - manual review required")
        elif decision == SecurityDecision.QUARANTINE:
            recommendations.append("Event quarantined for security review - investigate before releasing")
        elif decision == SecurityDecision.REQUIRE_APPROVAL:
            recommendations.append("Event requires manual approval before processing")
        elif decision == SecurityDecision.MONITOR:
            recommendations.append("Event allowed with enhanced monitoring - watch for suspicious activity")
        
        # Threat analysis recommendations
        if threat_analysis and hasattr(threat_analysis, 'recommended_actions'):
            recommendations.extend(threat_analysis.recommended_actions)
        
        # Access control recommendations
        if access_control and not access_control.granted:
            denied_perms = getattr(access_control, 'denied_permissions', [])
            if denied_perms:
                perm_names = [p.name if hasattr(p, 'name') else str(p) for p in denied_perms]
                recommendations.append(f"Missing permissions: {', '.join(perm_names)}")
        
        # Compliance recommendations
        if compliance_validation and not compliance_validation.compliant:
            violations = compliance_validation.violations
            if violations:
                for violation in violations:
                    if hasattr(violation, 'severity') and violation.severity.value == 'critical':
                        recommendations.append(f"Critical compliance violation: {violation.description}")
        
        return recommendations
    
    def _collect_security_warnings(self,
                                 threat_analysis: Any,
                                 access_control: Any,
                                 compliance_validation: Any) -> List[str]:
        """Collect warnings from all security assessments"""
        
        warnings = []
        
        # Threat analysis warnings
        if threat_analysis and hasattr(threat_analysis, 'indicators'):
            low_confidence_indicators = [
                i for i in threat_analysis.indicators 
                if hasattr(i, 'confidence_score') and i.confidence_score < 0.5
            ]
            if low_confidence_indicators:
                warnings.append(f"{len(low_confidence_indicators)} threat indicators with low confidence")
        
        # Access control warnings
        if access_control and hasattr(access_control, 'temporary_grants'):
            temp_grants = access_control.temporary_grants
            if temp_grants:
                warnings.append(f"{len(temp_grants)} temporary permission grants issued")
        
        # Compliance warnings
        if compliance_validation and hasattr(compliance_validation, 'warnings'):
            warnings.extend(compliance_validation.warnings)
        
        return warnings
    
    def _update_processing_stats(self, assessment -> None: SecurityAssessment) -> None:
        """Update processing statistics"""
        
        self.processing_stats['total_events'] += 1
        
        if assessment.decision == SecurityDecision.ALLOW:
            self.processing_stats['allowed'] += 1
        elif assessment.decision == SecurityDecision.DENY:
            self.processing_stats['denied'] += 1
        elif assessment.decision == SecurityDecision.QUARANTINE:
            self.processing_stats['quarantined'] += 1
        
        # Track processing times (keep last 1000)
        processing_times = self.processing_stats['processing_times']
        processing_times.append(assessment.processing_time_ms)
        if len(processing_times) > 1000:
            self.processing_stats['processing_times'] = processing_times[-1000:]
    
    async def _execute_security_callbacks(self, event_type -> None: str, assessment -> None: SecurityAssessment) -> None:
        """Execute registered callbacks for event type"""
        
        callbacks = self.event_callbacks.get(event_type, [])
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(assessment)
                else:
                    callback(assessment)
            except Exception as e:
                logger.error(f"Error executing security callback: {str(e)}")
    
    def register_security_callback(self, event_type -> None: str, callback -> None: Callable) -> None:
        """Register a callback for security events"""
        
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
        logger.info(f"Security callback registered for event type: {event_type}")
    
    def _initialize_security_policies(self) -> Dict[str, Any]:
        """Initialize security policies"""
        
        return {
            'threat_thresholds': {
                'critical': 0.9,
                'high': 0.7,
                'medium': 0.5,
                'low': 0.3
            },
            'access_control': {
                'require_mfa_for_high_risk': True,
                'temporary_grant_duration_hours': 1,
                'max_failed_attempts': 5
            },
            'compliance': {
                'auto_correction_enabled': True,
                'critical_violation_block': True,
                'gdpr_consent_required': True
            },
            'audit': {
                'audit_level': 'standard',
                'retention_days': 2555,  # 7 years
                'real_time_monitoring': True
            }
        }
    
    def _create_permissive_assessment(self,
                                    event: Any,
                                    security_context: SecurityContext) -> SecurityAssessment:
        """Create permissive assessment when orchestrator is disabled"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        
        return SecurityAssessment(
            event_id=event_id,
            decision=SecurityDecision.ALLOW,
            confidence=0.5,
            threat_analysis=None,
            access_control=None,
            compliance_validation=None,
            audit_record=None,
            security_score=0.5,
            recommendations=["Security orchestration disabled"],
            processing_time_ms=0.0,
            warnings=["Security orchestration disabled - no security checks performed"]
        )
    
    def _create_error_assessment(self,
                               event: Any,
                               security_context: SecurityContext,
                               error_message: str) -> SecurityAssessment:
        """Create error assessment when orchestration fails"""
        
        event_id = getattr(event, 'event_id', 'unknown')
        
        return SecurityAssessment(
            event_id=event_id,
            decision=SecurityDecision.DENY,  # Conservative approach on error
            confidence=0.0,
            threat_analysis=None,
            access_control=None,
            compliance_validation=None,
            audit_record=None,
            security_score=0.0,
            recommendations=["Manual security review required due to orchestration error"],
            processing_time_ms=0.0,
            warnings=[f"Security orchestration error: {error_message}"]
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        
        stats = self.processing_stats.copy()
        
        # Calculate averages
        processing_times = stats['processing_times']
        if processing_times:
            stats['avg_processing_time_ms'] = sum(processing_times) / len(processing_times)
            stats['max_processing_time_ms'] = max(processing_times)
            stats['min_processing_time_ms'] = min(processing_times)
        else:
            stats['avg_processing_time_ms'] = 0.0
            stats['max_processing_time_ms'] = 0.0
            stats['min_processing_time_ms'] = 0.0
        
        # Calculate percentages
        total = stats['total_events']
        if total > 0:
            stats['allow_percentage'] = (stats['allowed'] / total) * 100
            stats['deny_percentage'] = (stats['denied'] / total) * 100
            stats['quarantine_percentage'] = (stats['quarantined'] / total) * 100
        else:
            stats['allow_percentage'] = 0.0
            stats['deny_percentage'] = 0.0
            stats['quarantine_percentage'] = 0.0
        
        return stats
    
    def set_security_level(self, level -> None: SecurityLevel) -> None:
        """Set security processing level"""
        self.security_level = level
        logger.info(f"Security level set to: {level.value}")
    
    def enable_orchestration(self) -> None:
        """Enable security orchestration"""
        self.enabled = True
        logger.info("Security orchestration enabled")
    
    def disable_orchestration(self) -> None:
        """Disable security orchestration"""
        self.enabled = False
        logger.info("Security orchestration disabled")


# Export for module use
__all__ = ['EventSecurityOrchestrator', 'SecurityContext', 'SecurityAssessment', 'SecurityDecision', 'SecurityLevel']