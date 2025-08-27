"""
Comprehensive Health Monitoring System
Master health checker coordinating all subsystem health monitoring

This module provides unified health monitoring by orchestrating:
- Core application and system resource monitoring
- Database and cache system health checks
- Machine learning and AI service monitoring
- Content protection service health verification
- Monetization and payment system checks
- External API integration monitoring
- Infrastructure component health validation
- Real-time health dashboards and alerting

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

from .core_health import CoreHealthChecker, HealthStatus, HealthCheckResult
from .database_health import DatabaseHealthChecker
from .ml_health import MLServiceHealthChecker
from .protection_health import ProtectionServiceHealthChecker
from .monetization_health import MonetizationHealthChecker
from .external_api_health import ExternalAPIHealthChecker
from .infrastructure_health import InfrastructureHealthChecker


@dataclass
class PlatformHealthSummary:
    """Complete platform health summary"""
    overall_status: str
    overall_health_percentage: float
    total_services: int
    healthy_services: int
    degraded_services: int
    unhealthy_services: int
    critical_services: int
    average_response_time_ms: float
    last_check_timestamp: str
    subsystem_summaries: Dict[str, Any]
    critical_issues: List[str]
    recommendations: List[str]


class ComprehensiveHealthChecker:
    """
    Master health monitoring system for IA Influencer Agent Platform
    
    Coordinates health checking across all platform subsystems and provides
    unified health reporting, alerting, and diagnostic capabilities.
    """

    def __init__(self, config: Dict[str, Any], app=None):
        """
        Initialize comprehensive health checker
        
        Args:
            config: Complete platform configuration
            app: FastAPI application instance (optional)
        """
        self.config = config
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        # Initialize subsystem health checkers
        self.core_checker = CoreHealthChecker(app, config) if app else None
        self.database_checker = DatabaseHealthChecker(config)
        self.ml_checker = MLServiceHealthChecker(config)
        self.protection_checker = ProtectionServiceHealthChecker(config)
        self.monetization_checker = MonetizationHealthChecker(config)
        self.external_api_checker = ExternalAPIHealthChecker(config)
        self.infrastructure_checker = InfrastructureHealthChecker(config)
        
        # Health check configuration
        self.health_config = config.get("health_checks", {})
        self.check_interval_seconds = self.health_config.get("check_interval_seconds", 300)  # 5 minutes
        self.alert_thresholds = self.health_config.get("alert_thresholds", {})
        
        # Health history and metrics
        self._health_history = []
        self._last_comprehensive_check = None
        self._consecutive_failures = {}

    async def perform_comprehensive_health_check(self) -> PlatformHealthSummary:
        """
        Perform comprehensive health check across all platform subsystems
        
        Returns:
            PlatformHealthSummary: Complete platform health status
        """
        start_time = time.time()
        self.logger.info("Starting comprehensive platform health check")
        
        try:
            # Execute all subsystem health checks concurrently
            check_tasks = []
            
            if self.core_checker:
                check_tasks.append(("core", self.core_checker.perform_comprehensive_check()))
            
            check_tasks.extend([
                ("database", self.database_checker.perform_comprehensive_check()),
                ("ml_services", self.ml_checker.perform_comprehensive_check()),
                ("protection", self.protection_checker.perform_comprehensive_check()),
                ("monetization", self.monetization_checker.perform_comprehensive_check()),
                ("external_apis", self.external_api_checker.perform_comprehensive_check()),
                ("infrastructure", self.infrastructure_checker.perform_comprehensive_check())
            ])
            
            # Execute all checks concurrently
            subsystem_results = {}
            
            for subsystem_name, check_coro in check_tasks:
                try:
                    results = await check_coro
                    subsystem_results[subsystem_name] = results
                except Exception as e:
                    self.logger.error(f"Subsystem {subsystem_name} health check failed: {str(e)}")
                    subsystem_results[subsystem_name] = [HealthCheckResult(
                        service=f"{subsystem_name}_error",
                        status=HealthStatus.CRITICAL,
                        response_time_ms=0.0,
                        timestamp=datetime.utcnow(),
                        details={},
                        error_message=str(e)
                    )]
            
            # Aggregate results and calculate overall health
            all_results = []
            subsystem_summaries = {}
            
            for subsystem_name, results in subsystem_results.items():
                all_results.extend(results)
                
                # Calculate subsystem summary
                subsystem_summaries[subsystem_name] = self._calculate_subsystem_summary(results)
            
            # Calculate overall platform health metrics
            platform_summary = self._calculate_platform_summary(all_results, subsystem_summaries)
            
            # Store health check result
            self._last_comprehensive_check = platform_summary
            self._update_health_history(platform_summary)
            
            # Log health check completion
            total_time = (time.time() - start_time) * 1000
            self.logger.info(
                f"Comprehensive health check completed in {total_time:.1f}ms. "
                f"Overall status: {platform_summary.overall_status}, "
                f"Health: {platform_summary.overall_health_percentage:.1f}%"
            )
            
            return platform_summary
            
        except Exception as e:
            self.logger.error(f"Comprehensive health check failed: {str(e)}")
            
            # Return critical status summary
            return PlatformHealthSummary(
                overall_status=HealthStatus.CRITICAL.value,
                overall_health_percentage=0.0,
                total_services=0,
                healthy_services=0,
                degraded_services=0,
                unhealthy_services=0,
                critical_services=1,
                average_response_time_ms=0.0,
                last_check_timestamp=datetime.utcnow().isoformat(),
                subsystem_summaries={},
                critical_issues=[f"Health check system failure: {str(e)}"],
                recommendations=["Investigate health monitoring system", "Check system resources", "Review logs"]
            )

    def _calculate_subsystem_summary(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Calculate health summary for a specific subsystem"""
        if not results:
            return {
                "status": HealthStatus.CRITICAL.value,
                "health_percentage": 0.0,
                "total_services": 0,
                "healthy_services": 0,
                "average_response_time_ms": 0.0,
                "issues": ["No health check results available"]
            }
        
        # Count services by status
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0
        }
        
        total_response_time = 0.0
        issues = []
        
        for result in results:
            status_counts[result.status] += 1
            total_response_time += result.response_time_ms
            
            if result.error_message:
                issues.append(f"{result.service}: {result.error_message}")
        
        # Calculate overall subsystem status
        if status_counts[HealthStatus.CRITICAL] > 0:
            subsystem_status = HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            subsystem_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            subsystem_status = HealthStatus.DEGRADED
        else:
            subsystem_status = HealthStatus.HEALTHY
        
        # Calculate health percentage
        total_services = len(results)
        healthy_services = status_counts[HealthStatus.HEALTHY]
        health_percentage = (healthy_services / total_services) * 100
        
        # Calculate average response time
        avg_response_time = total_response_time / total_services if total_services > 0 else 0.0
        
        return {
            "status": subsystem_status.value,
            "health_percentage": round(health_percentage, 2),
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": status_counts[HealthStatus.DEGRADED],
            "unhealthy_services": status_counts[HealthStatus.UNHEALTHY],
            "critical_services": status_counts[HealthStatus.CRITICAL],
            "average_response_time_ms": round(avg_response_time, 2),
            "issues": issues[:5]  # Limit to top 5 issues
        }

    def _calculate_platform_summary(self, all_results: List[HealthCheckResult], 
                                   subsystem_summaries: Dict[str, Any]) -> PlatformHealthSummary:
        """Calculate overall platform health summary"""
        
        # Aggregate all service counts
        total_services = len(all_results)
        
        status_counts = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 0,
            HealthStatus.UNHEALTHY: 0,
            HealthStatus.CRITICAL: 0
        }
        
        total_response_time = 0.0
        critical_issues = []
        
        for result in all_results:
            status_counts[result.status] += 1
            total_response_time += result.response_time_ms
            
            if result.status == HealthStatus.CRITICAL and result.error_message:
                critical_issues.append(f"{result.service}: {result.error_message}")
        
        # Calculate overall platform status
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate overall health percentage
        healthy_services = status_counts[HealthStatus.HEALTHY]
        overall_health_percentage = (healthy_services / total_services) * 100 if total_services > 0 else 0.0
        
        # Calculate average response time
        avg_response_time = total_response_time / total_services if total_services > 0 else 0.0
        
        # Generate recommendations based on health status
        recommendations = self._generate_recommendations(overall_status, subsystem_summaries, status_counts)
        
        return PlatformHealthSummary(
            overall_status=overall_status.value,
            overall_health_percentage=round(overall_health_percentage, 2),
            total_services=total_services,
            healthy_services=status_counts[HealthStatus.HEALTHY],
            degraded_services=status_counts[HealthStatus.DEGRADED],
            unhealthy_services=status_counts[HealthStatus.UNHEALTHY],
            critical_services=status_counts[HealthStatus.CRITICAL],
            average_response_time_ms=round(avg_response_time, 2),
            last_check_timestamp=datetime.utcnow().isoformat(),
            subsystem_summaries=subsystem_summaries,
            critical_issues=critical_issues[:10],  # Limit to top 10 critical issues
            recommendations=recommendations
        )

    def _generate_recommendations(self, overall_status: HealthStatus, 
                                subsystem_summaries: Dict[str, Any],
                                status_counts: Dict[HealthStatus, int]) -> List[str]:
        """Generate actionable recommendations based on health status"""
        recommendations = []
        
        # Critical status recommendations
        if overall_status == HealthStatus.CRITICAL:
            recommendations.append("URGENT: Platform has critical issues requiring immediate attention")
            recommendations.append("Check system logs and error messages for root cause analysis")
            recommendations.append("Consider activating disaster recovery procedures if necessary")
        
        # Database-specific recommendations
        if "database" in subsystem_summaries:
            db_summary = subsystem_summaries["database"]
            if db_summary["status"] in [HealthStatus.UNHEALTHY.value, HealthStatus.CRITICAL.value]:
                recommendations.append("Database issues detected - check connectivity and performance")
                recommendations.append("Review database connection pools and query performance")
        
        # ML services recommendations
        if "ml_services" in subsystem_summaries:
            ml_summary = subsystem_summaries["ml_services"]
            if ml_summary["status"] in [HealthStatus.UNHEALTHY.value, HealthStatus.CRITICAL.value]:
                recommendations.append("ML/AI services experiencing issues - check GPU resources and model availability")
                recommendations.append("Verify ML model endpoints and vector database connectivity")
        
        # Infrastructure recommendations
        if "infrastructure" in subsystem_summaries:
            infra_summary = subsystem_summaries["infrastructure"]
            if infra_summary["status"] in [HealthStatus.UNHEALTHY.value, HealthStatus.CRITICAL.value]:
                recommendations.append("Infrastructure issues detected - check Kubernetes/Docker status")
                recommendations.append("Verify storage systems and SSL certificate validity")
        
        # Performance recommendations
        if status_counts[HealthStatus.DEGRADED] > 0:
            recommendations.append("Performance degradation detected - consider scaling resources")
            recommendations.append("Review response time metrics and optimize slow services")
        
        # External API recommendations
        if "external_apis" in subsystem_summaries:
            api_summary = subsystem_summaries["external_apis"]
            if api_summary["status"] in [HealthStatus.DEGRADED.value, HealthStatus.UNHEALTHY.value]:
                recommendations.append("External API issues - check rate limits and authentication")
                recommendations.append("Review API credentials and endpoint availability")
        
        # General recommendations
        if overall_status != HealthStatus.HEALTHY:
            recommendations.append("Enable additional monitoring and alerting for affected services")
            recommendations.append("Consider implementing circuit breakers for failing services")
        
        return recommendations[:8]  # Limit to top 8 recommendations

    def _update_health_history(self, summary: PlatformHealthSummary):
        """Update health check history for trend analysis"""
        history_entry = {
            "timestamp": summary.last_check_timestamp,
            "overall_status": summary.overall_status,
            "health_percentage": summary.overall_health_percentage,
            "total_services": summary.total_services,
            "healthy_services": summary.healthy_services,
            "critical_services": summary.critical_services
        }
        
        self._health_history.append(history_entry)
        
        # Keep only last 24 hours of history (assuming 5-minute intervals)
        max_entries = (24 * 60) // self.check_interval_seconds * 60  # 24 hours worth
        if len(self._health_history) > max_entries:
            self._health_history = self._health_history[-max_entries:]

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status without performing new checks
        
        Returns:
            Dict[str, Any]: Current health status and summary
        """
        if self._last_comprehensive_check is None:
            return {
                "status": "no_data",
                "message": "No health check data available. Run comprehensive check first.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return asdict(self._last_comprehensive_check)

    async def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get health trends and historical data
        
        Args:
            hours: Number of hours of history to return
        
        Returns:
            Dict[str, Any]: Health trends and metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter history for requested time period
        filtered_history = [
            entry for entry in self._health_history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
        ]
        
        if not filtered_history:
            return {
                "status": "no_data",
                "message": f"No health data available for the last {hours} hours",
                "requested_hours": hours
            }
        
        # Calculate trend metrics
        health_percentages = [entry["health_percentage"] for entry in filtered_history]
        
        return {
            "period_hours": hours,
            "data_points": len(filtered_history),
            "current_health_percentage": health_percentages[-1] if health_percentages else 0,
            "average_health_percentage": sum(health_percentages) / len(health_percentages),
            "min_health_percentage": min(health_percentages),
            "max_health_percentage": max(health_percentages),
            "health_trend": "improving" if len(health_percentages) > 1 and health_percentages[-1] > health_percentages[0] else "declining",
            "critical_incidents": len([entry for entry in filtered_history if entry["critical_services"] > 0]),
            "uptime_percentage": len([entry for entry in filtered_history if entry["overall_status"] == "healthy"]) / len(filtered_history) * 100,
            "history": filtered_history,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_subsystem_health(self, subsystem: str) -> Dict[str, Any]:
        """
        Get detailed health information for a specific subsystem
        
        Args:
            subsystem: Name of subsystem (core, database, ml_services, etc.)
        
        Returns:
            Dict[str, Any]: Detailed subsystem health information
        """
        checker_map = {
            "core": self.core_checker,
            "database": self.database_checker,
            "ml_services": self.ml_checker,
            "protection": self.protection_checker,
            "monetization": self.monetization_checker,
            "external_apis": self.external_api_checker,
            "infrastructure": self.infrastructure_checker
        }
        
        checker = checker_map.get(subsystem)
        
        if not checker:
            return {
                "error": f"Unknown subsystem: {subsystem}",
                "available_subsystems": list(checker_map.keys())
            }
        
        try:
            # Perform subsystem-specific health check
            results = await checker.perform_comprehensive_check()
            summary = self._calculate_subsystem_summary(results)
            
            return {
                "subsystem": subsystem,
                "summary": summary,
                "detailed_results": [asdict(result) for result in results],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Subsystem {subsystem} health check failed: {str(e)}")
            return {
                "subsystem": subsystem,
                "error": str(e),
                "status": "critical",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_service_readiness(self) -> Dict[str, Any]:
        """
        Perform quick readiness check for essential services
        
        Returns:
            Dict[str, Any]: Service readiness status
        """
        start_time = time.time()
        
        essential_checks = []
        
        # Quick database connectivity check
        try:
            db_result = await self.database_checker.check_postgresql_health()
            essential_checks.append(("database", db_result.status))
        except:
            essential_checks.append(("database", HealthStatus.CRITICAL))
        
        # Quick Redis check
        try:
            redis_result = await self.database_checker.check_redis_health()
            essential_checks.append(("cache", redis_result.status))
        except:
            essential_checks.append(("cache", HealthStatus.CRITICAL))
        
        # Calculate readiness
        critical_services = [name for name, status in essential_checks if status == HealthStatus.CRITICAL]
        
        if critical_services:
            readiness_status = "not_ready"
            message = f"Critical services unavailable: {', '.join(critical_services)}"
        else:
            readiness_status = "ready"
            message = "All essential services are available"
        
        return {
            "readiness_status": readiness_status,
            "message": message,
            "essential_services": dict(essential_checks),
            "check_duration_ms": (time.time() - start_time) * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def cleanup_resources(self):
        """Clean up health checker resources"""
        try:
            await self.database_checker.cleanup_connections()
            self.logger.info("Health checker resources cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up health checker resources: {str(e)}")
