"""📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION - Industrialization Success Metrics
===========================================================================

Complete implementation of industrialization success metrics for the Ainflue platform
matching the exact specifications from the problem statement.

🎯 KPIs TECHNIQUES & 💼 KPIs BUSINESS

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict
import statistics
import time

from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry

logger = logging.getLogger(__name__)


class KPIType(Enum):
    """KPI types for industrialization success metrics"""
    TECHNICAL = "technical"
    BUSINESS = "business"


@dataclass
class IndustrializationKPI:
    """Individual industrialization KPI definition"""
    name: str
    objective: str
    measure: str
    current_value: float = 0.0
    target_value: float = 0.0
    unit: str = ""
    kpi_type: KPIType = KPIType.TECHNICAL
    last_updated: Optional[datetime] = None
    trend: str = "stable"  # "improving", "declining", "stable"


class IndustrializationSuccessMetrics:
    """
    📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION
    
    Complete implementation of industrialization success metrics tracking
    both technical and business KPIs as specified in the requirements.
    """
    
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.kpis: Dict[str, IndustrializationKPI] = {}
        self.metrics_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        
        # Initialize Prometheus metrics
        self.registry = CollectorRegistry()
        self._initialize_prometheus_metrics()
        
        # Initialize KPIs according to problem statement
        self._initialize_technical_kpis()
        self._initialize_business_kpis()
        
        self.logger.info("Industrialization Success Metrics initialized")
    
    def _initialize_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics for monitoring"""
        self.technical_kpi_gauge = Gauge(
            'industrialization_technical_kpi_value',
            'Technical KPI values for industrialization success',
            ['metric_name', 'unit'],
            registry=self.registry
        )
        
        self.business_kpi_gauge = Gauge(
            'industrialization_business_kpi_value', 
            'Business KPI values for industrialization success',
            ['metric_name', 'unit'],
            registry=self.registry
        )
        
        self.kpi_target_gauge = Gauge(
            'industrialization_kpi_target',
            'Target values for industrialization KPIs',
            ['metric_name', 'kpi_type'],
            registry=self.registry
        )
        
        self.kpi_achievement_gauge = Gauge(
            'industrialization_kpi_achievement_rate',
            'Achievement rate for KPIs (current/target)',
            ['metric_name', 'kpi_type'],
            registry=self.registry
        )
    
    def _initialize_technical_kpis(self) -> None:
        """
        🎯 KPIs TECHNIQUES
        Initialize technical KPIs exactly as specified in problem statement
        """
        technical_kpis = [
            IndustrializationKPI(
                name="uptime_sla",
                objective="99.9%",
                measure="Monitoring continu",
                target_value=99.9,
                unit="percent",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="response_time_api",
                objective="<200ms P95",
                measure="APM + alerting",
                target_value=200.0,
                unit="milliseconds",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="error_rate",
                objective="<0.1%",
                measure="Logs + metrics",
                target_value=0.1,
                unit="percent",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="mttr",
                objective="<15 minutes",
                measure="Incident tracking",
                target_value=15.0,
                unit="minutes",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="deployment_frequency",
                objective=">10/jour",
                measure="CI/CD metrics",
                target_value=10.0,
                unit="per_day",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="security_score",
                objective="A+ (95%+)",
                measure="Security scanning",
                target_value=95.0,
                unit="percent",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="code_coverage",
                objective=">90%",
                measure="Testing automation",
                target_value=90.0,
                unit="percent",
                kpi_type=KPIType.TECHNICAL
            ),
            IndustrializationKPI(
                name="technical_debt_ratio",
                objective="<5%",
                measure="Code quality tools",
                target_value=5.0,
                unit="percent",
                kpi_type=KPIType.TECHNICAL
            )
        ]
        
        for kpi in technical_kpis:
            self.kpis[kpi.name] = kpi
            # Set target values in Prometheus
            self.kpi_target_gauge.labels(
                metric_name=kpi.name,
                kpi_type=kpi.kpi_type.value
            ).set(kpi.target_value)
    
    def _initialize_business_kpis(self) -> None:
        """
        💼 KPIs BUSINESS
        Initialize business KPIs exactly as specified in problem statement
        """
        business_kpis = [
            IndustrializationKPI(
                name="time_to_market",
                objective="<1 jour",
                measure="Feature deployment",
                target_value=1.0,
                unit="days",
                kpi_type=KPIType.BUSINESS
            ),
            IndustrializationKPI(
                name="customer_satisfaction",
                objective=">4.5/5",
                measure="Surveys + NPS",
                target_value=4.5,
                unit="rating",
                kpi_type=KPIType.BUSINESS
            ),
            IndustrializationKPI(
                name="cost_per_transaction",
                objective="<€0.10",
                measure="Financial analytics",
                target_value=0.10,
                unit="euros",
                kpi_type=KPIType.BUSINESS
            ),
            IndustrializationKPI(
                name="revenue_growth",
                objective="+20% MoM",
                measure="Business intelligence",
                target_value=20.0,
                unit="percent",
                kpi_type=KPIType.BUSINESS
            ),
            IndustrializationKPI(
                name="user_retention",
                objective=">85%",
                measure="Cohort analysis",
                target_value=85.0,
                unit="percent",
                kpi_type=KPIType.BUSINESS
            ),
            IndustrializationKPI(
                name="support_ticket_volume",
                objective="<100/jour",
                measure="Support analytics",
                target_value=100.0,
                unit="per_day",
                kpi_type=KPIType.BUSINESS
            )
        ]
        
        for kpi in business_kpis:
            self.kpis[kpi.name] = kpi
            # Set target values in Prometheus
            self.kpi_target_gauge.labels(
                metric_name=kpi.name,
                kpi_type=kpi.kpi_type.value
            ).set(kpi.target_value)
    
    async def update_kpi_value(self, kpi_name: str, value: float, timestamp: Optional[datetime] = None) -> bool:
        """Update a KPI value with the provided measurement"""
        try:
            if kpi_name not in self.kpis:
                self.logger.error(f"Unknown KPI: {kpi_name}")
                return False
            
            if timestamp is None:
                timestamp = datetime.now()
            
            kpi = self.kpis[kpi_name]
            kpi.current_value = value
            kpi.last_updated = timestamp
            
            # Update trend analysis
            self._update_trend(kpi_name, value, timestamp)
            
            # Update Prometheus metrics
            if kpi.kpi_type == KPIType.TECHNICAL:
                self.technical_kpi_gauge.labels(
                    metric_name=kpi_name,
                    unit=kpi.unit
                ).set(value)
            else:
                self.business_kpi_gauge.labels(
                    metric_name=kpi_name,
                    unit=kpi.unit
                ).set(value)
            
            # Calculate and update achievement rate
            if kpi.target_value > 0:
                # For metrics where higher is better (most cases)
                if kpi_name in ["uptime_sla", "security_score", "code_coverage", "customer_satisfaction", 
                               "revenue_growth", "user_retention", "deployment_frequency"]:
                    achievement_rate = (value / kpi.target_value) * 100
                # For metrics where lower is better
                else:
                    if value <= kpi.target_value:
                        achievement_rate = 100.0
                    else:
                        achievement_rate = (kpi.target_value / value) * 100
                
                self.kpi_achievement_gauge.labels(
                    metric_name=kpi_name,
                    kpi_type=kpi.kpi_type.value
                ).set(achievement_rate)
            
            self.logger.debug(f"Updated KPI {kpi_name}: {value} {kpi.unit}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating KPI {kpi_name}: {str(e)}")
            return False
    
    def _update_trend(self, kpi_name -> None: str, value -> None: float, timestamp -> None: datetime) -> None:
        """Update trend analysis for a KPI"""
        history = self.metrics_history[kpi_name]
        history.append((timestamp, value))
        
        # Keep only last 10 measurements for trend analysis
        if len(history) > 10:
            history.pop(0)
        
        # Calculate trend
        if len(history) >= 3:
            recent_values = [v for _, v in history[-3:]]
            if recent_values[-1] > recent_values[0] * 1.05:  # 5% improvement threshold
                self.kpis[kpi_name].trend = "improving"
            elif recent_values[-1] < recent_values[0] * 0.95:  # 5% decline threshold
                self.kpis[kpi_name].trend = "declining"
            else:
                self.kpis[kpi_name].trend = "stable"
    
    async def get_technical_kpis(self) -> Dict[str, Any]:
        """Get all technical KPIs"""
        technical_kpis = {
            name: {
                "name": kpi.name,
                "objective": kpi.objective,
                "measure": kpi.measure,
                "current_value": kpi.current_value,
                "target_value": kpi.target_value,
                "unit": kpi.unit,
                "trend": kpi.trend,
                "last_updated": kpi.last_updated.isoformat() if kpi.last_updated else None
            }
            for name, kpi in self.kpis.items()
            if kpi.kpi_type == KPIType.TECHNICAL
        }
        return technical_kpis
    
    async def get_business_kpis(self) -> Dict[str, Any]:
        """Get all business KPIs"""
        business_kpis = {
            name: {
                "name": kpi.name,
                "objective": kpi.objective,
                "measure": kpi.measure,
                "current_value": kpi.current_value,
                "target_value": kpi.target_value,
                "unit": kpi.unit,
                "trend": kpi.trend,
                "last_updated": kpi.last_updated.isoformat() if kpi.last_updated else None
            }
            for name, kpi in self.kpis.items()
            if kpi.kpi_type == KPIType.BUSINESS
        }
        return business_kpis
    
    async def get_all_kpis(self) -> Dict[str, Any]:
        """Get all KPIs organized by type"""
        return {
            "technical_kpis": await self.get_technical_kpis(),
            "business_kpis": await self.get_business_kpis(),
            "summary": await self.get_kpi_summary()
        }
    
    async def get_kpi_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all KPIs"""
        technical_kpis = await self.get_technical_kpis()
        business_kpis = await self.get_business_kpis()
        
        def calculate_achievement_stats(kpis) -> None:
            achievements = []
            for kpi_data in kpis.values():
                if kpi_data["target_value"] > 0 and kpi_data["current_value"] > 0:
                    # Calculate achievement based on objective type
                    kpi_name = kpi_data["name"]
                    if kpi_name in ["uptime_sla", "security_score", "code_coverage", "customer_satisfaction", 
                                   "revenue_growth", "user_retention", "deployment_frequency"]:
                        achievement = (kpi_data["current_value"] / kpi_data["target_value"]) * 100
                    else:
                        if kpi_data["current_value"] <= kpi_data["target_value"]:
                            achievement = 100.0
                        else:
                            achievement = (kpi_data["target_value"] / kpi_data["current_value"]) * 100
                    achievements.append(min(achievement, 100.0))  # Cap at 100%
            
            if achievements:
                return {
                    "average_achievement": statistics.mean(achievements),
                    "min_achievement": min(achievements),
                    "max_achievement": max(achievements),
                    "total_kpis": len(achievements),
                    "kpis_on_target": sum(1 for a in achievements if a >= 100.0)
                }
            return {"average_achievement": 0, "min_achievement": 0, "max_achievement": 0, 
                   "total_kpis": 0, "kpis_on_target": 0}
        
        technical_stats = calculate_achievement_stats(technical_kpis)
        business_stats = calculate_achievement_stats(business_kpis)
        
        return {
            "technical_kpis_stats": technical_stats,
            "business_kpis_stats": business_stats,
            "overall_industrialization_score": (
                technical_stats["average_achievement"] * 0.6 +  # 60% weight for technical
                business_stats["average_achievement"] * 0.4     # 40% weight for business
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    async def check_kpi_alerts(self) -> List[Dict[str, Any]]:
        """Check for KPI alerts based on targets"""
        alerts = []
        
        for kpi_name, kpi in self.kpis.items():
            if kpi.current_value == 0.0:  # No data yet
                continue
            
            alert_triggered = False
            severity = "info"
            
            # Define alert conditions based on KPI type
            if kpi_name in ["uptime_sla", "security_score", "code_coverage", "customer_satisfaction", 
                           "revenue_growth", "user_retention", "deployment_frequency"]:
                # Higher is better - alert if below target
                if kpi.current_value < kpi.target_value * 0.9:  # 10% below target
                    alert_triggered = True
                    severity = "critical" if kpi.current_value < kpi.target_value * 0.8 else "warning"
            else:
                # Lower is better - alert if above target
                if kpi.current_value > kpi.target_value * 1.1:  # 10% above target
                    alert_triggered = True
                    severity = "critical" if kpi.current_value > kpi.target_value * 1.5 else "warning"
            
            if alert_triggered:
                alerts.append({
                    "kpi_name": kpi_name,
                    "kpi_type": kpi.kpi_type.value,
                    "current_value": kpi.current_value,
                    "target_value": kpi.target_value,
                    "objective": kpi.objective,
                    "unit": kpi.unit,
                    "severity": severity,
                    "trend": kpi.trend,
                    "timestamp": datetime.now().isoformat()
                })
        
        return alerts
    
    async def generate_industrialization_report(self) -> Dict[str, Any]:
        """Generate comprehensive industrialization success report"""
        try:
            technical_kpis = await self.get_technical_kpis()
            business_kpis = await self.get_business_kpis()
            summary = await self.get_kpi_summary()
            alerts = await self.check_kpi_alerts()
            
            report = {
                "report_type": "Industrialization Success Metrics",
                "generated_at": datetime.now().isoformat(),
                "technical_kpis": technical_kpis,
                "business_kpis": business_kpis,
                "summary": summary,
                "alerts": alerts,
                "recommendations": self._generate_recommendations(summary, alerts)
            }
            
            self.logger.info(f"Generated industrialization report with {len(alerts)} alerts")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating industrialization report: {str(e)}")
            raise
    
    def _generate_recommendations(self, summary: Dict[str, Any], alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on current KPI performance"""
        recommendations = []
        
        overall_score = summary.get("overall_industrialization_score", 0)
        
        if overall_score < 70:
            recommendations.append("🚨 Critical: Overall industrialization score below 70%. Immediate action required.")
        elif overall_score < 85:
            recommendations.append("⚠️ Warning: Industrialization score below 85%. Review underperforming KPIs.")
        
        # Technical KPI recommendations
        tech_stats = summary.get("technical_kpis_stats", {})
        if tech_stats.get("average_achievement", 0) < 80:
            recommendations.append("🔧 Focus on technical infrastructure improvements and monitoring.")
        
        # Business KPI recommendations  
        business_stats = summary.get("business_kpis_stats", {})
        if business_stats.get("average_achievement", 0) < 80:
            recommendations.append("💼 Prioritize business process optimization and customer experience.")
        
        # Specific alert-based recommendations
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
        if critical_alerts:
            recommendations.append(f"🔥 {len(critical_alerts)} critical KPI alerts require immediate attention.")
        
        if len(recommendations) == 0:
            recommendations.append("✅ All KPIs performing well. Continue monitoring and optimization.")
        
        return recommendations


# Global instance for easy access
industrialization_metrics = IndustrializationSuccessMetrics()


async def main() -> None:
    """Test the industrialization success metrics system"""
    logging.basicConfig(level=logging.INFO)
    
    # Simulate some metric updates
    await industrialization_metrics.update_kpi_value("uptime_sla", 99.95)
    await industrialization_metrics.update_kpi_value("response_time_api", 150.0)
    await industrialization_metrics.update_kpi_value("error_rate", 0.05)
    await industrialization_metrics.update_kpi_value("customer_satisfaction", 4.6)
    await industrialization_metrics.update_kpi_value("revenue_growth", 22.5)
    
    # Generate report
    report = await industrialization_metrics.generate_industrialization_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())