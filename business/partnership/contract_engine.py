"""Contract Engine for IA Influencer Agent
Advanced legal contract generation and management system

⚠️ STRICT COPYRIGHT WARNING ⚠️
Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
All rights reserved. Unauthorized use, copying, or reproduction 
of this code, concept, or intellectual property without explicit 
written permission from Fahed Mlaiel is strictly prohibited.

Development Team Specialties:
- Lead Developer + AI Architect: Fahed Mlaiel
- Senior Backend Developer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architecture Expert
- Audio Processing Developer
- DevOps Engineer
- AI Prompt Engineering Specialist
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from docx import Document
import markdown

from .partnership_models import (
    Partnership, Contract, ContractType, ContractTerm,
    PartnershipType, RevenueModel
)
from ..core.exceptions import ContractError, ValidationError


logger = logging.getLogger(__name__)


class ContractEngine:
    """
    Advanced contract generation and management engine for partnerships.
    Handles legal document creation, template management, and contract lifecycle.
    """
    def __init__(self, templates_path: Optional[str] = None):
        self.templates_path = templates_path or "./contract_templates"
        self.template_env = Environment(
            loader=FileSystemLoader(self.templates_path),
            autoescape=True
        )
        self.logger = logger
        
        # Contract templates registry
        self.contract_templates = {
            ContractType.EXCLUSIVE: "exclusive_partnership_template.html",
            ContractType.NON_EXCLUSIVE: "non_exclusive_partnership_template.html",
            ContractType.REVENUE_SHARE: "revenue_share_template.html",
            ContractType.FLAT_FEE: "flat_fee_template.html",
            ContractType.PERFORMANCE_BASED: "performance_based_template.html",
            ContractType.HYBRID: "hybrid_partnership_template.html"
        }

    async def generate_partnership_contract(
        self,
        partnership: Partnership,
        contract_terms: Dict[str, Any]
    ) -> Contract:
        """Generate comprehensive partnership contract"""
        try:
            # Determine contract type based on partnership
            contract_type = self._determine_contract_type(partnership, contract_terms)
            
            # Generate contract terms
            terms_conditions = await self._generate_contract_terms(
                partnership, contract_terms, contract_type
            )

            # Create contract entity
            contract = Contract(
                partnership_id=partnership.partnership_id,
                contract_type=contract_type,
                terms_and_conditions=terms_conditions,
                payment_terms=self._generate_payment_terms(partnership, contract_terms),
                intellectual_property=self._generate_ip_terms(partnership, contract_terms),
                termination_clauses=self._generate_termination_clauses(contract_terms),
                governing_law=contract_terms.get('governing_law', 'Delaware'),
                jurisdiction=contract_terms.get('jurisdiction', 'Delaware'),
                dispute_resolution=contract_terms.get('dispute_resolution', 'binding_arbitration')
            )

            # Generate contract document
            contract.contract_document_url = await self._generate_contract_document(
                contract, partnership, contract_terms
            )

            self.logger.info(f"Contract generated for partnership: {partnership.partnership_id}")
            return contract

        except Exception as e:
            self.logger.error(f"Contract generation failed: {str(e)}")
            raise ContractError(f"Failed to generate contract: {str(e)}")

    async def validate_contract_terms(
        self,
        contract: Contract,
        validation_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate contract terms for legal compliance"""
        try:
            validation_result = {
                'is_valid': True,
                'warnings': [],
                'errors': [],
                'recommendations': [],
                'compliance_score': 0.0
            }

            # Legal compliance checks
            compliance_checks = await self._perform_compliance_checks(contract)
            validation_result.update(compliance_checks)

            # Business logic validation
            business_validation = await self._validate_business_terms(contract)
            validation_result['warnings'].extend(business_validation.get('warnings', []))
            validation_result['errors'].extend(business_validation.get('errors', []))

            # Risk assessment
            risk_assessment = await self._assess_contract_risks(contract)
            validation_result['risk_score'] = risk_assessment['overall_risk']
            validation_result['risk_factors'] = risk_assessment['risk_factors']

            # Calculate overall compliance score
            validation_result['compliance_score'] = await self._calculate_compliance_score(
                validation_result
            )

            if validation_result['errors']:
                validation_result['is_valid'] = False

            self.logger.info(f"Contract validation completed: {contract.contract_id}")
            return validation_result

        except Exception as e:
            self.logger.error(f"Contract validation failed: {str(e)}")
            raise ContractError(f"Failed to validate contract: {str(e)}")

    async def amend_contract(
        self,
        contract: Contract,
        amendments: Dict[str, Any],
        amended_by: str
    ) -> Contract:
        """Create contract amendment with version control"""
        try:
            # Validate amendment permissions
            if not await self._validate_amendment_permissions(contract, amended_by):
                raise ContractError("Insufficient permissions to amend contract")

            # Create amendment record
            amendment_record = {
                'amendment_id': str(uuid.uuid4()),
                'contract_version': contract.contract_version,
                'changes': amendments,
                'amended_by': amended_by,
                'amendment_date': datetime.utcnow().isoformat(),
                'approval_status': 'pending',
                'legal_review_required': await self._requires_legal_review(amendments)
            }

            # Update contract version
            version_parts = contract.contract_version.split('.')
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            contract.contract_version = '.'.join(version_parts)

            # Apply amendments to contract terms
            await self._apply_amendments(contract, amendments)

            # Add amendment to contract history
            contract.amendments.append(amendment_record)
            contract.updated_at = datetime.utcnow()

            # Generate updated contract document
            if amendment_record['legal_review_required']:
                contract.legal_review_status = 'pending_amendment_review'
            else:
                contract.contract_document_url = await self._regenerate_contract_document(contract)

            self.logger.info(f"Contract amended: {contract.contract_id}")
            return contract

        except Exception as e:
            self.logger.error(f"Contract amendment failed: {str(e)}")
            raise ContractError(f"Failed to amend contract: {str(e)}")

    async def execute_contract(
        self,
        contract: Contract,
        creator_signature: Dict[str, Any],
        partner_signature: Dict[str, Any]
    ) -> Contract:
        """Execute contract with digital signatures"""
        try:
            # Validate signatures
            creator_validation = await self._validate_signature(creator_signature)
            partner_validation = await self._validate_signature(partner_signature)

            if not (creator_validation['valid'] and partner_validation['valid']):
                raise ContractError("Invalid digital signatures")

            # Apply signatures
            contract.creator_signature = creator_signature
            contract.partner_signature = partner_signature
            contract.effective_date = datetime.utcnow()
            contract.legal_review_status = 'executed'

            # Set expiration date if specified
            if contract.terms_and_conditions:
                contract_duration = next(
                    (term for term in contract.terms_and_conditions 
                     if term.term_name == 'contract_duration'), None
                )
                if contract_duration and contract_duration.term_value:
                    months = int(contract_duration.term_value)
                    contract.expiration_date = contract.effective_date + timedelta(days=months * 30)

            # Generate executed contract document
            contract.contract_document_url = await self._generate_executed_contract_document(
                contract
            )

            # Notify stakeholders
            await self._notify_contract_execution(contract)

            self.logger.info(f"Contract executed: {contract.contract_id}")
            return contract

        except Exception as e:
            self.logger.error(f"Contract execution failed: {str(e)}")
            raise ContractError(f"Failed to execute contract: {str(e)}")

    async def generate_contract_summary(self, contract: Contract) -> Dict[str, Any]:
        """Generate executive summary of contract terms"""
        try:
            summary = {
                'contract_overview': {
                    'contract_id': contract.contract_id,
                    'contract_type': contract.contract_type.value,
                    'status': contract.legal_review_status,
                    'effective_date': contract.effective_date.isoformat() if contract.effective_date else None,
                    'expiration_date': contract.expiration_date.isoformat() if contract.expiration_date else None
                },
                'key_terms': {},
                'financial_terms': {},
                'obligations': {
                    'creator_obligations': [],
                    'partner_obligations': []
                },
                'risk_factors': [],
                'renewal_terms': {}
            }

            # Extract key terms
            for term in contract.terms_and_conditions:
                if term.term_name in ['exclusivity', 'territory', 'duration']:
                    summary['key_terms'][term.term_name] = term.term_value

            # Extract financial terms
            summary['financial_terms'] = contract.payment_terms.copy()

            # Extract obligations and clauses
            summary['obligations'] = await self._extract_obligations(contract)
            summary['risk_factors'] = await self._identify_contract_risks(contract)

            self.logger.info(f"Contract summary generated: {contract.contract_id}")
            return summary

        except Exception as e:
            self.logger.error(f"Contract summary generation failed: {str(e)}")
            raise ContractError(f"Failed to generate summary: {str(e)}")

    # Private helper methods

    def _determine_contract_type(
        self,
        partnership: Partnership,
        contract_terms: Dict[str, Any]
    ) -> ContractType:
        """Determine optimal contract type based on partnership"""
        if partnership.revenue_model == RevenueModel.PERCENTAGE_SPLIT:
            return ContractType.REVENUE_SHARE
        elif partnership.revenue_model == RevenueModel.FLAT_RATE:
            return ContractType.FLAT_FEE
        elif partnership.revenue_model == RevenueModel.PERFORMANCE_BONUS:
            return ContractType.PERFORMANCE_BASED
        elif contract_terms.get('exclusivity', False):
            return ContractType.EXCLUSIVE
        else:
            return ContractType.NON_EXCLUSIVE

    async def _generate_contract_terms(
        self,
        partnership: Partnership,
        contract_terms: Dict[str, Any],
        contract_type: ContractType
    ) -> List[ContractTerm]:
        """
Generate comprehensive contract terms"""
        terms = []

        # Core partnership terms
        terms.append(ContractTerm(
            term_id=str(uuid.uuid4()),
            term_name="partnership_type",
            term_value=partnership.partner_type.value,
            is_negotiable=False,
            priority_level="critical",
            legal_implications=["Defines scope of partnership"]
        ))

        # Revenue terms
        terms.append(ContractTerm(
            term_id=str(uuid.uuid4()),
            term_name="commission_rate",
            term_value=str(partnership.commission_rate),
            is_negotiable=True,
            priority_level="high",
            legal_implications=["Revenue distribution", "Tax implications"]
        ))

        # Duration terms
        duration_months = contract_terms.get('duration_months', 12)
        terms.append(ContractTerm(
            term_id=str(uuid.uuid4()),
            term_name="contract_duration",
            term_value=duration_months,
            is_negotiable=True,
            priority_level="medium",
            legal_implications=["Contract validity period"]
        ))

        # Content obligations
        if partnership.content_categories:
            terms.append(ContractTerm(
                term_id=str(uuid.uuid4()),
                term_name="content_categories",
                term_value=partnership.content_categories,
                is_negotiable=True,
                priority_level="medium",
                legal_implications=["Content creation obligations"]
            ))

        # Exclusivity terms
        if contract_terms.get('exclusivity'):
            terms.append(ContractTerm(
                term_id=str(uuid.uuid4()),
                term_name="exclusivity_clause",
                term_value=contract_terms['exclusivity'],
                is_negotiable=True,
                priority_level="high",
                legal_implications=["Exclusivity restrictions", "Competitor limitations"]
            ))

        # Performance requirements
        if contract_terms.get('performance_metrics'):
            terms.append(ContractTerm(
                term_id=str(uuid.uuid4()),
                term_name="performance_metrics",
                term_value=contract_terms['performance_metrics'],
                is_negotiable=True,
                priority_level="medium",
                legal_implications=["Performance obligations"]
            ))

        return terms

    def _generate_payment_terms(
        self,
        partnership: Partnership,
        contract_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive payment terms"""
        return {
            'payment_schedule': contract_terms.get('payment_schedule', 'monthly'),
            'payment_method': contract_terms.get('payment_method', 'bank_transfer'),
            'payment_currency': contract_terms.get('payment_currency', 'USD'),
            'minimum_payout': str(partnership.minimum_guarantee or Decimal('100')),
            'payment_processing_fee': contract_terms.get('processing_fee', '2.9%'),
            'late_payment_penalty': contract_terms.get('late_payment_penalty', '1.5% per month'),
            'tax_withholding': contract_terms.get('tax_withholding', 'per_jurisdiction'),
            'invoice_requirements': [
                'Monthly revenue statements required',
                'Performance metrics documentation',
                'Tax documentation as required'
            ]
        }

    def _generate_ip_terms(
        self,
        partnership: Partnership,
        contract_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Generate intellectual property terms"""
        return {
            'content_ownership': 'Creator retains full ownership',
            'usage_rights': {
                'partner_usage_scope': contract_terms.get('usage_scope', 'promotional_only'),
                'duration': contract_terms.get('usage_duration', 'contract_duration'),
                'attribution_required': True,
                'modification_rights': contract_terms.get('modification_rights', 'limited')
            },
            'trademark_usage': {
                'partner_brand_usage': 'Approved uses only',
                'creator_brand_protection': 'Full protection maintained',
                'co_branding_terms': contract_terms.get('co_branding', {})
            },
            'confidentiality': {
                'mutual_nda': True,
                'confidential_info_definition': 'Business strategies, financial data, proprietary processes',
                'disclosure_restrictions': 'No disclosure without written consent'
            }
        }

    def _generate_termination_clauses(self, contract_terms: Dict[str, Any]) -> List[str]:
        """
Generate contract termination clauses"""
        return [
            f"Either party may terminate with {contract_terms.get('termination_notice', 30)} days written notice",
            "Immediate termination for material breach if not cured within 10 days",
            "Termination for insolvency, bankruptcy, or assignment for benefit of creditors",
            "Termination for repeated failure to meet performance metrics",
            "Creator maintains right to terminate for brand safety concerns",
            "All outstanding payments due within 30 days of termination",
            "IP usage rights revert to creator upon termination",
            "Confidentiality obligations survive contract termination"
        ]

    async def _generate_contract_document(
        self,
        contract: Contract,
        partnership: Partnership,
        contract_terms: Dict[str, Any]
    ) -> str:
        """Generate formatted contract document"""
        try:
            template = self.template_env.get_template(
                self.contract_templates.get(
                    contract.contract_type,
                    "default_partnership_template.html"
                )
            )

            contract_data = {
                'contract': contract,
                'partnership': partnership,
                'terms': contract_terms,
                'generated_date': datetime.utcnow().strftime('%B %d, %Y'),
                'contract_id': contract.contract_id
            }

            html_content = template.render(**contract_data)
            
            # Convert to PDF and store
            document_url = f"/contracts/{contract.contract_id}.pdf"
            
            # In production, this would generate actual PDF
            self.logger.info(f"Contract document generated: {document_url}")
            return document_url

        except Exception as e:
            self.logger.error(f"Contract document generation failed: {str(e)}")
            raise ContractError(f"Failed to generate document: {str(e)}")

    async def _perform_compliance_checks(self, contract: Contract) -> Dict[str, Any]:
        """Perform legal compliance checks"""
        checks = {
            'warnings': [],
            'errors': []
        }

        # Check for required terms
        required_terms = ['partnership_type', 'commission_rate', 'contract_duration']
        existing_terms = {term.term_name for term in contract.terms_and_conditions}
        
        for required_term in required_terms:
            if required_term not in existing_terms:
                checks['errors'].append(f"Missing required term: {required_term}")

        # Validate payment terms
        if not contract.payment_terms.get('payment_schedule'):
            checks['warnings'].append("Payment schedule not specified")

        # Check jurisdiction compliance
        if contract.governing_law not in ['Delaware', 'New York', 'California']:
            checks['warnings'].append("Non-standard governing law jurisdiction")

        return checks

    async def _validate_business_terms(self, contract: Contract) -> Dict[str, Any]:
        """Validate business logic in contract terms"""
        validation = {
            'warnings': [],
            'errors': []
        }

        # Validate commission rates
        commission_term = next(
            (term for term in contract.terms_and_conditions 
             if term.term_name == 'commission_rate'), None
        )
        
        if commission_term:
            commission_rate = float(commission_term.term_value)
            if commission_rate > 0.5:
                validation['warnings'].append("Commission rate exceeds 50% - unusually high")
            elif commission_rate < 0.05:
                validation['warnings'].append("Commission rate below 5% - unusually low")

        return validation

    async def _assess_contract_risks(self, contract: Contract) -> Dict[str, Any]:
        """Assess legal and business risks in contract"""
        risk_factors = []
        risk_score = 0.0

        # High commission rate risk
        commission_term = next(
            (term for term in contract.terms_and_conditions 
             if term.term_name == 'commission_rate'), None
        )
        
        if commission_term and float(commission_term.term_value) > 0.3:
            risk_factors.append("High commission rate may impact profitability")
            risk_score += 0.2

        # Exclusivity risks
        exclusivity_term = next(
            (term for term in contract.terms_and_conditions 
             if term.term_name == 'exclusivity_clause'), None
        )
        
        if exclusivity_term:
            risk_factors.append("Exclusivity clause limits other opportunities")
            risk_score += 0.3

        # Long-term contract risk
        duration_term = next(
            (term for term in contract.terms_and_conditions 
             if term.term_name == 'contract_duration'), None
        )
        
        if duration_term and int(duration_term.term_value) > 24:
            risk_factors.append("Long-term contract reduces flexibility")
            risk_score += 0.1

        return {
            'risk_factors': risk_factors,
            'overall_risk': min(risk_score, 1.0)
        }

    async def _calculate_compliance_score(self, validation_result: Dict[str, Any]) -> float:
        """Calculate overall compliance score"""
        base_score = 1.0
        
        # Deduct for errors and warnings
        error_penalty = len(validation_result.get('errors', [])) * 0.2
        warning_penalty = len(validation_result.get('warnings', [])) * 0.05
        
        compliance_score = max(0.0, base_score - error_penalty - warning_penalty)
        return compliance_score

    async def _validate_amendment_permissions(self, contract: Contract, amended_by: str) -> bool:
        """
Validate permissions to amend contract"""
        # In production, this would check user permissions
        return True

    async def _requires_legal_review(self, amendments: Dict[str, Any]) -> bool:
        """
Determine if amendments require legal review"""
        high_risk_changes = [
            'commission_rate', 'exclusivity_clause', 'termination_terms',
            'intellectual_property', 'liability_limitations'
        ]
        
        return any(key in amendments for key in high_risk_changes)

    async def _apply_amendments(self, contract: Contract, amendments: Dict[str, Any]):
        """
Apply amendments to contract terms"""
        for amendment_key, amendment_value in amendments.items():
            # Find existing term and update
            existing_term = next(
                (term for term in contract.terms_and_conditions 
                 if term.term_name == amendment_key), None
            )
            
            if existing_term:
                existing_term.term_value = amendment_value
            else:
                # Add new term
                new_term = ContractTerm(
                    term_id=str(uuid.uuid4()),
                    term_name=amendment_key,
                    term_value=amendment_value,
                    is_negotiable=True,
                    priority_level="medium",
                    legal_implications=[f"Amendment: {amendment_key}"]
                )
                contract.terms_and_conditions.append(new_term)

    async def _regenerate_contract_document(self, contract: Contract) -> str:
        """Regenerate contract document after amendments"""
        # Implementation would regenerate PDF with amendments
        return f"/contracts/{contract.contract_id}_v{contract.contract_version}.pdf"

    async def _validate_signature(self, signature: Dict[str, Any]) -> Dict[str, bool]:
        """Validate digital signature"""
        # In production, this would validate actual digital signatures
        required_fields = ['signer_name', 'signature_date', 'ip_address', 'signature_hash']
        
        valid = all(field in signature for field in required_fields)
        return {'valid': valid}

    async def _generate_executed_contract_document(self, contract: Contract) -> str:
        """
Generate final executed contract document"""
        return f"/contracts/{contract.contract_id}_executed.pdf"

    async def _notify_contract_execution(self, contract: Contract):
        """Notify stakeholders of contract execution"""
        # Implementation would send notifications
        self.logger.info(f"Contract execution notifications sent: {contract.contract_id}")

    async def _extract_obligations(self, contract: Contract) -> Dict[str, List[str]]:
        """Extract obligations from contract terms"""
        return {
            'creator_obligations': [
                'Deliver agreed content according to schedule',
                'Maintain brand safety standards',
                'Provide performance reporting'
            ],
            'partner_obligations': [
                'Make payments according to schedule',
                'Provide marketing support as agreed',
                'Respect intellectual property rights'
            ]
        }

    async def _identify_contract_risks(self, contract: Contract) -> List[str]:
        """
Identify potential risks in contract"""
        return [
            'Payment delay risks due to complex approval processes',
            'Performance metric disputes without clear measurement criteria',
            'IP usage scope may be too broad for partner'
        ]
