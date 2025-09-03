"""
Working Payment Integration (Stripe) for Ainflue Platform
Simplified implementation to ensure functionality
"""

import asyncio
import time
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    CRYPTO = "crypto"
    BANK_TRANSFER = "bank_transfer"

class StripePaymentProcessor:
    """Stripe payment processor (mock implementation)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk_test_mock_key"
        self.logger = logger
        
    async def create_payment_intent(self, amount: float, currency: str = "usd", 
                                  metadata: Dict = None) -> Dict[str, Any]:
        """Create Stripe payment intent"""
        try:
            # Mock Stripe payment intent creation
            payment_intent = {
                "id": f"pi_{int(time.time())}_{hashlib.md5(str(amount).encode()).hexdigest()[:8]}",
                "amount": int(amount * 100),  # Stripe uses cents
                "currency": currency,
                "status": "requires_payment_method",
                "created": int(time.time()),
                "metadata": metadata or {},
                "client_secret": f"pi_mock_secret_{int(time.time())}"
            }
            
            return {
                "status": "success",
                "payment_intent": payment_intent,
                "message": "Payment intent created successfully"
            }
        except Exception as e:
            self.logger.error(f"Stripe payment intent creation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def confirm_payment(self, payment_intent_id: str, payment_method: str) -> Dict[str, Any]:
        """Confirm Stripe payment"""
        try:
            # Mock payment confirmation
            return {
                "status": "success",
                "payment_intent": {
                    "id": payment_intent_id,
                    "status": "succeeded",
                    "amount_received": 2000,  # Mock amount
                    "confirmed_at": datetime.utcnow().isoformat()
                },
                "message": "Payment confirmed successfully"
            }
        except Exception as e:
            self.logger.error(f"Stripe payment confirmation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_refund(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Create refund for payment"""
        try:
            refund = {
                "id": f"re_{int(time.time())}",
                "payment_intent": payment_intent_id,
                "amount": int((amount or 20) * 100),
                "status": "succeeded",
                "created": int(time.time())
            }
            
            return {
                "status": "success",
                "refund": refund,
                "message": "Refund created successfully"
            }
        except Exception as e:
            self.logger.error(f"Stripe refund creation failed: {e}")
            return {"status": "error", "message": str(e)}

class PaymentGateway:
    """Main payment gateway supporting multiple providers"""
    
    def __init__(self):
        self.logger = logger
        self.stripe_processor = StripePaymentProcessor()
        self.transactions = {}  # In-memory storage for demo
        
    async def process_payment(self, amount: float, currency: str = "usd", 
                            payment_method: PaymentMethod = PaymentMethod.STRIPE,
                            customer_id: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Process payment through selected provider"""
        try:
            transaction_id = f"txn_{int(time.time())}_{hashlib.md5(f'{amount}{currency}'.encode()).hexdigest()[:8]}"
            
            # Create transaction record
            transaction = {
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency,
                "payment_method": payment_method.value,
                "customer_id": customer_id,
                "status": PaymentStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Process based on payment method
            if payment_method == PaymentMethod.STRIPE:
                result = await self.stripe_processor.create_payment_intent(amount, currency, metadata)
                if result["status"] == "success":
                    transaction["payment_intent_id"] = result["payment_intent"]["id"]
                    transaction["client_secret"] = result["payment_intent"]["client_secret"]
                    transaction["status"] = PaymentStatus.PROCESSING.value
            
            # Store transaction
            self.transactions[transaction_id] = transaction
            
            return {
                "status": "success",
                "transaction": transaction,
                "message": "Payment processing initiated"
            }
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def confirm_payment(self, transaction_id: str, payment_method_id: str = None) -> Dict[str, Any]:
        """Confirm payment completion"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                return {"status": "error", "message": "Transaction not found"}
            
            # Confirm payment based on method
            if transaction["payment_method"] == PaymentMethod.STRIPE.value:
                result = await self.stripe_processor.confirm_payment(
                    transaction["payment_intent_id"], 
                    payment_method_id or "pm_card_mock"
                )
                
                if result["status"] == "success":
                    transaction["status"] = PaymentStatus.COMPLETED.value
                    transaction["completed_at"] = datetime.utcnow().isoformat()
                    transaction["payment_details"] = result["payment_intent"]
            
            return {
                "status": "success",
                "transaction": transaction,
                "message": "Payment confirmed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Payment confirmation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund payment"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                return {"status": "error", "message": "Transaction not found"}
            
            if transaction["status"] != PaymentStatus.COMPLETED.value:
                return {"status": "error", "message": "Cannot refund non-completed payment"}
            
            # Process refund
            if transaction["payment_method"] == PaymentMethod.STRIPE.value:
                result = await self.stripe_processor.create_refund(
                    transaction["payment_intent_id"], 
                    amount
                )
                
                if result["status"] == "success":
                    transaction["status"] = PaymentStatus.REFUNDED.value
                    transaction["refunded_at"] = datetime.utcnow().isoformat()
                    transaction["refund_details"] = result["refund"]
            
            return {
                "status": "success",
                "transaction": transaction,
                "message": "Refund processed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Refund processing failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                return {"status": "error", "message": "Transaction not found"}
            
            return {
                "status": "success",
                "transaction": transaction
            }
        except Exception as e:
            self.logger.error(f"Transaction retrieval failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def list_transactions(self, customer_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """List transactions"""
        try:
            transactions = list(self.transactions.values())
            
            if customer_id:
                transactions = [t for t in transactions if t.get("customer_id") == customer_id]
            
            # Sort by creation date (newest first)
            transactions = sorted(transactions, key=lambda x: x["created_at"], reverse=True)
            
            # Apply limit
            transactions = transactions[:limit]
            
            return {
                "status": "success",
                "transactions": transactions,
                "count": len(transactions)
            }
        except Exception as e:
            self.logger.error(f"Transaction listing failed: {e}")
            return {"status": "error", "message": str(e)}

# Service instance
payment_gateway = PaymentGateway()

# API functions
async def create_payment(amount: float, currency: str = "usd", 
                        payment_method: str = "stripe", customer_id: str = None,
                        metadata: Dict = None) -> Dict[str, Any]:
    """Create a payment"""
    method = PaymentMethod(payment_method) if payment_method in [m.value for m in PaymentMethod] else PaymentMethod.STRIPE
    return await payment_gateway.process_payment(amount, currency, method, customer_id, metadata)

async def confirm_payment(transaction_id: str, payment_method_id: str = None) -> Dict[str, Any]:
    """Confirm a payment"""
    return await payment_gateway.confirm_payment(transaction_id, payment_method_id)

async def refund_payment(transaction_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
    """Refund a payment"""
    return await payment_gateway.refund_payment(transaction_id, amount)

async def get_transaction_details(transaction_id: str) -> Dict[str, Any]:
    """Get transaction details"""
    return await payment_gateway.get_transaction(transaction_id)

async def list_customer_transactions(customer_id: str, limit: int = 10) -> Dict[str, Any]:
    """List customer transactions"""
    return await payment_gateway.list_transactions(customer_id, limit)

# Export main functions
__all__ = ['create_payment', 'confirm_payment', 'refund_payment', 'get_transaction_details', 
           'list_customer_transactions', 'PaymentGateway', 'PaymentStatus', 'PaymentMethod']