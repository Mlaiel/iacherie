"""
Payment Processing Agent - Usage Examples

Industrial examples demonstrating payment processing capabilities,
fraud detection, compliance, analytics, and currency conversion.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any

# Import payment processing components
from . import (
    PaymentProcessingService,
    get_payment_agent,
    PaymentConfig,
    PaymentTransaction,
    PaymentMethod,
    RevenueAllocation
)

logger = logging.getLogger(__name__)


async def example_basic_payment_processing():
    """Example: Basic payment processing workflow"""
    print("=== Basic Payment Processing Example ===")
    
    # Get payment agent
    agent = await get_payment_agent()
    
    # Process a payment
    transaction = await agent.process_payment(
        creator_id="creator_123",
        amount=Decimal("29.99"),
        currency="USD",
        source="subscription",
        payment_method="stripe",
        metadata={
            "subscriber_id": "user_456",
            "plan": "premium_monthly",
            "ip_address": "203.0.113.1",
            "user_agent": "Mozilla/5.0..."
        }
    )
    
    print(f"✅ Payment processed: {transaction.id}")
    print(f"   Amount: ${transaction.amount} {transaction.currency}")
    print(f"   Status: {transaction.status}")
    print(f"   Fee: ${transaction.fee_amount}")
    
    return transaction


async def example_revenue_allocation():
    """Example: Revenue allocation and creator payments"""
    print("\n=== Revenue Allocation Example ===")
    
    agent = await get_payment_agent()
    
    # Allocate revenue from multiple sources
    allocations = await agent.allocate_revenue(
        creator_id="creator_123",
        total_revenue=Decimal("1000.00"),
        currency="USD",
        sources={
            "subscriptions": Decimal("600.00"),
            "tips": Decimal("250.00"),
            "merchandise": Decimal("150.00")
        },
        period_start=datetime(2025, 8, 1),
        period_end=datetime(2025, 8, 31)
    )
    
    for allocation in allocations:
        print(f"📊 Revenue source: {allocation.source}")
        print(f"   Gross: ${allocation.gross_amount}")
        print(f"   Net: ${allocation.net_amount}")
        print(f"   Platform fee: ${allocation.platform_fee}")
        print(f"   Tax: ${allocation.tax_amount}")
    
    return allocations


async def example_fraud_detection():
    """Example: Fraud detection and risk assessment"""
    print("\n=== Fraud Detection Example ===")
    
    agent = await get_payment_agent()
    
    # Analyze suspicious transaction
    fraud_analysis = await agent.analyze_fraud(
        amount=Decimal("500.00"),
        user_id="user_suspicious_789",
        payment_method="crypto",
        metadata={
            "ip_address": "192.0.2.1",
            "country": "XX",  # Unknown country
            "device_fingerprint": "suspicious_device",
            "is_vpn": True,
            "velocity_score": 0.8  # High velocity
        }
    )
    
    print(f"🔍 Fraud Analysis Results:")
    print(f"   Risk Level: {fraud_analysis['risk_classification']}")
    print(f"   Risk Score: {fraud_analysis['risk_level']:.2f}")
    print(f"   Recommendation: {fraud_analysis['recommendation']}")
    print(f"   Risk Factors: {', '.join(fraud_analysis['risk_factors'])}")
    
    return fraud_analysis


async def example_currency_conversion():
    """Example: Multi-currency payment processing"""
    print("\n=== Currency Conversion Example ===")
    
    agent = await get_payment_agent()
    
    # Convert payment from EUR to USD
    converted_payment = await agent.process_payment(
        creator_id="creator_europe_456",
        amount=Decimal("25.00"),  # 25 EUR
        currency="EUR",
        target_currency="USD",  # Convert to USD
        source="subscription",
        payment_method="stripe"
    )
    
    print(f"💱 Currency Conversion:")
    print(f"   Original: €{converted_payment.amount} EUR")
    print(f"   Converted: ${converted_payment.converted_amount} USD")
    print(f"   Exchange Rate: {converted_payment.exchange_rate}")
    
    return converted_payment


async def example_compliance_check():
    """Example: KYC/AML compliance verification"""
    print("\n=== Compliance Check Example ===")
    
    agent = await get_payment_agent()
    
    # Check compliance for high-value transaction
    compliance_result = await agent.check_compliance(
        creator_id="creator_high_value_789",
        transaction_amount=Decimal("10000.00"),
        transaction_type="payout",
        jurisdiction="US",
        metadata={
            "identity_verified": True,
            "address_verified": False,
            "income_documents": ["w2_2024.pdf"],
            "risk_score": 0.3
        }
    )
    
    print(f"⚖️  Compliance Check:")
    print(f"   Status: {compliance_result['status']}")
    print(f"   KYC Level: {compliance_result['kyc_level']}")
    print(f"   Required Actions: {compliance_result['required_actions']}")
    
    if compliance_result['violations']:
        print(f"   ⚠️  Violations: {compliance_result['violations']}")
    
    return compliance_result


async def example_payout_scheduling():
    """Example: Automated payout scheduling"""
    print("\n=== Payout Scheduling Example ===")
    
    agent = await get_payment_agent()
    
    # Schedule weekly payouts for creator
    payout_schedule = await agent.schedule_payout(
        creator_id="creator_weekly_123",
        frequency="weekly",
        day_of_week=5,  # Friday
        minimum_amount=Decimal("50.00"),
        currency="USD",
        payment_method_id="bank_account_456",
        auto_tax_calculation=True
    )
    
    print(f"📅 Payout Schedule Created:")
    print(f"   Schedule ID: {payout_schedule.id}")
    print(f"   Frequency: {payout_schedule.frequency}")
    print(f"   Next Payout: {payout_schedule.next_execution}")
    print(f"   Minimum Amount: ${payout_schedule.minimum_amount}")
    
    return payout_schedule


async def example_analytics_dashboard():
    """Example: Revenue analytics and insights"""
    print("\n=== Analytics Dashboard Example ===")
    
    agent = await get_payment_agent()
    
    # Get creator analytics for the month
    analytics = await agent.get_revenue_analytics(
        creator_id="creator_analytics_789",
        start_date=datetime(2025, 8, 1),
        end_date=datetime(2025, 8, 31),
        granularity="daily"
    )
    
    print(f"📈 Revenue Analytics:")
    print(f"   Total Revenue: ${analytics['total_revenue']}")
    print(f"   Revenue Growth: {analytics['revenue_growth']:.1f}%")
    print(f"   Top Source: {analytics['top_revenue_source']}")
    print(f"   Average Transaction: ${analytics['avg_transaction_amount']}")
    print(f"   Conversion Rate: {analytics['conversion_rate']:.2f}%")
    
    # Revenue forecast
    forecast = analytics.get('revenue_forecast', {})
    if forecast:
        print(f"   📊 Next Month Forecast: ${forecast['predicted_amount']}")
        print(f"   Confidence: {forecast['confidence']:.1f}%")
    
    return analytics


async def example_webhook_handling():
    """Example: Webhook processing for payment updates"""
    print("\n=== Webhook Handling Example ===")
    
    agent = await get_payment_agent()
    
    # Simulate Stripe webhook
    webhook_payload = {
        "id": "evt_stripe_123",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_stripe_456",
                "amount": 2999,  # $29.99
                "currency": "usd",
                "status": "succeeded",
                "metadata": {
                    "creator_id": "creator_123",
                    "source": "subscription"
                }
            }
        }
    }
    
    # Process webhook
    result = await agent.process_webhook(
        provider="stripe",
        event_type="payment_intent.succeeded",
        payload=webhook_payload,
        signature="stripe_signature_hash"
    )
    
    print(f"🔗 Webhook Processed:")
    print(f"   Event ID: {result['event_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Action Taken: {result['action']}")
    
    return result


async def example_multi_provider_processing():
    """Example: Multi-provider payment processing"""
    print("\n=== Multi-Provider Processing Example ===")
    
    agent = await get_payment_agent()
    
    # Process payments through different providers
    providers_test = [
        ("stripe", Decimal("29.99"), "USD"),
        ("paypal", Decimal("19.99"), "EUR"), 
        ("wise", Decimal("49.99"), "GBP"),
        ("crypto", Decimal("0.001"), "BTC")
    ]
    
    results = []
    for provider, amount, currency in providers_test:
        try:
            transaction = await agent.process_payment(
                creator_id=f"creator_{provider}",
                amount=amount,
                currency=currency,
                source="test_payment",
                payment_method=provider,
                metadata={"provider_test": True}
            )
            
            results.append({
                "provider": provider,
                "status": "success",
                "transaction_id": transaction.id,
                "amount": f"{amount} {currency}"
            })
            
            print(f"✅ {provider.upper()}: {amount} {currency} - Success")
            
        except Exception as e:
            results.append({
                "provider": provider,
                "status": "failed",
                "error": str(e),
                "amount": f"{amount} {currency}"
            })
            
            print(f"❌ {provider.upper()}: {amount} {currency} - Failed: {str(e)}")
    
    return results


async def example_performance_monitoring():
    """Example: Performance monitoring and metrics"""
    print("\n=== Performance Monitoring Example ===")
    
    # Get service instance for monitoring
    from . import get_service
    service = await get_service()
    
    # Get comprehensive health check
    health = await service.health_check()
    
    print(f"🏥 System Health:")
    print(f"   Service Status: {health['service']['status']}")
    print(f"   Components: {len(health['components'])} active")
    
    # Check individual components
    for component, status in health['components'].items():
        print(f"   📊 {component}: {status['status']}")
        
        if 'metrics' in status:
            metrics = status['metrics']
            if isinstance(metrics, dict):
                if 'total' in metrics:
                    total = metrics['total']
                    hit_rate = total.get('hit_count', 0) / max(1, total.get('hit_count', 0) + total.get('miss_count', 0))
                    print(f"      Cache Hit Rate: {hit_rate:.2%}")
    
    return health


async def run_all_examples():
    """Run all payment processing examples"""
    print("🚀 Payment Processing Agent - Industrial Examples")
    print("=" * 60)
    
    try:
        # Initialize service
        service = PaymentProcessingService(
            enable_cache=True,
            enable_fraud_detection=True,
            enable_analytics=True,
            enable_compliance=True,
            enable_scheduling=True
        )
        
        async with service.lifespan():
            # Run all examples
            await example_basic_payment_processing()
            await example_revenue_allocation()
            await example_fraud_detection()
            await example_currency_conversion()
            await example_compliance_check()
            await example_payout_scheduling()
            await example_analytics_dashboard()
            await example_webhook_handling()
            await example_multi_provider_processing()
            await example_performance_monitoring()
            
            print("\n🎉 All examples completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Example execution failed: {str(e)}")
        logger.error(f"Example execution error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(run_all_examples())
