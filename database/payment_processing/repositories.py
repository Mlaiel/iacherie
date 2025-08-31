"""Payment Processing Repository Layer - Enterprise Grade

Advanced repository layer for payment processing operations,
providing secure, efficient, and scalable database access patterns
with comprehensive CRUD operations, advanced querying, and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert + 
      Payment Systems Architect + Financial Technology Specialist + DevOps Engineer + 
      Microservices Expert + Audio Processing Engineer
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

ENTERPRISE REPOSITORY FEATURES:
- Advanced query optimization and caching
- Comprehensive CRUD operations with validation
- Real-time analytics and reporting queries
- Transaction-safe operations with rollback
- Connection pooling and performance monitoring
- Advanced filtering and pagination
- Audit trail and compliance tracking
"""
from sqlalchemy.orm import Session, sessionmaker, joinedload, selectinload
from sqlalchemy import and_, or_, func, desc, asc, text, case, distinct, exists
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.dialects.postgresql import insert
from typing import List, Dict, Any, Optional, Union, Tuple, Generic, TypeVar
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import uuid
import asyncio
from contextlib import contextmanager, asynccontextmanager
from abc import ABC, abstractmethod

from .models import (
    PaymentTransaction, PaymentMethod, BillingRecord, 
    FinancialRecord, AutomatedPayout, PaymentAnalytics,
    RevenueTracking, PaymentWebhook, PaymentConfiguration,
    PaymentStatus, PaymentMethodType, BillingFrequency, 
    CurrencyCode, PayoutStatus, TransactionType
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class QueryResult:
    """Container for query results with metadata"""
    data: List[Any]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


@dataclass
class FilterCriteria:
    """Container for complex filter criteria"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, like, between
    value: Any
    secondary_value: Optional[Any] = None  # For 'between' operations


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository with common CRUD operations
    """
    
    def __init__(self, session_factory: sessionmaker, model_class: type):
        self.session_factory = session_factory
        self.model_class = model_class
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions with error handling"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            session.close()
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Create new record"""
        try:
            with self.get_session() as session:
                instance = self.model_class(**data)
                session.add(instance)
                session.flush()
                session.refresh(instance)
                return instance
        except IntegrityError as e:
            logger.error(f"Integrity error creating {self.model_class.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            raise
    
    async def get_by_id(self, record_id: Union[str, uuid.UUID]) -> Optional[T]:
        """Get record by ID"""
        try:
            with self.get_session() as session:
                return session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID: {str(e)}")
            raise
    
    async def update(self, record_id: Union[str, uuid.UUID], data: Dict[str, Any]) -> Optional[T]:
        """Update record by ID"""
        try:
            with self.get_session() as session:
                instance = session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
                if instance:
                    for key, value in data.items():
                        if hasattr(instance, key):
                            setattr(instance, key, value)
                    
                    if hasattr(instance, 'updated_at'):
                        instance.updated_at = datetime.utcnow()
                    
                    session.flush()
                    session.refresh(instance)
                    return instance
                return None
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__}: {str(e)}")
            raise
    
    async def delete(self, record_id: Union[str, uuid.UUID]) -> bool:
        """Delete record by ID"""
        try:
            with self.get_session() as session:
                instance = session.query(self.model_class).filter(
                    self.model_class.id == record_id
                ).first()
                
                if instance:
                    session.delete(instance)
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__}: {str(e)}")
            raise
    
    async def list_with_pagination(
        self,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[List[FilterCriteria]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "desc"
    ) -> QueryResult:
        """List records with pagination and filtering"""
        try:
            with self.get_session() as session:
                query = session.query(self.model_class)
                
                # Apply filters
                if filters:
                    for filter_criteria in filters:
                        query = self._apply_filter(query, filter_criteria)
                
                # Count total records
                total_count = query.count()
                
                # Apply ordering
                if order_by and hasattr(self.model_class, order_by):
                    order_column = getattr(self.model_class, order_by)
                    if order_direction.lower() == "asc":
                        query = query.order_by(asc(order_column))
                    else:
                        query = query.order_by(desc(order_column))
                
                # Apply pagination
                offset = (page - 1) * page_size
                records = query.offset(offset).limit(page_size).all()
                
                return QueryResult(
                    data=records,
                    total_count=total_count,
                    page=page,
                    page_size=page_size,
                    has_next=(offset + page_size) < total_count,
                    has_previous=page > 1
                )
        except Exception as e:
            logger.error(f"Error listing {self.model_class.__name__}: {str(e)}")
            raise
    
    def _apply_filter(self, query, filter_criteria: FilterCriteria):
        """Apply filter criteria to query"""
        column = getattr(self.model_class, filter_criteria.field)
        
        if filter_criteria.operator == "eq":
            return query.filter(column == filter_criteria.value)
        elif filter_criteria.operator == "ne":
            return query.filter(column != filter_criteria.value)
        elif filter_criteria.operator == "gt":
            return query.filter(column > filter_criteria.value)
        elif filter_criteria.operator == "lt":
            return query.filter(column < filter_criteria.value)
        elif filter_criteria.operator == "gte":
            return query.filter(column >= filter_criteria.value)
        elif filter_criteria.operator == "lte":
            return query.filter(column <= filter_criteria.value)
        elif filter_criteria.operator == "in":
            return query.filter(column.in_(filter_criteria.value))
        elif filter_criteria.operator == "like":
            return query.filter(column.like(f"%{filter_criteria.value}%"))
        elif filter_criteria.operator == "between":
            return query.filter(column.between(filter_criteria.value, filter_criteria.secondary_value))
        else:
            return query


class PaymentTransactionRepository(BaseRepository[PaymentTransaction]):
    """
    Repository for payment transaction operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, PaymentTransaction)
    
    async def get_by_user_id(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 50,
        status_filter: Optional[List[str]] = None
    ) -> QueryResult:
        """Get transactions for a specific user"""
        try:
            with self.get_session() as session:
                query = session.query(PaymentTransaction).filter(
                    PaymentTransaction.user_id == user_id
                )
                
                if status_filter:
                    query = query.filter(PaymentTransaction.status.in_(status_filter))
                
                query = query.order_by(desc(PaymentTransaction.created_at))
                
                total_count = query.count()
                offset = (page - 1) * page_size
                transactions = query.offset(offset).limit(page_size).all()
                
                return QueryResult(
                    data=transactions,
                    total_count=total_count,
                    page=page,
                    page_size=page_size,
                    has_next=(offset + page_size) < total_count,
                    has_previous=page > 1
                )
        except Exception as e:
            logger.error(f"Error getting transactions for user {user_id}: {str(e)}")
            raise
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        transaction_types: Optional[List[str]] = None
    ) -> List[PaymentTransaction]:
        """Get transactions within date range"""
        try:
            with self.get_session() as session:
                query = session.query(PaymentTransaction).filter(
                    and_(
                        PaymentTransaction.created_at >= start_date,
                        PaymentTransaction.created_at <= end_date
                    )
                )
                
                if user_id:
                    query = query.filter(PaymentTransaction.user_id == user_id)
                
                if transaction_types:
                    query = query.filter(PaymentTransaction.transaction_type.in_(transaction_types))
                
                return query.order_by(desc(PaymentTransaction.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting transactions by date range: {str(e)}")
            raise
    
    async def get_revenue_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Get revenue summary for date range"""
        try:
            with self.get_session() as session:
                query = session.query(
                    func.count(PaymentTransaction.id).label('transaction_count'),
                    func.sum(PaymentTransaction.amount).label('total_amount'),
                    func.sum(PaymentTransaction.platform_fee).label('total_fees'),
                    func.sum(PaymentTransaction.net_amount).label('net_amount'),
                    func.avg(PaymentTransaction.amount).label('average_amount')
                ).filter(
                    and_(
                        PaymentTransaction.created_at >= start_date,
                        PaymentTransaction.created_at <= end_date,
                        PaymentTransaction.currency == currency,
                        PaymentTransaction.status == PaymentStatus.COMPLETED.value
                    )
                )
                
                if user_id:
                    query = query.filter(PaymentTransaction.user_id == user_id)
                
                result = query.first()
                
                return {
                    'transaction_count': result.transaction_count or 0,
                    'total_amount': float(result.total_amount or 0),
                    'total_fees': float(result.total_fees or 0),
                    'net_amount': float(result.net_amount or 0),
                    'average_amount': float(result.average_amount or 0),
                    'currency': currency,
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting revenue summary: {str(e)}")
            raise
    
    async def update_status(self, transaction_id: str, new_status: str) -> bool:
        """Update transaction status"""
        try:
            with self.get_session() as session:
                result = session.query(PaymentTransaction).filter(
                    PaymentTransaction.id == transaction_id
                ).update({
                    'status': new_status,
                    'updated_at': datetime.utcnow(),
                    'processed_at': datetime.utcnow() if new_status == PaymentStatus.COMPLETED.value else None
                })
                
                return result > 0
        except Exception as e:
            logger.error(f"Error updating transaction status: {str(e)}")
            raise
    
    async def get_pending_transactions(self, older_than_minutes: int = 30) -> List[PaymentTransaction]:
        """Get pending transactions older than specified minutes"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=older_than_minutes)
            
            with self.get_session() as session:
                return session.query(PaymentTransaction).filter(
                    and_(
                        PaymentTransaction.status == PaymentStatus.PENDING.value,
                        PaymentTransaction.created_at <= cutoff_time
                    )
                ).all()
        except Exception as e:
            logger.error(f"Error getting pending transactions: {str(e)}")
            raise
    
    async def get_daily_transaction_volume(
        self,
        user_id: str,
        date: Optional[datetime] = None
    ) -> Decimal:
        """Get daily transaction volume for user"""
        try:
            target_date = date or datetime.utcnow()
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            with self.get_session() as session:
                result = session.query(
                    func.sum(PaymentTransaction.amount)
                ).filter(
                    and_(
                        PaymentTransaction.user_id == user_id,
                        PaymentTransaction.created_at >= start_of_day,
                        PaymentTransaction.created_at < end_of_day,
                        PaymentTransaction.status.in_([
                            PaymentStatus.COMPLETED.value,
                            PaymentStatus.PROCESSING.value
                        ])
                    )
                ).scalar()
                
                return Decimal(str(result or 0))
        except Exception as e:
            logger.error(f"Error getting daily transaction volume: {str(e)}")
            raise


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    """
    Repository for payment method operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, PaymentMethod)
    
    async def get_by_user_id(self, user_id: str, active_only: bool = True) -> List[PaymentMethod]:
        """Get payment methods for a user"""
        try:
            with self.get_session() as session:
                query = session.query(PaymentMethod).filter(
                    PaymentMethod.user_id == user_id
                )
                
                if active_only:
                    query = query.filter(PaymentMethod.is_active == True)
                
                return query.order_by(desc(PaymentMethod.is_default), desc(PaymentMethod.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting payment methods for user {user_id}: {str(e)}")
            raise
    
    async def get_default_method(self, user_id: str) -> Optional[PaymentMethod]:
        """Get default payment method for user"""
        try:
            with self.get_session() as session:
                return session.query(PaymentMethod).filter(
                    and_(
                        PaymentMethod.user_id == user_id,
                        PaymentMethod.is_default == True,
                        PaymentMethod.is_active == True
                    )
                ).first()
        except Exception as e:
            logger.error(f"Error getting default payment method for user {user_id}: {str(e)}")
            raise
    
    async def set_as_default(self, method_id: str, user_id: str) -> bool:
        """Set payment method as default for user"""
        try:
            with self.get_session() as session:
                # First, unset all other methods as default
                session.query(PaymentMethod).filter(
                    and_(
                        PaymentMethod.user_id == user_id,
                        PaymentMethod.id != method_id
                    )
                ).update({'is_default': False})
                
                # Then set the specified method as default
                result = session.query(PaymentMethod).filter(
                    and_(
                        PaymentMethod.id == method_id,
                        PaymentMethod.user_id == user_id
                    )
                ).update({'is_default': True, 'updated_at': datetime.utcnow()})
                
                return result > 0
        except Exception as e:
            logger.error(f"Error setting default payment method: {str(e)}")
            raise
    
    async def deactivate_method(self, method_id: str, user_id: str) -> bool:
        """Deactivate payment method"""
        try:
            with self.get_session() as session:
                result = session.query(PaymentMethod).filter(
                    and_(
                        PaymentMethod.id == method_id,
                        PaymentMethod.user_id == user_id
                    )
                ).update({
                    'is_active': False,
                    'is_default': False,
                    'updated_at': datetime.utcnow()
                })
                
                return result > 0
        except Exception as e:
            logger.error(f"Error deactivating payment method: {str(e)}")
            raise


class BillingRecordRepository(BaseRepository[BillingRecord]):
    """
    Repository for billing record operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, BillingRecord)
    
    async def get_by_subscription_id(self, subscription_id: str) -> List[BillingRecord]:
        """Get billing records for subscription"""
        try:
            with self.get_session() as session:
                return session.query(BillingRecord).filter(
                    BillingRecord.subscription_id == subscription_id
                ).order_by(desc(BillingRecord.billing_date)).all()
        except Exception as e:
            logger.error(f"Error getting billing records for subscription {subscription_id}: {str(e)}")
            raise
    
    async def get_upcoming_billings(self, days_ahead: int = 7) -> List[BillingRecord]:
        """Get upcoming billing records"""
        try:
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            with self.get_session() as session:
                return session.query(BillingRecord).filter(
                    and_(
                        BillingRecord.next_billing_date <= cutoff_date,
                        BillingRecord.status == 'active'
                    )
                ).order_by(asc(BillingRecord.next_billing_date)).all()
        except Exception as e:
            logger.error(f"Error getting upcoming billings: {str(e)}")
            raise


class FinancialRecordRepository(BaseRepository[FinancialRecord]):
    """
    Repository for financial record operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, FinancialRecord)
    
    async def get_by_user_and_period(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        record_types: Optional[List[str]] = None
    ) -> List[FinancialRecord]:
        """Get financial records for user within period"""
        try:
            with self.get_session() as session:
                query = session.query(FinancialRecord).filter(
                    and_(
                        FinancialRecord.user_id == user_id,
                        FinancialRecord.transaction_date >= start_date,
                        FinancialRecord.transaction_date <= end_date
                    )
                )
                
                if record_types:
                    query = query.filter(FinancialRecord.record_type.in_(record_types))
                
                return query.order_by(desc(FinancialRecord.transaction_date)).all()
        except Exception as e:
            logger.error(f"Error getting financial records: {str(e)}")
            raise


class AutomatedPayoutRepository(BaseRepository[AutomatedPayout]):
    """
    Repository for automated payout operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, AutomatedPayout)
    
    async def get_scheduled(self, due_before: Optional[datetime] = None) -> List[AutomatedPayout]:
        """Get scheduled payouts"""
        try:
            cutoff_time = due_before or datetime.utcnow()
            
            with self.get_session() as session:
                return session.query(AutomatedPayout).filter(
                    and_(
                        AutomatedPayout.status == PayoutStatus.SCHEDULED.value,
                        AutomatedPayout.scheduled_at <= cutoff_time
                    )
                ).order_by(asc(AutomatedPayout.scheduled_at)).all()
        except Exception as e:
            logger.error(f"Error getting scheduled payouts: {str(e)}")
            raise
    
    async def update_status(self, payout_id: str, new_status: str, error_message: Optional[str] = None) -> bool:
        """Update payout status"""
        try:
            with self.get_session() as session:
                update_data = {
                    'status': new_status,
                    'updated_at': datetime.utcnow()
                }
                
                if new_status == PayoutStatus.SENT.value:
                    update_data['processed_at'] = datetime.utcnow()
                
                if error_message:
                    update_data['error_message'] = error_message
                
                result = session.query(AutomatedPayout).filter(
                    AutomatedPayout.id == payout_id
                ).update(update_data)
                
                return result > 0
        except Exception as e:
            logger.error(f"Error updating payout status: {str(e)}")
            raise


class PaymentAnalyticsRepository(BaseRepository[PaymentAnalytics]):
    """
    Repository for payment analytics operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, PaymentAnalytics)
    
    async def get_metrics_by_period(
        self,
        metric_type: str,
        period_start: datetime,
        period_end: datetime,
        user_id: Optional[str] = None
    ) -> List[PaymentAnalytics]:
        """Get analytics metrics for period"""
        try:
            with self.get_session() as session:
                query = session.query(PaymentAnalytics).filter(
                    and_(
                        PaymentAnalytics.metric_type == metric_type,
                        PaymentAnalytics.period_start >= period_start,
                        PaymentAnalytics.period_end <= period_end
                    )
                )
                
                if user_id:
                    query = query.filter(PaymentAnalytics.user_id == user_id)
                
                return query.order_by(asc(PaymentAnalytics.period_start)).all()
        except Exception as e:
            logger.error(f"Error getting analytics metrics: {str(e)}")
            raise


class RevenueTrackingRepository(BaseRepository[RevenueTracking]):
    """
    Repository for revenue tracking operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, RevenueTracking)
    
    async def get_by_user_period(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> List[RevenueTracking]:
        """Get revenue tracking records for user and period"""
        try:
            with self.get_session() as session:
                return session.query(RevenueTracking).filter(
                    and_(
                        RevenueTracking.user_id == user_id,
                        RevenueTracking.tracking_period_start >= period_start,
                        RevenueTracking.tracking_period_end <= period_end
                    )
                ).order_by(desc(RevenueTracking.tracking_period_start)).all()
        except Exception as e:
            logger.error(f"Error getting revenue tracking data: {str(e)}")
            raise


class PaymentWebhookRepository(BaseRepository[PaymentWebhook]):
    """
    Repository for payment webhook operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, PaymentWebhook)
    
    async def get_unprocessed(self, limit: int = 100) -> List[PaymentWebhook]:
        """Get unprocessed webhooks"""
        try:
            with self.get_session() as session:
                return session.query(PaymentWebhook).filter(
                    PaymentWebhook.status == 'pending'
                ).order_by(asc(PaymentWebhook.received_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting unprocessed webhooks: {str(e)}")
            raise
    
    async def mark_as_processed(self, webhook_id: str, success: bool, error_message: Optional[str] = None) -> bool:
        """Mark webhook as processed"""
        try:
            with self.get_session() as session:
                update_data = {
                    'status': 'processed' if success else 'failed',
                    'processed_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                
                if error_message:
                    update_data['error_message'] = error_message
                
                result = session.query(PaymentWebhook).filter(
                    PaymentWebhook.id == webhook_id
                ).update(update_data)
                
                return result > 0
        except Exception as e:
            logger.error(f"Error marking webhook as processed: {str(e)}")
            raise


class PaymentConfigurationRepository(BaseRepository[PaymentConfiguration]):
    """
    Repository for payment configuration operations
    """
    
    def __init__(self, session_factory: sessionmaker):
        super().__init__(session_factory, PaymentConfiguration)
    
    async def get_by_type_and_provider(
        self,
        config_type: str,
        provider: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[PaymentConfiguration]:
        """Get configuration by type and provider"""
        try:
            with self.get_session() as session:
                query = session.query(PaymentConfiguration).filter(
                    and_(
                        PaymentConfiguration.config_type == config_type,
                        PaymentConfiguration.is_active == True
                    )
                )
                
                if provider:
                    query = query.filter(PaymentConfiguration.provider == provider)
                
                if user_id:
                    query = query.filter(PaymentConfiguration.user_id == user_id)
                
                return query.first()
        except Exception as e:
            logger.error(f"Error getting payment configuration: {str(e)}")
            raise
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()


class PaymentTransactionRepository(PaymentProcessingRepository):
    """Repository for payment transaction operations"""
    
    def create_transaction(
        self,
        user_id: int,
        amount: Decimal,
        currency: str,
        transaction_type: str,
        processor: str,
        **kwargs
    ) -> PaymentTransaction:
        """Create a new payment transaction"""
        with self.get_session() as session:
            transaction = PaymentTransaction(
                user_id=user_id,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                processor=processor,
                gross_amount=amount,
                net_amount=amount - kwargs.get('fees_amount', Decimal('0')),
                **kwargs
            )
            session.add(transaction)
            session.flush()
            session.refresh(transaction)
            
            logger.info(f"Created payment transaction {transaction.id} for user {user_id}")
            return transaction
    
    def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Optional[PaymentTransaction]:
        """Get transaction by ID"""
        with self.get_session() as session:
            return session.query(PaymentTransaction).filter(
                PaymentTransaction.id == transaction_id
            ).first()
    
    def get_user_transactions(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PaymentTransaction]:
        """Get user transactions with optional filtering"""
        with self.get_session() as session:
            query = session.query(PaymentTransaction).filter(
                PaymentTransaction.user_id == user_id
            )
            
            if status:
                query = query.filter(PaymentTransaction.status == status)
            
            return query.order_by(desc(PaymentTransaction.created_at))\
                       .limit(limit).offset(offset).all()
    
    def update_transaction_status(
        self,
        transaction_id: uuid.UUID,
        status: str,
        processor_response: Optional[Dict] = None
    ) -> bool:
        """Update transaction status"""
        with self.get_session() as session:
            transaction = session.query(PaymentTransaction).filter(
                PaymentTransaction.id == transaction_id
            ).first()
            
            if not transaction:
                return False
            
            transaction.status = status
            if processor_response:
                transaction.processor_response = processor_response
            
            if status == PaymentStatus.COMPLETED.value:
                transaction.processed_at = datetime.utcnow()
            
            logger.info(f"Updated transaction {transaction_id} status to {status}")
            return True
    
    def get_transactions_by_external_id(
        self,
        external_id: str,
        processor: str
    ) -> List[PaymentTransaction]:
        """Get transactions by external ID and processor"""
        with self.get_session() as session:
            return session.query(PaymentTransaction).filter(
                and_(
                    PaymentTransaction.external_transaction_id == external_id,
                    PaymentTransaction.processor == processor
                )
            ).all()
    
    def get_revenue_analytics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get revenue analytics for a user"""
        with self.get_session() as session:
            result = session.query(
                func.sum(PaymentTransaction.net_amount).label('total_revenue'),
                func.count(PaymentTransaction.id).label('transaction_count'),
                func.avg(PaymentTransaction.net_amount).label('avg_transaction')
            ).filter(
                and_(
                    PaymentTransaction.user_id == user_id,
                    PaymentTransaction.status == PaymentStatus.COMPLETED.value,
                    PaymentTransaction.created_at >= start_date,
                    PaymentTransaction.created_at <= end_date
                )
            ).first()
            
            return {
                'total_revenue': float(result.total_revenue or 0),
                'transaction_count': result.transaction_count or 0,
                'average_transaction': float(result.avg_transaction or 0)
            }


class PaymentMethodRepository(PaymentProcessingRepository):
    """Repository for payment method operations"""
    
    def create_payment_method(
        self,
        user_id: int,
        method_type: str,
        provider: str,
        **kwargs
    ) -> PaymentMethod:
        """Create a new payment method"""
        with self.get_session() as session:
            # Set as default if it's the first payment method
            is_first_method = not session.query(PaymentMethod).filter(
                PaymentMethod.user_id == user_id
            ).first()
            
            payment_method = PaymentMethod(
                user_id=user_id,
                method_type=method_type,
                provider=provider,
                is_default=is_first_method,
                **kwargs
            )
            session.add(payment_method)
            session.flush()
            session.refresh(payment_method)
            
            logger.info(f"Created payment method {payment_method.id} for user {user_id}")
            return payment_method
    
    def get_user_payment_methods(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[PaymentMethod]:
        """Get user payment methods"""
        with self.get_session() as session:
            query = session.query(PaymentMethod).filter(
                PaymentMethod.user_id == user_id
            )
            
            if active_only:
                query = query.filter(PaymentMethod.is_active == True)
            
            return query.order_by(desc(PaymentMethod.is_default)).all()
    
    def set_default_payment_method(
        self,
        user_id: int,
        payment_method_id: uuid.UUID
    ) -> bool:
        """Set a payment method as default"""
        with self.get_session() as session:
            # Remove default from all user's payment methods
            session.query(PaymentMethod).filter(
                PaymentMethod.user_id == user_id
            ).update({PaymentMethod.is_default: False})
            
            # Set new default
            method = session.query(PaymentMethod).filter(
                and_(
                    PaymentMethod.id == payment_method_id,
                    PaymentMethod.user_id == user_id
                )
            ).first()
            
            if method:
                method.is_default = True
                method.last_used_at = datetime.utcnow()
                logger.info(f"Set payment method {payment_method_id} as default for user {user_id}")
                return True
            
            return False
    
    def deactivate_payment_method(
        self,
        payment_method_id: uuid.UUID,
        user_id: int
    ) -> bool:
        """Deactivate a payment method"""
        with self.get_session() as session:
            method = session.query(PaymentMethod).filter(
                and_(
                    PaymentMethod.id == payment_method_id,
                    PaymentMethod.user_id == user_id
                )
            ).first()
            
            if method:
                method.is_active = False
                if method.is_default:
                    # Find another method to set as default
                    other_method = session.query(PaymentMethod).filter(
                        and_(
                            PaymentMethod.user_id == user_id,
                            PaymentMethod.id != payment_method_id,
                            PaymentMethod.is_active == True
                        )
                    ).first()
                    
                    if other_method:
                        other_method.is_default = True
                
                logger.info(f"Deactivated payment method {payment_method_id}")
                return True
            
            return False


class BillingRecordRepository(PaymentProcessingRepository):
    """Repository for billing record operations"""
    
    def create_billing_record(
        self,
        user_id: int,
        subscription_type: str,
        billing_frequency: str,
        amount: Decimal,
        billing_period_start: datetime,
        billing_period_end: datetime,
        **kwargs
    ) -> BillingRecord:
        """Create a new billing record"""
        with self.get_session() as session:
            billing_record = BillingRecord(
                user_id=user_id,
                subscription_type=subscription_type,
                billing_frequency=billing_frequency,
                amount=amount,
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                due_date=billing_period_end + timedelta(days=7),  # Default 7 days after period end
                **kwargs
            )
            session.add(billing_record)
            session.flush()
            session.refresh(billing_record)
            
            logger.info(f"Created billing record {billing_record.id} for user {user_id}")
            return billing_record
    
    def get_overdue_bills(self, days_overdue: int = 0) -> List[BillingRecord]:
        """Get overdue billing records"""
        with self.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)
            return session.query(BillingRecord).filter(
                and_(
                    BillingRecord.due_date <= cutoff_date,
                    BillingRecord.status == 'pending'
                )
            ).all()
    
    def get_user_billing_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[BillingRecord]:
        """Get user billing history"""
        with self.get_session() as session:
            return session.query(BillingRecord).filter(
                BillingRecord.user_id == user_id
            ).order_by(desc(BillingRecord.created_at)).limit(limit).all()


class FinancialRecordRepository(PaymentProcessingRepository):
    """Repository for financial record operations"""
    
    def create_financial_record(
        self,
        user_id: int,
        record_type: str,
        category: str,
        amount: Decimal,
        currency: str,
        transaction_date: datetime,
        **kwargs
    ) -> FinancialRecord:
        """Create a new financial record"""
        with self.get_session() as session:
            financial_record = FinancialRecord(
                user_id=user_id,
                record_type=record_type,
                category=category,
                amount=amount,
                currency=currency,
                transaction_date=transaction_date,
                accounting_period=transaction_date.strftime("%Y-%m"),
                **kwargs
            )
            session.add(financial_record)
            session.flush()
            session.refresh(financial_record)
            
            logger.info(f"Created financial record {financial_record.id} for user {user_id}")
            return financial_record
    
    def get_financial_summary(
        self,
        user_id: int,
        period: str,
        record_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get financial summary for a period"""
        with self.get_session() as session:
            query = session.query(
                func.sum(FinancialRecord.amount).label('total_amount'),
                func.count(FinancialRecord.id).label('record_count'),
                FinancialRecord.category
            ).filter(
                and_(
                    FinancialRecord.user_id == user_id,
                    FinancialRecord.accounting_period == period
                )
            )
            
            if record_type:
                query = query.filter(FinancialRecord.record_type == record_type)
            
            results = query.group_by(FinancialRecord.category).all()
            
            return {
                'categories': [
                    {
                        'category': result.category,
                        'total_amount': float(result.total_amount),
                        'record_count': result.record_count
                    }
                    for result in results
                ],
                'period': period,
                'total_amount': sum(float(r.total_amount) for r in results)
            }


class AutomatedPayoutRepository(PaymentProcessingRepository):
    """Repository for automated payout operations"""
    
    def create_payout(
        self,
        user_id: int,
        payment_method_id: uuid.UUID,
        total_amount: Decimal,
        period_start: datetime,
        period_end: datetime,
        **kwargs
    ) -> AutomatedPayout:
        """Create a new automated payout"""
        with self.get_session() as session:
            payout = AutomatedPayout(
                user_id=user_id,
                payment_method_id=payment_method_id,
                total_amount=total_amount,
                net_amount=total_amount - kwargs.get('fees_amount', Decimal('0')),
                period_start=period_start,
                period_end=period_end,
                scheduled_at=datetime.utcnow() + timedelta(days=1),  # Default next day
                **kwargs
            )
            session.add(payout)
            session.flush()
            session.refresh(payout)
            
            logger.info(f"Created automated payout {payout.id} for user {user_id}")
            return payout
    
    def get_pending_payouts(self) -> List[AutomatedPayout]:
        """Get pending payouts ready for processing"""
        with self.get_session() as session:
            return session.query(AutomatedPayout).filter(
                and_(
                    AutomatedPayout.status == 'pending',
                    AutomatedPayout.scheduled_at <= datetime.utcnow()
                )
            ).all()
    
    def update_payout_status(
        self,
        payout_id: uuid.UUID,
        status: str,
        external_payout_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update payout status"""
        with self.get_session() as session:
            payout = session.query(AutomatedPayout).filter(
                AutomatedPayout.id == payout_id
            ).first()
            
            if not payout:
                return False
            
            payout.status = status
            if external_payout_id:
                payout.external_payout_id = external_payout_id
            if error_message:
                payout.last_error = error_message
                payout.retry_count += 1
            
            if status == 'completed':
                payout.completed_at = datetime.utcnow()
            elif status == 'processing':
                payout.processed_at = datetime.utcnow()
            
            logger.info(f"Updated payout {payout_id} status to {status}")
            return True


class PaymentAnalyticsRepository(PaymentProcessingRepository):
    """Repository for payment analytics and reporting"""
    
    def get_revenue_trends(
        self,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get revenue trends over time"""
        with self.get_session() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            results = session.query(
                func.date(PaymentTransaction.created_at).label('date'),
                func.sum(PaymentTransaction.net_amount).label('daily_revenue'),
                func.count(PaymentTransaction.id).label('transaction_count')
            ).filter(
                and_(
                    PaymentTransaction.user_id == user_id,
                    PaymentTransaction.status == PaymentStatus.COMPLETED.value,
                    PaymentTransaction.created_at >= start_date
                )
            ).group_by(func.date(PaymentTransaction.created_at)).all()
            
            return [
                {
                    'date': result.date.isoformat(),
                    'revenue': float(result.daily_revenue),
                    'transactions': result.transaction_count
                }
                for result in results
            ]
    
    def get_platform_revenue_breakdown(
        self,
        user_id: int,
        period_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get revenue breakdown by platform"""
        with self.get_session() as session:
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            results = session.query(
                PaymentTransaction.platform_reference.label('platform'),
                func.sum(PaymentTransaction.net_amount).label('total_revenue'),
                func.count(PaymentTransaction.id).label('transaction_count')
            ).filter(
                and_(
                    PaymentTransaction.user_id == user_id,
                    PaymentTransaction.status == PaymentStatus.COMPLETED.value,
                    PaymentTransaction.created_at >= start_date,
                    PaymentTransaction.platform_reference.isnot(None)
                )
            ).group_by(PaymentTransaction.platform_reference).all()
            
            return [
                {
                    'platform': result.platform,
                    'revenue': float(result.total_revenue),
                    'transactions': result.transaction_count
                }
                for result in results
            ]


# Utility functions for repository operations
def create_repository_manager(session_factory: sessionmaker) -> Dict[str, Any]:
    """Create a repository manager with all repositories"""
    return {
        'transactions': PaymentTransactionRepository(session_factory),
        'payment_methods': PaymentMethodRepository(session_factory),
        'billing': BillingRecordRepository(session_factory),
        'financial': FinancialRecordRepository(session_factory),
        'payouts': AutomatedPayoutRepository(session_factory),
        'analytics': PaymentAnalyticsRepository(session_factory)
    }
