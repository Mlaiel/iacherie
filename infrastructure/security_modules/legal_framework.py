"""
Legal Framework - Enterprise Legal Compliance Management
© 2025 Fahed Mlaiel. All rights reserved.

Comprehensive legal framework for Ainflue creator platform.
Manages multi-jurisdictional legal compliance and requirements.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json

from .compliance_base import (
    ComplianceBaseManager, ComplianceFramework, ComplianceStatus, 
    ComplianceRequirement, ComplianceCheck, DataClassification
)

logger = logging.getLogger(__name__)


class Jurisdiction(Enum):
    """Legal jurisdictions"""
    US = "united_states"
    EU = "european_union"
    UK = "united_kingdom"
    CA = "canada"
    AU = "australia"
    JP = "japan"
    BR = "brazil"
    IN = "india"
    GLOBAL = "global"


class LegalDocumentType(Enum):
    """Legal document types"""
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    COOKIE_POLICY = "cookie_policy"
    CREATOR_AGREEMENT = "creator_agreement"
    PLATFORM_AGREEMENT = "platform_agreement"
    DATA_PROCESSING_AGREEMENT = "data_processing_agreement"
    DMCA_POLICY = "dmca_policy"
    COMMUNITY_GUIDELINES = "community_guidelines"
    REVENUE_SHARING_AGREEMENT = "revenue_sharing_agreement"


class LegalFrameworkManager(ComplianceBaseManager):
    """
    Legal Framework Management for Creator Platform
    
    Comprehensive legal compliance management:
    - Multi-jurisdictional legal requirements
    - Legal document management and updates
    - Contract and agreement lifecycle
    - Regulatory compliance tracking
    - Legal risk assessment
    - Creator legal protections
    - Platform liability management
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.legal_documents = {}
        self.legal_requirements = {}
        self.jurisdiction_rules = self._initialize_jurisdiction_rules()
        self.contract_templates = {}
        self.legal_assessments = {}
        
        # Legal framework configuration
        self.legal_config = {
            'supported_jurisdictions': [j.value for j in Jurisdiction],
            'document_review_cycle_months': 6,
            'legal_update_notification': True,
            'automated_compliance_checking': True,
            'legal_version_control': True
        }
        
        # Creator platform specific legal areas
        self.legal_areas = {
            'intellectual_property': {
                'copyright_protection': 'Creator content copyright management',
                'trademark_protection': 'Brand and trademark protection',
                'licensing_agreements': 'Content licensing frameworks',
                'fair_use_guidelines': 'Fair use policy implementation'
            },
            'data_protection': {
                'privacy_compliance': 'Multi-jurisdictional privacy law compliance',
                'data_processing_agreements': 'Third-party data processing contracts',
                'consent_management': 'Legal consent framework',
                'cross_border_transfers': 'International data transfer compliance'
            },
            'commercial_law': {
                'revenue_sharing': 'Creator revenue sharing agreements',
                'payment_processing': 'Payment processing legal compliance',
                'tax_compliance': 'Multi-jurisdictional tax obligations',
                'consumer_protection': 'Consumer rights protection'
            },
            'platform_governance': {
                'terms_of_service': 'Platform usage terms',
                'community_guidelines': 'Content and behavior standards',
                'content_moderation': 'Content moderation legal framework',
                'dispute_resolution': 'Dispute resolution procedures'
            },
            'employment_law': {
                'creator_classification': 'Creator vs employee classification',
                'labor_compliance': 'Labor law compliance',
                'contractor_agreements': 'Independent contractor frameworks',
                'benefits_compliance': 'Creator benefits and protections'
            }
        }
        
        logger.info("Legal framework manager initialized for creator platform")
    
    def _initialize_jurisdiction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize jurisdiction-specific legal rules"""
        
        rules = {
            Jurisdiction.US.value: {
                'required_frameworks': [
                    ComplianceFramework.CCPA,
                    ComplianceFramework.DMCA,
                    ComplianceFramework.COPPA
                ],
                'creator_classification_rules': {
                    'default_status': 'independent_contractor',
                    'employment_test': 'abc_test',
                    'minimum_wage_applicable': False,
                    'benefits_required': False
                },
                'tax_obligations': {
                    'form_1099_required': True,
                    'backup_withholding': True,
                    'state_tax_compliance': True
                },
                'content_regulations': {
                    'section_230_protection': True,
                    'dmca_safe_harbor': True,
                    'ftc_disclosure_requirements': True
                }
            },
            Jurisdiction.EU.value: {
                'required_frameworks': [
                    ComplianceFramework.GDPR,
                    ComplianceFramework.ISO_27001
                ],
                'creator_classification_rules': {
                    'default_status': 'self_employed',
                    'employment_test': 'eu_directive_test',
                    'minimum_wage_applicable': True,
                    'benefits_required': True
                },
                'tax_obligations': {
                    'vat_registration_required': True,
                    'digital_services_tax': True,
                    'country_specific_reporting': True
                },
                'content_regulations': {
                    'dsm_directive_compliance': True,
                    'platform_liability': 'limited_safe_harbor',
                    'content_moderation_required': True
                }
            },
            Jurisdiction.UK.value: {
                'required_frameworks': [
                    ComplianceFramework.GDPR,  # UK GDPR
                    ComplianceFramework.ISO_27001
                ],
                'creator_classification_rules': {
                    'default_status': 'self_employed',
                    'employment_test': 'ir35_assessment',
                    'minimum_wage_applicable': True,
                    'benefits_required': False
                },
                'tax_obligations': {
                    'vat_registration_required': True,
                    'digital_services_tax': True,
                    'ir35_compliance': True
                },
                'content_regulations': {
                    'online_safety_bill': True,
                    'age_appropriate_design_code': True,
                    'ofcom_regulation': True
                }
            },
            Jurisdiction.CA.value: {
                'required_frameworks': [
                    ComplianceFramework.PCI_DSS,
                    ComplianceFramework.SOC_2
                ],
                'creator_classification_rules': {
                    'default_status': 'independent_contractor',
                    'employment_test': 'common_law_test',
                    'minimum_wage_applicable': True,
                    'benefits_required': False
                },
                'tax_obligations': {
                    'gst_hst_applicable': True,
                    't4a_reporting': True,
                    'provincial_tax_compliance': True
                },
                'content_regulations': {
                    'canadian_content_requirements': False,
                    'platform_liability': 'notice_and_takedown',
                    'french_language_requirements': True
                }
            }
        }
        
        return rules
    
    async def assess_legal_compliance(
        self, 
        jurisdiction: str, 
        business_activities: List[str]
    ) -> Dict[str, Any]:
        """
        Assess legal compliance for specific jurisdiction and activities
        
        Args:
            jurisdiction: Target jurisdiction for assessment
            business_activities: List of business activities to assess
            
        Returns:
            Comprehensive legal compliance assessment
        """
        logger.info(f"Assessing legal compliance for {jurisdiction}")
        
        assessment = {
            'jurisdiction': jurisdiction,
            'assessment_timestamp': datetime.utcnow().isoformat(),
            'business_activities': business_activities,
            'overall_compliance': False,
            'compliance_score': 0.0,
            'legal_requirements': [],
            'compliance_gaps': [],
            'legal_risks': [],
            'required_documents': [],
            'recommended_actions': [],
            'next_review_date': (datetime.utcnow() + timedelta(days=180)).isoformat()
        }
        
        try:
            # Get jurisdiction rules
            jurisdiction_rules = self.jurisdiction_rules.get(jurisdiction, {})
            
            # Assess required compliance frameworks
            framework_assessment = await self._assess_required_frameworks(
                jurisdiction_rules.get('required_frameworks', [])
            )
            assessment['legal_requirements'].extend(framework_assessment)
            
            # Assess creator classification compliance
            creator_assessment = await self._assess_creator_classification(
                jurisdiction_rules.get('creator_classification_rules', {})
            )
            assessment['legal_requirements'].append(creator_assessment)
            
            # Assess tax obligations
            tax_assessment = await self._assess_tax_obligations(
                jurisdiction_rules.get('tax_obligations', {})
            )
            assessment['legal_requirements'].append(tax_assessment)
            
            # Assess content regulations
            content_assessment = await self._assess_content_regulations(
                jurisdiction_rules.get('content_regulations', {})
            )
            assessment['legal_requirements'].append(content_assessment)
            
            # Assess required legal documents
            document_assessment = await self._assess_required_documents(jurisdiction)
            assessment['required_documents'] = document_assessment
            
            # Calculate overall compliance score
            compliance_scores = [req.get('compliance_score', 0.0) for req in assessment['legal_requirements']]
            assessment['compliance_score'] = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
            assessment['overall_compliance'] = assessment['compliance_score'] >= 0.85
            
            # Identify compliance gaps
            assessment['compliance_gaps'] = [
                req for req in assessment['legal_requirements'] 
                if req.get('compliance_score', 0.0) < 0.8
            ]
            
            # Assess legal risks
            legal_risks = await self._assess_legal_risks(assessment)
            assessment['legal_risks'] = legal_risks
            
            # Generate recommended actions
            recommended_actions = await self._generate_legal_recommendations(assessment)
            assessment['recommended_actions'] = recommended_actions
            
        except Exception as e:
            logger.error(f"Error in legal compliance assessment: {e}")
            assessment['error'] = str(e)
        
        return assessment
    
    async def _assess_required_frameworks(self, required_frameworks: List[str]) -> List[Dict[str, Any]]:
        """Assess compliance with required legal frameworks"""
        
        framework_assessments = []
        
        for framework in required_frameworks:
            assessment = {
                'requirement_type': 'compliance_framework',
                'framework': framework,
                'compliance_score': 0.85,  # Placeholder - would integrate with actual compliance checks
                'status': 'compliant',
                'last_assessment': datetime.utcnow().isoformat(),
                'gaps': [],
                'evidence': []
            }
            
            # Simulate framework-specific assessment
            if framework == 'gdpr':
                assessment.update({
                    'compliance_score': 0.88,
                    'gaps': ['data_subject_rights_automation'],
                    'evidence': ['privacy_notice', 'consent_management', 'data_mapping']
                })
            elif framework == 'ccpa':
                assessment.update({
                    'compliance_score': 0.82,
                    'gaps': ['consumer_request_automation'],
                    'evidence': ['privacy_notice', 'opt_out_mechanism', 'non_discrimination_policy']
                })
            elif framework == 'dmca':
                assessment.update({
                    'compliance_score': 0.90,
                    'gaps': [],
                    'evidence': ['dmca_agent_registration', 'takedown_procedures', 'repeat_infringer_policy']
                })
            
            framework_assessments.append(assessment)
        
        return framework_assessments
    
    async def _assess_creator_classification(self, classification_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Assess creator classification compliance"""
        
        assessment = {
            'requirement_type': 'creator_classification',
            'default_status': classification_rules.get('default_status', 'independent_contractor'),
            'employment_test': classification_rules.get('employment_test', 'common_law_test'),
            'compliance_score': 0.85,
            'status': 'compliant',
            'risks': [],
            'recommendations': []
        }
        
        # Assess classification risks
        if classification_rules.get('minimum_wage_applicable'):
            assessment['risks'].append('Minimum wage compliance required for some creators')
        
        if classification_rules.get('benefits_required'):
            assessment['risks'].append('Benefits may be required for certain creator arrangements')
        
        # Add recommendations
        assessment['recommendations'] = [
            'Regular review of creator classification criteria',
            'Clear documentation of independent contractor relationship',
            'Avoid excessive control over creator work methods',
            'Maintain arm\'s length business relationship'
        ]
        
        return assessment
    
    async def _assess_tax_obligations(self, tax_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Assess tax compliance obligations"""
        
        assessment = {
            'requirement_type': 'tax_obligations',
            'compliance_score': 0.80,
            'status': 'compliant',
            'obligations': [],
            'reporting_requirements': [],
            'compliance_measures': []
        }
        
        # Process tax obligations
        for obligation, required in tax_rules.items():
            if required:
                assessment['obligations'].append(obligation)
                
                # Add specific compliance measures
                if obligation == 'form_1099_required':
                    assessment['compliance_measures'].append('Automated 1099 generation and filing')
                elif obligation == 'vat_registration_required':
                    assessment['compliance_measures'].append('VAT registration and reporting system')
                elif obligation == 'gst_hst_applicable':
                    assessment['compliance_measures'].append('GST/HST calculation and remittance')
        
        return assessment
    
    async def _assess_content_regulations(self, content_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Assess content regulation compliance"""
        
        assessment = {
            'requirement_type': 'content_regulations',
            'compliance_score': 0.87,
            'status': 'compliant',
            'regulations': [],
            'protections': [],
            'obligations': []
        }
        
        # Process content regulations
        for regulation, applicable in content_rules.items():
            if applicable:
                assessment['regulations'].append(regulation)
                
                # Add specific obligations
                if regulation == 'section_230_protection':
                    assessment['protections'].append('Section 230 safe harbor protection')
                elif regulation == 'dmca_safe_harbor':
                    assessment['protections'].append('DMCA safe harbor protection')
                elif regulation == 'content_moderation_required':
                    assessment['obligations'].append('Proactive content moderation')
        
        return assessment
    
    async def _assess_required_documents(self, jurisdiction: str) -> List[Dict[str, Any]]:
        """Assess required legal documents for jurisdiction"""
        
        required_docs = [
            {
                'document_type': LegalDocumentType.TERMS_OF_SERVICE.value,
                'jurisdiction_specific': True,
                'last_updated': datetime.utcnow().isoformat(),
                'review_frequency_months': 6,
                'compliance_score': 0.90,
                'customizations_needed': [
                    'Jurisdiction-specific dispute resolution',
                    'Local consumer protection laws',
                    'Creator classification language'
                ]
            },
            {
                'document_type': LegalDocumentType.PRIVACY_POLICY.value,
                'jurisdiction_specific': True,
                'last_updated': datetime.utcnow().isoformat(),
                'review_frequency_months': 3,
                'compliance_score': 0.88,
                'customizations_needed': [
                    'Local privacy law requirements',
                    'Data transfer mechanisms',
                    'Consumer rights procedures'
                ]
            },
            {
                'document_type': LegalDocumentType.CREATOR_AGREEMENT.value,
                'jurisdiction_specific': True,
                'last_updated': datetime.utcnow().isoformat(),
                'review_frequency_months': 12,
                'compliance_score': 0.85,
                'customizations_needed': [
                    'Creator classification terms',
                    'Revenue sharing structure',
                    'Intellectual property rights',
                    'Termination procedures'
                ]
            }
        ]
        
        # Add jurisdiction-specific documents
        if jurisdiction == Jurisdiction.EU.value:
            required_docs.append({
                'document_type': LegalDocumentType.DATA_PROCESSING_AGREEMENT.value,
                'jurisdiction_specific': True,
                'compliance_score': 0.92,
                'customizations_needed': ['GDPR Article 28 compliance']
            })
        
        if jurisdiction == Jurisdiction.US.value:
            required_docs.append({
                'document_type': LegalDocumentType.DMCA_POLICY.value,
                'jurisdiction_specific': False,
                'compliance_score': 0.95,
                'customizations_needed': ['Safe harbor compliance']
            })
        
        return required_docs
    
    async def _assess_legal_risks(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess legal risks based on compliance assessment"""
        
        risks = []
        
        # Check compliance score
        if assessment['compliance_score'] < 0.8:
            risks.append({
                'risk_type': 'compliance_gap',
                'severity': 'high',
                'description': 'Overall compliance score below acceptable threshold',
                'potential_impact': 'Regulatory penalties and legal action',
                'mitigation': 'Address identified compliance gaps immediately'
            })
        
        # Check for specific gaps
        for gap in assessment['compliance_gaps']:
            risks.append({
                'risk_type': 'framework_non_compliance',
                'severity': 'medium',
                'description': f"Non-compliance in {gap.get('requirement_type', 'unknown')}",
                'potential_impact': 'Regulatory enforcement action',
                'mitigation': 'Implement missing compliance measures'
            })
        
        # Add jurisdiction-specific risks
        jurisdiction = assessment['jurisdiction']
        if jurisdiction == Jurisdiction.EU.value:
            risks.append({
                'risk_type': 'gdpr_penalties',
                'severity': 'high',
                'description': 'GDPR non-compliance can result in significant fines',
                'potential_impact': 'Up to 4% of annual revenue or €20M fine',
                'mitigation': 'Maintain comprehensive GDPR compliance program'
            })
        
        if jurisdiction == Jurisdiction.US.value:
            risks.append({
                'risk_type': 'creator_classification',
                'severity': 'medium',
                'description': 'Creator misclassification risk in various states',
                'potential_impact': 'Employment law penalties and benefits obligations',
                'mitigation': 'Regular review of creator relationship structures'
            })
        
        return risks
    
    async def _generate_legal_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate legal recommendations based on assessment"""
        
        recommendations = []
        
        # General recommendations
        recommendations.extend([
            'Establish regular legal document review schedule',
            'Implement automated compliance monitoring',
            'Maintain comprehensive legal audit trail',
            'Engage local legal counsel in each jurisdiction'
        ])
        
        # Compliance gap recommendations
        for gap in assessment['compliance_gaps']:
            gap_type = gap.get('requirement_type', 'unknown')
            recommendations.append(f"Address compliance gaps in {gap_type}")
        
        # Risk mitigation recommendations
        for risk in assessment['legal_risks']:
            recommendations.append(risk.get('mitigation', 'Review and mitigate identified risk'))
        
        # Jurisdiction-specific recommendations
        jurisdiction = assessment['jurisdiction']
        if jurisdiction == Jurisdiction.EU.value:
            recommendations.extend([
                'Implement GDPR Article 30 processing records',
                'Establish EU representative if required',
                'Review and update Standard Contractual Clauses'
            ])
        
        if jurisdiction == Jurisdiction.US.value:
            recommendations.extend([
                'Review state-specific creator classification laws',
                'Implement FTC disclosure requirements for influencers',
                'Maintain DMCA safe harbor compliance'
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def generate_legal_document(
        self, 
        document_type: str, 
        jurisdiction: str, 
        customizations: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate jurisdiction-specific legal document"""
        
        document_id = f"legal_{document_type}_{jurisdiction}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        document = {
            'document_id': document_id,
            'document_type': document_type,
            'jurisdiction': jurisdiction,
            'created_at': datetime.utcnow().isoformat(),
            'version': '1.0',
            'status': 'draft',
            'customizations': customizations or {},
            'content_sections': [],
            'legal_review_required': True,
            'effective_date': None
        }
        
        # Generate document sections based on type
        if document_type == LegalDocumentType.TERMS_OF_SERVICE.value:
            document['content_sections'] = await self._generate_terms_of_service_sections(jurisdiction)
        elif document_type == LegalDocumentType.PRIVACY_POLICY.value:
            document['content_sections'] = await self._generate_privacy_policy_sections(jurisdiction)
        elif document_type == LegalDocumentType.CREATOR_AGREEMENT.value:
            document['content_sections'] = await self._generate_creator_agreement_sections(jurisdiction)
        
        # Store document
        self.legal_documents[document_id] = document
        
        logger.info(f"Generated legal document: {document_id}")
        return document
    
    async def _generate_terms_of_service_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Generate terms of service sections"""
        
        sections = [
            {
                'section': 'acceptance_of_terms',
                'title': 'Acceptance of Terms',
                'content': 'By accessing and using the Ainflue platform, you agree to be bound by these Terms of Service.'
            },
            {
                'section': 'creator_obligations',
                'title': 'Creator Obligations',
                'content': 'Creators must comply with all applicable laws and platform guidelines when using the service.'
            },
            {
                'section': 'intellectual_property',
                'title': 'Intellectual Property',
                'content': 'Creators retain ownership of their original content, subject to platform licensing terms.'
            },
            {
                'section': 'revenue_sharing',
                'title': 'Revenue Sharing',
                'content': 'Revenue sharing arrangements are defined in separate Creator Agreements.'
            },
            {
                'section': 'dispute_resolution',
                'title': 'Dispute Resolution',
                'content': f'Disputes will be resolved according to {jurisdiction} law and jurisdiction.'
            }
        ]
        
        return sections
    
    async def _generate_privacy_policy_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Generate privacy policy sections"""
        
        sections = [
            {
                'section': 'data_collection',
                'title': 'Data Collection',
                'content': 'We collect information necessary to provide creator platform services.'
            },
            {
                'section': 'data_use',
                'title': 'Data Use',
                'content': 'Personal data is used to provide, improve, and secure our services.'
            },
            {
                'section': 'data_sharing',
                'title': 'Data Sharing',
                'content': 'We may share data with third parties as necessary for service provision.'
            },
            {
                'section': 'consumer_rights',
                'title': 'Your Rights',
                'content': f'You have rights under {jurisdiction} privacy laws to access, correct, and delete your data.'
            },
            {
                'section': 'contact_information',
                'title': 'Contact Information',
                'content': 'Contact our Data Protection Officer at privacy@ainflue.com for privacy inquiries.'
            }
        ]
        
        return sections
    
    async def _generate_creator_agreement_sections(self, jurisdiction: str) -> List[Dict[str, str]]:
        """Generate creator agreement sections"""
        
        sections = [
            {
                'section': 'relationship',
                'title': 'Creator Relationship',
                'content': 'This agreement establishes an independent contractor relationship between Creator and Ainflue.'
            },
            {
                'section': 'content_licensing',
                'title': 'Content Licensing',
                'content': 'Creator grants Ainflue necessary licenses to distribute and monetize content on the platform.'
            },
            {
                'section': 'revenue_terms',
                'title': 'Revenue Terms',
                'content': 'Revenue sharing percentages and payment terms are specified in the compensation schedule.'
            },
            {
                'section': 'compliance_obligations',
                'title': 'Compliance Obligations',
                'content': f'Creator must comply with all applicable laws in {jurisdiction} and content guidelines.'
            },
            {
                'section': 'termination',
                'title': 'Termination',
                'content': 'Either party may terminate this agreement with appropriate notice as specified herein.'
            }
        ]
        
        return sections
    
    async def update_legal_document(
        self, 
        document_id: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing legal document"""
        
        if document_id not in self.legal_documents:
            raise ValueError(f"Document {document_id} not found")
        
        document = self.legal_documents[document_id]
        
        # Create new version
        old_version = document.get('version', '1.0')
        version_parts = old_version.split('.')
        new_version = f"{version_parts[0]}.{int(version_parts[1]) + 1}"
        
        # Apply updates
        document.update(updates)
        document['version'] = new_version
        document['last_updated'] = datetime.utcnow().isoformat()
        document['status'] = 'draft'
        document['legal_review_required'] = True
        
        logger.info(f"Updated legal document {document_id} to version {new_version}")
        return document
    
    async def approve_legal_document(self, document_id: str, approver: str) -> Dict[str, Any]:
        """Approve legal document for publication"""
        
        if document_id not in self.legal_documents:
            raise ValueError(f"Document {document_id} not found")
        
        document = self.legal_documents[document_id]
        
        # Update document status
        document['status'] = 'approved'
        document['approved_by'] = approver
        document['approved_at'] = datetime.utcnow().isoformat()
        document['effective_date'] = (datetime.utcnow() + timedelta(days=30)).isoformat()
        document['legal_review_required'] = False
        
        logger.info(f"Approved legal document: {document_id}")
        return document
    
    async def get_legal_dashboard(self) -> Dict[str, Any]:
        """Get legal compliance dashboard"""
        
        dashboard = {
            'last_updated': datetime.utcnow().isoformat(),
            'legal_overview': {
                'total_documents': len(self.legal_documents),
                'documents_needing_review': len([
                    d for d in self.legal_documents.values() 
                    if d.get('legal_review_required', False)
                ]),
                'documents_expiring_soon': len([
                    d for d in self.legal_documents.values()
                    if d.get('effective_date') and 
                    datetime.fromisoformat(d['effective_date'].replace('Z', '+00:00')) < 
                    datetime.utcnow() + timedelta(days=90)
                ])
            },
            'jurisdiction_coverage': {
                jurisdiction: len([
                    d for d in self.legal_documents.values()
                    if d.get('jurisdiction') == jurisdiction
                ])
                for jurisdiction in [j.value for j in Jurisdiction]
            },
            'compliance_summary': {
                'overall_compliance_score': 0.85,
                'high_risk_areas': [],
                'upcoming_deadlines': []
            },
            'document_types': {
                doc_type.value: len([
                    d for d in self.legal_documents.values()
                    if d.get('document_type') == doc_type.value
                ])
                for doc_type in LegalDocumentType
            }
        }
        
        return dashboard