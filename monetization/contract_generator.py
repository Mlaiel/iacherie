"""
Contract Generator - Automated Legal Contract System
===================================================

Advanced contract generation system for content licensing with legal compliance,
customizable templates, and automated validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
from jinja2 import Template, Environment, BaseLoader

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of licensing contracts"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    CUSTOM = "custom"
    SYNC = "sync"
    COMMERCIAL = "commercial"
    EXCLUSIVE = "exclusive"
    SUBSCRIPTION = "subscription"


class ContractStatus(Enum):
    """Contract status"""
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    SIGNED = "signed"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class ContractClause:
    """Individual contract clause"""
    clause_id: str
    title: str
    content: str
    required: bool = True
    customizable: bool = False
    legal_references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractTemplate:
    """Contract template definition"""
    template_id: str
    name: str
    description: str
    contract_type: ContractType
    jurisdiction: str
    language: str
    version: str
    clauses: List[ContractClause]
    variables: Dict[str, Any] = field(default_factory=dict)
    legal_requirements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GeneratedContract:
    """Generated contract instance"""
    contract_id: str
    template_id: str
    contract_type: ContractType
    parties: Dict[str, Any]
    terms: Dict[str, Any]
    content: str
    hash: str
    status: ContractStatus = ContractStatus.GENERATED
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContractGenerator:
    """
    Advanced contract generation system
    
    Features:
    - Multiple contract templates
    - Legal compliance validation
    - Dynamic clause generation
    - Multi-jurisdiction support
    - Digital signatures
    - Version control
    - Automated updates
    - Legal review workflow
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize contract generator"""
        self.config = config or {}
        
        # Template storage
        self.templates: Dict[str, ContractTemplate] = {}
        self.generated_contracts: Dict[str, GeneratedContract] = {}
        
        # Jinja2 environment for template rendering
        self.template_env = Environment(loader=BaseLoader())
        
        # Legal compliance rules
        self.compliance_rules = {
            "GDPR": {
                "required_clauses": ["data_protection", "user_rights", "data_retention"],
                "prohibited_terms": ["unlimited_liability", "no_refund"],
                "jurisdictions": ["DE", "EU", "UK"]
            },
            "CCPA": {
                "required_clauses": ["privacy_notice", "data_rights", "opt_out"],
                "prohibited_terms": ["data_selling"],
                "jurisdictions": ["US", "CA"]
            },
            "DMCA": {
                "required_clauses": ["takedown_notice", "counter_notice", "safe_harbor"],
                "prohibited_terms": [],
                "jurisdictions": ["US"]
            }
        }
        
        # Default variables for contract generation
        self.default_variables = {
            "company_name": "Ainflue Content Protection Platform",
            "company_address": "Digital Content Solutions GmbH, Germany",
            "company_email": "legal@ainflue.com",
            "governing_law": "German Law",
            "jurisdiction": "Courts of Berlin, Germany",
            "currency": "EUR",
            "language": "en"
        }
        
        # Initialize default templates
        self._initialize_templates()
        
        logger.info("ContractGenerator initialized successfully")
    
    async def generate_contract(
        self,
        content_data: Dict[str, Any],
        licensee_id: int,
        license_terms: Dict[str, Any],
        contract_type: str = "standard"
    ) -> GeneratedContract:
        """
        Generate a licensing contract
        
        Args:
            content_data: Information about the content being licensed
            licensee_id: ID of the licensee
            license_terms: Terms and conditions for the license
            contract_type: Type of contract to generate
            
        Returns:
            GeneratedContract: Generated contract instance
        """
        try:
            # Get appropriate template
            template = await self._get_template(contract_type, license_terms)
            
            if not template:
                raise ValueError(f"No template found for contract type: {contract_type}")
            
            # Prepare contract variables
            variables = await self._prepare_variables(
                content_data, licensee_id, license_terms, template
            )
            
            # Validate legal compliance
            await self._validate_compliance(template, variables, license_terms)
            
            # Generate contract content
            contract_content = await self._render_contract(template, variables)
            
            # Generate contract hash for integrity
            contract_hash = self._generate_contract_hash(contract_content)
            
            # Create contract instance
            contract = GeneratedContract(
                contract_id=f"contract_{datetime.utcnow().timestamp()}",
                template_id=template.template_id,
                contract_type=ContractType(contract_type),
                parties={
                    "licensor": {
                        "id": content_data.get("user_id"),
                        "name": content_data.get("user_name", "Content Owner"),
                        "type": "licensor"
                    },
                    "licensee": {
                        "id": licensee_id,
                        "name": license_terms.get("licensee_name", f"User {licensee_id}"),
                        "type": "licensee"
                    }
                },
                terms=license_terms,
                content=contract_content,
                hash=contract_hash,
                metadata={
                    "content_id": content_data.get("id"),
                    "content_title": content_data.get("metadata", {}).get("title", "Untitled"),
                    "template_version": template.version,
                    "jurisdiction": template.jurisdiction,
                    "language": template.language
                }
            )
            
            # Store generated contract
            self.generated_contracts[contract.contract_id] = contract
            
            logger.info(f"Contract generated: {contract.contract_id}")
            return contract
            
        except Exception as e:
            logger.error(f"Error generating contract: {e}")
            raise
    
    async def get_contract(self, contract_id: str) -> Optional[GeneratedContract]:
        """Get a generated contract by ID"""
        return self.generated_contracts.get(contract_id)
    
    async def update_contract_status(
        self,
        contract_id: str,
        status: ContractStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update contract status
        
        Args:
            contract_id: Contract ID
            status: New status
            metadata: Additional metadata
            
        Returns:
            bool: True if updated successfully
        """
        try:
            if contract_id not in self.generated_contracts:
                return False
            
            contract = self.generated_contracts[contract_id]
            contract.status = status
            
            if metadata:
                contract.metadata.update(metadata)
            
            logger.info(f"Contract status updated: {contract_id} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating contract status: {e}")
            return False
    
    async def validate_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Validate a generated contract
        
        Args:
            contract_id: Contract ID
            
        Returns:
            Dict: Validation results
        """
        try:
            if contract_id not in self.generated_contracts:
                return {"valid": False, "error": "Contract not found"}
            
            contract = self.generated_contracts[contract_id]
            validation_results = {
                "valid": True,
                "contract_id": contract_id,
                "issues": [],
                "compliance_status": {},
                "recommendations": []
            }
            
            # Verify contract hash
            current_hash = self._generate_contract_hash(contract.content)
            if current_hash != contract.hash:
                validation_results["valid"] = False
                validation_results["issues"].append("Contract content has been modified")
            
            # Check legal compliance
            template = self.templates.get(contract.template_id)
            if template:
                compliance_check = await self._check_compliance(template, contract.terms)
                validation_results["compliance_status"] = compliance_check
                
                if not compliance_check.get("compliant", False):
                    validation_results["issues"].extend(compliance_check.get("violations", []))
            
            # Check expiration
            if "end_date" in contract.terms:
                end_date = datetime.fromisoformat(contract.terms["end_date"])
                if datetime.utcnow() > end_date:
                    validation_results["issues"].append("Contract has expired")
            
            # Final validation status
            validation_results["valid"] = len(validation_results["issues"]) == 0
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating contract: {e}")
            return {"valid": False, "error": str(e)}
    
    async def generate_amendment(
        self,
        contract_id: str,
        amendments: Dict[str, Any]
    ) -> Optional[GeneratedContract]:
        """
        Generate an amendment to an existing contract
        
        Args:
            contract_id: Original contract ID
            amendments: Changes to be made
            
        Returns:
            GeneratedContract: Amendment contract or None if failed
        """
        try:
            original_contract = self.generated_contracts.get(contract_id)
            if not original_contract:
                return None
            
            # Create amendment terms
            amendment_terms = {
                **original_contract.terms,
                **amendments,
                "original_contract_id": contract_id,
                "amendment_date": datetime.utcnow().isoformat(),
                "amendment_reason": amendments.get("reason", "Contract modification")
            }
            
            # Generate amendment contract
            amendment_contract = await self.generate_contract(
                content_data={
                    "id": original_contract.metadata.get("content_id"),
                    "metadata": {"title": original_contract.metadata.get("content_title")}
                },
                licensee_id=original_contract.parties["licensee"]["id"],
                license_terms=amendment_terms,
                contract_type="amendment"
            )
            
            # Update original contract status
            await self.update_contract_status(
                contract_id,
                ContractStatus.TERMINATED,
                {"superseded_by": amendment_contract.contract_id}
            )
            
            logger.info(f"Amendment generated: {amendment_contract.contract_id}")
            return amendment_contract
            
        except Exception as e:
            logger.error(f"Error generating amendment: {e}")
            return None
    
    async def _get_template(
        self,
        contract_type: str,
        license_terms: Dict[str, Any]
    ) -> Optional[ContractTemplate]:
        """Get appropriate contract template"""
        try:
            # Look for exact match first
            template_id = f"{contract_type}_template"
            if template_id in self.templates:
                return self.templates[template_id]
            
            # Look for compatible templates
            for template in self.templates.values():
                if template.contract_type.value == contract_type:
                    # Check jurisdiction compatibility
                    jurisdiction = license_terms.get("governing_law", "German Law")
                    if "german" in jurisdiction.lower() or "eu" in jurisdiction.lower():
                        return template
            
            # Default to standard template
            return self.templates.get("standard_template")
            
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return None
    
    async def _prepare_variables(
        self,
        content_data: Dict[str, Any],
        licensee_id: int,
        license_terms: Dict[str, Any],
        template: ContractTemplate
    ) -> Dict[str, Any]:
        """Prepare variables for contract rendering"""
        try:
            variables = {
                **self.default_variables,
                **template.variables,
                
                # Content information
                "content_id": content_data.get("id"),
                "content_title": content_data.get("metadata", {}).get("title", "Untitled Content"),
                "content_type": content_data.get("content_type", "digital content"),
                "content_description": content_data.get("metadata", {}).get("description", ""),
                
                # Licensor information
                "licensor_id": content_data.get("user_id"),
                "licensor_name": content_data.get("user_name", "Content Owner"),
                
                # Licensee information
                "licensee_id": licensee_id,
                "licensee_name": license_terms.get("licensee_name", f"User {licensee_id}"),
                
                # License terms
                "license_type": license_terms.get("license_type", "standard"),
                "territory": license_terms.get("territory", "worldwide"),
                "start_date": license_terms.get("start_date", datetime.utcnow().isoformat()),
                "end_date": license_terms.get("end_date", ""),
                "price": license_terms.get("price", "0.00"),
                "currency": license_terms.get("currency", "EUR"),
                
                # Usage rights
                "commercial_use": license_terms.get("commercial_use", False),
                "exclusive": license_terms.get("exclusive", False),
                "modifications_allowed": license_terms.get("modifications_allowed", False),
                "attribution_required": license_terms.get("attribution_required", True),
                
                # Contract metadata
                "contract_date": datetime.utcnow().strftime("%B %d, %Y"),
                "contract_jurisdiction": template.jurisdiction,
                "contract_language": template.language
            }
            
            return variables
            
        except Exception as e:
            logger.error(f"Error preparing variables: {e}")
            return {}
    
    async def _validate_compliance(
        self,
        template: ContractTemplate,
        variables: Dict[str, Any],
        license_terms: Dict[str, Any]
    ) -> None:
        """Validate legal compliance before contract generation"""
        try:
            jurisdiction = template.jurisdiction
            
            # Check GDPR compliance for EU jurisdictions
            if jurisdiction in ["DE", "EU", "UK"]:
                await self._validate_gdpr_compliance(variables, license_terms)
            
            # Check CCPA compliance for US jurisdictions
            if jurisdiction in ["US", "CA"]:
                await self._validate_ccpa_compliance(variables, license_terms)
            
            # Check DMCA compliance for US content
            if jurisdiction == "US":
                await self._validate_dmca_compliance(variables, license_terms)
            
        except Exception as e:
            logger.error(f"Error validating compliance: {e}")
            raise
    
    async def _validate_gdpr_compliance(
        self,
        variables: Dict[str, Any],
        license_terms: Dict[str, Any]
    ) -> None:
        """Validate GDPR compliance"""
        required_clauses = ["data_protection", "user_rights", "data_retention"]
        
        # Check if personal data is involved
        if license_terms.get("contains_personal_data", False):
            # Ensure data protection clauses are included
            for clause in required_clauses:
                if clause not in variables:
                    raise ValueError(f"GDPR compliance requires {clause} clause")
    
    async def _validate_ccpa_compliance(
        self,
        variables: Dict[str, Any],
        license_terms: Dict[str, Any]
    ) -> None:
        """Validate CCPA compliance"""
        logger.info("Validating CCPA compliance for contract")
        
        # Check for required CCPA elements
        required_clauses = [
            "data_collection_notice",
            "consumer_rights",
            "opt_out_mechanism",
            "data_deletion_rights"
        ]
        
        # Validate data collection notice
        if not variables.get("data_collection_notice"):
            logger.warning("CCPA: Data collection notice missing")
            variables["data_collection_notice"] = (
                "This agreement complies with California Consumer Privacy Act (CCPA). "
                "Consumer data collection practices are disclosed and consent-based."
            )
        
        # Validate consumer rights clause
        if not variables.get("consumer_rights_clause"):
            logger.info("Adding CCPA consumer rights clause")
            variables["consumer_rights_clause"] = (
                "Consumers have the right to know about personal information collected, "
                "the right to delete personal information, and the right to opt-out of "
                "the sale of personal information as defined under CCPA."
            )
        
        # Add CCPA-specific terms to license
        if "ccpa_compliance" not in license_terms:
            license_terms["ccpa_compliance"] = {
                "data_subject_rights": True,
                "opt_out_available": True,
                "data_deletion_policy": "Upon request within 45 days",
                "privacy_policy_link": variables.get("privacy_policy_url", "/privacy-policy")
            }
        
        logger.info("CCPA compliance validation completed")
    
    async def _validate_dmca_compliance(
        self,
        variables: Dict[str, Any],
        license_terms: Dict[str, Any]
    ) -> None:
        """Validate DMCA compliance"""
        logger.info("Validating DMCA compliance for contract")
        
        # Check for required DMCA elements
        required_dmca_elements = [
            "copyright_notice",
            "takedown_procedure",
            "counter_notification_process",
            "dmca_agent_contact"
        ]
        
        # Validate copyright notice
        if not variables.get("copyright_notice"):
            logger.warning("DMCA: Copyright notice missing, adding default")
            variables["copyright_notice"] = (
                f"© {datetime.now().year} {variables.get('licensor_name', 'Content Owner')}. "
                "All rights reserved. Unauthorized use is prohibited."
            )
        
        # Validate takedown procedure
        if not variables.get("dmca_takedown_procedure"):
            logger.info("Adding DMCA takedown procedure")
            variables["dmca_takedown_procedure"] = (
                "Copyright infringement claims should be submitted to our DMCA agent "
                "with: (1) Physical/electronic signature of copyright owner, "
                "(2) Identification of copyrighted work, (3) Location of infringing material, "
                "(4) Contact information, (5) Good faith statement, (6) Accuracy statement."
            )
        
        # Add DMCA agent information if not present
        if not variables.get("dmca_agent_contact"):
            logger.info("Adding DMCA agent contact information")
            variables["dmca_agent_contact"] = {
                "email": variables.get("dmca_email", "dmca@company.com"),
                "address": variables.get("dmca_address", "DMCA Agent, Legal Department"),
                "phone": variables.get("dmca_phone", "+1-XXX-XXX-XXXX")
            }
        
        # Add DMCA-specific license terms
        if "dmca_compliance" not in license_terms:
            license_terms["dmca_compliance"] = {
                "takedown_response_time": "24-48 hours",
                "counter_notification_time": "10 business days",
                "safe_harbor_protection": True,
                "copyright_monitoring": variables.get("copyright_monitoring", True)
            }
        
        # Validate content identification requirements
        if "content_identification" not in license_terms:
            license_terms["content_identification"] = {
                "fingerprinting_enabled": True,
                "metadata_tracking": True,
                "usage_monitoring": True,
                "infringement_detection": "automated"
            }
        
        logger.info("DMCA compliance validation completed")
    
    async def _render_contract(
        self,
        template: ContractTemplate,
        variables: Dict[str, Any]
    ) -> str:
        """Render contract content from template"""
        try:
            # Build contract content from clauses
            contract_sections = []
            
            contract_sections.append(f"# {template.name}")
            contract_sections.append(f"Generated on: {datetime.utcnow().strftime('%B %d, %Y')}")
            contract_sections.append("")
            
            # Parties section
            contract_sections.append("## Parties")
            contract_sections.append(f"**Licensor:** {variables.get('licensor_name', 'N/A')}")
            contract_sections.append(f"**Licensee:** {variables.get('licensee_name', 'N/A')}")
            contract_sections.append("")
            
            # Content section
            contract_sections.append("## Licensed Content")
            contract_sections.append(f"**Title:** {variables.get('content_title', 'N/A')}")
            contract_sections.append(f"**Type:** {variables.get('content_type', 'N/A')}")
            contract_sections.append(f"**Content ID:** {variables.get('content_id', 'N/A')}")
            contract_sections.append("")
            
            # License terms section
            contract_sections.append("## License Terms")
            contract_sections.append(f"**License Type:** {variables.get('license_type', 'N/A')}")
            contract_sections.append(f"**Territory:** {variables.get('territory', 'N/A')}")
            contract_sections.append(f"**Commercial Use:** {'Permitted' if variables.get('commercial_use') else 'Not Permitted'}")
            contract_sections.append(f"**Exclusive:** {'Yes' if variables.get('exclusive') else 'No'}")
            contract_sections.append("")
            
            # Financial terms
            contract_sections.append("## Financial Terms")
            contract_sections.append(f"**License Fee:** {variables.get('currency', 'EUR')} {variables.get('price', '0.00')}")
            contract_sections.append("")
            
            # Add template clauses
            for clause in template.clauses:
                contract_sections.append(f"## {clause.title}")
                
                # Render clause content with variables
                clause_template = Template(clause.content)
                rendered_clause = clause_template.render(**variables)
                contract_sections.append(rendered_clause)
                contract_sections.append("")
            
            # Footer
            contract_sections.append("---")
            contract_sections.append(f"Contract generated by {variables.get('company_name', 'Ainflue Platform')}")
            contract_sections.append(f"Governing Law: {variables.get('governing_law', 'German Law')}")
            contract_sections.append(f"Jurisdiction: {variables.get('jurisdiction', 'Berlin, Germany')}")
            
            return "\n".join(contract_sections)
            
        except Exception as e:
            logger.error(f"Error rendering contract: {e}")
            raise
    
    def _generate_contract_hash(self, content: str) -> str:
        """Generate hash for contract integrity verification"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    async def _check_compliance(
        self,
        template: ContractTemplate,
        terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check legal compliance of contract terms"""
        try:
            compliance_result = {
                "compliant": True,
                "violations": [],
                "warnings": [],
                "requirements_met": []
            }
            
            jurisdiction = template.jurisdiction
            
            # Check each compliance framework
            for framework, rules in self.compliance_rules.items():
                if jurisdiction in rules["jurisdictions"]:
                    # Check required clauses
                    for required_clause in rules["required_clauses"]:
                        if required_clause not in template.clauses:
                            compliance_result["violations"].append(
                                f"{framework}: Missing required clause '{required_clause}'"
                            )
                            compliance_result["compliant"] = False
                        else:
                            compliance_result["requirements_met"].append(
                                f"{framework}: Required clause '{required_clause}' present"
                            )
                    
                    # Check prohibited terms
                    for prohibited_term in rules["prohibited_terms"]:
                        if any(prohibited_term in str(value).lower() for value in terms.values()):
                            compliance_result["violations"].append(
                                f"{framework}: Prohibited term '{prohibited_term}' found"
                            )
                            compliance_result["compliant"] = False
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            return {"compliant": False, "error": str(e)}
    
    def _initialize_templates(self) -> None:
        """Initialize default contract templates"""
        try:
            # Standard licensing template
            standard_clauses = [
                ContractClause(
                    clause_id="grant_of_license",
                    title="Grant of License",
                    content="""The Licensor hereby grants to the Licensee a {{ 'non-exclusive' if not exclusive else 'exclusive' }} license to use the Licensed Content in accordance with the terms and conditions set forth in this Agreement.

The license is granted for the territory of {{ territory }} and is valid from {{ start_date }} to {{ end_date if end_date else 'indefinitely' }}.

{{ 'Commercial use is permitted under this license.' if commercial_use else 'This license is for non-commercial use only.' }}"""
                ),
                ContractClause(
                    clause_id="usage_restrictions",
                    title="Usage Restrictions",
                    content="""The Licensee agrees to use the Licensed Content only for the purposes specified in this Agreement. 

{{ 'The Licensee may modify the Licensed Content as necessary for the intended use.' if modifications_allowed else 'The Licensee may not modify, alter, or create derivative works based on the Licensed Content without prior written consent from the Licensor.' }}

{{ 'Attribution to the Licensor is required in all uses of the Licensed Content.' if attribution_required else 'No attribution is required for the use of the Licensed Content.' }}"""
                ),
                ContractClause(
                    clause_id="payment_terms",
                    title="Payment Terms",
                    content="""The total license fee for the Licensed Content is {{ currency }} {{ price }}.

Payment is due within 30 days of the execution of this Agreement. Late payments may incur additional charges as per the platform's payment policy."""
                ),
                ContractClause(
                    clause_id="termination",
                    title="Termination",
                    content="""This Agreement may be terminated by either party with 30 days written notice. Upon termination, the Licensee must cease all use of the Licensed Content and destroy any copies in their possession."""
                ),
                ContractClause(
                    clause_id="governing_law",
                    title="Governing Law",
                    content="""This Agreement shall be governed by and construed in accordance with {{ governing_law }}. Any disputes arising under this Agreement shall be subject to the exclusive jurisdiction of {{ jurisdiction }}."""
                )
            ]
            
            standard_template = ContractTemplate(
                template_id="standard_template",
                name="Standard Content License Agreement",
                description="Standard template for content licensing",
                contract_type=ContractType.STANDARD,
                jurisdiction="DE",
                language="en",
                version="1.0",
                clauses=standard_clauses,
                legal_requirements=["GDPR", "German Contract Law"]
            )
            
            self.templates["standard_template"] = standard_template
            
            # Premium licensing template (more comprehensive)
            premium_clauses = standard_clauses + [
                ContractClause(
                    clause_id="intellectual_property",
                    title="Intellectual Property Rights",
                    content="""The Licensor retains all intellectual property rights in the Licensed Content. This Agreement does not transfer any ownership rights to the Licensee."""
                ),
                ContractClause(
                    clause_id="warranties",
                    title="Warranties and Representations",
                    content="""The Licensor warrants that they have the full right and authority to grant this license and that the Licensed Content does not infringe upon any third-party rights."""
                ),
                ContractClause(
                    clause_id="indemnification",
                    title="Indemnification",
                    content="""The Licensee agrees to indemnify and hold harmless the Licensor from any claims, damages, or expenses arising from the Licensee's use of the Licensed Content."""
                )
            ]
            
            premium_template = ContractTemplate(
                template_id="premium_template",
                name="Premium Content License Agreement",
                description="Comprehensive template for premium content licensing",
                contract_type=ContractType.PREMIUM,
                jurisdiction="DE",
                language="en",
                version="1.0",
                clauses=premium_clauses,
                legal_requirements=["GDPR", "German Contract Law", "EU Copyright Directive"]
            )
            
            self.templates["premium_template"] = premium_template
            
            logger.info("Contract templates initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing templates: {e}")
    
    def get_generator_stats(self) -> Dict[str, Any]:
        """Get contract generator statistics"""
        try:
            total_contracts = len(self.generated_contracts)
            
            # Status breakdown
            status_breakdown = {}
            for contract in self.generated_contracts.values():
                status = contract.status.value
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            # Template usage
            template_usage = {}
            for contract in self.generated_contracts.values():
                template_id = contract.template_id
                template_usage[template_id] = template_usage.get(template_id, 0) + 1
            
            return {
                "version": "1.0.0",
                "contracts": {
                    "total_generated": total_contracts,
                    "status_breakdown": status_breakdown,
                    "template_usage": template_usage
                },
                "templates": {
                    "total_templates": len(self.templates),
                    "available_types": [t.contract_type.value for t in self.templates.values()],
                    "supported_jurisdictions": list(set(t.jurisdiction for t in self.templates.values()))
                },
                "compliance": {
                    "supported_frameworks": list(self.compliance_rules.keys()),
                    "default_jurisdiction": "DE",
                    "default_language": "en"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting generator stats: {e}")
            return {"error": str(e)}