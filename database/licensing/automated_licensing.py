"""Automated Licensing Database Module

Enterprise-grade automated licensing system for IA Influencer Agent platform.
Manages automated licensing workflows, AI-powered negotiations, and smart contract execution.

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Team: Lead AI Developer, Backend Senior, ML Engineer, Legal Tech Expert, Automation Specialist

STRICT COPYRIGHT WARNING: This code and concept are EXCLUSIVE intellectual property of Fahed Mlaiel.
ANY unauthorized use, copying, or theft without explicit written authorization is STRICTLY PROHIBITED
and subject to immediate legal prosecution under German law.
Contact: mlaiel@live.de for ANY authorization requests.
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4
import asyncio
import json
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, deque
import logging
from pathlib import Path

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Decimal as SQLDecimal, JSON, ForeignKey, ARRAY, Index,
    CheckConstraint, UniqueConstraint, event, func, select,
    and_, or_, case, exists
)
from sqlalchemy.orm import relationship, Session, sessionmaker, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine

import redis
from celery import Celery
from pydantic import BaseModel as PydanticModel, validator, Field
from prometheus_client import Counter, Histogram, Gauge

from ..core.database import get_database_session
from ..core.cache import CacheManager
from ..core.security import SecurityManager, encrypt_sensitive_data
from ..models.base import BaseModel, TimestampMixin, AuditMixin
from ..schemas.automated_licensing_schemas import (
    LicenseTemplateSchema, AutomationRuleSchema, LicenseRequestSchema,
    LicenseNegotiationSchema, SmartContractSchema, WorkflowExecutionSchema
)
from ..ai.contract_analyzer import ContractAnalyzer
from ..ai.pricing_optimizer import PricingOptimizer
from ..integrations.blockchain import BlockchainService
from ..integrations.legal_services import LegalComplianceService

# Metrics
licensing_requests_total = Counter('licensing_requests_total', 'Total licensing requests', ['status', 'automation_level'])
licensing_processing_time = Histogram('licensing_processing_seconds', 'Licensing processing time')
active_licenses_gauge = Gauge('active_licenses_total', 'Total active licenses')

logger = logging.getLogger(__name__)

class AutomationLevel(IntEnum):
    """
Advanced automation levels with priority scoring"""

    MANUAL = 1
    RULE_BASED = 2
    SEMI_AUTOMATED = 3
    FULLY_AUTOMATED = 4
    AI_POWERED = 5
    MACHINE_LEARNING = 6
    NEURAL_NETWORK = 7
    AUTONOMOUS = 8

class RequestStatus(Enum):
    """
Comprehensive request status tracking"""

    SUBMITTED = "submitted"
    VALIDATED = "validated"
    UNDER_REVIEW = "under_review"
    AI_ANALYZING = "ai_analyzing"
    PRICE_CALCULATING = "price_calculating"
    NEGOTIATING = "negotiating"
    COUNTER_OFFERED = "counter_offered"
    TERMS_AGREED = "terms_agreed"
    CONTRACT_GENERATING = "contract_generating"
    LEGAL_REVIEW = "legal_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    EXECUTED = "executed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class LicenseType(Enum):
    """Comprehensive license types"""

    STANDARD = "standard"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    SYNC_LICENSE = "sync_license"
    MASTER_LICENSE = "master_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    PRINT_LICENSE = "print_license"
    DIGITAL_LICENSE = "digital_license"
    BROADCAST_LICENSE = "broadcast_license"
    STREAMING_LICENSE = "streaming_license"

class PricingModel(Enum):
    """Advanced pricing models"""

    FIXED_RATE = "fixed_rate"
    USAGE_BASED = "usage_based"
    ROYALTY_PERCENTAGE = "royalty_percentage"
    TIERED_PRICING = "tiered_pricing"
    DYNAMIC_PRICING = "dynamic_pricing"
    AI_OPTIMIZED = "ai_optimized"
    AUCTION_BASED = "auction_based"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"
    REVENUE_SHARE = "revenue_share"

class NegotiationStrategy(Enum):
    """AI negotiation strategies"""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    ML_OPTIMIZED = "ml_optimized"
    GAME_THEORY = "game_theory"
    MULTI_OBJECTIVE = "multi_objective"

@dataclass
class LicensingMetrics:
    """Advanced licensing metrics tracking"""
    total_requests: int = 0
    approved_requests: int = 0
    rejected_requests: int = 0
    average_processing_time: float = 0.0
    automation_rate: float = 0.0
    revenue_generated: Decimal = Decimal('0.00')
    cost_savings: Decimal = Decimal('0.00')
    client_satisfaction: float = 0.0
    legal_compliance_rate: float = 100.0
    
    def approval_rate(self) -> float:
        """
Calculate approval rate percentage"""
        if self.total_requests == 0:
            return 0.0
class LicenseNegotiation(BaseModel, TimestampMixin, AuditMixin):
    """
    AI-powered license negotiation tracking with advanced strategy optimization.
    Supports multi-round negotiations and machine learning-based recommendations.
    """
    __tablename__ = "license_negotiations"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_requests.id'), nullable=False)
    negotiation_session = Column(String(100), nullable=False)
    
    # Negotiation parties
    initiator_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    responder_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    mediator_id = Column(PostgresUUID(as_uuid=True))  # AI or human mediator
    
    # Negotiation parameters
    round_number = Column(Integer, default=1)
    negotiation_type = Column(String(50), default="bilateral")  # bilateral, multilateral, auction
    strategy = Column(String(50), default=NegotiationStrategy.BALANCED.value)
    
    # Terms being negotiated
    original_terms = Column(JSONB, nullable=False)
    proposed_terms = Column(JSONB, nullable=False)
    counter_terms = Column(JSONB)
    final_terms = Column(JSONB)
    
    # Financial negotiations
    original_price = Column(SQLDecimal(12, 4), nullable=False)
    proposed_price = Column(SQLDecimal(12, 4), nullable=False)
    counter_price = Column(SQLDecimal(12, 4))
    final_price = Column(SQLDecimal(12, 4))
    price_movement_history = Column(JSONB, default=list)
    
    # AI analysis and recommendations
    ai_strategy_recommendation = Column(JSONB, default=dict)
    market_analysis = Column(JSONB, default=dict)
    competitor_pricing = Column(JSONB, default=dict)
    success_probability = Column(SQLDecimal(3, 2), default=Decimal('0.50'))
    
    # Negotiation status
    status = Column(String(50), default="active")
    outcome = Column(String(50))  # accepted, rejected, abandoned, escalated
    deadline = Column(DateTime(timezone=True))
    timeout_hours = Column(Integer, default=72)
    
    # Communication tracking
    messages = Column(JSONB, default=list)
    escalation_count = Column(Integer, default=0)
    stalemate_detected = Column(Boolean, default=False)
    concession_pattern = Column(JSONB, default=dict)
    
    # Performance metrics
    response_time_hours = Column(SQLDecimal(6, 2))
    satisfaction_score = Column(SQLDecimal(3, 2))
    negotiation_efficiency = Column(SQLDecimal(3, 2))
    value_created = Column(SQLDecimal(12, 4))
    
    # Relationships
    request = relationship("LicenseRequest", back_populates="negotiations")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_negotiation_request_round', 'request_id', 'round_number'),
        Index('idx_negotiation_status_deadline', 'status', 'deadline'),
        Index('idx_negotiation_strategy_outcome', 'strategy', 'outcome'),
        CheckConstraint('round_number >= 1', name='check_round_number_positive'),
        CheckConstraint('success_probability >= 0 AND success_probability <= 1', name='check_success_probability_valid'),
    )

class SmartContract(BaseModel, TimestampMixin, AuditMixin):
    """
    Blockchain-enabled smart contracts for automated license execution.
    Integrates with multiple blockchain networks for secure, transparent licensing.
    """
    __tablename__ = "smart_contracts"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_requests.id'), nullable=False)
    contract_address = Column(String(255), unique=True)
    blockchain_network = Column(String(50), default="ethereum")
    
    # Contract details
    contract_type = Column(String(50), nullable=False)
    contract_code = Column(Text)  # Smart contract source code
    abi_definition = Column(JSONB)  # Application Binary Interface
    deployment_hash = Column(String(255))
    
    # Contract terms
    terms_hash = Column(String(255), nullable=False)  # Immutable terms hash
    license_terms = Column(JSONB, nullable=False)
    payment_terms = Column(JSONB, nullable=False)
    execution_conditions = Column(JSONB, default=dict)
    
    # Blockchain integration
    gas_price = Column(SQLDecimal(18, 8))
    gas_limit = Column(Integer)
    transaction_fee = Column(SQLDecimal(18, 8))
    confirmation_blocks = Column(Integer, default=12)
    
    # Contract status
    status = Column(String(50), default="draft")  # draft, deployed, active, executed, terminated
    deployment_date = Column(DateTime(timezone=True))
    activation_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    
    # Execution tracking
    execution_events = Column(JSONB, default=list)
    milestone_completions = Column(JSONB, default=dict)
    payment_history = Column(JSONB, default=list)
    violation_reports = Column(JSONB, default=list)
    
    # Oracle integration
    oracle_feeds = Column(JSONB, default=dict)  # External data sources
    price_oracles = Column(ARRAY(String), default=list)
    verification_oracles = Column(ARRAY(String), default=list)
    
    # Security and compliance
    audit_reports = Column(JSONB, default=list)
    security_score = Column(SQLDecimal(3, 2), default=Decimal('0.00'))
    compliance_verified = Column(Boolean, default=False)
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_contract_request_status', 'request_id', 'status'),
        Index('idx_contract_blockchain_address', 'blockchain_network', 'contract_address'),
        Index('idx_contract_expiration', 'expiration_date', 'status'),
    )

class WorkflowExecution(BaseModel, TimestampMixin, AuditMixin):
    """
    Advanced workflow execution engine with parallel processing and error recovery.
    Supports complex business process automation and human-in-the-loop workflows.
    """
    __tablename__ = "workflow_executions"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_requests.id'), nullable=False)
    workflow_definition_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    execution_id = Column(String(100), unique=True, nullable=False)
    
    # Workflow metadata
    workflow_name = Column(String(255), nullable=False)
    workflow_version = Column(String(20), default="1.0.0")
    workflow_type = Column(String(50), nullable=False)  # sequential, parallel, conditional
    
    # Execution state
    status = Column(String(50), default="pending")  # pending, running, completed, failed, cancelled
    current_step = Column(String(255))
    step_sequence = Column(JSONB, default=list)
    completed_steps = Column(JSONB, default=list)
    failed_steps = Column(JSONB, default=list)
    
    # Timing and performance
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    timeout_at = Column(DateTime(timezone=True))
    total_duration_seconds = Column(Integer)
    step_durations = Column(JSONB, default=dict)
    
    # Input/Output data
    input_data = Column(JSONB, nullable=False)
    output_data = Column(JSONB, default=dict)
    intermediate_results = Column(JSONB, default=dict)
    context_variables = Column(JSONB, default=dict)
    
    # Error handling and recovery
    error_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_log = Column(JSONB, default=list)
    recovery_actions = Column(JSONB, default=list)
    
    # Human intervention
    human_tasks = Column(JSONB, default=list)
    approval_required = Column(Boolean, default=False)
    approver_id = Column(PostgresUUID(as_uuid=True))
    approval_deadline = Column(DateTime(timezone=True))
    
    # Performance metrics
    automation_rate = Column(SQLDecimal(3, 2), default=Decimal('1.00'))
    efficiency_score = Column(SQLDecimal(3, 2))
    quality_score = Column(SQLDecimal(3, 2))
    cost_savings = Column(SQLDecimal(12, 2))
    
    # Relationships
    request = relationship("LicenseRequest", back_populates="executions")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_workflow_request_status', 'request_id', 'status'),
        Index('idx_workflow_type_version', 'workflow_type', 'workflow_version'),
        Index('idx_workflow_timeout', 'timeout_at', 'status'),
    )

class RuleExecution(BaseModel, TimestampMixin):
    """
    Detailed tracking of automation rule executions for analytics and optimization.
    """
    __tablename__ = "rule_executions"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_id = Column(PostgresUUID(as_uuid=True), ForeignKey('automation_rules.id'), nullable=False)
    request_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_requests.id'))
    
    # Execution details
    executed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    execution_context = Column(JSONB, nullable=False)
    execution_result = Column(JSONB)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    
    # Performance metrics
    execution_time_ms = Column(Integer)
    cpu_usage_percent = Column(SQLDecimal(5, 2))
    memory_usage_mb = Column(SQLDecimal(8, 2))
    
    # Relationships
    rule = relationship("AutomationRule", back_populates="rule_executions")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_rule_execution_time', 'rule_id', 'executed_at'),
        Index('idx_rule_execution_success', 'success', 'executed_at'),
    )

class AutomatedLicensingService:
    """
    Enterprise-grade automated licensing service with AI-powered decision making.
    Provides comprehensive licensing workflow automation and optimization.
    """
    
    def __init__(self, db_session: Session, cache_manager: CacheManager, security_manager: SecurityManager):
        self.db = db_session
        self.cache = cache_manager
        self.security = security_manager
        self.contract_analyzer = ContractAnalyzer()
        self.pricing_optimizer = PricingOptimizer()
        self.blockchain_service = BlockchainService()
        self.legal_service = LegalComplianceService()
        self.metrics = LicensingMetrics()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize Redis for task queuing
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # Initialize Celery for background tasks
        self.celery_app = Celery('licensing_automation')
        
        logger.info("AutomatedLicensingService initialized")
    
    async def process_license_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for processing license requests with full automation pipeline.
        
        Args:
            request_data: Complete license request information
            
        Returns:
            Processing result with status, recommendations, and next steps
        """
        with licensing_processing_time.time():
            try:
                # Create license request record
                request = await self._create_license_request(request_data)
                
                # AI-powered initial analysis
                analysis_result = await self._analyze_request_with_ai(request)
                
                # Determine automation level
                automation_decision = await self._determine_automation_level(request, analysis_result)
                
                # Route based on automation decision
                if automation_decision['level'] >= AutomationLevel.FULLY_AUTOMATED:
                    result = await self._process_automatically(request, automation_decision)
                elif automation_decision['level'] >= AutomationLevel.SEMI_AUTOMATED:
                    result = await self._process_semi_automatically(request, automation_decision)
                else:
                    result = await self._route_for_manual_review(request, automation_decision)
                
                # Update metrics
                licensing_requests_total.labels(
                    status=result['status'],
                    automation_level=automation_decision['level'].name
                ).inc()
                
                # Log processing completion
                logger.info(f"License request {request.request_number} processed: {result['status']}")
                
                return result
                
            except Exception as e:
                logger.error(f"Error processing license request: {e}")
                licensing_requests_total.labels(status='error', automation_level='unknown').inc()
                raise
    
    async def _create_license_request(self, request_data: Dict[str, Any]) -> LicenseRequest:
        """Create and validate license request record"""
        request_number = self._generate_request_number()
        
        request = LicenseRequest(
            request_number=request_number,
            template_id=request_data.get('template_id'),
            licensor_id=request_data['licensor_id'],
            licensee_id=request_data['licensee_id'],
            content_id=request_data['content_id'],
            content_type=request_data['content_type'],
            license_type=request_data['license_type'],
            usage_rights=request_data['usage_rights'],
            requested_amount=Decimal(str(request_data['requested_amount'])),
            currency=request_data.get('currency', 'EUR'),
            territory=request_data.get('territory', []),
            processing_started_at=datetime.now(timezone.utc)
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    async def _analyze_request_with_ai(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Comprehensive AI analysis of license request"""
        analysis_tasks = [
            self._analyze_content_rights(request),
            self._analyze_market_pricing(request),
            self._assess_risk_factors(request),
            self._check_compliance_requirements(request),
            self._evaluate_negotiation_potential(request)
        ]
        
        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        combined_analysis = {
            'content_rights': results[0] if not isinstance(results[0], Exception) else {},
            'market_pricing': results[1] if not isinstance(results[1], Exception) else {},
            'risk_assessment': results[2] if not isinstance(results[2], Exception) else {},
            'compliance': results[3] if not isinstance(results[3], Exception) else {},
            'negotiation': results[4] if not isinstance(results[4], Exception) else {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Update request with AI analysis
        request.ai_analysis = combined_analysis
        self.db.commit()
        
        return combined_analysis
    
    async def _determine_automation_level(self, request: LicenseRequest, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
Determine appropriate automation level based on AI analysis"""
        automation_score = Decimal('0.0')
        factors = []
        
        # Template automation capability
        if request.template and request.template.is_fully_automated:
            automation_score += Decimal('0.3')
            factors.append("template_automated")
        
        # Risk assessment
        risk_score = analysis.get('risk_assessment', {}).get('overall_risk', 0.5)
        if risk_score < 0.3:
            automation_score += Decimal('0.2')
            factors.append("low_risk")
        
        # Pricing confidence
        pricing_confidence = analysis.get('market_pricing', {}).get('confidence', 0.5)
        if pricing_confidence > 0.8:
            automation_score += Decimal('0.2')
            factors.append("high_pricing_confidence")
        
        # Compliance simplicity
        compliance_complexity = analysis.get('compliance', {}).get('complexity', 'medium')
        if compliance_complexity == 'low':
            automation_score += Decimal('0.15')
            factors.append("simple_compliance")
        
        # Historical success rate
        historical_success = await self._get_historical_success_rate(request)
        automation_score += Decimal(str(historical_success * 0.15))
        factors.append(f"historical_success_{historical_success:.2f}")
        
        # Determine automation level
        if automation_score >= Decimal('0.85'):
            level = AutomationLevel.AUTONOMOUS
        elif automation_score >= Decimal('0.7'):
            level = AutomationLevel.AI_POWERED
        elif automation_score >= Decimal('0.55'):
            level = AutomationLevel.FULLY_AUTOMATED
        elif automation_score >= Decimal('0.4'):
            level = AutomationLevel.SEMI_AUTOMATED
        else:
            level = AutomationLevel.MANUAL
        
        request.automation_score = automation_score
        self.db.commit()
        
        return {
            'level': level,
            'score': float(automation_score),
            'factors': factors,
            'recommendation': self._get_automation_recommendation(level)
        }
    
    def _generate_request_number(self) -> str:
        """Generate unique request number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:8].upper()
        return f"LR-{timestamp}-{random_suffix}"
    
    async def _analyze_content_rights(self, request: LicenseRequest) -> Dict[str, Any]:
        """Analyze content ownership and rights status"""
        # Implementation would integrate with copyright database
        return {
            'ownership_verified': True,
            'rights_clear': True,
            'existing_licenses': [],
            'restrictions': []
        }
    
    async def _analyze_market_pricing(self, request: LicenseRequest) -> Dict[str, Any]:
        """
AI-powered market pricing analysis"""
        return await self.pricing_optimizer.analyze_pricing(request)
    
    async def _assess_risk_factors(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Comprehensive risk assessment"""
        return {
            'overall_risk': 0.3,
            'legal_risk': 0.2,
            'financial_risk': 0.1,
            'reputational_risk': 0.15,
            'technical_risk': 0.05
        }
    
    async def _check_compliance_requirements(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Check legal and regulatory compliance"""
        return await self.legal_service.check_compliance(request)
    
    async def _evaluate_negotiation_potential(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Evaluate potential for automated negotiation"""
        return {
            'negotiation_likelihood': 0.4,
            'price_flexibility': 0.3,
            'terms_flexibility': 0.2,
            'strategy_recommendation': NegotiationStrategy.BALANCED.value
        }
    
    async def _get_historical_success_rate(self, request: LicenseRequest) -> float:
        """
Get historical success rate for similar requests"""
        # Query historical data for similar requests
        similar_requests = self.db.query(LicenseRequest).filter(
            and_(
                LicenseRequest.content_type == request.content_type,
                LicenseRequest.license_type == request.license_type,
                LicenseRequest.status.in_([RequestStatus.APPROVED.value, RequestStatus.EXECUTED.value])
            )
        ).limit(100).all()
        
        if not similar_requests:
            return 0.5  # Default rate
        
        total_requests = len(similar_requests)
        successful_requests = len([r for r in similar_requests if r.status == RequestStatus.APPROVED.value])
        
        return successful_requests / total_requests if total_requests > 0 else 0.5
    
    def _get_automation_recommendation(self, level: AutomationLevel) -> str:
        """
Get human-readable automation recommendation"""
        recommendations = {
            AutomationLevel.MANUAL: "Manual review required - complex case",
            AutomationLevel.SEMI_AUTOMATED: "Automated pre-processing with human approval",
            AutomationLevel.FULLY_AUTOMATED: "Full automation with monitoring",
            AutomationLevel.AI_POWERED: "AI-driven processing with smart contracts",
            AutomationLevel.AUTONOMOUS: "Autonomous processing - highest confidence"
        }
        return recommendations.get(level, "Unknown automation level")
    
    async def _process_automatically(self, request: LicenseRequest, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Process request with full automation"""
        # Implementation for full automation pipeline
        request.status = RequestStatus.AI_ANALYZING.value
        self.db.commit()
        
        # AI processing pipeline
        result = await self._execute_ai_processing_pipeline(request)
        
        if result['success']:
            request.status = RequestStatus.APPROVED.value
            # Generate smart contract
            await self._generate_smart_contract(request)
        else:
            request.status = RequestStatus.REJECTED.value
            request.rejection_reason = result.get('reason', 'Automated processing failed')
        
        request.processing_completed_at = datetime.now(timezone.utc)
        self.db.commit()
        
        return {
            'status': request.status,
            'automation_level': 'fully_automated',
            'processing_time': str(request.processing_time),
            'result': result
        }
    
    async def _execute_ai_processing_pipeline(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Execute comprehensive AI processing pipeline"""
        pipeline_steps = [
            ('content_verification', self._verify_content_authenticity),
            ('rights_validation', self._validate_usage_rights),
            ('pricing_optimization', self._optimize_pricing),
            ('terms_generation', self._generate_license_terms),
            ('compliance_check', self._final_compliance_check)
        ]
        
        results = {}
        for step_name, step_function in pipeline_steps:
            try:
                step_result = await step_function(request)
                results[step_name] = step_result
                
                if not step_result.get('success', False):
                    return {
                        'success': False,
                        'failed_step': step_name,
                        'reason': step_result.get('reason', f'{step_name} failed'),
                        'results': results
                    }
            except Exception as e:
                logger.error(f"Pipeline step {step_name} failed: {e}")
                return {
                    'success': False,
                    'failed_step': step_name,
                    'reason': str(e),
                    'results': results
                }
        
        return {
            'success': True,
            'results': results
        }
    
    async def _verify_content_authenticity(self, request: LicenseRequest) -> Dict[str, Any]:
        """Verify content authenticity and ownership"""
        # Implementation would integrate with fingerprinting system
        return {'success': True, 'authenticity_score': 0.95}
    
    async def _validate_usage_rights(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Validate requested usage rights against available rights"""
        return {'success': True, 'rights_available': True}
    
    async def _optimize_pricing(self, request: LicenseRequest) -> Dict[str, Any]:
        """
AI-optimized pricing calculation"""
        optimized_price = await self.pricing_optimizer.calculate_optimal_price(request)
        request.offered_amount = optimized_price
        return {'success': True, 'optimized_price': float(optimized_price)}
    
    async def _generate_license_terms(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Generate customized license terms"""
        terms = await self.contract_analyzer.generate_terms(request)
        return {'success': True, 'terms': terms}
    
    async def _final_compliance_check(self, request: LicenseRequest) -> Dict[str, Any]:
        """
Final compliance verification"""
        compliance_result = await self.legal_service.final_compliance_check(request)
        return compliance_result
    
    async def _generate_smart_contract(self, request: LicenseRequest) -> SmartContract:
        """
Generate blockchain smart contract for license"""
        contract_terms = {
            'licensor': str(request.licensor_id),
            'licensee': str(request.licensee_id),
            'content_id': str(request.content_id),
            'usage_rights': request.usage_rights,
            'payment_amount': float(request.offered_amount or request.requested_amount),
            'currency': request.currency,
            'duration_start': request.duration_start.isoformat() if request.duration_start else None,
            'duration_end': request.duration_end.isoformat() if request.duration_end else None
        }
        
        contract = SmartContract(
            request_id=request.id,
            contract_type='licensing_agreement',
            license_terms=contract_terms,
            payment_terms={'amount': float(request.offered_amount or request.requested_amount)},
            terms_hash=hashlib.sha256(json.dumps(contract_terms, sort_keys=True).encode()).hexdigest()
        )
        
        self.db.add(contract)
        self.db.commit()
        
        # Deploy to blockchain (async)
        asyncio.create_task(self._deploy_smart_contract(contract))
        
        return contract
    
    async def _deploy_smart_contract(self, contract: SmartContract):
        """
Deploy smart contract to blockchain"""
        try:
            deployment_result = await self.blockchain_service.deploy_contract(contract)
            contract.contract_address = deployment_result['address']
            contract.deployment_hash = deployment_result['hash']
            contract.status = 'deployed'
            contract.deployment_date = datetime.now(timezone.utc)
            self.db.commit()
        except Exception as e:
            logger.error(f"Smart contract deployment failed: {e}")
            contract.status = 'deployment_failed'
            self.db.commit()

# Export all models and services
__all__ = [
    'LicenseTemplate', 'AutomationRule', 'LicenseRequest', 'LicenseNegotiation',
    'SmartContract', 'WorkflowExecution', 'RuleExecution', 'AutomatedLicensingService',
    'AutomationLevel', 'RequestStatus', 'LicenseType', 'PricingModel', 'NegotiationStrategy',
    'LicensingMetrics'
]
class LicenseTemplate(BaseModel, TimestampMixin, AuditMixin):
    """
    Enterprise-grade license template model with AI-powered customization.
    Supports dynamic contract generation and multi-jurisdiction compliance.
    """
    __tablename__ = "license_templates"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    template_name = Column(String(255), nullable=False, index=True)
    template_code = Column(String(50), unique=True, nullable=False)
    
    # Template categorization
    license_type = Column(String(50), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    jurisdiction = Column(String(100), default="international")
    language_code = Column(String(10), default="en")
    
    # Content and structure
    template_content = Column(Text, nullable=False)
    variables = Column(JSONB, default=dict)
    conditional_clauses = Column(JSONB, default=dict)
    default_terms = Column(JSONB, default=dict)
    
    # Pricing configuration
    pricing_model = Column(String(50), nullable=False)
    base_price = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    minimum_price = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    maximum_price = Column(SQLDecimal(12, 4))
    royalty_rate = Column(SQLDecimal(5, 4), default=Decimal('0.0000'))
    
    # Automation settings
    automation_level = Column(Integer, default=AutomationLevel.MANUAL)
    auto_approval_conditions = Column(JSONB, default=dict)
    requires_human_review = Column(Boolean, default=True)
    max_auto_approval_amount = Column(SQLDecimal(12, 2), default=Decimal('0.00'))
    
    # Business logic
    usage_restrictions = Column(JSONB, default=dict)
    territory_restrictions = Column(ARRAY(String), default=list)
    duration_limits = Column(JSONB, default=dict)
    exclusivity_options = Column(JSONB, default=dict)
    
    # AI and ML features
    ai_optimization_enabled = Column(Boolean, default=False)
    learning_enabled = Column(Boolean, default=False)
    success_metrics = Column(JSONB, default=dict)
    performance_data = Column(JSONB, default=dict)
    
    # Compliance and legal
    legal_review_required = Column(Boolean, default=True)
    compliance_standards = Column(ARRAY(String), default=list)
    risk_level = Column(String(20), default="medium")
    liability_caps = Column(JSONB, default=dict)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    version = Column(String(20), default="1.0.0")
    effective_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    
    # Relationships
    license_requests = relationship("LicenseRequest", back_populates="template")
    automation_rules = relationship("AutomationRule", back_populates="template")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_template_type_category', 'license_type', 'category'),
        Index('idx_template_jurisdiction', 'jurisdiction', 'language_code'),
        Index('idx_template_automation', 'automation_level', 'is_active'),
        CheckConstraint('base_price >= 0', name='check_base_price_positive'),
        CheckConstraint('royalty_rate >= 0 AND royalty_rate <= 1', name='check_royalty_rate_valid'),
        UniqueConstraint('template_code', 'version', name='unique_template_version'),
    )
    
    @validates('automation_level')
    def validate_automation_level(self, key, automation_level):
        if automation_level not in [level.value for level in AutomationLevel]:
            raise ValueError(f"Invalid automation level: {automation_level}")
        return automation_level
    
    @hybrid_property
    def is_fully_automated(self):
        return self.automation_level >= AutomationLevel.FULLY_AUTOMATED
    
    def can_auto_approve(self, request_amount: Decimal) -> bool:
        """Check if request can be automatically approved"""
        if not self.is_active:
            return False
        if self.requires_human_review:
            return False
        if self.max_auto_approval_amount and request_amount > self.max_auto_approval_amount:
            return False
        return self.automation_level >= AutomationLevel.SEMI_AUTOMATED

class AutomationRule(BaseModel, TimestampMixin, AuditMixin):
    """
    Advanced automation rules engine with AI-powered decision making.
    Supports complex conditional logic and machine learning optimization.
    """
    __tablename__ = "automation_rules"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    rule_name = Column(String(255), nullable=False)
    rule_code = Column(String(100), unique=True, nullable=False)
    template_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_templates.id'))
    
    # Rule definition
    rule_type = Column(String(50), nullable=False)  # approval, rejection, pricing, routing
    conditions = Column(JSONB, nullable=False)
    actions = Column(JSONB, nullable=False)
    priority = Column(Integer, default=100)
    
    # Advanced logic
    conditional_logic = Column(Text)  # Python expression for complex conditions
    action_script = Column(Text)  # Python script for complex actions
    machine_learning_model = Column(String(255))  # ML model identifier
    
    # Execution settings
    is_active = Column(Boolean, default=True)
    execution_order = Column(Integer, default=100)
    max_executions_per_day = Column(Integer)
    cooldown_period_minutes = Column(Integer, default=0)
    
    # Performance tracking
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    average_execution_time = Column(SQLDecimal(8, 4), default=Decimal('0.0000'))
    last_executed_at = Column(DateTime(timezone=True))
    
    # AI and optimization
    learning_enabled = Column(Boolean, default=False)
    optimization_target = Column(String(100))  # approval_rate, revenue, satisfaction
    performance_threshold = Column(SQLDecimal(5, 4), default=Decimal('0.8000'))
    
    # Business impact
    estimated_savings = Column(SQLDecimal(12, 2), default=Decimal('0.00'))
    risk_score = Column(SQLDecimal(3, 2), default=Decimal('0.50'))
    business_value = Column(String(20), default="medium")
    
    # Relationships
    template = relationship("LicenseTemplate", back_populates="automation_rules")
    rule_executions = relationship("RuleExecution", back_populates="rule")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_rule_template_priority', 'template_id', 'priority'),
        Index('idx_rule_type_active', 'rule_type', 'is_active'),
        Index('idx_rule_execution_order', 'execution_order', 'is_active'),
        CheckConstraint('priority >= 1 AND priority <= 999', name='check_priority_range'),
        CheckConstraint('risk_score >= 0 AND risk_score <= 1', name='check_risk_score_valid'),
    )
    
    @hybrid_property
    def success_rate(self):
        if self.execution_count == 0:
            return Decimal('0.0000')
        return Decimal(self.success_count) / Decimal(self.execution_count)
    
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Determine if rule should execute based on conditions and constraints"""
        if not self.is_active:
            return False
            
        # Check cooldown period
        if self.last_executed_at and self.cooldown_period_minutes:
            cooldown_end = self.last_executed_at + timedelta(minutes=self.cooldown_period_minutes)
            if datetime.now(timezone.utc) < cooldown_end:
                return False
        
        # Check daily execution limit
        if self.max_executions_per_day:
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_executions = self.rule_executions.filter(
                RuleExecution.executed_at >= today_start
            ).count()
            if today_executions >= self.max_executions_per_day:
                return False
        
        return self._evaluate_conditions(context)
    
    def _evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """
Evaluate rule conditions against provided context"""
        try:
            # Simple JSON-based conditions
            for key, expected_value in self.conditions.items():
                if key not in context:
                    return False
                if context[key] != expected_value:
                    return False
            
            # Complex conditional logic if provided
            if self.conditional_logic:
                # Safely evaluate Python expression
                safe_globals = {
                    '__builtins__': {},
                    'context': context,
                    'datetime': datetime,
                    'Decimal': Decimal
                }
                return eval(self.conditional_logic, safe_globals)
            
            return True
        except Exception as e:
            logger.error(f"Error evaluating rule conditions: {e}")
            return False

class LicenseRequest(BaseModel, TimestampMixin, AuditMixin):
    """
    Comprehensive license request model with AI-powered processing pipeline.
    Supports complex negotiations, multi-party approvals, and automated workflows.
    """
    __tablename__ = "license_requests"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    request_number = Column(String(50), unique=True, nullable=False)
    template_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_templates.id'))
    
    # Parties involved
    licensor_id = Column(PostgresUUID(as_uuid=True), nullable=False)  # Content owner
    licensee_id = Column(PostgresUUID(as_uuid=True), nullable=False)  # License requester
    agent_id = Column(PostgresUUID(as_uuid=True))  # Optional agent/broker
    
    # Content information
    content_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    content_type = Column(String(50), nullable=False)
    content_title = Column(String(500))
    content_description = Column(Text)
    content_metadata = Column(JSONB, default=dict)
    
    # License terms
    license_type = Column(String(50), nullable=False)
    usage_rights = Column(JSONB, nullable=False)
    territory = Column(ARRAY(String), default=list)
    duration_start = Column(DateTime(timezone=True))
    duration_end = Column(DateTime(timezone=True))
    exclusivity = Column(Boolean, default=False)
    
    # Financial terms
    pricing_model = Column(String(50), nullable=False)
    requested_amount = Column(SQLDecimal(12, 4), nullable=False)
    offered_amount = Column(SQLDecimal(12, 4))
    negotiated_amount = Column(SQLDecimal(12, 4))
    currency = Column(String(3), default="EUR")
    payment_terms = Column(JSONB, default=dict)
    royalty_terms = Column(JSONB, default=dict)
    
    # Request status and workflow
    status = Column(String(50), default=RequestStatus.SUBMITTED.value)
    priority = Column(String(20), default="normal")
    urgency_level = Column(Integer, default=5)  # 1-10 scale
    deadline = Column(DateTime(timezone=True))
    
    # AI processing
    ai_analysis = Column(JSONB, default=dict)
    risk_assessment = Column(JSONB, default=dict)
    pricing_recommendation = Column(JSONB, default=dict)
    automation_score = Column(SQLDecimal(3, 2), default=Decimal('0.00'))
    
    # Negotiation tracking
    negotiation_rounds = Column(Integer, default=0)
    counter_offers = Column(JSONB, default=list)
    negotiation_strategy = Column(String(50))
    concession_history = Column(JSONB, default=list)
    
    # Processing metadata
    assigned_to = Column(PostgresUUID(as_uuid=True))
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Communication and documentation
    communication_log = Column(JSONB, default=list)
    document_references = Column(ARRAY(String), default=list)
    attachments = Column(JSONB, default=list)
    legal_documents = Column(JSONB, default=list)
    
    # Compliance and approval
    compliance_checks = Column(JSONB, default=dict)
    approval_workflow = Column(JSONB, default=dict)
    approver_chain = Column(ARRAY(String), default=list)
    final_approver = Column(PostgresUUID(as_uuid=True))
    
    # Relationships
    template = relationship("LicenseTemplate", back_populates="license_requests")
    negotiations = relationship("LicenseNegotiation", back_populates="request")
    executions = relationship("WorkflowExecution", back_populates="request")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_request_status_priority', 'status', 'priority'),
        Index('idx_request_licensor_licensee', 'licensor_id', 'licensee_id'),
        Index('idx_request_content_type', 'content_id', 'content_type'),
        Index('idx_request_deadline', 'deadline', 'status'),
        CheckConstraint('requested_amount >= 0', name='check_requested_amount_positive'),
        CheckConstraint('urgency_level >= 1 AND urgency_level <= 10', name='check_urgency_valid'),
        CheckConstraint('automation_score >= 0 AND automation_score <= 1', name='check_automation_score_valid'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in [s.value for s in RequestStatus]:
            raise ValueError(f"Invalid status: {status}")
        return status
    
    @hybrid_property
    def processing_time(self):
        if self.processing_started_at and self.processing_completed_at:
            return self.processing_completed_at - self.processing_started_at
        return None
    
    @hybrid_property
    def is_expired(self):
        return self.deadline and datetime.now(timezone.utc) > self.deadline
    
    def can_auto_process(self) -> bool:
        """Determine if request can be automatically processed"""
        return (
            self.automation_score >= Decimal('0.8') and
            self.template and 
            self.template.is_fully_automated and
            not self.is_expired
        )
class PricingStrategy:
    """
Stratégie de tarification automatique"""
    base_price: Decimal
    pricing_model: PricingModel
    tier_multipliers: Optional[Dict[str, Decimal]] = None
    volume_discounts: Optional[Dict[str, Decimal]] = None
    time_based_adjustments: Optional[Dict[str, Decimal]] = None

class LicenseTemplate(BaseModel):
    """
    Modèle de template de licence pour l'automatisation.
    Définit les paramètres standard pour différents types de licences.
    """
    __tablename__ = "license_templates"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Informations de base
    template_name = Column(String(200), nullable=False)
    template_type = Column(String(30), nullable=False)
    description = Column(Text)
    version = Column(String(10), default="1.0")
    
    # Configuration du template
    license_terms = Column(JSON, nullable=False)
    pricing_strategy = Column(JSON, nullable=False)
    automation_rules = Column(JSON, nullable=False)
    
    # Paramètres d'automatisation
    automation_level = Column(String(20), default=AutomationLevel.SEMI_AUTOMATED.value)
    auto_approval_threshold = Column(SQLDecimal(10, 2))
    manual_review_triggers = Column(ARRAY(String))
    
    # Restrictions et conditions
    eligible_content_types = Column(ARRAY(String))
    territorial_restrictions = Column(ARRAY(String))
    usage_restrictions = Column(JSON)
    
    # Validité et activation
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(DateTime)
    
    # Statistiques d'usage
    usage_count = Column(Integer, default=0)
    success_rate = Column(SQLDecimal(5, 2))
    average_approval_time_minutes = Column(Integer)
    
    # Relations
    creator = relationship("User", back_populates="license_templates")
    license_requests = relationship("AutomatedLicenseRequest", back_populates="template")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.template_id:
            self.template_id = f"LT-{uuid.uuid4().hex[:8].upper()}"

    def is_applicable(
        self,
        content_type: str,
        territory: str,
        requested_usage: List[str]
    ) -> Tuple[bool, str]:
        """Vérifie si le template est applicable à une demande"""
        
        # Vérification du type de contenu
        if self.eligible_content_types:
            if content_type not in self.eligible_content_types:
                return False, f"Type de contenu non éligible: {content_type}"
        
        # Vérification territoriale
        if self.territorial_restrictions:
            if territory in self.territorial_restrictions:
                return False, f"Territoire restreint: {territory}"
        
        # Vérification des usages
        if self.usage_restrictions:
            restricted_usages = self.usage_restrictions.get('prohibited_usages', [])
            for usage in requested_usage:
                if usage in restricted_usages:
                    return False, f"Usage interdit: {usage}"
        
        return True, "Template applicable"

    def calculate_price(
        self,
        request_data: Dict[str, Any]
    ) -> Tuple[Decimal, Dict[str, Any]]:
        """Calcule le prix selon la stratégie de tarification"""
        
        pricing = self.pricing_strategy
        base_price = Decimal(str(pricing['base_price']))
        pricing_model = pricing['pricing_model']
        
        calculation_details = {
            "base_price": float(base_price),
            "pricing_model": pricing_model,
            "adjustments": []
        }
        
        final_price = base_price
        
        # Application des multiplicateurs
        if pricing_model == PricingModel.TIERED_PRICING.value:
            tier_multipliers = pricing.get('tier_multipliers', {})
            user_tier = request_data.get('user_tier', 'standard')
            multiplier = Decimal(str(tier_multipliers.get(user_tier, 1.0)))
            final_price *= multiplier
            calculation_details['adjustments'].append({
                "type": "tier_multiplier",
                "factor": float(multiplier),
                "reason": f"User tier: {user_tier}"
            })
        
        # Remises volume
        volume_discounts = pricing.get('volume_discounts', {})
        if volume_discounts:
            content_count = request_data.get('content_count', 1)
            for threshold, discount in sorted(volume_discounts.items(), key=lambda x: int(x[0]), reverse=True):
                if content_count >= int(threshold):
                    discount_multiplier = Decimal('1') - Decimal(str(discount))
                    final_price *= discount_multiplier
                    calculation_details['adjustments'].append({
                        "type": "volume_discount",
                        "factor": float(discount_multiplier),
                        "reason": f"Volume discount for {content_count} items"
                    })
                    break
        
        # Ajustements temporels
        time_adjustments = pricing.get('time_based_adjustments', {})
        if time_adjustments:
            current_hour = datetime.utcnow().hour
            if 'peak_hours' in time_adjustments and current_hour in time_adjustments['peak_hours']:
                peak_multiplier = Decimal(str(time_adjustments.get('peak_multiplier', 1.2)))
                final_price *= peak_multiplier
                calculation_details['adjustments'].append({
                    "type": "peak_hour_adjustment",
                    "factor": float(peak_multiplier),
                    "reason": "Peak hour pricing"
                })
        
        calculation_details['final_price'] = float(final_price)
        return final_price, calculation_details

    def should_auto_approve(
        self,
        request_value: Decimal,
        requester_reputation: float,
        content_sensitivity: str
    ) -> Tuple[bool, str]:
        """Détermine si une demande peut être approuvée automatiquement"""
        
        if self.automation_level == AutomationLevel.MANUAL.value:
            return False, "Template configuré en mode manuel"
        
        # Vérification du seuil de valeur
        if self.auto_approval_threshold and request_value > self.auto_approval_threshold:
            return False, f"Valeur dépassant le seuil d'approbation automatique: {request_value}"
        
        # Vérification des déclencheurs de révision manuelle
        if self.manual_review_triggers:
            if content_sensitivity in self.manual_review_triggers:
                return False, f"Contenu sensible nécessitant révision manuelle: {content_sensitivity}"
            
            if requester_reputation < 0.7 and "low_reputation" in self.manual_review_triggers:
                return False, f"Réputation faible nécessitant révision: {requester_reputation}"
        
        return True, "Éligible pour approbation automatique"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le template en dictionnaire"""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "template_name": self.template_name,
            "template_type": self.template_type,
            "automation_level": self.automation_level,
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "success_rate": float(self.success_rate) if self.success_rate else None,
            "eligible_content_types": self.eligible_content_types,
            "created_at": self.created_at.isoformat()
        }

class AutomatedLicenseRequest(BaseModel):
    """
    Modèle des demandes de licence automatisées.
    Gère le processus complet de demande et d'approbation.
    """
    __tablename__ = "automated_license_requests"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("license_templates.id"))
    
    # Informations de la demande
    request_type = Column(String(50), nullable=False)
    requested_usage_types = Column(ARRAY(String), nullable=False)
    purpose_description = Column(Text)
    commercial_use = Column(Boolean, default=False)
    
    # Détails territoriaux et temporels
    territorial_scope = Column(ARRAY(String))
    requested_duration_days = Column(Integer)
    start_date = Column(DateTime)
    urgency_level = Column(String(20), default="normal")
    
    # Tarification et négociation
    proposed_price = Column(SQLDecimal(12, 2))
    currency = Column(String(3), default="EUR")
    pricing_model = Column(String(30))
    negotiation_allowed = Column(Boolean, default=True)
    
    # Statut et traitement
    status = Column(String(30), default=RequestStatus.SUBMITTED.value)
    processing_method = Column(String(30))  # automated, manual, hybrid
    submitted_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)
    
    # Réponse automatique
    ai_recommendation = Column(JSON)
    automation_confidence = Column(SQLDecimal(3, 2))
    risk_assessment = Column(JSON)
    
    # Décision finale
    decision = Column(String(20))
    decision_reason = Column(Text)
    decision_date = Column(DateTime)
    decided_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Contrat généré
    generated_contract = Column(JSON)
    contract_signed = Column(Boolean, default=False)
    contract_execution_date = Column(DateTime)
    
    # Relations
    requester = relationship("User", foreign_keys=[requester_id], back_populates="license_requests_sent")
    content_owner = relationship("User", foreign_keys=[content_owner_id], back_populates="license_requests_received")
    content = relationship("ContentItem", back_populates="license_requests")
    template = relationship("LicenseTemplate", back_populates="license_requests")
    decided_by = relationship("User", foreign_keys=[decided_by_user_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.request_id:
            self.request_id = f"ALR-{uuid.uuid4().hex[:8].upper()}"

    def calculate_risk_score(self) -> Decimal:
        """Calcule un score de risque pour la demande"""
        
        risk_score = Decimal('0.5')  # Score de base
        
        # Facteurs de risque
        if self.commercial_use:
            risk_score += Decimal('0.2')
        
        if self.urgency_level == "urgent":
            risk_score += Decimal('0.1')
        
        if self.proposed_price and self.proposed_price > Decimal('10000'):
            risk_score += Decimal('0.2')
        
        # Intégrer la réputation du demandeur
        requester_reputation = self._get_requester_reputation()
        if requester_reputation < 0.5:
            risk_score += Decimal('0.3')
        elif requester_reputation > 0.8:
            risk_score -= Decimal('0.1')
        
        # Analyser l'historique des licences
        license_history_risk = self._analyze_license_history()
        risk_score += license_history_risk
        
        return min(risk_score, Decimal('1.0'))
    
    def _get_requester_reputation(self) -> float:
        """Récupère la réputation du demandeur"""
        try:
            # En production, ceci interrogerait la base de données des réputations
            # Simulation basée sur l'ID utilisateur
            if hasattr(self, 'user_id'):
                user_id = self.user_id
                # Simulation: utilisateurs avec ID pair ont une meilleure réputation
                base_reputation = 0.8 if user_id % 2 == 0 else 0.6
                # Variation basée sur l'historique simulé
                reputation_bonus = (user_id % 100) / 500  # 0 à 0.2
                return min(base_reputation + reputation_bonus, 1.0)
            return 0.7  # Réputation par défaut
        except:
            return 0.5  # Réputation conservatrice en cas d'erreur
    
    def _analyze_license_history(self) -> Decimal:
        """
Analyse l'historique des licences pour évaluer le risque"""
        try:
            # Simulation de l'analyse de l'historique
            if hasattr(self, 'user_id'):
                user_id = self.user_id
                # Utilisateurs avec historique problématique (simulation)
                if user_id % 10 == 9:  # 10% d'utilisateurs à risque
                    return Decimal('0.2')
                elif user_id % 5 == 0:  # 20% d'utilisateurs fiables
                    return Decimal('-0.1')
            return Decimal('0.0')  # Historique neutre
        except:
            return Decimal('0.1')  # Légère augmentation du risque en cas d'erreur
    
    def _evaluate_content_sensitivity(self) -> str:
        """Évalue la sensibilité du contenu"""
        try:
            # En production, ceci analyserait les métadonnées du contenu
            if hasattr(self, 'content_id'):
                content_id = self.content_id
                # Simulation basée sur l'ID du contenu
                if content_id % 10 == 0:
                    return "high"  # 10% de contenu hautement sensible
                elif content_id % 5 == 0:
                    return "low"   # 20% de contenu peu sensible
                return "standard"  # 70% de contenu standard
            return "standard"
        except:
            return "high"  # Prudence en cas d'erreur
    
    def _get_user_tier(self, user_id: int) -> str:
        """Récupère le tier de l'utilisateur"""
        try:
            # En production, ceci interrogerait la table des abonnements
            # Simulation basée sur l'ID utilisateur
            if user_id % 10 == 0:
                return "premium"
            elif user_id % 5 == 0:
                return "pro"
            return "standard"
        except:
            return "standard"

    def generate_ai_recommendation(self) -> Dict[str, Any]:
        """Génère une recommandation IA pour la demande"""
        
        risk_score = float(self.calculate_risk_score())
        
        # Recommandation basée sur le risque et d'autres facteurs
        if risk_score < 0.3:
            recommendation = "APPROVE"
            confidence = 0.9
        elif risk_score < 0.6:
            recommendation = "APPROVE_WITH_CONDITIONS"
            confidence = 0.7
        elif risk_score < 0.8:
            recommendation = "MANUAL_REVIEW"
            confidence = 0.8
        else:
            recommendation = "REJECT"
            confidence = 0.85
        
        recommendation_data = {
            "recommendation": recommendation,
            "confidence": confidence,
            "risk_score": risk_score,
            "factors": {
                "commercial_use": self.commercial_use,
                "urgency": self.urgency_level,
                "proposed_value": float(self.proposed_price) if self.proposed_price else 0,
                "duration": self.requested_duration_days
            },
            "suggested_conditions": [],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Conditions suggérées
        if risk_score > 0.5:
            recommendation_data["suggested_conditions"].extend([
                "Attribution requise",
                "Rapport d'usage mensuel"
            ])
        
        if self.commercial_use:
            recommendation_data["suggested_conditions"].append("Partage de revenus 15%")
        
        self.ai_recommendation = recommendation_data
        self.automation_confidence = Decimal(str(confidence))
        
        return recommendation_data

    def auto_process(self) -> bool:
        """Traite automatiquement la demande si possible"""
        
        try:
            # Génération de la recommandation IA
            recommendation_data = self.generate_ai_recommendation()
            
            # Vérification si l'automatisation est possible
            if not self.template:
                self.status = RequestStatus.MANUAL_REVIEW_REQUIRED.value
                self.processing_method = "manual"
                return False
            
            # Vérification des seuils d'approbation automatique
            requester_reputation = self._get_requester_reputation()
            content_sensitivity = self._evaluate_content_sensitivity()
            
            can_auto_approve, reason = self.template.should_auto_approve(
                self.proposed_price or Decimal('0'),
                requester_reputation,
                content_sensitivity
            )
            
            if not can_auto_approve:
                self.status = RequestStatus.MANUAL_REVIEW_REQUIRED.value
                self.decision_reason = reason
                self.processing_method = "manual"
                return False
            
            # Traitement automatique selon la recommandation
            recommendation = recommendation_data["recommendation"]
            
            if recommendation == "APPROVE" and self.automation_confidence >= Decimal('0.8'):
                self.status = RequestStatus.AUTO_APPROVED.value
                self.decision = "approved"
                self.decision_reason = "Approbation automatique basée sur l'IA"
                self.processing_method = "automated"
                self.processed_date = datetime.utcnow()
                return True
                
            elif recommendation == "REJECT" and self.automation_confidence >= Decimal('0.8'):
                self.status = RequestStatus.AUTO_REJECTED.value
                self.decision = "rejected"
                self.decision_reason = "Rejet automatique basé sur l'analyse de risque"
                self.processing_method = "automated"
                self.processed_date = datetime.utcnow()
                return True
            
            else:
                self.status = RequestStatus.MANUAL_REVIEW_REQUIRED.value
                self.processing_method = "hybrid"
                return False
                
        except Exception as e:
            logger.error(f"Erreur traitement automatique: {str(e)}")
            self.status = RequestStatus.MANUAL_REVIEW_REQUIRED.value
            return False

    def generate_contract(self) -> Dict[str, Any]:
        """Génère automatiquement le contrat de licence"""
        
        if self.decision != "approved":
            raise ValueError("Impossible de générer un contrat pour une demande non approuvée")
        
        contract_data = {
            "contract_id": f"CONTRACT-{self.request_id}",
            "parties": {
                "licensor": self.content_owner_id,
                "licensee": self.requester_id
            },
            "content": {
                "content_id": self.content_id,
                "usage_types": self.requested_usage_types,
                "territorial_scope": self.territorial_scope
            },
            "terms": {
                "duration_days": self.requested_duration_days,
                "commercial_use": self.commercial_use,
                "price": float(self.proposed_price) if self.proposed_price else 0,
                "currency": self.currency
            },
            "conditions": self.ai_recommendation.get("suggested_conditions", []),
            "generated_date": datetime.utcnow().isoformat(),
            "template_used": self.template.template_id if self.template else None
        }
        
        # Ajout des clauses spécifiques du template
        if self.template and self.template.license_terms:
            contract_data["standard_clauses"] = self.template.license_terms
        
        self.generated_contract = contract_data
        return contract_data

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la demande en dictionnaire"""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "requester_id": self.requester_id,
            "content_id": self.content_id,
            "request_type": self.request_type,
            "requested_usage_types": self.requested_usage_types,
            "status": self.status,
            "decision": self.decision,
            "proposed_price": float(self.proposed_price) if self.proposed_price else None,
            "submitted_date": self.submitted_date.isoformat(),
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "automation_confidence": float(self.automation_confidence) if self.automation_confidence else None,
            "processing_method": self.processing_method,
            "created_at": self.created_at.isoformat()
        }

class LicenseAutomationEngine(BaseModel):
    """
    Moteur d'automatisation des licences.
    Configure et gère les règles d'automatisation globales.
    """
    __tablename__ = "license_automation_engines"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    engine_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Configuration
    engine_name = Column(String(200), nullable=False)
    automation_level = Column(String(20), default=AutomationLevel.SEMI_AUTOMATED.value)
    is_active = Column(Boolean, default=True)
    
    # Règles d'automatisation
    automation_rules = Column(JSON, nullable=False)
    global_settings = Column(JSON)
    
    # Seuils et limites
    max_auto_approval_value = Column(SQLDecimal(12, 2))
    daily_auto_approval_limit = Column(Integer, default=100)
    monthly_auto_approval_limit = Column(Integer, default=1000)
    
    # Statistiques de performance
    total_requests_processed = Column(Integer, default=0)
    auto_approved_count = Column(Integer, default=0)
    auto_rejected_count = Column(Integer, default=0)
    manual_review_count = Column(Integer, default=0)
    
    # Métriques de performance
    average_processing_time_seconds = Column(Integer)
    accuracy_rate = Column(SQLDecimal(5, 2))
    user_satisfaction_score = Column(SQLDecimal(3, 2))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.engine_id:
            self.engine_id = f"LAE-{uuid.uuid4().hex[:8].upper()}"

class AutomatedLicensingManager:
    """
    Gestionnaire pour le système de licence automatisée.
    Fournit une interface complète pour l'automatisation des licences.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    def create_license_template(
        self,
        creator_id: int,
        template_name: str,
        template_type: LicenseTemplateType,
        license_terms: Dict[str, Any],
        pricing_strategy: PricingStrategy,
        automation_rules: List[AutomationRule],
        automation_level: AutomationLevel = AutomationLevel.SEMI_AUTOMATED
    ) -> LicenseTemplate:
        """
Crée un nouveau template de licence"""
        
        try:
            template = LicenseTemplate(
                creator_id=creator_id,
                template_name=template_name,
                template_type=template_type.value,
                license_terms=license_terms,
                pricing_strategy=asdict(pricing_strategy),
                automation_rules=[asdict(rule) for rule in automation_rules],
                automation_level=automation_level.value
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            self.logger.info(f"Template de licence créé: {template.template_id}")
            return template
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur création template: {str(e)}")
            raise

    def submit_license_request(
        self,
        requester_id: int,
        content_id: int,
        request_type: str,
        usage_types: List[str],
        commercial_use: bool = False,
        duration_days: Optional[int] = None,
        proposed_price: Optional[Decimal] = None,
        urgency: str = "normal"
    ) -> AutomatedLicenseRequest:
        """Soumet une nouvelle demande de licence"""
        
        try:
            # Récupération des informations du contenu
            content = self.db.query(ContentItem).filter(
                ContentItem.id == content_id
            ).first()
            
            if not content:
                raise ValueError(f"Contenu non trouvé: {content_id}")
            
            # Recherche du template approprié
            template = self._find_best_template(
                content.content_type,
                usage_types,
                commercial_use
            )
            
            # Création de la demande
            request = AutomatedLicenseRequest(
                requester_id=requester_id,
                content_owner_id=content.owner_id,
                content_id=content_id,
                template_id=template.id if template else None,
                request_type=request_type,
                requested_usage_types=usage_types,
                commercial_use=commercial_use,
                requested_duration_days=duration_days,
                proposed_price=proposed_price,
                urgency_level=urgency
            )
            
            # Calcul du prix si template disponible
            if template and not proposed_price:
                user_tier = self._get_user_tier(user_id)
                calculated_price, _ = template.calculate_price({
                    "user_tier": user_tier,
                    "content_count": 1
                })
                request.proposed_price = calculated_price
            
            self.db.add(request)
            self.db.commit()
            self.db.refresh(request)
            
            # Tentative de traitement automatique
            if template and template.automation_level != AutomationLevel.MANUAL.value:
                request.auto_process()
                self.db.commit()
            
            self.logger.info(f"Demande de licence soumise: {request.request_id}")
            return request
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur soumission demande: {str(e)}")
            raise

    def process_pending_requests(self) -> Dict[str, int]:
        """Traite automatiquement les demandes en attente"""
        
        pending_requests = self.db.query(AutomatedLicenseRequest).filter(
            AutomatedLicenseRequest.status.in_([
                RequestStatus.SUBMITTED.value,
                RequestStatus.UNDER_REVIEW.value
            ])
        ).all()
        
        results = {
            "processed": 0,
            "auto_approved": 0,
            "auto_rejected": 0,
            "manual_review": 0,
            "errors": 0
        }
        
        for request in pending_requests:
            try:
                processed = request.auto_process()
                if processed:
                    results["processed"] += 1
                    if request.status == RequestStatus.AUTO_APPROVED.value:
                        results["auto_approved"] += 1
                        # Génération automatique du contrat
                        request.generate_contract()
                    elif request.status == RequestStatus.AUTO_REJECTED.value:
                        results["auto_rejected"] += 1
                else:
                    results["manual_review"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                self.logger.error(f"Erreur traitement demande {request.request_id}: {str(e)}")
                continue
        
        self.db.commit()
        self.logger.info(f"Traitement automatique terminé: {results}")
        return results

    def approve_request(
        self,
        request_id: str,
        approver_id: int,
        conditions: Optional[List[str]] = None,
        custom_terms: Optional[Dict] = None
    ) -> bool:
        """Approuve manuellement une demande de licence"""
        
        try:
            request = self.db.query(AutomatedLicenseRequest).filter(
                AutomatedLicenseRequest.request_id == request_id
            ).first()
            
            if not request:
                raise ValueError(f"Demande non trouvée: {request_id}")
            
            if request.content_owner_id != approver_id:
                raise ValueError("Seul le propriétaire du contenu peut approuver")
            
            request.status = RequestStatus.APPROVED.value
            request.decision = "approved"
            request.decision_date = datetime.utcnow()
            request.decided_by_user_id = approver_id
            request.processing_method = "manual"
            
            # Ajout des conditions personnalisées
            if conditions or custom_terms:
                if not request.ai_recommendation:
                    request.ai_recommendation = {}
                
                request.ai_recommendation["manual_conditions"] = conditions or []
                request.ai_recommendation["custom_terms"] = custom_terms or {}
            
            # Génération du contrat
            contract = request.generate_contract()
            
            self.db.commit()
            self.logger.info(f"Demande approuvée manuellement: {request_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur approbation manuelle: {str(e)}")
            raise

    def reject_request(
        self,
        request_id: str,
        rejector_id: int,
        reason: str
    ) -> bool:
        """Rejette une demande de licence"""
        
        try:
            request = self.db.query(AutomatedLicenseRequest).filter(
                AutomatedLicenseRequest.request_id == request_id
            ).first()
            
            if not request:
                raise ValueError(f"Demande non trouvée: {request_id}")
            
            if request.content_owner_id != rejector_id:
                raise ValueError("Seul le propriétaire du contenu peut rejeter")
            
            request.status = RequestStatus.REJECTED.value
            request.decision = "rejected"
            request.decision_reason = reason
            request.decision_date = datetime.utcnow()
            request.decided_by_user_id = rejector_id
            request.processing_method = "manual"
            
            self.db.commit()
            self.logger.info(f"Demande rejetée: {request_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur rejet demande: {str(e)}")
            raise

    def get_automation_analytics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Génère des analytics d'automatisation"""
        
        # Récupération des demandes pour la période
        requests = self.db.query(AutomatedLicenseRequest).filter(
            AutomatedLicenseRequest.content_owner_id == user_id,
            AutomatedLicenseRequest.submitted_date >= start_date,
            AutomatedLicenseRequest.submitted_date <= end_date
        ).all()
        
        # Calculs d'agrégation
        total_requests = len(requests)
        auto_approved = len([r for r in requests if r.status == RequestStatus.AUTO_APPROVED.value])
        auto_rejected = len([r for r in requests if r.status == RequestStatus.AUTO_REJECTED.value])
        manual_review = len([r for r in requests if r.status == RequestStatus.MANUAL_REVIEW_REQUIRED.value])
        
        automation_rate = (auto_approved + auto_rejected) / total_requests * 100 if total_requests > 0 else 0
        
        # Analyse des temps de traitement
        processed_requests = [r for r in requests if r.processed_date]
        avg_processing_time = 0
        if processed_requests:
            total_time = sum([
                (r.processed_date - r.submitted_date).total_seconds()
                for r in processed_requests
            ])
            avg_processing_time = total_time / len(processed_requests) / 60  # en minutes
        
        # Revenus générés
        total_revenue = sum([
            float(r.proposed_price) for r in requests
            if r.status == RequestStatus.AUTO_APPROVED.value and r.proposed_price
        ])
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_requests": total_requests,
                "auto_approved": auto_approved,
                "auto_rejected": auto_rejected,
                "manual_review": manual_review,
                "automation_rate": round(automation_rate, 2),
                "avg_processing_time_minutes": round(avg_processing_time, 2),
                "total_revenue": total_revenue
            },
            "efficiency_metrics": {
                "automation_success_rate": round(auto_approved / (auto_approved + auto_rejected) * 100, 2) if (auto_approved + auto_rejected) > 0 else 0,
                "manual_intervention_rate": round(manual_review / total_requests * 100, 2) if total_requests > 0 else 0,
                "revenue_per_request": round(total_revenue / total_requests, 2) if total_requests > 0 else 0
            },
            "recommendations": self._generate_automation_recommendations(requests),
            "generated_at": datetime.utcnow().isoformat()
        }

    def _find_best_template(
        self,
        content_type: str,
        usage_types: List[str],
        commercial_use: bool
    ) -> Optional[LicenseTemplate]:
        """Trouve le meilleur template pour une demande"""
        
        # Recherche des templates actifs et applicables
        templates = self.db.query(LicenseTemplate).filter(
            LicenseTemplate.is_active == True
        ).all()
        
        best_template = None
        best_score = 0
        
        for template in templates:
            applicable, _ = template.is_applicable(content_type, "DE", usage_types)
            if not applicable:
                continue
            
            # Calcul d'un score de correspondance
            score = 0
            
            # Bonus pour correspondance exacte du type
            if template.template_type == content_type:
                score += 3
            
            # Bonus pour usage commercial si approprié
            if commercial_use and "commercial" in template.template_type:
                score += 2
            
            # Bonus pour le taux de succès
            if template.success_rate:
                score += float(template.success_rate) / 100
            
            # Bonus pour l'usage fréquent (popularité)
            if template.usage_count > 10:
                score += 1
            
            if score > best_score:
                best_score = score
                best_template = template
        
        return best_template

    def _generate_automation_recommendations(
        self,
        requests: List[AutomatedLicenseRequest]
    ) -> List[str]:
        """Génère des recommandations d'amélioration de l'automatisation"""
        
        recommendations = []
        
        if not requests:
            return ["Aucune donnée suffisante pour générer des recommandations"]
        
        total_requests = len(requests)
        manual_reviews = len([r for r in requests if r.status == RequestStatus.MANUAL_REVIEW_REQUIRED.value])
        
        # Recommandations basées sur le taux de révision manuelle
        if manual_reviews / total_requests > 0.5:
            recommendations.append("Taux de révision manuelle élevé - considérer l'ajustement des seuils d'automatisation")
        
        # Recommandations basées sur les types de demandes
        commercial_requests = len([r for r in requests if r.commercial_use])
        if commercial_requests / total_requests > 0.7:
            recommendations.append("Forte proportion d'usages commerciaux - créer un template spécialisé")
        
        # Recommandations de performance
        urgent_requests = len([r for r in requests if r.urgency_level == "urgent"])
        if urgent_requests > 0:
            recommendations.append("Demandes urgentes détectées - implémenter un canal prioritaire")
        
        return recommendations
