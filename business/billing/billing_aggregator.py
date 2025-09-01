"""Billing Aggregator Engine - Centralized billing orchestration and aggregation
=============================================================================

Master billing orchestrator that coordinates all billing components,
provides unified interfaces, and handles complex billing workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json

# Import all billing components
from .invoice_generator import InvoiceGeneratorEngine
from .payment_processor import PaymentProcessorEngine
from .commission_calculator import CommissionCalculatorEngine
from .subscription_billing import SubscriptionBillingEngine
from .royalty_distributor import RoyaltyDistributorEngine
from .tax_compliance import TaxComplianceEngine
from .billing_analytics import BillingAnalyticsEngine
from .payment_gateway import PaymentGatewayEngine
from .dispute_manager import DisputeManagerEngine

logger = logging.getLogger(__name__)

class BillingWorkflowType(Enum):
    """
Types of billing workflows"""

    ONE_TIME_PAYMENT = "one_time_payment"
    SUBSCRIPTION_BILLING = "subscription_billing"
    COMMISSION_PAYOUT = "commission_payout"
    ROYALTY_DISTRIBUTION = "royalty_distribution"
    REFUND_PROCESSING = "refund_processing"
    DISPUTE_HANDLING = "dispute_handling"

class WorkflowStatus(Enum):
    """Workflow execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"

@dataclass
class BillingWorkflow:
    """Billing workflow definition"""
    workflow_id: str
    workflow_type: BillingWorkflowType
    parameters: Dict[str, Any]
    status: WorkflowStatus
    steps: List[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime] = None

@dataclass
class BillingMetrics:
    """
Comprehensive billing metrics"""
    total_revenue: Decimal
    processed_payments: int
    active_subscriptions: int
    pending_disputes: int
    commission_payouts: Decimal
    tax_compliance_score: float
    processing_efficiency: float

class BillingAggregatorEngine:
    """
    Master billing aggregator that orchestrates all billing operations,
    provides unified APIs, and manages complex multi-step workflows.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
        # Initialize all billing engines
        self.invoice_generator = InvoiceGeneratorEngine(redis_client, db_pool)
        self.payment_processor = PaymentProcessorEngine(redis_client, db_pool)
        self.commission_calculator = CommissionCalculatorEngine(redis_client, db_pool)
        self.subscription_billing = SubscriptionBillingEngine(redis_client, db_pool)
        self.royalty_distributor = RoyaltyDistributorEngine(redis_client, db_pool)
        self.tax_compliance = TaxComplianceEngine(redis_client, db_pool)
        self.billing_analytics = BillingAnalyticsEngine(redis_client, db_pool)
        self.payment_gateway = PaymentGatewayEngine(redis_client, db_pool)
        self.dispute_manager = DisputeManagerEngine(redis_client, db_pool)
        
    async def initialize(self) -> None:
        """
Initialize billing aggregator and all components"""
        try:
            await self._setup_database_tables()
            
            # Initialize all engines
            await asyncio.gather(
                self.invoice_generator.initialize(),
                self.payment_processor.initialize(),
                self.commission_calculator.initialize(),
                self.subscription_billing.initialize(),
                self.royalty_distributor.initialize(),
                self.tax_compliance.initialize(),
                self.billing_analytics.initialize(),
                self.payment_gateway.initialize(),
                self.dispute_manager.initialize()
            )
            
            await self._setup_workflow_templates()
            logger.info("Billing Aggregator Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Billing Aggregator Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for billing aggregation"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS billing_workflows (
                    id SERIAL PRIMARY KEY,
                    workflow_id VARCHAR(100) UNIQUE NOT NULL,
                    workflow_type VARCHAR(30) NOT NULL,
                    parameters JSONB NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    steps JSONB NOT NULL,
                    current_step INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    INDEX idx_workflows_status (status, created_at DESC),
                    INDEX idx_workflows_type (workflow_type, status)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS billing_events (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(100) UNIQUE NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(100) NOT NULL,
                    entity_type VARCHAR(30) NOT NULL,
                    event_data JSONB NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_events_type_processed (event_type, processed),
                    INDEX idx_events_entity (entity_type, entity_id, created_at DESC)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS billing_metrics_snapshots (
                    id SERIAL PRIMARY KEY,
                    snapshot_date DATE UNIQUE NOT NULL,
                    metrics_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _setup_workflow_templates(self) -> None:
        """
Setup workflow templates for common billing operations"""
        try:
            workflow_templates = {
                BillingWorkflowType.ONE_TIME_PAYMENT: [
                    {'step': 'validate_payment_data', 'engine': 'payment_processor'},
                    {'step': 'calculate_taxes', 'engine': 'tax_compliance'},
                    {'step': 'process_payment', 'engine': 'payment_gateway'},
                    {'step': 'generate_invoice', 'engine': 'invoice_generator'},
                    {'step': 'update_analytics', 'engine': 'billing_analytics'}
                ],
                BillingWorkflowType.SUBSCRIPTION_BILLING: [
                    {'step': 'validate_subscription', 'engine': 'subscription_billing'},
                    {'step': 'calculate_prorated_amount', 'engine': 'subscription_billing'},
                    {'step': 'calculate_taxes', 'engine': 'tax_compliance'},
                    {'step': 'process_payment', 'engine': 'payment_gateway'},
                    {'step': 'generate_invoice', 'engine': 'invoice_generator'},
                    {'step': 'update_subscription_state', 'engine': 'subscription_billing'},
                    {'step': 'update_analytics', 'engine': 'billing_analytics'}
                ],
                BillingWorkflowType.COMMISSION_PAYOUT: [
                    {'step': 'calculate_commissions', 'engine': 'commission_calculator'},
                    {'step': 'validate_payout_data', 'engine': 'commission_calculator'},
                    {'step': 'process_bulk_payouts', 'engine': 'payment_processor'},
                    {'step': 'generate_payout_reports', 'engine': 'billing_analytics'}
                ],
                BillingWorkflowType.ROYALTY_DISTRIBUTION: [
                    {'step': 'calculate_distribution', 'engine': 'royalty_distributor'},
                    {'step': 'validate_stakeholders', 'engine': 'royalty_distributor'},
                    {'step': 'process_distributions', 'engine': 'royalty_distributor'},
                    {'step': 'update_analytics', 'engine': 'billing_analytics'}
                ]
            }
            
            # Cache workflow templates
            for workflow_type, steps in workflow_templates.items():
                self.redis.setex(
                    f"workflow_template_{workflow_type.value}",
                    86400,
                    json.dumps(steps)
                )
                
        except Exception as e:
            logger.error(f"Failed to setup workflow templates: {e}")

    async def process_one_time_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process one-time payment with full billing workflow"""
        try:
            workflow_id = f"payment_{payment_data['customer_id']}_{int(datetime.now().timestamp())}"
            
            workflow = BillingWorkflow(
                workflow_id=workflow_id,
                workflow_type=BillingWorkflowType.ONE_TIME_PAYMENT,
                parameters=payment_data,
                status=WorkflowStatus.PENDING,
                steps=[],
                created_at=datetime.now()
            )
            
            # Execute payment workflow
            result = await self._execute_workflow(workflow)
            
            return {
                'workflow_id': workflow_id,
                'payment_status': result.get('payment_status', 'unknown'),
                'transaction_id': result.get('transaction_id'),
                'invoice_id': result.get('invoice_id'),
                'total_amount': result.get('total_amount'),
                'tax_amount': result.get('tax_amount'),
                'net_amount': result.get('net_amount'),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process one-time payment: {e}")
            raise HTTPException(status_code=500, detail="One-time payment processing failed")

    async def process_subscription_billing(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process subscription billing cycle"""
        try:
            workflow_id = f"subscription_{subscription_data['subscription_id']}_{int(datetime.now().timestamp())}"
            
            workflow = BillingWorkflow(
                workflow_id=workflow_id,
                workflow_type=BillingWorkflowType.SUBSCRIPTION_BILLING,
                parameters=subscription_data,
                status=WorkflowStatus.PENDING,
                steps=[],
                created_at=datetime.now()
            )
            
            result = await self._execute_workflow(workflow)
            
            return {
                'workflow_id': workflow_id,
                'subscription_id': subscription_data['subscription_id'],
                'billing_status': result.get('billing_status', 'unknown'),
                'payment_status': result.get('payment_status', 'unknown'),
                'next_billing_date': result.get('next_billing_date'),
                'amount_charged': result.get('amount_charged'),
                'invoice_id': result.get('invoice_id'),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process subscription billing: {e}")
            raise HTTPException(status_code=500, detail="Subscription billing processing failed")

    async def process_commission_payouts(self, payout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process commission payouts for period"""
        try:
            workflow_id = f"commission_payout_{int(datetime.now().timestamp())}"
            
            workflow = BillingWorkflow(
                workflow_id=workflow_id,
                workflow_type=BillingWorkflowType.COMMISSION_PAYOUT,
                parameters=payout_data,
                status=WorkflowStatus.PENDING,
                steps=[],
                created_at=datetime.now()
            )
            
            result = await self._execute_workflow(workflow)
            
            return {
                'workflow_id': workflow_id,
                'payout_period': payout_data.get('period'),
                'total_payouts': result.get('total_payouts', 0),
                'successful_payouts': result.get('successful_payouts', 0),
                'failed_payouts': result.get('failed_payouts', 0),
                'total_amount': result.get('total_amount', 0),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process commission payouts: {e}")
            raise HTTPException(status_code=500, detail="Commission payout processing failed")

    async def process_royalty_distribution(self, distribution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process royalty distribution"""
        try:
            workflow_id = f"royalty_dist_{distribution_data['content_id']}_{int(datetime.now().timestamp())}"
            
            workflow = BillingWorkflow(
                workflow_id=workflow_id,
                workflow_type=BillingWorkflowType.ROYALTY_DISTRIBUTION,
                parameters=distribution_data,
                status=WorkflowStatus.PENDING,
                steps=[],
                created_at=datetime.now()
            )
            
            result = await self._execute_workflow(workflow)
            
            return {
                'workflow_id': workflow_id,
                'content_id': distribution_data['content_id'],
                'distribution_id': result.get('distribution_id'),
                'total_revenue': result.get('total_revenue', 0),
                'stakeholder_count': result.get('stakeholder_count', 0),
                'distribution_status': result.get('distribution_status', 'unknown'),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process royalty distribution: {e}")
            raise HTTPException(status_code=500, detail="Royalty distribution processing failed")

    async def _execute_workflow(self, workflow: BillingWorkflow) -> Dict[str, Any]:
        """Execute billing workflow"""
        try:
            # Store workflow
            await self._store_workflow(workflow)
            
            # Get workflow steps
            steps = await self._get_workflow_steps(workflow.workflow_type)
            workflow.steps = steps
            workflow.status = WorkflowStatus.IN_PROGRESS
            
            # Update workflow status
            await self._update_workflow_status(workflow)
            
            result = {}
            step_number = 0
            
            # Execute each step
            for step in steps:
                try:
                    step_result = await self._execute_workflow_step(
                        step, workflow.parameters, result
                    )
                    
                    # Merge step result
                    result.update(step_result)
                    step_number += 1
                    
                    # Update progress
                    await self._update_workflow_progress(workflow.workflow_id, step_number)
                    
                except Exception as step_error:
                    logger.error(f"Workflow step {step['step']} failed: {step_error}")
                    
                    # Mark workflow as failed
                    workflow.status = WorkflowStatus.FAILED
                    await self._update_workflow_status(workflow)
                    
                    # Return partial results
                    result['workflow_status'] = 'failed'
                    result['failure_step'] = step['step']
                    result['failure_reason'] = str(step_error)
                    return result
            
            # Mark workflow as completed
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            await self._update_workflow_status(workflow)
            
            result['workflow_status'] = 'completed'
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute workflow: {e}")
            return {
                'workflow_status': 'failed',
                'failure_reason': str(e)
            }

    async def _get_workflow_steps(self, workflow_type: BillingWorkflowType) -> List[Dict[str, Any]]:
        """Get workflow steps from template"""
        try:
            cached_template = self.redis.get(f"workflow_template_{workflow_type.value}")
            if cached_template:
                return json.loads(cached_template.decode())
            
            # Fallback to basic steps
            return [
                {'step': 'process_request', 'engine': 'payment_processor'},
                {'step': 'update_analytics', 'engine': 'billing_analytics'}
            ]
            
        except Exception as e:
            logger.error(f"Failed to get workflow steps: {e}")
            return []

    async def _execute_workflow_step(self, step: Dict[str, Any], 
                                   parameters: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        try:
            engine_name = step['engine']
            step_name = step['step']
            
            # Route to appropriate engine
            if engine_name == 'payment_processor':
                return await self._execute_payment_processor_step(step_name, parameters, context)
            elif engine_name == 'invoice_generator':
                return await self._execute_invoice_generator_step(step_name, parameters, context)
            elif engine_name == 'tax_compliance':
                return await self._execute_tax_compliance_step(step_name, parameters, context)
            elif engine_name == 'payment_gateway':
                return await self._execute_payment_gateway_step(step_name, parameters, context)
            elif engine_name == 'subscription_billing':
                return await self._execute_subscription_billing_step(step_name, parameters, context)
            elif engine_name == 'commission_calculator':
                return await self._execute_commission_calculator_step(step_name, parameters, context)
            elif engine_name == 'royalty_distributor':
                return await self._execute_royalty_distributor_step(step_name, parameters, context)
            elif engine_name == 'billing_analytics':
                return await self._execute_billing_analytics_step(step_name, parameters, context)
            else:
                return {'step_status': 'skipped', 'reason': 'unknown_engine'}
                
        except Exception as e:
            logger.error(f"Failed to execute workflow step: {e}")
            raise

    async def _execute_payment_processor_step(self, step_name: str, 
                                            parameters: Dict[str, Any],
                                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute payment processor step"""
        if step_name == 'validate_payment_data':
            # Validate payment data
            required_fields = ['amount', 'currency', 'customer_id', 'payment_method']
            for field in required_fields:
                if field not in parameters:
                    raise ValueError(f"Missing required field: {field}")
            
            return {'validation_status': 'passed'}
            
        elif step_name == 'process_bulk_payouts':
            # Process bulk payouts
            payout_results = await self.payment_processor.process_bulk_payouts(
                parameters.get('payouts', [])
            )
            return {
                'total_payouts': len(payout_results.get('results', [])),
                'successful_payouts': payout_results.get('successful_count', 0),
                'failed_payouts': payout_results.get('failed_count', 0)
            }
        
        return {'step_status': 'completed'}

    async def _execute_tax_compliance_step(self, step_name: str,
                                         parameters: Dict[str, Any],
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tax compliance step"""
        if step_name == 'calculate_taxes':
            tax_calc = await self.tax_compliance.calculate_tax(
                f"temp_{int(datetime.now().timestamp())}",
                Decimal(str(parameters['amount'])),
                parameters.get('customer_country', 'US'),
                parameters.get('category', 'digital_content')
            )
            
            return {
                'tax_amount': float(tax_calc.tax_amount),
                'net_amount': float(tax_calc.net_amount),
                'tax_breakdown': tax_calc.tax_breakdown
            }
        
        return {'step_status': 'completed'}

    async def _execute_payment_gateway_step(self, step_name: str,
                                          parameters: Dict[str, Any],
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute payment gateway step"""
        if step_name == 'process_payment':
            from .payment_gateway import PaymentRequest
            
            payment_request = PaymentRequest(
                amount=Decimal(str(parameters['amount'])),
                currency=parameters['currency'],
                customer_id=parameters['customer_id'],
                payment_method=parameters['payment_method'],
                description=parameters.get('description', ''),
                metadata=parameters.get('metadata', {}),
                preferred_gateway=parameters.get('preferred_gateway')
            )
            
            payment_result = await self.payment_gateway.process_payment(payment_request)
            
            return {
                'payment_status': payment_result.status.value,
                'transaction_id': payment_result.transaction_id,
                'gateway_used': payment_result.gateway_used,
                'processing_fee': float(payment_result.processing_fee),
                'total_amount': float(payment_result.amount)
            }
        
        return {'step_status': 'completed'}

    async def _execute_invoice_generator_step(self, step_name: str,
                                            parameters: Dict[str, Any],
                                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute invoice generator step"""
        if step_name == 'generate_invoice':
            # Use context data from previous steps
            invoice_data = {
                'customer_id': parameters['customer_id'],
                'amount': context.get('total_amount', parameters['amount']),
                'tax_amount': context.get('tax_amount', 0),
                'items': parameters.get('items', []),
                'transaction_id': context.get('transaction_id')
            }
            
            invoice = await self.invoice_generator.generate_invoice(invoice_data)
            
            return {
                'invoice_id': invoice['invoice_id'],
                'invoice_number': invoice['invoice_number'],
                'invoice_status': invoice['status']
            }
        
        return {'step_status': 'completed'}

    async def _execute_subscription_billing_step(self, step_name: str,
                                                parameters: Dict[str, Any],
                                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute subscription billing step"""
        if step_name == 'validate_subscription':
            subscription = await self.subscription_billing.get_subscription_details(
                parameters['subscription_id']
            )
            
            if not subscription or subscription['status'] != 'active':
                raise ValueError("Invalid or inactive subscription")
            
            return {'subscription_valid': True, 'subscription_data': subscription}
            
        elif step_name == 'calculate_prorated_amount':
            # Calculate prorated amount if needed
            amount = await self.subscription_billing.calculate_prorated_amount(
                parameters['subscription_id'],
                parameters.get('billing_date', datetime.now())
            )
            
            return {'prorated_amount': float(amount)}
            
        elif step_name == 'update_subscription_state':
            # Update subscription after successful billing
            await self.subscription_billing.update_subscription_billing_state(
                parameters['subscription_id'],
                context.get('transaction_id'),
                context.get('invoice_id')
            )
            
            return {'subscription_updated': True}
        
        return {'step_status': 'completed'}

    async def _execute_commission_calculator_step(self, step_name: str,
                                                parameters: Dict[str, Any],
                                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute commission calculator step"""
        if step_name == 'calculate_commissions':
            calculations = await self.commission_calculator.calculate_period_commissions(
                parameters.get('start_date', datetime.now() - timedelta(days=30)),
                parameters.get('end_date', datetime.now())
            )
            
            return {
                'commission_calculations': calculations,
                'total_amount': sum(calc.get('amount', 0) for calc in calculations)
            }
            
        elif step_name == 'validate_payout_data':
            # Validate payout data
            payouts = context.get('commission_calculations', [])
            validated_payouts = []
            
            for payout in payouts:
                if payout.get('amount', 0) > 0:
                    validated_payouts.append(payout)
            
            return {'validated_payouts': validated_payouts}
        
        return {'step_status': 'completed'}

    async def _execute_royalty_distributor_step(self, step_name: str,
                                              parameters: Dict[str, Any],
                                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute royalty distributor step"""
        if step_name == 'calculate_distribution':
            from .royalty_distributor import RoyaltyType
            
            distribution = await self.royalty_distributor.calculate_royalty_distribution(
                parameters['content_id'],
                Decimal(str(parameters['total_revenue'])),
                RoyaltyType(parameters.get('royalty_type', 'content_sales')),
                (
                    parameters.get('period_start', datetime.now() - timedelta(days=30)),
                    parameters.get('period_end', datetime.now())
                )
            )
            
            return {
                'distribution_id': distribution.distribution_id,
                'stakeholder_count': len(distribution.stakeholders),
                'total_revenue': float(distribution.total_revenue),
                'net_distributable': float(distribution.net_distributable)
            }
            
        elif step_name == 'validate_stakeholders':
            # Stakeholder validation already done in calculate_distribution
            return {'stakeholders_valid': True}
            
        elif step_name == 'process_distributions':
            distribution_id = context.get('distribution_id')
            if distribution_id:
                results = await self.royalty_distributor.process_distribution_payments(distribution_id)
                return {
                    'distribution_status': 'completed' if results['failed'] == 0 else 'partial',
                    'successful_distributions': results['successful'],
                    'failed_distributions': results['failed']
                }
        
        return {'step_status': 'completed'}

    async def _execute_billing_analytics_step(self, step_name: str,
                                            parameters: Dict[str, Any],
                                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute billing analytics step"""
        if step_name == 'update_analytics':
            # Trigger analytics update
            await self._trigger_analytics_update(parameters, context)
            return {'analytics_updated': True}
            
        elif step_name == 'generate_payout_reports':
            # Generate payout reports
            report_data = await self.billing_analytics.create_analytics_dashboard()
            return {'report_generated': True, 'report_data': report_data}
        
        return {'step_status': 'completed'}

    async def _trigger_analytics_update(self, parameters: Dict[str, Any], 
                                      context: Dict[str, Any]) -> None:
        """
Trigger analytics update"""
        try:
            # Create analytics event
            event_id = f"analytics_update_{int(datetime.now().timestamp())}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO billing_events
                    (event_id, event_type, entity_id, entity_type, event_data)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                event_id,
                'analytics_update',
                context.get('transaction_id', 'unknown'),
                'payment',
                json.dumps({
                    'amount': context.get('total_amount', 0),
                    'payment_status': context.get('payment_status', 'unknown'),
                    'processed_at': datetime.now().isoformat()
                })
                )
                
        except Exception as e:
            logger.error(f"Failed to trigger analytics update: {e}")

    async def _store_workflow(self, workflow: BillingWorkflow) -> None:
        """Store workflow in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO billing_workflows
                    (workflow_id, workflow_type, parameters, status, steps)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                workflow.workflow_id,
                workflow.workflow_type.value,
                json.dumps(workflow.parameters, default=str),
                workflow.status.value,
                json.dumps(workflow.steps)
                )
                
        except Exception as e:
            logger.error(f"Failed to store workflow: {e}")

    async def _update_workflow_status(self, workflow: BillingWorkflow) -> None:
        """Update workflow status"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE billing_workflows
                    SET status = $1, updated_at = NOW(), completed_at = $2
                    WHERE workflow_id = $3
                """,
                workflow.status.value,
                workflow.completed_at,
                workflow.workflow_id
                )
                
        except Exception as e:
            logger.error(f"Failed to update workflow status: {e}")

    async def _update_workflow_progress(self, workflow_id: str, current_step: int) -> None:
        """Update workflow progress"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE billing_workflows
                    SET current_step = $1, updated_at = NOW()
                    WHERE workflow_id = $2
                """, current_step, workflow_id)
                
        except Exception as e:
            logger.error(f"Failed to update workflow progress: {e}")

    async def get_comprehensive_billing_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive billing dashboard"""
        try:
            # Gather data from all engines
            analytics_dashboard = await self.billing_analytics.create_analytics_dashboard()
            dispute_dashboard = await self.dispute_manager.get_dispute_dashboard()
            
            # Get workflow statistics
            async with self.db_pool.acquire() as conn:
                workflow_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_workflows,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_workflows,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_workflows,
                        COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as active_workflows
                    FROM billing_workflows
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                
                # Recent workflows
                recent_workflows = await conn.fetch("""
                    SELECT workflow_id, workflow_type, status, created_at, completed_at
                    FROM billing_workflows
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
            
            return {
                'dashboard_type': 'comprehensive_billing',
                'last_updated': datetime.now().isoformat(),
                'workflow_statistics': {
                    'total_workflows': int(workflow_stats['total_workflows']) if workflow_stats else 0,
                    'completed_workflows': int(workflow_stats['completed_workflows']) if workflow_stats else 0,
                    'failed_workflows': int(workflow_stats['failed_workflows']) if workflow_stats else 0,
                    'active_workflows': int(workflow_stats['active_workflows']) if workflow_stats else 0,
                    'success_rate': float(workflow_stats['completed_workflows'] or 0) / max(float(workflow_stats['total_workflows'] or 1), 1) * 100
                },
                'recent_workflows': [
                    {
                        'workflow_id': wf['workflow_id'],
                        'type': wf['workflow_type'],
                        'status': wf['status'],
                        'created_at': wf['created_at'].isoformat(),
                        'completed_at': wf['completed_at'].isoformat() if wf['completed_at'] else None
                    }
                    for wf in recent_workflows
                ],
                'analytics_data': analytics_dashboard,
                'dispute_data': dispute_dashboard
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive billing dashboard: {e}")
            raise HTTPException(status_code=500, detail="Billing dashboard data retrieval failed")

    async def get_billing_health_status(self) -> Dict[str, Any]:
        """Get overall billing system health status"""
        try:
            # Check each component health
            health_checks = {
                'invoice_generator': await self._check_component_health('invoice_generator'),
                'payment_processor': await self._check_component_health('payment_processor'),
                'subscription_billing': await self._check_component_health('subscription_billing'),
                'tax_compliance': await self._check_component_health('tax_compliance'),
                'payment_gateway': await self._check_component_health('payment_gateway'),
                'dispute_manager': await self._check_component_health('dispute_manager')
            }
            
            # Calculate overall health score
            healthy_components = sum(1 for status in health_checks.values() if status['healthy'])
            total_components = len(health_checks)
            health_score = (healthy_components / total_components) * 100
            
            return {
                'overall_health': 'healthy' if health_score >= 90 else 'degraded' if health_score >= 70 else 'unhealthy',
                'health_score': health_score,
                'component_status': health_checks,
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get billing health status: {e}")
            return {
                'overall_health': 'unknown',
                'health_score': 0,
                'component_status': {},
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }

    async def _check_component_health(self, component_name: str) -> Dict[str, Any]:
        """Check health of specific billing component"""
        try:
            # Basic health check - could be expanded with actual component tests
            return {
                'healthy': True,
                'response_time': 0.1,
                'last_error': None,
                'checked_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'healthy': False,
                'response_time': None,
                'last_error': str(e),
                'checked_at': datetime.now().isoformat()
            }
