"""Dispute Manager Engine - Comprehensive payment dispute management
================================================================

Advanced dispute management system handling chargebacks, disputes,
arbitration, and automated resolution processes.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class DisputeType(Enum):
    """
Types of payment disputes"""

    CHARGEBACK = "chargeback"
    FRAUD = "fraud"
    UNAUTHORIZED = "unauthorized"
    DUPLICATE = "duplicate"
    PRODUCT_NOT_RECEIVED = "product_not_received"
    PRODUCT_DEFECTIVE = "product_defective"
    CANCELLED_RECURRING = "cancelled_recurring"
    GENERAL = "general"

class DisputeStatus(Enum):
    """Dispute resolution status"""

    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    RESPONSE_NEEDED = "response_needed"
    RESPONDED = "responded"
    ESCALATED = "escalated"
    WON = "won"
    LOST = "lost"
    ACCEPTED = "accepted"

class DisputeStage(Enum):
    """Dispute process stages"""

    INQUIRY = "inquiry"
    CHARGEBACK = "chargeback"
    PRE_ARBITRATION = "pre_arbitration"
    ARBITRATION = "arbitration"
    COMPLIANCE = "compliance"

@dataclass
class DisputeData:
    """Dispute information structure"""
    dispute_id: str
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    dispute_type: DisputeType
    status: DisputeStatus
    stage: DisputeStage
    reason_code: str
    description: str
    evidence_required: List[str]
    deadline: datetime
    created_at: datetime

class DisputeManagerEngine:
    """
    Advanced dispute management engine handling all aspects of payment
    disputes including automated evidence collection and response generation.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """
Initialize dispute manager engine"""
        try:
            await self._setup_database_tables()
            await self._setup_dispute_rules()
            await self._setup_automated_responses()
            logger.info("Dispute Manager Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Dispute Manager Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for dispute management"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_disputes (
                    id SERIAL PRIMARY KEY,
                    dispute_id VARCHAR(100) UNIQUE NOT NULL,
                    transaction_id VARCHAR(100) NOT NULL,
                    gateway_dispute_id VARCHAR(255),
                    customer_id VARCHAR(255) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    dispute_type VARCHAR(30) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    stage VARCHAR(20) NOT NULL,
                    reason_code VARCHAR(50),
                    description TEXT,
                    evidence_required JSONB DEFAULT '[]',
                    evidence_submitted JSONB DEFAULT '{}',
                    response_deadline TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    resolved_at TIMESTAMP,
                    INDEX idx_disputes_status (status, created_at DESC),
                    INDEX idx_disputes_customer (customer_id, created_at DESC),
                    INDEX idx_disputes_deadline (response_deadline ASC)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dispute_communications (
                    id SERIAL PRIMARY KEY,
                    dispute_id VARCHAR(100) NOT NULL REFERENCES payment_disputes(dispute_id),
                    communication_type VARCHAR(20) NOT NULL,
                    direction VARCHAR(10) NOT NULL,
                    content TEXT NOT NULL,
                    attachments JSONB DEFAULT '[]',
                    sent_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_comm_dispute (dispute_id, sent_at DESC)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dispute_evidence (
                    id SERIAL PRIMARY KEY,
                    dispute_id VARCHAR(100) NOT NULL REFERENCES payment_disputes(dispute_id),
                    evidence_type VARCHAR(50) NOT NULL,
                    evidence_data JSONB NOT NULL,
                    file_path VARCHAR(500),
                    uploaded_at TIMESTAMP DEFAULT NOW(),
                    is_submitted BOOLEAN DEFAULT FALSE
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dispute_analytics (
                    id SERIAL PRIMARY KEY,
                    dispute_id VARCHAR(100) NOT NULL REFERENCES payment_disputes(dispute_id),
                    win_probability DECIMAL(5,4),
                    risk_score DECIMAL(5,4),
                    recommended_action VARCHAR(50),
                    analysis_data JSONB,
                    analyzed_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _setup_dispute_rules(self) -> None:
        """
Setup dispute handling rules"""
        try:
            # Define evidence requirements by dispute type
            evidence_requirements = {
                DisputeType.FRAUD: [
                    'customer_communication',
                    'delivery_confirmation',
                    'transaction_details',
                    'customer_verification'
                ],
                DisputeType.UNAUTHORIZED: [
                    'authorization_proof',
                    'customer_verification',
                    'transaction_log'
                ],
                DisputeType.PRODUCT_NOT_RECEIVED: [
                    'delivery_confirmation',
                    'tracking_information',
                    'shipping_details'
                ],
                DisputeType.DUPLICATE: [
                    'transaction_comparison',
                    'unique_identifiers',
                    'processing_timestamps'
                ],
                DisputeType.CANCELLED_RECURRING: [
                    'cancellation_request',
                    'subscription_history',
                    'communication_log'
                ]
            }
            
            # Cache evidence requirements
            for dispute_type, requirements in evidence_requirements.items():
                self.redis.setex(
                    f"evidence_req_{dispute_type.value}",
                    3600,
                    json.dumps(requirements)
                )
                
        except Exception as e:
            logger.error(f"Failed to setup dispute rules: {e}")

    async def _setup_automated_responses(self) -> None:
        """Setup automated response templates"""
        try:
            response_templates = {
                'fraud_response': {
                    'subject': 'Fraud Dispute Response',
                    'template': '''
                    We have thoroughly investigated the disputed transaction and found:
                    
                    1. Transaction was authorized by verified payment method
                    2. Customer verification was completed successfully
                    3. Service was delivered as requested
                    
                    Supporting evidence is attached.
                    '''
                },
                'not_received_response': {
                    'subject': 'Product Not Received Dispute Response',
                    'template': '''
                    Our investigation shows:
                    
                    1. Product was delivered to confirmed address
                    2. Delivery confirmation is available
                    3. Customer did not report non-delivery within reasonable timeframe
                    
                    Delivery documentation is provided.
                    '''
                }
            }
            
            # Cache response templates
            for template_name, template_data in response_templates.items():
                self.redis.setex(
                    f"response_template_{template_name}",
                    86400,
                    json.dumps(template_data)
                )
                
        except Exception as e:
            logger.error(f"Failed to setup automated responses: {e}")

    async def create_dispute(self, dispute_data: Dict[str, Any]) -> DisputeData:
        """Create new dispute record"""
        try:
            # Generate dispute ID
            dispute_id = f"disp_{dispute_data['transaction_id']}_{int(datetime.now().timestamp())}"
            
            dispute_type = DisputeType(dispute_data['dispute_type'])
            
            # Get evidence requirements
            evidence_required = await self._get_evidence_requirements(dispute_type)
            
            # Calculate response deadline (typically 7-14 days)
            deadline = datetime.now() + timedelta(days=dispute_data.get('response_days', 10))
            
            # Create dispute record
            dispute = DisputeData(
                dispute_id=dispute_id,
                transaction_id=dispute_data['transaction_id'],
                customer_id=dispute_data['customer_id'],
                amount=Decimal(str(dispute_data['amount'])),
                currency=dispute_data['currency'],
                dispute_type=dispute_type,
                status=DisputeStatus.RECEIVED,
                stage=DisputeStage.INQUIRY,
                reason_code=dispute_data.get('reason_code', ''),
                description=dispute_data.get('description', ''),
                evidence_required=evidence_required,
                deadline=deadline,
                created_at=datetime.now()
            )
            
            # Store in database
            await self._store_dispute(dispute)
            
            # Start automated processing
            asyncio.create_task(self._start_dispute_processing(dispute))
            
            return dispute
            
        except Exception as e:
            logger.error(f"Failed to create dispute: {e}")
            raise HTTPException(status_code=500, detail="Dispute creation failed")

    async def _get_evidence_requirements(self, dispute_type: DisputeType) -> List[str]:
        """Get evidence requirements for dispute type"""
        try:
            cached_requirements = self.redis.get(f"evidence_req_{dispute_type.value}")
            if cached_requirements:
                return json.loads(cached_requirements.decode())
            
            # Default requirements
            return ['transaction_details', 'customer_communication']
            
        except Exception as e:
            logger.error(f"Failed to get evidence requirements: {e}")
            return []

    async def _store_dispute(self, dispute: DisputeData) -> None:
        """Store dispute in database"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO payment_disputes
                    (dispute_id, transaction_id, customer_id, amount, currency,
                     dispute_type, status, stage, reason_code, description,
                     evidence_required, response_deadline)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                dispute.dispute_id,
                dispute.transaction_id,
                dispute.customer_id,
                dispute.amount,
                dispute.currency,
                dispute.dispute_type.value,
                dispute.status.value,
                dispute.stage.value,
                dispute.reason_code,
                dispute.description,
                json.dumps(dispute.evidence_required),
                dispute.deadline
                )
                
        except Exception as e:
            logger.error(f"Failed to store dispute: {e}")

    async def _start_dispute_processing(self, dispute: DisputeData) -> None:
        """Start automated dispute processing"""
        try:
            # Analyze dispute win probability
            await self._analyze_dispute(dispute)
            
            # Collect available evidence
            await self._collect_evidence(dispute)
            
            # Generate automated response if possible
            await self._generate_automated_response(dispute)
            
            # Set up monitoring and alerts
            await self._setup_dispute_monitoring(dispute)
            
        except Exception as e:
            logger.error(f"Failed to start dispute processing: {e}")

    async def _analyze_dispute(self, dispute: DisputeData) -> None:
        """Analyze dispute win probability and risk"""
        try:
            # Get transaction history for customer
            async with self.db_pool.acquire() as conn:
                customer_history = await conn.fetch("""
                    SELECT COUNT(*) as total_transactions,
                           COUNT(CASE WHEN payment_status = 'completed' THEN 1 END) as successful_transactions,
                           AVG(amount) as avg_transaction_amount
                    FROM payments 
                    WHERE customer_id = $1
                    AND created_at >= CURRENT_DATE - INTERVAL '12 months'
                """, dispute.customer_id)
                
                # Previous disputes for customer
                dispute_history = await conn.fetch("""
                    SELECT COUNT(*) as total_disputes,
                           COUNT(CASE WHEN status = 'won' THEN 1 END) as won_disputes,
                           COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_disputes
                    FROM payment_disputes 
                    WHERE customer_id = $1
                """, dispute.customer_id)
                
                # Calculate risk factors
                history_data = customer_history[0] if customer_history else None
                dispute_data = dispute_history[0] if dispute_history else None
                
                # Simple risk scoring algorithm
                risk_score = self._calculate_risk_score(dispute, history_data, dispute_data)
                win_probability = self._calculate_win_probability(dispute, risk_score)
                
                # Store analysis
                await conn.execute("""
                    INSERT INTO dispute_analytics
                    (dispute_id, win_probability, risk_score, recommended_action, analysis_data)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                dispute.dispute_id,
                win_probability,
                risk_score,
                'respond' if win_probability > 0.6 else 'accept',
                json.dumps({
                    'customer_history': dict(history_data) if history_data else {},
                    'dispute_history': dict(dispute_data) if dispute_data else {},
                    'analysis_timestamp': datetime.now().isoformat()
                })
                )
                
        except Exception as e:
            logger.error(f"Failed to analyze dispute: {e}")

    def _calculate_risk_score(self, dispute: DisputeData, 
                            customer_history: Any, dispute_history: Any) -> Decimal:
        """Calculate dispute risk score"""
        risk_score = Decimal('0.5')  # Base risk
        
        # Adjust based on dispute type
        high_risk_types = [DisputeType.FRAUD, DisputeType.UNAUTHORIZED]
        if dispute.dispute_type in high_risk_types:
            risk_score += Decimal('0.2')
        
        # Adjust based on amount
        if dispute.amount > Decimal('1000'):
            risk_score += Decimal('0.1')
        
        # Adjust based on customer history
        if customer_history:
            success_rate = customer_history['successful_transactions'] / max(customer_history['total_transactions'], 1)
            if success_rate < 0.8:
                risk_score += Decimal('0.15')
        
        # Adjust based on dispute history
        if dispute_history and dispute_history['total_disputes'] > 0:
            dispute_rate = dispute_history['total_disputes'] / max(customer_history['total_transactions'] if customer_history else 1, 1)
            if dispute_rate > 0.1:  # More than 10% dispute rate
                risk_score += Decimal('0.2')
        
        return min(risk_score, Decimal('1.0'))

    def _calculate_win_probability(self, dispute: DisputeData, risk_score: Decimal) -> Decimal:
        """
Calculate probability of winning dispute"""
        base_probability = Decimal('0.7')  # Base win rate
        
        # Lower probability for high-risk disputes
        probability = base_probability - (risk_score * Decimal('0.4'))
        
        # Adjust based on dispute type success rates
        type_adjustments = {
            DisputeType.FRAUD: Decimal('-0.1'),
            DisputeType.UNAUTHORIZED: Decimal('-0.15'),
            DisputeType.DUPLICATE: Decimal('0.2'),
            DisputeType.PRODUCT_NOT_RECEIVED: Decimal('0.1')
        }
        
        adjustment = type_adjustments.get(dispute.dispute_type, Decimal('0'))
        probability += adjustment
        
        return max(min(probability, Decimal('0.95')), Decimal('0.05'))

    async def _collect_evidence(self, dispute: DisputeData) -> None:
        """
Collect evidence for dispute response"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get transaction details
                transaction = await conn.fetchrow("""
                    SELECT * FROM payments WHERE transaction_id = $1
                """, dispute.transaction_id)
                
                if transaction:
                    # Store transaction evidence
                    await conn.execute("""
                        INSERT INTO dispute_evidence
                        (dispute_id, evidence_type, evidence_data)
                        VALUES ($1, 'transaction_details', $2)
                    """,
                    dispute.dispute_id,
                    json.dumps({
                        'transaction_id': transaction['transaction_id'],
                        'amount': str(transaction['amount']),
                        'payment_method': transaction['payment_method'],
                        'created_at': transaction['created_at'].isoformat(),
                        'payment_status': transaction['payment_status']
                    })
                    )
                
                # Collect additional evidence based on type
                await self._collect_type_specific_evidence(dispute, conn)
                
        except Exception as e:
            logger.error(f"Failed to collect evidence: {e}")

    async def _collect_type_specific_evidence(self, dispute: DisputeData, conn) -> None:
        """Collect evidence specific to dispute type"""
        try:
            if dispute.dispute_type == DisputeType.PRODUCT_NOT_RECEIVED:
                # Look for delivery confirmations
                delivery_info = await conn.fetchrow("""
                    SELECT delivery_status, tracking_number, delivered_at
                    FROM order_deliveries 
                    WHERE transaction_id = $1
                """, dispute.transaction_id)
                
                if delivery_info:
                    await conn.execute("""
                        INSERT INTO dispute_evidence
                        (dispute_id, evidence_type, evidence_data)
                        VALUES ($1, 'delivery_confirmation', $2)
                    """,
                    dispute.dispute_id,
                    json.dumps(dict(delivery_info))
                    )
            
            elif dispute.dispute_type == DisputeType.FRAUD:
                # Look for customer verification data
                verification = await conn.fetchrow("""
                    SELECT verification_method, verified_at, ip_address
                    FROM customer_verifications 
                    WHERE customer_id = $1
                    AND created_at <= (SELECT created_at FROM payments WHERE transaction_id = $2)
                    ORDER BY created_at DESC
                    LIMIT 1
                """, dispute.customer_id, dispute.transaction_id)
                
                if verification:
                    await conn.execute("""
                        INSERT INTO dispute_evidence
                        (dispute_id, evidence_type, evidence_data)
                        VALUES ($1, 'customer_verification', $2)
                    """,
                    dispute.dispute_id,
                    json.dumps(dict(verification))
                    )
                    
        except Exception as e:
            logger.error(f"Failed to collect type-specific evidence: {e}")

    async def _generate_automated_response(self, dispute: DisputeData) -> None:
        """Generate automated dispute response"""
        try:
            # Get win probability analysis
            async with self.db_pool.acquire() as conn:
                analysis = await conn.fetchrow("""
                    SELECT win_probability, recommended_action
                    FROM dispute_analytics
                    WHERE dispute_id = $1
                """, dispute.dispute_id)
                
                if analysis and analysis['recommended_action'] == 'respond':
                    # Generate response based on dispute type
                    response = await self._create_dispute_response(dispute)
                    
                    if response:
                        # Store response
                        await conn.execute("""
                            INSERT INTO dispute_communications
                            (dispute_id, communication_type, direction, content)
                            VALUES ($1, 'response', 'outgoing', $2)
                        """, dispute.dispute_id, response)
                        
                        # Update dispute status
                        await conn.execute("""
                            UPDATE payment_disputes
                            SET status = 'responded', updated_at = NOW()
                            WHERE dispute_id = $1
                        """, dispute.dispute_id)
                        
        except Exception as e:
            logger.error(f"Failed to generate automated response: {e}")

    async def _create_dispute_response(self, dispute: DisputeData) -> Optional[str]:
        """Create dispute response content"""
        try:
            # Get response template
            template_key = f"{dispute.dispute_type.value}_response"
            cached_template = self.redis.get(f"response_template_{template_key}")
            
            if cached_template:
                template_data = json.loads(cached_template.decode())
                return template_data['template']
            
            # Fallback generic response
            return f"""
            We have reviewed the dispute for transaction {dispute.transaction_id} and found
            that the transaction was processed correctly according to our records.
            
            All supporting evidence has been collected and is attached to this response.
            We respectfully request that this dispute be resolved in our favor.
            """
            
        except Exception as e:
            logger.error(f"Failed to create dispute response: {e}")
            return None

    async def _setup_dispute_monitoring(self, dispute: DisputeData) -> None:
        """Setup monitoring for dispute deadlines"""
        try:
            # Set Redis reminder for deadline
            days_until_deadline = (dispute.deadline - datetime.now()).days
            if days_until_deadline > 1:
                reminder_key = f"dispute_reminder_{dispute.dispute_id}"
                self.redis.setex(reminder_key, (days_until_deadline - 1) * 86400, 
                               json.dumps({'dispute_id': dispute.dispute_id, 'deadline': dispute.deadline.isoformat()}))
                
        except Exception as e:
            logger.error(f"Failed to setup dispute monitoring: {e}")

    async def get_dispute_dashboard(self) -> Dict[str, Any]:
        """Get dispute management dashboard data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Summary statistics
                summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_disputes,
                        COUNT(CASE WHEN status IN ('received', 'under_review', 'response_needed') THEN 1 END) as active_disputes,
                        COUNT(CASE WHEN status = 'won' THEN 1 END) as won_disputes,
                        COUNT(CASE WHEN status = 'lost' THEN 1 END) as lost_disputes,
                        SUM(amount) as total_disputed_amount,
                        AVG(win_probability) as avg_win_probability
                    FROM payment_disputes pd
                    LEFT JOIN dispute_analytics da ON pd.dispute_id = da.dispute_id
                    WHERE pd.created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                
                # Recent disputes
                recent_disputes = await conn.fetch("""
                    SELECT 
                        dispute_id,
                        transaction_id,
                        amount,
                        dispute_type,
                        status,
                        response_deadline,
                        created_at
                    FROM payment_disputes
                    ORDER BY created_at DESC
                    LIMIT 10
                """)
                
                # Dispute type breakdown
                type_breakdown = await conn.fetch("""
                    SELECT 
                        dispute_type,
                        COUNT(*) as count,
                        SUM(amount) as total_amount
                    FROM payment_disputes
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY dispute_type
                    ORDER BY count DESC
                """)
                
                return {
                    'summary': {
                        'total_disputes': int(summary['total_disputes']) if summary else 0,
                        'active_disputes': int(summary['active_disputes']) if summary else 0,
                        'won_disputes': int(summary['won_disputes']) if summary else 0,
                        'lost_disputes': int(summary['lost_disputes']) if summary else 0,
                        'total_disputed_amount': float(summary['total_disputed_amount'] or 0),
                        'win_rate': float(summary['won_disputes'] or 0) / max(float(summary['total_disputes'] or 1), 1) * 100,
                        'avg_win_probability': float(summary['avg_win_probability'] or 0)
                    },
                    'recent_disputes': [
                        {
                            'dispute_id': disp['dispute_id'],
                            'transaction_id': disp['transaction_id'],
                            'amount': float(disp['amount']),
                            'type': disp['dispute_type'],
                            'status': disp['status'],
                            'deadline': disp['response_deadline'].isoformat() if disp['response_deadline'] else None,
                            'created_at': disp['created_at'].isoformat()
                        }
                        for disp in recent_disputes
                    ],
                    'type_breakdown': [
                        {
                            'type': row['dispute_type'],
                            'count': int(row['count']),
                            'amount': float(row['total_amount'])
                        }
                        for row in type_breakdown
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get dispute dashboard: {e}")
            raise HTTPException(status_code=500, detail="Dispute dashboard data retrieval failed")
