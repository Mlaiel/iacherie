"""Dunning Management System - Automated failed payment recovery
==============================================================

Advanced dunning management system for handling failed payments
with configurable workflows, escalation rules, and recovery tracking.

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

class DunningStage(Enum):
    """Dunning process stages"""
    SOFT_DECLINE = "soft_decline"
    FIRST_NOTICE = "first_notice"
    SECOND_NOTICE = "second_notice"
    FINAL_NOTICE = "final_notice"
    SUSPENSION = "suspension"
    CANCELLATION = "cancellation"
    RECOVERED = "recovered"

class DunningAction(Enum):
    """Types of dunning actions"""
    EMAIL_REMINDER = "email_reminder"
    SMS_NOTIFICATION = "sms_notification"
    PHONE_CALL = "phone_call"
    PAYMENT_RETRY = "payment_retry"
    ACCOUNT_SUSPENSION = "account_suspension"
    SERVICE_CANCELLATION = "service_cancellation"
    COLLECTION_AGENCY = "collection_agency"

class FailureReason(Enum):
    """Payment failure reasons"""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_CARD = "expired_card"
    DECLINED_CARD = "declined_card"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    LIMIT_EXCEEDED = "limit_exceeded"
    FRAUD_SUSPECTED = "fraud_suspected"
    UNKNOWN = "unknown"

@dataclass
class DunningCase:
    """Dunning case tracking"""
    case_id: str
    customer_id: str
    subscription_id: str
    payment_id: str
    amount: Decimal
    currency: str
    failure_reason: FailureReason
    current_stage: DunningStage
    attempts_count: int
    last_attempt_date: datetime
    next_action_date: datetime
    created_at: datetime
    recovered: bool = False
    
@dataclass
class DunningRule:
    """Dunning escalation rule"""
    rule_id: str
    stage: DunningStage
    days_offset: int
    actions: List[DunningAction]
    retry_payment: bool
    suspend_service: bool
    active: bool = True

@dataclass
class DunningActivity:
    """Dunning activity log"""
    activity_id: str
    case_id: str
    action: DunningAction
    stage: DunningStage
    executed_at: datetime
    success: bool
    details: Dict[str, Any]

class DunningManagementSystem:
    """Advanced dunning management system"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.dunning_rules = {}
        
    async def initialize(self) -> None:
        """Initialize dunning management system"""
        try:
            await self._setup_database_tables()
            await self._load_dunning_rules()
            logger.info("Dunning Management System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Dunning Management System: {e}")
            raise
            
    async def _setup_database_tables(self) -> None:
        """Setup required database tables"""
        async with self.db_pool.acquire() as conn:
            # Dunning cases table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dunning_cases (
                    case_id VARCHAR PRIMARY KEY,
                    customer_id VARCHAR NOT NULL,
                    subscription_id VARCHAR,
                    payment_id VARCHAR NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    failure_reason VARCHAR(50) NOT NULL,
                    current_stage VARCHAR(20) NOT NULL,
                    attempts_count INTEGER DEFAULT 0,
                    last_attempt_date TIMESTAMP,
                    next_action_date TIMESTAMP,
                    recovered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Dunning rules table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dunning_rules (
                    rule_id VARCHAR PRIMARY KEY,
                    stage VARCHAR(20) NOT NULL,
                    days_offset INTEGER NOT NULL,
                    actions JSONB NOT NULL,
                    retry_payment BOOLEAN DEFAULT FALSE,
                    suspend_service BOOLEAN DEFAULT FALSE,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Dunning activities table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS dunning_activities (
                    activity_id VARCHAR PRIMARY KEY,
                    case_id VARCHAR REFERENCES dunning_cases(case_id),
                    action VARCHAR(30) NOT NULL,
                    stage VARCHAR(20) NOT NULL,
                    executed_at TIMESTAMP DEFAULT NOW(),
                    success BOOLEAN DEFAULT FALSE,
                    details JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dunning_cases_customer 
                ON dunning_cases(customer_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dunning_cases_next_action 
                ON dunning_cases(next_action_date)
            """)
            
    async def _load_dunning_rules(self) -> None:
        """Load dunning escalation rules"""
        default_rules = [
            DunningRule(
                rule_id="soft_decline",
                stage=DunningStage.SOFT_DECLINE,
                days_offset=0,
                actions=[DunningAction.EMAIL_REMINDER, DunningAction.PAYMENT_RETRY],
                retry_payment=True,
                suspend_service=False
            ),
            DunningRule(
                rule_id="first_notice",
                stage=DunningStage.FIRST_NOTICE,
                days_offset=3,
                actions=[DunningAction.EMAIL_REMINDER, DunningAction.SMS_NOTIFICATION],
                retry_payment=True,
                suspend_service=False
            ),
            DunningRule(
                rule_id="second_notice",
                stage=DunningStage.SECOND_NOTICE,
                days_offset=7,
                actions=[DunningAction.EMAIL_REMINDER, DunningAction.PAYMENT_RETRY],
                retry_payment=True,
                suspend_service=False
            ),
            DunningRule(
                rule_id="final_notice",
                stage=DunningStage.FINAL_NOTICE,
                days_offset=14,
                actions=[DunningAction.EMAIL_REMINDER, DunningAction.PHONE_CALL],
                retry_payment=True,
                suspend_service=True
            ),
            DunningRule(
                rule_id="suspension",
                stage=DunningStage.SUSPENSION,
                days_offset=21,
                actions=[DunningAction.ACCOUNT_SUSPENSION],
                retry_payment=False,
                suspend_service=True
            ),
            DunningRule(
                rule_id="cancellation",
                stage=DunningStage.CANCELLATION,
                days_offset=30,
                actions=[DunningAction.SERVICE_CANCELLATION],
                retry_payment=False,
                suspend_service=True
            )
        ]
        
        # Store rules in database and memory
        async with self.db_pool.acquire() as conn:
            for rule in default_rules:
                await conn.execute("""
                    INSERT INTO dunning_rules (
                        rule_id, stage, days_offset, actions,
                        retry_payment, suspend_service, active
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (rule_id) DO UPDATE SET
                        days_offset = EXCLUDED.days_offset,
                        actions = EXCLUDED.actions,
                        retry_payment = EXCLUDED.retry_payment,
                        suspend_service = EXCLUDED.suspend_service
                """, 
                rule.rule_id, rule.stage.value, rule.days_offset,
                json.dumps([action.value for action in rule.actions]),
                rule.retry_payment, rule.suspend_service, rule.active
                )
                
                self.dunning_rules[rule.stage] = rule
                
    async def create_dunning_case(
        self,
        customer_id: str,
        payment_id: str,
        amount: Decimal,
        currency: str,
        failure_reason: FailureReason,
        subscription_id: Optional[str] = None
    ) -> DunningCase:
        """Create new dunning case for failed payment"""
        try:
            case_id = f"DUN_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{customer_id[:8]}"
            
            # Determine initial stage based on failure reason
            initial_stage = self._determine_initial_stage(failure_reason)
            
            # Calculate next action date
            rule = self.dunning_rules.get(initial_stage)
            next_action_date = datetime.utcnow() + timedelta(days=rule.days_offset if rule else 0)
            
            case = DunningCase(
                case_id=case_id,
                customer_id=customer_id,
                subscription_id=subscription_id,
                payment_id=payment_id,
                amount=amount,
                currency=currency,
                failure_reason=failure_reason,
                current_stage=initial_stage,
                attempts_count=0,
                last_attempt_date=datetime.utcnow(),
                next_action_date=next_action_date,
                created_at=datetime.utcnow()
            )
            
            # Store case in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO dunning_cases (
                        case_id, customer_id, subscription_id, payment_id,
                        amount, currency, failure_reason, current_stage,
                        attempts_count, last_attempt_date, next_action_date
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, 
                case_id, customer_id, subscription_id, payment_id,
                amount, currency, failure_reason.value, initial_stage.value,
                0, datetime.utcnow(), next_action_date
                )
            
            # Schedule initial actions
            await self._schedule_dunning_actions(case)
            
            logger.info(f"Dunning case created: {case_id}")
            return case
            
        except Exception as e:
            logger.error(f"Failed to create dunning case: {e}")
            raise
            
    def _determine_initial_stage(self, failure_reason: FailureReason) -> DunningStage:
        """Determine initial dunning stage based on failure reason"""
        if failure_reason in [
            FailureReason.NETWORK_ERROR,
            FailureReason.AUTHENTICATION_FAILED
        ]:
            return DunningStage.SOFT_DECLINE
        elif failure_reason in [
            FailureReason.INSUFFICIENT_FUNDS,
            FailureReason.LIMIT_EXCEEDED
        ]:
            return DunningStage.FIRST_NOTICE
        elif failure_reason in [
            FailureReason.EXPIRED_CARD,
            FailureReason.DECLINED_CARD
        ]:
            return DunningStage.FIRST_NOTICE
        else:
            return DunningStage.SOFT_DECLINE
            
    async def _schedule_dunning_actions(self, case: DunningCase) -> None:
        """Schedule dunning actions for case"""
        try:
            rule = self.dunning_rules.get(case.current_stage)
            if not rule:
                return
                
            for action in rule.actions:
                await self._execute_dunning_action(case, action)
                
        except Exception as e:
            logger.error(f"Failed to schedule dunning actions: {e}")
            
    async def _execute_dunning_action(
        self,
        case: DunningCase,
        action: DunningAction
    ) -> DunningActivity:
        """Execute specific dunning action"""
        try:
            activity_id = f"DA_{case.case_id}_{action.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            success = False
            details = {}
            
            if action == DunningAction.EMAIL_REMINDER:
                success, details = await self._send_email_reminder(case)
            elif action == DunningAction.SMS_NOTIFICATION:
                success, details = await self._send_sms_notification(case)
            elif action == DunningAction.PAYMENT_RETRY:
                success, details = await self._retry_payment(case)
            elif action == DunningAction.ACCOUNT_SUSPENSION:
                success, details = await self._suspend_account(case)
            elif action == DunningAction.SERVICE_CANCELLATION:
                success, details = await self._cancel_service(case)
            
            activity = DunningActivity(
                activity_id=activity_id,
                case_id=case.case_id,
                action=action,
                stage=case.current_stage,
                executed_at=datetime.utcnow(),
                success=success,
                details=details
            )
            
            # Store activity
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO dunning_activities (
                        activity_id, case_id, action, stage,
                        executed_at, success, details
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                activity_id, case.case_id, action.value, case.current_stage.value,
                datetime.utcnow(), success, json.dumps(details)
                )
            
            logger.info(f"Executed dunning action {action.value} for case {case.case_id}")
            return activity
            
        except Exception as e:
            logger.error(f"Failed to execute dunning action {action.value}: {e}")
            raise
            
    async def _send_email_reminder(self, case: DunningCase) -> tuple[bool, Dict[str, Any]]:
        """Send email reminder to customer"""
        try:
            # In production, integrate with email service
            # For now, simulate email sending
            
            email_template = self._get_email_template(case.current_stage)
            
            details = {
                "recipient": case.customer_id,
                "template": email_template,
                "amount": float(case.amount),
                "currency": case.currency,
                "stage": case.current_stage.value
            }
            
            # Simulate successful email sending
            logger.info(f"Email reminder sent for case {case.case_id}")
            return True, details
            
        except Exception as e:
            logger.error(f"Failed to send email reminder: {e}")
            return False, {"error": str(e)}
            
    async def _send_sms_notification(self, case: DunningCase) -> tuple[bool, Dict[str, Any]]:
        """Send SMS notification to customer"""
        try:
            # In production, integrate with SMS service
            message = f"Payment failed for ${case.amount}. Please update your payment method."
            
            details = {
                "recipient": case.customer_id,
                "message": message,
                "stage": case.current_stage.value
            }
            
            # Simulate successful SMS sending
            logger.info(f"SMS notification sent for case {case.case_id}")
            return True, details
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
            return False, {"error": str(e)}
            
    async def _retry_payment(self, case: DunningCase) -> tuple[bool, Dict[str, Any]]:
        """Retry failed payment"""
        try:
            # In production, integrate with payment processor
            # For now, simulate payment retry logic
            
            details = {
                "original_payment_id": case.payment_id,
                "amount": float(case.amount),
                "currency": case.currency,
                "retry_attempt": case.attempts_count + 1
            }
            
            # Simulate 30% success rate for retries
            import random
            success = random.random() < 0.3
            
            if success:
                details["new_payment_id"] = f"PAY_RETRY_{case.case_id}"
                await self._mark_case_recovered(case)
                
            logger.info(f"Payment retry {'successful' if success else 'failed'} for case {case.case_id}")
            return success, details
            
        except Exception as e:
            logger.error(f"Failed to retry payment: {e}")
            return False, {"error": str(e)}
            
    async def _suspend_account(self, case: DunningCase) -> tuple[bool, Dict[str, Any]]:
        """Suspend customer account"""
        try:
            # In production, integrate with account management system
            details = {
                "customer_id": case.customer_id,
                "suspension_reason": "payment_failure",
                "amount_owed": float(case.amount)
            }
            
            # Simulate successful account suspension
            logger.info(f"Account suspended for case {case.case_id}")
            return True, details
            
        except Exception as e:
            logger.error(f"Failed to suspend account: {e}")
            return False, {"error": str(e)}
            
    async def _cancel_service(self, case: DunningCase) -> tuple[bool, Dict[str, Any]]:
        """Cancel customer service"""
        try:
            # In production, integrate with subscription management
            details = {
                "customer_id": case.customer_id,
                "subscription_id": case.subscription_id,
                "cancellation_reason": "payment_failure",
                "final_amount": float(case.amount)
            }
            
            # Simulate successful service cancellation
            logger.info(f"Service cancelled for case {case.case_id}")
            return True, details
            
        except Exception as e:
            logger.error(f"Failed to cancel service: {e}")
            return False, {"error": str(e)}
            
    def _get_email_template(self, stage: DunningStage) -> str:
        """Get email template for dunning stage"""
        templates = {
            DunningStage.SOFT_DECLINE: "payment_retry_reminder",
            DunningStage.FIRST_NOTICE: "first_payment_notice",
            DunningStage.SECOND_NOTICE: "second_payment_notice",
            DunningStage.FINAL_NOTICE: "final_payment_notice",
            DunningStage.SUSPENSION: "account_suspension_notice",
            DunningStage.CANCELLATION: "service_cancellation_notice"
        }
        return templates.get(stage, "generic_payment_reminder")
        
    async def _mark_case_recovered(self, case: DunningCase) -> None:
        """Mark dunning case as recovered"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE dunning_cases 
                    SET recovered = TRUE,
                        current_stage = $1,
                        updated_at = NOW()
                    WHERE case_id = $2
                """, DunningStage.RECOVERED.value, case.case_id)
                
            logger.info(f"Dunning case {case.case_id} marked as recovered")
            
        except Exception as e:
            logger.error(f"Failed to mark case as recovered: {e}")
            
    async def process_dunning_queue(self) -> Dict[str, Any]:
        """Process dunning cases ready for next action"""
        try:
            current_time = datetime.utcnow()
            
            # Get cases ready for processing
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM dunning_cases 
                    WHERE recovered = FALSE 
                    AND next_action_date <= $1
                    AND current_stage NOT IN ('cancellation', 'recovered')
                """, current_time)
                
            processed_cases = []
            
            for row in rows:
                case = DunningCase(
                    case_id=row['case_id'],
                    customer_id=row['customer_id'],
                    subscription_id=row['subscription_id'],
                    payment_id=row['payment_id'],
                    amount=row['amount'],
                    currency=row['currency'],
                    failure_reason=FailureReason(row['failure_reason']),
                    current_stage=DunningStage(row['current_stage']),
                    attempts_count=row['attempts_count'],
                    last_attempt_date=row['last_attempt_date'],
                    next_action_date=row['next_action_date'],
                    created_at=row['created_at'],
                    recovered=row['recovered']
                )
                
                # Process case
                await self._process_dunning_case(case)
                processed_cases.append(case.case_id)
                
            logger.info(f"Processed {len(processed_cases)} dunning cases")
            
            return {
                "processed_cases": len(processed_cases),
                "case_ids": processed_cases,
                "processed_at": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process dunning queue: {e}")
            raise
            
    async def _process_dunning_case(self, case: DunningCase) -> None:
        """Process individual dunning case"""
        try:
            # Execute current stage actions
            await self._schedule_dunning_actions(case)
            
            # Escalate to next stage
            next_stage = self._get_next_stage(case.current_stage)
            if next_stage:
                next_rule = self.dunning_rules.get(next_stage)
                next_action_date = datetime.utcnow() + timedelta(
                    days=next_rule.days_offset if next_rule else 7
                )
                
                # Update case
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE dunning_cases 
                        SET current_stage = $1,
                            attempts_count = attempts_count + 1,
                            last_attempt_date = NOW(),
                            next_action_date = $2,
                            updated_at = NOW()
                        WHERE case_id = $3
                    """, next_stage.value, next_action_date, case.case_id)
                    
        except Exception as e:
            logger.error(f"Failed to process dunning case {case.case_id}: {e}")
            
    def _get_next_stage(self, current_stage: DunningStage) -> Optional[DunningStage]:
        """Get next escalation stage"""
        stage_progression = {
            DunningStage.SOFT_DECLINE: DunningStage.FIRST_NOTICE,
            DunningStage.FIRST_NOTICE: DunningStage.SECOND_NOTICE,
            DunningStage.SECOND_NOTICE: DunningStage.FINAL_NOTICE,
            DunningStage.FINAL_NOTICE: DunningStage.SUSPENSION,
            DunningStage.SUSPENSION: DunningStage.CANCELLATION,
            DunningStage.CANCELLATION: None,
            DunningStage.RECOVERED: None
        }
        return stage_progression.get(current_stage)
        
    async def get_dunning_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get dunning management analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Case statistics
                case_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_cases,
                        COUNT(*) FILTER (WHERE recovered = TRUE) as recovered_cases,
                        SUM(amount) as total_amount,
                        SUM(amount) FILTER (WHERE recovered = TRUE) as recovered_amount
                    FROM dunning_cases 
                    WHERE created_at BETWEEN $1 AND $2
                """, start_date, end_date)
                
                # Stage distribution
                stage_distribution = await conn.fetch("""
                    SELECT 
                        current_stage,
                        COUNT(*) as count,
                        SUM(amount) as amount
                    FROM dunning_cases 
                    WHERE created_at BETWEEN $1 AND $2
                    GROUP BY current_stage
                """, start_date, end_date)
                
                # Recovery rate by failure reason
                failure_stats = await conn.fetch("""
                    SELECT 
                        failure_reason,
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE recovered = TRUE) as recovered
                    FROM dunning_cases 
                    WHERE created_at BETWEEN $1 AND $2
                    GROUP BY failure_reason
                """, start_date, end_date)
                
            recovery_rate = (
                float(case_stats['recovered_cases']) / float(case_stats['total_cases'])
                if case_stats['total_cases'] > 0 else 0
            ) * 100
            
            return {
                "summary": {
                    "total_cases": case_stats['total_cases'],
                    "recovered_cases": case_stats['recovered_cases'],
                    "recovery_rate": round(recovery_rate, 2),
                    "total_amount": float(case_stats['total_amount'] or 0),
                    "recovered_amount": float(case_stats['recovered_amount'] or 0)
                },
                "stage_distribution": [
                    {
                        "stage": row['current_stage'],
                        "count": row['count'],
                        "amount": float(row['amount'])
                    } for row in stage_distribution
                ],
                "failure_analysis": [
                    {
                        "reason": row['failure_reason'],
                        "total": row['total'],
                        "recovered": row['recovered'],
                        "recovery_rate": round(
                            (row['recovered'] / row['total']) * 100, 2
                        ) if row['total'] > 0 else 0
                    } for row in failure_stats
                ],
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get dunning analytics: {e}")
            raise