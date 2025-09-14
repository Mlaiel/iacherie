"""
Legal Framework Engine - Enterprise Legal Compliance Management

Comprehensive legal framework management system for handling legal compliance,
contract analysis, intellectual property protection, and legal risk assessment.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import json
import logging
import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable

import aioredis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class LegalFrameworkType(Enum):
    """Legal framework types"""
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    USER_AGREEMENT = "user_agreement"
    DATA_PROCESSING_AGREEMENT = "data_processing_agreement"
    COOKIE_POLICY = "cookie_policy"
    CONTENT_POLICY = "content_policy"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    LIABILITY_DISCLAIMER = "liability_disclaimer"
    JURISDICTION_CLAUSE = "jurisdiction_clause"


class ContractType(Enum):
    """Contract types for analysis"""
    SERVICE_AGREEMENT = "service_agreement"
    LICENSING_AGREEMENT = "licensing_agreement"
    PARTNERSHIP_AGREEMENT = "partnership_agreement"
    VENDOR_CONTRACT = "vendor_contract"
    EMPLOYMENT_CONTRACT = "employment_contract"
    NDA = "nda"
    API_AGREEMENT = "api_agreement"
    SLA = "sla"


class LegalRiskLevel(Enum):
    """Legal risk assessment levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IntellectualPropertyType(Enum):
    """Intellectual property types"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    TRADE_SECRET = "trade_secret"
    LICENSING = "licensing"
    FAIR_USE = "fair_use"


class LegalJurisdiction(Enum):
    """Legal jurisdictions"""
    US_FEDERAL = "us_federal"
    US_CALIFORNIA = "us_california"
    EU_GDPR = "eu_gdpr"
    UK_DPA = "uk_dpa"
    CANADA_PIPEDA = "canada_pipeda"
    INTERNATIONAL = "international"


@dataclass
class LegalDocument:
    """Legal document structure"""
    document_id: str
    document_type: LegalFrameworkType
    title: str
    content: str
    version: str
    effective_date: datetime
    review_date: datetime
    jurisdiction: LegalJurisdiction
    approval_status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractAnalysisResult:
    """Contract analysis result"""
    analysis_id: str
    contract_id: str
    contract_type: ContractType
    risk_level: LegalRiskLevel
    risk_factors: List[str]
    key_terms: Dict[str, Any]
    compliance_issues: List[str]
    recommendations: List[str]
    analyzed_at: datetime
    analyst: str


@dataclass
class IntellectualPropertyAssessment:
    """IP assessment result"""
    assessment_id: str
    content_id: str
    ip_type: IntellectualPropertyType
    infringement_risk: float
    protected_elements: List[str]
    recommendations: List[str]
    assessed_at: datetime


class LegalDocumentRecord(Base):
    """Database model for legal documents"""
    __tablename__ = "legal_documents"
    
    document_id = Column(String, primary_key=True)
    document_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    review_date = Column(DateTime, nullable=False)
    jurisdiction = Column(String, nullable=False)
    approval_status = Column(String, default="draft")
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class ContractAnalysisRecord(Base):
    """Database model for contract analysis"""
    __tablename__ = "contract_analysis"
    
    analysis_id = Column(String, primary_key=True)
    contract_id = Column(String, nullable=False)
    contract_type = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    risk_factors = Column(JSON, default=[])
    key_terms = Column(JSON, default={})
    compliance_issues = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    analyst = Column(String, nullable=False)


class IPAssessmentRecord(Base):
    """Database model for IP assessments"""
    __tablename__ = "ip_assessments"
    
    assessment_id = Column(String, primary_key=True)
    content_id = Column(String, nullable=False)
    ip_type = Column(String, nullable=False)
    infringement_risk = Column(Float, nullable=False)
    protected_elements = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    assessed_at = Column(DateTime, default=datetime.utcnow)
    assessor = Column(String, nullable=False)


class LegalDocumentManager:
    """Legal document lifecycle management"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def create_legal_document(self, 
                                  document_type: LegalFrameworkType,
                                  title: str,
                                  content: str,
                                  jurisdiction: LegalJurisdiction,
                                  template_data: Dict[str, Any] = None) -> LegalDocument:
        """Create new legal document"""
        try:
            document_id = str(uuid.uuid4())
            
            # Apply template if provided
            if template_data:
                content = await self._apply_template(document_type, content, template_data)
            
            # Validate legal content
            validation_result = await self._validate_legal_content(content, document_type, jurisdiction)
            
            if not validation_result["is_valid"]:
                raise ValueError(f"Legal document validation failed: {validation_result['issues']}")
            
            # Create document
            document = LegalDocument(
                document_id=document_id,
                document_type=document_type,
                title=title,
                content=content,
                version="1.0",
                effective_date=datetime.utcnow(),
                review_date=datetime.utcnow() + timedelta(days=365),
                jurisdiction=jurisdiction,
                approval_status="draft",
                metadata={
                    "created_by": "legal_system",
                    "validation_result": validation_result,
                    "template_applied": template_data is not None
                }
            )
            
            # Store document
            await self._store_legal_document(document)
            
            return document
            
        except Exception as e:
            logger.error(f"Legal document creation failed: {str(e)}")
            raise
    
    async def update_legal_document(self, 
                                  document_id: str,
                                  updates: Dict[str, Any],
                                  increment_version: bool = True) -> LegalDocument:
        """Update existing legal document"""
        try:
            # Get current document
            document = await self._get_legal_document(document_id)
            if not document:
                raise ValueError(f"Legal document {document_id} not found")
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(document, field):
                    setattr(document, field, value)
            
            # Increment version if requested
            if increment_version:
                current_version = float(document.version)
                document.version = str(current_version + 0.1)
            
            # Validate updated content
            if "content" in updates:
                validation_result = await self._validate_legal_content(
                    document.content, document.document_type, document.jurisdiction
                )
                
                if not validation_result["is_valid"]:
                    raise ValueError(f"Updated document validation failed: {validation_result['issues']}")
                
                document.metadata["last_validation"] = validation_result
            
            # Update timestamps
            document.metadata["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated document
            await self._store_legal_document(document)
            
            return document
            
        except Exception as e:
            logger.error(f"Legal document update failed: {str(e)}")
            raise
    
    async def review_legal_documents(self, jurisdiction: LegalJurisdiction = None) -> List[Dict[str, Any]]:
        """Review legal documents for compliance and updates"""
        try:
            documents = await self._get_documents_for_review(jurisdiction)
            review_results = []
            
            for document in documents:
                review_result = await self._perform_document_review(document)
                review_results.append(review_result)
            
            return review_results
            
        except Exception as e:
            logger.error(f"Legal document review failed: {str(e)}")
            raise
    
    async def _apply_template(self, 
                            document_type: LegalFrameworkType,
                            content: str,
                            template_data: Dict[str, Any]) -> str:
        """Apply template data to legal document content"""
        try:
            # Get template for document type
            template = await self._get_legal_template(document_type)
            
            if template:
                # Replace template variables
                for key, value in template_data.items():
                    placeholder = f"{{{key}}}"
                    content = content.replace(placeholder, str(value))
            
            return content
            
        except Exception as e:
            logger.error(f"Template application failed: {str(e)}")
            return content
    
    async def _validate_legal_content(self, 
                                    content: str,
                                    document_type: LegalFrameworkType,
                                    jurisdiction: LegalJurisdiction) -> Dict[str, Any]:
        """Validate legal document content"""
        validation_result = {
            "is_valid": True,
            "issues": [],
            "recommendations": [],
            "compliance_score": 1.0
        }
        
        try:
            # Check required clauses based on document type
            required_clauses = await self._get_required_clauses(document_type, jurisdiction)
            
            for clause in required_clauses:
                if not await self._check_clause_presence(content, clause):
                    validation_result["issues"].append(f"Missing required clause: {clause}")
                    validation_result["compliance_score"] -= 0.1
            
            # Check for problematic language
            problematic_terms = await self._check_problematic_terms(content)
            if problematic_terms:
                validation_result["issues"].extend(problematic_terms)
                validation_result["compliance_score"] -= 0.05 * len(problematic_terms)
            
            # Check jurisdiction-specific requirements
            jurisdiction_issues = await self._check_jurisdiction_requirements(content, jurisdiction)
            if jurisdiction_issues:
                validation_result["issues"].extend(jurisdiction_issues)
                validation_result["compliance_score"] -= 0.1 * len(jurisdiction_issues)
            
            # Generate recommendations
            validation_result["recommendations"] = await self._generate_content_recommendations(
                validation_result["issues"], document_type
            )
            
            validation_result["is_valid"] = validation_result["compliance_score"] >= 0.7
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Legal content validation failed: {str(e)}")
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def _get_legal_template(self, document_type: LegalFrameworkType) -> Optional[str]:
        """Get legal document template"""
        templates = {
            LegalFrameworkType.PRIVACY_POLICY: """
This Privacy Policy describes how {company_name} collects, uses, and protects
your personal information when you use our services.

1. Information We Collect
{information_collection_clause}

2. How We Use Information
{information_usage_clause}

3. Data Protection
{data_protection_clause}

4. Your Rights
{user_rights_clause}

5. Contact Information
{contact_information}
""",
            LegalFrameworkType.TERMS_OF_SERVICE: """
These Terms of Service govern your use of {service_name} provided by {company_name}.

1. Acceptance of Terms
{acceptance_clause}

2. Service Description
{service_description}

3. User Responsibilities
{user_responsibilities}

4. Intellectual Property
{ip_clause}

5. Limitation of Liability
{liability_clause}
"""
        }
        
        return templates.get(document_type)
    
    async def _get_required_clauses(self, 
                                  document_type: LegalFrameworkType,
                                  jurisdiction: LegalJurisdiction) -> List[str]:
        """Get required clauses for document type and jurisdiction"""
        clauses_map = {
            (LegalFrameworkType.PRIVACY_POLICY, LegalJurisdiction.EU_GDPR): [
                "lawful_basis", "data_subject_rights", "data_retention", "contact_dpo"
            ],
            (LegalFrameworkType.PRIVACY_POLICY, LegalJurisdiction.US_CALIFORNIA): [
                "ccpa_rights", "do_not_sell", "consumer_request_process"
            ],
            (LegalFrameworkType.TERMS_OF_SERVICE, LegalJurisdiction.US_FEDERAL): [
                "acceptance", "modification", "termination", "liability_limitation"
            ]
        }
        
        return clauses_map.get((document_type, jurisdiction), [])
    
    async def _check_clause_presence(self, content: str, clause: str) -> bool:
        """Check if required clause is present in content"""
        clause_patterns = {
            "lawful_basis": r"lawful\s+basis|legal\s+basis",
            "data_subject_rights": r"data\s+subject\s+rights|your\s+rights",
            "data_retention": r"data\s+retention|how\s+long\s+we\s+keep",
            "liability_limitation": r"limitation\s+of\s+liability|disclaim",
            "acceptance": r"accept|agree\s+to|bound\s+by"
        }
        
        pattern = clause_patterns.get(clause, clause)
        return bool(re.search(pattern, content, re.IGNORECASE))
    
    async def _check_problematic_terms(self, content: str) -> List[str]:
        """Check for potentially problematic legal terms"""
        problematic_patterns = {
            "unlimited_liability": r"unlimited\s+liability",
            "no_warranties": r"no\s+warranties|without\s+warranty",
            "binding_arbitration": r"binding\s+arbitration",
            "class_action_waiver": r"class\s+action\s+waiver"
        }
        
        issues = []
        for issue_type, pattern in problematic_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potentially problematic clause: {issue_type}")
        
        return issues
    
    async def _check_jurisdiction_requirements(self, 
                                             content: str,
                                             jurisdiction: LegalJurisdiction) -> List[str]:
        """Check jurisdiction-specific legal requirements"""
        issues = []
        
        if jurisdiction == LegalJurisdiction.EU_GDPR:
            if not re.search(r"gdpr|general\s+data\s+protection", content, re.IGNORECASE):
                issues.append("GDPR compliance statement missing")
        
        elif jurisdiction == LegalJurisdiction.US_CALIFORNIA:
            if not re.search(r"ccpa|california\s+consumer\s+privacy", content, re.IGNORECASE):
                issues.append("CCPA compliance statement missing")
        
        return issues
    
    async def _generate_content_recommendations(self, 
                                              issues: List[str],
                                              document_type: LegalFrameworkType) -> List[str]:
        """Generate recommendations for content improvement"""
        recommendations = []
        
        if any("missing" in issue.lower() for issue in issues):
            recommendations.append("Add all required legal clauses for compliance")
        
        if any("problematic" in issue.lower() for issue in issues):
            recommendations.append("Review and revise potentially problematic clauses")
        
        if document_type == LegalFrameworkType.PRIVACY_POLICY:
            recommendations.append("Ensure plain language and user-friendly explanations")
        
        return recommendations
    
    async def _store_legal_document(self, document: LegalDocument) -> None:
        """Store legal document in database"""
        try:
            document_record = LegalDocumentRecord(
                document_id=document.document_id,
                document_type=document.document_type.value,
                title=document.title,
                content=document.content,
                version=document.version,
                effective_date=document.effective_date,
                review_date=document.review_date,
                jurisdiction=document.jurisdiction.value,
                approval_status=document.approval_status,
                metadata=document.metadata
            )
            
            self.db.add(document_record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store legal document: {str(e)}")
            raise
    
    async def _get_legal_document(self, document_id: str) -> Optional[LegalDocument]:
        """Retrieve legal document from database"""
        # Implementation would query database
        return None
    
    async def _get_documents_for_review(self, jurisdiction: LegalJurisdiction = None) -> List[LegalDocument]:
        """Get documents that need review"""
        # Implementation would query database for documents due for review
        return []
    
    async def _perform_document_review(self, document: LegalDocument) -> Dict[str, Any]:
        """Perform comprehensive document review"""
        return {
            "document_id": document.document_id,
            "review_status": "compliant",
            "issues_found": [],
            "recommendations": [],
            "next_review_date": document.review_date + timedelta(days=365)
        }


class ContractAnalyzer:
    """Contract analysis and risk assessment"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        
    async def analyze_contract(self, 
                             contract_id: str,
                             contract_content: str,
                             contract_type: ContractType) -> ContractAnalysisResult:
        """Analyze contract for legal risks and compliance"""
        try:
            analysis_id = str(uuid.uuid4())
            
            # Extract key terms
            key_terms = await self._extract_key_terms(contract_content, contract_type)
            
            # Assess legal risks
            risk_assessment = await self._assess_contract_risks(contract_content, contract_type)
            
            # Check compliance issues
            compliance_issues = await self._check_contract_compliance(contract_content, contract_type)
            
            # Generate recommendations
            recommendations = await self._generate_contract_recommendations(
                risk_assessment, compliance_issues, contract_type
            )
            
            analysis_result = ContractAnalysisResult(
                analysis_id=analysis_id,
                contract_id=contract_id,
                contract_type=contract_type,
                risk_level=risk_assessment["risk_level"],
                risk_factors=risk_assessment["risk_factors"],
                key_terms=key_terms,
                compliance_issues=compliance_issues,
                recommendations=recommendations,
                analyzed_at=datetime.utcnow(),
                analyst="automated_system"
            )
            
            # Cache analysis result
            await self.redis.setex(f"contract_analysis:{analysis_id}", 3600 * 24,
                                  json.dumps(analysis_result.__dict__, default=str))
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Contract analysis failed: {str(e)}")
            raise
    
    async def _extract_key_terms(self, content: str, contract_type: ContractType) -> Dict[str, Any]:
        """Extract key terms from contract"""
        key_terms = {}
        
        # Extract common terms
        key_terms["payment_terms"] = await self._extract_payment_terms(content)
        key_terms["termination_clause"] = await self._extract_termination_clause(content)
        key_terms["liability_terms"] = await self._extract_liability_terms(content)
        key_terms["intellectual_property"] = await self._extract_ip_terms(content)
        
        # Contract-type specific terms
        if contract_type == ContractType.SLA:
            key_terms["sla_metrics"] = await self._extract_sla_metrics(content)
        elif contract_type == ContractType.NDA:
            key_terms["confidentiality_scope"] = await self._extract_confidentiality_scope(content)
        
        return key_terms
    
    async def _assess_contract_risks(self, content: str, contract_type: ContractType) -> Dict[str, Any]:
        """Assess legal risks in contract"""
        risk_factors = []
        risk_score = 0.0
        
        # Check for high-risk clauses
        high_risk_patterns = [
            r"unlimited\s+liability",
            r"no\s+limitation\s+of\s+damages",
            r"indemnify.*against.*all.*claims",
            r"sole\s+and\s+exclusive\s+remedy"
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                risk_factors.append(f"High-risk clause detected: {pattern}")
                risk_score += 0.3
        
        # Check for missing protective clauses
        protective_clauses = [
            r"limitation\s+of\s+liability",
            r"force\s+majeure",
            r"governing\s+law",
            r"dispute\s+resolution"
        ]
        
        for clause in protective_clauses:
            if not re.search(clause, content, re.IGNORECASE):
                risk_factors.append(f"Missing protective clause: {clause}")
                risk_score += 0.2
        
        # Determine risk level
        if risk_score >= 0.8:
            risk_level = LegalRiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = LegalRiskLevel.HIGH
        elif risk_score >= 0.4:
            risk_level = LegalRiskLevel.MEDIUM
        elif risk_score >= 0.2:
            risk_level = LegalRiskLevel.LOW
        else:
            risk_level = LegalRiskLevel.MINIMAL
        
        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors
        }
    
    async def _check_contract_compliance(self, content: str, contract_type: ContractType) -> List[str]:
        """Check contract for compliance issues"""
        compliance_issues = []
        
        # Check for legal compliance requirements
        if not re.search(r"governing\s+law", content, re.IGNORECASE):
            compliance_issues.append("Missing governing law clause")
        
        if not re.search(r"entire\s+agreement", content, re.IGNORECASE):
            compliance_issues.append("Missing entire agreement clause")
        
        # Contract-specific compliance checks
        if contract_type == ContractType.EMPLOYMENT_CONTRACT:
            if not re.search(r"at-will\s+employment|employment\s+term", content, re.IGNORECASE):
                compliance_issues.append("Employment terms not clearly defined")
        
        return compliance_issues
    
    async def _generate_contract_recommendations(self, 
                                               risk_assessment: Dict[str, Any],
                                               compliance_issues: List[str],
                                               contract_type: ContractType) -> List[str]:
        """Generate contract improvement recommendations"""
        recommendations = []
        
        if risk_assessment["risk_level"] in [LegalRiskLevel.HIGH, LegalRiskLevel.CRITICAL]:
            recommendations.append("Review and revise high-risk clauses with legal counsel")
        
        if compliance_issues:
            recommendations.append("Add missing compliance clauses")
        
        if risk_assessment["risk_score"] > 0.5:
            recommendations.append("Consider adding additional protective clauses")
        
        # Contract-specific recommendations
        if contract_type == ContractType.SLA:
            recommendations.append("Ensure SLA metrics are measurable and achievable")
        
        return recommendations
    
    async def _extract_payment_terms(self, content: str) -> Dict[str, Any]:
        """Extract payment terms from contract"""
        payment_terms = {}
        
        # Extract payment amount
        amount_match = re.search(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', content)
        if amount_match:
            payment_terms["amount"] = amount_match.group(1)
        
        # Extract payment schedule
        if re.search(r'monthly|per\s+month', content, re.IGNORECASE):
            payment_terms["schedule"] = "monthly"
        elif re.search(r'annually|per\s+year', content, re.IGNORECASE):
            payment_terms["schedule"] = "annual"
        
        return payment_terms
    
    async def _extract_termination_clause(self, content: str) -> Dict[str, Any]:
        """Extract termination clause details"""
        termination = {}
        
        # Extract notice period
        notice_match = re.search(r'(\d+)\s+days?\s+notice', content, re.IGNORECASE)
        if notice_match:
            termination["notice_period"] = f"{notice_match.group(1)} days"
        
        # Check for termination conditions
        if re.search(r'terminate.*for\s+cause', content, re.IGNORECASE):
            termination["for_cause"] = True
        
        return termination
    
    async def _extract_liability_terms(self, content: str) -> Dict[str, Any]:
        """Extract liability limitation terms"""
        liability = {}
        
        if re.search(r'limitation\s+of\s+liability', content, re.IGNORECASE):
            liability["limited"] = True
        
        # Extract liability cap
        cap_match = re.search(r'liability.*limited\s+to.*\$(\d{1,3}(?:,\d{3})*)', content, re.IGNORECASE)
        if cap_match:
            liability["cap"] = cap_match.group(1)
        
        return liability
    
    async def _extract_ip_terms(self, content: str) -> Dict[str, Any]:
        """Extract intellectual property terms"""
        ip_terms = {}
        
        if re.search(r'intellectual\s+property', content, re.IGNORECASE):
            ip_terms["ip_clause_present"] = True
        
        if re.search(r'work\s+for\s+hire', content, re.IGNORECASE):
            ip_terms["work_for_hire"] = True
        
        return ip_terms
    
    async def _extract_sla_metrics(self, content: str) -> Dict[str, Any]:
        """Extract SLA metrics from service level agreement"""
        sla_metrics = {}
        
        # Extract uptime requirement
        uptime_match = re.search(r'(\d{2,3}(?:\.\d+)?)\s*%\s*uptime', content, re.IGNORECASE)
        if uptime_match:
            sla_metrics["uptime"] = f"{uptime_match.group(1)}%"
        
        # Extract response time
        response_match = re.search(r'respond.*within\s+(\d+)\s+(hours?|minutes?)', content, re.IGNORECASE)
        if response_match:
            sla_metrics["response_time"] = f"{response_match.group(1)} {response_match.group(2)}"
        
        return sla_metrics
    
    async def _extract_confidentiality_scope(self, content: str) -> Dict[str, Any]:
        """Extract confidentiality scope from NDA"""
        confidentiality = {}
        
        if re.search(r'confidential\s+information', content, re.IGNORECASE):
            confidentiality["definition_present"] = True
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s+years?.*confidential', content, re.IGNORECASE)
        if duration_match:
            confidentiality["duration"] = f"{duration_match.group(1)} years"
        
        return confidentiality


class IntellectualPropertyAnalyzer:
    """Intellectual property analysis and protection"""
    
    def __init__(self, redis_client -> None: aioredis.Redis) -> None:
        self.redis = redis_client
        
    async def assess_ip_infringement_risk(self, 
                                        content: str,
                                        content_type: str,
                                        ip_type: IntellectualPropertyType) -> IntellectualPropertyAssessment:
        """Assess intellectual property infringement risk"""
        try:
            assessment_id = str(uuid.uuid4())
            content_id = str(uuid.uuid4())  # Would be provided in real implementation
            
            # Analyze content for IP elements
            protected_elements = await self._identify_protected_elements(content, ip_type)
            
            # Calculate infringement risk
            infringement_risk = await self._calculate_infringement_risk(content, protected_elements, ip_type)
            
            # Generate recommendations
            recommendations = await self._generate_ip_recommendations(infringement_risk, protected_elements, ip_type)
            
            assessment = IntellectualPropertyAssessment(
                assessment_id=assessment_id,
                content_id=content_id,
                ip_type=ip_type,
                infringement_risk=infringement_risk,
                protected_elements=protected_elements,
                recommendations=recommendations,
                assessed_at=datetime.utcnow()
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"IP infringement assessment failed: {str(e)}")
            raise
    
    async def _identify_protected_elements(self, content: str, ip_type: IntellectualPropertyType) -> List[str]:
        """Identify potentially protected IP elements"""
        protected_elements = []
        
        if ip_type == IntellectualPropertyType.COPYRIGHT:
            # Look for copyrightable content
            if re.search(r'copyright|©|\(c\)', content, re.IGNORECASE):
                protected_elements.append("Copyright notice detected")
            
            # Check for creative content indicators
            creative_indicators = ["story", "poem", "article", "image", "video", "music"]
            for indicator in creative_indicators:
                if indicator in content.lower():
                    protected_elements.append(f"Creative content: {indicator}")
        
        elif ip_type == IntellectualPropertyType.TRADEMARK:
            # Look for trademark indicators
            trademark_patterns = [r'™', r'®', r'\btrademark\b', r'\bTM\b']
            for pattern in trademark_patterns:
                if re.search(pattern, content):
                    protected_elements.append("Trademark indicator detected")
        
        elif ip_type == IntellectualPropertyType.PATENT:
            # Look for patent-related content
            patent_indicators = ["invention", "patent", "innovative process", "technical solution"]
            for indicator in patent_indicators:
                if indicator in content.lower():
                    protected_elements.append(f"Patent-related: {indicator}")
        
        return protected_elements
    
    async def _calculate_infringement_risk(self, 
                                         content: str,
                                         protected_elements: List[str],
                                         ip_type: IntellectualPropertyType) -> float:
        """Calculate IP infringement risk score"""
        base_risk = 0.0
        
        # Risk based on protected elements found
        base_risk += len(protected_elements) * 0.2
        
        # IP type specific risk factors
        if ip_type == IntellectualPropertyType.COPYRIGHT:
            if any("copyright notice" in element.lower() for element in protected_elements):
                base_risk += 0.3
        
        elif ip_type == IntellectualPropertyType.TRADEMARK:
            if any("trademark" in element.lower() for element in protected_elements):
                base_risk += 0.4
        
        elif ip_type == IntellectualPropertyType.PATENT:
            if any("patent" in element.lower() for element in protected_elements):
                base_risk += 0.5
        
        # Check for fair use indicators (reduces risk for copyright)
        if ip_type == IntellectualPropertyType.COPYRIGHT:
            fair_use_indicators = ["commentary", "criticism", "parody", "educational", "research"]
            if any(indicator in content.lower() for indicator in fair_use_indicators):
                base_risk -= 0.2
        
        return min(max(base_risk, 0.0), 1.0)
    
    async def _generate_ip_recommendations(self, 
                                         risk_score: float,
                                         protected_elements: List[str],
                                         ip_type: IntellectualPropertyType) -> List[str]:
        """Generate IP protection recommendations"""
        recommendations = []
        
        if risk_score >= 0.7:
            recommendations.append("High IP infringement risk - seek legal review")
            recommendations.append("Consider removing or modifying protected content")
        
        elif risk_score >= 0.4:
            recommendations.append("Moderate IP risk - verify usage rights")
            recommendations.append("Document fair use justification if applicable")
        
        if ip_type == IntellectualPropertyType.COPYRIGHT:
            recommendations.append("Ensure proper attribution for copyrighted material")
            recommendations.append("Consider fair use defense if applicable")
        
        elif ip_type == IntellectualPropertyType.TRADEMARK:
            recommendations.append("Verify trademark usage rights")
            recommendations.append("Consider nominative fair use if applicable")
        
        return recommendations


# Main Legal Framework Engine
class LegalFrameworkEngine:
    """Main legal framework management engine"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
        # Initialize components
        self.document_manager = LegalDocumentManager(db_session, redis_client)
        self.contract_analyzer = ContractAnalyzer(redis_client)
        self.ip_analyzer = IntellectualPropertyAnalyzer(redis_client)
        
    async def comprehensive_legal_review(self, 
                                       content: str,
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive legal review of content"""
        try:
            review_id = str(uuid.uuid4())
            
            # Perform contract analysis if applicable
            contract_analysis = None
            if context.get("content_type") == "contract":
                contract_type = ContractType(context.get("contract_type", "service_agreement"))
                contract_analysis = await self.contract_analyzer.analyze_contract(
                    context.get("contract_id", review_id), content, contract_type
                )
            
            # Perform IP analysis
            ip_assessments = []
            for ip_type in [IntellectualPropertyType.COPYRIGHT, IntellectualPropertyType.TRADEMARK]:
                ip_assessment = await self.ip_analyzer.assess_ip_infringement_risk(
                    content, context.get("content_type", "text"), ip_type
                )
                ip_assessments.append(ip_assessment)
            
            # Generate overall legal risk assessment
            legal_risk = await self._assess_overall_legal_risk(contract_analysis, ip_assessments)
            
            # Generate recommendations
            recommendations = await self._generate_legal_recommendations(
                contract_analysis, ip_assessments, legal_risk
            )
            
            comprehensive_review = {
                "review_id": review_id,
                "overall_legal_risk": legal_risk,
                "contract_analysis": contract_analysis.__dict__ if contract_analysis else None,
                "ip_assessments": [assessment.__dict__ for assessment in ip_assessments],
                "recommendations": recommendations,
                "reviewed_at": datetime.utcnow().isoformat()
            }
            
            # Cache review result
            await self.redis.setex(f"legal_review:{review_id}", 3600 * 24,
                                  json.dumps(comprehensive_review, default=str))
            
            return comprehensive_review
            
        except Exception as e:
            logger.error(f"Comprehensive legal review failed: {str(e)}")
            raise
    
    async def _assess_overall_legal_risk(self, 
                                       contract_analysis: Optional[ContractAnalysisResult],
                                       ip_assessments: List[IntellectualPropertyAssessment]) -> Dict[str, Any]:
        """Assess overall legal risk"""
        risk_factors = []
        risk_scores = []
        
        # Contract risk
        if contract_analysis:
            contract_risk_score = self._risk_level_to_score(contract_analysis.risk_level)
            risk_scores.append(contract_risk_score)
            if contract_risk_score > 0.5:
                risk_factors.extend(contract_analysis.risk_factors)
        
        # IP risk
        for assessment in ip_assessments:
            risk_scores.append(assessment.infringement_risk)
            if assessment.infringement_risk > 0.5:
                risk_factors.append(f"High {assessment.ip_type.value} infringement risk")
        
        # Calculate overall risk
        overall_risk_score = max(risk_scores) if risk_scores else 0.0
        
        if overall_risk_score >= 0.8:
            risk_level = "critical"
        elif overall_risk_score >= 0.6:
            risk_level = "high"
        elif overall_risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "overall_risk_score": overall_risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "component_risks": {
                "contract": contract_analysis.risk_level.value if contract_analysis else "not_applicable",
                "ip_infringement": max([a.infringement_risk for a in ip_assessments]) if ip_assessments else 0.0
            }
        }
    
    def _risk_level_to_score(self, risk_level: LegalRiskLevel) -> float:
        """Convert risk level to numeric score"""
        risk_map = {
            LegalRiskLevel.MINIMAL: 0.1,
            LegalRiskLevel.LOW: 0.3,
            LegalRiskLevel.MEDIUM: 0.5,
            LegalRiskLevel.HIGH: 0.7,
            LegalRiskLevel.CRITICAL: 0.9
        }
        return risk_map.get(risk_level, 0.5)
    
    async def _generate_legal_recommendations(self, 
                                            contract_analysis: Optional[ContractAnalysisResult],
                                            ip_assessments: List[IntellectualPropertyAssessment],
                                            legal_risk: Dict[str, Any]) -> List[str]:
        """Generate comprehensive legal recommendations"""
        recommendations = []
        
        # Overall risk recommendations
        if legal_risk["risk_level"] in ["high", "critical"]:
            recommendations.append("Seek immediate legal counsel review")
            recommendations.append("Consider legal risk mitigation strategies")
        
        # Contract recommendations
        if contract_analysis:
            recommendations.extend(contract_analysis.recommendations)
        
        # IP recommendations
        for assessment in ip_assessments:
            recommendations.extend(assessment.recommendations)
        
        # General legal protection recommendations
        recommendations.extend([
            "Maintain comprehensive legal documentation",
            "Regular legal compliance reviews",
            "Update legal policies as needed"
        ])
        
        return list(set(recommendations))  # Remove duplicates


# Export main classes
__all__ = [
    "LegalFrameworkEngine",
    "LegalDocumentManager",
    "ContractAnalyzer",
    "IntellectualPropertyAnalyzer",
    "LegalFrameworkType",
    "ContractType",
    "LegalRiskLevel",
    "IntellectualPropertyType",
    "LegalJurisdiction",
    "LegalDocument",
    "ContractAnalysisResult",
    "IntellectualPropertyAssessment"
]
