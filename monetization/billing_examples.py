"""
Comprehensive Billing Engine - Usage Examples
=============================================

This document provides complete examples of how to use the advanced billing engine
with all its features including subscriptions, fraud detection, payment processing,
and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from monetization import (
    ComprehensiveBillingEngine,
    AdvancedSubscriptionManager,
    AdvancedFraudDetector,
    BillingCycle,
    ProrationMethod,
    TransactionContext,
    billing_router
)


async def example_complete_billing_workflow():
    """
    Complete example showing the full billing workflow
    """
    print("=== Complete Billing Workflow Example ===\n")
    
    # 1. Initialize the billing system
    billing_engine = ComprehensiveBillingEngine()
    subscription_manager = AdvancedSubscriptionManager(billing_engine)
    fraud_detector = AdvancedFraudDetector()
    
    print("✓ Billing system initialized")
    
    # 2. Create a subscription for a customer
    print("\n--- Creating Subscription ---")
    subscription = await subscription_manager.create_subscription_with_plan(
        customer_id="customer_123",
        plan_id="professional",
        billing_cycle=BillingCycle.MONTHLY,
        coupon_code="WELCOME10"  # 10% discount
    )
    
    print(f"✓ Subscription created: {subscription.id}")
    print(f"  - Plan: {subscription.plan_id}")
    print(f"  - Amount: {subscription.amount} {subscription.currency}")
    print(f"  - Billing Cycle: {subscription.billing_cycle.value}")
    print(f"  - Next Billing: {subscription.next_billing_date}")
    
    # 3. Generate and process invoice
    print("\n--- Invoice Generation and Payment Processing ---")
    invoice = await billing_engine.generate_invoice(subscription.id)
    
    print(f"✓ Invoice generated: {invoice.id}")
    print(f"  - Amount: {invoice.amount} {invoice.currency}")
    print(f"  - Tax: {invoice.tax_amount} {invoice.currency}")
    print(f"  - Total: {invoice.total_amount} {invoice.currency}")
    print(f"  - Due Date: {invoice.due_date}")
    
    # 4. Fraud detection analysis
    print("\n--- Fraud Detection Analysis ---")
    fraud_context = TransactionContext(
        transaction_id=invoice.id,
        customer_id=subscription.customer_id,
        amount=invoice.total_amount,
        currency=invoice.currency,
        timestamp=datetime.now(),
        ip_address="192.168.1.100",
        device_fingerprint="device_fingerprint_abc123",
        billing_country="DE",
        email="customer@example.com"
    )
    
    fraud_analysis = await fraud_detector.analyze_transaction(fraud_context)
    
    print(f"✓ Fraud analysis completed")
    print(f"  - Risk Level: {fraud_analysis.risk_level.value}")
    print(f"  - Risk Score: {fraud_analysis.risk_score}/100")
    print(f"  - Flags: {fraud_analysis.flags}")
    print(f"  - Recommended Action: {fraud_analysis.recommended_action}")
    
    # 5. Process payment with failover
    print("\n--- Payment Processing with Failover ---")
    # Mock successful payment processing
    billing_engine.multi_provider_service.process_payment = mock_successful_payment
    
    payment_result = await billing_engine.process_payment_with_failover(
        invoice_id=invoice.id,
        payment_method_id="pm_1234567890"
    )
    
    print(f"✓ Payment processed: {payment_result['success']}")
    if payment_result['success']:
        print(f"  - Provider: {payment_result['provider_used']}")
        print(f"  - Transaction ID: {payment_result['transaction_id']}")
    
    # 6. Subscription upgrade with proration
    print("\n--- Subscription Upgrade with Proration ---")
    upgrade_result = await subscription_manager.upgrade_subscription(
        subscription_id=subscription.id,
        new_plan_id="enterprise",
        proration_method=ProrationMethod.IMMEDIATE
    )
    
    print(f"✓ Subscription upgraded: {upgrade_result['success']}")
    print(f"  - New Plan: {upgrade_result['new_plan']}")
    print(f"  - Proration Amount: {upgrade_result['proration_amount']}")
    print(f"  - Effective Date: {upgrade_result['effective_date']}")
    
    # 7. Generate analytics and reports
    print("\n--- Analytics and Reporting ---")
    
    # Revenue analytics
    revenue_analytics = await billing_engine.get_revenue_analytics(
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        currency="EUR"
    )
    
    print(f"✓ Revenue Analytics (Last 30 days):")
    print(f"  - Total Revenue: {revenue_analytics['total_revenue']} EUR")
    print(f"  - Subscription Revenue: {revenue_analytics['subscription_revenue']} EUR")
    print(f"  - Predicted Next 30 Days: {revenue_analytics['predicted_next_30_days']} EUR")
    
    # Subscription analytics
    subscription_analytics = await subscription_manager.get_subscription_analytics()
    
    print(f"✓ Subscription Analytics:")
    print(f"  - Total Subscriptions: {subscription_analytics['total_subscriptions']}")
    print(f"  - Active Subscriptions: {subscription_analytics['active_subscriptions']}")
    print(f"  - MRR: {subscription_analytics['monthly_recurring_revenue']} EUR")
    print(f"  - Churn Rate: {subscription_analytics['churn_rate']:.2%}")
    
    # Financial report
    financial_report = await billing_engine.generate_financial_report(
        report_type="monthly",
        year=datetime.now().year,
        month=datetime.now().month
    )
    
    print(f"✓ Financial Report Generated: {financial_report['report_id']}")
    print(f"  - Total Invoiced: {financial_report['summary']['total_invoiced']}")
    print(f"  - Total Paid: {financial_report['summary']['total_paid']}")
    print(f"  - Payment Success Rate: {financial_report['summary']['payment_success_rate']:.2%}")
    
    return {
        "subscription": subscription,
        "invoice": invoice,
        "fraud_analysis": fraud_analysis,
        "payment_result": payment_result,
        "upgrade_result": upgrade_result,
        "analytics": {
            "revenue": revenue_analytics,
            "subscriptions": subscription_analytics,
            "financial_report": financial_report
        }
    }


async def example_subscription_lifecycle():
    """
    Example showing complete subscription lifecycle management
    """
    print("\n\n=== Subscription Lifecycle Management ===\n")
    
    billing_engine = ComprehensiveBillingEngine()
    subscription_manager = AdvancedSubscriptionManager(billing_engine)
    
    # 1. Create subscription with trial
    print("--- Creating Subscription with Trial ---")
    subscription = await subscription_manager.create_subscription_with_plan(
        customer_id="customer_456",
        plan_id="basic",
        billing_cycle=BillingCycle.MONTHLY,
        trial_days=14
    )
    
    print(f"✓ Subscription with trial: {subscription.id}")
    print(f"  - Trial ends: {subscription.trial_end}")
    
    # 2. Pause subscription
    print("\n--- Pausing Subscription ---")
    pause_result = await subscription_manager.pause_subscription(
        subscription_id=subscription.id,
        pause_until=datetime.now() + timedelta(days=30),
        reason="customer_vacation"
    )
    
    print(f"✓ Subscription paused: {pause_result['success']}")
    print(f"  - Paused until: {pause_result['paused_until']}")
    print(f"  - Next billing: {pause_result['next_billing_date']}")
    
    # 3. Resume subscription (would be called when pause expires)
    # subscription.status = SubscriptionStatus.ACTIVE
    
    # 4. Downgrade subscription
    print("\n--- Downgrading Subscription ---")
    subscription.status = SubscriptionStatus.ACTIVE  # Resume for downgrade
    
    downgrade_result = await subscription_manager.downgrade_subscription(
        subscription_id=subscription.id,
        new_plan_id="basic",  # Already basic, but for example
        proration_method=ProrationMethod.NEXT_CYCLE
    )
    
    print(f"✓ Subscription downgrade scheduled: {downgrade_result['success']}")
    print(f"  - Effective date: {downgrade_result['effective_date']}")
    
    # 5. Cancel subscription
    print("\n--- Cancelling Subscription ---")
    cancel_result = await subscription_manager.cancel_subscription(
        subscription_id=subscription.id,
        cancel_immediately=False,  # Cancel at period end
        reason="customer_request"
    )
    
    print(f"✓ Subscription cancelled: {cancel_result['success']}")
    print(f"  - Effective date: {cancel_result['effective_date']}")
    print(f"  - Immediate: {cancel_result['immediate']}")
    
    return subscription


async def example_fraud_detection_scenarios():
    """
    Example showing various fraud detection scenarios
    """
    print("\n\n=== Fraud Detection Scenarios ===\n")
    
    fraud_detector = AdvancedFraudDetector()
    
    # Scenario 1: High-risk transaction
    print("--- High-Risk Transaction Analysis ---")
    high_risk_context = TransactionContext(
        transaction_id="tx_high_risk_001",
        customer_id="suspicious_customer",
        amount=Decimal("5000.00"),  # High amount
        currency="EUR",
        timestamp=datetime.now(),
        ip_address="1.2.3.4",  # Suspicious IP
        device_fingerprint="new_device_fingerprint",
        billing_country="XX",  # High-risk country
        email="temp_email@tempmail.com"  # Temporary email
    )
    
    high_risk_analysis = await fraud_detector.analyze_transaction(high_risk_context)
    
    print(f"✓ High-risk analysis:")
    print(f"  - Risk Level: {high_risk_analysis.risk_level.value}")
    print(f"  - Risk Score: {high_risk_analysis.risk_score}/100")
    print(f"  - Flags: {high_risk_analysis.flags}")
    print(f"  - Action: {high_risk_analysis.recommended_action}")
    
    # Scenario 2: Velocity check
    print("\n--- Velocity Anomaly Detection ---")
    customer_id = "velocity_test_customer"
    
    # Simulate multiple rapid transactions
    for i in range(6):  # Trigger velocity rule (5+ transactions in 10 minutes)
        velocity_context = TransactionContext(
            transaction_id=f"tx_velocity_{i}",
            customer_id=customer_id,
            amount=Decimal("100.00"),
            currency="EUR",
            timestamp=datetime.now() - timedelta(minutes=i),
            ip_address="192.168.1.1",
            billing_country="DE",
            email="customer@example.com"
        )
        
        velocity_analysis = await fraud_detector.analyze_transaction(velocity_context)
        
        if i == 5:  # Last transaction should trigger velocity alert
            print(f"✓ Velocity analysis (transaction {i+1}):")
            print(f"  - Risk Level: {velocity_analysis.risk_level.value}")
            print(f"  - Flags: {velocity_analysis.flags}")
    
    # Scenario 3: Pattern detection
    print("\n--- Pattern Detection (Test + Large Transaction) ---")
    
    # Small test transaction
    test_context = TransactionContext(
        transaction_id="tx_test_small",
        customer_id="pattern_test_customer",
        amount=Decimal("5.00"),  # Small test amount
        currency="EUR",
        timestamp=datetime.now() - timedelta(minutes=5),
        billing_country="DE"
    )
    
    await fraud_detector.analyze_transaction(test_context)
    
    # Large transaction following test
    large_context = TransactionContext(
        transaction_id="tx_large_follow",
        customer_id="pattern_test_customer",
        amount=Decimal("500.00"),  # Large amount
        currency="EUR",
        timestamp=datetime.now(),
        billing_country="DE"
    )
    
    pattern_analysis = await fraud_detector.analyze_transaction(large_context)
    
    print(f"✓ Pattern analysis:")
    print(f"  - Risk Level: {pattern_analysis.risk_level.value}")
    print(f"  - Flags: {pattern_analysis.flags}")
    print(f"  - Action: {pattern_analysis.recommended_action}")
    
    # Get fraud statistics
    fraud_stats = await fraud_detector.get_fraud_statistics(days=1)
    print(f"\n✓ Fraud Statistics (Last 24 hours):")
    print(f"  - Total Events: {fraud_stats['total_fraud_events']}")
    print(f"  - Fraud Signals: {fraud_stats['fraud_signals']}")
    print(f"  - Actions Taken: {fraud_stats['actions_taken']}")
    
    return fraud_detector


async def example_refund_processing():
    """
    Example showing refund processing workflow
    """
    print("\n\n=== Refund Processing Example ===\n")
    
    billing_engine = ComprehensiveBillingEngine()
    subscription_manager = AdvancedSubscriptionManager(billing_engine)
    
    # Create subscription and invoice
    subscription = await subscription_manager.create_subscription_with_plan(
        customer_id="refund_customer",
        plan_id="professional",
        billing_cycle=BillingCycle.MONTHLY
    )
    
    invoice = await billing_engine.generate_invoice(subscription.id)
    
    # Mark invoice as paid (simulate successful payment)
    invoice.status = InvoiceStatus.PAID
    invoice.paid_at = datetime.now()
    
    print(f"✓ Setup: Invoice {invoice.id} paid for {invoice.total_amount} {invoice.currency}")
    
    # Process partial refund
    print("\n--- Partial Refund ---")
    partial_refund = await billing_engine.process_refund(
        invoice_id=invoice.id,
        amount=Decimal("15.00"),
        reason="service_issue"
    )
    
    print(f"✓ Partial refund: {partial_refund['success']}")
    print(f"  - Refund ID: {partial_refund['refund_id']}")
    print(f"  - Amount: {partial_refund['amount']} EUR")
    
    # Process full refund (create new invoice for demo)
    invoice2 = await billing_engine.generate_invoice(subscription.id)
    invoice2.status = InvoiceStatus.PAID
    invoice2.paid_at = datetime.now()
    
    print("\n--- Full Refund ---")
    full_refund = await billing_engine.process_refund(
        invoice_id=invoice2.id,
        reason="customer_cancellation"
    )
    
    print(f"✓ Full refund: {full_refund['success']}")
    print(f"  - Refund ID: {full_refund['refund_id']}")
    print(f"  - Amount: {full_refund['amount']} EUR")
    print(f"  - Invoice Status: {invoice2.status.value}")
    
    return {"partial_refund": partial_refund, "full_refund": full_refund}


# Mock function for successful payment
async def mock_successful_payment(*args, **kwargs):
    """Mock successful payment for example"""
    return {
        "success": True,
        "transaction_id": "mock_tx_123456"
    }


async def run_all_examples():
    """
    Run all billing system examples
    """
    print("🚀 Starting Comprehensive Billing Engine Examples\n")
    
    try:
        # Run complete workflow
        workflow_result = await example_complete_billing_workflow()
        
        # Run subscription lifecycle
        lifecycle_subscription = await example_subscription_lifecycle()
        
        # Run fraud detection scenarios
        fraud_detector = await example_fraud_detection_scenarios()
        
        # Run refund processing
        refund_results = await example_refund_processing()
        
        print("\n\n🎉 All Examples Completed Successfully!")
        print("✅ Comprehensive billing engine is fully operational")
        
        return {
            "workflow": workflow_result,
            "lifecycle": lifecycle_subscription,
            "fraud": fraud_detector,
            "refunds": refund_results
        }
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_examples())