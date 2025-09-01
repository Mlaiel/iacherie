"""Revenue Recognition Engine - Automated accounting compliance system
====================================================================

Advanced revenue recognition system compliant with accounting standards
(ASC 606, IFRS 15) for automated revenue tracking and reporting.

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

class RevenueType(Enum):
    """Types of revenue recognition"""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"
    COMMISSION = "commission"
    LICENSING = "licensing"
    REFUND = "refund"

class RecognitionMethod(Enum):
    """Revenue recognition methods"""
    STRAIGHT_LINE = "straight_line"
    MILESTONE_BASED = "milestone_based"
    USAGE_BASED = "usage_based"
    IMMEDIATE = "immediate"
    DEFERRED = "deferred"

class AccountingStandard(Enum):
    """Supported accounting standards"""
    ASC_606 = "asc_606"
    IFRS_15 = "ifrs_15"
    GAAP = "gaap"

@dataclass
class RevenueContract:
    """Revenue contract details"""
    contract_id: str
    customer_id: str
    start_date: datetime
    end_date: Optional[datetime]
    total_value: Decimal
    currency: str
    performance_obligations: List[Dict[str, Any]]
    accounting_standard: AccountingStandard
    recognition_method: RecognitionMethod
    
@dataclass
class RevenueSchedule:
    """Revenue recognition schedule"""
    schedule_id: str
    contract_id: str
    period_start: datetime
    period_end: datetime
    recognized_amount: Decimal
    deferred_amount: Decimal
    status: str
    created_at: datetime

class RevenueRecognitionEngine:
    """Advanced revenue recognition processing engine"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.recognition_rules = {}
        
    async def initialize(self) -> None:
        """Initialize revenue recognition engine"""
        try:
            await self._setup_database_tables()
            await self._load_recognition_rules()
            logger.info("Revenue Recognition Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Revenue Recognition Engine: {e}")
            raise
            
    async def _setup_database_tables(self) -> None:
        """Setup required database tables"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue_contracts (
                    contract_id VARCHAR PRIMARY KEY,
                    customer_id VARCHAR NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP,
                    total_value DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    performance_obligations JSONB,
                    accounting_standard VARCHAR(20) NOT NULL,
                    recognition_method VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue_schedules (
                    schedule_id VARCHAR PRIMARY KEY,
                    contract_id VARCHAR REFERENCES revenue_contracts(contract_id),
                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,
                    recognized_amount DECIMAL(15,2) NOT NULL,
                    deferred_amount DECIMAL(15,2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue_journal_entries (
                    entry_id VARCHAR PRIMARY KEY,
                    schedule_id VARCHAR REFERENCES revenue_schedules(schedule_id),
                    account_code VARCHAR(20) NOT NULL,
                    debit_amount DECIMAL(15,2) DEFAULT 0,
                    credit_amount DECIMAL(15,2) DEFAULT 0,
                    entry_date TIMESTAMP NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
    async def _load_recognition_rules(self) -> None:
        """Load revenue recognition rules"""
        self.recognition_rules = {
            RevenueType.SUBSCRIPTION: {
                "method": RecognitionMethod.STRAIGHT_LINE,
                "deferral_account": "2400", # Deferred Revenue
                "revenue_account": "4000"   # Revenue
            },
            RevenueType.ONE_TIME: {
                "method": RecognitionMethod.IMMEDIATE,
                "revenue_account": "4000"
            },
            RevenueType.COMMISSION: {
                "method": RecognitionMethod.IMMEDIATE,
                "revenue_account": "4100"   # Commission Revenue
            }
        }
        
    async def create_revenue_contract(
        self,
        customer_id: str,
        total_value: Decimal,
        currency: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        revenue_type: RevenueType = RevenueType.SUBSCRIPTION,
        accounting_standard: AccountingStandard = AccountingStandard.ASC_606
    ) -> RevenueContract:
        """Create new revenue contract"""
        try:
            contract_id = f"RC_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{customer_id[:8]}"
            
            # Determine recognition method based on revenue type
            recognition_method = self.recognition_rules.get(
                revenue_type, {}
            ).get("method", RecognitionMethod.STRAIGHT_LINE)
            
            contract = RevenueContract(
                contract_id=contract_id,
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                total_value=total_value,
                currency=currency,
                performance_obligations=[],
                accounting_standard=accounting_standard,
                recognition_method=recognition_method
            )
            
            # Store contract in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO revenue_contracts (
                        contract_id, customer_id, start_date, end_date,
                        total_value, currency, performance_obligations,
                        accounting_standard, recognition_method
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, 
                contract_id, customer_id, start_date, end_date,
                total_value, currency, json.dumps([]),
                accounting_standard.value, recognition_method.value
                )
            
            # Create revenue schedule
            await self._create_revenue_schedule(contract, revenue_type)
            
            logger.info(f"Revenue contract created: {contract_id}")
            return contract
            
        except Exception as e:
            logger.error(f"Failed to create revenue contract: {e}")
            raise
            
    async def _create_revenue_schedule(
        self, 
        contract: RevenueContract,
        revenue_type: RevenueType
    ) -> List[RevenueSchedule]:
        """Create revenue recognition schedule"""
        try:
            schedules = []
            
            if contract.recognition_method == RecognitionMethod.IMMEDIATE:
                # Recognize revenue immediately
                schedule = RevenueSchedule(
                    schedule_id=f"RS_{contract.contract_id}_001",
                    contract_id=contract.contract_id,
                    period_start=contract.start_date,
                    period_end=contract.start_date,
                    recognized_amount=contract.total_value,
                    deferred_amount=Decimal('0'),
                    status="ready",
                    created_at=datetime.utcnow()
                )
                schedules.append(schedule)
                
            elif contract.recognition_method == RecognitionMethod.STRAIGHT_LINE:
                # Straight-line recognition over contract period
                if contract.end_date:
                    total_days = (contract.end_date - contract.start_date).days
                    daily_amount = contract.total_value / total_days if total_days > 0 else contract.total_value
                    
                    current_date = contract.start_date
                    month_counter = 1
                    
                    while current_date < contract.end_date:
                        period_end = min(
                            current_date.replace(day=1) + timedelta(days=32),
                            contract.end_date
                        ).replace(day=1) - timedelta(days=1)
                        
                        period_days = (period_end - current_date).days + 1
                        period_amount = daily_amount * period_days
                        
                        schedule = RevenueSchedule(
                            schedule_id=f"RS_{contract.contract_id}_{month_counter:03d}",
                            contract_id=contract.contract_id,
                            period_start=current_date,
                            period_end=period_end,
                            recognized_amount=period_amount,
                            deferred_amount=contract.total_value - period_amount,
                            status="scheduled",
                            created_at=datetime.utcnow()
                        )
                        schedules.append(schedule)
                        
                        current_date = period_end + timedelta(days=1)
                        month_counter += 1
            
            # Store schedules in database
            async with self.db_pool.acquire() as conn:
                for schedule in schedules:
                    await conn.execute("""
                        INSERT INTO revenue_schedules (
                            schedule_id, contract_id, period_start, period_end,
                            recognized_amount, deferred_amount, status
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, 
                    schedule.schedule_id, schedule.contract_id,
                    schedule.period_start, schedule.period_end,
                    schedule.recognized_amount, schedule.deferred_amount,
                    schedule.status
                    )
            
            logger.info(f"Created {len(schedules)} revenue schedules for contract {contract.contract_id}")
            return schedules
            
        except Exception as e:
            logger.error(f"Failed to create revenue schedule: {e}")
            raise
            
    async def process_revenue_recognition(self, as_of_date: datetime = None) -> Dict[str, Any]:
        """Process revenue recognition for due schedules"""
        try:
            if not as_of_date:
                as_of_date = datetime.utcnow()
                
            # Get schedules ready for recognition
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM revenue_schedules 
                    WHERE status IN ('scheduled', 'ready') 
                    AND period_start <= $1
                """, as_of_date)
                
            processed_schedules = []
            total_recognized = Decimal('0')
            
            for row in rows:
                schedule = RevenueSchedule(
                    schedule_id=row['schedule_id'],
                    contract_id=row['contract_id'],
                    period_start=row['period_start'],
                    period_end=row['period_end'],
                    recognized_amount=row['recognized_amount'],
                    deferred_amount=row['deferred_amount'],
                    status=row['status'],
                    created_at=row['created_at']
                )
                
                # Create journal entries
                await self._create_journal_entries(schedule)
                
                # Update schedule status
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE revenue_schedules 
                        SET status = 'recognized' 
                        WHERE schedule_id = $1
                    """, schedule.schedule_id)
                
                processed_schedules.append(schedule.schedule_id)
                total_recognized += schedule.recognized_amount
                
            logger.info(f"Processed {len(processed_schedules)} revenue schedules")
            
            return {
                "processed_schedules": len(processed_schedules),
                "total_recognized": float(total_recognized),
                "schedule_ids": processed_schedules,
                "as_of_date": as_of_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process revenue recognition: {e}")
            raise
            
    async def _create_journal_entries(self, schedule: RevenueSchedule) -> None:
        """Create accounting journal entries"""
        try:
            entry_id = f"JE_{schedule.schedule_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            async with self.db_pool.acquire() as conn:
                # Debit: Deferred Revenue (liability decrease)
                await conn.execute("""
                    INSERT INTO revenue_journal_entries (
                        entry_id, schedule_id, account_code, debit_amount,
                        entry_date, description
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                f"{entry_id}_DR", schedule.schedule_id, "2400",
                schedule.recognized_amount, datetime.utcnow(),
                f"Revenue recognition for period {schedule.period_start.date()}"
                )
                
                # Credit: Revenue (income increase)
                await conn.execute("""
                    INSERT INTO revenue_journal_entries (
                        entry_id, schedule_id, account_code, credit_amount,
                        entry_date, description
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """, 
                f"{entry_id}_CR", schedule.schedule_id, "4000",
                schedule.recognized_amount, datetime.utcnow(),
                f"Revenue recognition for period {schedule.period_start.date()}"
                )
                
        except Exception as e:
            logger.error(f"Failed to create journal entries: {e}")
            raise
            
    async def get_revenue_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get revenue recognition analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Recognized revenue
                recognized_result = await conn.fetchrow("""
                    SELECT 
                        SUM(recognized_amount) as total_recognized,
                        COUNT(*) as schedule_count
                    FROM revenue_schedules 
                    WHERE status = 'recognized' 
                    AND period_start BETWEEN $1 AND $2
                """, start_date, end_date)
                
                # Deferred revenue
                deferred_result = await conn.fetchrow("""
                    SELECT SUM(deferred_amount) as total_deferred
                    FROM revenue_schedules 
                    WHERE status IN ('scheduled', 'ready')
                """)
                
                # Revenue by type
                type_breakdown = await conn.fetch("""
                    SELECT 
                        rc.recognition_method,
                        SUM(rs.recognized_amount) as amount,
                        COUNT(*) as count
                    FROM revenue_schedules rs
                    JOIN revenue_contracts rc ON rs.contract_id = rc.contract_id
                    WHERE rs.status = 'recognized'
                    AND rs.period_start BETWEEN $1 AND $2
                    GROUP BY rc.recognition_method
                """, start_date, end_date)
                
            return {
                "total_recognized": float(recognized_result['total_recognized'] or 0),
                "total_deferred": float(deferred_result['total_deferred'] or 0),
                "schedule_count": recognized_result['schedule_count'] or 0,
                "type_breakdown": [
                    {
                        "method": row['recognition_method'],
                        "amount": float(row['amount']),
                        "count": row['count']
                    } for row in type_breakdown
                ],
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {e}")
            raise
            
    async def generate_compliance_report(
        self,
        accounting_standard: AccountingStandard,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report for specified accounting standard"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get contracts for the standard
                contracts = await conn.fetch("""
                    SELECT rc.*, 
                           SUM(rs.recognized_amount) as total_recognized,
                           SUM(rs.deferred_amount) as total_deferred
                    FROM revenue_contracts rc
                    LEFT JOIN revenue_schedules rs ON rc.contract_id = rs.contract_id
                    WHERE rc.accounting_standard = $1
                    AND rs.period_start BETWEEN $2 AND $3
                    GROUP BY rc.contract_id
                """, accounting_standard.value, period_start, period_end)
                
                # Get journal entries
                journal_entries = await conn.fetch("""
                    SELECT je.*, rs.contract_id
                    FROM revenue_journal_entries je
                    JOIN revenue_schedules rs ON je.schedule_id = rs.schedule_id
                    JOIN revenue_contracts rc ON rs.contract_id = rc.contract_id
                    WHERE rc.accounting_standard = $1
                    AND je.entry_date BETWEEN $2 AND $3
                    ORDER BY je.entry_date
                """, accounting_standard.value, period_start, period_end)
                
            return {
                "accounting_standard": accounting_standard.value,
                "period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "contracts": [
                    {
                        "contract_id": contract['contract_id'],
                        "customer_id": contract['customer_id'],
                        "total_value": float(contract['total_value']),
                        "recognized": float(contract['total_recognized'] or 0),
                        "deferred": float(contract['total_deferred'] or 0),
                        "recognition_method": contract['recognition_method']
                    } for contract in contracts
                ],
                "journal_entries": [
                    {
                        "entry_id": entry['entry_id'],
                        "contract_id": entry['contract_id'],
                        "account_code": entry['account_code'],
                        "debit": float(entry['debit_amount'] or 0),
                        "credit": float(entry['credit_amount'] or 0),
                        "date": entry['entry_date'].isoformat(),
                        "description": entry['description']
                    } for entry in journal_entries
                ],
                "summary": {
                    "total_contracts": len(contracts),
                    "total_recognized": sum(float(c['total_recognized'] or 0) for c in contracts),
                    "total_deferred": sum(float(c['total_deferred'] or 0) for c in contracts)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise