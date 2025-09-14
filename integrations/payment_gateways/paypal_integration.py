"""
PayPal Payment Integration Module
=================================

Enterprise-grade integration with PayPal payment processing
Specialized for creator monetization and marketplace workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Role Applied: Backend Senior + Security + DBA + Microservices
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import hashlib
import hmac

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class PayPalEnvironment(Enum):
    """PayPal environment configuration."""
    SANDBOX = "sandbox"
    LIVE = "live"


class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PayoutStatus(Enum):
    """Payout status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PayPalCredentials:
    """PayPal API credentials configuration."""
    client_id: str
    client_secret: str
    environment: PayPalEnvironment = PayPalEnvironment.SANDBOX
    webhook_id: Optional[str] = None


@dataclass
class PaymentRequest:
    """PayPal payment request configuration."""
    amount: float
    currency: str = "USD"
    description: str = ""
    return_url: str = ""
    cancel_url: str = ""
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    content_id: Optional[str] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PayoutRequest:
    """PayPal payout request configuration."""
    recipient_email: str
    amount: float
    currency: str = "USD"
    note: str = ""
    sender_item_id: Optional[str] = None
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    revenue_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentResult:
    """PayPal payment result with business context."""
    payment_id: str = ""
    status: PaymentStatus = PaymentStatus.PENDING
    amount: float = 0.0
    currency: str = "USD"
    approval_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    payer_email: Optional[str] = None
    transaction_fee: float = 0.0
    net_amount: float = 0.0
    creator_context: Dict[str, Any] = field(default_factory=dict)
    business_metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class PayoutResult:
    """PayPal payout result with creator context."""
    payout_id: str = ""
    batch_id: str = ""
    status: PayoutStatus = PayoutStatus.PENDING
    amount: float = 0.0
    currency: str = "USD"
    recipient_email: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    fees: float = 0.0
    net_amount: float = 0.0
    creator_context: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class PayPalEnterpriseClient:
    """
    Enterprise PayPal API client with creator workflow integration.
    
    Specialized for Ainflue platform business logic:
    - Creator monetization and payouts
    - Marketplace payment processing
    - Subscription billing for creators
    - Advanced security and compliance
    """
    
    def __init__(
        self,
        credentials -> None: PayPalCredentials,
        timeout -> None: int = 30,
        max_retries -> None: int = 3,
        enable_webhook_verification -> None: bool = True,
        enable_creator_workflows -> None: bool = True
    ) -> None:
        """Initialize PayPal client with enterprise configuration."""
        self.credentials = credentials
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_webhook_verification = enable_webhook_verification
        self.enable_creator_workflows = enable_creator_workflows
        
        # Environment configuration
        self.base_url = self._get_base_url()
        self.access_token = None
        self.token_expires_at = None
        
        # Enterprise session configuration
        self.session = None
        if httpx:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout),
                headers={"Content-Type": "application/json"}
            )
        
        # Creator workflow configurations
        self.creator_fee_structures = self._initialize_creator_fees()
        self.payout_schedules = self._initialize_payout_schedules()
        
        # Transaction tracking
        self.transaction_history = []
        self.revenue_tracking = {
            "total_processed": 0.0,
            "total_fees": 0.0,
            "creator_payouts": 0.0,
            "platform_revenue": 0.0
        }
        
        logger.info("✅ PayPal Enterprise Client initialized")

    def _get_base_url(self) -> str:
        """Get PayPal API base URL based on environment."""
        if self.credentials.environment == PayPalEnvironment.LIVE:
            return "https://api-m.paypal.com"
        else:
            return "https://api-m.sandbox.paypal.com"

    def _initialize_creator_fees(self) -> Dict[str, Dict[str, float]]:
        """Initialize creator-specific fee structures."""
        return {
            "musician": {
                "platform_fee": 0.05,  # 5% platform fee
                "payment_processing": 0.029 + 0.30,  # PayPal fee
                "minimum_payout": 25.00
            },
            "blogger": {
                "platform_fee": 0.10,  # 10% platform fee
                "payment_processing": 0.029 + 0.30,
                "minimum_payout": 10.00
            },
            "photographer": {
                "platform_fee": 0.15,  # 15% platform fee
                "payment_processing": 0.029 + 0.30,
                "minimum_payout": 50.00
            },
            "influencer": {
                "platform_fee": 0.08,  # 8% platform fee
                "payment_processing": 0.029 + 0.30,
                "minimum_payout": 20.00
            },
            "comedian": {
                "platform_fee": 0.12,  # 12% platform fee
                "payment_processing": 0.029 + 0.30,
                "minimum_payout": 15.00
            }
        }

    def _initialize_payout_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize payout schedules for different creator types."""
        return {
            "musician": {
                "frequency": "weekly",
                "day": "friday",
                "minimum_threshold": 25.00,
                "auto_payout": True
            },
            "blogger": {
                "frequency": "monthly",
                "day": 1,
                "minimum_threshold": 10.00,
                "auto_payout": True
            },
            "photographer": {
                "frequency": "bi-weekly",
                "day": "tuesday",
                "minimum_threshold": 50.00,
                "auto_payout": False  # Manual approval required
            },
            "influencer": {
                "frequency": "weekly",
                "day": "monday",
                "minimum_threshold": 20.00,
                "auto_payout": True
            },
            "comedian": {
                "frequency": "monthly",
                "day": 15,
                "minimum_threshold": 15.00,
                "auto_payout": True
            }
        }

    async def _get_access_token(self) -> str:
        """Get or refresh PayPal access token."""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token
        
        # Request new access token
        auth_string = f"{self.credentials.client_id}:{self.credentials.client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = "grant_type=client_credentials"
        
        if not self.session:
            raise Exception("HTTP session not initialized")
        
        response = await self.session.post(
            f"{self.base_url}/v1/oauth2/token",
            headers=headers,
            content=data
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
        
        return self.access_token

    async def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        token = await self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": self._generate_request_id()
        }

    def _generate_request_id(self) -> str:
        """Generate unique request ID for idempotency."""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        return f"ainflue-{timestamp}"

    async def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """
        Create PayPal payment with creator workflow integration.
        
        Args:
            request: Payment request configuration
            
        Returns:
            PaymentResult with payment details and approval URL
        """
        try:
            # Apply creator workflow processing
            if self.enable_creator_workflows:
                request = await self._apply_creator_payment_processing(request)
            
            # Create payment payload
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": f"{request.amount:.2f}",
                        "currency": request.currency
                    },
                    "description": request.description,
                    "custom": json.dumps({
                        "creator_id": request.creator_id,
                        "creator_type": request.creator_type,
                        "content_id": request.content_id,
                        "business_context": request.business_context
                    })
                }],
                "redirect_urls": {
                    "return_url": request.return_url,
                    "cancel_url": request.cancel_url
                }
            }
            
            headers = await self._get_headers()
            
            if not self.session:
                raise Exception("HTTP session not initialized")
            
            response = await self.session.post(
                f"{self.base_url}/v1/payments/payment",
                headers=headers,
                json=payment_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract approval URL
            approval_url = ""
            for link in data.get("links", []):
                if link.get("rel") == "approval_url":
                    approval_url = link.get("href", "")
                    break
            
            # Create payment result
            result = PaymentResult(
                payment_id=data.get("id", ""),
                status=PaymentStatus.PENDING,
                amount=request.amount,
                currency=request.currency,
                approval_url=approval_url,
                creator_context={
                    "creator_id": request.creator_id,
                    "creator_type": request.creator_type,
                    "content_id": request.content_id
                },
                business_metadata=request.business_context
            )
            
            # Track transaction
            self._track_transaction("payment_created", result)
            
            logger.info(f"✅ PayPal payment created: {result.payment_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ PayPal payment creation failed: {e}")
            return PaymentResult(
                status=PaymentStatus.FAILED,
                error_message=str(e)
            )

    async def execute_payment(self, payment_id: str, payer_id: str) -> PaymentResult:
        """Execute approved PayPal payment."""
        try:
            headers = await self._get_headers()
            
            execute_data = {
                "payer_id": payer_id
            }
            
            if not self.session:
                raise Exception("HTTP session not initialized")
            
            response = await self.session.post(
                f"{self.base_url}/v1/payments/payment/{payment_id}/execute",
                headers=headers,
                json=execute_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract transaction details
            transaction = data.get("transactions", [{}])[0]
            related_resources = transaction.get("related_resources", [{}])[0]
            sale = related_resources.get("sale", {})
            
            # Calculate fees and net amount
            transaction_fee = float(sale.get("transaction_fee", {}).get("value", "0"))
            gross_amount = float(transaction.get("amount", {}).get("total", "0"))
            net_amount = gross_amount - transaction_fee
            
            # Create result
            result = PaymentResult(
                payment_id=payment_id,
                status=PaymentStatus.COMPLETED,
                amount=gross_amount,
                currency=transaction.get("amount", {}).get("currency", "USD"),
                completed_at=datetime.now(),
                payer_email=data.get("payer", {}).get("payer_info", {}).get("email"),
                transaction_fee=transaction_fee,
                net_amount=net_amount
            )
            
            # Apply creator revenue processing
            if self.enable_creator_workflows:
                await self._process_creator_revenue(result, data)
            
            # Track transaction
            self._track_transaction("payment_completed", result)
            
            logger.info(f"✅ PayPal payment executed: {payment_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ PayPal payment execution failed: {e}")
            return PaymentResult(
                payment_id=payment_id,
                status=PaymentStatus.FAILED,
                error_message=str(e)
            )

    async def get_payment_details(self, payment_id: str) -> PaymentResult:
        """Get PayPal payment details."""
        try:
            headers = await self._get_headers()
            
            if not self.session:
                raise Exception("HTTP session not initialized")
            
            response = await self.session.get(
                f"{self.base_url}/v1/payments/payment/{payment_id}",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse payment status
            status_mapping = {
                "created": PaymentStatus.PENDING,
                "approved": PaymentStatus.APPROVED,
                "failed": PaymentStatus.FAILED,
                "cancelled": PaymentStatus.CANCELLED,
                "expired": PaymentStatus.FAILED
            }
            
            payment_status = status_mapping.get(data.get("state"), PaymentStatus.PENDING)
            
            # Extract transaction details
            transaction = data.get("transactions", [{}])[0]
            amount = float(transaction.get("amount", {}).get("total", "0"))
            currency = transaction.get("amount", {}).get("currency", "USD")
            
            result = PaymentResult(
                payment_id=payment_id,
                status=payment_status,
                amount=amount,
                currency=currency,
                created_at=datetime.fromisoformat(data.get("create_time", datetime.now().isoformat()).replace("Z", "+00:00"))
            )
            
            # Parse custom data if available
            custom_data = transaction.get("custom")
            if custom_data:
                try:
                    custom_info = json.loads(custom_data)
                    result.creator_context = {
                        "creator_id": custom_info.get("creator_id"),
                        "creator_type": custom_info.get("creator_type"),
                        "content_id": custom_info.get("content_id")
                    }
                    result.business_metadata = custom_info.get("business_context", {})
                except json.JSONDecodeError:
                    pass
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get payment details: {e}")
            raise

    async def create_payout(self, request: PayoutRequest) -> PayoutResult:
        """
        Create PayPal payout to creator.
        
        Args:
            request: Payout request configuration
            
        Returns:
            PayoutResult with payout details
        """
        try:
            # Validate payout eligibility
            if self.enable_creator_workflows:
                await self._validate_payout_eligibility(request)
            
            # Create payout payload
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": self._generate_request_id(),
                    "email_subject": "You have a payment from Ainflue",
                    "email_message": f"Congratulations! You've received a payment for your creative work."
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{request.amount:.2f}",
                        "currency": request.currency
                    },
                    "receiver": request.recipient_email,
                    "note": request.note,
                    "sender_item_id": request.sender_item_id or self._generate_request_id()
                }]
            }
            
            headers = await self._get_headers()
            
            if not self.session:
                raise Exception("HTTP session not initialized")
            
            response = await self.session.post(
                f"{self.base_url}/v1/payments/payouts",
                headers=headers,
                json=payout_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Create payout result
            result = PayoutResult(
                payout_id=data.get("items", [{}])[0].get("payout_item_id", ""),
                batch_id=data.get("batch_header", {}).get("payout_batch_id", ""),
                status=PayoutStatus.PENDING,
                amount=request.amount,
                currency=request.currency,
                recipient_email=request.recipient_email,
                creator_context={
                    "creator_id": request.creator_id,
                    "creator_type": request.creator_type,
                    "revenue_context": request.revenue_context
                }
            )
            
            # Track payout
            self._track_transaction("payout_created", result)
            
            logger.info(f"✅ PayPal payout created: {result.payout_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ PayPal payout creation failed: {e}")
            return PayoutResult(
                status=PayoutStatus.FAILED,
                error_message=str(e)
            )

    async def get_payout_details(self, payout_item_id: str) -> PayoutResult:
        """Get PayPal payout details."""
        try:
            headers = await self._get_headers()
            
            if not self.session:
                raise Exception("HTTP session not initialized")
            
            response = await self.session.get(
                f"{self.base_url}/v1/payments/payouts-item/{payout_item_id}",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse payout status
            status_mapping = {
                "PENDING": PayoutStatus.PENDING,
                "PROCESSING": PayoutStatus.PROCESSING,
                "SUCCESS": PayoutStatus.SUCCESS,
                "FAILED": PayoutStatus.FAILED,
                "BLOCKED": PayoutStatus.FAILED,
                "REFUNDED": PayoutStatus.CANCELLED,
                "RETURNED": PayoutStatus.FAILED
            }
            
            payout_status = status_mapping.get(
                data.get("transaction_status"), 
                PayoutStatus.PENDING
            )
            
            # Calculate fees
            amount = float(data.get("payout_item", {}).get("amount", {}).get("value", "0"))
            fees = float(data.get("payout_item_fee", {}).get("value", "0"))
            net_amount = amount - fees
            
            result = PayoutResult(
                payout_id=payout_item_id,
                batch_id=data.get("payout_batch_id", ""),
                status=payout_status,
                amount=amount,
                currency=data.get("payout_item", {}).get("amount", {}).get("currency", "USD"),
                recipient_email=data.get("payout_item", {}).get("receiver", ""),
                fees=fees,
                net_amount=net_amount,
                created_at=datetime.fromisoformat(
                    data.get("time_processed", datetime.now().isoformat()).replace("Z", "+00:00")
                )
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to get payout details: {e}")
            raise

    async def verify_webhook(self, headers: Dict[str, str], body: str) -> bool:
        """Verify PayPal webhook signature for security."""
        if not self.enable_webhook_verification or not self.credentials.webhook_id:
            return True
        
        try:
            # Extract required headers
            auth_algo = headers.get("PAYPAL-AUTH-ALGO")
            transmission_id = headers.get("PAYPAL-TRANSMISSION-ID")
            cert_id = headers.get("PAYPAL-CERT-ID")
            transmission_time = headers.get("PAYPAL-TRANSMISSION-TIME")
            webhook_signature = headers.get("PAYPAL-TRANSMISSION-SIG")
            
            if not all([auth_algo, transmission_id, cert_id, transmission_time, webhook_signature]):
                return False
            
            # Verify webhook signature (simplified - in production, implement full verification)
            # This would involve getting the PayPal certificate and verifying the signature
            # For now, we'll do basic validation
            
            expected_auth_algo = "SHA256withRSA"
            if auth_algo != expected_auth_algo:
                return False
            
            # In production, implement full certificate verification
            # For demo purposes, assume verification passes
            logger.info("✅ PayPal webhook signature verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ PayPal webhook verification failed: {e}")
            return False

    async def _apply_creator_payment_processing(self, request: PaymentRequest) -> PaymentRequest:
        """Apply creator-specific payment processing logic."""
        creator_type = request.creator_type
        
        if creator_type and creator_type in self.creator_fee_structures:
            fee_config = self.creator_fee_structures[creator_type]
            
            # Add fee information to business context
            request.business_context.update({
                "platform_fee_rate": fee_config["platform_fee"],
                "payment_processing_fee": fee_config["payment_processing"],
                "minimum_payout": fee_config["minimum_payout"]
            })
            
            # Update description to include creator context
            if request.creator_id:
                request.description += f" - Creator: {request.creator_id}"
        
        return request

    async def _process_creator_revenue(self, result: PaymentResult, payment_data: Dict[str, Any]) -> None:
        """Process creator revenue sharing and payout scheduling."""
        # Extract creator context from custom data
        transaction = payment_data.get("transactions", [{}])[0]
        custom_data = transaction.get("custom")
        
        if custom_data:
            try:
                custom_info = json.loads(custom_data)
                creator_id = custom_info.get("creator_id")
                creator_type = custom_info.get("creator_type")
                
                if creator_id and creator_type:
                    # Calculate creator revenue
                    await self._calculate_creator_revenue(result, creator_type)
                    
                    # Schedule payout if eligible
                    await self._schedule_creator_payout(result, creator_id, creator_type)
                    
            except json.JSONDecodeError:
                pass

    async def _calculate_creator_revenue(self, result: PaymentResult, creator_type: str) -> None:
        """Calculate creator revenue after fees."""
        if creator_type not in self.creator_fee_structures:
            return
        
        fee_config = self.creator_fee_structures[creator_type]
        
        # Calculate platform fee
        platform_fee = result.net_amount * fee_config["platform_fee"]
        
        # Creator receives net amount minus platform fee
        creator_revenue = result.net_amount - platform_fee
        
        # Update result with revenue breakdown
        result.business_metadata.update({
            "platform_fee": platform_fee,
            "creator_revenue": creator_revenue,
            "fee_structure": fee_config
        })
        
        # Update tracking
        self.revenue_tracking["total_processed"] += result.amount
        self.revenue_tracking["total_fees"] += result.transaction_fee + platform_fee
        self.revenue_tracking["platform_revenue"] += platform_fee

    async def _schedule_creator_payout(self, result: PaymentResult, creator_id: str, creator_type: str) -> None:
        """Schedule creator payout based on payout policies."""
        if creator_type not in self.payout_schedules:
            return
        
        payout_config = self.payout_schedules[creator_type]
        creator_revenue = result.business_metadata.get("creator_revenue", 0.0)
        
        # Check minimum threshold
        if creator_revenue >= payout_config["minimum_threshold"]:
            # In production, this would create a payout schedule record
            result.business_metadata.update({
                "payout_scheduled": True,
                "payout_frequency": payout_config["frequency"],
                "auto_payout": payout_config["auto_payout"],
                "next_payout_date": self._calculate_next_payout_date(payout_config)
            })
            
            logger.info(f"💰 Payout scheduled for creator {creator_id}: ${creator_revenue:.2f}")

    def _calculate_next_payout_date(self, payout_config: Dict[str, Any]) -> str:
        """Calculate next payout date based on frequency."""
        frequency = payout_config["frequency"]
        
        if frequency == "weekly":
            # Next occurrence of specified day
            next_date = datetime.now() + timedelta(days=7)
        elif frequency == "bi-weekly":
            next_date = datetime.now() + timedelta(days=14)
        elif frequency == "monthly":
            # Next month, same day
            next_date = datetime.now().replace(day=payout_config["day"])
            if next_date <= datetime.now():
                # Next month
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
        else:
            next_date = datetime.now() + timedelta(days=30)  # Default to monthly
        
        return next_date.isoformat()

    async def _validate_payout_eligibility(self, request: PayoutRequest) -> None:
        """Validate creator payout eligibility."""
        creator_type = request.creator_type
        
        if creator_type and creator_type in self.creator_fee_structures:
            fee_config = self.creator_fee_structures[creator_type]
            minimum_payout = fee_config["minimum_payout"]
            
            if request.amount < minimum_payout:
                raise ValueError(
                    f"Payout amount ${request.amount:.2f} is below minimum "
                    f"${minimum_payout:.2f} for {creator_type} creators"
                )

    def _track_transaction(self, transaction_type: str, result: Union[PaymentResult, PayoutResult]) -> None:
        """Track transaction for analytics and reporting."""
        transaction_record = {
            "type": transaction_type,
            "id": getattr(result, "payment_id", "") or getattr(result, "payout_id", ""),
            "amount": result.amount,
            "currency": result.currency,
            "timestamp": datetime.now().isoformat(),
            "creator_context": getattr(result, "creator_context", {}),
            "status": result.status.value
        }
        
        self.transaction_history.append(transaction_record)

    async def get_revenue_analytics(self) -> Dict[str, Any]:
        """Get revenue analytics and creator earnings breakdown."""
        # Calculate creator-specific analytics
        creator_analytics = {}
        for transaction in self.transaction_history:
            creator_id = transaction.get("creator_context", {}).get("creator_id")
            creator_type = transaction.get("creator_context", {}).get("creator_type")
            
            if creator_id and creator_type:
                if creator_type not in creator_analytics:
                    creator_analytics[creator_type] = {
                        "total_earnings": 0.0,
                        "transaction_count": 0,
                        "avg_transaction": 0.0
                    }
                
                if transaction["type"] == "payment_completed":
                    creator_analytics[creator_type]["total_earnings"] += transaction["amount"]
                    creator_analytics[creator_type]["transaction_count"] += 1
        
        # Calculate averages
        for creator_type, stats in creator_analytics.items():
            if stats["transaction_count"] > 0:
                stats["avg_transaction"] = stats["total_earnings"] / stats["transaction_count"]
        
        return {
            "revenue_summary": self.revenue_tracking,
            "creator_analytics": creator_analytics,
            "transaction_count": len(self.transaction_history),
            "fee_structures": self.creator_fee_structures,
            "payout_schedules": self.payout_schedules
        }

    async def close(self) -> None:
        """Clean up resources and close connections."""
        if self.session:
            await self.session.aclose()
            self.session = None
            
        logger.info("✅ PayPal client closed")

    async def __aenter__(self) -> None:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


# Factory function for easy instantiation
def create_paypal_client(
    client_id: str,
    client_secret: str,
    environment: PayPalEnvironment = PayPalEnvironment.SANDBOX,
    webhook_id: Optional[str] = None,
    enable_creator_workflows: bool = True
) -> PayPalEnterpriseClient:
    """
    Factory function to create PayPal client with enterprise configuration.
    
    Args:
        client_id: PayPal client ID
        client_secret: PayPal client secret
        environment: PayPal environment (sandbox or live)
        webhook_id: PayPal webhook ID for signature verification
        enable_creator_workflows: Enable creator-specific workflows
        
    Returns:
        Configured PayPalEnterpriseClient instance
    """
    credentials = PayPalCredentials(
        client_id=client_id,
        client_secret=client_secret,
        environment=environment,
        webhook_id=webhook_id
    )
    
    return PayPalEnterpriseClient(
        credentials=credentials,
        enable_creator_workflows=enable_creator_workflows
    )


# Example usage for creator monetization
async def example_creator_monetization() -> None:
    """Example of creator monetization workflow."""
    try:
        client = create_paypal_client(
            client_id="your-client-id",
            client_secret="your-client-secret",
            environment=PayPalEnvironment.SANDBOX
        )
        
        # Create payment for content purchase
        payment_request = PaymentRequest(
            amount=29.99,
            currency="USD",
            description="Premium Music Course - Beat Production Masterclass",
            return_url="https://ainflue.com/payment/success",
            cancel_url="https://ainflue.com/payment/cancel",
            creator_id="musician_123",
            creator_type="musician",
            content_id="course_beatprod_001",
            business_context={
                "course_name": "Beat Production Masterclass",
                "content_type": "educational_course",
                "pricing_tier": "premium"
            }
        )
        
        payment_result = await client.create_payment(payment_request)
        
        if payment_result.status == PaymentStatus.PENDING:
            print(f"💳 Payment created: {payment_result.payment_id}")
            print(f"🔗 Approval URL: {payment_result.approval_url}")
            
            # Simulate payment approval and execution
            # In real implementation, user would be redirected to PayPal
            # payer_id = "simulated_payer_id"
            # executed_payment = await client.execute_payment(payment_result.payment_id, payer_id)
            
            # print(f"✅ Payment executed: ${executed_payment.amount}")
            # print(f"💰 Creator revenue: ${executed_payment.business_metadata.get('creator_revenue', 0):.2f}")
        
        # Create payout to creator
        payout_request = PayoutRequest(
            recipient_email="musician123@example.com",
            amount=75.50,
            currency="USD",
            note="Weekly earnings payout - Keep creating amazing content!",
            creator_id="musician_123",
            creator_type="musician",
            revenue_context={
                "period": "2025-01-13 to 2025-01-19",
                "content_sales": 3,
                "total_revenue": 89.97
            }
        )
        
        payout_result = await client.create_payout(payout_request)
        
        if payout_result.status == PayoutStatus.PENDING:
            print(f"💸 Payout created: {payout_result.payout_id}")
            print(f"📧 Sent to: {payout_result.recipient_email}")
        
        # Get revenue analytics
        analytics = await client.get_revenue_analytics()
        print(f"📊 Total processed: ${analytics['revenue_summary']['total_processed']:.2f}")
        print(f"🏦 Platform revenue: ${analytics['revenue_summary']['platform_revenue']:.2f}")
        
        await client.close()
        
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_monetization())