"""Monetization Module Index
===========================

Centralized access point for the complete monetization system providing
automated revenue sharing, real-time financial dashboard, and accounting compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging

# Import all monetization components
from . import (
    # Core engines
    AutomatedRevenueSharingEngine,
    RealTimeFinancialDashboard, 
    AccountingExportCompliance,
    
    # Global instances
    get_revenue_sharing_engine,
    get_financial_dashboard,
    get_accounting_export,
    
    # Convenience functions
    register_content_revenue_sharing,
    distribute_content_revenue,
    update_revenue_metric,
    update_expense_metric,
    track_transaction_volume,
    record_revenue_transaction,
    export_tax_report,
    
    # Types and enums
    TaxJurisdiction,
    ExportFormat
)

logger = logging.getLogger(__name__)


class MonetizationService:
    """
    Unified monetization service providing enterprise-grade financial management
    for content creators, influencers, and platform operators.
    """

    def __init__(self):
        self.revenue_engine = get_revenue_sharing_engine()
        self.dashboard = get_financial_dashboard()
        self.accounting = get_accounting_export()
        
        # Service metrics
        self.metrics = {
            "total_revenue_processed": Decimal('0.00'),
            "total_transactions": 0,
            "active_revenue_shares": 0,
            "compliance_score": 0.0
        }

    async def process_content_monetization(
        self,
        content_id: int,
        revenue_amount: Decimal,
        platform: str,
        user_id: int,
        currency: str = "EUR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete monetization workflow for content revenue.
        
        This is the main entry point for processing content monetization,
        handling revenue sharing, dashboard updates, and accounting compliance.
        """
        try:
            # 1. Distribute revenue automatically
            period_start = datetime.utcnow() - timedelta(hours=1)
            period_end = datetime.utcnow()
            
            distribution = await distribute_content_revenue(
                content_id=content_id,
                revenue_amount=revenue_amount,
                period_start=period_start,
                period_end=period_end
            )
            
            # 2. Update real-time dashboard
            await update_revenue_metric(revenue_amount, {
                'content_id': content_id,
                'platform': platform,
                'user_id': user_id,
                'currency': currency
            })
            
            # Update platform fees
            platform_fee = revenue_amount * Decimal('0.05')  # 5% platform fee
            await update_expense_metric(platform_fee, {
                'type': 'platform_fee',
                'content_id': content_id,
                'platform': platform
            })
            
            # Track transaction
            await track_transaction_volume(1, {
                'content_id': content_id,
                'platform': platform,
                'amount': float(revenue_amount)
            })
            
            # 3. Record accounting transaction
            transaction = await record_revenue_transaction(
                amount=revenue_amount,
                currency=currency,
                description=f"Content revenue from {platform}",
                user_id=user_id,
                content_id=content_id,
                metadata={
                    'platform': platform,
                    'distribution_id': distribution.distribution_id,
                    **(metadata or {})
                }
            )
            
            # 4. Update service metrics
            self.metrics["total_revenue_processed"] += revenue_amount
            self.metrics["total_transactions"] += 1
            
            logger.info(f"Processed monetization for content {content_id}: {revenue_amount} {currency}")
            
            return {
                "success": True,
                "distribution": {
                    "distribution_id": distribution.distribution_id,
                    "total_revenue": float(distribution.total_revenue),
                    "net_revenue": float(distribution.net_revenue),
                    "platform_fee": float(distribution.platform_fee),
                    "shares_count": len(distribution.shares),
                    "status": distribution.status.value
                },
                "accounting": {
                    "transaction_id": transaction.transaction_id,
                    "net_amount": float(transaction.net_amount),
                    "tax_amount": float(transaction.tax_amount),
                    "compliance_status": transaction.compliance_status
                },
                "dashboard_updated": True,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process content monetization: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_timestamp": datetime.utcnow().isoformat()
            }

    async def setup_creator_monetization(
        self,
        user_id: int,
        content_ids: List[int],
        revenue_sharing_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Setup monetization configuration for a creator.
        """
        try:
            created_shares = []
            
            for content_id in content_ids:
                shares = await register_content_revenue_sharing(
                    content_id=content_id,
                    sharing_rules=revenue_sharing_rules
                )
                created_shares.extend(shares)
                
                # Update metrics
                self.metrics["active_revenue_shares"] += len(shares)
            
            logger.info(f"Setup monetization for creator {user_id}: {len(created_shares)} revenue shares")
            
            return {
                "success": True,
                "creator_id": user_id,
                "content_count": len(content_ids),
                "revenue_shares_created": len(created_shares),
                "sharing_rules": [
                    {
                        "share_id": share.share_id,
                        "content_id": share.content_id,
                        "user_id": share.user_id,
                        "percentage": float(share.percentage),
                        "sharing_type": share.sharing_type.value
                    }
                    for share in created_shares
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to setup creator monetization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_financial_overview(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial overview combining all monetization data.
        """
        try:
            # Default to last 30 days if no dates provided
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get dashboard data
            dashboard_data = await self.dashboard.get_dashboard_data(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get revenue analytics
            revenue_analytics = await self.revenue_engine.get_revenue_analytics(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get user revenue summary if user specified
            user_summary = None
            if user_id:
                user_summary = await self.revenue_engine.get_user_revenue_summary(
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date
                )
            
            # Get compliance status
            compliance_status = await self.accounting.get_compliance_status()
            
            # Get financial summary
            financial_summary = await self.dashboard.get_financial_summary(
                start_date=start_date,
                end_date=end_date
            )
            
            overview = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "dashboard": dashboard_data,
                "revenue_analytics": revenue_analytics,
                "financial_summary": financial_summary,
                "compliance": compliance_status,
                "service_metrics": dict(self.metrics)
            }
            
            if user_summary:
                overview["user_summary"] = user_summary
            
            return overview
            
        except Exception as e:
            logger.error(f"Failed to get financial overview: {str(e)}")
            raise

    async def generate_financial_reports(
        self,
        jurisdiction: TaxJurisdiction = TaxJurisdiction.GERMANY,
        export_format: ExportFormat = ExportFormat.JSON,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive financial reports for compliance and analysis.
        """
        try:
            # Default to current quarter if no dates provided
            if not start_date:
                now = datetime.utcnow()
                start_date = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Generate tax report
            tax_report_result = await export_tax_report(
                jurisdiction=jurisdiction,
                start_date=start_date,
                end_date=end_date,
                export_format=export_format
            )
            
            # Export dashboard data
            dashboard_export = await self.dashboard.export_dashboard_data(
                export_format=export_format.value,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get revenue analytics for the period
            revenue_analytics = await self.revenue_engine.get_revenue_analytics(
                start_date=start_date,
                end_date=end_date
            )
            
            reports = {
                "generation_timestamp": datetime.utcnow().isoformat(),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "jurisdiction": jurisdiction.value,
                "export_format": export_format.value,
                "tax_report": tax_report_result,
                "dashboard_export": dashboard_export,
                "revenue_analytics": revenue_analytics,
                "compliance_summary": await self.accounting.get_compliance_status()
            }
            
            logger.info(f"Generated financial reports for period {start_date} to {end_date}")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to generate financial reports: {str(e)}")
            raise

    async def create_financial_alert(
        self,
        alert_name: str,
        metric_type: str,
        threshold_value: float,
        threshold_type: str = "above",
        notification_channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create financial monitoring alert.
        """
        try:
            from .realtime_financial_dashboard import DashboardMetricType
            
            # Convert string to enum
            metric_enum = DashboardMetricType(metric_type)
            
            alert = await self.dashboard.create_financial_alert(
                name=alert_name,
                metric_type=metric_enum,
                threshold_value=Decimal(str(threshold_value)),
                threshold_type=threshold_type,
                notification_channels=notification_channels or ["email"]
            )
            
            return {
                "success": True,
                "alert": {
                    "alert_id": alert.alert_id,
                    "name": alert.name,
                    "metric_type": alert.metric_type.value,
                    "threshold_value": float(alert.threshold_value),
                    "threshold_type": alert.threshold_type,
                    "notification_channels": alert.notification_channels,
                    "created_at": alert.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create financial alert: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_service_health(self) -> Dict[str, Any]:
        """
        Get monetization service health status.
        """
        try:
            compliance_status = await self.accounting.get_compliance_status()
            
            health = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": dict(self.metrics),
                "components": {
                    "revenue_sharing": {
                        "status": "operational",
                        "active_shares": self.metrics["active_revenue_shares"]
                    },
                    "dashboard": {
                        "status": "operational",
                        "active_widgets": len(self.dashboard.active_widgets)
                    },
                    "accounting": {
                        "status": "operational" if compliance_status["overview"]["compliance_score"] >= 95 else "degraded",
                        "compliance_score": compliance_status["overview"]["compliance_score"],
                        "total_transactions": compliance_status["overview"]["total_transactions"]
                    }
                }
            }
            
            # Determine overall health
            component_statuses = [comp["status"] for comp in health["components"].values()]
            if "degraded" in component_statuses:
                health["status"] = "degraded"
            elif any(status != "operational" for status in component_statuses):
                health["status"] = "unhealthy"
            
            return health
            
        except Exception as e:
            logger.error(f"Failed to get service health: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global monetization service instance
_monetization_service = None

def get_monetization_service() -> MonetizationService:
    """Get global monetization service instance"""
    global _monetization_service
    if _monetization_service is None:
        _monetization_service = MonetizationService()
    return _monetization_service


# Convenience functions for common operations
async def monetize_content(
    content_id: int,
    revenue_amount: float,
    platform: str,
    user_id: int,
    currency: str = "EUR"
) -> Dict[str, Any]:
    """Monetize content with automatic revenue sharing and accounting"""
    service = get_monetization_service()
    return await service.process_content_monetization(
        content_id=content_id,
        revenue_amount=Decimal(str(revenue_amount)),
        platform=platform,
        user_id=user_id,
        currency=currency
    )


async def setup_creator(
    user_id: int,
    content_ids: List[int],
    revenue_percentage: float = 70.0
) -> Dict[str, Any]:
    """Setup monetization for creator with default revenue sharing"""
    service = get_monetization_service()
    
    sharing_rules = [{
        "user_id": user_id,
        "type": "creator_royalty",
        "percentage": revenue_percentage,
        "currency": "EUR"
    }]
    
    return await service.setup_creator_monetization(
        user_id=user_id,
        content_ids=content_ids,
        revenue_sharing_rules=sharing_rules
    )


async def get_financial_dashboard() -> Dict[str, Any]:
    """Get comprehensive financial dashboard data"""
    service = get_monetization_service()
    return await service.get_financial_overview()


async def create_revenue_alert(
    threshold_amount: float,
    alert_name: str = "Revenue Alert"
) -> Dict[str, Any]:
    """Create revenue monitoring alert"""
    service = get_monetization_service()
    return await service.create_financial_alert(
        alert_name=alert_name,
        metric_type="revenue",
        threshold_value=threshold_amount,
        threshold_type="above"
    )


# Export main service class and convenience functions
__all__ = [
    "MonetizationService",
    "get_monetization_service",
    "monetize_content",
    "setup_creator",
    "get_financial_dashboard", 
    "create_revenue_alert"
]