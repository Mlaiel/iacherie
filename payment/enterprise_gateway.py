"""💳 Enterprise Payment Gateway Orchestrator
===========================================

Master orchestrator that integrates all payment gateway components into
a unified enterprise-grade payment processing system for the Ainflue
AI creator platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

# Core components
from .multi_provider_gateway import MultiProviderPaymentGateway, PaymentRequest, PaymentType, PaymentProvider
from .core.configuration_manager import PaymentGatewayConfigurationManager
from .core.router_engine import PaymentRouterEngine, RoutingCriteria
from .core.health_monitor import GatewayHealthMonitor
from .core.transaction_logger import PaymentTransactionLogger, TransactionEvent, LogLevel
from .core.integration_manager import ProviderIntegrationManager

# Security components
from .security.fraud_detection_engine import FraudDetectionEngine
from .security.pci_compliance_manager import PCIComplianceManager

# Revenue components
from .revenue.revenue_split_calculator import RevenueSplitCalculator, RevenueCategory
from .revenue.creator_revenue_manager import CreatorRevenueManager

# Analytics components
from .analytics.gateway_analytics import PaymentGatewayAnalytics

logger = logging.getLogger(__name__)


@dataclass
class GatewayStatus:
    """Overall gateway status"""
    is_healthy: bool
    active_providers: List[str]
    total_transactions_24h: int
    success_rate_24h: float
    fraud_rate_24h: float
    last_updated: datetime


class EnterprisePaymentGateway:
    """
    Master enterprise payment gateway orchestrator that integrates all
    components for complete payment processing, security, and analytics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize enterprise payment gateway"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.multi_provider_gateway = MultiProviderPaymentGateway(config)
        self.configuration_manager = PaymentGatewayConfigurationManager(config)
        self.router_engine = PaymentRouterEngine(config)
        self.health_monitor = GatewayHealthMonitor(config)
        self.transaction_logger = PaymentTransactionLogger(config)
        self.integration_manager = ProviderIntegrationManager(config)
        
        # Security components
        self.fraud_detection = FraudDetectionEngine(config)
        self.pci_compliance = PCIComplianceManager(config)
        
        # Revenue components
        self.revenue_calculator = RevenueSplitCalculator(config)
        self.creator_revenue_manager = CreatorRevenueManager(config)
        
        # Analytics components
        self.analytics_engine = PaymentGatewayAnalytics(config)
        
        # Gateway state
        self.is_initialized = False
        self.gateway_status = GatewayStatus(
            is_healthy=False,
            active_providers=[],
            total_transactions_24h=0,
            success_rate_24h=0.0,
            fraud_rate_24h=0.0,
            last_updated=datetime.now()
        )
    
    async def initialize(self):
        """Initialize all gateway components"""
        try:
            self.logger.info("Initializing Enterprise Payment Gateway...")
            
            # Initialize components in dependency order
            await self.configuration_manager.initialize()
            await self.integration_manager.initialize()
            await self.transaction_logger.initialize()
            await self.health_monitor.initialize()
            await self.router_engine.initialize()
            await self.fraud_detection.initialize()
            await self.pci_compliance.initialize()
            await self.revenue_calculator.initialize()
            await self.creator_revenue_manager.initialize()
            await self.analytics_engine.initialize()
            
            # Initialize multi-provider gateway last
            await self._initialize_providers()
            
            self.is_initialized = True
            await self._update_gateway_status()
            
            self.logger.info("Enterprise Payment Gateway initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Enterprise Payment Gateway: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown all gateway components"""
        try:
            self.logger.info("Shutting down Enterprise Payment Gateway...")
            
            # Shutdown in reverse order
            await self.analytics_engine.shutdown()
            await self.creator_revenue_manager.shutdown()
            await self.pci_compliance.shutdown()
            await self.fraud_detection.shutdown()
            await self.health_monitor.shutdown()
            await self.transaction_logger.shutdown()
            await self.integration_manager.shutdown()
            await self.configuration_manager.shutdown()
            
            self.is_initialized = False
            
            self.logger.info("Enterprise Payment Gateway shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during gateway shutdown: {e}")
    
    async def process_creator_payment(self, creator_id: str, buyer_id: str, 
                                    content_id: str, amount: Decimal, 
                                    currency: str, payment_method: str = "stripe",
                                    **kwargs) -> Dict[str, Any]:
        """
        Process creator content payment with full enterprise features:
        - Intelligent routing
        - Fraud detection
        - Revenue split calculation
        - Compliance logging
        """
        try:
            transaction_id = f"creator_payment_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.logger.info(f"Processing creator payment: {transaction_id}")
            
            # Log transaction start
            await self.transaction_logger.log_transaction_event(
                transaction_id=transaction_id,
                event_type=TransactionEvent.CREATED,
                provider_name="multi_provider",
                message=f"Creator payment initiated: {amount} {currency}",
                data={
                    "creator_id": creator_id,
                    "buyer_id": buyer_id,
                    "content_id": content_id,
                    "amount": float(amount),
                    "currency": currency,
                    "payment_method": payment_method
                },
                level=LogLevel.INFO,
                user_id=buyer_id
            )
            
            # 1. Fraud Detection
            fraud_assessment = await self.fraud_detection.assess_transaction({
                'transaction_id': transaction_id,
                'user_id': buyer_id,
                'amount': float(amount),
                'currency': currency,
                'timestamp': datetime.now().isoformat(),
                'merchant_id': creator_id,
                'payment_method': payment_method,
                'country_code': kwargs.get('country_code', 'US'),
                'ip_address': kwargs.get('ip_address', ''),
                'device_fingerprint': kwargs.get('device_fingerprint', ''),
                'user_agent': kwargs.get('user_agent', '')
            })
            
            # Check fraud assessment
            if fraud_assessment.recommended_action.value in ['block', 'challenge']:
                await self.transaction_logger.log_transaction_event(
                    transaction_id=transaction_id,
                    event_type=TransactionEvent.FAILED,
                    provider_name="fraud_detection",
                    message=f"Transaction blocked by fraud detection: {fraud_assessment.explanation}",
                    data={"fraud_assessment": fraud_assessment.__dict__},
                    level=LogLevel.WARNING
                )
                return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': 'Transaction blocked for security reasons',
                    'fraud_assessment': fraud_assessment.__dict__
                }
            
            # 2. Intelligent Payment Routing
            routing_criteria = RoutingCriteria(
                amount=amount,
                currency=currency,
                source_country=kwargs.get('country_code', 'US'),
                user_id=buyer_id,
                merchant_id=creator_id,
                payment_method=payment_method
            )
            
            # Get available providers
            active_providers = await self.configuration_manager.get_active_providers()
            available_provider_names = [p.provider_name for p in active_providers]
            
            routing_decision = await self.router_engine.route_payment(
                routing_criteria, available_provider_names
            )
            
            await self.transaction_logger.log_transaction_event(
                transaction_id=transaction_id,
                event_type=TransactionEvent.ROUTED,
                provider_name=routing_decision.selected_provider,
                message=f"Payment routed to {routing_decision.selected_provider}: {routing_decision.reasoning}",
                data={"routing_decision": routing_decision.__dict__},
                level=LogLevel.INFO
            )
            
            # 3. Process Payment
            payment_request = PaymentRequest(
                amount=amount,
                currency=currency,
                payment_type=PaymentType.MARKETPLACE_SPLIT,
                provider=PaymentProvider(routing_decision.selected_provider),
                sender_id=buyer_id,
                recipient_id=creator_id,
                description=f"Content purchase: {content_id}",
                metadata={
                    "content_id": content_id,
                    "creator_id": creator_id,
                    "fraud_score": fraud_assessment.risk_score,
                    "routing_score": routing_decision.routing_score
                }
            )
            
            payment_response = await self.multi_provider_gateway.process_payment(payment_request)
            
            await self.transaction_logger.log_transaction_event(
                transaction_id=transaction_id,
                event_type=TransactionEvent.PROCESSING,
                provider_name=routing_decision.selected_provider,
                message=f"Payment submitted to provider",
                data={"payment_response": payment_response.__dict__},
                level=LogLevel.INFO
            )
            
            # 4. Revenue Split Calculation and Creator Payment
            if payment_response.status.value == 'completed':
                creator_payment_result = await self.creator_revenue_manager.process_content_purchase(
                    content_id=content_id,
                    buyer_id=buyer_id,
                    amount=amount,
                    currency=currency,
                    payment_method=routing_decision.selected_provider
                )
                
                await self.transaction_logger.log_transaction_event(
                    transaction_id=transaction_id,
                    event_type=TransactionEvent.COMPLETED,
                    provider_name=routing_decision.selected_provider,
                    message=f"Creator payment processed successfully",
                    data={"creator_payment": creator_payment_result},
                    level=LogLevel.INFO
                )
                
                # Record analytics
                await self.analytics_engine.record_metric(
                    metric_type="transaction_volume",
                    value=float(amount),
                    labels={
                        "provider": routing_decision.selected_provider,
                        "creator_id": creator_id,
                        "currency": currency
                    }
                )
                
                await self.analytics_engine.record_metric(
                    metric_type="success_rate",
                    value=1.0,
                    labels={"provider": routing_decision.selected_provider}
                )
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'payment_provider': routing_decision.selected_provider,
                    'amount_charged': float(amount),
                    'creator_earnings': creator_payment_result.get('creator_earnings', 0),
                    'platform_fees': creator_payment_result.get('platform_fees', 0),
                    'fraud_score': fraud_assessment.risk_score,
                    'routing_score': routing_decision.routing_score
                }
            else:
                await self.transaction_logger.log_transaction_event(
                    transaction_id=transaction_id,
                    event_type=TransactionEvent.FAILED,
                    provider_name=routing_decision.selected_provider,
                    message=f"Payment failed: {payment_response.status.value}",
                    data={"payment_response": payment_response.__dict__},
                    level=LogLevel.ERROR
                )
                
                await self.analytics_engine.record_metric(
                    metric_type="success_rate",
                    value=0.0,
                    labels={"provider": routing_decision.selected_provider}
                )
                
                return {
                    'success': False,
                    'transaction_id': transaction_id,
                    'error': f"Payment failed: {payment_response.status.value}",
                    'provider': routing_decision.selected_provider
                }
            
        except Exception as e:
            self.logger.error(f"Creator payment processing failed: {e}")
            
            await self.transaction_logger.log_transaction_event(
                transaction_id=transaction_id,
                event_type=TransactionEvent.FAILED,
                provider_name="system",
                message=f"System error during payment processing: {str(e)}",
                data={"error": str(e)},
                level=LogLevel.CRITICAL
            )
            
            return {
                'success': False,
                'transaction_id': transaction_id,
                'error': f"System error: {str(e)}"
            }
    
    async def get_gateway_health(self) -> Dict[str, Any]:
        """Get comprehensive gateway health status"""
        try:
            # Get health from all components
            provider_health = await self.health_monitor.get_all_health_status()
            analytics_dashboard = await self.analytics_engine.get_real_time_dashboard()
            
            # Get compliance status
            compliance_assessment = await self.pci_compliance.run_compliance_assessment()
            
            # Update gateway status
            await self._update_gateway_status()
            
            return {
                'gateway_status': self.gateway_status.__dict__,
                'provider_health': {name: status.__dict__ for name, status in provider_health.items()},
                'analytics_dashboard': analytics_dashboard.__dict__,
                'compliance_score': compliance_assessment.get('overall_score', 0),
                'fraud_detection_stats': await self.fraud_detection.get_fraud_statistics(),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get gateway health: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def generate_comprehensive_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive enterprise report"""
        try:
            # Analytics report
            analytics_report = await self.analytics_engine.generate_analytics_report(
                report_type="comprehensive",
                period_days=days
            )
            
            # PCI compliance report
            pci_report = await self.pci_compliance.generate_pci_report()
            
            # Fraud statistics
            fraud_stats = await self.fraud_detection.get_fraud_statistics()
            
            # Creator revenue analytics
            # Get sample creator for demo
            creator_analytics = None
            if hasattr(self.creator_revenue_manager, 'creator_profiles') and self.creator_revenue_manager.creator_profiles:
                sample_creator_id = next(iter(self.creator_revenue_manager.creator_profiles.keys()))
                creator_analytics = await self.creator_revenue_manager.generate_revenue_analytics(
                    sample_creator_id, days
                )
            
            return {
                'report_id': f"enterprise_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'analytics_report': analytics_report.__dict__,
                'pci_compliance_report': pci_report.__dict__,
                'fraud_statistics': fraud_stats,
                'creator_analytics': creator_analytics.__dict__ if creator_analytics else None,
                'gateway_health': await self.get_gateway_health()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive report: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _initialize_providers(self):
        """Initialize payment providers"""
        # Get provider configurations
        active_providers = await self.configuration_manager.get_active_providers()
        
        for provider_config in active_providers:
            provider_name = provider_config.provider_name
            
            # Get provider credentials
            credentials = await self.configuration_manager.get_provider_credentials(provider_name)
            
            if credentials:
                self.logger.info(f"Initializing provider: {provider_name}")
                # Provider initialization would happen here
                self.gateway_status.active_providers.append(provider_name)
    
    async def _update_gateway_status(self):
        """Update overall gateway status"""
        try:
            # Get health from all providers
            provider_health = await self.health_monitor.get_all_health_status()
            
            # Check if gateway is healthy
            is_healthy = True
            if provider_health:
                unhealthy_providers = [
                    name for name, status in provider_health.items()
                    if status.overall_status.value != 'healthy'
                ]
                is_healthy = len(unhealthy_providers) == 0
            
            # Get recent analytics
            dashboard_data = await self.analytics_engine.get_real_time_dashboard()
            
            self.gateway_status = GatewayStatus(
                is_healthy=is_healthy,
                active_providers=self.gateway_status.active_providers,
                total_transactions_24h=dashboard_data.today_volume if dashboard_data else 0,
                success_rate_24h=dashboard_data.today_success_rate if dashboard_data else 0.0,
                fraud_rate_24h=0.1,  # Would be calculated from fraud stats
                last_updated=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to update gateway status: {e}")


# Export main class
__all__ = ["EnterprisePaymentGateway", "GatewayStatus"]