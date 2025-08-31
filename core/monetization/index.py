"""Monetization System Index
Central access point for all monetization components and services

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from . import (
    # Core systems
    PaymentProcessor, RevenueCalculator, PlatformConnector,
    MonetizationAnalytics, CommissionCalculator, WithdrawalManager,
    TaxCalculator, FinancialReporter,
    
    # Advanced systems
    PlatformRevenueAggregator, AdvancedLicensingEngine, PayoutEngine,
    PerformanceAnalyticsEngine, PricingEngine, PayoutOptimizer
)

from ...core.security.encryption import SecurityManager


class MonetizationSystemIndex:
    """
    Central index for all monetization system components
    Provides unified access and orchestration for monetization services
    """
    
    def __init__(
        self,
        security_manager: SecurityManager,
        config: Optional[Dict[str, Any]] = None
    ):
        self.security_manager = security_manager
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self._initialize_core_systems()
        
        # Initialize advanced systems
        self._initialize_advanced_systems()
        
        self.logger.info("Monetization system index initialized successfully")
    
    def _initialize_core_systems(self):
        """Initialize core monetization systems"""
        
        # Payment processing
        self.payment_processor = PaymentProcessor(
            security_manager=self.security_manager,
            config=self.config.get('payment', {})
        )
        
        # Revenue calculation
        self.revenue_calculator = RevenueCalculator()
        
        # Platform connectivity
        self.platform_connector = PlatformConnector(
            security_manager=self.security_manager
        )
        
        # Analytics
        self.analytics = MonetizationAnalytics()
        
        # Commission calculation
        self.commission_calculator = CommissionCalculator()
        
        # Withdrawal management
        self.withdrawal_manager = WithdrawalManager(
            payment_processor=self.payment_processor,
            security_manager=self.security_manager
        )
        
        # Tax calculation
        self.tax_calculator = TaxCalculator()
        
        # Financial reporting
        self.financial_reporter = FinancialReporter(
            analytics_engine=self.analytics,
            tax_calculator=self.tax_calculator
        )
    
    def _initialize_advanced_systems(self):
        """
Initialize advanced monetization systems"""
        
        # Platform revenue aggregation
        self.platform_aggregator = PlatformRevenueAggregator(
            security_manager=self.security_manager
        )
        
        # Pricing engine for licensing
        self.pricing_engine = PricingEngine(
            revenue_calculator=self.revenue_calculator
        )
        
        # Advanced licensing system
        self.licensing_engine = AdvancedLicensingEngine(
            pricing_engine=self.pricing_engine,
            security_manager=self.security_manager
        )
        
        # Payout optimization
        self.payout_optimizer = PayoutOptimizer()
        
        # Automated payout engine
        self.payout_engine = PayoutEngine(
            payment_processor=self.payment_processor,
            optimizer=self.payout_optimizer,
            security_manager=self.security_manager
        )
        
        # Performance analytics
        self.performance_analytics = PerformanceAnalyticsEngine()
    
    async def get_user_monetization_overview(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
Get comprehensive monetization overview for user"""
        
        try:
            # Get current balance
            balance = await self.withdrawal_manager.get_user_balance(user_id, session)
            
            # Get recent revenue summary
            revenue_summary = await self.platform_aggregator.get_total_revenue(
                user_id=user_id,
                start_date=None,  # This would be calculated for recent period
                end_date=None,
                session=session
            )
            
            # Get active licenses
            active_licenses = await self.licensing_engine.get_active_licenses(
                licensor_id=user_id,
                session=session
            )
            
            # Get pending payouts
            payout_history = await self.payout_engine.get_user_payout_history(
                user_id=user_id,
                limit=5,
                session=session
            )
            
            return {
                "user_id": user_id,
                "current_balance": float(balance),
                "revenue_summary": revenue_summary,
                "active_licenses_count": len(active_licenses),
                "recent_payouts": [payout.to_dict() for payout in payout_history],
                "system_status": "operational"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get monetization overview: {str(e)}")
            return {"error": str(e)}
    
    async def process_revenue_sync(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Process revenue synchronization for user"""
        
        try:
            from datetime import datetime, timedelta
            
            # Sync last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            revenue_data = await self.platform_aggregator.sync_all_platforms(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                session=session
            )
            
            return {
                "sync_status": "completed",
                "revenue_records_synced": len(revenue_data),
                "sync_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_revenue": sum(data.amount for data in revenue_data)
            }
            
        except Exception as e:
            self.logger.error(f"Revenue sync failed: {str(e)}")
            return {"error": str(e)}
    
    async def generate_license_offer(
        self,
        content_id: str,
        content_title: str,
        licensee_name: str,
        licensee_email: str,
        proposed_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate and evaluate license offer"""
        
        try:
            from .content_licensing_system import LicenseTerms, LicenseType, UsageRights
            from decimal import Decimal
            
            # Convert proposed terms
            terms = LicenseTerms(
                license_type=LicenseType(proposed_terms["license_type"]),
                usage_rights=[UsageRights(right) for right in proposed_terms["usage_rights"]],
                territory=proposed_terms["territory"],
                duration_months=proposed_terms["duration_months"],
                payment_amount=Decimal(str(proposed_terms["payment_amount"])),
                currency=proposed_terms.get("currency", "EUR")
            )
            
            # Create offer
            offer = await self.licensing_engine.create_license_offer(
                licensee_name=licensee_name,
                licensee_email=licensee_email,
                content_id=content_id,
                content_title=content_title,
                proposed_terms=terms
            )
            
            return {
                "offer_created": True,
                "offer_id": offer.offer_id,
                "offer_details": offer.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"License offer generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def request_payout(
        self,
        user_id: int,
        amount: float,
        currency: str,
        destination_config: Dict[str, Any],
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Request user payout"""
        
        try:
            from .automated_payout_engine import PayoutDestination, PayoutMethod
            from decimal import Decimal
            
            # Create payout destination
            destination = PayoutDestination(
                method=PayoutMethod(destination_config["method"]),
                account_id=destination_config["account_id"],
                account_name=destination_config["account_name"],
                routing_details=destination_config.get("routing_details", {}),
                currency=currency,
                is_verified=destination_config.get("is_verified", False)
            )
            
            # Create payout request
            payout_request = await self.payout_engine.create_payout_request(
                user_id=user_id,
                amount=Decimal(str(amount)),
                currency=currency,
                destination=destination,
                session=session
            )
            
            return {
                "payout_requested": True,
                "request_id": payout_request.request_id,
                "estimated_processing_fee": float(payout_request.processing_fee),
                "net_amount": float(payout_request.net_amount),
                "status": payout_request.status.value
            }
            
        except Exception as e:
            self.logger.error(f"Payout request failed: {str(e)}")
            return {"error": str(e)}
    
    async def get_performance_report(
        self,
        user_id: int,
        days: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate performance analytics report"""
        
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            report = await self.performance_analytics.generate_comprehensive_report(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                session=session
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Performance report generation failed: {str(e)}")
            return {"error": str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get monetization system health status"""
        
        health_status = {
            "overall_status": "healthy",
            "components": {
                "payment_processor": "operational",
                "revenue_calculator": "operational",
                "platform_connector": "operational",
                "analytics": "operational",
                "licensing_engine": "operational",
                "payout_engine": "operational",
                "performance_analytics": "operational"
            },
            "last_check": datetime.now().isoformat()
        }
        
        return health_status
    
    async def get_system_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get overall system statistics"""
        
        try:
            # This would calculate system-wide statistics
            # Implementation depends on your specific metrics needs
            
            return {
                "total_users": 0,  # Would be calculated from database
                "total_revenue_processed": 0,
                "total_payouts_processed": 0,
                "active_licenses": 0,
                "platforms_connected": 0,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system statistics: {str(e)}")
            return {"error": str(e)}


# Global monetization system instance
_monetization_system: Optional[MonetizationSystemIndex] = None


def get_monetization_system(
    security_manager: SecurityManager,
    config: Optional[Dict[str, Any]] = None
) -> MonetizationSystemIndex:
    """Get or create monetization system instance"""
    
    global _monetization_system
    
    if _monetization_system is None:
        _monetization_system = MonetizationSystemIndex(
            security_manager=security_manager,
            config=config
        )
    
    return _monetization_system


def initialize_monetization_system(
    security_manager: SecurityManager,
    config: Optional[Dict[str, Any]] = None
) -> MonetizationSystemIndex:
    """
Initialize monetization system with configuration"""
    
    global _monetization_system
    
    _monetization_system = MonetizationSystemIndex(
        security_manager=security_manager,
        config=config
    )
    
    return _monetization_system
