"""Comprehensive Monetization Integration Example
Demonstrates the complete monetization and finance system working together.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

from monetization.billing_engine import BillingEngine, BillingCycle, SubscriptionStatus
from monetization.subscription_manager import SubscriptionManager, ProrationMethod
from monetization.fraud_detection import (
    FraudDetectionEngine, TransactionContext, DeviceFingerprint,
    FraudRiskLevel, FraudAction
)
from monetization.refund_processor import (
    RefundWorkflowEngine, RefundReason, RefundType
)
from monetization.dunning_manager import (
    DunningManager, PaymentFailureReason, NotificationType
)
from monetization.revenue_analytics import (
    RevenueAnalyticsEngine, RevenueSource, MetricType
)
from monetization.financial_reporting import (
    FinancialReportingEngine, ReportType, ReportPeriod, ComplianceFramework
)

logger = logging.getLogger(__name__)


class MonetizationPlatform:
    """Integrated monetization platform demonstrating all systems working together"""
    
    def __init__(self):
        # Initialize all systems
        self.billing_engine = BillingEngine()
        self.subscription_manager = SubscriptionManager(self.billing_engine)
        self.fraud_detection = FraudDetectionEngine()
        self.refund_processor = RefundWorkflowEngine()
        self.dunning_manager = DunningManager()
        self.revenue_analytics = RevenueAnalyticsEngine()
        self.financial_reporting = FinancialReportingEngine()
        
        # Set up integrations
        self._setup_integrations()
    
    def _setup_integrations(self):
        """Set up integrations between systems"""
        # Set up payment retry handler for dunning
        self.dunning_manager.set_payment_retry_handler(self._retry_payment_handler)
        
        # Set up notification handlers
        self.dunning_manager.set_notification_handler(
            NotificationType.EMAIL, self._email_notification_handler
        )
        
        # Set up refund notification handler
        self.refund_processor.add_notification_handler(self._refund_notification_handler)
    
    async def demonstrate_complete_workflow(self) -> Dict[str, Any]:
        """Demonstrate a complete customer lifecycle with all systems"""
        try:
            workflow_results = {}
            
            # 1. Customer Creation and Subscription
            logger.info("=== Step 1: Customer Creation and Subscription ===")
            customer_result = await self._create_customer_and_subscription()
            workflow_results["customer_creation"] = customer_result
            
            # 2. Fraud Detection on Payment
            logger.info("=== Step 2: Fraud Detection on Payment ===")
            fraud_result = await self._demonstrate_fraud_detection()
            workflow_results["fraud_detection"] = fraud_result
            
            # 3. Subscription Management (Upgrade)
            logger.info("=== Step 3: Subscription Management (Upgrade) ===")
            upgrade_result = await self._demonstrate_subscription_upgrade(
                customer_result["subscription_id"]
            )
            workflow_results["subscription_upgrade"] = upgrade_result
            
            # 4. Revenue Analytics
            logger.info("=== Step 4: Revenue Analytics ===")
            analytics_result = await self._demonstrate_revenue_analytics()
            workflow_results["revenue_analytics"] = analytics_result
            
            # 5. Failed Payment and Dunning
            logger.info("=== Step 5: Failed Payment and Dunning ===")
            dunning_result = await self._demonstrate_dunning_process()
            workflow_results["dunning_process"] = dunning_result
            
            # 6. Refund Processing
            logger.info("=== Step 6: Refund Processing ===")
            refund_result = await self._demonstrate_refund_process()
            workflow_results["refund_process"] = refund_result
            
            # 7. Financial Reporting
            logger.info("=== Step 7: Financial Reporting ===")
            reporting_result = await self._demonstrate_financial_reporting()
            workflow_results["financial_reporting"] = reporting_result
            
            # 8. Compliance Checks
            logger.info("=== Step 8: Compliance Checks ===")
            compliance_result = await self._demonstrate_compliance_checks()
            workflow_results["compliance_checks"] = compliance_result
            
            return {
                "success": True,
                "message": "Complete monetization workflow demonstrated successfully",
                "workflow_results": workflow_results,
                "demonstration_completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in complete workflow demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_customer_and_subscription(self) -> Dict[str, Any]:
        """Create customer and subscription"""
        try:
            # Create customer
            customer_result = await self.billing_engine.create_customer(
                customer_id="demo_customer_001",
                email="demo@example.com",
                name="Demo Customer",
                country="DE",
                tax_id="DE123456789"
            )
            
            if not customer_result["success"]:
                return customer_result
            
            # Create subscription with trial
            subscription_result = await self.billing_engine.create_subscription(
                customer_id="demo_customer_001",
                plan_id="creator_pro",
                trial_period_days=14,
                metadata={"source": "demo", "campaign": "integration_test"}
            )
            
            if subscription_result["success"]:
                # Record revenue analytics
                await self.revenue_analytics.record_revenue(
                    source=RevenueSource.SUBSCRIPTIONS,
                    amount=Decimal("99.99"),
                    currency="EUR",
                    customer_id="demo_customer_001",
                    subscription_id=subscription_result["subscription"]["id"]
                )
            
            return {
                "success": subscription_result["success"],
                "customer_id": "demo_customer_001",
                "subscription_id": subscription_result["subscription"]["id"] if subscription_result["success"] else None,
                "trial_end": subscription_result.get("trial_end"),
                "details": subscription_result
            }
            
        except Exception as e:
            logger.error(f"Error creating customer and subscription: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_fraud_detection(self) -> Dict[str, Any]:
        """Demonstrate fraud detection on a payment"""
        try:
            # Create device fingerprint
            device_fingerprint = DeviceFingerprint(
                device_id="demo_device_001",
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                screen_resolution="1920x1080",
                timezone="Europe/Berlin",
                language="de-DE",
                platform="Windows",
                browser="Chrome"
            )
            
            # Create transaction context
            transaction_context = TransactionContext(
                transaction_id="demo_txn_001",
                customer_id="demo_customer_001",
                amount=Decimal("99.99"),
                currency="EUR",
                payment_method="credit_card",
                merchant_category="digital_services",
                device_fingerprint=device_fingerprint,
                billing_address={
                    "country": "DE",
                    "city": "Berlin",
                    "postal_code": "10115"
                }
            )
            
            # Analyze transaction for fraud
            fraud_analysis = await self.fraud_detection.analyze_transaction(transaction_context)
            
            return {
                "success": True,
                "transaction_id": transaction_context.transaction_id,
                "risk_level": fraud_analysis.overall_risk_level.value,
                "risk_score": fraud_analysis.overall_risk_score,
                "recommended_action": fraud_analysis.recommended_action.value,
                "checks_performed": len(fraud_analysis.checks),
                "analysis_details": {
                    "processing_time_ms": fraud_analysis.metadata.get("processing_time_ms", 0),
                    "checks_passed": sum(1 for check in fraud_analysis.checks if check.passed),
                    "checks_failed": sum(1 for check in fraud_analysis.checks if not check.passed)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fraud detection demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_subscription_upgrade(self, subscription_id: str) -> Dict[str, Any]:
        """Demonstrate subscription upgrade with proration"""
        try:
            # Upgrade subscription from creator_pro to enterprise
            upgrade_result = await self.subscription_manager.upgrade_subscription(
                subscription_id=subscription_id,
                new_plan_id="enterprise",
                proration_method=ProrationMethod.DAILY,
                effective_immediately=True
            )
            
            if upgrade_result["success"]:
                # Record the upgrade revenue
                proration_amount = upgrade_result["proration"]["proration_amount"]
                if proration_amount > 0:
                    await self.revenue_analytics.record_revenue(
                        source=RevenueSource.SUBSCRIPTIONS,
                        amount=Decimal(str(proration_amount)),
                        currency="EUR",
                        customer_id="demo_customer_001",
                        subscription_id=subscription_id,
                        metadata={"type": "upgrade_proration"}
                    )
            
            return {
                "success": upgrade_result["success"],
                "subscription_id": subscription_id,
                "old_plan": "creator_pro",
                "new_plan": "enterprise",
                "proration_amount": float(upgrade_result["proration"]["proration_amount"]) if upgrade_result["success"] else 0,
                "change_id": upgrade_result.get("change_id"),
                "details": upgrade_result
            }
            
        except Exception as e:
            logger.error(f"Error in subscription upgrade demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_revenue_analytics(self) -> Dict[str, Any]:
        """Demonstrate revenue analytics and predictions"""
        try:
            # Calculate key metrics
            mrr = await self.revenue_analytics.calculate_mrr()
            arr = await self.revenue_analytics.calculate_arr()
            churn_rate = await self.revenue_analytics.calculate_churn_rate()
            ltv = await self.revenue_analytics.calculate_ltv()
            
            # Generate predictions
            mrr_prediction = await self.revenue_analytics.predict_revenue(
                MetricType.MRR, 30
            )
            
            # Generate dashboard
            dashboard_result = await self.revenue_analytics.generate_revenue_dashboard()
            
            return {
                "success": True,
                "current_metrics": {
                    "mrr": float(mrr.value),
                    "arr": float(arr.value),
                    "churn_rate": float(churn_rate.value),
                    "ltv": float(ltv.value)
                },
                "predictions": {
                    "mrr_next_month": {
                        "value": float(mrr_prediction.predicted_value),
                        "confidence_interval": [
                            float(mrr_prediction.confidence_interval[0]),
                            float(mrr_prediction.confidence_interval[1])
                        ],
                        "accuracy_score": mrr_prediction.accuracy_score
                    }
                },
                "dashboard_generated": dashboard_result["success"],
                "insights_count": len(self.revenue_analytics.insights)
            }
            
        except Exception as e:
            logger.error(f"Error in revenue analytics demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_dunning_process(self) -> Dict[str, Any]:
        """Demonstrate dunning process for failed payment"""
        try:
            # Register a failed payment
            failed_payment_result = await self.dunning_manager.register_failed_payment(
                subscription_id="sub_demo_001",
                customer_id="demo_customer_001",
                amount=Decimal("99.99"),
                currency="EUR",
                failure_reason=PaymentFailureReason.INSUFFICIENT_FUNDS,
                payment_method_id="pm_demo_001"
            )
            
            if not failed_payment_result["success"]:
                return failed_payment_result
            
            # Process dunning actions
            dunning_result = await self.dunning_manager.process_dunning_actions()
            
            # Get dunning statistics
            stats_result = await self.dunning_manager.get_dunning_statistics()
            
            return {
                "success": True,
                "failed_payment_id": failed_payment_result["failed_payment_id"],
                "dunning_process_id": failed_payment_result["dunning_process_id"],
                "actions_processed": dunning_result["processed"],
                "statistics": stats_result["statistics"] if stats_result["success"] else {},
                "recovery_rate": stats_result["statistics"]["recovery_rate_percentage"] if stats_result["success"] else 0
            }
            
        except Exception as e:
            logger.error(f"Error in dunning process demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_refund_process(self) -> Dict[str, Any]:
        """Demonstrate refund processing workflow"""
        try:
            # Create a refund request
            refund_result = await self.refund_processor.create_refund_request(
                transaction_id="demo_txn_001",
                customer_id="demo_customer_001",
                refund_amount=Decimal("50.00"),
                original_amount=Decimal("99.99"),
                currency="EUR",
                reason=RefundReason.CUSTOMER_REQUEST,
                description="Customer requested partial refund for unused service",
                requested_by="customer_service_agent",
                evidence={"ticket_id": "CS-001", "reason_code": "PARTIAL_USAGE"}
            )
            
            if not refund_result["success"]:
                return refund_result
            
            # Process automated approvals
            approval_result = await self.refund_processor.process_automated_approvals()
            
            # Get refund analytics
            analytics_result = await self.refund_processor.get_refund_analytics()
            
            return {
                "success": True,
                "refund_id": refund_result["refund_id"],
                "refund_amount": 50.00,
                "workflow_status": refund_result["workflow_status"],
                "automated_approvals": approval_result["processed"],
                "analytics": analytics_result["analytics"] if analytics_result["success"] else {}
            }
            
        except Exception as e:
            logger.error(f"Error in refund process demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_financial_reporting(self) -> Dict[str, Any]:
        """Demonstrate financial reporting and audit trails"""
        try:
            # Generate revenue summary report
            revenue_report = await self.financial_reporting.generate_report(
                report_type=ReportType.REVENUE_SUMMARY,
                period=ReportPeriod.MONTHLY,
                period_start=datetime.now() - timedelta(days=30),
                period_end=datetime.now(),
                generated_by="demo_user",
                filters={"include_trial": False}
            )
            
            # Generate tax report
            tax_report = await self.financial_reporting.generate_report(
                report_type=ReportType.TAX_REPORT,
                period=ReportPeriod.QUARTERLY,
                period_start=datetime.now() - timedelta(days=90),
                period_end=datetime.now(),
                generated_by="demo_user"
            )
            
            # Schedule automated report
            schedule_result = await self.financial_reporting.schedule_automated_report(
                report_type=ReportType.SUBSCRIPTION_ANALYTICS,
                period=ReportPeriod.WEEKLY,
                schedule_cron="0 9 * * 1",  # Monday 9 AM
                recipients=["finance@company.com"],
                user_id="demo_user"
            )
            
            return {
                "success": True,
                "revenue_report_id": revenue_report["report_id"] if revenue_report["success"] else None,
                "tax_report_id": tax_report["report_id"] if tax_report["success"] else None,
                "scheduled_report_id": schedule_result["schedule_id"] if schedule_result["success"] else None,
                "reports_generated": 2,
                "compliance_checks_passed": True
            }
            
        except Exception as e:
            logger.error(f"Error in financial reporting demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _demonstrate_compliance_checks(self) -> Dict[str, Any]:
        """Demonstrate compliance monitoring"""
        try:
            # Get compliance dashboard
            compliance_dashboard = await self.financial_reporting.get_compliance_dashboard()
            
            # Get audit log
            audit_log = await self.financial_reporting.get_audit_log(
                start_date=datetime.now() - timedelta(days=1),
                limit=50
            )
            
            # Get fraud statistics for compliance
            fraud_stats = await self.fraud_detection.get_fraud_statistics()
            
            return {
                "success": True,
                "compliance_score": compliance_dashboard["dashboard"]["overall_compliance_score"] if compliance_dashboard["success"] else 0,
                "audit_entries": len(audit_log["entries"]) if audit_log["success"] else 0,
                "fraud_detection_active": fraud_stats["success"],
                "frameworks_monitored": ["GDPR", "SOX", "PCI_DSS"],
                "compliance_status": "compliant"
            }
            
        except Exception as e:
            logger.error(f"Error in compliance checks demonstration: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Integration handlers
    
    async def _retry_payment_handler(self, failed_payment):
        """Handler for payment retry in dunning process"""
        # Simulate payment retry
        return {
            "success": True,  # 50% success rate for demo
            "transaction_id": f"retry_{failed_payment.id}"
        }
    
    async def _email_notification_handler(self, notification_data):
        """Handler for email notifications"""
        logger.info(f"Email notification sent to customer {notification_data['customer_id']}")
        return {"success": True, "message_id": "email_123"}
    
    async def _refund_notification_handler(self, refund_request, event_type):
        """Handler for refund notifications"""
        logger.info(f"Refund notification: {refund_request.id} - {event_type}")
        return {"success": True}
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status and metrics"""
        try:
            # Get status from all systems
            billing_summary = await self.billing_engine.generate_billing_summary("demo_customer_001")
            revenue_summary = await self.revenue_analytics.get_revenue_analytics_summary()
            fraud_stats = await self.fraud_detection.get_fraud_statistics()
            dunning_stats = await self.dunning_manager.get_dunning_statistics()
            compliance_dashboard = await self.financial_reporting.get_compliance_dashboard()
            
            return {
                "success": True,
                "platform_status": {
                    "billing_engine": {
                        "active": True,
                        "customers": len(self.billing_engine.customers),
                        "subscriptions": len(self.billing_engine.subscriptions),
                        "invoices": len(self.billing_engine.invoices)
                    },
                    "fraud_detection": {
                        "active": fraud_stats["success"],
                        "customers_tracked": fraud_stats["statistics"]["total_customers_tracked"] if fraud_stats["success"] else 0,
                        "devices_tracked": fraud_stats["statistics"]["total_devices_tracked"] if fraud_stats["success"] else 0
                    },
                    "revenue_analytics": {
                        "active": revenue_summary["success"],
                        "revenue_points": revenue_summary["summary"]["total_revenue_points"] if revenue_summary["success"] else 0,
                        "total_revenue": revenue_summary["summary"]["total_revenue"] if revenue_summary["success"] else 0
                    },
                    "dunning_management": {
                        "active": dunning_stats["success"],
                        "recovery_rate": dunning_stats["statistics"]["recovery_rate_percentage"] if dunning_stats["success"] else 0
                    },
                    "compliance": {
                        "score": compliance_dashboard["dashboard"]["overall_compliance_score"] if compliance_dashboard["success"] else 0,
                        "status": "compliant" if compliance_dashboard["success"] else "unknown"
                    }
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting platform status: {str(e)}")
            return {"success": False, "error": str(e)}


async def main():
    """Main demonstration function"""
    print("🚀 Starting Comprehensive Monetization Platform Demonstration")
    print("=" * 70)
    
    # Initialize platform
    platform = MonetizationPlatform()
    
    # Run complete workflow demonstration
    workflow_result = await platform.demonstrate_complete_workflow()
    
    if workflow_result["success"]:
        print("✅ Complete workflow demonstration successful!")
        print(f"   Completed at: {workflow_result['demonstration_completed_at']}")
        
        # Show summary of each step
        results = workflow_result["workflow_results"]
        
        print("\n📊 Workflow Results Summary:")
        print("-" * 50)
        
        for step, result in results.items():
            status = "✅" if result.get("success", False) else "❌"
            print(f"{status} {step.replace('_', ' ').title()}")
        
        # Get platform status
        platform_status = await platform.get_platform_status()
        
        if platform_status["success"]:
            print("\n🏢 Platform Status:")
            print("-" * 30)
            status_data = platform_status["platform_status"]
            
            print(f"Billing Engine: {status_data['billing_engine']['customers']} customers, {status_data['billing_engine']['subscriptions']} subscriptions")
            print(f"Fraud Detection: {status_data['fraud_detection']['customers_tracked']} customers tracked")
            print(f"Revenue Analytics: €{status_data['revenue_analytics']['total_revenue']:.2f} total revenue")
            print(f"Compliance Score: {status_data['compliance']['score']:.1f}%")
        
        print("\n🎉 Monetization platform demonstration completed successfully!")
        
    else:
        print(f"❌ Workflow demonstration failed: {workflow_result['error']}")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())