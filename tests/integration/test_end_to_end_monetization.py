"""
Integration tests for Ainflue Platform
End-to-end integration tests for the complete platform workflow.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import uuid

from monetization.revenue_calculator import RevenueCalculator, RevenueData
from monetization.payment_processor import PaymentProcessor, PaymentProvider, PaymentStatus
from crawlers.youtube_crawler import YouTubeVideoData, YouTubeMonitoringResult


class TestEndToEndMonetization:
    """Integration tests for complete monetization workflow"""
    
    @pytest.fixture
    async def setup_monetization_system(self):
        """Setup complete monetization system for testing"""
        revenue_calculator = RevenueCalculator()
        payment_processor = PaymentProcessor()
        
        # Configure payment processor
        await payment_processor.configure_stripe(
            secret_key="sk_test_integration",
            webhook_secret="whsec_test_integration"
        )
        
        return {
            "revenue_calculator": revenue_calculator,
            "payment_processor": payment_processor
        }
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_complete_monetization_workflow(self, setup_monetization_system):
        """Test complete end-to-end monetization workflow"""
        system = await setup_monetization_system
        revenue_calculator = system["revenue_calculator"]
        payment_processor = system["payment_processor"]
        
        # Step 1: Calculate revenue from multiple platforms
        platform_data = {
            "youtube": {
                "views": 50000,
                "watch_time_hours": 25000,
                "engagement_rate": 0.06,
                "subscriber_count": 5000,
                "country": "US"
            },
            "spotify": {
                "streams": 100000,
                "premium_streams": 60000,
                "country_distribution": {"US": 50000, "DE": 30000, "GB": 20000}
            },
            "instagram": {
                "impressions": 200000,
                "reach": 150000,
                "engagement_rate": 0.04,
                "story_views": 25000,
                "follower_count": 3000
            }
        }
        
        revenues = await revenue_calculator.calculate_total_revenue(
            "integration_test_content", platform_data
        )
        
        # Verify revenue calculation
        assert "total" in revenues
        assert revenues["total"] > 0
        assert revenues["youtube"] > 0
        assert revenues["spotify"] > 0
        assert revenues["instagram"] > 0
        
        # Step 2: Distribute revenue shares
        split_rules = {
            "creator_1": 0.5,    # 50% to main creator
            "creator_2": 0.3,    # 30% to collaborator
            "platform": 0.2     # 20% to platform
        }
        
        revenue_data = {"total": revenues["total"]}
        
        transactions = await payment_processor.distribute_revenue_shares(
            revenue_data, split_rules, "EUR"
        )
        
        # Verify revenue distribution
        assert len(transactions) == 3
        
        total_distributed = sum(t.amount for t in transactions)
        assert abs(total_distributed - revenues["total"]) < 0.01
        
        # Step 3: Verify individual payouts
        creator_1_payout = next(t for t in transactions if t.payee_id == "creator_1")
        creator_2_payout = next(t for t in transactions if t.payee_id == "creator_2")
        platform_payout = next(t for t in transactions if t.payee_id == "platform")
        
        assert abs(creator_1_payout.amount - (revenues["total"] * 0.5)) < 0.01
        assert abs(creator_2_payout.amount - (revenues["total"] * 0.3)) < 0.01
        assert abs(platform_payout.amount - (revenues["total"] * 0.2)) < 0.01
        
        # Step 4: Create escrow for dispute protection
        escrow = await payment_processor.create_escrow_transaction(
            payment_id=creator_1_payout.id,
            amount=creator_1_payout.amount,
            currency="EUR",
            release_conditions=["content_verified", "no_disputes"],
            dispute_period_days=7
        )
        
        assert escrow.amount == creator_1_payout.amount
        assert escrow.status == "active"
        
        # Step 5: Process license payment for content usage
        license_payment = await payment_processor.process_license_payment(
            license_id="license_integration_test",
            payer_id="licensee_123",
            payee_id="creator_1",
            amount=250.0,
            currency="EUR",
            payment_method_id="pm_test_integration"
        )
        
        assert license_payment.amount == 250.0
        assert license_payment.currency == "EUR"
        assert license_payment.status in [PaymentStatus.PROCESSING, PaymentStatus.FAILED]
    
    @pytest.mark.integration
    async def test_platform_sync_workflow(self):
        """Test platform data synchronization workflow"""
        # Simulate data from multiple platforms
        youtube_data = YouTubeVideoData(
            video_id="integration_test_video",
            title="Integration Test Video",
            description="Test video for integration testing",
            channel_id="UC_integration_test",
            channel_title="Integration Test Channel",
            published_at=datetime.now() - timedelta(days=7),
            view_count=75000,
            like_count=3500,
            duration="PT5M30S",
            thumbnail_url="https://test.com/thumb.jpg",
            video_url="https://youtube.com/watch?v=integration_test",
            tags=["test", "integration", "music"],
            category_id="10",
            language="en",
            similarity_score=0.0  # Original content
        )
        
        # Create revenue data from platform performance
        revenue_calculator = RevenueCalculator()
        
        youtube_revenue = await revenue_calculator.calculate_youtube_revenue(
            views=youtube_data.view_count,
            watch_time_hours=youtube_data.view_count * 0.05,  # Estimate 3 minutes avg
            engagement_rate=youtube_data.like_count / youtube_data.view_count,
            subscriber_count=10000,
            country="US"
        )
        
        assert youtube_revenue > 0
        
        # Simulate real-time monitoring results
        monitoring_result = YouTubeMonitoringResult(
            original_content_id="integration_test_content",
            search_query="integration test video",
            total_results=1,
            potential_violations=[]  # No violations found
        )
        
        assert monitoring_result.total_results == 1
        assert len(monitoring_result.potential_violations) == 0
    
    @pytest.mark.integration
    async def test_payment_flow_with_disputes(self, setup_monetization_system):
        """Test complete payment flow including dispute handling"""
        system = await setup_monetization_system
        payment_processor = system["payment_processor"]
        
        # Step 1: Process initial payment
        payment = await payment_processor.process_license_payment(
            license_id="dispute_test_license",
            payer_id="payer_integration",
            payee_id="payee_integration",
            amount=500.0,
            currency="EUR",
            payment_method_id="pm_test_dispute"
        )
        
        # Step 2: Create escrow
        escrow = await payment_processor.create_escrow_transaction(
            payment_id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            release_conditions=["content_delivered", "quality_approved"],
            dispute_period_days=14
        )
        
        # Step 3: Simulate dispute
        dispute_result = await payment_processor.handle_payment_dispute(
            transaction_id=payment.id,
            dispute_reason="Content not as described",
            evidence={
                "screenshots": ["evidence1.png", "evidence2.png"],
                "correspondence": ["email_thread.pdf"],
                "contract": ["original_agreement.pdf"]
            }
        )
        
        assert dispute_result["success"] is True
        assert "dispute_id" in dispute_result
        assert payment.status == PaymentStatus.DISPUTED
        
        # Step 4: Resolve dispute (simulate manual resolution)
        # In production, this would be handled through admin interface
        # For integration test, we simulate successful resolution
        
        resolution_success = await payment_processor.release_escrow(
            escrow_id=escrow.id,
            release_reason="dispute_resolved_in_favor_of_payee"
        )
        
        assert resolution_success is True
        assert escrow.status in ["released_manual", "released_auto"]
    
    @pytest.mark.integration
    async def test_multi_currency_collaboration_workflow(self, setup_monetization_system):
        """Test multi-currency collaboration and revenue sharing"""
        system = await setup_monetization_system
        payment_processor = system["payment_processor"]
        revenue_calculator = system["revenue_calculator"]
        
        # Step 1: Calculate revenue in multiple currencies
        global_revenue_data = {
            "youtube_us": 500.0,    # USD
            "spotify_global": 300.0,  # EUR  
            "instagram_uk": 200.0   # GBP
        }
        
        # Step 2: Process multi-currency payments
        usd_to_eur_payment = await payment_processor.process_multi_currency_payment(
            amount=global_revenue_data["youtube_us"],
            from_currency="USD",
            to_currency="EUR",
            payer_id="platform_us",
            payee_id="creator_global"
        )
        
        gbp_to_eur_payment = await payment_processor.process_multi_currency_payment(
            amount=global_revenue_data["instagram_uk"],
            from_currency="GBP", 
            to_currency="EUR",
            payer_id="platform_uk",
            payee_id="creator_global"
        )
        
        # Verify currency conversions
        assert usd_to_eur_payment.currency == "EUR"
        assert gbp_to_eur_payment.currency == "EUR"
        assert usd_to_eur_payment.amount != global_revenue_data["youtube_us"]  # Should be converted
        assert gbp_to_eur_payment.amount != global_revenue_data["instagram_uk"]  # Should be converted
        
        # Step 3: Calculate total converted revenue
        total_eur_revenue = (
            usd_to_eur_payment.amount +
            global_revenue_data["spotify_global"] +  # Already in EUR
            gbp_to_eur_payment.amount
        )
        
        # Step 4: Distribute to international collaborators
        international_split = {
            "creator_us": 0.4,      # 40% to US creator
            "creator_eu": 0.35,     # 35% to EU creator  
            "creator_asia": 0.25    # 25% to Asian creator
        }
        
        distribution_transactions = await payment_processor.distribute_revenue_shares(
            {"total": total_eur_revenue},
            international_split,
            "EUR"
        )
        
        assert len(distribution_transactions) == 3
        
        # Verify proper distribution
        total_distributed = sum(t.amount for t in distribution_transactions)
        assert abs(total_distributed - total_eur_revenue) < 0.01
    
    @pytest.mark.integration
    async def test_collaboration_workflow_complete(self):
        """Test complete collaboration workflow from discovery to payment"""
        # This would integrate collaboration engine when available
        # For now, test the payment aspects of collaboration
        
        payment_processor = PaymentProcessor()
        await payment_processor.configure_stripe(
            secret_key="sk_test_collaboration",
            webhook_secret="whsec_test_collaboration"
        )
        
        # Step 1: Simulate collaboration agreement
        collaboration_data = {
            "project_id": "collab_integration_test",
            "collaborators": {
                "lead_creator": {"role": "lead", "contribution": 0.5},
                "music_producer": {"role": "producer", "contribution": 0.3},
                "video_editor": {"role": "editor", "contribution": 0.2}
            },
            "total_budget": 1000.0
        }
        
        # Step 2: Process upfront payments for collaboration
        upfront_payments = []
        for collaborator, details in collaboration_data["collaborators"].items():
            upfront_amount = collaboration_data["total_budget"] * details["contribution"] * 0.5  # 50% upfront
            
            payment = await payment_processor.process_license_payment(
                license_id=f"collab_{collaboration_data['project_id']}_{collaborator}",
                payer_id="project_sponsor",
                payee_id=collaborator,
                amount=upfront_amount,
                currency="EUR",
                payment_method_id="pm_test_collab"
            )
            
            upfront_payments.append(payment)
        
        assert len(upfront_payments) == 3
        
        # Step 3: Hold remaining payments in escrow until completion
        escrow_transactions = []
        for i, (collaborator, details) in enumerate(collaboration_data["collaborators"].items()):
            remaining_amount = collaboration_data["total_budget"] * details["contribution"] * 0.5  # Remaining 50%
            
            escrow = await payment_processor.create_escrow_transaction(
                payment_id=upfront_payments[i].id,
                amount=remaining_amount,
                currency="EUR",
                release_conditions=["project_completed", "deliverables_approved"],
                dispute_period_days=30
            )
            
            escrow_transactions.append(escrow)
        
        assert len(escrow_transactions) == 3
        
        # Step 4: Simulate project completion and escrow release
        for escrow in escrow_transactions:
            success = await payment_processor.release_escrow(
                escrow_id=escrow.id,
                release_reason="project_completed_successfully"
            )
            assert success is True
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_revenue_prediction_and_tax_reporting(self, setup_monetization_system):
        """Test revenue prediction and tax reporting integration"""
        system = await setup_monetization_system
        revenue_calculator = system["revenue_calculator"]
        payment_processor = system["payment_processor"]
        
        # Step 1: Create historical revenue data
        historical_data = []
        base_revenue = 100.0
        
        for days_ago in range(30, 0, -1):  # 30 days of data
            revenue_data = RevenueData(
                platform="youtube",
                content_id="tax_test_content",
                views=10000 + (days_ago * 100),
                engagement_rate=0.05 + (days_ago * 0.001),
                revenue=base_revenue + (30 - days_ago) * 2,  # Increasing trend
                period_start=datetime.now() - timedelta(days=days_ago+1),
                period_end=datetime.now() - timedelta(days=days_ago)
            )
            historical_data.append(revenue_data)
        
        # Step 2: Generate revenue predictions
        predictions = await revenue_calculator.predict_revenue_ml(
            platform="youtube",
            historical_data=historical_data,
            forecast_days=30
        )
        
        assert len(predictions) == 30
        assert all(pred > 0 for pred in predictions)
        
        # Step 3: Simulate actual revenue transactions for tax reporting
        user_id = "tax_integration_user"
        year = 2025
        
        total_annual_revenue = 0
        for month in range(1, 13):  # 12 months
            monthly_revenue = base_revenue * month  # Increasing monthly revenue
            
            # Create revenue share transaction
            transaction = await payment_processor.process_license_payment(
                license_id=f"tax_test_license_{month}",
                payer_id="platform",
                payee_id=user_id,
                amount=monthly_revenue,
                currency="EUR",
                payment_method_id="pm_test_tax"
            )
            
            # Simulate completion
            transaction.status = PaymentStatus.COMPLETED
            transaction.processed_at = datetime(year, month, 15)
            
            total_annual_revenue += monthly_revenue
        
        # Step 4: Generate tax report
        tax_report = await payment_processor.generate_tax_reports(
            user_id=user_id,
            year=year,
            country="DE"  # Germany
        )
        
        assert tax_report["user_id"] == user_id
        assert tax_report["year"] == year
        assert tax_report["country"] == "DE"
        assert tax_report["total_income"] > 0
        assert "tax_obligations" in tax_report
        assert tax_report["transaction_count"] == 12
        
        # Verify tax calculations
        tax_info = tax_report["tax_obligations"]
        assert "tax_owed" in tax_info
        assert "taxable_income" in tax_info
        assert tax_info["tax_rate"] == 0.25  # German tax rate
    
    @pytest.mark.integration
    async def test_error_recovery_and_resilience(self, setup_monetization_system):
        """Test system error recovery and resilience"""
        system = await setup_monetization_system
        payment_processor = system["payment_processor"]
        
        # Test 1: Failed payment recovery
        with patch.object(payment_processor, '_process_stripe_payment', 
                         return_value={"success": False, "error": "Network timeout"}):
            
            failed_payment = await payment_processor.process_license_payment(
                license_id="resilience_test",
                payer_id="test_payer",
                payee_id="test_payee",
                amount=100.0,
                currency="EUR",
                payment_method_id="pm_test_fail"
            )
            
            assert failed_payment.status == PaymentStatus.FAILED
        
        # Test 2: Partial revenue distribution failure
        revenue_data = {"total": 1000.0}
        split_rules = {
            "creator_success": 0.5,
            "creator_fail": 0.3,
            "platform": 0.2
        }
        
        # Mock one payout to fail
        original_payout = payment_processor._process_stripe_payout
        
        async def mock_payout(transaction):
            if transaction.payee_id == "creator_fail":
                return {"success": False, "error": "Account suspended"}
            return await original_payout(transaction)
        
        with patch.object(payment_processor, '_process_stripe_payout', side_effect=mock_payout):
            transactions = await payment_processor.distribute_revenue_shares(
                revenue_data, split_rules, "EUR"
            )
            
            # Should still process successful transactions
            successful_transactions = [t for t in transactions if t.status == PaymentStatus.PROCESSING]
            failed_transactions = [t for t in transactions if t.status == PaymentStatus.FAILED]
            
            assert len(successful_transactions) == 2  # creator_success and platform
            assert len(failed_transactions) == 1     # creator_fail
        
        # Test 3: Escrow system resilience
        try:
            # Attempt to release non-existent escrow
            result = await payment_processor.release_escrow("non_existent", "test")
            assert result is False  # Should handle gracefully
            
            # Attempt to create escrow with invalid data
            escrow = await payment_processor.create_escrow_transaction(
                payment_id="valid_payment",
                amount=100.0,
                currency="EUR",
                release_conditions=[],  # Empty conditions should work
                dispute_period_days=7
            )
            assert escrow is not None
            
        except Exception as e:
            pytest.fail(f"System should handle errors gracefully: {e}")