"""
Legal Agent - Advanced Legal Operations & Intelligence System

Professional-grade legal automation covering contract law, intellectual property,
litigation support, and legal document processing for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from ..base import BaseAgent, AgentStatus, AgentMetrics
from ...core.database import get_db_session
from ...core.exceptions import LegalError, ValidationError
from ...security.encryption import ContentEncryption
from ...models.legal_models import (
    LegalCase, Contract, LegalDocument, IntellectualProperty,
    LegalAdvice, LitigationRecord, LegalEntity, LegalCompliance
)
from ...utils.ai_processor import AIProcessor
from ...utils.document_parser import DocumentParser
from ...utils.legal_templates import LegalTemplates

logger = logging.getLogger(__name__)

class LegalActionType(Enum):
    """Legal action categories"""
    CONTRACT_REVIEW = "contract_review"
    IP_PROTECTION = "ip_protection"
    LITIGATION_SUPPORT = "litigation_support"
    COMPLIANCE_CHECK = "compliance_check"
    DOCUMENT_GENERATION = "document_generation"
    LEGAL_RESEARCH = "legal_research"
    RISK_ASSESSMENT = "risk_assessment"
    NEGOTIATION_SUPPORT = "negotiation_support"

class LegalPriority(Enum):
    """Legal matter priority levels"""
    CRITICAL = "critical"        # Immediate legal action required
    HIGH = "high"               # Urgent legal attention needed  
    MEDIUM = "medium"           # Standard legal processing
    LOW = "low"                 # Routine legal maintenance

class LegalJurisdiction(Enum):
    """Legal jurisdiction coverage"""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_GENERAL = "eu_general" 
    UK_COMMON = "uk_common"
    GERMAN_CIVIL = "german_civil"
    FRENCH_CIVIL = "french_civil"
    INTERNATIONAL = "international"
    PLATFORM_SPECIFIC = "platform_specific"

@dataclass
class LegalContext:
    """Legal processing context information"""
    user_id: str
    content_id: str
    action_type: LegalActionType
    priority: LegalPriority
    jurisdiction: LegalJurisdiction
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class LegalResult:
    """Legal operation result structure"""
    success: bool
    legal_advice: Optional[str] = None
    documents_generated: List[str] = field(default_factory=list)
    contracts_reviewed: List[str] = field(default_factory=list)
    ip_protections: List[str] = field(default_factory=list)
    risk_assessment: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)
    compliance_status: Optional[str] = None
    legal_entities: List[str] = field(default_factory=list)
    litigation_status: Optional[str] = None
    contract_terms: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    confidence_score: float = 0.0
    error_message: Optional[str] = None


class LegalAgent(BaseAgent):
    """
    Advanced Legal Operations & Intelligence System
    
    Comprehensive legal automation covering:
    - Contract law and analysis
    - Intellectual property protection
    - Litigation support and case management
    - Legal document generation and processing
    - Compliance monitoring and regulatory tracking
    - Risk assessment and legal advisory
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("legal_agent", config)
        self.ai_processor = AIProcessor(config.get('ai_config', {}))
        self.document_parser = DocumentParser()
        self.legal_templates = LegalTemplates()
        self.encryption = ContentEncryption()
        self.supported_actions = [action.value for action in LegalActionType]
        self.legal_database = None
        self._initialize_legal_systems()
    
    def _initialize_legal_systems(self):
        """Initialize legal processing systems"""
        try:
            # Initialize legal database connection
            self.legal_database = self._setup_legal_database()
            
            # Load legal templates and forms
            self.templates = self.legal_templates.load_all_templates()
            
            # Initialize AI models for legal processing
            self._setup_legal_ai_models()
            
            # Configure legal jurisdiction handlers
            self._setup_jurisdiction_handlers()
            
            logger.info("Legal systems initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize legal systems: {e}")
            raise LegalError(f"Legal system initialization failed: {e}")
    
    def _setup_legal_database(self):
        """Setup legal database connections and indexes"""
        try:
            db = get_db_session()
            
            # Verify legal tables exist
            tables = ['legal_cases', 'contracts', 'legal_documents', 
                     'intellectual_property', 'legal_entities', 'litigation_records']
            
            for table in tables:
                if not self._table_exists(db, table):
                    logger.warning(f"Legal table {table} not found")
            
            return db
            
        except Exception as e:
            logger.error(f"Legal database setup failed: {e}")
            raise LegalError(f"Database setup error: {e}")
    
    def _setup_legal_ai_models(self):
        """Initialize AI models for legal processing"""
        try:
            # Legal document classifier
            self.document_classifier = pipeline(
                "text-classification",
                model="nlpaueb/legal-bert-base-uncased",
                device=0 if self.config.get('use_gpu', False) else -1
            )
            
            # Contract term extractor
            self.term_extractor = pipeline(
                "ner",
                model="law-ai/roberta-legal-ner",
                device=0 if self.config.get('use_gpu', False) else -1
            )
            
            # Legal text summarizer
            self.legal_summarizer = pipeline(
                "summarization",
                model="microsoft/DialoGPT-legal-medium",
                device=0 if self.config.get('use_gpu', False) else -1
            )
            
            logger.info("Legal AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Legal AI models setup failed: {e}")
            # Continue without AI models if they fail to load
            self.document_classifier = None
            self.term_extractor = None
            self.legal_summarizer = None
    
    def _setup_jurisdiction_handlers(self):
        """Setup legal jurisdiction specific handlers"""
        self.jurisdiction_handlers = {
            LegalJurisdiction.US_FEDERAL: self._handle_us_federal_law,
            LegalJurisdiction.EU_GENERAL: self._handle_eu_law,
            LegalJurisdiction.GERMAN_CIVIL: self._handle_german_law,
            LegalJurisdiction.FRENCH_CIVIL: self._handle_french_law,
            LegalJurisdiction.UK_COMMON: self._handle_uk_law,
            LegalJurisdiction.INTERNATIONAL: self._handle_international_law,
            LegalJurisdiction.PLATFORM_SPECIFIC: self._handle_platform_law
        }
    
    async def process_legal_matter(self, context: LegalContext) -> LegalResult:
        """
        Process comprehensive legal matter with full analysis
        
        Args:
            context: Legal processing context
            
        Returns:
            Complete legal analysis results
        """
        try:
            start_time = datetime.now(timezone.utc)
            
            # Validate legal context
            self._validate_legal_context(context)
            
            # Route to appropriate legal handler
            handler = self._get_legal_handler(context.action_type)
            if not handler:
                raise LegalError(f"No handler found for action type: {context.action_type}")
            
            # Execute legal processing
            result = await handler(context)
            
            # Enhance with jurisdiction-specific analysis
            if context.jurisdiction in self.jurisdiction_handlers:
                jurisdiction_result = await self.jurisdiction_handlers[context.jurisdiction](context, result)
                result = self._merge_legal_results(result, jurisdiction_result)
            
            # Calculate processing metrics
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            result.processing_time = processing_time
            
            # Log legal action for audit trail
            await self._log_legal_action(context, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Legal matter processing failed: {e}")
            return LegalResult(
                success=False,
                error_message=str(e),
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds() if 'start_time' in locals() else 0.0
            )
    
    def _get_legal_handler(self, action_type: LegalActionType):
        """Get appropriate handler for legal action type"""
        handlers = {
            LegalActionType.CONTRACT_REVIEW: self._handle_contract_review,
            LegalActionType.IP_PROTECTION: self._handle_ip_protection,
            LegalActionType.LITIGATION_SUPPORT: self._handle_litigation_support,
            LegalActionType.COMPLIANCE_CHECK: self._handle_compliance_check,
            LegalActionType.DOCUMENT_GENERATION: self._handle_document_generation,
            LegalActionType.LEGAL_RESEARCH: self._handle_legal_research,
            LegalActionType.RISK_ASSESSMENT: self._handle_risk_assessment,
            LegalActionType.NEGOTIATION_SUPPORT: self._handle_negotiation_support
        }
        return handlers.get(action_type)
    
    async def _handle_contract_review(self, context: LegalContext) -> LegalResult:
        """Handle comprehensive contract review and analysis"""
        try:
            contract_content = context.metadata.get('contract_content', '')
            if not contract_content:
                raise LegalError("Contract content is required for review")
            
            # Extract contract terms using AI
            terms = await self._extract_contract_terms(contract_content)
            
            # Analyze contract clauses
            clause_analysis = await self._analyze_contract_clauses(contract_content)
            
            # Identify potential risks
            risk_assessment = await self._assess_contract_risks(terms, clause_analysis)
            
            # Generate recommendations
            recommendations = await self._generate_contract_recommendations(risk_assessment)
            
            # Create legal advice summary
            legal_advice = await self._generate_contract_advice(terms, risk_assessment)
            
            return LegalResult(
                success=True,
                legal_advice=legal_advice,
                contract_terms=terms,
                risk_assessment=risk_assessment,
                recommendations=recommendations,
                confidence_score=self._calculate_confidence_score(terms, clause_analysis)
            )
            
        except Exception as e:
            logger.error(f"Contract review failed: {e}")
            raise LegalError(f"Contract review error: {e}")
    
    async def _handle_ip_protection(self, context: LegalContext) -> LegalResult:
        """Handle intellectual property protection and analysis"""
        try:
            content_type = context.metadata.get('content_type', '')
            content_data = context.metadata.get('content_data', '')
            
            # Analyze IP protectability
            ip_analysis = await self._analyze_ip_protectability(content_type, content_data)
            
            # Generate IP protection documents
            protection_docs = await self._generate_ip_documents(ip_analysis)
            
            # Check for prior art or existing IP
            prior_art_search = await self._search_prior_art(content_data)
            
            # Generate IP protection strategy
            protection_strategy = await self._create_protection_strategy(ip_analysis, prior_art_search)
            
            return LegalResult(
                success=True,
                ip_protections=protection_docs,
                documents_generated=protection_docs,
                legal_advice=protection_strategy,
                risk_assessment=prior_art_search,
                confidence_score=ip_analysis.get('confidence', 0.0)
            )
            
        except Exception as e:
            logger.error(f"IP protection failed: {e}")
            raise LegalError(f"IP protection error: {e}")
    
    async def _handle_litigation_support(self, context: LegalContext) -> LegalResult:
        """Handle litigation support and case management"""
        try:
            case_type = context.metadata.get('case_type', '')
            case_details = context.metadata.get('case_details', {})
            
            # Analyze case merits
            case_analysis = await self._analyze_case_merits(case_type, case_details)
            
            # Research relevant case law
            precedent_research = await self._research_precedents(case_type, case_details)
            
            # Generate litigation documents
            litigation_docs = await self._generate_litigation_documents(case_analysis)
            
            # Create case strategy recommendations
            strategy_recommendations = await self._develop_case_strategy(case_analysis, precedent_research)
            
            return LegalResult(
                success=True,
                documents_generated=litigation_docs,
                legal_advice=case_analysis.get('summary', ''),
                recommendations=strategy_recommendations,
                litigation_status="analysis_complete",
                confidence_score=case_analysis.get('strength_score', 0.0)
            )
            
        except Exception as e:
            logger.error(f"Litigation support failed: {e}")
            raise LegalError(f"Litigation support error: {e}")
    
    async def _handle_compliance_check(self, context: LegalContext) -> LegalResult:
        """Handle comprehensive compliance checking"""
        try:
            content_type = context.metadata.get('content_type', '')
            platform = context.metadata.get('platform', '')
            jurisdiction = context.jurisdiction
            
            # Check platform-specific compliance
            platform_compliance = await self._check_platform_compliance(content_type, platform)
            
            # Check jurisdiction-specific regulations
            regulatory_compliance = await self._check_regulatory_compliance(jurisdiction, content_type)
            
            # Analyze overall compliance status
            compliance_status = self._determine_compliance_status(platform_compliance, regulatory_compliance)
            
            # Generate compliance recommendations
            compliance_recommendations = await self._generate_compliance_recommendations(
                platform_compliance, regulatory_compliance
            )
            
            return LegalResult(
                success=True,
                compliance_status=compliance_status,
                recommendations=compliance_recommendations,
                legal_advice=f"Compliance analysis for {content_type} on {platform}",
                confidence_score=0.95 if compliance_status == "compliant" else 0.6
            )
            
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            raise LegalError(f"Compliance check error: {e}")
    
    async def _handle_document_generation(self, context: LegalContext) -> LegalResult:
        """Handle legal document generation"""
        try:
            document_type = context.metadata.get('document_type', '')
            template_data = context.metadata.get('template_data', {})
            
            # Generate document from template
            generated_docs = await self._generate_legal_documents(document_type, template_data)
            
            # Validate generated documents
            validation_results = await self._validate_generated_documents(generated_docs)
            
            # Create document summaries
            document_summaries = await self._create_document_summaries(generated_docs)
            
            return LegalResult(
                success=True,
                documents_generated=list(generated_docs.keys()),
                legal_advice=f"Generated {len(generated_docs)} legal documents",
                recommendations=validation_results,
                confidence_score=0.9
            )
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            raise LegalError(f"Document generation error: {e}")
    
    async def _handle_legal_research(self, context: LegalContext) -> LegalResult:
        """Handle comprehensive legal research"""
        try:
            research_query = context.metadata.get('query', '')
            research_scope = context.metadata.get('scope', 'general')
            
            # Conduct case law research
            case_law_results = await self._research_case_law(research_query, context.jurisdiction)
            
            # Research statutory law
            statutory_results = await self._research_statutes(research_query, context.jurisdiction)
            
            # Analyze regulatory guidance
            regulatory_guidance = await self._research_regulations(research_query, context.jurisdiction)
            
            # Synthesize research findings
            research_summary = await self._synthesize_research_findings(
                case_law_results, statutory_results, regulatory_guidance
            )
            
            return LegalResult(
                success=True,
                legal_advice=research_summary,
                recommendations=self._extract_research_recommendations(research_summary),
                confidence_score=0.85
            )
            
        except Exception as e:
            logger.error(f"Legal research failed: {e}")
            raise LegalError(f"Legal research error: {e}")
    
    async def _handle_risk_assessment(self, context: LegalContext) -> LegalResult:
        """Handle comprehensive legal risk assessment"""
        try:
            risk_factors = context.metadata.get('risk_factors', [])
            business_context = context.metadata.get('business_context', {})
            
            # Analyze legal risks
            risk_analysis = await self._analyze_legal_risks(risk_factors, business_context)
            
            # Calculate risk scores
            risk_scores = self._calculate_risk_scores(risk_analysis)
            
            # Generate risk mitigation strategies
            mitigation_strategies = await self._generate_risk_mitigation(risk_analysis)
            
            # Create comprehensive risk report
            risk_report = self._create_risk_report(risk_analysis, risk_scores, mitigation_strategies)
            
            return LegalResult(
                success=True,
                risk_assessment=risk_analysis,
                recommendations=mitigation_strategies,
                legal_advice=risk_report,
                confidence_score=risk_scores.get('overall_confidence', 0.8)
            )
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            raise LegalError(f"Risk assessment error: {e}")
    
    async def _handle_negotiation_support(self, context: LegalContext) -> LegalResult:
        """Handle negotiation support and strategy"""
        try:
            negotiation_type = context.metadata.get('negotiation_type', '')
            counterparty_info = context.metadata.get('counterparty', {})
            terms_proposed = context.metadata.get('terms', [])
            
            # Analyze negotiation position
            position_analysis = await self._analyze_negotiation_position(
                negotiation_type, counterparty_info, terms_proposed
            )
            
            # Generate negotiation strategies
            negotiation_strategies = await self._generate_negotiation_strategies(position_analysis)
            
            # Create alternative proposals
            alternative_proposals = await self._generate_alternative_proposals(terms_proposed)
            
            # Develop negotiation playbook
            negotiation_playbook = self._create_negotiation_playbook(
                position_analysis, negotiation_strategies, alternative_proposals
            )
            
            return LegalResult(
                success=True,
                legal_advice=negotiation_playbook,
                recommendations=negotiation_strategies,
                contract_terms=alternative_proposals,
                confidence_score=position_analysis.get('strength_score', 0.75)
            )
            
        except Exception as e:
            logger.error(f"Negotiation support failed: {e}")
            raise LegalError(f"Negotiation support error: {e}")
    
    # Jurisdiction-specific handlers
    async def _handle_us_federal_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle US Federal law specific requirements"""
        # Implementation for US Federal law compliance and analysis
        us_specific_analysis = await self._analyze_us_federal_requirements(context)
        result.legal_advice += f"\n\nUS Federal Analysis: {us_specific_analysis}"
        return result
    
    async def _handle_eu_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle EU law specific requirements"""
        # Implementation for EU law compliance (GDPR, Digital Services Act, etc.)
        eu_specific_analysis = await self._analyze_eu_requirements(context)
        result.legal_advice += f"\n\nEU Analysis: {eu_specific_analysis}"
        return result
    
    async def _handle_german_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle German civil law specific requirements"""
        # Implementation for German civil law compliance
        german_specific_analysis = await self._analyze_german_requirements(context)
        result.legal_advice += f"\n\nGerman Law Analysis: {german_specific_analysis}"
        return result
    
    async def _handle_french_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle French civil law specific requirements"""
        # Implementation for French civil law compliance
        french_specific_analysis = await self._analyze_french_requirements(context)
        result.legal_advice += f"\n\nFrench Law Analysis: {french_specific_analysis}"
        return result
    
    async def _handle_uk_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle UK common law specific requirements"""
        # Implementation for UK common law compliance
        uk_specific_analysis = await self._analyze_uk_requirements(context)
        result.legal_advice += f"\n\nUK Law Analysis: {uk_specific_analysis}"
        return result
    
    async def _handle_international_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle international law specific requirements"""
        # Implementation for international law compliance
        international_analysis = await self._analyze_international_requirements(context)
        result.legal_advice += f"\n\nInternational Law Analysis: {international_analysis}"
        return result
    
    async def _handle_platform_law(self, context: LegalContext, result: LegalResult) -> LegalResult:
        """Handle platform-specific legal requirements"""
        # Implementation for platform-specific terms and conditions
        platform_analysis = await self._analyze_platform_requirements(context)
        result.legal_advice += f"\n\nPlatform Compliance Analysis: {platform_analysis}"
        return result
    
    # Helper methods for legal processing
    async def _extract_contract_terms(self, contract_content: str) -> List[Dict[str, Any]]:
        """Extract and categorize contract terms using AI"""
        try:
            if self.term_extractor:
                entities = self.term_extractor(contract_content)
                terms = []
                for entity in entities:
                    terms.append({
                        'term': entity['word'],
                        'category': entity['entity_group'],
                        'confidence': entity['score'],
                        'position': [entity['start'], entity['end']]
                    })
                return terms
            else:
                # Fallback manual extraction
                return self._manual_term_extraction(contract_content)
        except Exception as e:
            logger.error(f"Term extraction failed: {e}")
            return []
    
    def _manual_term_extraction(self, content: str) -> List[Dict[str, Any]]:
        """Manual fallback for contract term extraction"""
        # Implementation for manual contract term extraction
        terms = []
        common_terms = [
            'payment', 'termination', 'liability', 'indemnification',
            'confidentiality', 'intellectual property', 'warranty'
        ]
        
        for term in common_terms:
            if term.lower() in content.lower():
                terms.append({
                    'term': term,
                    'category': 'contract_clause',
                    'confidence': 0.7,
                    'position': [content.lower().find(term.lower()), 
                               content.lower().find(term.lower()) + len(term)]
                })
        return terms
    
    def _validate_legal_context(self, context: LegalContext):
        """Validate legal processing context"""
        if not context.user_id:
            raise ValidationError("User ID is required for legal processing")
        if not context.content_id:
            raise ValidationError("Content ID is required for legal processing")
        if not isinstance(context.action_type, LegalActionType):
            raise ValidationError("Valid legal action type is required")
    
    def _table_exists(self, db: Session, table_name: str) -> bool:
        """Check if database table exists"""
        try:
            result = db.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            return True
        except:
            return False
    
    async def _log_legal_action(self, context: LegalContext, result: LegalResult):
        """Log legal action for audit trail and compliance"""
        try:
            with get_db_session() as db:
                log_entry = {
                    'user_id': context.user_id,
                    'action_type': context.action_type.value,
                    'jurisdiction': context.jurisdiction.value,
                    'success': result.success,
                    'timestamp': context.timestamp,
                    'processing_time': result.processing_time
                }
                # Save to legal audit log
                logger.info(f"Legal action logged: {log_entry}")
        except Exception as e:
            logger.error(f"Failed to log legal action: {e}")


class LegalAgentManager:
    """
    Legal Agent Manager for coordinating legal operations across the platform
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, LegalAgent] = {}
        self.jurisdiction_routing = {}
        self._initialize_manager()
    
    def _initialize_manager(self):
        """Initialize legal agent manager"""
        try:
            # Create specialized legal agents for different jurisdictions
            jurisdictions = [
                LegalJurisdiction.US_FEDERAL,
                LegalJurisdiction.EU_GENERAL,
                LegalJurisdiction.GERMAN_CIVIL,
                LegalJurisdiction.FRENCH_CIVIL,
                LegalJurisdiction.UK_COMMON
            ]
            
            for jurisdiction in jurisdictions:
                agent_config = self.config.copy()
                agent_config['jurisdiction'] = jurisdiction.value
                agent = LegalAgent(agent_config)
                self.agents[jurisdiction.value] = agent
                
            logger.info(f"Legal Agent Manager initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Legal Agent Manager initialization failed: {e}")
            raise LegalError(f"Manager initialization error: {e}")
    
    async def route_legal_request(self, context: LegalContext) -> LegalResult:
        """Route legal request to appropriate specialized agent"""
        try:
            jurisdiction_key = context.jurisdiction.value
            if jurisdiction_key not in self.agents:
                # Fall back to general agent
                jurisdiction_key = LegalJurisdiction.INTERNATIONAL.value
                if jurisdiction_key not in self.agents:
                    raise LegalError(f"No agent available for jurisdiction: {context.jurisdiction}")
            
            agent = self.agents[jurisdiction_key]
            return await agent.process_legal_matter(context)
            
        except Exception as e:
            logger.error(f"Legal request routing failed: {e}")
            raise LegalError(f"Request routing error: {e}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all legal agents"""
        status = {}
        for jurisdiction, agent in self.agents.items():
            status[jurisdiction] = {
                'status': agent.status.value if hasattr(agent, 'status') else 'unknown',
                'active': True,
                'last_activity': datetime.now(timezone.utc).isoformat()
            }
        return status
    error_message: Optional[str] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0

class LegalAgent(BaseAgent):
    """
    Advanced Legal Operations Agent
    
    Handles comprehensive legal operations including:
    - Contract analysis and generation
    - Intellectual property protection
    - Legal document processing
    - Risk assessment and compliance
    - Litigation support and research
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id or f"legal_agent_{uuid.uuid4().hex[:8]}",
            name="Legal Operations Agent",
            version="2.1.0",
            capabilities=[
                "contract_analysis", "ip_protection", "document_generation",
                "legal_research", "compliance_monitoring", "risk_assessment",
                "litigation_support", "negotiation_assistance"
            ]
        )
        self.ai_processor = AIProcessor()
        self.document_parser = DocumentParser()
        self.legal_templates = LegalTemplates()
        self.encryption = ContentEncryption()
        
        # Legal processing metrics
        self.contracts_processed = 0
        self.ip_cases_handled = 0
        self.legal_documents_generated = 0
        self.risk_assessments_completed = 0

    async def process_legal_request(
        self,
        context: LegalContext,
        content_data: Dict[str, Any]
    ) -> LegalResult:
        """
        Process comprehensive legal request with full analysis
        
        Args:
            context: Legal processing context
            content_data: Content requiring legal processing
            
        Returns:
            LegalResult with complete legal analysis
        """
        start_time = time.time()
        
        try:
            # Validate legal context
            await self._validate_legal_context(context)
            
            # Initialize legal processing session
            session = await self._initialize_legal_session(context)
            
            # Route to appropriate legal handler
            result = await self._route_legal_action(context, content_data, session)
            
            # Generate comprehensive legal report
            legal_report = await self._generate_legal_report(context, result, session)
            
            # Update legal metrics
            await self._update_legal_metrics(context, result)
            
            processing_time = time.time() - start_time
            
            return LegalResult(
                success=True,
                legal_advice=result.get('legal_advice'),
                documents_generated=result.get('documents_generated', []),
                contracts_reviewed=result.get('contracts_reviewed', []),
                ip_protections=result.get('ip_protections', []),
                risk_assessment=result.get('risk_assessment'),
                recommendations=result.get('recommendations', []),
                compliance_status=result.get('compliance_status'),
                processing_time=processing_time,
                confidence_score=result.get('confidence_score', 0.85)
            )
            
        except Exception as e:
            logger.error(f"Legal processing failed: {str(e)}")
            return LegalResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )

    async def analyze_contract(
        self,
        contract_data: Dict[str, Any],
        context: LegalContext
    ) -> Dict[str, Any]:
        """
        Advanced contract analysis with AI-powered insights
        
        Args:
            contract_data: Contract information and content
            context: Legal processing context
            
        Returns:
            Comprehensive contract analysis
        """
        try:
            # Parse contract content
            contract_content = await self.document_parser.parse_legal_document(
                contract_data.get('content'),
                document_type='contract'
            )
            
            # AI-powered contract analysis
            analysis_prompt = self._build_contract_analysis_prompt(contract_content, context)
            ai_analysis = await self.ai_processor.process_legal_content(
                analysis_prompt,
                model_type='legal_specialist'
            )
            
            # Extract key contract terms
            key_terms = await self._extract_contract_terms(contract_content)
            
            # Identify legal risks
            risk_analysis = await self._assess_contract_risks(contract_content, context)
            
            # Generate improvement recommendations
            recommendations = await self._generate_contract_recommendations(
                contract_content, ai_analysis, context
            )
            
            # Calculate contract score
            contract_score = await self._calculate_contract_score(
                key_terms, risk_analysis, ai_analysis
            )
            
            self.contracts_processed += 1
            
            return {
                'contract_id': contract_data.get('id'),
                'analysis_summary': ai_analysis.get('summary'),
                'key_terms': key_terms,
                'risk_assessment': risk_analysis,
                'recommendations': recommendations,
                'contract_score': contract_score,
                'legal_status': ai_analysis.get('legal_status'),
                'modification_suggestions': ai_analysis.get('modifications', []),
                'compliance_issues': ai_analysis.get('compliance_issues', [])
            }
            
        except Exception as e:
            logger.error(f"Contract analysis failed: {str(e)}")
            raise LegalError(f"Contract analysis error: {str(e)}")

    async def protect_intellectual_property(
        self,
        content_data: Dict[str, Any],
        protection_type: str,
        context: LegalContext
    ) -> Dict[str, Any]:
        """
        Comprehensive intellectual property protection system
        
        Args:
            content_data: Content requiring IP protection
            protection_type: Type of IP protection needed
            context: Legal processing context
            
        Returns:
            IP protection status and documentation
        """
        try:
            # Generate content fingerprint
            content_hash = await self._generate_content_fingerprint(content_data)
            
            # Analyze IP eligibility
            eligibility_analysis = await self._analyze_ip_eligibility(
                content_data, protection_type, context
            )
            
            # Generate IP documentation
            ip_documents = await self._generate_ip_documents(
                content_data, protection_type, eligibility_analysis
            )
            
            # File IP protection records
            protection_record = await self._file_ip_protection(
                content_data, ip_documents, context
            )
            
            # Setup monitoring for IP violations
            monitoring_setup = await self._setup_ip_monitoring(
                content_hash, protection_record, context
            )
            
            # Generate IP certificate
            ip_certificate = await self._generate_ip_certificate(
                protection_record, eligibility_analysis
            )
            
            self.ip_cases_handled += 1
            
            return {
                'ip_id': protection_record.get('id'),
                'protection_type': protection_type,
                'content_fingerprint': content_hash,
                'eligibility_score': eligibility_analysis.get('score'),
                'protection_status': protection_record.get('status'),
                'documents_generated': ip_documents,
                'certificate_id': ip_certificate.get('id'),
                'monitoring_active': monitoring_setup.get('active', False),
                'protection_coverage': eligibility_analysis.get('coverage'),
                'renewal_date': protection_record.get('renewal_date')
            }
            
        except Exception as e:
            logger.error(f"IP protection failed: {str(e)}")
            raise LegalError(f"IP protection error: {str(e)}")

    async def generate_legal_document(
        self,
        document_type: str,
        parameters: Dict[str, Any],
        context: LegalContext
    ) -> Dict[str, Any]:
        """
        AI-powered legal document generation system
        
        Args:
            document_type: Type of document to generate
            parameters: Document parameters and content
            context: Legal processing context
            
        Returns:
            Generated legal document information
        """
        try:
            # Load appropriate legal template
            template = await self.legal_templates.get_template(
                document_type, context.jurisdiction
            )
            
            # AI-enhanced document generation
            generation_prompt = self._build_document_generation_prompt(
                document_type, parameters, context, template
            )
            
            generated_content = await self.ai_processor.generate_legal_document(
                generation_prompt,
                template_structure=template
            )
            
            # Legal compliance validation
            compliance_check = await self._validate_document_compliance(
                generated_content, document_type, context
            )
            
            # Apply legal formatting and styling
            formatted_document = await self._format_legal_document(
                generated_content, document_type, context
            )
            
            # Generate document metadata
            document_metadata = await self._generate_document_metadata(
                formatted_document, parameters, context
            )
            
            # Encrypt and store document
            document_id = await self._store_legal_document(
                formatted_document, document_metadata, context
            )
            
            self.legal_documents_generated += 1
            
            return {
                'document_id': document_id,
                'document_type': document_type,
                'content_preview': formatted_document[:500] + "...",
                'compliance_status': compliance_check.get('status'),
                'legal_validity': compliance_check.get('validity_score'),
                'jurisdiction_coverage': context.jurisdiction.value,
                'generation_quality': generated_content.get('quality_score', 0.9),
                'metadata': document_metadata,
                'download_url': f"/legal/documents/{document_id}/download"
            }
            
        except Exception as e:
            logger.error(f"Document generation failed: {str(e)}")
            raise LegalError(f"Document generation error: {str(e)}")

    async def assess_legal_risks(
        self,
        content_data: Dict[str, Any],
        context: LegalContext
    ) -> Dict[str, Any]:
        """
        Comprehensive legal risk assessment system
        
        Args:
            content_data: Content for risk assessment
            context: Legal processing context
            
        Returns:
            Detailed legal risk analysis
        """
        try:
            # Analyze content for legal risks
            content_risks = await self._analyze_content_legal_risks(content_data, context)
            
            # Platform-specific risk assessment
            platform_risks = await self._assess_platform_risks(content_data, context)
            
            # IP infringement risk analysis
            ip_risks = await self._assess_ip_infringement_risks(content_data, context)
            
            # Regulatory compliance risks
            regulatory_risks = await self._assess_regulatory_risks(content_data, context)
            
            # Generate risk mitigation strategies
            mitigation_strategies = await self._generate_risk_mitigation(
                content_risks, platform_risks, ip_risks, regulatory_risks
            )
            
            # Calculate overall risk score
            overall_risk_score = await self._calculate_overall_risk_score([
                content_risks, platform_risks, ip_risks, regulatory_risks
            ])
            
            # Generate risk report
            risk_report = await self._generate_risk_report(
                overall_risk_score, mitigation_strategies, context
            )
            
            self.risk_assessments_completed += 1
            
            return {
                'risk_id': f"risk_{uuid.uuid4().hex[:8]}",
                'overall_risk_score': overall_risk_score,
                'risk_level': self._categorize_risk_level(overall_risk_score),
                'content_risks': content_risks,
                'platform_risks': platform_risks,
                'ip_risks': ip_risks,
                'regulatory_risks': regulatory_risks,
                'mitigation_strategies': mitigation_strategies,
                'risk_report': risk_report,
                'assessment_date': datetime.now(timezone.utc).isoformat(),
                'validity_period': '90_days'
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            raise LegalError(f"Risk assessment error: {str(e)}")

    # Private helper methods
    async def _validate_legal_context(self, context: LegalContext):
        """Validate legal processing context"""
        if not context.user_id:
            raise ValidationError("User ID required for legal processing")
        if not context.action_type:
            raise ValidationError("Legal action type required")
        if not context.jurisdiction:
            raise ValidationError("Legal jurisdiction required")

    async def _initialize_legal_session(self, context: LegalContext) -> Dict[str, Any]:
        """Initialize legal processing session"""
        return {
            'session_id': f"legal_{uuid.uuid4().hex[:12]}",
            'start_time': datetime.now(timezone.utc),
            'context': context,
            'status': 'active'
        }

    async def _route_legal_action(
        self,
        context: LegalContext,
        content_data: Dict[str, Any],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route legal request to appropriate handler"""
        action_handlers = {
            LegalActionType.CONTRACT_REVIEW: self._handle_contract_review,
            LegalActionType.IP_PROTECTION: self._handle_ip_protection,
            LegalActionType.DOCUMENT_GENERATION: self._handle_document_generation,
            LegalActionType.RISK_ASSESSMENT: self._handle_risk_assessment,
            LegalActionType.LEGAL_RESEARCH: self._handle_legal_research,
            LegalActionType.COMPLIANCE_CHECK: self._handle_compliance_check
        }
        
        handler = action_handlers.get(context.action_type)
        if not handler:
            raise LegalError(f"Unsupported legal action: {context.action_type}")
            
        return await handler(content_data, context, session)

    def _build_contract_analysis_prompt(self, content: str, context: LegalContext) -> str:
        """Build AI prompt for contract analysis"""
        return f"""
        Analyze the following contract under {context.jurisdiction.value} jurisdiction:
        
        Contract Content:
        {content}
        
        Provide comprehensive analysis including:
        - Key terms and obligations
        - Risk assessment
        - Legal compliance status  
        - Improvement recommendations
        - Potential issues or concerns
        """

    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

class LegalAgentManager:
    """
    Legal Agent Manager - Orchestrates legal operations across the platform
    """
    
    def __init__(self):
        self.active_agents: Dict[str, LegalAgent] = {}
        self.legal_queue = asyncio.Queue()
        self.processing_stats = {
            'total_requests': 0,
            'successful_operations': 0,
            'failed_operations': 0
        }

    async def get_or_create_agent(self, user_id: str) -> LegalAgent:
        """Get existing agent or create new one for user"""
        if user_id not in self.active_agents:
            agent = LegalAgent(agent_id=f"legal_{user_id}")
            await agent.initialize()
            self.active_agents[user_id] = agent
        
        return self.active_agents[user_id]

    async def process_legal_operation(
        self,
        user_id: str,
        operation_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process legal operation with full monitoring"""
        agent = await self.get_or_create_agent(user_id)
        
        context = LegalContext(
            user_id=user_id,
            content_id=data.get('content_id', ''),
            action_type=LegalActionType(operation_type),
            priority=LegalPriority(data.get('priority', 'medium')),
            jurisdiction=LegalJurisdiction(data.get('jurisdiction', 'us_federal')),
            metadata=data.get('metadata', {})
        )
        
        try:
            result = await agent.process_legal_request(context, data)
            self.processing_stats['successful_operations'] += 1
            return result.__dict__
            
        except Exception as e:
            self.processing_stats['failed_operations'] += 1
            logger.error(f"Legal operation failed: {str(e)}")
            raise
        finally:
            self.processing_stats['total_requests'] += 1

    async def get_legal_metrics(self) -> Dict[str, Any]:
        """Get comprehensive legal processing metrics"""
        total_contracts = sum(agent.contracts_processed for agent in self.active_agents.values())
        total_ip_cases = sum(agent.ip_cases_handled for agent in self.active_agents.values())
        total_documents = sum(agent.legal_documents_generated for agent in self.active_agents.values())
        total_assessments = sum(agent.risk_assessments_completed for agent in self.active_agents.values())
        
        return {
            'active_agents': len(self.active_agents),
            'processing_stats': self.processing_stats,
            'contracts_processed': total_contracts,
            'ip_cases_handled': total_ip_cases,
            'documents_generated': total_documents,
            'risk_assessments': total_assessments,
            'success_rate': (
                self.processing_stats['successful_operations'] / 
                max(self.processing_stats['total_requests'], 1)
            ) * 100
        }
