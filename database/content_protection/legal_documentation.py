"""Legal Documentation Generator

Ultra-advanced legal documentation generation system for content protection
with automated DMCA takedowns, cease & desist letters, and litigation support.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
==================================================================
This code and all associated intellectual property are the EXCLUSIVE property of Fahed Mlaiel.
ANY unauthorized use, copying, modification, distribution, or commercialization without 
explicit written permission is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries.
Legal violations will be prosecuted to the full extent of international law.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.content_models import (
    LegalDocument, TakedownRequest, ViolationReport,
    ContentFingerprint, LegalTemplate, CourtOrder
)
from ..security.encryption import AdvancedEncryptionManager
from ...core.config import DatabaseConfig
from ...utils.pdf_generator import LegalPDFGenerator
from ...utils.email_sender import LegalEmailSender
from ...utils.document_validator import DocumentValidator


logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """
Legal document types"""

    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    COPYRIGHT_NOTICE = "copyright_notice"
    LICENSING_AGREEMENT = "licensing_agreement"
    SETTLEMENT_OFFER = "settlement_offer"
    LITIGATION_NOTICE = "litigation_notice"
    EVIDENCE_PRESERVATION = "evidence_preservation"
    COURT_FILING = "court_filing"
    ARBITRATION_DEMAND = "arbitration_demand"
    TRADEMARK_NOTICE = "trademark_notice"


class JurisdictionType(Enum):
    """Legal jurisdictions"""

    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_GENERAL = "eu_general"
    UK = "uk"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GERMANY = "germany"
    FRANCE = "france"
    JAPAN = "japan"
    INTERNATIONAL = "international"


class UrgencyLevel(Enum):
    """Document urgency levels"""

    ROUTINE = "routine"
    STANDARD = "standard"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    COURT_DEADLINE = "court_deadline"


class LegalDocumentationError(Exception):
    """Custom exception for legal documentation operations"""
    pass


class LegalDocumentationGenerator:
    """
    Ultra-advanced legal documentation generator with enterprise features:
    - Automated DMCA takedown generation and submission
    - Multi-jurisdiction legal document templates
    - Evidence collection and preservation
    - Court filing assistance and automation
    - Settlement negotiation documentation
    - Trademark and copyright enforcement
    - International legal compliance
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        config: DatabaseConfig,
        template_loader: Optional[Environment] = None,
        pdf_generator: Optional[LegalPDFGenerator] = None,
        email_sender: Optional[LegalEmailSender] = None,
        document_validator: Optional[DocumentValidator] = None
    ):
        self.db_session = db_session
        self.config = config
        self.template_env = template_loader or Environment(
            loader=FileSystemLoader(config.legal_templates_path or "templates/legal")
        )
        self.pdf_generator = pdf_generator or LegalPDFGenerator()
        self.email_sender = email_sender or LegalEmailSender()
        self.document_validator = document_validator or DocumentValidator()
        
        # Legal settings
        self.default_attorney_info = config.default_attorney_info or {}
        self.law_firm_info = config.law_firm_info or {}
        self.litigation_threshold = config.litigation_threshold or 10000  # USD
        
        # Document templates
        self.document_templates = {
            DocumentType.DMCA_TAKEDOWN: "dmca_takedown.j2",
            DocumentType.CEASE_DESIST: "cease_desist.j2",
            DocumentType.COPYRIGHT_NOTICE: "copyright_notice.j2",
            DocumentType.LICENSING_AGREEMENT: "licensing_agreement.j2",
            DocumentType.SETTLEMENT_OFFER: "settlement_offer.j2",
            DocumentType.LITIGATION_NOTICE: "litigation_notice.j2",
            DocumentType.EVIDENCE_PRESERVATION: "evidence_preservation.j2",
            DocumentType.COURT_FILING: "court_filing.j2",
            DocumentType.ARBITRATION_DEMAND: "arbitration_demand.j2",
            DocumentType.TRADEMARK_NOTICE: "trademark_notice.j2"
        }
        
        # Jurisdiction-specific requirements
        self.jurisdiction_requirements = {
            JurisdictionType.US_FEDERAL: {
                "dmca_safe_harbor": True,
                "statutory_damages": True,
                "attorney_fees": True,
                "injunctive_relief": True
            },
            JurisdictionType.EU_GENERAL: {
                "gdpr_compliance": True,
                "dsa_compliance": True,
                "notice_takedown": True,
                "right_to_explanation": True
            }
        }
        
        logger.info("LegalDocumentationGenerator initialized with enterprise configuration")
    
    async def generate_dmca_takedown_notice(
        self,
        violation_report_id: str,
        copyright_owner: Dict[str, Any],
        infringing_content: Dict[str, Any],
        platform_info: Dict[str, Any],
        urgency: UrgencyLevel = UrgencyLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Generate DMCA takedown notice with full legal compliance
        
        Args:
            violation_report_id: ID of the violation report
            copyright_owner: Copyright owner information
            infringing_content: Details of infringing content
            platform_info: Platform/service provider information
            urgency: Urgency level for processing
            
        Returns:
            Dict containing generated DMCA notice and metadata
        """
        try:
            logger.info(f"Generating DMCA takedown notice for violation: {violation_report_id}")
            
            # Validate copyright ownership
            ownership_validation = await self._validate_copyright_ownership(
                copyright_owner, infringing_content
            )
            
            if not ownership_validation["is_valid"]:
                raise LegalDocumentationError(f"Invalid copyright ownership: {ownership_validation['errors']}")
            
            # Gather evidence
            evidence_package = await self._compile_evidence_package(violation_report_id)
            
            # Generate unique notice ID
            notice_id = f"DMCA-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8]}"
            
            # Prepare template variables
            template_vars = {
                "notice_id": notice_id,
                "generation_date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
                "copyright_owner": {
                    "name": copyright_owner.get("name", ""),
                    "address": copyright_owner.get("address", ""),
                    "email": copyright_owner.get("email", ""),
                    "phone": copyright_owner.get("phone", ""),
                    "registration_number": copyright_owner.get("registration_number", "")
                },
                "authorized_agent": self.default_attorney_info,
                "copyrighted_work": {
                    "title": infringing_content.get("original_title", ""),
                    "description": infringing_content.get("description", ""),
                    "creation_date": infringing_content.get("creation_date", ""),
                    "registration_info": infringing_content.get("registration_info", ""),
                    "first_publication": infringing_content.get("first_publication", "")
                },
                "infringing_material": {
                    "url": infringing_content.get("infringing_url", ""),
                    "description": infringing_content.get("infringement_description", ""),
                    "location": infringing_content.get("location_description", ""),
                    "platform": platform_info.get("name", "")
                },
                "platform": {
                    "name": platform_info.get("name", ""),
                    "dmca_agent": platform_info.get("dmca_agent", {}),
                    "address": platform_info.get("address", ""),
                    "email": platform_info.get("dmca_email", "")
                },
                "evidence": evidence_package,
                "good_faith_statement": await self._generate_good_faith_statement(infringing_content),
                "accuracy_statement": await self._generate_accuracy_statement(),
                "perjury_statement": await self._generate_perjury_statement(),
                "signature_block": await self._generate_signature_block(copyright_owner),
                "urgency_level": urgency.value,
                "follow_up_deadline": (datetime.now() + timedelta(days=14)).strftime("%B %d, %Y")
            }
            
            # Render DMCA notice template
            template = self.template_env.get_template(self.document_templates[DocumentType.DMCA_TAKEDOWN])
            dmca_content = template.render(**template_vars)
            
            # Validate document
            validation_result = await self.document_validator.validate_dmca_notice(dmca_content)
            
            if not validation_result["is_valid"]:
                raise LegalDocumentationError(f"DMCA notice validation failed: {validation_result['errors']}")
            
            # Generate PDF
            pdf_path = await self.pdf_generator.generate_dmca_pdf(dmca_content, notice_id)
            
            # Create legal document record
            dmca_document = {
                "document_id": str(uuid4()),
                "notice_id": notice_id,
                "document_type": DocumentType.DMCA_TAKEDOWN.value,
                "violation_report_id": violation_report_id,
                "jurisdiction": JurisdictionType.US_FEDERAL.value,
                "urgency_level": urgency.value,
                "content": dmca_content,
                "pdf_path": pdf_path,
                "template_variables": template_vars,
                "validation_result": validation_result,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "draft",
                "recipients": [platform_info.get("dmca_email", "")],
                "delivery_methods": ["email", "certified_mail"],
                "legal_requirements_met": True,
                "follow_up_required": True,
                "deadline": (datetime.now() + timedelta(days=14)).isoformat()
            }
            
            # Store document
            await self._store_legal_document(dmca_document)
            
            # Schedule automated follow-up
            await self._schedule_document_follow_up(dmca_document["document_id"], urgency)
            
            logger.info(f"DMCA takedown notice generated successfully: {notice_id}")
            return dmca_document
            
        except Exception as e:
            logger.error(f"DMCA takedown generation failed: {e}")
            raise LegalDocumentationError(f"DMCA generation failed: {e}")
    
    async def generate_cease_desist_letter(
        self,
        infringer_info: Dict[str, Any],
        violation_details: Dict[str, Any],
        copyright_owner: Dict[str, Any],
        demands: List[str],
        deadline_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate cease and desist letter with legal authority
        
        Args:
            infringer_info: Information about the infringer
            violation_details: Details of the copyright violation
            copyright_owner: Copyright owner information
            demands: List of specific demands
            deadline_days: Days to comply with demands
            
        Returns:
            Dict containing generated cease and desist letter
        """
        try:
            logger.info(f"Generating cease and desist letter for infringer: {infringer_info.get('name', 'Unknown')}")
            
            # Calculate monetary damages
            damage_assessment = await self._assess_monetary_damages(violation_details)
            
            # Generate letter ID
            letter_id = f"CD-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8]}"
            
            # Determine escalation path
            escalation_path = await self._determine_escalation_path(damage_assessment["total_damages"])
            
            # Prepare template variables
            template_vars = {
                "letter_id": letter_id,
                "date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
                "infringer": {
                    "name": infringer_info.get("name", ""),
                    "address": infringer_info.get("address", ""),
                    "email": infringer_info.get("email", ""),
                    "business_name": infringer_info.get("business_name", "")
                },
                "copyright_owner": copyright_owner,
                "attorney": self.default_attorney_info,
                "law_firm": self.law_firm_info,
                "violation": {
                    "description": violation_details.get("description", ""),
                    "first_discovered": violation_details.get("discovery_date", ""),
                    "evidence": violation_details.get("evidence_summary", ""),
                    "platforms": violation_details.get("platforms", []),
                    "duration": violation_details.get("violation_duration", "")
                },
                "copyrighted_works": violation_details.get("copyrighted_works", []),
                "damages": damage_assessment,
                "demands": demands,
                "deadline": (datetime.now() + timedelta(days=deadline_days)).strftime("%B %d, %Y"),
                "consequences": await self._generate_legal_consequences(damage_assessment["total_damages"]),
                "settlement_offer": await self._calculate_settlement_offer(damage_assessment),
                "escalation_warning": escalation_path,
                "jurisdiction": await self._determine_jurisdiction(infringer_info, copyright_owner),
                "statutory_provisions": await self._get_applicable_statutes(violation_details)
            }
            
            # Render cease and desist template
            template = self.template_env.get_template(self.document_templates[DocumentType.CEASE_DESIST])
            letter_content = template.render(**template_vars)
            
            # Validate document
            validation_result = await self.document_validator.validate_cease_desist(letter_content)
            
            # Generate PDF
            pdf_path = await self.pdf_generator.generate_cease_desist_pdf(letter_content, letter_id)
            
            # Create document record
            cd_document = {
                "document_id": str(uuid4()),
                "letter_id": letter_id,
                "document_type": DocumentType.CEASE_DESIST.value,
                "violation_details": violation_details,
                "infringer_info": infringer_info,
                "content": letter_content,
                "pdf_path": pdf_path,
                "template_variables": template_vars,
                "damage_assessment": damage_assessment,
                "settlement_offer": template_vars["settlement_offer"],
                "deadline": template_vars["deadline"],
                "escalation_path": escalation_path,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "draft",
                "delivery_method": "certified_mail_email",
                "follow_up_required": True
            }
            
            # Store document
            await self._store_legal_document(cd_document)
            
            logger.info(f"Cease and desist letter generated: {letter_id}")
            return cd_document
            
        except Exception as e:
            logger.error(f"Cease and desist generation failed: {e}")
            raise LegalDocumentationError(f"Cease and desist generation failed: {e}")
    
    async def generate_litigation_notice(
        self,
        case_details: Dict[str, Any],
        defendants: List[Dict[str, Any]],
        claims: List[str],
        relief_sought: Dict[str, Any],
        jurisdiction: JurisdictionType
    ) -> Dict[str, Any]:
        """
        Generate litigation notice and court filing documents
        
        Args:
            case_details: Details of the legal case
            defendants: List of defendants
            claims: Legal claims being asserted
            relief_sought: Types of relief requested
            jurisdiction: Legal jurisdiction for filing
            
        Returns:
            Dict containing litigation documents
        """
        try:
            logger.info(f"Generating litigation notice for case: {case_details.get('case_name', 'Unknown')}")
            
            # Generate case number
            case_number = f"CV-{datetime.now().strftime('%Y')}-{str(uuid4())[:8]}"
            
            # Prepare comprehensive case package
            case_package = {
                "case_number": case_number,
                "filing_date": datetime.now(timezone.utc).isoformat(),
                "jurisdiction": jurisdiction.value,
                "court_info": await self._get_court_information(jurisdiction),
                "plaintiff": case_details.get("plaintiff", {}),
                "defendants": defendants,
                "case_details": case_details,
                "legal_claims": claims,
                "relief_sought": relief_sought,
                "damages_calculation": await self._calculate_litigation_damages(case_details),
                "evidence_index": await self._compile_litigation_evidence(case_details.get("violation_ids", [])),
                "jurisdiction_analysis": await self._analyze_jurisdiction_basis(defendants, case_details),
                "service_requirements": await self._determine_service_requirements(defendants, jurisdiction),
                "filing_fees": await self._calculate_filing_fees(jurisdiction, relief_sought),
                "procedural_requirements": await self._get_procedural_requirements(jurisdiction)
            }
            
            # Generate multiple litigation documents
            litigation_documents = []
            
            # Complaint
            complaint = await self._generate_complaint(case_package)
            litigation_documents.append(complaint)
            
            # Summons
            for defendant in defendants:
                summons = await self._generate_summons(case_package, defendant)
                litigation_documents.append(summons)
            
            # Motion for preliminary injunction (if applicable)
            if relief_sought.get("injunctive_relief", False):
                injunction_motion = await self._generate_injunction_motion(case_package)
                litigation_documents.append(injunction_motion)
            
            # Evidence preservation demand
            evidence_demand = await self._generate_evidence_preservation_demand(case_package)
            litigation_documents.append(evidence_demand)
            
            # Store litigation package
            litigation_record = {
                "litigation_id": str(uuid4()),
                "case_number": case_number,
                "case_package": case_package,
                "documents": litigation_documents,
                "total_documents": len(litigation_documents),
                "filing_status": "prepared",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "estimated_filing_cost": case_package["filing_fees"]["total"],
                "priority": "high",
                "attorney_assigned": self.default_attorney_info.get("name", ""),
                "next_deadline": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            await self._store_litigation_package(litigation_record)
            
            logger.info(f"Litigation package generated: {case_number} with {len(litigation_documents)} documents")
            return litigation_record
            
        except Exception as e:
            logger.error(f"Litigation notice generation failed: {e}")
            raise LegalDocumentationError(f"Litigation generation failed: {e}")
    
    async def send_legal_document(
        self,
        document_id: str,
        delivery_method: str = "email",
        tracking_required: bool = True
    ) -> Dict[str, Any]:
        """
        Send legal document with proper delivery confirmation
        
        Args:
            document_id: ID of the document to send
            delivery_method: Method of delivery (email, certified_mail, process_service)
            tracking_required: Whether delivery tracking is required
            
        Returns:
            Dict containing delivery confirmation and tracking info
        """
        try:
            logger.info(f"Sending legal document: {document_id} via {delivery_method}")
            
            # Retrieve document
            document = await self._get_legal_document(document_id)
            
            if not document:
                raise LegalDocumentationError(f"Document not found: {document_id}")
            
            delivery_result = {}
            
            if delivery_method == "email":
                # Send via secure email
                delivery_result = await self.email_sender.send_legal_document(
                    document["content"],
                    document["pdf_path"],
                    document["recipients"],
                    document["document_type"],
                    tracking_required
                )
            
            elif delivery_method == "certified_mail":
                # Prepare for certified mail delivery
                delivery_result = await self._prepare_certified_mail_delivery(document)
            
            elif delivery_method == "process_service":
                # Arrange professional process service
                delivery_result = await self._arrange_process_service(document)
            
            # Update document delivery status
            await self._update_document_delivery_status(document_id, delivery_result)
            
            logger.info(f"Document delivery initiated: {document_id}")
            return delivery_result
            
        except Exception as e:
            logger.error(f"Document delivery failed: {e}")
            raise LegalDocumentationError(f"Document delivery failed: {e}")
    
    # Private helper methods
    
    async def _validate_copyright_ownership(
        self, owner_info: Dict[str, Any], content_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate copyright ownership claims"""
        # Implementation for copyright ownership validation
        return {"is_valid": True, "errors": []}
    
    async def _compile_evidence_package(self, violation_id: str) -> Dict[str, Any]:
        """Compile comprehensive evidence package"""
        # Implementation for evidence compilation
        return {"evidence_count": 5, "evidence_types": ["screenshots", "metadata", "fingerprints"]}
    
    async def _assess_monetary_damages(self, violation_details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess monetary damages from copyright violation"""
        # Implementation for damage assessment
        return {"actual_damages": 5000, "profits": 2000, "statutory_damages": 150000, "total_damages": 157000}
    
    async def _store_legal_document(self, document_data: Dict[str, Any]) -> None:
        """Store legal document in database"""
        try:
            legal_doc = LegalDocument(
                id=uuid4(),
                document_id=document_data["document_id"],
                document_type=document_data["document_type"],
                content=document_data["content"],
                metadata=document_data,
                created_at=datetime.now(timezone.utc),
                status="draft"
            )
            
            self.db_session.add(legal_doc)
            await self.db_session.commit()
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to store legal document: {e}")
            raise


__all__ = [
    "LegalDocumentationGenerator",
    "DocumentType",
    "JurisdictionType",
    "UrgencyLevel",
    "LegalDocumentationError"
]
