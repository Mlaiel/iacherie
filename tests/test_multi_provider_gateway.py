"""Test suite for Multi-Provider Payment Gateway
============================================

Comprehensive tests for the unified payment gateway covering all payment providers
and payment types: marketplace splits, escrow, international transfers, and crypto.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
import uuid

from payment.multi_provider_gateway import (
    MultiProviderPaymentGateway,
    PaymentRequest,
    PaymentResponse,
    PaymentProvider,
    PaymentType,
    PaymentStatus
)


class TestMultiProviderPaymentGateway:
    """Test suite for Multi-Provider Payment Gateway"""
    
    @pytest.fixture
    def gateway_config(self):
        """Gateway configuration for testing"""
        return {
            "stripe": {
                "api_key": "sk_test_123456789",
                "webhook_secret": "whsec_test_123456789"
            },
            "paypal": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "environment": "sandbox"
            },
            "wise": {
                "api_token": "test_wise_token",
                "webhook_secret": "wise_webhook_secret"
            },
            "crypto": {
                "api_keys": {
                    "coinbase": "test_coinbase_key",
                    "bitcoin": "test_bitcoin_key"
                },
                "webhook_secret": "crypto_webhook_secret",
                "testnet": True
            }
        }
    
    @pytest.fixture
    async def gateway(self, gateway_config):
        """Create payment gateway instance"""
        gateway = MultiProviderPaymentGateway(gateway_config)
        return gateway
    
    @pytest.mark.asyncio
    async def test_marketplace_split_payment(self, gateway):
        """Test Stripe Connect marketplace split payment"""
        request = PaymentRequest(
            amount=Decimal("100.00"),
            currency="USD",
            payment_type=PaymentType.MARKETPLACE_SPLIT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="cus_sender123",
            recipient_id="acct_recipient123",
            description="Marketplace split payment test",
            platform_fee_percent=Decimal("0.05"),  # 5% platform fee
            recipients=[
                {"account_id": "acct_recipient123", "amount": Decimal("95.00")},
                {"account_id": "platform", "amount": Decimal("5.00")}
            ]
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.PENDING
        assert response.provider == PaymentProvider.STRIPE_CONNECT
        assert response.amount == Decimal("100.00")
        assert response.currency == "USD"
        assert "platform_fee" in response.fees
        assert response.fees["platform_fee"] == Decimal("5.00")
        assert response.transaction_id.startswith("mp_")
        assert response.provider_transaction_id is not None
    
    @pytest.mark.asyncio
    async def test_paypal_escrow_payment(self, gateway):
        """Test PayPal Business escrow payment"""
        release_date = datetime.now() + timedelta(days=30)
        
        request = PaymentRequest(
            amount=Decimal("500.00"),
            currency="USD",
            payment_type=PaymentType.ESCROW_PAYMENT,
            provider=PaymentProvider.PAYPAL_BUSINESS,
            sender_id="buyer123",
            recipient_id="seller456",
            description="Service delivery escrow",
            escrow_release_date=release_date,
            escrow_conditions={"delivery_required": True, "quality_check": True},
            metadata={"recipient_email": "seller@example.com"}
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.ESCROWED
        assert response.provider == PaymentProvider.PAYPAL_BUSINESS
        assert response.amount == Decimal("500.00")
        assert response.currency == "USD"
        assert response.escrow_id is not None
        assert response.escrow_id.startswith("escrow_")
        assert "paypal_fee" in response.fees
        assert response.transaction_id.startswith("esc_")
    
    @pytest.mark.asyncio
    async def test_escrow_release(self, gateway):
        """Test escrow release functionality"""
        # First create an escrow payment
        release_date = datetime.now() + timedelta(days=30)
        
        request = PaymentRequest(
            amount=Decimal("250.00"),
            currency="EUR",
            payment_type=PaymentType.ESCROW_PAYMENT,
            provider=PaymentProvider.PAYPAL_BUSINESS,
            sender_id="buyer789",
            recipient_id="seller012",
            description="Product delivery escrow",
            escrow_release_date=release_date,
            escrow_conditions={"product_delivered": True},
            metadata={"recipient_email": "seller012@example.com"}
        )
        
        payment_response = await gateway.process_payment(request)
        escrow_id = payment_response.escrow_id
        
        # Now release the escrow
        release_conditions = {
            "product_delivered": True,
            "quality_approved": True,
            "released_by": "buyer789"
        }
        
        release_result = await gateway.release_escrow(escrow_id, release_conditions)
        
        assert release_result["success"] is True
        assert release_result["escrow_id"] == escrow_id
        assert release_result["amount"] == Decimal("250.00")
        assert release_result["currency"] == "EUR"
        assert "released_at" in release_result
    
    @pytest.mark.asyncio
    async def test_wise_international_transfer(self, gateway):
        """Test Wise international transfer"""
        request = PaymentRequest(
            amount=Decimal("1000.00"),
            currency="USD",
            payment_type=PaymentType.INTERNATIONAL_TRANSFER,
            provider=PaymentProvider.WISE,
            sender_id="user_us",
            recipient_id="user_eu",
            description="International freelancer payment",
            recipient_country="DE",
            transfer_purpose="digital_services",
            metadata={"target_currency": "EUR"}
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.PENDING
        assert response.provider == PaymentProvider.WISE
        assert response.amount == Decimal("1000.00")
        assert response.currency == "USD"
        assert "wise_fee" in response.fees
        assert "exchange_rate" in response.fees
        assert response.transaction_id.startswith("wise_")
    
    @pytest.mark.asyncio
    async def test_crypto_transfer_bitcoin(self, gateway):
        """Test Bitcoin cryptocurrency transfer"""
        request = PaymentRequest(
            amount=Decimal("0.01"),
            currency="BTC",
            payment_type=PaymentType.CRYPTO_TRANSFER,
            provider=PaymentProvider.CRYPTO,
            sender_id="crypto_user1",
            recipient_id="crypto_user2",
            description="Bitcoin payment for NFT",
            from_address="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            to_address="1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
            network="bitcoin"
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.PENDING
        assert response.provider == PaymentProvider.CRYPTO
        assert response.amount == Decimal("0.01")
        assert response.currency == "BTC"
        assert "network_fee" in response.fees
        assert "processing_fee" in response.fees
        assert response.transaction_id.startswith("crypto_")
    
    @pytest.mark.asyncio
    async def test_crypto_transfer_ethereum(self, gateway):
        """Test Ethereum cryptocurrency transfer"""
        request = PaymentRequest(
            amount=Decimal("0.5"),
            currency="ETH",
            payment_type=PaymentType.CRYPTO_TRANSFER,
            provider=PaymentProvider.CRYPTO,
            sender_id="eth_user1",
            recipient_id="eth_user2",
            description="Ethereum payment for services",
            from_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4d",
            to_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4e",
            network="ethereum"
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.PENDING
        assert response.provider == PaymentProvider.CRYPTO
        assert response.amount == Decimal("0.5")
        assert response.currency == "ETH"
        assert response.transaction_id.startswith("crypto_")
    
    @pytest.mark.asyncio
    async def test_crypto_transfer_usdc(self, gateway):
        """Test USDC stablecoin transfer"""
        request = PaymentRequest(
            amount=Decimal("1000.00"),
            currency="USDC",
            payment_type=PaymentType.CRYPTO_TRANSFER,
            provider=PaymentProvider.CRYPTO,
            sender_id="usdc_user1",
            recipient_id="usdc_user2",
            description="USDC payment for subscription",
            from_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4d",
            to_address="0x742d35cc694c048e5b1b1e6c9dcaa9999e2b8b4f",
            network="ethereum"  # USDC on Ethereum
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.PENDING
        assert response.provider == PaymentProvider.CRYPTO
        assert response.amount == Decimal("1000.00")
        assert response.currency == "USDC"
        assert response.transaction_id.startswith("crypto_")
    
    @pytest.mark.asyncio
    async def test_simple_payment(self, gateway):
        """Test simple payment processing"""
        request = PaymentRequest(
            amount=Decimal("50.00"),
            currency="USD",
            payment_type=PaymentType.SIMPLE_PAYMENT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="simple_sender",
            recipient_id="simple_recipient",
            description="Simple payment test"
        )
        
        response = await gateway.process_payment(request)
        
        assert response.status == PaymentStatus.PENDING
        assert response.provider == PaymentProvider.STRIPE_CONNECT
        assert response.amount == Decimal("50.00")
        assert response.currency == "USD"
        assert "stripe_fee" in response.fees
        assert response.transaction_id.startswith("simple_")
    
    @pytest.mark.asyncio
    async def test_transaction_status_tracking(self, gateway):
        """Test transaction status tracking"""
        request = PaymentRequest(
            amount=Decimal("75.00"),
            currency="USD",
            payment_type=PaymentType.SIMPLE_PAYMENT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="status_sender",
            recipient_id="status_recipient",
            description="Status tracking test"
        )
        
        response = await gateway.process_payment(request)
        transaction_id = response.transaction_id
        
        # Get transaction status
        status = await gateway.get_transaction_status(transaction_id)
        
        assert status["transaction_id"] == transaction_id
        assert status["status"] == PaymentStatus.PENDING.value
        assert status["provider"] == PaymentProvider.STRIPE_CONNECT.value
        assert status["amount"] == 75.00
        assert status["currency"] == "USD"
        assert "fees" in status
        assert "provider_status" in status
    
    @pytest.mark.asyncio
    async def test_payment_validation_negative_amount(self, gateway):
        """Test payment validation for negative amounts"""
        request = PaymentRequest(
            amount=Decimal("-10.00"),
            currency="USD",
            payment_type=PaymentType.SIMPLE_PAYMENT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="invalid_sender",
            recipient_id="invalid_recipient",
            description="Invalid amount test"
        )
        
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            await gateway.process_payment(request)
    
    @pytest.mark.asyncio
    async def test_payment_validation_invalid_currency(self, gateway):
        """Test payment validation for invalid currency"""
        request = PaymentRequest(
            amount=Decimal("10.00"),
            currency="INVALID",
            payment_type=PaymentType.SIMPLE_PAYMENT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="invalid_sender",
            recipient_id="invalid_recipient",
            description="Invalid currency test"
        )
        
        with pytest.raises(ValueError, match="Invalid currency code"):
            await gateway.process_payment(request)
    
    @pytest.mark.asyncio
    async def test_marketplace_split_validation(self, gateway):
        """Test validation for marketplace split payments"""
        request = PaymentRequest(
            amount=Decimal("100.00"),
            currency="USD",
            payment_type=PaymentType.MARKETPLACE_SPLIT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="split_sender",
            recipient_id="split_recipient",
            description="Marketplace split without recipients",
            recipients=None  # Missing recipients
        )
        
        with pytest.raises(ValueError, match="Recipients required for marketplace split payments"):
            await gateway.process_payment(request)
    
    @pytest.mark.asyncio
    async def test_escrow_validation(self, gateway):
        """Test validation for escrow payments"""
        request = PaymentRequest(
            amount=Decimal("100.00"),
            currency="USD",
            payment_type=PaymentType.ESCROW_PAYMENT,
            provider=PaymentProvider.PAYPAL_BUSINESS,
            sender_id="escrow_sender",
            recipient_id="escrow_recipient",
            description="Escrow without release date",
            escrow_release_date=None  # Missing release date
        )
        
        with pytest.raises(ValueError, match="Escrow release date required for escrow payments"):
            await gateway.process_payment(request)
    
    @pytest.mark.asyncio
    async def test_crypto_validation(self, gateway):
        """Test validation for crypto transfers"""
        request = PaymentRequest(
            amount=Decimal("1.00"),
            currency="BTC",
            payment_type=PaymentType.CRYPTO_TRANSFER,
            provider=PaymentProvider.CRYPTO,
            sender_id="crypto_sender",
            recipient_id="crypto_recipient",
            description="Crypto without addresses",
            from_address=None,  # Missing from address
            to_address=None     # Missing to address
        )
        
        with pytest.raises(ValueError, match="Crypto addresses required for crypto transfers"):
            await gateway.process_payment(request)
    
    @pytest.mark.asyncio
    async def test_nonexistent_transaction_status(self, gateway):
        """Test getting status of non-existent transaction"""
        with pytest.raises(ValueError, match="Transaction nonexistent_tx not found"):
            await gateway.get_transaction_status("nonexistent_tx")
    
    @pytest.mark.asyncio
    async def test_nonexistent_escrow_release(self, gateway):
        """Test releasing non-existent escrow"""
        with pytest.raises(ValueError, match="Escrow transaction nonexistent_escrow not found"):
            await gateway.release_escrow("nonexistent_escrow", {"condition": "met"})
    
    @pytest.mark.asyncio
    async def test_multiple_provider_support(self, gateway):
        """Test that all required providers are initialized"""
        expected_providers = {
            PaymentProvider.STRIPE_CONNECT,
            PaymentProvider.PAYPAL_BUSINESS,
            PaymentProvider.WISE,
            PaymentProvider.CRYPTO
        }
        
        assert set(gateway.processors.keys()) == expected_providers
    
    @pytest.mark.asyncio
    async def test_fee_calculation_accuracy(self, gateway):
        """Test fee calculation accuracy across providers"""
        # Stripe marketplace fee test
        stripe_request = PaymentRequest(
            amount=Decimal("100.00"),
            currency="USD",
            payment_type=PaymentType.MARKETPLACE_SPLIT,
            provider=PaymentProvider.STRIPE_CONNECT,
            sender_id="fee_sender",
            recipient_id="fee_recipient",
            description="Fee calculation test",
            platform_fee_percent=Decimal("0.025"),
            recipients=[{"account_id": "fee_recipient", "amount": Decimal("97.50")}]
        )
        
        stripe_response = await gateway.process_payment(stripe_request)
        
        expected_platform_fee = Decimal("2.50")  # 2.5% of 100
        expected_stripe_fee = Decimal("100.00") * Decimal("0.029") + Decimal("0.30")  # 2.9% + $0.30
        
        assert stripe_response.fees["platform_fee"] == expected_platform_fee
        assert stripe_response.fees["stripe_fee"] == expected_stripe_fee
    
    @pytest.mark.asyncio 
    async def test_concurrent_payments(self, gateway):
        """Test handling multiple concurrent payments"""
        requests = []
        for i in range(5):
            request = PaymentRequest(
                amount=Decimal(f"{10 + i}.00"),
                currency="USD",
                payment_type=PaymentType.SIMPLE_PAYMENT,
                provider=PaymentProvider.STRIPE_CONNECT,
                sender_id=f"concurrent_sender_{i}",
                recipient_id=f"concurrent_recipient_{i}",
                description=f"Concurrent payment {i}"
            )
            requests.append(request)
        
        # Process payments concurrently
        responses = await asyncio.gather(
            *[gateway.process_payment(req) for req in requests]
        )
        
        # Verify all payments were processed
        assert len(responses) == 5
        transaction_ids = [resp.transaction_id for resp in responses]
        assert len(set(transaction_ids)) == 5  # All unique transaction IDs
        
        for i, response in enumerate(responses):
            assert response.amount == Decimal(f"{10 + i}.00")
            assert response.status == PaymentStatus.PENDING
            assert response.provider == PaymentProvider.STRIPE_CONNECT