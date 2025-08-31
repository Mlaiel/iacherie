# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Unit tests for Payment Processor
Tests for automated payment processing and distribution functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import uuid

from monetization.payment_processor import (
    PaymentProcessor, PaymentTransaction, EscrowTransaction,
    PaymentProvider, PaymentStatus, PaymentType
)


class TestPaymentProcessor:
    """Test suite for PaymentProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Create PaymentProcessor instance for testing"""
        return PaymentProcessor()
    
    @pytest.fixture
    async def configured_processor(self, processor):
        """Create configured PaymentProcessor for testing"""
        await processor.configure_stripe(
            secret_key="sk_test_123",
            webhook_secret="whsec_test_123"
        )
        await processor.configure_paypal(
            client_id="paypal_test_client",
            client_secret="paypal_test_secret"
        )
        return processor
    
    @pytest.fixture
    def sample_transaction_data(self):
        """Sample transaction data for testing"""
        return {
            "license_id": "license_123",
            "payer_id": "user_456",
            "payee_id": "creator_789", 
            "amount": 100.0,
            "currency": "EUR"
        }
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_stripe_configuration(self, processor):
        """Test Stripe provider configuration"""
        await processor.configure_stripe(
            secret_key="sk_test_123",
            webhook_secret="whsec_test_123",
            connect_enabled=True
        )
        
        stripe_config = processor.provider_configs[PaymentProvider.STRIPE]
        assert stripe_config["secret_key"] == "sk_test_123"
        assert stripe_config["webhook_secret"] == "whsec_test_123"
        assert stripe_config["connect_enabled"] is True
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_paypal_configuration(self, processor):
        """Test PayPal provider configuration"""
        await processor.configure_paypal(
            client_id="paypal_test_client",
            client_secret="paypal_test_secret",
            environment="sandbox"
        )
        
        paypal_config = processor.provider_configs[PaymentProvider.PAYPAL]
        assert paypal_config["client_id"] == "paypal_test_client"
        assert paypal_config["client_secret"] == "paypal_test_secret"
        assert paypal_config["environment"] == "sandbox"
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_fee_calculation_stripe(self, processor):
        """Test fee calculation for Stripe"""
        amount = 100.0
        fees = processor._calculate_fees(amount, PaymentProvider.STRIPE, "EUR")
        
        expected_fee = (100.0 * 0.029) + 0.30  # 2.9% + €0.30
        assert abs(fees - expected_fee) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_fee_calculation_international(self, processor):
        """Test fee calculation for international payments"""
        amount = 100.0
        fees = processor._calculate_fees(
            amount, PaymentProvider.STRIPE, "EUR", international=True
        )
        
        expected_fee = (100.0 * 0.039) + 0.30  # 3.9% + €0.30 for international
        assert abs(fees - expected_fee) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_fee_calculation_wise(self, processor):
        """Test fee calculation for Wise transfers"""
        amount = 100.0
        fees = processor._calculate_fees(amount, PaymentProvider.WISE, "EUR")
        
        expected_fee = (100.0 * 0.005) + 0.50  # 0.5% + €0.50
        assert abs(fees - expected_fee) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_fee_calculation_bitcoin(self, processor):
        """Test fee calculation for Bitcoin payments"""
        amount = 100.0
        fees = processor._calculate_fees(amount, PaymentProvider.BITCOIN, "BTC")
        
        expected_fee = 100.0 * 0.01  # 1% with no fixed fee
        assert abs(fees - expected_fee) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_fee_cap(self, processor):
        """Test that fees are capped at reasonable amount"""
        amount = 10.0  # Small amount
        fees = processor._calculate_fees(amount, PaymentProvider.STRIPE, "EUR")
        
        # Fees should not exceed 10% of amount
        assert fees <= amount * 0.1
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_license_payment_processing(self, configured_processor, sample_transaction_data):
        """Test license payment processing"""
        transaction = await configured_processor.process_license_payment(
            license_id=sample_transaction_data["license_id"],
            payer_id=sample_transaction_data["payer_id"],
            payee_id=sample_transaction_data["payee_id"],
            amount=sample_transaction_data["amount"],
            currency=sample_transaction_data["currency"],
            payment_method_id="pm_test_123"
        )
        
        assert isinstance(transaction, PaymentTransaction)
        assert transaction.transaction_type == PaymentType.LICENSE_PAYMENT
        assert transaction.provider == PaymentProvider.STRIPE
        assert transaction.amount == 100.0
        assert transaction.currency == "EUR"
        assert transaction.fees > 0
        assert transaction.net_amount < transaction.amount
        assert transaction.status in [PaymentStatus.PROCESSING, PaymentStatus.FAILED]
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_license_payment_without_payment_method(self, configured_processor, sample_transaction_data):
        """Test license payment processing without payment method"""
        transaction = await configured_processor.process_license_payment(
            license_id=sample_transaction_data["license_id"],
            payer_id=sample_transaction_data["payer_id"],
            payee_id=sample_transaction_data["payee_id"],
            amount=sample_transaction_data["amount"],
            currency=sample_transaction_data["currency"]
        )
        
        # Should fail without payment method
        assert transaction.status == PaymentStatus.FAILED
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_revenue_distribution(self, configured_processor):
        """Test automated revenue distribution"""
        revenue_data = {
            "youtube": 100.0,
            "spotify": 50.0,
            "instagram": 75.0
        }
        
        split_rules = {
            "creator_1": 0.6,  # 60%
            "creator_2": 0.3,  # 30%
            "platform": 0.1   # 10%
        }
        
        transactions = await configured_processor.distribute_revenue_shares(
            revenue_data, split_rules, "EUR"
        )
        
        assert len(transactions) == 3
        
        total_distributed = sum(t.amount for t in transactions)
        expected_total = sum(revenue_data.values())
        assert abs(total_distributed - expected_total) < 0.01
        
        # Check individual distributions
        creator_1_transaction = next(t for t in transactions if t.payee_id == "creator_1")
        assert abs(creator_1_transaction.amount - (expected_total * 0.6)) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_revenue_distribution_minimum_threshold(self, configured_processor):
        """Test revenue distribution respects minimum payout threshold"""
        revenue_data = {"youtube": 5.0}  # Small amount
        split_rules = {"creator_1": 0.1}  # 10% = €0.50, below minimum
        
        transactions = await configured_processor.distribute_revenue_shares(
            revenue_data, split_rules, "EUR"
        )
        
        # Should skip payout due to minimum threshold
        assert len(transactions) == 0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_escrow_creation(self, configured_processor):
        """Test escrow transaction creation"""
        escrow = await configured_processor.create_escrow_transaction(
            payment_id="payment_123",
            amount=100.0,
            currency="EUR",
            release_conditions=["content_delivered", "no_disputes"],
            dispute_period_days=7
        )
        
        assert isinstance(escrow, EscrowTransaction)
        assert escrow.payment_id == "payment_123"
        assert escrow.amount == 100.0
        assert escrow.currency == "EUR"
        assert escrow.status == "active"
        assert len(escrow.release_conditions) == 2
        
        # Check dispute deadline
        expected_deadline = datetime.now() + timedelta(days=7)
        assert abs((escrow.dispute_deadline - expected_deadline).total_seconds()) < 60
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_escrow_release(self, configured_processor, sample_transaction_data):
        """Test escrow fund release"""
        # First create a transaction and escrow
        transaction = await configured_processor.process_license_payment(
            **sample_transaction_data,
            payment_method_id="pm_test_123"
        )
        
        escrow = await configured_processor.create_escrow_transaction(
            payment_id=transaction.id,
            amount=transaction.amount,
            currency=transaction.currency,
            release_conditions=["content_delivered"]
        )
        
        # Release escrow
        success = await configured_processor.release_escrow(
            escrow_id=escrow.id,
            release_reason="content_delivered"
        )
        
        assert success is True
        assert escrow.status in ["released_manual", "released_auto"]
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_escrow_release_nonexistent(self, configured_processor):
        """Test escrow release for non-existent escrow"""
        success = await configured_processor.release_escrow(
            escrow_id="nonexistent_escrow",
            release_reason="test"
        )
        
        assert success is False
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_multi_currency_payment(self, configured_processor):
        """Test multi-currency payment processing"""
        transaction = await configured_processor.process_multi_currency_payment(
            amount=100.0,
            from_currency="USD",
            to_currency="EUR",
            payer_id="user_456",
            payee_id="creator_789"
        )
        
        assert isinstance(transaction, PaymentTransaction)
        assert transaction.provider == PaymentProvider.WISE
        assert transaction.currency == "EUR"
        assert transaction.amount != 100.0  # Should be converted
        assert "original_amount" in transaction.metadata
        assert "exchange_rate" in transaction.metadata
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_payment_dispute_handling(self, configured_processor, sample_transaction_data):
        """Test payment dispute handling"""
        # Create a transaction first
        transaction = await configured_processor.process_license_payment(
            **sample_transaction_data,
            payment_method_id="pm_test_123"
        )
        
        # Create dispute
        result = await configured_processor.handle_payment_dispute(
            transaction_id=transaction.id,
            dispute_reason="Content not delivered",
            evidence={"screenshots": ["evidence1.png"], "emails": ["email1.txt"]}
        )
        
        assert result["success"] is True
        assert "dispute_id" in result
        assert result["status"] == "open"
        assert transaction.status == PaymentStatus.DISPUTED
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_dispute_nonexistent_transaction(self, configured_processor):
        """Test dispute handling for non-existent transaction"""
        result = await configured_processor.handle_payment_dispute(
            transaction_id="nonexistent_transaction",
            dispute_reason="Test dispute",
            evidence={}
        )
        
        assert result["success"] is False
        assert "Transaction not found" in result["error"]
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_tax_report_generation(self, configured_processor):
        """Test tax report generation"""
        # Create some test transactions
        user_id = "user_123"
        
        # Simulate completed transactions
        for i in range(3):
            transaction = PaymentTransaction(
                id=str(uuid.uuid4()),
                transaction_type=PaymentType.REVENUE_SHARE,
                provider=PaymentProvider.STRIPE,
                amount=100.0,
                currency="EUR",
                payer_id="platform",
                payee_id=user_id,
                status=PaymentStatus.COMPLETED,
                fees=3.0,
                net_amount=97.0,
                created_at=datetime(2025, 1, 15)
            )
            configured_processor.transactions[transaction.id] = transaction
        
        report = await configured_processor.generate_tax_reports(
            user_id=user_id,
            year=2025,
            country="DE"
        )
        
        assert report["user_id"] == user_id
        assert report["year"] == 2025
        assert report["country"] == "DE"
        assert report["total_income"] == 291.0  # 3 transactions * 97.0
        assert report["total_fees"] == 9.0      # 3 transactions * 3.0
        assert "tax_obligations" in report
        assert report["transaction_count"] == 3
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_tax_calculation_germany(self, configured_processor):
        """Test German tax calculation"""
        tax_info = configured_processor._calculate_tax_obligations(20000.0, "DE")
        
        assert "taxable_income" in tax_info
        assert "tax_rate" in tax_info
        assert "tax_owed" in tax_info
        assert tax_info["tax_rate"] == 0.25  # 25% for Germany
        assert tax_info["threshold"] == 9744  # German tax-free threshold
        
        # Should only tax income above threshold
        expected_taxable = 20000.0 - 9744
        assert abs(tax_info["taxable_income"] - expected_taxable) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_tax_calculation_below_threshold(self, configured_processor):
        """Test tax calculation below threshold"""
        tax_info = configured_processor._calculate_tax_obligations(5000.0, "DE")
        
        assert tax_info["taxable_income"] == 0.0
        assert tax_info["tax_owed"] == 0.0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    def test_provider_fee_structures(self, processor):
        """Test payment provider fee structures"""
        fees = processor.PROVIDER_FEES
        
        # Check all providers have required fee structure
        required_providers = [
            PaymentProvider.STRIPE, PaymentProvider.PAYPAL, 
            PaymentProvider.WISE, PaymentProvider.BITCOIN
        ]
        
        for provider in required_providers:
            assert provider in fees
            provider_fees = fees[provider]
            assert "percentage" in provider_fees
            assert "fixed" in provider_fees
            assert "international" in provider_fees
            
            # Verify reasonable fee ranges
            assert 0 <= provider_fees["percentage"] <= 0.05  # 0-5%
            assert 0 <= provider_fees["fixed"] <= 1.0        # 0-€1
    
    @pytest.mark.unit
    @pytest.mark.monetization
    def test_payment_transaction_dataclass(self):
        """Test PaymentTransaction dataclass structure"""
        transaction = PaymentTransaction(
            id="test_123",
            transaction_type=PaymentType.LICENSE_PAYMENT,
            provider=PaymentProvider.STRIPE,
            amount=100.0,
            currency="EUR",
            payer_id="user_456",
            payee_id="creator_789",
            status=PaymentStatus.PENDING
        )
        
        assert transaction.id == "test_123"
        assert transaction.transaction_type == PaymentType.LICENSE_PAYMENT
        assert transaction.provider == PaymentProvider.STRIPE
        assert transaction.amount == 100.0
        assert transaction.currency == "EUR"
        assert transaction.status == PaymentStatus.PENDING
        assert transaction.fees == 0.0  # Default value
        assert transaction.net_amount == 0.0  # Default value
    
    @pytest.mark.unit
    @pytest.mark.monetization
    def test_escrow_transaction_dataclass(self):
        """Test EscrowTransaction dataclass structure"""
        escrow = EscrowTransaction(
            id="escrow_123",
            payment_id="payment_456",
            amount=100.0,
            currency="EUR",
            holder="platform",
            release_conditions=["condition1", "condition2"],
            dispute_deadline=datetime.now() + timedelta(days=7)
        )
        
        assert escrow.id == "escrow_123"
        assert escrow.payment_id == "payment_456"
        assert escrow.amount == 100.0
        assert escrow.currency == "EUR"
        assert escrow.holder == "platform"
        assert len(escrow.release_conditions) == 2
        assert escrow.status == "active"  # Default value
    
    @pytest.mark.unit
    @pytest.mark.monetization
    def test_payment_enums(self):
        """Test payment-related enums"""
        # Test PaymentProvider enum
        assert PaymentProvider.STRIPE.value == "stripe"
        assert PaymentProvider.PAYPAL.value == "paypal"
        assert PaymentProvider.WISE.value == "wise"
        assert PaymentProvider.BITCOIN.value == "bitcoin"
        
        # Test PaymentStatus enum
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.DISPUTED.value == "disputed"
        
        # Test PaymentType enum
        assert PaymentType.LICENSE_PAYMENT.value == "license_payment"
        assert PaymentType.REVENUE_SHARE.value == "revenue_share"
        assert PaymentType.SUBSCRIPTION.value == "subscription"
    
    @pytest.mark.slow
    @pytest.mark.monetization
    async def test_large_scale_revenue_distribution(self, configured_processor):
        """Test revenue distribution with many recipients"""
        revenue_data = {"youtube": 10000.0}  # Large revenue
        
        # Create many recipients with small shares
        split_rules = {f"creator_{i}": 0.01 for i in range(50)}  # 50 creators, 1% each
        
        transactions = await configured_processor.distribute_revenue_shares(
            revenue_data, split_rules, "EUR"
        )
        
        assert len(transactions) == 50
        
        # Each should get 1% of €10,000 = €100
        for transaction in transactions:
            assert abs(transaction.amount - 100.0) < 0.01
    
    @pytest.mark.unit
    @pytest.mark.monetization 
    async def test_exchange_rate_lookup(self, configured_processor):
        """Test exchange rate lookup functionality"""
        # Test known exchange rates
        usd_to_eur = await configured_processor._get_exchange_rate("USD", "EUR")
        eur_to_usd = await configured_processor._get_exchange_rate("EUR", "USD")
        
        assert usd_to_eur == 0.85
        assert eur_to_usd == 1.18
        
        # Test unknown currency pair defaults to 1.0
        unknown_rate = await configured_processor._get_exchange_rate("XYZ", "ABC")
        assert unknown_rate == 1.0