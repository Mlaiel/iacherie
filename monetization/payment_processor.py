"""Payment Processor
Automated payment processing and distribution system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import hashlib
import hmac
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class PaymentProvider(Enum):
    """Payment providers"""    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"


class PaymentStatus(Enum):
    """Payment status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class PaymentType(Enum):
    """Payment types"""    LICENSE_PAYMENT = "license_payment"
    ROYALTY_PAYMENT = "royalty_payment"
    REVENUE_SHARE = "revenue_share"
    SUBSCRIPTION = "subscription"
    REFUND = "refund"
    ESCROW_RELEASE = "escrow_release"


@dataclass
class PaymentTransaction:
    """Payment transaction structure"""    id: str
    transaction_type: PaymentType
    provider: PaymentProvider
    amount: float
    currency: str
    payer_id: str
    payee_id: str
    status: PaymentStatus
    provider_transaction_id: Optional[str] = None
    metadata: Optional[Dict] = None
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    fees: float = 0.0
    net_amount: float = 0.0


@dataclass
class EscrowTransaction:
    """Escrow transaction for dispute management"""    id: str
    payment_id: str
    amount: float
    currency: str
    holder: str  # Platform holding funds
    release_conditions: List[str]
    dispute_deadline: datetime
    status: str = "active"
    created_at: Optional[datetime] = None


class PaymentProcessor:
    """Automated payment processing and distribution engine"""    
    # Provider fee structures
    PROVIDER_FEES = {
        PaymentProvider.STRIPE: {
            "percentage": 0.029,  # 2.9%
            "fixed": 0.30,       # €0.30
            "international": 0.039  # 3.9% for international
        },
        PaymentProvider.PAYPAL: {
            "percentage": 0.034,  # 3.4%
            "fixed": 0.35,       # €0.35
            "international": 0.044  # 4.4% for international
        },
        PaymentProvider.WISE: {
            "percentage": 0.005,  # 0.5%
            "fixed": 0.50,       # €0.50
            "international": 0.008  # 0.8% for international
        },
        PaymentProvider.BITCOIN: {
            "percentage": 0.01,   # 1%
            "fixed": 0.0,        # No fixed fee
            "international": 0.01  # Same for international
        }
    }
    
    def __init__(self):
        self.transactions = {}
        self.escrow_accounts = {}
        self.provider_configs = {}
        
    async def configure_stripe(
        self,
        secret_key: str,
        webhook_secret: str,
        connect_enabled: bool = True
    ):
        """Configure Stripe payment provider"""        try:
            self.provider_configs[PaymentProvider.STRIPE] = {
                "secret_key": secret_key,
                "webhook_secret": webhook_secret,
                "connect_enabled": connect_enabled
            }
            
            logger.info("Stripe configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring Stripe: {str(e)}")
            raise
    
    async def configure_paypal(
        self,
        client_id: str,
        client_secret: str,
        environment: str = "sandbox"
    ):
        """Configure PayPal payment provider"""        try:
            self.provider_configs[PaymentProvider.PAYPAL] = {
                "client_id": client_id,
                "client_secret": client_secret,
                "environment": environment
            }
            
            logger.info("PayPal configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring PayPal: {str(e)}")
            raise
    
    async def process_license_payment(
        self,
        license_id: str,
        payer_id: str,
        payee_id: str,
        amount: float,
        currency: str = "EUR",
        provider: PaymentProvider = PaymentProvider.STRIPE,
        payment_method_id: Optional[str] = None
    ) -> PaymentTransaction:
        """Process license payment"""        try:
            transaction_id = str(uuid.uuid4())
            
            # Calculate fees
            fees = self._calculate_fees(amount, provider, currency)
            net_amount = amount - fees
            
            transaction = PaymentTransaction(
                id=transaction_id,
                transaction_type=PaymentType.LICENSE_PAYMENT,
                provider=provider,
                amount=amount,
                currency=currency,
                payer_id=payer_id,
                payee_id=payee_id,
                status=PaymentStatus.PENDING,
                fees=fees,
                net_amount=net_amount,
                metadata={"license_id": license_id},
                created_at=datetime.now()
            )
            
            # Process payment based on provider
            if provider == PaymentProvider.STRIPE:
                result = await self._process_stripe_payment(transaction, payment_method_id)
            elif provider == PaymentProvider.PAYPAL:
                result = await self._process_paypal_payment(transaction)
            elif provider == PaymentProvider.WISE:
                result = await self._process_wise_payment(transaction)
            else:
                raise ValueError(f"Unsupported payment provider: {provider}")
            
            if result["success"]:
                transaction.status = PaymentStatus.PROCESSING
                transaction.provider_transaction_id = result.get("transaction_id")
            else:
                transaction.status = PaymentStatus.FAILED
                
            self.transactions[transaction_id] = transaction
            
            logger.info(f"License payment processed: {transaction_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error processing license payment: {str(e)}")
            raise
    
    async def distribute_revenue_shares(
        self,
        revenue_data: Dict[str, float],
        split_rules: Dict[str, float],
        currency: str = "EUR"
    ) -> List[PaymentTransaction]:
        """Distribute revenue shares automatically"""        try:
            transactions = []
            total_revenue = sum(revenue_data.values())
            
            for recipient_id, share_percentage in split_rules.items():
                if share_percentage <= 0:
                    continue
                    
                share_amount = total_revenue * share_percentage
                
                if share_amount < 1.0:  # Minimum payout threshold
                    logger.info(f"Skipping payout to {recipient_id}: amount too small ({share_amount})")
                    continue
                
                transaction_id = str(uuid.uuid4())
                
                # Calculate fees
                fees = self._calculate_fees(share_amount, PaymentProvider.STRIPE, currency)
                net_amount = share_amount - fees
                
                transaction = PaymentTransaction(
                    id=transaction_id,
                    transaction_type=PaymentType.REVENUE_SHARE,
                    provider=PaymentProvider.STRIPE,  # Default to Stripe
                    amount=share_amount,
                    currency=currency,
                    payer_id="platform",  # Platform pays
                    payee_id=recipient_id,
                    status=PaymentStatus.PENDING,
                    fees=fees,
                    net_amount=net_amount,
                    metadata={"revenue_split": share_percentage},
                    created_at=datetime.now()
                )
                
                # Process payout
                result = await self._process_stripe_payout(transaction)
                
                if result["success"]:
                    transaction.status = PaymentStatus.PROCESSING
                    transaction.provider_transaction_id = result.get("payout_id")
                else:
                    transaction.status = PaymentStatus.FAILED
                    
                self.transactions[transaction_id] = transaction
                transactions.append(transaction)
            
            logger.info(f"Revenue shares distributed: {len(transactions)} payouts")
            return transactions
            
        except Exception as e:
            logger.error(f"Error distributing revenue shares: {str(e)}")
            return []
    
    async def create_escrow_transaction(
        self,
        payment_id: str,
        amount: float,
        currency: str,
        release_conditions: List[str],
        dispute_period_days: int = 7
    ) -> EscrowTransaction:
        """Create escrow transaction for dispute protection"""        try:
            escrow_id = str(uuid.uuid4())
            
            escrow = EscrowTransaction(
                id=escrow_id,
                payment_id=payment_id,
                amount=amount,
                currency=currency,
                holder="platform",
                release_conditions=release_conditions,
                dispute_deadline=datetime.now() + timedelta(days=dispute_period_days),
                created_at=datetime.now()
            )
            
            self.escrow_accounts[escrow_id] = escrow
            
            logger.info(f"Escrow transaction created: {escrow_id}")
            return escrow
            
        except Exception as e:
            logger.error(f"Error creating escrow transaction: {str(e)}")
            raise
    
    async def release_escrow(
        self,
        escrow_id: str,
        release_reason: str
    ) -> bool:
        """Release funds from escrow"""        try:
            escrow = self.escrow_accounts.get(escrow_id)
            if not escrow:
                logger.error(f"Escrow transaction not found: {escrow_id}")
                return False
                
            if escrow.status != "active":
                logger.error(f"Escrow already processed: {escrow_id}")
                return False
                
            # Check if past dispute deadline
            if datetime.now() > escrow.dispute_deadline:
                escrow.status = "released_auto"
            else:
                escrow.status = "released_manual"
                
            # Process actual fund release
            original_transaction = self.transactions.get(escrow.payment_id)
            if original_transaction:
                original_transaction.status = PaymentStatus.COMPLETED
                original_transaction.processed_at = datetime.now()
                
            logger.info(f"Escrow funds released: {escrow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error releasing escrow: {str(e)}")
            return False
    
    async def process_multi_currency_payment(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        payer_id: str,
        payee_id: str
    ) -> PaymentTransaction:
        """Process multi-currency payment with conversion"""        try:
            # Get exchange rate (simplified - in production use real exchange API)
            exchange_rate = await self._get_exchange_rate(from_currency, to_currency)
            converted_amount = amount * exchange_rate
            
            transaction_id = str(uuid.uuid4())
            
            # Use Wise for international transfers
            fees = self._calculate_fees(converted_amount, PaymentProvider.WISE, to_currency)
            net_amount = converted_amount - fees
            
            transaction = PaymentTransaction(
                id=transaction_id,
                transaction_type=PaymentType.LICENSE_PAYMENT,
                provider=PaymentProvider.WISE,
                amount=converted_amount,
                currency=to_currency,
                payer_id=payer_id,
                payee_id=payee_id,
                status=PaymentStatus.PENDING,
                fees=fees,
                net_amount=net_amount,
                metadata={
                    "original_amount": amount,
                    "original_currency": from_currency,
                    "exchange_rate": exchange_rate
                },
                created_at=datetime.now()
            )
            
            # Process with Wise
            result = await self._process_wise_payment(transaction)
            
            if result["success"]:
                transaction.status = PaymentStatus.PROCESSING
                transaction.provider_transaction_id = result.get("transfer_id")
            else:
                transaction.status = PaymentStatus.FAILED
                
            self.transactions[transaction_id] = transaction
            
            logger.info(f"Multi-currency payment processed: {transaction_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error processing multi-currency payment: {str(e)}")
            raise
    
    async def handle_payment_dispute(
        self,
        transaction_id: str,
        dispute_reason: str,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle payment dispute"""        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                return {"success": False, "error": "Transaction not found"}
                
            transaction.status = PaymentStatus.DISPUTED
            
            # Create dispute record
            dispute_id = str(uuid.uuid4())
            dispute_data = {
                "id": dispute_id,
                "transaction_id": transaction_id,
                "reason": dispute_reason,
                "evidence": evidence,
                "status": "open",
                "created_at": datetime.now().isoformat()
            }
            
            # In production, this would integrate with provider dispute APIs
            logger.info(f"Payment dispute created: {dispute_id}")
            
            return {
                "success": True,
                "dispute_id": dispute_id,
                "status": "open"
            }
            
        except Exception as e:
            logger.error(f"Error handling payment dispute: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_tax_reports(
        self,
        user_id: str,
        year: int,
        country: str
    ) -> Dict[str, Any]:
        """Generate tax reports for users"""        try:
            user_transactions = [
                t for t in self.transactions.values()
                if (t.payee_id == user_id or t.payer_id == user_id) and
                t.created_at and t.created_at.year == year and
                t.status == PaymentStatus.COMPLETED
            ]
            
            income_transactions = [t for t in user_transactions if t.payee_id == user_id]
            expense_transactions = [t for t in user_transactions if t.payer_id == user_id]
            
            total_income = sum(t.net_amount for t in income_transactions)
            total_expenses = sum(t.amount for t in expense_transactions)
            total_fees = sum(t.fees for t in income_transactions)
            
            # Country-specific tax calculations
            tax_info = self._calculate_tax_obligations(total_income, country)
            
            report = {
                "user_id": user_id,
                "year": year,
                "country": country,
                "total_income": total_income,
                "total_expenses": total_expenses,
                "total_fees": total_fees,
                "net_income": total_income - total_expenses,
                "tax_obligations": tax_info,
                "transaction_count": len(user_transactions),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Tax report generated for user {user_id}, year {year}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating tax report: {str(e)}")
            return {}
    
    def _calculate_fees(
        self,
        amount: float,
        provider: PaymentProvider,
        currency: str,
        international: bool = False
    ) -> float:
        """Calculate payment provider fees"""        try:
            fee_structure = self.PROVIDER_FEES.get(provider)
            if not fee_structure:
                return amount * 0.03  # Default 3%
                
            percentage_fee = fee_structure["international" if international else "percentage"]
            fixed_fee = fee_structure["fixed"]
            
            total_fee = (amount * percentage_fee) + fixed_fee
            
            # Cap fees at reasonable amount
            return min(total_fee, amount * 0.1)  # Max 10%
            
        except Exception as e:
            logger.error(f"Error calculating fees: {str(e)}")
            return amount * 0.03
    
    async def _process_stripe_payment(
        self,
        transaction: PaymentTransaction,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process Stripe payment (simplified implementation)"""        try:
            # In production, this would use the Stripe SDK
            # For now, simulate processing
            
            if not payment_method_id:
                return {"success": False, "error": "Payment method required"}
                
            # Simulate API call
            await asyncio.sleep(0.1)
            
            # Simulate success (90% success rate)
            import random
            if random.random() < 0.9:
                return {
                    "success": True,
                    "transaction_id": f"ch_{uuid.uuid4().hex[:24]}",
                    "status": "succeeded"
                }
            else:
                return {
                    "success": False,
                    "error": "Card declined"
                }
                
        except Exception as e:
            logger.error(f"Error processing Stripe payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_stripe_payout(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process Stripe payout (simplified implementation)"""        try:
            # In production, this would use Stripe Connect
            await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "payout_id": f"po_{uuid.uuid4().hex[:24]}",
                "status": "paid"
            }
            
        except Exception as e:
            logger.error(f"Error processing Stripe payout: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_paypal_payment(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process PayPal payment (simplified implementation)"""        try:
            # Simulate PayPal processing
            await asyncio.sleep(0.2)
            
            return {
                "success": True,
                "transaction_id": f"PAY-{uuid.uuid4().hex[:17].upper()}",
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error processing PayPal payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_wise_payment(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process Wise transfer (simplified implementation)"""        try:
            # Simulate Wise processing
            await asyncio.sleep(0.3)
            
            return {
                "success": True,
                "transfer_id": f"transfer_{uuid.uuid4().hex[:20]}",
                "status": "processing"
            }
            
        except Exception as e:
            logger.error(f"Error processing Wise payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate (simplified implementation)"""        try:
            # In production, use real exchange rate API
            rates = {
                ("USD", "EUR"): 0.85,
                ("EUR", "USD"): 1.18,
                ("GBP", "EUR"): 1.15,
                ("EUR", "GBP"): 0.87
            }
            
            return rates.get((from_currency, to_currency), 1.0)
            
        except Exception as e:
            logger.error(f"Error getting exchange rate: {str(e)}")
            return 1.0
    
    def _calculate_tax_obligations(self, income: float, country: str) -> Dict[str, float]:
        """Calculate tax obligations by country"""        try:
            # Simplified tax calculations
            tax_rates = {
                "DE": {"rate": 0.25, "threshold": 9744},  # Germany
                "FR": {"rate": 0.30, "threshold": 10225},  # France
                "US": {"rate": 0.22, "threshold": 12950},  # USA
                "GB": {"rate": 0.20, "threshold": 12570},  # UK
            }
            
            country_tax = tax_rates.get(country, {"rate": 0.20, "threshold": 10000})
            
            taxable_income = max(0, income - country_tax["threshold"])
            tax_owed = taxable_income * country_tax["rate"]
            
            return {
                "taxable_income": taxable_income,
                "tax_rate": country_tax["rate"],
                "tax_owed": tax_owed,
                "threshold": country_tax["threshold"]
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax obligations: {str(e)}")
            return {"tax_owed": 0.0}