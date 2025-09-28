"""
💳 Billing Service
Advanced billing and payment processing system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class BillingStatus(Enum):
    """Billing status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    """Payment method types"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class BillingCycle(Enum):
    """Billing cycle types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class BillingService:
    """Advanced billing and payment processing service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.invoices: List[Dict[str, Any]] = []
        self.payments: List[Dict[str, Any]] = []
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.billing_plans: Dict[str, Dict[str, Any]] = {}
        self.payment_methods: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_billing_plans()
        self.logger.info("✅ BillingService initialized")
    
    def _initialize_billing_plans(self):
        """Initialize default billing plans"""
        self.billing_plans = {
            "basic": {
                "name": "Plan Basic",
                "description": "Fonctionnalités de base pour débuter",
                "price": Decimal("9.99"),
                "currency": "EUR",
                "billing_cycle": BillingCycle.MONTHLY,
                "features": [
                    "5 projets par mois",
                    "1 GB de stockage",
                    "Support par email"
                ],
                "limits": {
                    "projects": 5,
                    "storage_gb": 1,
                    "api_calls": 1000
                }
            },
            "pro": {
                "name": "Plan Professional",
                "description": "Fonctionnalités avancées pour professionnels",
                "price": Decimal("29.99"),
                "currency": "EUR",
                "billing_cycle": BillingCycle.MONTHLY,
                "features": [
                    "Projets illimités",
                    "10 GB de stockage",
                    "Support prioritaire",
                    "Analyses avancées"
                ],
                "limits": {
                    "projects": -1,
                    "storage_gb": 10,
                    "api_calls": 10000
                }
            },
            "enterprise": {
                "name": "Plan Enterprise",
                "description": "Solution complète pour entreprises",
                "price": Decimal("99.99"),
                "currency": "EUR",
                "billing_cycle": BillingCycle.MONTHLY,
                "features": [
                    "Tout illimité",
                    "Stockage illimité",
                    "Support 24/7",
                    "Intégrations personnalisées",
                    "White-label"
                ],
                "limits": {
                    "projects": -1,
                    "storage_gb": -1,
                    "api_calls": -1
                }
            }
        }
    
    async def create_invoice(
        self, 
        user_id: str, 
        plan_id: str,
        billing_period_start: datetime = None,
        billing_period_end: datetime = None
    ) -> Dict[str, Any]:
        """Create new invoice for user"""
        try:
            if plan_id not in self.billing_plans:
                return {
                    "success": False,
                    "error": "Plan de facturation invalide"
                }
            
            plan = self.billing_plans[plan_id]
            invoice_id = str(uuid.uuid4())
            
            # Calculate billing period
            if not billing_period_start:
                billing_period_start = datetime.utcnow()
            
            if not billing_period_end:
                if plan["billing_cycle"] == BillingCycle.MONTHLY:
                    billing_period_end = billing_period_start + timedelta(days=30)
                elif plan["billing_cycle"] == BillingCycle.QUARTERLY:
                    billing_period_end = billing_period_start + timedelta(days=90)
                elif plan["billing_cycle"] == BillingCycle.YEARLY:
                    billing_period_end = billing_period_start + timedelta(days=365)
                else:
                    billing_period_end = billing_period_start
            
            # Calculate taxes (TVA 20% for France)
            subtotal = plan["price"]
            tax_rate = Decimal("0.20")
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            invoice = {
                "invoice_id": invoice_id,
                "user_id": user_id,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "subtotal": float(subtotal),
                "tax_rate": float(tax_rate),
                "tax_amount": float(tax_amount),
                "total_amount": float(total_amount),
                "currency": plan["currency"],
                "status": BillingStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "billing_period": {
                    "start": billing_period_start.isoformat(),
                    "end": billing_period_end.isoformat()
                },
                "line_items": [
                    {
                        "description": plan["name"],
                        "quantity": 1,
                        "unit_price": float(subtotal),
                        "total": float(subtotal)
                    }
                ]
            }
            
            self.invoices.append(invoice)
            
            return {
                "success": True,
                "invoice": invoice,
                "message": "Facture créée avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Invoice creation failed: {str(e)}")
            return {
                "success": False,
                "error": "Échec de création de facture",
                "message": str(e)
            }
    
    async def process_payment(
        self, 
        invoice_id: str,
        payment_method: PaymentMethod,
        payment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment for invoice"""
        try:
            # Find invoice
            invoice = None
            for inv in self.invoices:
                if inv["invoice_id"] == invoice_id:
                    invoice = inv
                    break
            
            if not invoice:
                return {
                    "success": False,
                    "error": "Facture introuvable"
                }
            
            if invoice["status"] != BillingStatus.PENDING.value:
                return {
                    "success": False,
                    "error": "La facture n'est pas en attente de paiement"
                }
            
            payment_id = str(uuid.uuid4())
            
            payment = {
                "payment_id": payment_id,
                "invoice_id": invoice_id,
                "user_id": invoice["user_id"],
                "amount": invoice["total_amount"],
                "currency": invoice["currency"],
                "payment_method": payment_method.value,
                "status": BillingStatus.PROCESSING.value,
                "created_at": datetime.utcnow().isoformat(),
                "payment_details": payment_details,
                "transaction_reference": f"TXN_{payment_id[:8].upper()}"
            }
            
            # Simulate payment processing
            await asyncio.sleep(0.5)  # Simulate API call
            
            # In a real system, integrate with payment processors here
            # (Stripe, PayPal, bank APIs, etc.)
            
            # Simulate success (95% success rate)
            import random
            if random.random() > 0.05:
                payment["status"] = BillingStatus.COMPLETED.value
                payment["completed_at"] = datetime.utcnow().isoformat()
                payment["processor_reference"] = f"PROC_{uuid.uuid4().hex[:10].upper()}"
                
                # Update invoice status
                invoice["status"] = BillingStatus.COMPLETED.value
                invoice["paid_at"] = datetime.utcnow().isoformat()
                invoice["payment_id"] = payment_id
                
                success = True
                message = "Paiement traité avec succès"
            else:
                payment["status"] = BillingStatus.FAILED.value
                payment["error_code"] = "PAYMENT_DECLINED"
                payment["error_message"] = "Paiement refusé par la banque"
                
                success = False
                message = "Paiement échoué"
            
            self.payments.append(payment)
            
            return {
                "success": success,
                "payment": payment,
                "message": message
            }
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {str(e)}")
            return {
                "success": False,
                "error": "Échec du traitement du paiement",
                "message": str(e)
            }
    
    async def create_subscription(
        self, 
        user_id: str, 
        plan_id: str,
        payment_method: PaymentMethod
    ) -> Dict[str, Any]:
        """Create recurring subscription"""
        try:
            if plan_id not in self.billing_plans:
                return {
                    "success": False,
                    "error": "Plan invalide"
                }
            
            subscription_id = str(uuid.uuid4())
            plan = self.billing_plans[plan_id]
            
            subscription = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "status": "active",
                "billing_cycle": plan["billing_cycle"].value,
                "amount": float(plan["price"]),
                "currency": plan["currency"],
                "payment_method": payment_method.value,
                "created_at": datetime.utcnow().isoformat(),
                "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "trial_end_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "features": plan["features"],
                "limits": plan["limits"]
            }
            
            self.subscriptions[subscription_id] = subscription
            
            # Create first invoice
            invoice_result = await self.create_invoice(user_id, plan_id)
            
            return {
                "success": True,
                "subscription": subscription,
                "first_invoice": invoice_result.get("invoice"),
                "message": "Abonnement créé avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Subscription creation failed: {str(e)}")
            return {
                "success": False,
                "error": "Échec de création d'abonnement",
                "message": str(e)
            }
    
    async def get_billing_history(self, user_id: str) -> Dict[str, Any]:
        """Get billing history for user"""
        try:
            user_invoices = [
                inv for inv in self.invoices
                if inv["user_id"] == user_id
            ]
            
            user_payments = [
                pay for pay in self.payments
                if pay["user_id"] == user_id
            ]
            
            user_subscriptions = [
                sub for sub in self.subscriptions.values()
                if sub["user_id"] == user_id
            ]
            
            # Sort by date (newest first)
            user_invoices.sort(key=lambda x: x["created_at"], reverse=True)
            user_payments.sort(key=lambda x: x["created_at"], reverse=True)
            
            return {
                "success": True,
                "user_id": user_id,
                "invoices": user_invoices,
                "payments": user_payments,
                "subscriptions": user_subscriptions,
                "summary": {
                    "total_invoices": len(user_invoices),
                    "total_payments": len(user_payments),
                    "total_spent": sum(pay["amount"] for pay in user_payments if pay["status"] == "completed"),
                    "active_subscriptions": len([sub for sub in user_subscriptions if sub["status"] == "active"])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Getting billing history failed: {str(e)}")
            return {
                "success": False,
                "error": "Échec de récupération de l'historique",
                "message": str(e)
            }
    
    async def cancel_subscription(self, subscription_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return {
                    "success": False,
                    "error": "Abonnement introuvable"
                }
            
            subscription = self.subscriptions[subscription_id]
            
            if subscription["user_id"] != user_id:
                return {
                    "success": False,
                    "error": "Accès non autorisé"
                }
            
            subscription["status"] = "cancelled"
            subscription["cancelled_at"] = datetime.utcnow().isoformat()
            subscription["cancellation_reason"] = "User requested cancellation"
            
            return {
                "success": True,
                "subscription": subscription,
                "message": "Abonnement annulé avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Subscription cancellation failed: {str(e)}")
            return {
                "success": False,
                "error": "Échec d'annulation d'abonnement",
                "message": str(e)
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "BillingService",
            "status": "healthy",
            "total_invoices": len(self.invoices),
            "total_payments": len(self.payments),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s["status"] == "active"]),
            "billing_plans": len(self.billing_plans),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['BillingService', 'BillingStatus', 'PaymentMethod', 'BillingCycle']