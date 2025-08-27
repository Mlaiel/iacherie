"""
Payments API Routes
Payment processing and financial transaction endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import json

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...monetization.payment_processor import PaymentProcessor
from ...integrations.services.stripe_integration import StripeIntegration
from ...integrations.services.wise_integration import WiseIntegration
from ...integrations.services.paypal_integration import PayPalIntegration


# Enums
class PaymentMethod(str, Enum):
    STRIPE_CARD = "stripe_card"
    STRIPE_BANK = "stripe_bank"
    PAYPAL = "paypal"
    WISE_TRANSFER = "wise_transfer"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class TransactionType(str, Enum):
    PAYMENT_IN = "payment_in"
    PAYMENT_OUT = "payment_out"
    REFUND = "refund"
    PAYOUT = "payout"
    FEE = "fee"
    CHARGEBACK = "chargeback"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


# Pydantic models
class PaymentMethodDetails(BaseModel):
    method_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    method_type: PaymentMethod
    display_name: str = Field(..., min_length=1, max_length=100)
    details: Dict[str, Any]  # Card details, bank account, etc.
    is_default: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    billing_address: Optional[Dict[str, str]] = None


class PaymentRequest(BaseModel):
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: Decimal = Field(..., gt=0)
    currency: Currency = Field(default=Currency.USD)
    payment_method_id: str
    description: str = Field(..., min_length=1, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None


class PayoutRequest(BaseModel):
    payout_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: Decimal = Field(..., gt=0)
    currency: Currency = Field(default=Currency.USD)
    destination_method_id: str
    description: str = Field(..., min_length=1, max_length=500)
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")
    metadata: Optional[Dict[str, Any]] = None


class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    transaction_type: TransactionType
    amount: Decimal
    currency: Currency
    payment_method: PaymentMethod
    status: PaymentStatus
    description: str
    external_id: Optional[str] = None
    fees: Optional[Dict[str, Decimal]] = None
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class RefundRequest(BaseModel):
    refund_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    amount: Optional[Decimal] = None  # None for full refund
    reason: str = Field(..., min_length=1, max_length=500)
    metadata: Optional[Dict[str, Any]] = None


class BankAccountDetails(BaseModel):
    account_holder_name: str = Field(..., min_length=1, max_length=200)
    account_number: str = Field(..., min_length=1)
    routing_number: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    bank_name: str = Field(..., min_length=1, max_length=200)
    bank_address: Dict[str, str]
    account_type: str = Field(default="checking", regex="^(checking|savings|business)$")


class PaymentAnalytics(BaseModel):
    period: str
    total_volume: Decimal
    transaction_count: int
    average_transaction: Decimal
    payment_methods_breakdown: Dict[str, Dict[str, Any]]
    currency_breakdown: Dict[str, Decimal]
    status_breakdown: Dict[str, int]
    fee_summary: Dict[str, Decimal]
    growth_metrics: Dict[str, float]


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize payment processors
payment_processor = PaymentProcessor()
stripe_integration = StripeIntegration()
wise_integration = WiseIntegration()
paypal_integration = PayPalIntegration()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/methods", response_model=Dict[str, str])
async def add_payment_method(
    method: PaymentMethodDetails,
    user: dict = Depends(get_current_user)
):
    """Add a new payment method"""
    try:
        # Validate payment method details
        validation_result = await payment_processor.validate_payment_method(method)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment method: {validation_result['errors']}"
            )
        
        # Encrypt sensitive details
        encrypted_details = await security_manager.encrypt_payment_details(method.details)
        
        # Store payment method
        async with database_manager.get_postgres_session() as session:
            # If this is set as default, unset others
            if method.is_default:
                await session.execute("""
                    UPDATE payment_methods SET is_default = false
                    WHERE user_id = %s
                """, (user['user_id'],))
            
            await session.execute("""
                INSERT INTO payment_methods (method_id, user_id, method_type, display_name,
                                           encrypted_details, is_default, is_verified,
                                           billing_address, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                method.method_id, user['user_id'], method.method_type.value,
                method.display_name, encrypted_details, method.is_default,
                method.is_verified, method.billing_address, datetime.utcnow()
            ))
            await session.commit()
        
        # Verify method with provider if needed
        if method.method_type in [PaymentMethod.STRIPE_CARD, PaymentMethod.STRIPE_BANK]:
            verification_result = await stripe_integration.verify_payment_method(
                method.method_id, method.details
            )
            
            # Update verification status
            async with database_manager.get_postgres_session() as session:
                await session.execute("""
                    UPDATE payment_methods 
                    SET is_verified = %s, verification_data = %s
                    WHERE method_id = %s
                """, (verification_result['verified'], verification_result, method.method_id))
                await session.commit()
        
        logger.info(f"Payment method added: {method.method_id} by user {user['user_id']}")
        
        return {
            "method_id": method.method_id,
            "status": "verified" if method.is_verified else "pending_verification",
            "message": "Payment method added successfully"
        }
        
    except Exception as e:
        logger.error(f"Add payment method failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add payment method"
        )


@router.get("/methods", response_model=List[Dict[str, Any]])
async def get_payment_methods(
    user: dict = Depends(get_current_user)
):
    """Get user's payment methods"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT method_id, method_type, display_name, is_default, is_verified,
                       billing_address, created_at, last_used_at
                FROM payment_methods
                WHERE user_id = %s AND deleted_at IS NULL
                ORDER BY is_default DESC, created_at DESC
            """, (user['user_id'],))
            
            methods = result.fetchall()
        
        method_list = []
        for method in methods:
            method_list.append({
                "method_id": method[0],
                "method_type": method[1],
                "display_name": method[2],
                "is_default": method[3],
                "is_verified": method[4],
                "billing_address": method[5],
                "created_at": method[6],
                "last_used_at": method[7]
            })
        
        return method_list
        
    except Exception as e:
        logger.error(f"Get payment methods failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment methods"
        )


@router.post("/process", response_model=Dict[str, str])
async def process_payment(
    payment: PaymentRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Process a payment"""
    try:
        # Get payment method details
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT method_type, encrypted_details, is_verified
                FROM payment_methods
                WHERE method_id = %s AND user_id = %s AND deleted_at IS NULL
            """, (payment.payment_method_id, user['user_id']))
            
            method_info = result.fetchone()
            if not method_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment method not found or access denied"
                )
            
            if not method_info[2]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment method not verified"
                )
        
        method_type, encrypted_details, _ = method_info
        payment_details = await security_manager.decrypt_payment_details(encrypted_details)
        
        # Create transaction record
        transaction_id = str(uuid.uuid4())
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO transactions (transaction_id, user_id, payment_id, transaction_type,
                                        amount, currency, payment_method, payment_method_id,
                                        status, description, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                transaction_id, user['user_id'], payment.payment_id,
                TransactionType.PAYMENT_IN.value, payment.amount, payment.currency.value,
                method_type, payment.payment_method_id, PaymentStatus.PENDING.value,
                payment.description, payment.metadata, datetime.utcnow()
            ))
            await session.commit()
        
        # Process payment via appropriate provider
        background_tasks.add_task(
            _process_payment_async, transaction_id, payment, method_type, payment_details, user
        )
        
        logger.info(f"Payment processing initiated: {payment.payment_id} by user {user['user_id']}")
        
        return {
            "payment_id": payment.payment_id,
            "transaction_id": transaction_id,
            "status": "processing",
            "message": "Payment processing initiated"
        }
        
    except Exception as e:
        logger.error(f"Process payment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment"
        )


@router.post("/payout", response_model=Dict[str, str])
async def process_payout(
    payout: PayoutRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Process a payout to user"""
    try:
        # Check user balance
        balance = await _get_user_balance(user['user_id'], payout.currency.value)
        if balance < payout.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: {balance} {payout.currency.value}"
            )
        
        # Get payout method details
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT method_type, encrypted_details, is_verified
                FROM payment_methods
                WHERE method_id = %s AND user_id = %s AND deleted_at IS NULL
            """, (payout.destination_method_id, user['user_id']))
            
            method_info = result.fetchone()
            if not method_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payout method not found or access denied"
                )
            
            if not method_info[2]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payout method not verified"
                )
        
        method_type, encrypted_details, _ = method_info
        payout_details = await security_manager.decrypt_payment_details(encrypted_details)
        
        # Create payout transaction
        transaction_id = str(uuid.uuid4())
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO transactions (transaction_id, user_id, payout_id, transaction_type,
                                        amount, currency, payment_method, payment_method_id,
                                        status, description, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                transaction_id, user['user_id'], payout.payout_id,
                TransactionType.PAYOUT.value, payout.amount, payout.currency.value,
                method_type, payout.destination_method_id, PaymentStatus.PENDING.value,
                payout.description, payout.metadata, datetime.utcnow()
            ))
            await session.commit()
        
        # Process payout via appropriate provider
        background_tasks.add_task(
            _process_payout_async, transaction_id, payout, method_type, payout_details, user
        )
        
        logger.info(f"Payout processing initiated: {payout.payout_id} by user {user['user_id']}")
        
        return {
            "payout_id": payout.payout_id,
            "transaction_id": transaction_id,
            "status": "processing",
            "message": "Payout processing initiated"
        }
        
    except Exception as e:
        logger.error(f"Process payout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payout"
        )


@router.post("/refund", response_model=Dict[str, str])
async def process_refund(
    refund: RefundRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Process a refund"""
    try:
        # Get original transaction
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT transaction_id, amount, currency, payment_method, external_id, status
                FROM transactions
                WHERE transaction_id = %s AND user_id = %s AND transaction_type = %s
            """, (refund.transaction_id, user['user_id'], TransactionType.PAYMENT_IN.value))
            
            transaction_info = result.fetchone()
            if not transaction_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found or access denied"
                )
            
            if transaction_info[5] != PaymentStatus.COMPLETED.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only refund completed transactions"
                )
        
        # Validate refund amount
        original_amount = transaction_info[1]
        refund_amount = refund.amount or original_amount
        
        if refund_amount > original_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount cannot exceed original transaction amount"
            )
        
        # Create refund transaction
        refund_transaction_id = str(uuid.uuid4())
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO transactions (transaction_id, user_id, refund_id, transaction_type,
                                        amount, currency, payment_method, original_transaction_id,
                                        status, description, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                refund_transaction_id, user['user_id'], refund.refund_id,
                TransactionType.REFUND.value, refund_amount, transaction_info[2],
                transaction_info[3], refund.transaction_id, PaymentStatus.PENDING.value,
                refund.reason, refund.metadata, datetime.utcnow()
            ))
            await session.commit()
        
        # Process refund via appropriate provider
        background_tasks.add_task(
            _process_refund_async, refund_transaction_id, refund, transaction_info, user
        )
        
        logger.info(f"Refund processing initiated: {refund.refund_id} by user {user['user_id']}")
        
        return {
            "refund_id": refund.refund_id,
            "transaction_id": refund_transaction_id,
            "status": "processing",
            "message": "Refund processing initiated"
        }
        
    except Exception as e:
        logger.error(f"Process refund failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund"
        )


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    transaction_type: Optional[TransactionType] = None,
    status: Optional[PaymentStatus] = None,
    currency: Optional[Currency] = None,
    days: int = Field(default=30, ge=1, le=365),
    limit: int = Field(default=50, ge=1, le=200),
    user: dict = Depends(get_current_user)
):
    """Get user's transactions"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
            SELECT transaction_id, user_id, transaction_type, amount, currency,
                   payment_method, status, description, external_id, fees,
                   metadata, created_at, updated_at, completed_at
            FROM transactions
            WHERE user_id = %s AND created_at >= %s
        """
        params = [user['user_id'], start_date]
        
        if transaction_type:
            query += " AND transaction_type = %s"
            params.append(transaction_type.value)
        
        if status:
            query += " AND status = %s"
            params.append(status.value)
        
        if currency:
            query += " AND currency = %s"
            params.append(currency.value)
            
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            transactions = result.fetchall()
        
        transaction_list = []
        for txn in transactions:
            transaction_list.append(Transaction(
                transaction_id=txn[0],
                user_id=txn[1],
                transaction_type=TransactionType(txn[2]),
                amount=txn[3],
                currency=Currency(txn[4]),
                payment_method=PaymentMethod(txn[5]),
                status=PaymentStatus(txn[6]),
                description=txn[7],
                external_id=txn[8],
                fees=txn[9],
                metadata=txn[10] or {},
                created_at=txn[11],
                updated_at=txn[12],
                completed_at=txn[13]
            ))
        
        return transaction_list
        
    except Exception as e:
        logger.error(f"Get transactions failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions"
        )


@router.get("/balance", response_model=Dict[str, Any])
async def get_balance(
    user: dict = Depends(get_current_user)
):
    """Get user's account balance"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Get balance by currency
            result = await session.execute("""
                SELECT currency, 
                       SUM(CASE WHEN transaction_type IN ('payment_in', 'refund') THEN amount ELSE 0 END) -
                       SUM(CASE WHEN transaction_type IN ('payment_out', 'payout', 'fee') THEN amount ELSE 0 END) as balance
                FROM transactions
                WHERE user_id = %s AND status = %s
                GROUP BY currency
            """, (user['user_id'], PaymentStatus.COMPLETED.value))
            
            balances = {row[0]: float(row[1]) for row in result.fetchall()}
            
            # Get pending transactions
            result = await session.execute("""
                SELECT currency, transaction_type, SUM(amount) as total
                FROM transactions
                WHERE user_id = %s AND status IN (%s, %s)
                GROUP BY currency, transaction_type
            """, (user['user_id'], PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value))
            
            pending = {}
            for row in result.fetchall():
                currency = row[0]
                if currency not in pending:
                    pending[currency] = {}
                pending[currency][row[1]] = float(row[2])
        
        return {
            "available_balances": balances,
            "pending_transactions": pending,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get balance failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get balance"
        )


@router.get("/analytics", response_model=PaymentAnalytics)
async def get_payment_analytics(
    days: int = Field(default=30, ge=1, le=365),
    user: dict = Depends(get_current_user)
):
    """Get payment analytics"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        async with database_manager.get_postgres_session() as session:
            # Total volume and count
            result = await session.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as volume
                FROM transactions
                WHERE user_id = %s AND created_at >= %s AND status = %s
            """, (user['user_id'], start_date, PaymentStatus.COMPLETED.value))
            
            total_stats = result.fetchone()
            total_count = total_stats[0]
            total_volume = float(total_stats[1])
            
            # Payment methods breakdown
            result = await session.execute("""
                SELECT payment_method, COUNT(*) as count, COALESCE(SUM(amount), 0) as volume
                FROM transactions
                WHERE user_id = %s AND created_at >= %s AND status = %s
                GROUP BY payment_method
            """, (user['user_id'], start_date, PaymentStatus.COMPLETED.value))
            
            payment_methods = {}
            for row in result.fetchall():
                payment_methods[row[0]] = {
                    "count": row[1],
                    "volume": float(row[2]),
                    "average": float(row[2]) / row[1] if row[1] > 0 else 0
                }
            
            # Currency breakdown
            result = await session.execute("""
                SELECT currency, COALESCE(SUM(amount), 0) as volume
                FROM transactions
                WHERE user_id = %s AND created_at >= %s AND status = %s
                GROUP BY currency
            """, (user['user_id'], start_date, PaymentStatus.COMPLETED.value))
            
            currency_breakdown = {row[0]: float(row[1]) for row in result.fetchall()}
            
            # Status breakdown
            result = await session.execute("""
                SELECT status, COUNT(*) as count
                FROM transactions
                WHERE user_id = %s AND created_at >= %s
                GROUP BY status
            """, (user['user_id'], start_date))
            
            status_breakdown = {row[0]: row[1] for row in result.fetchall()}
            
            # Fee summary
            result = await session.execute("""
                SELECT COALESCE(SUM((fees->>'processing_fee')::decimal), 0) as processing_fees,
                       COALESCE(SUM((fees->>'platform_fee')::decimal), 0) as platform_fees
                FROM transactions
                WHERE user_id = %s AND created_at >= %s AND status = %s AND fees IS NOT NULL
            """, (user['user_id'], start_date, PaymentStatus.COMPLETED.value))
            
            fee_data = result.fetchone()
            fee_summary = {
                "processing_fees": float(fee_data[0] or 0),
                "platform_fees": float(fee_data[1] or 0)
            }
            
            # Growth metrics (compare with previous period)
            prev_start = start_date - timedelta(days=days)
            result = await session.execute("""
                SELECT COUNT(*) as prev_count, COALESCE(SUM(amount), 0) as prev_volume
                FROM transactions
                WHERE user_id = %s AND created_at >= %s AND created_at < %s AND status = %s
            """, (user['user_id'], prev_start, start_date, PaymentStatus.COMPLETED.value))
            
            prev_stats = result.fetchone()
            prev_count = prev_stats[0]
            prev_volume = float(prev_stats[1])
            
            growth_metrics = {
                "volume_growth": ((total_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0,
                "count_growth": ((total_count - prev_count) / prev_count * 100) if prev_count > 0 else 0
            }
        
        analytics = PaymentAnalytics(
            period=f"{days}d",
            total_volume=Decimal(str(total_volume)),
            transaction_count=total_count,
            average_transaction=Decimal(str(total_volume / total_count)) if total_count > 0 else Decimal(0),
            payment_methods_breakdown=payment_methods,
            currency_breakdown={k: Decimal(str(v)) for k, v in currency_breakdown.items()},
            status_breakdown=status_breakdown,
            fee_summary={k: Decimal(str(v)) for k, v in fee_summary.items()},
            growth_metrics=growth_metrics
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Get payment analytics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get payment analytics"
        )


@router.delete("/methods/{method_id}")
async def delete_payment_method(
    method_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a payment method"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Check if method exists and belongs to user
            result = await session.execute("""
                SELECT method_id, is_default FROM payment_methods
                WHERE method_id = %s AND user_id = %s AND deleted_at IS NULL
            """, (method_id, user['user_id']))
            
            method_info = result.fetchone()
            if not method_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment method not found or access denied"
                )
            
            # Check for pending transactions using this method
            result = await session.execute("""
                SELECT COUNT(*) FROM transactions
                WHERE user_id = %s AND payment_method_id = %s 
                  AND status IN (%s, %s)
            """, (user['user_id'], method_id, PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value))
            
            pending_count = result.fetchone()[0]
            if pending_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete payment method with pending transactions"
                )
            
            # Soft delete the payment method
            await session.execute("""
                UPDATE payment_methods 
                SET deleted_at = %s, is_default = false
                WHERE method_id = %s
            """, (datetime.utcnow(), method_id))
            
            # If this was the default method, set another as default if available
            if method_info[1]:  # was default
                await session.execute("""
                    UPDATE payment_methods 
                    SET is_default = true
                    WHERE user_id = %s AND deleted_at IS NULL AND method_id != %s
                    ORDER BY created_at ASC
                    LIMIT 1
                """, (user['user_id'], method_id))
            
            await session.commit()
        
        logger.info(f"Payment method deleted: {method_id}")
        
        return {"message": "Payment method deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete payment method failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment method"
        )


# Helper functions
async def _get_user_balance(user_id: str, currency: str) -> Decimal:
    """Get user balance for specific currency"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT 
                    SUM(CASE WHEN transaction_type IN ('payment_in', 'refund') THEN amount ELSE 0 END) -
                    SUM(CASE WHEN transaction_type IN ('payment_out', 'payout', 'fee') THEN amount ELSE 0 END) as balance
                FROM transactions
                WHERE user_id = %s AND currency = %s AND status = %s
            """, (user_id, currency, PaymentStatus.COMPLETED.value))
            
            balance = result.fetchone()[0]
            return Decimal(str(balance or 0))
    except Exception as e:
        logger.error(f"Get user balance failed: {e}")
        return Decimal(0)


# Background task functions
async def _process_payment_async(transaction_id: str, payment: PaymentRequest, 
                                method_type: str, payment_details: Dict[str, Any], user: dict):
    """Process payment asynchronously"""
    try:
        # Update status to processing
        await _update_transaction_status(transaction_id, PaymentStatus.PROCESSING)
        
        # Process via appropriate provider
        if method_type.startswith("stripe"):
            result = await stripe_integration.process_payment(
                payment.amount, payment.currency.value, payment_details, payment.metadata
            )
        elif method_type == "paypal":
            result = await paypal_integration.process_payment(
                payment.amount, payment.currency.value, payment_details, payment.metadata
            )
        else:
            raise Exception(f"Unsupported payment method: {method_type}")
        
        # Update transaction with result
        if result['success']:
            await _update_transaction_status(
                transaction_id, PaymentStatus.COMPLETED, result['external_id'], result.get('fees')
            )
        else:
            await _update_transaction_status(
                transaction_id, PaymentStatus.FAILED, error_message=result['error']
            )
        
        logger.info(f"Payment processed: {transaction_id}, success: {result['success']}")
        
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        await _update_transaction_status(transaction_id, PaymentStatus.FAILED, error_message=str(e))


async def _process_payout_async(transaction_id: str, payout: PayoutRequest,
                               method_type: str, payout_details: Dict[str, Any], user: dict):
    """Process payout asynchronously"""
    try:
        # Update status to processing
        await _update_transaction_status(transaction_id, PaymentStatus.PROCESSING)
        
        # Process via appropriate provider
        if method_type == "wise_transfer":
            result = await wise_integration.process_payout(
                payout.amount, payout.currency.value, payout_details, payout.metadata
            )
        elif method_type.startswith("stripe"):
            result = await stripe_integration.process_payout(
                payout.amount, payout.currency.value, payout_details, payout.metadata
            )
        elif method_type == "paypal":
            result = await paypal_integration.process_payout(
                payout.amount, payout.currency.value, payout_details, payout.metadata
            )
        else:
            raise Exception(f"Unsupported payout method: {method_type}")
        
        # Update transaction with result
        if result['success']:
            await _update_transaction_status(
                transaction_id, PaymentStatus.COMPLETED, result['external_id'], result.get('fees')
            )
        else:
            await _update_transaction_status(
                transaction_id, PaymentStatus.FAILED, error_message=result['error']
            )
        
        logger.info(f"Payout processed: {transaction_id}, success: {result['success']}")
        
    except Exception as e:
        logger.error(f"Payout processing failed: {e}")
        await _update_transaction_status(transaction_id, PaymentStatus.FAILED, error_message=str(e))


async def _process_refund_async(transaction_id: str, refund: RefundRequest,
                               transaction_info: tuple, user: dict):
    """Process refund asynchronously"""
    try:
        # Update status to processing
        await _update_transaction_status(transaction_id, PaymentStatus.PROCESSING)
        
        original_amount, currency, payment_method, external_id = transaction_info[1:5]
        refund_amount = refund.amount or original_amount
        
        # Process via appropriate provider
        if payment_method.startswith("stripe"):
            result = await stripe_integration.process_refund(
                external_id, refund_amount, currency, refund.reason
            )
        elif payment_method == "paypal":
            result = await paypal_integration.process_refund(
                external_id, refund_amount, currency, refund.reason
            )
        else:
            raise Exception(f"Refunds not supported for payment method: {payment_method}")
        
        # Update transaction with result
        if result['success']:
            await _update_transaction_status(
                transaction_id, PaymentStatus.COMPLETED, result['external_id'], result.get('fees')
            )
        else:
            await _update_transaction_status(
                transaction_id, PaymentStatus.FAILED, error_message=result['error']
            )
        
        logger.info(f"Refund processed: {transaction_id}, success: {result['success']}")
        
    except Exception as e:
        logger.error(f"Refund processing failed: {e}")
        await _update_transaction_status(transaction_id, PaymentStatus.FAILED, error_message=str(e))


async def _update_transaction_status(transaction_id: str, status: PaymentStatus, 
                                   external_id: Optional[str] = None,
                                   fees: Optional[Dict[str, Any]] = None,
                                   error_message: Optional[str] = None):
    """Update transaction status"""
    try:
        async with database_manager.get_postgres_session() as session:
            if status == PaymentStatus.COMPLETED:
                await session.execute("""
                    UPDATE transactions 
                    SET status = %s, external_id = %s, fees = %s, completed_at = %s, updated_at = %s
                    WHERE transaction_id = %s
                """, (status.value, external_id, fees, datetime.utcnow(), datetime.utcnow(), transaction_id))
            elif status == PaymentStatus.FAILED:
                await session.execute("""
                    UPDATE transactions 
                    SET status = %s, error_message = %s, updated_at = %s
                    WHERE transaction_id = %s
                """, (status.value, error_message, datetime.utcnow(), transaction_id))
            else:
                await session.execute("""
                    UPDATE transactions 
                    SET status = %s, updated_at = %s
                    WHERE transaction_id = %s
                """, (status.value, datetime.utcnow(), transaction_id))
            
            await session.commit()
    except Exception as e:
        logger.error(f"Update transaction status failed: {e}")