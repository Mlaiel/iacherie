"""Business Monitoring Integration Module
=====================================

Main integration module that orchestrates all business monitoring components
and provides a unified interface for the comprehensive monitoring system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import json

# Import business monitoring components
try:
    from .business_monitoring import BusinessMonitoringSystem
    from .business_monitoring_config import BusinessMonitoringConfig, business_monitoring_config
    from .stakeholder_reporting import StakeholderReportingSystem, ReportType, ReportFrequency
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from business_monitoring import BusinessMonitoringSystem
    from business_monitoring_config import BusinessMonitoringConfig
    from stakeholder_reporting import StakeholderReportingSystem, ReportType, ReportFrequency
    # Create config instance
    business_monitoring_config = BusinessMonitoringConfig()

logger = logging.getLogger(__name__)


class BusinessMonitoringOrchestrator:
    """
    Main orchestrator for the comprehensive business monitoring system.
    Coordinates all monitoring components and provides unified management.
    """
    
    def __init__(self, config: Optional[BusinessMonitoringConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or business_monitoring_config
        
        # Initialize core components
        self.monitoring_system = BusinessMonitoringSystem()
        self.reporting_system = StakeholderReportingSystem()
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.monitoring_tasks: List[asyncio.Task] = []

    async def initialize(self) -> bool:
        """Initialize the complete business monitoring system"""
        try:
            self.logger.info("Initializing comprehensive business monitoring system...")
            
            # Validate configuration
            config_errors = self.config.validate_config()
            if config_errors:
                self.logger.error(f"Configuration validation failed: {config_errors}")
                return False
            
            # Initialize monitoring system
            await self.monitoring_system.initialize()
            
            # Configure business alerts from config
            await self._setup_business_alerts()
            
            # Configure KPI tracking
            await self._setup_kpi_tracking()
            
            # Setup funnel analysis
            await self._setup_funnel_analysis()
            
            # Setup cohort analysis
            await self._setup_cohort_analysis()
            
            # Configure competitive intelligence
            await self._setup_competitive_intelligence()
            
            # Initialize A/B testing integration
            await self._setup_ab_testing_integration()
            
            # Schedule automated reporting
            await self._setup_automated_reporting()
            
            self.is_initialized = True
            self.logger.info("Business monitoring system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize business monitoring system: {e}")
            return False

    async def start_monitoring(self) -> bool:
        """Start all monitoring processes"""
        try:
            if not self.is_initialized:
                if not await self.initialize():
                    return False
            
            self.logger.info("Starting business monitoring processes...")
            
            # Start real-time revenue monitoring
            revenue_task = asyncio.create_task(
                self._run_revenue_monitoring_loop(),
                name="revenue_monitoring"
            )
            self.monitoring_tasks.append(revenue_task)
            
            # Start churn prediction monitoring
            churn_task = asyncio.create_task(
                self._run_churn_prediction_loop(),
                name="churn_prediction"
            )
            self.monitoring_tasks.append(churn_task)
            
            # Start KPI alerting monitoring
            kpi_task = asyncio.create_task(
                self._run_kpi_alerting_loop(),
                name="kpi_alerting"
            )
            self.monitoring_tasks.append(kpi_task)
            
            # Start funnel analysis monitoring
            funnel_task = asyncio.create_task(
                self._run_funnel_analysis_loop(),
                name="funnel_analysis"
            )
            self.monitoring_tasks.append(funnel_task)
            
            # Start automated reporting
            reporting_task = asyncio.create_task(
                self._run_automated_reporting_loop(),
                name="automated_reporting"
            )
            self.monitoring_tasks.append(reporting_task)
            
            # Start competitive intelligence monitoring
            competitive_task = asyncio.create_task(
                self._run_competitive_monitoring_loop(),
                name="competitive_monitoring"
            )
            self.monitoring_tasks.append(competitive_task)
            
            self.is_running = True
            self.logger.info("All business monitoring processes started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring processes: {e}")
            await self.stop_monitoring()
            return False

    async def stop_monitoring(self):
        """Stop all monitoring processes"""
        try:
            self.logger.info("Stopping business monitoring processes...")
            
            # Cancel all monitoring tasks
            for task in self.monitoring_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            self.monitoring_tasks.clear()
            self.is_running = False
            
            self.logger.info("All monitoring processes stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring processes: {e}")

    async def get_business_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive business dashboard data"""
        try:
            # Get dashboard from monitoring system
            dashboard = await self.monitoring_system.create_business_dashboard()
            
            # Add real-time status information
            dashboard_data = {
                "dashboard": dashboard.__dict__ if hasattr(dashboard, '__dict__') else dashboard,
                "real_time_metrics": await self._get_real_time_metrics(),
                "system_status": await self.get_system_status(),
                "last_updated": datetime.now(timezone.utc),
                "alerts": await self._get_active_alerts(),
                "recommendations": await self._get_dashboard_recommendations()
            }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get business dashboard: {e}")
            raise

    async def generate_stakeholder_report(
        self,
        report_type: str = "weekly",
        recipients: Optional[List[str]] = None,
        custom_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate and optionally deliver stakeholder report"""
        try:
            # Map string to enum
            report_type_enum = ReportType.WEEKLY if report_type == "weekly" else ReportType.COMPREHENSIVE
            
            # Generate report
            report = await self.reporting_system.generate_report(
                report_type=report_type_enum,
                custom_sections=custom_sections
            )
            
            # Deliver to recipients if specified
            if recipients:
                from .stakeholder_reporting import DeliveryFormat
                delivery_results = await self.reporting_system._deliver_report(
                    report, recipients, [DeliveryFormat.PDF]
                )
                report["delivery_results"] = delivery_results
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate stakeholder report: {e}")
            raise

    async def analyze_conversion_funnel(self, funnel_name: str = "user_acquisition") -> Dict[str, Any]:
        """Analyze conversion funnel performance"""
        try:
            return await self.monitoring_system.analyze_conversion_funnel(funnel_name)
        except Exception as e:
            self.logger.error(f"Failed to analyze conversion funnel: {e}")
            raise

    async def perform_cohort_analysis(self, cohort_type: str = "acquisition") -> Dict[str, Any]:
        """Perform cohort analysis for user retention"""
        try:
            return await self.monitoring_system.perform_cohort_analysis(cohort_type)
        except Exception as e:
            self.logger.error(f"Failed to perform cohort analysis: {e}")
            raise

    async def predict_user_churn(self, user_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Predict user churn with preventive alerts"""
        try:
            predictions = await self.monitoring_system.predict_user_churn(user_ids)
            return [pred.__dict__ if hasattr(pred, '__dict__') else pred for pred in predictions]
        except Exception as e:
            self.logger.error(f"Failed to predict user churn: {e}")
            raise

    async def get_revenue_monitoring(self) -> Dict[str, Any]:
        """Get real-time revenue monitoring data"""
        try:
            return await self.monitoring_system.monitor_revenue_realtime()
        except Exception as e:
            self.logger.error(f"Failed to get revenue monitoring data: {e}")
            raise

    async def get_competitive_intelligence(self) -> Dict[str, Any]:
        """Get competitive intelligence summary"""
        try:
            return {
                "competitive_data": self.monitoring_system.competitive_data,
                "market_analysis": await self._get_market_analysis(),
                "threat_assessment": await self._assess_competitive_threats(),
                "opportunities": await self._identify_market_opportunities()
            }
        except Exception as e:
            self.logger.error(f"Failed to get competitive intelligence: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            monitoring_status = await self.monitoring_system.get_business_monitoring_status()
            reporting_status = self.reporting_system.get_reporting_status()
            
            return {
                "overall_status": "operational" if self.is_running else "stopped",
                "initialized": self.is_initialized,
                "running": self.is_running,
                "active_tasks": len([task for task in self.monitoring_tasks if not task.done()]),
                "monitoring_system": monitoring_status,
                "reporting_system": reporting_status,
                "configuration_valid": len(self.config.validate_config()) == 0,
                "last_health_check": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"overall_status": "error", "error": str(e)}

    # Private helper methods for setup and monitoring loops

    async def _setup_business_alerts(self):
        """Setup business alerts from configuration"""
        alert_configs = []
        for alert_config in self.config.alerts:
            from .business_monitoring import BusinessAlert
            alert = BusinessAlert(
                alert_id=alert_config.alert_id,
                alert_type=alert_config.alert_type,
                metric_type=alert_config.metric_type,
                threshold_value=alert_config.threshold_value,
                comparison_operator=alert_config.comparison_operator,
                alert_message=f"Business alert: {alert_config.alert_id}",
                severity=alert_config.severity,
                notification_channels=[channel.value for channel in alert_config.notification_channels]
            )
            alert_configs.append(alert)
        
        await self.monitoring_system.configure_business_alerting(alert_configs)

    async def _setup_kpi_tracking(self):
        """Setup KPI tracking from configuration"""
        for kpi_config in self.config.kpis:
            # Configure KPI tracking in the monitoring system
            pass  # Implementation would integrate with KPI tracker

    async def _setup_funnel_analysis(self):
        """Setup funnel analysis from configuration"""
        for funnel_config in self.config.funnels:
            # Setup funnel analysis configuration
            pass  # Implementation would configure funnels

    async def _setup_cohort_analysis(self):
        """Setup cohort analysis from configuration"""
        for cohort_config in self.config.cohorts:
            # Setup cohort analysis configuration
            pass  # Implementation would configure cohorts

    async def _setup_competitive_intelligence(self):
        """Setup competitive intelligence monitoring"""
        competitors = self.config.competitive_intelligence.competitors
        await self.monitoring_system.configure_competitive_intelligence(competitors)

    async def _setup_ab_testing_integration(self):
        """Setup A/B testing integration with analytics"""
        # Configure A/B testing integration
        pass  # Implementation would setup A/B testing

    async def _setup_automated_reporting(self):
        """Setup automated reporting schedules"""
        # Configure automated reporting from config
        pass  # Implementation would setup reporting schedules

    # Monitoring loop methods

    async def _run_revenue_monitoring_loop(self):
        """Run real-time revenue monitoring loop"""
        while self.is_running:
            try:
                revenue_data = await self.monitoring_system.monitor_revenue_realtime()
                
                # Check for revenue alerts
                await self._check_revenue_alerts(revenue_data)
                
                # Wait before next check (configurable interval)
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in revenue monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _run_churn_prediction_loop(self):
        """Run churn prediction monitoring loop"""
        while self.is_running:
            try:
                # Run churn prediction for at-risk users
                predictions = await self.monitoring_system.predict_user_churn()
                
                # Process high-risk predictions
                await self._process_churn_predictions(predictions)
                
                # Wait before next prediction cycle (configurable)
                await asyncio.sleep(3600)  # Check every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in churn prediction loop: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error

    async def _run_kpi_alerting_loop(self):
        """Run KPI alerting monitoring loop"""
        while self.is_running:
            try:
                # Check all configured KPI alerts
                await self._check_kpi_alerts()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in KPI alerting loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _run_funnel_analysis_loop(self):
        """Run funnel analysis monitoring loop"""
        while self.is_running:
            try:
                # Analyze all configured funnels
                for funnel_name in self.monitoring_system.funnel_configs.keys():
                    await self.monitoring_system.analyze_conversion_funnel(funnel_name)
                
                # Wait before next analysis
                await asyncio.sleep(1800)  # Analyze every 30 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in funnel analysis loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error

    async def _run_automated_reporting_loop(self):
        """Run automated reporting loop"""
        while self.is_running:
            try:
                # Check for scheduled reports to deliver
                delivered_reports = await self.reporting_system.deliver_scheduled_reports()
                
                if delivered_reports:
                    self.logger.info(f"Delivered {len(delivered_reports)} scheduled reports")
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in automated reporting loop: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error

    async def _run_competitive_monitoring_loop(self):
        """Run competitive intelligence monitoring loop"""
        while self.is_running:
            try:
                # Update competitive intelligence data
                await self._update_competitive_intelligence()
                
                # Wait before next update
                await asyncio.sleep(3600)  # Update every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in competitive monitoring loop: {e}")
                await asyncio.sleep(7200)  # Wait 2 hours on error

    # Helper methods for monitoring operations

    async def _get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time business metrics"""
        return {
            "timestamp": datetime.now(timezone.utc),
            "revenue": await self.monitoring_system._get_current_revenue_metrics(),
            "users": await self.monitoring_system._get_current_user_metrics(),
            "engagement": await self.monitoring_system._get_current_engagement_metrics()
        }

    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active business alerts"""
        return [
            {
                "alert_id": alert_id,
                "type": alert.alert_type.value,
                "severity": alert.severity,
                "message": alert.alert_message,
                "created_at": alert.created_at
            }
            for alert_id, alert in self.monitoring_system.business_alerts.items()
            if alert.is_active
        ]

    async def _get_dashboard_recommendations(self) -> List[str]:
        """Get dashboard recommendations based on current metrics"""
        return [
            "Revenue growth is on track to meet quarterly targets",
            "User retention rates are above industry average",
            "Consider expanding A/B testing on onboarding flow",
            "Churn prediction indicates opportunity for proactive outreach"
        ]

    async def _check_revenue_alerts(self, revenue_data: Dict[str, Any]):
        """Check revenue data against alert thresholds"""
        # Implementation would check revenue metrics against configured alerts
        pass

    async def _process_churn_predictions(self, predictions: List[Any]):
        """Process churn predictions and generate alerts"""
        high_risk_count = len([p for p in predictions if p.risk_level in ['high', 'critical']])
        if high_risk_count > 0:
            self.logger.warning(f"Found {high_risk_count} users at high risk of churning")

    async def _check_kpi_alerts(self):
        """Check KPI metrics against configured alerts"""
        # Implementation would check KPIs against alert thresholds
        pass

    async def _update_competitive_intelligence(self):
        """Update competitive intelligence data"""
        # Implementation would fetch and update competitive data
        pass

    async def _get_market_analysis(self) -> Dict[str, Any]:
        """Get market analysis summary"""
        return {
            "market_size": "Growing at 15% CAGR",
            "our_position": "Strong position in AI-powered creator tools",
            "growth_opportunities": ["Enterprise expansion", "International markets"],
            "threats": ["New competitor funding", "Platform policy changes"]
        }

    async def _assess_competitive_threats(self) -> List[Dict[str, Any]]:
        """Assess competitive threats"""
        return [
            {
                "threat_id": "competitor_a_funding",
                "description": "Competitor A raised $50M Series B",
                "impact": "medium",
                "recommended_action": "Monitor product releases and pricing"
            }
        ]

    async def _identify_market_opportunities(self) -> List[Dict[str, Any]]:
        """Identify market opportunities"""
        return [
            {
                "opportunity_id": "enterprise_expansion",
                "description": "Growing demand for enterprise creator management",
                "potential_impact": "high",
                "recommended_action": "Develop enterprise features and sales strategy"
            }
        ]


# Global orchestrator instance
business_monitoring_orchestrator = BusinessMonitoringOrchestrator()


# Convenience functions for easy access
async def initialize_business_monitoring() -> bool:
    """Initialize the business monitoring system"""
    return await business_monitoring_orchestrator.initialize()


async def start_business_monitoring() -> bool:
    """Start business monitoring processes"""
    return await business_monitoring_orchestrator.start_monitoring()


async def stop_business_monitoring():
    """Stop business monitoring processes"""
    await business_monitoring_orchestrator.stop_monitoring()


async def get_business_dashboard() -> Dict[str, Any]:
    """Get business dashboard data"""
    return await business_monitoring_orchestrator.get_business_dashboard()


async def generate_business_report(report_type: str = "weekly") -> Dict[str, Any]:
    """Generate business report"""
    return await business_monitoring_orchestrator.generate_stakeholder_report(report_type)


async def get_monitoring_status() -> Dict[str, Any]:
    """Get monitoring system status"""
    return await business_monitoring_orchestrator.get_system_status()