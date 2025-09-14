"""
Compliance Core - Central Compliance Management System
© 2025 Fahed Mlaiel. All rights reserved.

Central coordination of all compliance frameworks for Ainflue creator platform.
Provides unified compliance management and orchestration.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .compliance_base import (
    ComplianceBaseManager, ComplianceFramework, ComplianceStatus, 
    ComplianceRequirement, ComplianceCheck, DataClassification
)
from .gdpr_compliance import GDPRComplianceManager
from .ccpa_compliance import CCPAComplianceManager  
from .dmca_compliance import DMCAComplianceManager
from .audit_manager import AuditManager
from .legal_framework import LegalFrameworkManager, Jurisdiction

logger = logging.getLogger(__name__)


class ComplianceCoreManager:
    """
    Central Compliance Management System
    
    Orchestrates all compliance frameworks and provides:
    - Unified compliance dashboard
    - Cross-framework compliance analysis
    - Automated compliance monitoring
    - Risk aggregation and management
    - Compliance reporting and analytics
    - Multi-framework audit coordination
    """
    
    def __init__(self) -> None:
        # Initialize all compliance managers
        self.gdpr_manager = GDPRComplianceManager()
        self.ccpa_manager = CCPAComplianceManager()
        self.dmca_manager = DMCAComplianceManager()
        self.audit_manager = AuditManager()
        self.legal_manager = LegalFrameworkManager()
        
        # Central compliance tracking
        self.compliance_reports = {}
        self.risk_assessments = {}
        self.compliance_scores = {}
        
        # Configuration
        self.compliance_config = {
            'automated_monitoring': True,
            'assessment_frequency_days': 30,
            'risk_threshold_high': 0.7,
            'risk_threshold_medium': 0.4,
            'compliance_threshold': 0.85,
            'supported_frameworks': [
                ComplianceFramework.GDPR,
                ComplianceFramework.CCPA,
                ComplianceFramework.DMCA,
                ComplianceFramework.SOC_2,
                ComplianceFramework.ISO_27001
            ]
        }
        
        logger.info("Compliance core manager initialized")
    
    async def conduct_comprehensive_compliance_assessment(
        self, 
        infrastructure_config: Dict[str, Any],
        target_jurisdictions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive compliance assessment across all frameworks
        
        Args:
            infrastructure_config: Current infrastructure configuration
            target_jurisdictions: List of target jurisdictions to assess
            
        Returns:
            Comprehensive compliance report
        """
        assessment_id = f"compliance_assessment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting comprehensive compliance assessment: {assessment_id}")
        
        assessment = {
            'assessment_id': assessment_id,
            'timestamp': datetime.utcnow().isoformat(),
            'infrastructure_config_version': infrastructure_config.get('version', 'unknown'),
            'target_jurisdictions': target_jurisdictions or ['global'],
            'overall_compliance': False,
            'overall_score': 0.0,
            'framework_assessments': {},
            'jurisdiction_assessments': {},
            'risk_summary': {},
            'recommendations': [],
            'critical_findings': [],
            'next_assessment_date': (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        try:
            # Assess each compliance framework
            framework_results = await self._assess_all_frameworks(infrastructure_config)
            assessment['framework_assessments'] = framework_results
            
            # Assess jurisdictional compliance
            if target_jurisdictions:
                jurisdiction_results = await self._assess_jurisdictional_compliance(
                    target_jurisdictions, infrastructure_config
                )
                assessment['jurisdiction_assessments'] = jurisdiction_results
            
            # Conduct comprehensive audit
            audit_results = await self.audit_manager.conduct_comprehensive_audit(
                audit_scope=['data_protection', 'security_controls', 'compliance_frameworks'],
                audit_type='compliance_audit'
            )
            assessment['audit_results'] = audit_results
            
            # Aggregate risk assessment
            risk_summary = await self._aggregate_risk_assessment(assessment)
            assessment['risk_summary'] = risk_summary
            
            # Calculate overall compliance score
            overall_score = await self._calculate_overall_compliance_score(assessment)
            assessment['overall_score'] = overall_score
            assessment['overall_compliance'] = overall_score >= self.compliance_config['compliance_threshold']
            
            # Generate comprehensive recommendations
            recommendations = await self._generate_comprehensive_recommendations(assessment)
            assessment['recommendations'] = recommendations
            
            # Identify critical findings
            critical_findings = await self._identify_critical_findings(assessment)
            assessment['critical_findings'] = critical_findings
            
            # Store assessment
            self.compliance_reports[assessment_id] = assessment
            
            logger.info(f"Compliance assessment completed: {assessment_id}, Score: {overall_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error in comprehensive compliance assessment: {e}")
            assessment['error'] = str(e)
            assessment['status'] = 'failed'
        
        return assessment
    
    async def _assess_all_frameworks(self, infrastructure_config: Dict[str, Any]) -> Dict[str, Any]:
        """Assess all supported compliance frameworks"""
        
        framework_results = {}
        
        # GDPR Assessment
        try:
            gdpr_result = await self.gdpr_manager.assess_gdpr_compliance(infrastructure_config)
            framework_results['gdpr'] = gdpr_result
        except Exception as e:
            logger.error(f"GDPR assessment error: {e}")
            framework_results['gdpr'] = {'error': str(e), 'compliance_score': 0.0}
        
        # CCPA Assessment
        try:
            ccpa_result = await self.ccpa_manager.assess_ccpa_compliance(infrastructure_config)
            framework_results['ccpa'] = ccpa_result
        except Exception as e:
            logger.error(f"CCPA assessment error: {e}")
            framework_results['ccpa'] = {'error': str(e), 'compliance_score': 0.0}
        
        # DMCA Assessment
        try:
            dmca_result = await self.dmca_manager.assess_dmca_compliance(infrastructure_config)
            framework_results['dmca'] = dmca_result
        except Exception as e:
            logger.error(f"DMCA assessment error: {e}")
            framework_results['dmca'] = {'error': str(e), 'compliance_score': 0.0}
        
        return framework_results
    
    async def _assess_jurisdictional_compliance(
        self, 
        jurisdictions: List[str], 
        infrastructure_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess compliance for specific jurisdictions"""
        
        jurisdiction_results = {}
        
        for jurisdiction in jurisdictions:
            try:
                # Define business activities for creator platform
                business_activities = [
                    'content_hosting',
                    'payment_processing',
                    'data_processing',
                    'content_distribution',
                    'creator_monetization',
                    'platform_integrations'
                ]
                
                jurisdiction_result = await self.legal_manager.assess_legal_compliance(
                    jurisdiction, business_activities
                )
                jurisdiction_results[jurisdiction] = jurisdiction_result
                
            except Exception as e:
                logger.error(f"Jurisdiction assessment error for {jurisdiction}: {e}")
                jurisdiction_results[jurisdiction] = {'error': str(e), 'compliance_score': 0.0}
        
        return jurisdiction_results
    
    async def _aggregate_risk_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate risk assessment across all frameworks and jurisdictions"""
        
        risk_summary = {
            'overall_risk_level': 'low',
            'risk_score': 0.0,
            'high_risk_areas': [],
            'medium_risk_areas': [],
            'low_risk_areas': [],
            'cross_framework_risks': [],
            'jurisdiction_risks': [],
            'technical_risks': [],
            'legal_risks': [],
            'operational_risks': []
        }
        
        total_risk = 0.0
        risk_count = 0
        
        # Aggregate framework risks
        for framework, result in assessment.get('framework_assessments', {}).items():
            framework_score = result.get('compliance_score', 0.0)
            framework_risk = (100 - framework_score) / 100.0
            total_risk += framework_risk
            risk_count += 1
            
            # Categorize risk level
            if framework_risk > self.compliance_config['risk_threshold_high']:
                risk_summary['high_risk_areas'].append(f"{framework}_compliance")
            elif framework_risk > self.compliance_config['risk_threshold_medium']:
                risk_summary['medium_risk_areas'].append(f"{framework}_compliance")
            else:
                risk_summary['low_risk_areas'].append(f"{framework}_compliance")
        
        # Aggregate jurisdiction risks
        for jurisdiction, result in assessment.get('jurisdiction_assessments', {}).items():
            jurisdiction_score = result.get('compliance_score', 0.0)
            jurisdiction_risk = (100 - jurisdiction_score) / 100.0
            total_risk += jurisdiction_risk
            risk_count += 1
            
            # Add jurisdiction-specific risks
            legal_risks = result.get('legal_risks', [])
            for legal_risk in legal_risks:
                risk_summary['legal_risks'].append({
                    'jurisdiction': jurisdiction,
                    'risk': legal_risk
                })
        
        # Calculate overall risk score
        if risk_count > 0:
            risk_summary['risk_score'] = total_risk / risk_count
        
        # Determine overall risk level
        if risk_summary['risk_score'] > self.compliance_config['risk_threshold_high']:
            risk_summary['overall_risk_level'] = 'high'
        elif risk_summary['risk_score'] > self.compliance_config['risk_threshold_medium']:
            risk_summary['overall_risk_level'] = 'medium'
        
        # Identify cross-framework risks
        risk_summary['cross_framework_risks'] = await self._identify_cross_framework_risks(assessment)
        
        return risk_summary
    
    async def _identify_cross_framework_risks(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risks that span multiple compliance frameworks"""
        
        cross_risks = []
        
        # Data protection risks affecting multiple frameworks
        frameworks_with_data_issues = []
        for framework, result in assessment.get('framework_assessments', {}).items():
            if framework in ['gdpr', 'ccpa'] and result.get('compliance_score', 0.0) < 0.8:
                frameworks_with_data_issues.append(framework)
        
        if len(frameworks_with_data_issues) > 1:
            cross_risks.append({
                'risk_type': 'data_protection_multi_framework',
                'affected_frameworks': frameworks_with_data_issues,
                'severity': 'high',
                'description': 'Data protection issues affecting multiple privacy frameworks',
                'mitigation': 'Comprehensive data protection program implementation'
            })
        
        # Security control risks affecting compliance
        audit_result = assessment.get('audit_results', {})
        security_findings = audit_result.get('audit_findings', {}).get('security_controls', {})
        if security_findings.get('compliance_score', 1.0) < 0.8:
            cross_risks.append({
                'risk_type': 'security_controls_compliance_impact',
                'affected_frameworks': ['gdpr', 'ccpa', 'dmca'],
                'severity': 'medium',
                'description': 'Security control deficiencies impacting multiple compliance frameworks',
                'mitigation': 'Strengthen security controls and monitoring'
            })
        
        return cross_risks
    
    async def _calculate_overall_compliance_score(self, assessment: Dict[str, Any]) -> float:
        """Calculate weighted overall compliance score"""
        
        # Define framework weights based on business impact
        framework_weights = {
            'gdpr': 0.25,  # High weight due to high penalties
            'ccpa': 0.20,  # Significant for US market
            'dmca': 0.25,  # Critical for content platform
            'audit_overall': 0.20,  # Technical implementation
            'jurisdiction_average': 0.10  # Legal compliance
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        # Framework scores
        for framework, weight in framework_weights.items():
            if framework == 'audit_overall':
                audit_result = assessment.get('audit_results', {})
                score = audit_result.get('compliance_scores', {}).get('overall', 0.0)
                score = score  # Audit scores are already 0-1, convert to 0-100
            elif framework == 'jurisdiction_average':
                jurisdiction_scores = []
                for result in assessment.get('jurisdiction_assessments', {}).values():
                    jurisdiction_scores.append(result.get('compliance_score', 0.0))
                score = sum(jurisdiction_scores) / len(jurisdiction_scores) if jurisdiction_scores else 0.0
            else:
                framework_result = assessment.get('framework_assessments', {}).get(framework, {})
                score = framework_result.get('compliance_score', 0.0)
            
            if score > 0:  # Only include if we have a valid score
                weighted_score += score * weight
                total_weight += weight
        
        # Calculate final score
        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        return round(overall_score, 2)
    
    async def _generate_comprehensive_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations across all frameworks"""
        
        recommendations = []
        
        # Framework-specific recommendations
        for framework, result in assessment.get('framework_assessments', {}).items():
            framework_recommendations = result.get('recommendations', [])
            for rec in framework_recommendations:
                recommendations.append(f"[{framework.upper()}] {rec}")
        
        # Jurisdiction-specific recommendations
        for jurisdiction, result in assessment.get('jurisdiction_assessments', {}).items():
            jurisdiction_recommendations = result.get('recommended_actions', [])
            for rec in jurisdiction_recommendations:
                recommendations.append(f"[{jurisdiction.upper()}] {rec}")
        
        # Audit recommendations
        audit_result = assessment.get('audit_results', {})
        audit_recommendations = audit_result.get('recommendations', [])
        for rec in audit_recommendations:
            recommendations.append(f"[AUDIT] {rec}")
        
        # Cross-framework recommendations
        risk_summary = assessment.get('risk_summary', {})
        if risk_summary.get('overall_risk_level') == 'high':
            recommendations.extend([
                "[PRIORITY] Establish emergency compliance response team",
                "[PRIORITY] Conduct immediate compliance gap analysis",
                "[PRIORITY] Implement compensating controls for high-risk areas"
            ])
        
        # Strategic recommendations
        recommendations.extend([
            "[STRATEGIC] Implement continuous compliance monitoring system",
            "[STRATEGIC] Establish compliance governance framework",
            "[STRATEGIC] Create compliance training program for all staff",
            "[STRATEGIC] Develop compliance metrics and KPI dashboard"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _identify_critical_findings(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify critical compliance findings requiring immediate attention"""
        
        critical_findings = []
        
        # Framework critical findings
        for framework, result in assessment.get('framework_assessments', {}).items():
            framework_score = result.get('compliance_score', 0.0)
            if framework_score < 0.7:  # Critical threshold
                critical_findings.append({
                    'type': 'framework_non_compliance',
                    'framework': framework,
                    'severity': 'critical',
                    'score': framework_score,
                    'description': f"{framework.upper()} compliance below critical threshold",
                    'immediate_action_required': True
                })
        
        # Audit critical findings
        audit_result = assessment.get('audit_results', {})
        for scope, findings in audit_result.get('audit_findings', {}).items():
            critical_issues = findings.get('critical_issues', [])
            for issue in critical_issues:
                critical_findings.append({
                    'type': 'audit_critical_issue',
                    'scope': scope,
                    'severity': 'critical',
                    'issue': issue,
                    'immediate_action_required': True
                })
        
        # Risk-based critical findings
        risk_summary = assessment.get('risk_summary', {})
        high_risk_areas = risk_summary.get('high_risk_areas', [])
        for risk_area in high_risk_areas:
            critical_findings.append({
                'type': 'high_risk_area',
                'area': risk_area,
                'severity': 'high',
                'description': f"High risk identified in {risk_area}",
                'immediate_action_required': True
            })
        
        return critical_findings
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive compliance dashboard"""
        
        dashboard = {
            'last_updated': datetime.utcnow().isoformat(),
            'overall_status': {
                'compliance_score': 0.0,
                'risk_level': 'unknown',
                'frameworks_compliant': 0,
                'total_frameworks': len(self.compliance_config['supported_frameworks']),
                'last_assessment_date': None
            },
            'framework_status': {},
            'risk_summary': {
                'critical_risks': 0,
                'high_risks': 0,
                'medium_risks': 0,
                'low_risks': 0
            },
            'recent_assessments': [],
            'upcoming_deadlines': [],
            'compliance_trends': {},
            'action_items': []
        }
        
        # Get latest assessment
        if self.compliance_reports:
            latest_assessment = max(
                self.compliance_reports.values(),
                key=lambda x: x['timestamp']
            )
            
            dashboard['overall_status'].update({
                'compliance_score': latest_assessment.get('overall_score', 0.0),
                'risk_level': latest_assessment.get('risk_summary', {}).get('overall_risk_level', 'unknown'),
                'last_assessment_date': latest_assessment['timestamp']
            })
            
            # Framework status
            for framework, result in latest_assessment.get('framework_assessments', {}).items():
                dashboard['framework_status'][framework] = {
                    'compliance_score': result.get('compliance_score', 0.0),
                    'status': 'compliant' if result.get('compliance_score', 0.0) >= 85.0 else 'non_compliant',
                    'last_assessed': latest_assessment['timestamp']
                }
                
                if result.get('compliance_score', 0.0) >= 85.0:
                    dashboard['overall_status']['frameworks_compliant'] += 1
            
            # Risk summary
            risk_summary = latest_assessment.get('risk_summary', {})
            dashboard['risk_summary'].update({
                'critical_risks': len(latest_assessment.get('critical_findings', [])),
                'high_risks': len(risk_summary.get('high_risk_areas', [])),
                'medium_risks': len(risk_summary.get('medium_risk_areas', [])),
                'low_risks': len(risk_summary.get('low_risk_areas', []))
            })
            
            # Action items from recommendations
            recommendations = latest_assessment.get('recommendations', [])
            priority_actions = [rec for rec in recommendations if '[PRIORITY]' in rec]
            dashboard['action_items'] = priority_actions[:10]  # Top 10 priority actions
        
        # Recent assessments
        recent_assessments = sorted(
            self.compliance_reports.values(),
            key=lambda x: x['timestamp'],
            reverse=True
        )[:5]
        
        dashboard['recent_assessments'] = [
            {
                'assessment_id': assessment['assessment_id'],
                'timestamp': assessment['timestamp'],
                'overall_score': assessment.get('overall_score', 0.0),
                'frameworks_assessed': len(assessment.get('framework_assessments', {})),
                'critical_findings': len(assessment.get('critical_findings', []))
            }
            for assessment in recent_assessments
        ]
        
        return dashboard
    
    async def schedule_automated_monitoring(self) -> Dict[str, Any]:
        """Schedule automated compliance monitoring"""
        
        monitoring_schedule = {
            'enabled': self.compliance_config['automated_monitoring'],
            'frequency_days': self.compliance_config['assessment_frequency_days'],
            'next_assessment': (
                datetime.utcnow() + 
                timedelta(days=self.compliance_config['assessment_frequency_days'])
            ).isoformat(),
            'frameworks_monitored': [f.value for f in self.compliance_config['supported_frameworks']],
            'monitoring_tasks': []
        }
        
        if monitoring_schedule['enabled']:
            # Schedule framework-specific monitoring
            for framework in self.compliance_config['supported_frameworks']:
                task = {
                    'framework': framework.value,
                    'frequency_days': 30,
                    'next_check': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                    'automated': True
                }
                monitoring_schedule['monitoring_tasks'].append(task)
            
            # Schedule audit tasks
            audit_task = {
                'task_type': 'comprehensive_audit',
                'frequency_days': 90,
                'next_audit': (datetime.utcnow() + timedelta(days=90)).isoformat(),
                'scope': ['data_protection', 'security_controls', 'compliance_frameworks']
            }
            monitoring_schedule['monitoring_tasks'].append(audit_task)
        
        logger.info("Automated compliance monitoring scheduled")
        return monitoring_schedule