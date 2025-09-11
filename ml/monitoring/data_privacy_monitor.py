"""Data Privacy Monitor - GDPR Compliance & Creator Rights Protection

Enterprise-grade data privacy monitoring system with real-time compliance validation,
data anonymization tracking, and creator rights protection across ML operations.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

🛡️ SECURITY EXPERT IMPLEMENTATION:
- GDPR compliance monitoring with automated reporting
- Creator data rights protection and consent tracking
- Real-time privacy violation detection and alerting
- Data anonymization and pseudonymization validation
- Cross-border data transfer compliance (GDPR, CCPA, LGPD)
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
import numpy as np

class PrivacyRegulation(Enum):
    """Privacy regulation types."""
    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CCPA = "ccpa"  # California Consumer Privacy Act (US)
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act (Canada)

class DataCategory(Enum):
    """Data category classification for privacy monitoring."""
    PII = "pii"  # Personally Identifiable Information
    BIOMETRIC = "biometric"  # Biometric data (voice, face, etc.)
    BEHAVIORAL = "behavioral"  # User behavior patterns
    CONTENT = "content"  # Creator content data
    FINANCIAL = "financial"  # Payment and revenue data
    LOCATION = "location"  # Geographic location data

class PrivacyViolationType(Enum):
    """Types of privacy violations."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_LEAK = "data_leak"
    CONSENT_VIOLATION = "consent_violation"
    RETENTION_VIOLATION = "retention_violation"
    ANONYMIZATION_FAILURE = "anonymization_failure"
    CROSS_BORDER_VIOLATION = "cross_border_violation"

@dataclass
class PrivacyEvent:
    """Privacy-related event for monitoring and auditing."""
    event_id: str
    timestamp: datetime
    user_id: str
    data_category: DataCategory
    operation: str
    regulation: PrivacyRegulation
    consent_status: bool
    anonymized: bool
    location: str
    risk_score: float
    metadata: Dict[str, Any]

@dataclass
class PrivacyViolation:
    """Privacy violation incident."""
    violation_id: str
    timestamp: datetime
    violation_type: PrivacyViolationType
    severity: str  # "low", "medium", "high", "critical"
    affected_users: List[str]
    data_categories: List[DataCategory]
    description: str
    remediation_required: bool
    compliance_impact: List[PrivacyRegulation]

class DataPrivacyMonitor:
    """Enterprise data privacy monitoring system for ML operations.
    
    Features:
    - Real-time privacy compliance monitoring
    - GDPR/CCPA/LGPD compliance tracking
    - Creator consent management
    - Data anonymization validation
    - Cross-border transfer monitoring
    - Automated privacy reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize data privacy monitor.
        
        Args:
            config: Configuration including compliance settings, alert thresholds
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Privacy monitoring configuration
        self.compliance_regulations = self.config.get('regulations', [
            PrivacyRegulation.GDPR, PrivacyRegulation.CCPA
        ])
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.real_time_alerts = self.config.get('real_time_alerts', True)
        self.retention_limits = self.config.get('retention_limits', {
            DataCategory.PII: 365,  # days
            DataCategory.BIOMETRIC: 180,
            DataCategory.BEHAVIORAL: 730,
            DataCategory.CONTENT: 2555,  # 7 years for content
            DataCategory.FINANCIAL: 2555,  # 7 years for financial
            DataCategory.LOCATION: 90
        })
        
        # Monitoring state
        self.privacy_events: List[PrivacyEvent] = []
        self.violations: List[PrivacyViolation] = []
        self.consent_registry: Dict[str, Dict] = {}
        self.anonymization_registry: Dict[str, Dict] = {}
        
        # Initialize monitoring components
        self._initialize_privacy_monitor()
    
    def _initialize_privacy_monitor(self):
        """Initialize privacy monitoring components."""
        self.logger.info("🛡️ Initializing Data Privacy Monitor...")
        
        # Initialize compliance trackers
        self.compliance_trackers = {
            reg: self._create_compliance_tracker(reg) 
            for reg in self.compliance_regulations
        }
        
        # Initialize anonymization validator
        self.anonymization_validator = AnonymizationValidator()
        
        # Initialize consent manager
        self.consent_manager = ConsentManager()
        
        self.logger.info("✅ Data Privacy Monitor initialized successfully")
    
    def _create_compliance_tracker(self, regulation: PrivacyRegulation) -> Dict:
        """Create compliance tracker for specific regulation."""
        base_config = {
            'regulation': regulation,
            'data_retention_days': 365,
            'consent_required': True,
            'cross_border_restrictions': True
        }
        
        if regulation == PrivacyRegulation.GDPR:
            base_config.update({
                'right_to_be_forgotten': True,
                'data_portability': True,
                'consent_withdrawal': True,
                'data_minimization': True,
                'purpose_limitation': True
            })
        elif regulation == PrivacyRegulation.CCPA:
            base_config.update({
                'right_to_delete': True,
                'right_to_know': True,
                'opt_out_sale': True,
                'non_discrimination': True
            })
        
        return base_config
    
    async def monitor_data_access(
        self,
        user_id: str,
        data_categories: List[DataCategory],
        operation: str,
        context: Dict[str, Any]
    ) -> PrivacyEvent:
        """Monitor data access for privacy compliance.
        
        Args:
            user_id: User/creator identifier
            data_categories: Categories of data being accessed
            operation: Type of operation (read, write, delete, etc.)
            context: Additional context (location, purpose, etc.)
            
        Returns:
            PrivacyEvent: Logged privacy event
        """
        event_id = self._generate_event_id()
        timestamp = datetime.utcnow()
        
        # Check consent status
        consent_status = await self._check_consent_status(user_id, data_categories)
        
        # Validate anonymization
        anonymized = await self._validate_anonymization(user_id, data_categories)
        
        # Calculate privacy risk score
        risk_score = await self._calculate_privacy_risk(
            user_id, data_categories, operation, context
        )
        
        # Determine applicable regulation
        regulation = self._determine_applicable_regulation(context.get('location', 'EU'))
        
        # Create privacy event
        event = PrivacyEvent(
            event_id=event_id,
            timestamp=timestamp,
            user_id=user_id,
            data_category=data_categories[0] if data_categories else DataCategory.PII,
            operation=operation,
            regulation=regulation,
            consent_status=consent_status,
            anonymized=anonymized,
            location=context.get('location', 'unknown'),
            risk_score=risk_score,
            metadata=context
        )
        
        # Log event
        self.privacy_events.append(event)
        
        # Check for violations
        if risk_score > 0.7 or not consent_status:
            await self._detect_privacy_violations(event)
        
        # Real-time alerting
        if self.real_time_alerts and risk_score > 0.8:
            await self._send_privacy_alert(event)
        
        self.logger.info(f"📊 Privacy event logged: {event_id} (risk: {risk_score:.2f})")
        return event
    
    async def _check_consent_status(
        self,
        user_id: str,
        data_categories: List[DataCategory]
    ) -> bool:
        """Check user consent status for data categories."""
        consent_record = self.consent_registry.get(user_id)
        
        if not consent_record:
            # No consent record found
            return False
        
        # Check if consent covers all required categories
        for category in data_categories:
            if category.value not in consent_record.get('categories', []):
                return False
            
            # Check consent expiry
            consent_date = datetime.fromisoformat(consent_record.get('consent_date', '2020-01-01'))
            if (datetime.utcnow() - consent_date).days > 365:  # Consent expires after 1 year
                return False
        
        return True
    
    async def _validate_anonymization(
        self,
        user_id: str,
        data_categories: List[DataCategory]
    ) -> bool:
        """Validate data anonymization status."""
        # Check if sensitive categories require anonymization
        sensitive_categories = [DataCategory.PII, DataCategory.BIOMETRIC, DataCategory.FINANCIAL]
        
        for category in data_categories:
            if category in sensitive_categories:
                anonymization_record = self.anonymization_registry.get(
                    f"{user_id}_{category.value}"
                )
                if not anonymization_record:
                    return False
                    
                # Validate anonymization quality
                k_anonymity = anonymization_record.get('k_anonymity', 0)
                if k_anonymity < 5:  # Minimum k-anonymity threshold
                    return False
        
        return True
    
    async def _calculate_privacy_risk(
        self,
        user_id: str,
        data_categories: List[DataCategory],
        operation: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate privacy risk score (0-1 scale)."""
        risk_score = 0.0
        
        # Base risk by data category
        category_risks = {
            DataCategory.PII: 0.8,
            DataCategory.BIOMETRIC: 0.9,
            DataCategory.BEHAVIORAL: 0.5,
            DataCategory.CONTENT: 0.3,
            DataCategory.FINANCIAL: 0.9,
            DataCategory.LOCATION: 0.7
        }
        
        for category in data_categories:
            risk_score = max(risk_score, category_risks.get(category, 0.5))
        
        # Operation risk modifiers
        operation_modifiers = {
            'read': 1.0,
            'write': 1.2,
            'delete': 0.8,
            'export': 1.5,
            'share': 1.8,
            'anonymize': 0.5
        }
        
        risk_score *= operation_modifiers.get(operation, 1.0)
        
        # Context risk factors
        if context.get('cross_border', False):
            risk_score *= 1.3
        
        if context.get('third_party_access', False):
            risk_score *= 1.4
        
        if not context.get('encrypted', True):
            risk_score *= 1.5
        
        return min(risk_score, 1.0)
    
    def _determine_applicable_regulation(self, location: str) -> PrivacyRegulation:
        """Determine applicable privacy regulation based on location."""
        location_lower = location.lower()
        
        if any(eu_country in location_lower for eu_country in [
            'eu', 'germany', 'france', 'spain', 'italy', 'netherlands'
        ]):
            return PrivacyRegulation.GDPR
        elif 'california' in location_lower or 'ca' in location_lower:
            return PrivacyRegulation.CCPA
        elif 'brazil' in location_lower:
            return PrivacyRegulation.LGPD
        elif 'canada' in location_lower:
            return PrivacyRegulation.PIPEDA
        else:
            return PrivacyRegulation.GDPR  # Default to strictest regulation
    
    async def _detect_privacy_violations(self, event: PrivacyEvent):
        """Detect potential privacy violations."""
        violations = []
        
        # Check consent violations
        if not event.consent_status:
            violation = PrivacyViolation(
                violation_id=self._generate_violation_id(),
                timestamp=event.timestamp,
                violation_type=PrivacyViolationType.CONSENT_VIOLATION,
                severity="high",
                affected_users=[event.user_id],
                data_categories=[event.data_category],
                description=f"Data access without valid consent for {event.operation}",
                remediation_required=True,
                compliance_impact=[event.regulation]
            )
            violations.append(violation)
        
        # Check anonymization failures
        if not event.anonymized and event.data_category in [
            DataCategory.PII, DataCategory.BIOMETRIC
        ]:
            violation = PrivacyViolation(
                violation_id=self._generate_violation_id(),
                timestamp=event.timestamp,
                violation_type=PrivacyViolationType.ANONYMIZATION_FAILURE,
                severity="medium",
                affected_users=[event.user_id],
                data_categories=[event.data_category],
                description=f"Sensitive data not properly anonymized: {event.data_category.value}",
                remediation_required=True,
                compliance_impact=[event.regulation]
            )
            violations.append(violation)
        
        # Add violations to registry
        self.violations.extend(violations)
        
        for violation in violations:
            self.logger.warning(f"🚨 Privacy violation detected: {violation.violation_id}")
    
    async def _send_privacy_alert(self, event: PrivacyEvent):
        """Send real-time privacy alert."""
        alert_message = {
            "alert_type": "privacy_risk",
            "event_id": event.event_id,
            "risk_score": event.risk_score,
            "user_id": event.user_id,
            "operation": event.operation,
            "regulation": event.regulation.value,
            "timestamp": event.timestamp.isoformat(),
            "requires_immediate_attention": event.risk_score > 0.9
        }
        
        # In production, send to alerting system (PagerDuty, Slack, etc.)
        self.logger.warning(f"🚨 HIGH PRIVACY RISK ALERT: {json.dumps(alert_message, indent=2)}")
    
    async def register_consent(
        self,
        user_id: str,
        data_categories: List[DataCategory],
        consent_details: Dict[str, Any]
    ) -> bool:
        """Register user consent for data processing.
        
        Args:
            user_id: User/creator identifier
            data_categories: Data categories user consents to
            consent_details: Consent metadata (purpose, duration, etc.)
            
        Returns:
            bool: Success status
        """
        consent_record = {
            'user_id': user_id,
            'categories': [cat.value for cat in data_categories],
            'consent_date': datetime.utcnow().isoformat(),
            'purpose': consent_details.get('purpose', 'ml_processing'),
            'duration_days': consent_details.get('duration_days', 365),
            'withdrawal_method': consent_details.get('withdrawal_method', 'email'),
            'granular_consent': consent_details.get('granular_consent', {}),
            'consent_source': consent_details.get('source', 'web_ui')
        }
        
        self.consent_registry[user_id] = consent_record
        
        self.logger.info(f"✅ Consent registered for user {user_id}: {data_categories}")
        return True
    
    async def withdraw_consent(self, user_id: str, data_categories: List[DataCategory] = None) -> bool:
        """Process consent withdrawal (Right to be Forgotten).
        
        Args:
            user_id: User identifier
            data_categories: Specific categories to withdraw (None for all)
            
        Returns:
            bool: Success status
        """
        if user_id not in self.consent_registry:
            self.logger.warning(f"No consent record found for user {user_id}")
            return False
        
        if data_categories is None:
            # Withdraw all consent
            del self.consent_registry[user_id]
            self.logger.info(f"🗑️ All consent withdrawn for user {user_id}")
        else:
            # Withdraw specific categories
            current_categories = set(self.consent_registry[user_id]['categories'])
            withdrawn_categories = {cat.value for cat in data_categories}
            remaining_categories = current_categories - withdrawn_categories
            
            if remaining_categories:
                self.consent_registry[user_id]['categories'] = list(remaining_categories)
            else:
                del self.consent_registry[user_id]
            
            self.logger.info(f"🗑️ Consent withdrawn for categories {data_categories} for user {user_id}")
        
        # Trigger data deletion workflows
        await self._trigger_data_deletion(user_id, data_categories)
        
        return True
    
    async def _trigger_data_deletion(self, user_id: str, data_categories: List[DataCategory] = None):
        """Trigger data deletion workflows for consent withdrawal."""
        deletion_request = {
            'user_id': user_id,
            'categories': [cat.value for cat in data_categories] if data_categories else 'all',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending',
            'estimated_completion': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        # In production, trigger deletion workflows
        self.logger.info(f"🗑️ Data deletion triggered: {json.dumps(deletion_request, indent=2)}")
    
    async def generate_privacy_report(
        self,
        start_date: datetime,
        end_date: datetime,
        regulation: Optional[PrivacyRegulation] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive privacy compliance report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            regulation: Specific regulation to report on
            
        Returns:
            Dict: Privacy compliance report
        """
        # Filter events by date range
        filtered_events = [
            event for event in self.privacy_events
            if start_date <= event.timestamp <= end_date
        ]
        
        if regulation:
            filtered_events = [
                event for event in filtered_events
                if event.regulation == regulation
            ]
        
        # Generate report sections
        report = {
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'regulation': regulation.value if regulation else 'all',
                'total_events': len(filtered_events)
            },
            'consent_compliance': self._analyze_consent_compliance(filtered_events),
            'data_minimization': self._analyze_data_minimization(filtered_events),
            'violations_summary': self._summarize_violations(start_date, end_date),
            'risk_assessment': self._assess_privacy_risks(filtered_events),
            'recommendations': self._generate_privacy_recommendations(filtered_events)
        }
        
        self.logger.info(f"📊 Privacy report generated: {len(filtered_events)} events analyzed")
        return report
    
    def _analyze_consent_compliance(self, events: List[PrivacyEvent]) -> Dict[str, Any]:
        """Analyze consent compliance metrics."""
        total_events = len(events)
        consented_events = sum(1 for event in events if event.consent_status)
        
        return {
            'total_events': total_events,
            'consented_events': consented_events,
            'compliance_rate': consented_events / total_events if total_events > 0 else 0,
            'non_compliant_events': total_events - consented_events,
            'by_data_category': {
                category.value: {
                    'total': sum(1 for e in events if e.data_category == category),
                    'consented': sum(1 for e in events if e.data_category == category and e.consent_status)
                }
                for category in DataCategory
            }
        }
    
    def _analyze_data_minimization(self, events: List[PrivacyEvent]) -> Dict[str, Any]:
        """Analyze data minimization compliance."""
        category_counts = {}
        for event in events:
            category = event.data_category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate data minimization score (prefer minimal data access)
        minimization_score = 1.0 - (len(category_counts) / len(DataCategory))
        
        return {
            'minimization_score': minimization_score,
            'data_categories_accessed': len(category_counts),
            'access_distribution': category_counts,
            'recommendations': [
                "Reduce access to PII data where possible",
                "Implement purpose limitation controls",
                "Regular data access audits"
            ] if minimization_score < 0.7 else ["Data minimization practices are adequate"]
        }
    
    def _summarize_violations(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Summarize privacy violations in the period."""
        period_violations = [
            v for v in self.violations
            if start_date <= v.timestamp <= end_date
        ]
        
        violation_by_type = {}
        violation_by_severity = {}
        
        for violation in period_violations:
            vtype = violation.violation_type.value
            severity = violation.severity
            
            violation_by_type[vtype] = violation_by_type.get(vtype, 0) + 1
            violation_by_severity[severity] = violation_by_severity.get(severity, 0) + 1
        
        return {
            'total_violations': len(period_violations),
            'by_type': violation_by_type,
            'by_severity': violation_by_severity,
            'critical_violations': [
                {
                    'id': v.violation_id,
                    'type': v.violation_type.value,
                    'affected_users': len(v.affected_users),
                    'description': v.description
                }
                for v in period_violations if v.severity == 'critical'
            ]
        }
    
    def _assess_privacy_risks(self, events: List[PrivacyEvent]) -> Dict[str, Any]:
        """Assess overall privacy risk levels."""
        if not events:
            return {'overall_risk': 'low', 'risk_score': 0.0}
        
        risk_scores = [event.risk_score for event in events]
        avg_risk = np.mean(risk_scores)
        max_risk = np.max(risk_scores)
        
        risk_level = 'low'
        if avg_risk > 0.7:
            risk_level = 'high'
        elif avg_risk > 0.4:
            risk_level = 'medium'
        
        return {
            'overall_risk': risk_level,
            'average_risk_score': avg_risk,
            'maximum_risk_score': max_risk,
            'high_risk_events': sum(1 for score in risk_scores if score > 0.7),
            'risk_trend': 'improving' if avg_risk < 0.5 else 'concerning'
        }
    
    def _generate_privacy_recommendations(self, events: List[PrivacyEvent]) -> List[str]:
        """Generate privacy improvement recommendations."""
        recommendations = []
        
        # Analyze consent compliance
        consent_rate = sum(1 for e in events if e.consent_status) / len(events) if events else 1
        if consent_rate < 0.9:
            recommendations.append("Improve consent collection mechanisms")
            recommendations.append("Implement granular consent options")
        
        # Analyze anonymization usage
        anon_rate = sum(1 for e in events if e.anonymized) / len(events) if events else 1
        if anon_rate < 0.8:
            recommendations.append("Increase data anonymization coverage")
            recommendations.append("Implement differential privacy techniques")
        
        # Analyze high-risk operations
        high_risk_count = sum(1 for e in events if e.risk_score > 0.7)
        if high_risk_count > len(events) * 0.1:  # More than 10% high risk
            recommendations.append("Review high-risk data operations")
            recommendations.append("Implement additional privacy controls")
        
        if not recommendations:
            recommendations.append("Privacy practices are satisfactory")
            recommendations.append("Continue monitoring and regular audits")
        
        return recommendations
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return f"pe_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.utcnow()) % 10000:04d}"
    
    def _generate_violation_id(self) -> str:
        """Generate unique violation ID."""
        return f"pv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.utcnow()) % 10000:04d}"
    
    async def get_privacy_metrics(self) -> Dict[str, Any]:
        """Get current privacy monitoring metrics."""
        return {
            'total_events': len(self.privacy_events),
            'total_violations': len(self.violations),
            'consent_registry_size': len(self.consent_registry),
            'anonymization_registry_size': len(self.anonymization_registry),
            'monitoring_status': 'active' if self.monitoring_enabled else 'inactive',
            'compliance_regulations': [reg.value for reg in self.compliance_regulations],
            'last_event_time': self.privacy_events[-1].timestamp.isoformat() if self.privacy_events else None,
            'average_risk_score': np.mean([e.risk_score for e in self.privacy_events]) if self.privacy_events else 0.0
        }


class AnonymizationValidator:
    """Validator for data anonymization quality."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def validate_k_anonymity(self, dataset: pd.DataFrame, k: int = 5) -> bool:
        """Validate k-anonymity of dataset."""
        # Simplified k-anonymity check
        if dataset.empty:
            return True
        
        # Check for unique combinations
        quasi_identifiers = ['age', 'location', 'profession']  # Example QI columns
        available_qi = [col for col in quasi_identifiers if col in dataset.columns]
        
        if not available_qi:
            return True  # No quasi-identifiers to check
        
        group_sizes = dataset.groupby(available_qi).size()
        min_group_size = group_sizes.min()
        
        return min_group_size >= k
    
    async def validate_l_diversity(self, dataset: pd.DataFrame, l: int = 2) -> bool:
        """Validate l-diversity of dataset."""
        # Simplified l-diversity check
        sensitive_attrs = ['salary', 'medical_condition']  # Example sensitive attributes
        available_sa = [col for col in sensitive_attrs if col in dataset.columns]
        
        if not available_sa:
            return True
        
        # Check diversity in sensitive attributes
        for attr in available_sa:
            unique_values = dataset[attr].nunique()
            if unique_values < l:
                return False
        
        return True


class ConsentManager:
    """Manager for user consent tracking and validation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.consent_storage = {}
    
    async def validate_consent(
        self,
        user_id: str,
        purpose: str,
        data_categories: List[DataCategory]
    ) -> bool:
        """Validate user consent for specific purpose and data categories."""
        consent_record = self.consent_storage.get(user_id)
        
        if not consent_record:
            return False
        
        # Check purpose limitation
        if purpose not in consent_record.get('purposes', []):
            return False
        
        # Check data category consent
        consented_categories = set(consent_record.get('categories', []))
        required_categories = {cat.value for cat in data_categories}
        
        return required_categories.issubset(consented_categories)
    
    async def get_consent_expiry(self, user_id: str) -> Optional[datetime]:
        """Get consent expiry date for user."""
        consent_record = self.consent_storage.get(user_id)
        
        if not consent_record:
            return None
        
        consent_date = datetime.fromisoformat(consent_record['consent_date'])
        duration_days = consent_record.get('duration_days', 365)
        
        return consent_date + timedelta(days=duration_days)


# Example usage and testing
async def main():
    """Test data privacy monitor functionality."""
    # Initialize monitor
    config = {
        'regulations': [PrivacyRegulation.GDPR, PrivacyRegulation.CCPA],
        'monitoring_enabled': True,
        'real_time_alerts': True
    }
    
    monitor = DataPrivacyMonitor(config)
    
    # Register user consent
    await monitor.register_consent(
        user_id="creator_123",
        data_categories=[DataCategory.PII, DataCategory.CONTENT, DataCategory.BEHAVIORAL],
        consent_details={
            'purpose': 'content_analysis',
            'duration_days': 365,
            'source': 'web_consent_form'
        }
    )
    
    # Monitor data access
    privacy_event = await monitor.monitor_data_access(
        user_id="creator_123",
        data_categories=[DataCategory.PII],
        operation="read",
        context={
            'location': 'Germany',
            'purpose': 'content_analysis',
            'encrypted': True,
            'third_party_access': False
        }
    )
    
    print(f"Privacy event logged: {privacy_event.event_id}")
    
    # Generate privacy report
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    
    report = await monitor.generate_privacy_report(
        start_date=start_date,
        end_date=end_date,
        regulation=PrivacyRegulation.GDPR
    )
    
    print("Privacy Report Generated:")
    print(f"Events analyzed: {report['report_metadata']['total_events']}")
    print(f"Consent compliance: {report['consent_compliance']['compliance_rate']:.2%}")
    
    # Get current metrics
    metrics = await monitor.get_privacy_metrics()
    print(f"\nPrivacy Metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())