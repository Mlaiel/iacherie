"""Financial Reporting Engine - Automated financial reporting with audit trail
===========================================================================

Comprehensive financial reporting system for automated report generation,
audit trail management, and regulatory compliance reporting.

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
import hashlib

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types of financial reports"""
    REVENUE_SUMMARY = "revenue_summary"
    PAYMENT_REPORT = "payment_report"
    SUBSCRIPTION_METRICS = "subscription_metrics"
    TAX_REPORT = "tax_report"
    COMMISSION_REPORT = "commission_report"
    REFUND_REPORT = "refund_report"
    DUNNING_REPORT = "dunning_report"
    AUDIT_TRAIL = "audit_trail"
    COMPLIANCE_REPORT = "compliance_report"
    CASH_FLOW = "cash_flow"

class ReportFrequency(Enum):
    """Report generation frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class ReportFormat(Enum):
    """Report output formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"

class AuditEventType(Enum):
    """Types of audit events"""
    PAYMENT_PROCESSED = "payment_processed"
    REFUND_ISSUED = "refund_issued"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    COMMISSION_PAID = "commission_paid"
    TAX_CALCULATED = "tax_calculated"
    REVENUE_RECOGNIZED = "revenue_recognized"
    DUNNING_INITIATED = "dunning_initiated"
    REPORT_GENERATED = "report_generated"
    DATA_MODIFIED = "data_modified"

@dataclass
class FinancialReport:
    """Financial report metadata"""
    report_id: str
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    generated_by: str
    format: ReportFormat
    file_path: Optional[str]
    checksum: str
    data: Dict[str, Any]
    
@dataclass
class AuditEvent:
    """Audit trail event"""
    event_id: str
    event_type: AuditEventType
    entity_type: str
    entity_id: str
    user_id: Optional[str]
    timestamp: datetime
    changes: Dict[str, Any]
    metadata: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]

@dataclass
class ReportSchedule:
    """Automated report schedule"""
    schedule_id: str
    report_type: ReportType
    frequency: ReportFrequency
    recipients: List[str]
    format: ReportFormat
    active: bool
    last_generated: Optional[datetime]
    next_generation: datetime

class FinancialReportingEngine:
    """Advanced financial reporting and audit system"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.report_templates = {}
        
    async def initialize(self) -> None:
        """Initialize financial reporting engine"""
        try:
            await self._setup_database_tables()
            await self._load_report_templates()
            logger.info("Financial Reporting Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Financial Reporting Engine: {e}")
            raise
            
    async def _setup_database_tables(self) -> None:
        """Setup required database tables"""
        async with self.db_pool.acquire() as conn:
            # Financial reports table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS financial_reports (
                    report_id VARCHAR PRIMARY KEY,
                    report_type VARCHAR(30) NOT NULL,
                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,
                    generated_at TIMESTAMP DEFAULT NOW(),
                    generated_by VARCHAR(100),
                    format VARCHAR(10) NOT NULL,
                    file_path TEXT,
                    checksum VARCHAR(64) NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Audit events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id VARCHAR PRIMARY KEY,
                    event_type VARCHAR(30) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    entity_id VARCHAR(100) NOT NULL,
                    user_id VARCHAR(100),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    changes JSONB,
                    metadata JSONB,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Report schedules table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS report_schedules (
                    schedule_id VARCHAR PRIMARY KEY,
                    report_type VARCHAR(30) NOT NULL,
                    frequency VARCHAR(20) NOT NULL,
                    recipients JSONB NOT NULL,
                    format VARCHAR(10) NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    last_generated TIMESTAMP,
                    next_generation TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_financial_reports_type_period 
                ON financial_reports(report_type, period_start, period_end)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_events_entity 
                ON audit_events(entity_type, entity_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp 
                ON audit_events(timestamp)
            """)
            
    async def _load_report_templates(self) -> None:
        """Load report templates and configurations"""
        self.report_templates = {
            ReportType.REVENUE_SUMMARY: {
                "title": "Revenue Summary Report",
                "sections": [
                    "total_revenue", "revenue_by_source", "revenue_trends",
                    "top_customers", "geographical_breakdown"
                ],
                "data_sources": [
                    "revenue_schedules", "payments", "subscriptions"
                ]
            },
            ReportType.PAYMENT_REPORT: {
                "title": "Payment Processing Report",
                "sections": [
                    "payment_summary", "payment_methods", "success_rates",
                    "failed_payments", "gateway_performance"
                ],
                "data_sources": [
                    "payments", "payment_attempts", "gateways"
                ]
            },
            ReportType.SUBSCRIPTION_METRICS: {
                "title": "Subscription Metrics Report",
                "sections": [
                    "subscription_summary", "churn_analysis", "mrr_trends",
                    "plan_distribution", "retention_metrics"
                ],
                "data_sources": [
                    "subscriptions", "subscription_events", "customers"
                ]
            },
            ReportType.TAX_REPORT: {
                "title": "Tax Compliance Report",
                "sections": [
                    "tax_summary", "jurisdiction_breakdown", "compliance_status",
                    "tax_calculations", "exemptions"
                ],
                "data_sources": [
                    "tax_calculations", "tax_rules", "jurisdictions"
                ]
            }
        }
        
    async def generate_report(
        self,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime,
        format: ReportFormat = ReportFormat.JSON,
        generated_by: Optional[str] = None
    ) -> FinancialReport:
        """Generate financial report"""
        try:
            report_id = f"RPT_{report_type.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Generate report data based on type
            report_data = await self._generate_report_data(
                report_type, period_start, period_end
            )
            
            # Calculate checksum for data integrity
            data_json = json.dumps(report_data, sort_keys=True, default=str)
            checksum = hashlib.sha256(data_json.encode()).hexdigest()
            
            report = FinancialReport(
                report_id=report_id,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                generated_at=datetime.utcnow(),
                generated_by=generated_by or "system",
                format=format,
                file_path=None,
                checksum=checksum,
                data=report_data
            )
            
            # Store report in database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO financial_reports (
                        report_id, report_type, period_start, period_end,
                        generated_by, format, checksum, data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, 
                report_id, report_type.value, period_start, period_end,
                generated_by, format.value, checksum, json.dumps(report_data, default=str)
                )
            
            # Log audit event
            await self.log_audit_event(
                event_type=AuditEventType.REPORT_GENERATED,
                entity_type="financial_report",
                entity_id=report_id,
                user_id=generated_by,
                metadata={
                    "report_type": report_type.value,
                    "period": f"{period_start.date()} to {period_end.date()}",
                    "format": format.value
                }
            )
            
            logger.info(f"Financial report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate financial report: {e}")
            raise
            
    async def _generate_report_data(
        self,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate report data based on report type"""
        
        if report_type == ReportType.REVENUE_SUMMARY:
            return await self._generate_revenue_summary(period_start, period_end)
        elif report_type == ReportType.PAYMENT_REPORT:
            return await self._generate_payment_report(period_start, period_end)
        elif report_type == ReportType.SUBSCRIPTION_METRICS:
            return await self._generate_subscription_metrics(period_start, period_end)
        elif report_type == ReportType.TAX_REPORT:
            return await self._generate_tax_report(period_start, period_end)
        elif report_type == ReportType.AUDIT_TRAIL:
            return await self._generate_audit_trail(period_start, period_end)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
            
    async def _generate_revenue_summary(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate revenue summary report data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Total revenue
                total_revenue = await conn.fetchrow("""
                    SELECT 
                        SUM(recognized_amount) as total,
                        COUNT(*) as transactions
                    FROM revenue_schedules 
                    WHERE period_start BETWEEN $1 AND $2
                    AND status = 'recognized'
                """, period_start, period_end)
                
                # Revenue by source
                revenue_by_source = await conn.fetch("""
                    SELECT 
                        rc.recognition_method as source,
                        SUM(rs.recognized_amount) as amount,
                        COUNT(*) as count
                    FROM revenue_schedules rs
                    JOIN revenue_contracts rc ON rs.contract_id = rc.contract_id
                    WHERE rs.period_start BETWEEN $1 AND $2
                    AND rs.status = 'recognized'
                    GROUP BY rc.recognition_method
                """, period_start, period_end)
                
                # Monthly trends (if period > 1 month)
                monthly_trends = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', period_start) as month,
                        SUM(recognized_amount) as amount
                    FROM revenue_schedules 
                    WHERE period_start BETWEEN $1 AND $2
                    AND status = 'recognized'
                    GROUP BY DATE_TRUNC('month', period_start)
                    ORDER BY month
                """, period_start, period_end)
                
            return {
                "summary": {
                    "total_revenue": float(total_revenue['total'] or 0),
                    "total_transactions": total_revenue['transactions'] or 0,
                    "period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    }
                },
                "revenue_by_source": [
                    {
                        "source": row['source'],
                        "amount": float(row['amount']),
                        "count": row['count']
                    } for row in revenue_by_source
                ],
                "monthly_trends": [
                    {
                        "month": row['month'].strftime('%Y-%m'),
                        "amount": float(row['amount'])
                    } for row in monthly_trends
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate revenue summary: {e}")
            raise
            
    async def _generate_payment_report(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate payment processing report data"""
        try:
            # This would integrate with actual payment data
            # For now, return a basic structure
            return {
                "summary": {
                    "total_payments": 0,
                    "successful_payments": 0,
                    "failed_payments": 0,
                    "success_rate": 0.0,
                    "total_amount": 0.0
                },
                "payment_methods": [],
                "gateway_performance": [],
                "failure_analysis": []
            }
            
        except Exception as e:
            logger.error(f"Failed to generate payment report: {e}")
            raise
            
    async def _generate_subscription_metrics(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate subscription metrics report data"""
        try:
            # This would integrate with subscription data
            # For now, return a basic structure
            return {
                "summary": {
                    "active_subscriptions": 0,
                    "new_subscriptions": 0,
                    "cancelled_subscriptions": 0,
                    "churn_rate": 0.0,
                    "mrr": 0.0
                },
                "plan_distribution": [],
                "churn_analysis": [],
                "retention_metrics": []
            }
            
        except Exception as e:
            logger.error(f"Failed to generate subscription metrics: {e}")
            raise
            
    async def _generate_tax_report(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate tax compliance report data"""
        try:
            # This would integrate with tax calculation data
            # For now, return a basic structure
            return {
                "summary": {
                    "total_tax_calculated": 0.0,
                    "jurisdictions_count": 0,
                    "compliance_rate": 100.0
                },
                "jurisdiction_breakdown": [],
                "tax_calculations": [],
                "compliance_status": []
            }
            
        except Exception as e:
            logger.error(f"Failed to generate tax report: {e}")
            raise
            
    async def _generate_audit_trail(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Generate audit trail report data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Audit events summary
                events_summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_events,
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(DISTINCT entity_type) as entity_types
                    FROM audit_events 
                    WHERE timestamp BETWEEN $1 AND $2
                """, period_start, period_end)
                
                # Events by type
                events_by_type = await conn.fetch("""
                    SELECT 
                        event_type,
                        COUNT(*) as count
                    FROM audit_events 
                    WHERE timestamp BETWEEN $1 AND $2
                    GROUP BY event_type
                    ORDER BY count DESC
                """, period_start, period_end)
                
                # Recent events
                recent_events = await conn.fetch("""
                    SELECT 
                        event_id, event_type, entity_type, entity_id,
                        user_id, timestamp, metadata
                    FROM audit_events 
                    WHERE timestamp BETWEEN $1 AND $2
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, period_start, period_end)
                
            return {
                "summary": {
                    "total_events": events_summary['total_events'],
                    "unique_users": events_summary['unique_users'],
                    "entity_types": events_summary['entity_types']
                },
                "events_by_type": [
                    {
                        "event_type": row['event_type'],
                        "count": row['count']
                    } for row in events_by_type
                ],
                "recent_events": [
                    {
                        "event_id": row['event_id'],
                        "event_type": row['event_type'],
                        "entity_type": row['entity_type'],
                        "entity_id": row['entity_id'],
                        "user_id": row['user_id'],
                        "timestamp": row['timestamp'].isoformat(),
                        "metadata": row['metadata']
                    } for row in recent_events
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate audit trail: {e}")
            raise
            
    async def log_audit_event(
        self,
        event_type: AuditEventType,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEvent:
        """Log audit event"""
        try:
            event_id = f"AE_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{entity_type}_{entity_id[:8]}"
            
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                changes=changes or {},
                metadata=metadata or {},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Store audit event
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO audit_events (
                        event_id, event_type, entity_type, entity_id,
                        user_id, timestamp, changes, metadata,
                        ip_address, user_agent
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, 
                event_id, event_type.value, entity_type, entity_id,
                user_id, datetime.utcnow(), json.dumps(changes or {}),
                json.dumps(metadata or {}), ip_address, user_agent
                )
            
            logger.debug(f"Audit event logged: {event_id}")
            return event
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            raise
            
    async def schedule_report(
        self,
        report_type: ReportType,
        frequency: ReportFrequency,
        recipients: List[str],
        format: ReportFormat = ReportFormat.PDF
    ) -> ReportSchedule:
        """Schedule automated report generation"""
        try:
            schedule_id = f"SCH_{report_type.value}_{frequency.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Calculate next generation time
            next_generation = self._calculate_next_generation(frequency)
            
            schedule = ReportSchedule(
                schedule_id=schedule_id,
                report_type=report_type,
                frequency=frequency,
                recipients=recipients,
                format=format,
                active=True,
                last_generated=None,
                next_generation=next_generation
            )
            
            # Store schedule
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO report_schedules (
                        schedule_id, report_type, frequency, recipients,
                        format, active, next_generation
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                schedule_id, report_type.value, frequency.value,
                json.dumps(recipients), format.value, True, next_generation
                )
            
            logger.info(f"Report schedule created: {schedule_id}")
            return schedule
            
        except Exception as e:
            logger.error(f"Failed to schedule report: {e}")
            raise
            
    def _calculate_next_generation(self, frequency: ReportFrequency) -> datetime:
        """Calculate next report generation time"""
        now = datetime.utcnow()
        
        if frequency == ReportFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            # Next month, same day
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1)
            else:
                return now.replace(month=now.month + 1)
        elif frequency == ReportFrequency.QUARTERLY:
            # Next quarter
            quarter_month = ((now.month - 1) // 3 + 1) * 3 + 1
            if quarter_month > 12:
                return now.replace(year=now.year + 1, month=quarter_month - 12)
            else:
                return now.replace(month=quarter_month)
        elif frequency == ReportFrequency.YEARLY:
            return now.replace(year=now.year + 1)
        else:
            return now + timedelta(days=1)  # Default to daily
            
    async def process_scheduled_reports(self) -> Dict[str, Any]:
        """Process scheduled reports that are due"""
        try:
            current_time = datetime.utcnow()
            
            # Get schedules ready for processing
            async with self.db_pool.acquire() as conn:
                schedules = await conn.fetch("""
                    SELECT * FROM report_schedules 
                    WHERE active = TRUE 
                    AND next_generation <= $1
                """, current_time)
                
            generated_reports = []
            
            for schedule_row in schedules:
                try:
                    # Generate report
                    period_end = current_time
                    period_start = self._calculate_report_period_start(
                        ReportFrequency(schedule_row['frequency']), period_end
                    )
                    
                    report = await self.generate_report(
                        report_type=ReportType(schedule_row['report_type']),
                        period_start=period_start,
                        period_end=period_end,
                        format=ReportFormat(schedule_row['format']),
                        generated_by="scheduler"
                    )
                    
                    generated_reports.append(report.report_id)
                    
                    # Update schedule
                    next_generation = self._calculate_next_generation(
                        ReportFrequency(schedule_row['frequency'])
                    )
                    
                    async with self.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE report_schedules 
                            SET last_generated = $1,
                                next_generation = $2
                            WHERE schedule_id = $3
                        """, current_time, next_generation, schedule_row['schedule_id'])
                        
                except Exception as e:
                    logger.error(f"Failed to process schedule {schedule_row['schedule_id']}: {e}")
                    continue
                    
            logger.info(f"Processed {len(generated_reports)} scheduled reports")
            
            return {
                "processed_schedules": len(schedules),
                "generated_reports": len(generated_reports),
                "report_ids": generated_reports,
                "processed_at": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process scheduled reports: {e}")
            raise
            
    def _calculate_report_period_start(
        self,
        frequency: ReportFrequency,
        period_end: datetime
    ) -> datetime:
        """Calculate report period start based on frequency"""
        if frequency == ReportFrequency.DAILY:
            return period_end - timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            return period_end - timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            if period_end.month == 1:
                return period_end.replace(year=period_end.year - 1, month=12)
            else:
                return period_end.replace(month=period_end.month - 1)
        elif frequency == ReportFrequency.QUARTERLY:
            # Previous quarter
            quarter_month = ((period_end.month - 1) // 3) * 3 + 1
            if quarter_month <= 0:
                return period_end.replace(year=period_end.year - 1, month=10)
            else:
                return period_end.replace(month=quarter_month)
        elif frequency == ReportFrequency.YEARLY:
            return period_end.replace(year=period_end.year - 1)
        else:
            return period_end - timedelta(days=30)  # Default to 30 days
            
    async def get_reporting_analytics(self) -> Dict[str, Any]:
        """Get financial reporting analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Report generation stats
                report_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_reports,
                        COUNT(DISTINCT report_type) as report_types,
                        COUNT(*) FILTER (WHERE generated_at > NOW() - INTERVAL '30 days') as recent_reports
                    FROM financial_reports
                """)
                
                # Reports by type
                reports_by_type = await conn.fetch("""
                    SELECT 
                        report_type,
                        COUNT(*) as count
                    FROM financial_reports
                    GROUP BY report_type
                    ORDER BY count DESC
                """)
                
                # Audit events stats
                audit_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_events,
                        COUNT(*) FILTER (WHERE timestamp > NOW() - INTERVAL '24 hours') as recent_events
                    FROM audit_events
                """)
                
            return {
                "report_statistics": {
                    "total_reports": report_stats['total_reports'],
                    "report_types": report_stats['report_types'],
                    "recent_reports": report_stats['recent_reports']
                },
                "reports_by_type": [
                    {
                        "type": row['report_type'],
                        "count": row['count']
                    } for row in reports_by_type
                ],
                "audit_statistics": {
                    "total_events": audit_stats['total_events'],
                    "recent_events": audit_stats['recent_events']
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get reporting analytics: {e}")
            raise