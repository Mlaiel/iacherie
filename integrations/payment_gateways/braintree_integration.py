"""Braintree Integration - PayPal's Advanced Payment Platform
===========================================================

Enterprise-grade Braintree integration supporting payments, subscriptions,
marketplace functionality, and advanced fraud protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

import httpx
import braintree
from braintree.exceptions import (
    BraintreeError, AuthenticationError, AuthorizationError,
    ConfigurationError, DownForMaintenanceError, 
    ForgedQueryStringError, InvalidChallengeError,
    InvalidSignatureError, NotFoundError, ServerError,
    TooManyRequestsError, UnexpectedError, UpgradeRequiredError
)


class BraintreeTransactionStatus(Enum):
    """Braintree transaction status types."""
    AUTHORIZATION_EXPIRED = "authorization_expired"
    AUTHORIZED = "authorized"
    AUTHORIZING = "authorizing"
    FAILED = "failed"
    GATEWAY_REJECTED = "gateway_rejected"
    PROCESSOR_DECLINED = "processor_declined"
    SETTLED = "settled"
    SETTLING = "settling"
    SUBMITTED_FOR_SETTLEMENT = "submitted_for_settlement"
    VOIDED = "voided"


class BraintreeSubscriptionStatus(Enum):
    """Braintree subscription status types."""
    ACTIVE = "Active"
    CANCELED = "Canceled"
    EXPIRED = "Expired"
    PAST_DUE = "Past Due"
    PENDING = "Pending"


class BraintreePaymentMethod(Enum):
    """Braintree payment method types."""
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal_account"
    VENMO = "venmo_account"
    APPLE_PAY = "apple_pay_card"
    GOOGLE_PAY = "google_pay_card"
    SAMSUNG_PAY = "samsung_pay_card"
    VISA_CHECKOUT = "visa_checkout_card"
    MASTERPASS = "masterpass_card"


@dataclass
class BraintreeTransactionRequest:
    """Braintree transaction request structure."""
    amount: Decimal
    payment_method_nonce: Optional[str] = None
    payment_method_token: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    merchant_account_id: Optional[str] = None
    submit_for_settlement: bool = False
    device_data: Optional[str] = None
    customer: Optional[Dict[str, Any]] = None
    billing: Optional[Dict[str, Any]] = None
    shipping: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    descriptor: Optional[Dict[str, str]] = None
    service_fee_amount: Optional[Decimal] = None
    three_d_secure: Optional[Dict[str, Any]] = None


@dataclass
class BraintreeCustomerRequest:
    """Braintree customer request structure."""
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    website: Optional[str] = None
    credit_card: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class BraintreeSubscriptionRequest:
    """Braintree subscription request structure."""
    payment_method_token: str
    plan_id: str
    id: Optional[str] = None
    merchant_id: Optional[str] = None
    price: Optional[Decimal] = None
    trial_period: bool = False
    trial_duration: Optional[int] = None
    trial_duration_unit: Optional[str] = None
    number_of_billing_cycles: Optional[int] = None
    discounts: Optional[List[Dict[str, Any]]] = None
    options: Optional[Dict[str, Any]] = None


class BraintreePaymentProcessor:
    """Enterprise Braintree payment processor for advanced transactions.
    
    Features:
    - Advanced payment processing with fraud protection
    - Vault for secure payment method storage
    - Subscription and recurring billing management
    - Marketplace split payments and commission handling
    - 3D Secure authentication support
    - Multi-merchant account support
    - Advanced fraud detection and risk management
    - PayPal, Venmo, and digital wallet integration
    - PCI DSS Level 1 compliance
    - Comprehensive webhook notifications
    - Advanced reporting and analytics
    - International payment support
    """
    
    def __init__(
        self,
        merchant_id -> None: str,
        public_key -> None: str,
        private_key -> None: str,
        environment -> None: str = "sandbox",
        merchant_account_id -> None: Optional[str] = None,
        webhook_endpoint_url -> None: Optional[str] = None
    ) -> None:
        """Initialize Braintree payment processor.
        
        Args:
            merchant_id: Braintree merchant ID
            public_key: Braintree public key
            private_key: Braintree private key
            environment: Environment (sandbox/production)
            merchant_account_id: Default merchant account ID
            webhook_endpoint_url: Webhook endpoint URL
        """
        self.merchant_id = merchant_id
        self.public_key = public_key
        self.private_key = private_key
        self.environment = environment
        self.merchant_account_id = merchant_account_id
        self.webhook_endpoint_url = webhook_endpoint_url
        
        # Configure Braintree environment
        if environment == "production":
            braintree_env = braintree.Environment.Production
        else:
            braintree_env = braintree.Environment.Sandbox
        
        braintree.Configuration.configure(
            environment=braintree_env,
            merchant_id=merchant_id,
            public_key=public_key,
            private_key=private_key
        )
        
        self.logger = logging.getLogger(__name__)
        self.session = httpx.AsyncClient(timeout=30.0)

    async def generate_client_token(
        self,
        customer_id: Optional[str] = None,
        merchant_account_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate client token for frontend integration.
        
        Args:
            customer_id: Customer ID for vault operations
            merchant_account_id: Merchant account ID
            options: Additional options
            
        Returns:
            Client token string
        """
        try:
            params = {}
            
            if customer_id:
                params["customer_id"] = customer_id
            if merchant_account_id or self.merchant_account_id:
                params["merchant_account_id"] = merchant_account_id or self.merchant_account_id
            if options:
                params.update(options)
            
            result = braintree.ClientToken.generate(params)
            
            if result.is_success:
                self.logger.info("Generated client token successfully")
                return result.client_token
            else:
                error_msg = f"Failed to generate client token: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error generating client token: {e}")
            raise

    async def create_customer(
        self,
        customer_request: BraintreeCustomerRequest
    ) -> Dict[str, Any]:
        """Create a customer in Braintree vault.
        
        Args:
            customer_request: Customer creation request
            
        Returns:
            Dict containing customer details
        """
        try:
            params = {}
            
            if customer_request.id:
                params["id"] = customer_request.id
            if customer_request.first_name:
                params["first_name"] = customer_request.first_name
            if customer_request.last_name:
                params["last_name"] = customer_request.last_name
            if customer_request.company:
                params["company"] = customer_request.company
            if customer_request.email:
                params["email"] = customer_request.email
            if customer_request.phone:
                params["phone"] = customer_request.phone
            if customer_request.fax:
                params["fax"] = customer_request.fax
            if customer_request.website:
                params["website"] = customer_request.website
            if customer_request.credit_card:
                params["credit_card"] = customer_request.credit_card
            if customer_request.custom_fields:
                params["custom_fields"] = customer_request.custom_fields
            
            result = braintree.Customer.create(params)
            
            if result.is_success:
                customer = result.customer
                customer_data = {
                    "id": customer.id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "company": customer.company,
                    "email": customer.email,
                    "phone": customer.phone,
                    "fax": customer.fax,
                    "website": customer.website,
                    "created_at": customer.created_at.isoformat() if customer.created_at else None,
                    "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
                    "credit_cards": [self._format_credit_card(card) for card in customer.credit_cards],
                    "paypal_accounts": [self._format_paypal_account(account) for account in customer.paypal_accounts]
                }
                
                self.logger.info(f"Created customer: {customer.id}")
                return customer_data
            else:
                error_msg = f"Failed to create customer: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error creating customer: {e}")
            raise

    async def process_transaction(
        self,
        transaction_request: BraintreeTransactionRequest
    ) -> Dict[str, Any]:
        """Process a transaction through Braintree.
        
        Args:
            transaction_request: Transaction request details
            
        Returns:
            Dict containing transaction result
        """
        try:
            params = {
                "amount": str(transaction_request.amount)
            }
            
            if transaction_request.payment_method_nonce:
                params["payment_method_nonce"] = transaction_request.payment_method_nonce
            if transaction_request.payment_method_token:
                params["payment_method_token"] = transaction_request.payment_method_token
            if transaction_request.customer_id:
                params["customer_id"] = transaction_request.customer_id
            if transaction_request.order_id:
                params["order_id"] = transaction_request.order_id
            if transaction_request.merchant_account_id or self.merchant_account_id:
                params["merchant_account_id"] = transaction_request.merchant_account_id or self.merchant_account_id
            if transaction_request.submit_for_settlement:
                params["options"] = {"submit_for_settlement": True}
            if transaction_request.device_data:
                params["device_data"] = transaction_request.device_data
            if transaction_request.customer:
                params["customer"] = transaction_request.customer
            if transaction_request.billing:
                params["billing"] = transaction_request.billing
            if transaction_request.shipping:
                params["shipping"] = transaction_request.shipping
            if transaction_request.custom_fields:
                params["custom_fields"] = transaction_request.custom_fields
            if transaction_request.descriptor:
                params["descriptor"] = transaction_request.descriptor
            if transaction_request.service_fee_amount:
                params["service_fee_amount"] = str(transaction_request.service_fee_amount)
            if transaction_request.three_d_secure:
                params["three_d_secure"] = transaction_request.three_d_secure
            
            # Merge additional options
            if transaction_request.options:
                if "options" not in params:
                    params["options"] = {}
                params["options"].update(transaction_request.options)
            
            result = braintree.Transaction.sale(params)
            
            if result.is_success:
                transaction = result.transaction
                transaction_data = self._format_transaction(transaction)
                
                self.logger.info(f"Processed transaction: {transaction.id} - {transaction.status}")
                return transaction_data
            else:
                error_msg = f"Transaction failed: {result.message}"
                self.logger.error(error_msg)
                
                # Return detailed error information
                return {
                    "success": False,
                    "message": result.message,
                    "errors": [error.message for error in result.errors.deep_errors] if result.errors else [],
                    "processor_response_code": getattr(result.transaction, "processor_response_code", None) if result.transaction else None,
                    "processor_response_text": getattr(result.transaction, "processor_response_text", None) if result.transaction else None
                }
                
        except Exception as e:
            self.logger.error(f"Error processing transaction: {e}")
            raise

    async def capture_transaction(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Capture an authorized transaction.
        
        Args:
            transaction_id: Transaction ID to capture
            amount: Amount to capture (if partial capture)
            
        Returns:
            Dict containing capture result
        """
        try:
            if amount:
                result = braintree.Transaction.submit_for_settlement(transaction_id, str(amount))
            else:
                result = braintree.Transaction.submit_for_settlement(transaction_id)
            
            if result.is_success:
                transaction = result.transaction
                transaction_data = self._format_transaction(transaction)
                
                self.logger.info(f"Captured transaction: {transaction_id}")
                return transaction_data
            else:
                error_msg = f"Failed to capture transaction: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error capturing transaction: {e}")
            raise

    async def refund_transaction(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Refund a settled transaction.
        
        Args:
            transaction_id: Transaction ID to refund
            amount: Amount to refund (if partial refund)
            
        Returns:
            Dict containing refund result
        """
        try:
            if amount:
                result = braintree.Transaction.refund(transaction_id, str(amount))
            else:
                result = braintree.Transaction.refund(transaction_id)
            
            if result.is_success:
                transaction = result.transaction
                transaction_data = self._format_transaction(transaction)
                
                self.logger.info(f"Refunded transaction: {transaction_id}")
                return transaction_data
            else:
                error_msg = f"Failed to refund transaction: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error refunding transaction: {e}")
            raise

    async def void_transaction(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """Void an authorized transaction.
        
        Args:
            transaction_id: Transaction ID to void
            
        Returns:
            Dict containing void result
        """
        try:
            result = braintree.Transaction.void(transaction_id)
            
            if result.is_success:
                transaction = result.transaction
                transaction_data = self._format_transaction(transaction)
                
                self.logger.info(f"Voided transaction: {transaction_id}")
                return transaction_data
            else:
                error_msg = f"Failed to void transaction: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error voiding transaction: {e}")
            raise

    async def create_subscription(
        self,
        subscription_request: BraintreeSubscriptionRequest
    ) -> Dict[str, Any]:
        """Create a subscription for recurring payments.
        
        Args:
            subscription_request: Subscription request details
            
        Returns:
            Dict containing subscription details
        """
        try:
            params = {
                "payment_method_token": subscription_request.payment_method_token,
                "plan_id": subscription_request.plan_id
            }
            
            if subscription_request.id:
                params["id"] = subscription_request.id
            if subscription_request.merchant_id:
                params["merchant_id"] = subscription_request.merchant_id
            if subscription_request.price:
                params["price"] = str(subscription_request.price)
            if subscription_request.trial_period:
                params["trial_period"] = subscription_request.trial_period
            if subscription_request.trial_duration:
                params["trial_duration"] = subscription_request.trial_duration
            if subscription_request.trial_duration_unit:
                params["trial_duration_unit"] = subscription_request.trial_duration_unit
            if subscription_request.number_of_billing_cycles:
                params["number_of_billing_cycles"] = subscription_request.number_of_billing_cycles
            if subscription_request.discounts:
                params["discounts"] = subscription_request.discounts
            if subscription_request.options:
                params["options"] = subscription_request.options
            
            result = braintree.Subscription.create(params)
            
            if result.is_success:
                subscription = result.subscription
                subscription_data = self._format_subscription(subscription)
                
                self.logger.info(f"Created subscription: {subscription.id}")
                return subscription_data
            else:
                error_msg = f"Failed to create subscription: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error creating subscription: {e}")
            raise

    async def update_subscription(
        self,
        subscription_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing subscription.
        
        Args:
            subscription_id: Subscription ID to update
            updates: Updates to apply
            
        Returns:
            Dict containing updated subscription details
        """
        try:
            result = braintree.Subscription.update(subscription_id, updates)
            
            if result.is_success:
                subscription = result.subscription
                subscription_data = self._format_subscription(subscription)
                
                self.logger.info(f"Updated subscription: {subscription_id}")
                return subscription_data
            else:
                error_msg = f"Failed to update subscription: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error updating subscription: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str
    ) -> Dict[str, Any]:
        """Cancel a subscription.
        
        Args:
            subscription_id: Subscription ID to cancel
            
        Returns:
            Dict containing cancellation result
        """
        try:
            result = braintree.Subscription.cancel(subscription_id)
            
            if result.is_success:
                subscription = result.subscription
                subscription_data = self._format_subscription(subscription)
                
                self.logger.info(f"Cancelled subscription: {subscription_id}")
                return subscription_data
            else:
                error_msg = f"Failed to cancel subscription: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error cancelling subscription: {e}")
            raise

    async def create_payment_method(
        self,
        customer_id: str,
        payment_method_nonce: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment method in the vault.
        
        Args:
            customer_id: Customer ID
            payment_method_nonce: Payment method nonce from frontend
            options: Additional options
            
        Returns:
            Dict containing payment method details
        """
        try:
            params = {
                "customer_id": customer_id,
                "payment_method_nonce": payment_method_nonce
            }
            
            if options:
                params["options"] = options
            
            result = braintree.PaymentMethod.create(params)
            
            if result.is_success:
                payment_method = result.payment_method
                payment_method_data = self._format_payment_method(payment_method)
                
                self.logger.info(f"Created payment method: {payment_method.token}")
                return payment_method_data
            else:
                error_msg = f"Failed to create payment method: {result.message}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error creating payment method: {e}")
            raise

    async def delete_payment_method(
        self,
        payment_method_token: str
    ) -> bool:
        """Delete a payment method from the vault.
        
        Args:
            payment_method_token: Payment method token to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = braintree.PaymentMethod.delete(payment_method_token)
            
            if result.is_success:
                self.logger.info(f"Deleted payment method: {payment_method_token}")
                return True
            else:
                self.logger.error(f"Failed to delete payment method: {result.message}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting payment method: {e}")
            return False

    def verify_webhook_signature(
        self,
        signature: str,
        payload: str
    ) -> bool:
        """Verify webhook signature from Braintree.
        
        Args:
            signature: Signature from webhook
            payload: Webhook payload
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            return braintree.WebhookNotification.verify(signature, payload)
        except Exception as e:
            self.logger.error(f"Error verifying webhook signature: {e}")
            return False

    async def parse_webhook(
        self,
        signature: str,
        payload: str
    ) -> Dict[str, Any]:
        """Parse and process webhook notification from Braintree.
        
        Args:
            signature: Webhook signature
            payload: Webhook payload
            
        Returns:
            Dict containing webhook data
        """
        try:
            webhook_notification = braintree.WebhookNotification.parse(signature, payload)
            
            webhook_data = {
                "kind": webhook_notification.kind,
                "timestamp": webhook_notification.timestamp.isoformat() if webhook_notification.timestamp else None,
            }
            
            # Handle different webhook types
            if webhook_notification.subscription:
                webhook_data["subscription"] = self._format_subscription(webhook_notification.subscription)
            
            if webhook_notification.transaction:
                webhook_data["transaction"] = self._format_transaction(webhook_notification.transaction)
            
            if webhook_notification.dispute:
                webhook_data["dispute"] = self._format_dispute(webhook_notification.dispute)
            
            if webhook_notification.disbursement:
                webhook_data["disbursement"] = self._format_disbursement(webhook_notification.disbursement)
            
            self.logger.info(f"Processed webhook: {webhook_notification.kind}")
            return webhook_data
            
        except Exception as e:
            self.logger.error(f"Error parsing webhook: {e}")
            raise

    def _format_transaction(self, transaction) -> Dict[str, Any]:
        """Format transaction object to dictionary."""
        return {
            "id": transaction.id,
            "amount": str(transaction.amount),
            "status": transaction.status,
            "type": transaction.type,
            "currency_iso_code": transaction.currency_iso_code,
            "merchant_account_id": transaction.merchant_account_id,
            "order_id": transaction.order_id,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
            "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
            "processor_response_code": transaction.processor_response_code,
            "processor_response_text": transaction.processor_response_text,
            "gateway_rejection_reason": transaction.gateway_rejection_reason,
            "credit_card": self._format_credit_card(transaction.credit_card) if transaction.credit_card else None,
            "paypal_account": self._format_paypal_account(transaction.paypal_details) if transaction.paypal_details else None,
            "customer": self._format_customer(transaction.customer_details) if transaction.customer_details else None,
            "billing": self._format_address(transaction.billing_details) if transaction.billing_details else None,
            "shipping": self._format_address(transaction.shipping_details) if transaction.shipping_details else None,
            "service_fee_amount": str(transaction.service_fee_amount) if transaction.service_fee_amount else None,
            "disbursement_details": self._format_disbursement_details(transaction.disbursement_details) if transaction.disbursement_details else None,
            "subscription_id": transaction.subscription_id
        }

    def _format_subscription(self, subscription) -> Dict[str, Any]:
        """Format subscription object to dictionary."""
        return {
            "id": subscription.id,
            "status": subscription.status,
            "price": str(subscription.price),
            "plan_id": subscription.plan_id,
            "merchant_id": subscription.merchant_id,
            "payment_method_token": subscription.payment_method_token,
            "created_at": subscription.created_at.isoformat() if subscription.created_at else None,
            "updated_at": subscription.updated_at.isoformat() if subscription.updated_at else None,
            "billing_period_start_date": subscription.billing_period_start_date.isoformat() if subscription.billing_period_start_date else None,
            "billing_period_end_date": subscription.billing_period_end_date.isoformat() if subscription.billing_period_end_date else None,
            "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
            "number_of_billing_cycles": subscription.number_of_billing_cycles,
            "trial_period": subscription.trial_period,
            "trial_duration": subscription.trial_duration,
            "trial_duration_unit": subscription.trial_duration_unit,
            "balance": str(subscription.balance) if subscription.balance else None,
            "paid_through_date": subscription.paid_through_date.isoformat() if subscription.paid_through_date else None
        }

    def _format_customer(self, customer) -> Dict[str, Any]:
        """Format customer object to dictionary."""
        return {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "company": customer.company,
            "email": customer.email,
            "phone": customer.phone,
            "fax": customer.fax,
            "website": customer.website
        }

    def _format_credit_card(self, credit_card) -> Dict[str, Any]:
        """Format credit card object to dictionary."""
        return {
            "token": credit_card.token,
            "bin": credit_card.bin,
            "last_4": credit_card.last_4,
            "card_type": credit_card.card_type,
            "expiration_month": credit_card.expiration_month,
            "expiration_year": credit_card.expiration_year,
            "customer_id": credit_card.customer_id,
            "cardholder_name": credit_card.cardholder_name,
            "created_at": credit_card.created_at.isoformat() if credit_card.created_at else None,
            "updated_at": credit_card.updated_at.isoformat() if credit_card.updated_at else None,
            "prepaid": credit_card.prepaid,
            "healthcare": credit_card.healthcare,
            "debit": credit_card.debit,
            "durbin_regulated": credit_card.durbin_regulated,
            "commercial": credit_card.commercial,
            "payroll": credit_card.payroll,
            "country_of_issuance": credit_card.country_of_issuance,
            "issuing_bank": credit_card.issuing_bank
        }

    def _format_paypal_account(self, paypal_account) -> Dict[str, Any]:
        """Format PayPal account object to dictionary."""
        return {
            "token": getattr(paypal_account, "token", None),
            "email": getattr(paypal_account, "email", None),
            "payer_id": getattr(paypal_account, "payer_id", None),
            "customer_id": getattr(paypal_account, "customer_id", None),
            "created_at": paypal_account.created_at.isoformat() if getattr(paypal_account, "created_at", None) else None,
            "updated_at": paypal_account.updated_at.isoformat() if getattr(paypal_account, "updated_at", None) else None
        }

    def _format_payment_method(self, payment_method) -> Dict[str, Any]:
        """Format payment method object to dictionary."""
        if hasattr(payment_method, "card_type"):  # Credit card
            return self._format_credit_card(payment_method)
        elif hasattr(payment_method, "email"):  # PayPal
            return self._format_paypal_account(payment_method)
        else:
            return {
                "token": payment_method.token,
                "customer_id": getattr(payment_method, "customer_id", None),
                "type": type(payment_method).__name__
            }

    def _format_address(self, address) -> Dict[str, Any]:
        """Format address object to dictionary."""
        return {
            "first_name": getattr(address, "first_name", None),
            "last_name": getattr(address, "last_name", None),
            "company": getattr(address, "company", None),
            "street_address": getattr(address, "street_address", None),
            "extended_address": getattr(address, "extended_address", None),
            "locality": getattr(address, "locality", None),
            "region": getattr(address, "region", None),
            "postal_code": getattr(address, "postal_code", None),
            "country_name": getattr(address, "country_name", None),
            "country_code_alpha2": getattr(address, "country_code_alpha2", None),
            "country_code_alpha3": getattr(address, "country_code_alpha3", None),
            "country_code_numeric": getattr(address, "country_code_numeric", None)
        }

    def _format_dispute(self, dispute) -> Dict[str, Any]:
        """Format dispute object to dictionary."""
        return {
            "id": dispute.id,
            "amount": str(dispute.amount),
            "currency_iso_code": dispute.currency_iso_code,
            "received_date": dispute.received_date.isoformat() if dispute.received_date else None,
            "reply_by_date": dispute.reply_by_date.isoformat() if dispute.reply_by_date else None,
            "kind": dispute.kind,
            "status": dispute.status,
            "reason": dispute.reason,
            "transaction_id": dispute.transaction.id if dispute.transaction else None,
            "case_number": dispute.case_number,
            "processor_comments": dispute.processor_comments,
            "merchant_account_id": dispute.merchant_account_id
        }

    def _format_disbursement(self, disbursement) -> Dict[str, Any]:
        """Format disbursement object to dictionary."""
        return {
            "id": disbursement.id,
            "amount": str(disbursement.amount),
            "exception_message": disbursement.exception_message,
            "disbursement_date": disbursement.disbursement_date.isoformat() if disbursement.disbursement_date else None,
            "follow_up_action": disbursement.follow_up_action,
            "merchant_account": disbursement.merchant_account,
            "transaction_ids": disbursement.transaction_ids,
            "success": disbursement.success,
            "retry": disbursement.retry
        }

    def _format_disbursement_details(self, disbursement_details) -> Dict[str, Any]:
        """Format disbursement details object to dictionary."""
        return {
            "disbursement_date": disbursement_details.disbursement_date.isoformat() if disbursement_details.disbursement_date else None,
            "settlement_amount": str(disbursement_details.settlement_amount) if disbursement_details.settlement_amount else None,
            "settlement_currency_iso_code": disbursement_details.settlement_currency_iso_code,
            "settlement_currency_exchange_rate": str(disbursement_details.settlement_currency_exchange_rate) if disbursement_details.settlement_currency_exchange_rate else None,
            "funds_held": disbursement_details.funds_held,
            "success": disbursement_details.success
        }

    async def close(self) -> None:
        """Close the HTTP session."""
        await self.session.aclose()

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Creator monetization specific functions
async def create_creator_marketplace_transaction(
    processor: BraintreePaymentProcessor,
    total_amount: Decimal,
    creator_percentage: float,
    platform_percentage: float,
    creator_merchant_account: str,
    platform_merchant_account: str,
    payment_method_nonce: str,
    customer_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create marketplace transaction for creator monetization.
    
    Args:
        processor: Braintree payment processor instance
        total_amount: Total payment amount
        creator_percentage: Creator's percentage (0-100)
        platform_percentage: Platform's percentage (0-100)
        creator_merchant_account: Creator's sub-merchant account
        platform_merchant_account: Platform's master merchant account
        payment_method_nonce: Payment method nonce
        customer_id: Customer ID (optional)
        
    Returns:
        Dict containing transaction details
    """
    creator_amount = total_amount * Decimal(str(creator_percentage / 100))
    platform_fee = total_amount * Decimal(str(platform_percentage / 100))
    
    # Create main transaction to creator's account
    main_transaction = BraintreeTransactionRequest(
        amount=creator_amount,
        payment_method_nonce=payment_method_nonce,
        merchant_account_id=creator_merchant_account,
        customer_id=customer_id,
        submit_for_settlement=True,
        service_fee_amount=platform_fee,
        options={
            "hold_in_escrow": True
        }
    )
    
    return await processor.process_transaction(main_transaction)


async def setup_creator_subscription_plan(
    processor: BraintreePaymentProcessor,
    creator_id: str,
    subscriber_reference: str,
    tier_amount: Decimal,
    payment_method_token: str,
    plan_id: str
) -> Dict[str, Any]:
    """Setup creator subscription with Braintree.
    
    Args:
        processor: Braintree payment processor instance
        creator_id: Creator identifier
        subscriber_reference: Subscriber reference
        tier_amount: Subscription tier amount
        payment_method_token: Payment method token
        plan_id: Subscription plan ID
        
    Returns:
        Dict containing subscription details
    """
    subscription_request = BraintreeSubscriptionRequest(
        payment_method_token=payment_method_token,
        plan_id=plan_id,
        price=tier_amount,
        id=f"creator_{creator_id}_sub_{subscriber_reference}"
    )
    
    return await processor.create_subscription(subscription_request)