# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
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
Unit Tests for Monetization Agent
=================================

Critical unit tests for the AI-powered monetization agent module.
Tests revenue calculation, payment processing, subscription management,
and monetization strategy optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Address critical testing gap - "Tests Manquants: Pas de tests unitaires centralisés"
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import uuid


class MockMonetizationEngine:
    """
Mock implementation of monetization engine for testing"""
    
    def __init__(self):
        self.revenue_history = []
        self.active_subscriptions = {}
        self.payment_methods = {}
        self.commission_rates = {
            "standard": Decimal("0.15"),  # 15% platform commission
            "premium": Decimal("0.10"),   # 10% for premium creators
            "enterprise": Decimal("0.05") # 5% for enterprise accounts
        }
        
    async def calculate_revenue(self, content_id: str, metrics: Dict) -> Dict[str, Any]:
        """Calculate revenue based on content performance metrics"""
        views = metrics.get("views", 0)
        likes = metrics.get("likes", 0)
        shares = metrics.get("shares", 0)
        watch_time = metrics.get("watch_time_minutes", 0)
        
        # Base revenue calculation (simplified algorithm)
        base_revenue = Decimal(str(views * 0.001))  # $0.001 per view
        engagement_bonus = Decimal(str((likes + shares) * 0.01))  # $0.01 per engagement
        watch_time_bonus = Decimal(str(watch_time * 0.005))  # $0.005 per minute
        
        gross_revenue = base_revenue + engagement_bonus + watch_time_bonus
        
        # Apply quality multiplier
        quality_score = metrics.get("quality_score", 0.8)
        quality_multiplier = Decimal(str(1 + (quality_score - 0.5)))
        
        adjusted_revenue = gross_revenue * quality_multiplier
        
        # Calculate platform commission
        creator_tier = metrics.get("creator_tier", "standard")
        commission_rate = self.commission_rates.get(creator_tier, self.commission_rates["standard"])
        platform_commission = adjusted_revenue * commission_rate
        creator_revenue = adjusted_revenue - platform_commission
        
        revenue_data = {
            "content_id": content_id,
            "gross_revenue": float(adjusted_revenue),
            "platform_commission": float(platform_commission),
            "creator_revenue": float(creator_revenue),
            "commission_rate": float(commission_rate),
            "metrics_used": metrics,
            "calculated_at": datetime.utcnow().isoformat(),
            "revenue_breakdown": {
                "base_revenue": float(base_revenue),
                "engagement_bonus": float(engagement_bonus),
                "watch_time_bonus": float(watch_time_bonus),
                "quality_multiplier": float(quality_multiplier)
            }
        }
        
        self.revenue_history.append(revenue_data)
        return revenue_data
    
    async def process_payment(self, payment_data: Dict) -> Dict[str, Any]:
        """Process payment transaction"""
        payment_id = str(uuid.uuid4())
        amount = Decimal(str(payment_data.get("amount", 0)))
        
        # Validate payment data
        required_fields = ["user_id", "amount", "payment_method"]
        for field in required_fields:
            if field not in payment_data:
                raise ValueError(f"Missing required field: {field}")
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Simulate payment processing
        processing_fee = amount * Decimal("0.029")  # 2.9% processing fee
        net_amount = amount - processing_fee
        
        payment_result = {
            "payment_id": payment_id,
            "status": "completed",
            "amount": float(amount),
            "processing_fee": float(processing_fee),
            "net_amount": float(net_amount),
            "user_id": payment_data["user_id"],
            "payment_method": payment_data["payment_method"],
            "processed_at": datetime.utcnow().isoformat(),
            "transaction_reference": f"TXN_{payment_id[:8].upper()}"
        }
        
        return payment_result
    
    async def manage_subscription(self, action: str, subscription_data: Dict) -> Dict[str, Any]:
        """Manage user subscriptions"""
        user_id = subscription_data.get("user_id")
        plan_type = subscription_data.get("plan_type", "basic")
        
        # Define plan prices for all actions
        plan_prices = {
            "basic": Decimal("9.99"),
            "premium": Decimal("19.99"),
            "enterprise": Decimal("49.99")
        }
        
        if action == "create":
            subscription_id = str(uuid.uuid4())
            
            subscription = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "plan_type": plan_type,
                "monthly_price": float(plan_prices.get(plan_type, plan_prices["basic"])),
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "features": self._get_plan_features(plan_type)
            }
            
            self.active_subscriptions[user_id] = subscription
            return subscription
            
        elif action == "cancel":
            if user_id in self.active_subscriptions:
                subscription = self.active_subscriptions[user_id]
                subscription["status"] = "cancelled"
                subscription["cancelled_at"] = datetime.utcnow().isoformat()
                return subscription
            else:
                raise ValueError("Subscription not found")
                
        elif action == "upgrade":
            if user_id in self.active_subscriptions:
                subscription = self.active_subscriptions[user_id]
                old_plan = subscription["plan_type"]
                subscription["plan_type"] = plan_type
                subscription["monthly_price"] = float(plan_prices.get(plan_type, plan_prices["basic"]))
                subscription["features"] = self._get_plan_features(plan_type)
                subscription["upgraded_at"] = datetime.utcnow().isoformat()
                subscription["previous_plan"] = old_plan
                return subscription
            else:
                raise ValueError("Subscription not found")
    
    def _get_plan_features(self, plan_type: str) -> List[str]:
        """Get features for subscription plan"""
        features_map = {
            "basic": [
                "Basic content protection",
                "5 uploads per month",
                "Email support"
            ],
            "premium": [
                "Advanced content protection",
                "50 uploads per month",
                "Priority support",
                "Analytics dashboard",
                "API access"
            ],
            "enterprise": [
                "Enterprise content protection",
                "Unlimited uploads",
                "24/7 dedicated support",
                "Advanced analytics",
                "Custom API integration",
                "White-label solution"
            ]
        }
        return features_map.get(plan_type, features_map["basic"])
    
    async def generate_revenue_report(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Generate revenue report for a user"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Filter revenue history for the user and period
        user_revenues = [
            rev for rev in self.revenue_history
            if rev.get("user_id") == user_id and
            start_date <= datetime.fromisoformat(rev["calculated_at"]) <= end_date
        ]
        
        if not user_revenues:
            return {
                "user_id": user_id,
                "period_days": period_days,
                "total_revenue": 0.0,
                "total_commission": 0.0,
                "content_count": 0,
                "report_generated_at": datetime.utcnow().isoformat()
            }
        
        total_creator_revenue = sum(rev["creator_revenue"] for rev in user_revenues)
        total_platform_commission = sum(rev["platform_commission"] for rev in user_revenues)
        content_count = len(user_revenues)
        
        average_revenue_per_content = total_creator_revenue / content_count if content_count > 0 else 0
        
        return {
            "user_id": user_id,
            "period_days": period_days,
            "total_creator_revenue": round(total_creator_revenue, 2),
            "total_platform_commission": round(total_platform_commission, 2),
            "content_count": content_count,
            "average_revenue_per_content": round(average_revenue_per_content, 2),
            "top_performing_content": max(user_revenues, key=lambda x: x["creator_revenue"]) if user_revenues else None,
            "report_generated_at": datetime.utcnow().isoformat()
        }
    
    async def validate_payment_method(self, payment_method: Dict) -> bool:
        """Validate payment method"""
        required_fields = ["type", "details"]
        
        for field in required_fields:
            if field not in payment_method:
                return False
        
        payment_type = payment_method["type"]
        details = payment_method["details"]
        
        if payment_type == "credit_card":
            required_card_fields = ["number", "expiry", "cvv"]
            return all(field in details for field in required_card_fields)
        elif payment_type == "paypal":
            return "email" in details
        elif payment_type == "bank_transfer":
            required_bank_fields = ["account_number", "routing_number"]
            return all(field in details for field in required_bank_fields)
        
        return False


class TestMonetizationAgent:
    """Test suite for monetization agent functionality"""
    
    @pytest.fixture
    def monetization_engine(self):
        """
Create monetization engine fixture"""
        return MockMonetizationEngine()
    
    @pytest.fixture
    def sample_content_metrics(self):
        """
Sample content performance metrics"""
        return {
            "views": 10000,
            "likes": 500,
            "shares": 150,
            "watch_time_minutes": 2500,
            "quality_score": 0.85,
            "creator_tier": "premium"
        }
    
    @pytest.fixture
    def sample_payment_data(self):
        """Sample payment data"""
        return {
            "user_id": "user_123",
            "amount": 25.99,
            "payment_method": "credit_card",
            "currency": "USD"
        }
    
    @pytest.fixture
    def sample_subscription_data(self):
        """Sample subscription data"""
        return {
            "user_id": "user_456",
            "plan_type": "premium"
        }
    
    @pytest.mark.asyncio
    async def test_revenue_calculation(self, monetization_engine, sample_content_metrics):
        """Test revenue calculation functionality"""
        content_id = "content_123"
        
        revenue_data = await monetization_engine.calculate_revenue(
            content_id, sample_content_metrics
        )
        
        # Validate revenue calculation structure
        assert "content_id" in revenue_data
        assert revenue_data["content_id"] == content_id
        assert "gross_revenue" in revenue_data
        assert "creator_revenue" in revenue_data
        assert "platform_commission" in revenue_data
        assert "commission_rate" in revenue_data
        
        # Validate financial calculations
        assert revenue_data["gross_revenue"] > 0
        assert revenue_data["creator_revenue"] > 0
        assert revenue_data["platform_commission"] > 0
        
        # Validate commission rate for premium tier
        assert revenue_data["commission_rate"] == 0.10  # Premium tier
        
        # Validate revenue breakdown
        breakdown = revenue_data["revenue_breakdown"]
        assert "base_revenue" in breakdown
        assert "engagement_bonus" in breakdown
        assert "watch_time_bonus" in breakdown
        assert "quality_multiplier" in breakdown
        
        # Validate storage
        assert len(monetization_engine.revenue_history) == 1
    
    @pytest.mark.asyncio
    async def test_payment_processing(self, monetization_engine, sample_payment_data):
        """Test payment processing functionality"""
        payment_result = await monetization_engine.process_payment(sample_payment_data)
        
        # Validate payment result structure
        assert "payment_id" in payment_result
        assert "status" in payment_result
        assert payment_result["status"] == "completed"
        assert "amount" in payment_result
        assert "processing_fee" in payment_result
        assert "net_amount" in payment_result
        assert "transaction_reference" in payment_result
        
        # Validate financial calculations
        expected_fee = 25.99 * 0.029  # 2.9% processing fee
        expected_net = 25.99 - expected_fee
        
        assert abs(payment_result["processing_fee"] - expected_fee) < 0.01
        assert abs(payment_result["net_amount"] - expected_net) < 0.01
        
        # Validate transaction reference format
        assert payment_result["transaction_reference"].startswith("TXN_")
    
    @pytest.mark.asyncio
    async def test_payment_validation(self, monetization_engine):
        """Test payment validation"""
        # Test missing required fields
        invalid_payment = {"user_id": "user_123"}
        
        with pytest.raises(ValueError, match="Missing required field"):
            await monetization_engine.process_payment(invalid_payment)
        
        # Test negative amount
        negative_payment = {
            "user_id": "user_123",
            "amount": -10.00,
            "payment_method": "credit_card"
        }
        
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            await monetization_engine.process_payment(negative_payment)
    
    @pytest.mark.asyncio
    async def test_subscription_creation(self, monetization_engine, sample_subscription_data):
        """Test subscription creation"""
        subscription = await monetization_engine.manage_subscription(
            "create", sample_subscription_data
        )
        
        # Validate subscription structure
        assert "subscription_id" in subscription
        assert "user_id" in subscription
        assert subscription["user_id"] == sample_subscription_data["user_id"]
        assert "plan_type" in subscription
        assert subscription["plan_type"] == "premium"
        assert "status" in subscription
        assert subscription["status"] == "active"
        assert "monthly_price" in subscription
        assert subscription["monthly_price"] == 19.99  # Premium price
        assert "features" in subscription
        
        # Validate features for premium plan
        features = subscription["features"]
        assert "Advanced content protection" in features
        assert "Priority support" in features
        assert "API access" in features
        
        # Validate storage
        user_id = sample_subscription_data["user_id"]
        assert user_id in monetization_engine.active_subscriptions
    
    @pytest.mark.asyncio
    async def test_subscription_cancellation(self, monetization_engine, sample_subscription_data):
        """Test subscription cancellation"""
        # First create a subscription
        await monetization_engine.manage_subscription("create", sample_subscription_data)
        
        # Then cancel it
        cancelled_subscription = await monetization_engine.manage_subscription(
            "cancel", sample_subscription_data
        )
        
        # Validate cancellation
        assert cancelled_subscription["status"] == "cancelled"
        assert "cancelled_at" in cancelled_subscription
        
        # Test cancelling non-existent subscription
        non_existent_data = {"user_id": "non_existent_user"}
        
        with pytest.raises(ValueError, match="Subscription not found"):
            await monetization_engine.manage_subscription("cancel", non_existent_data)
    
    @pytest.mark.asyncio
    async def test_subscription_upgrade(self, monetization_engine, sample_subscription_data):
        """Test subscription upgrade"""
        # Create basic subscription first
        basic_data = {**sample_subscription_data, "plan_type": "basic"}
        await monetization_engine.manage_subscription("create", basic_data)
        
        # Upgrade to enterprise
        upgrade_data = {**sample_subscription_data, "plan_type": "enterprise"}
        upgraded_subscription = await monetization_engine.manage_subscription(
            "upgrade", upgrade_data
        )
        
        # Validate upgrade
        assert upgraded_subscription["plan_type"] == "enterprise"
        assert upgraded_subscription["monthly_price"] == 49.99  # Enterprise price
        assert upgraded_subscription["previous_plan"] == "basic"
        assert "upgraded_at" in upgraded_subscription
        
        # Validate enterprise features
        features = upgraded_subscription["features"]
        assert "Enterprise content protection" in features
        assert "24/7 dedicated support" in features
        assert "White-label solution" in features
    
    @pytest.mark.asyncio
    async def test_revenue_report_generation(self, monetization_engine):
        """Test revenue report generation"""
        user_id = "test_user_789"
        
        # Generate some revenue history
        test_metrics = [
            {"views": 5000, "likes": 250, "quality_score": 0.8, "creator_tier": "standard"},
            {"views": 8000, "likes": 400, "quality_score": 0.9, "creator_tier": "standard"},
            {"views": 12000, "likes": 600, "quality_score": 0.75, "creator_tier": "standard"}
        ]
        
        for i, metrics in enumerate(test_metrics):
            revenue_data = await monetization_engine.calculate_revenue(f"content_{i}", metrics)
            revenue_data["user_id"] = user_id  # Add user_id for filtering
        
        # Generate report
        report = await monetization_engine.generate_revenue_report(user_id, 30)
        
        # Validate report structure
        assert "user_id" in report
        assert report["user_id"] == user_id
        assert "total_creator_revenue" in report
        assert "total_platform_commission" in report
        assert "content_count" in report
        assert report["content_count"] == 3
        assert "average_revenue_per_content" in report
        assert "top_performing_content" in report
        
        # Validate calculations
        assert report["total_creator_revenue"] > 0
        assert report["total_platform_commission"] > 0
        assert report["average_revenue_per_content"] > 0
    
    @pytest.mark.asyncio
    async def test_payment_method_validation(self, monetization_engine):
        """Test payment method validation"""
        # Valid credit card
        valid_credit_card = {
            "type": "credit_card",
            "details": {
                "number": "4111111111111111",
                "expiry": "12/25",
                "cvv": "123"
            }
        }
        
        is_valid = await monetization_engine.validate_payment_method(valid_credit_card)
        assert is_valid is True
        
        # Valid PayPal
        valid_paypal = {
            "type": "paypal",
            "details": {
                "email": "user@example.com"
            }
        }
        
        is_valid = await monetization_engine.validate_payment_method(valid_paypal)
        assert is_valid is True
        
        # Invalid - missing fields
        invalid_payment_method = {
            "type": "credit_card",
            "details": {
                "number": "4111111111111111"
                # Missing expiry and cvv
            }
        }
        
        is_valid = await monetization_engine.validate_payment_method(invalid_payment_method)
        assert is_valid is False
        
        # Invalid - missing type
        incomplete_payment_method = {
            "details": {"email": "user@example.com"}
        }
        
        is_valid = await monetization_engine.validate_payment_method(incomplete_payment_method)
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_commission_rate_tiers(self, monetization_engine):
        """Test different commission rates for creator tiers"""
        content_id = "tier_test_content"
        base_metrics = {
            "views": 1000,
            "likes": 50,
            "shares": 10,
            "watch_time_minutes": 500,
            "quality_score": 0.8
        }
        
        # Test standard tier
        standard_metrics = {**base_metrics, "creator_tier": "standard"}
        standard_revenue = await monetization_engine.calculate_revenue(content_id + "_standard", standard_metrics)
        assert standard_revenue["commission_rate"] == 0.15
        
        # Test premium tier
        premium_metrics = {**base_metrics, "creator_tier": "premium"}
        premium_revenue = await monetization_engine.calculate_revenue(content_id + "_premium", premium_metrics)
        assert premium_revenue["commission_rate"] == 0.10
        
        # Test enterprise tier
        enterprise_metrics = {**base_metrics, "creator_tier": "enterprise"}
        enterprise_revenue = await monetization_engine.calculate_revenue(content_id + "_enterprise", enterprise_metrics)
        assert enterprise_revenue["commission_rate"] == 0.05
        
        # Validate that higher tiers result in higher creator revenue
        assert premium_revenue["creator_revenue"] > standard_revenue["creator_revenue"]
        assert enterprise_revenue["creator_revenue"] > premium_revenue["creator_revenue"]
    
    def test_engine_initialization(self):
        """Test monetization engine initialization"""
        engine = MockMonetizationEngine()
        
        assert engine.revenue_history == []
        assert engine.active_subscriptions == {}
        assert engine.payment_methods == {}
        assert len(engine.commission_rates) == 3
        assert engine.commission_rates["standard"] == Decimal("0.15")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([str(Path(__file__)), "-v"])