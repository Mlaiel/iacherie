"""
📊 Reporting Engine - IA Influencer Agent Surveillance Module
===========================================================

Advanced reporting and analytics engine for surveillance activities,
infringement detection, and creator protection metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import csv
import io
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import statistics
from collections import defaultdict
import base64

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports"""
    INFRINGEMENT_SUMMARY = "infringement_summary"
    CREATOR_PROTECTION = "creator_protection"
    PLATFORM_ANALYSIS = "platform_analysis"
    TAKEDOWN_EFFECTIVENESS = "takedown_effectiveness"
    REVENUE_IMPACT = "revenue_impact"
    THREAT_INTELLIGENCE = "threat_intelligence"
    SURVEILLANCE_ACTIVITY = "surveillance_activity"
    PERFORMANCE_METRICS = "performance_metrics"
    LEGAL_COMPLIANCE = "legal_compliance"
    EXECUTIVE_DASHBOARD = "executive_dashboard"


class ReportFormat(Enum):
    """Available report formats"""
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"
    XML = "xml"


class ReportPeriod(Enum):
    """Report time periods"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class ReportConfig:
    """Report configuration"""
    report_id: str
    report_type: ReportType
    title: str
    description: str
    format: ReportFormat
    period: ReportPeriod
    
    # Filters and criteria
    creator_ids: List[str] = field(default_factory=list)
    content_ids: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    date_range: Optional[Tuple[datetime, datetime]] = None
    
    # Report options
    include_charts: bool = True
    include_raw_data: bool = False
    include_recommendations: bool = True
    confidential: bool = False
    
    # Scheduling
    scheduled: bool = False
    schedule_frequency: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReportData:
    """Report data container"""
    report_id: str
    config: ReportConfig
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generation_time_ms: int = 0
    file_path: Optional[str] = None
    file_size: int = 0
    checksum: Optional[str] = None


class BaseReportGenerator:
    """Base class for report generators"""
    
    def __init__(self, report_type: ReportType, surveillance_system):
        self.report_type = report_type
        self.surveillance_system = surveillance_system
    
    async def generate(self, config: ReportConfig) -> ReportData:
        """Generate report based on configuration"""
        # Default implementation for report generators without specific implementation
        logging.warning(f"Report generation not implemented for {self.__class__.__name__}")
        from datetime import datetime
        return ReportData(
            report_type=getattr(config, 'report_type', 'unknown'),
            generated_at=datetime.utcnow(),
            data={
                "status": "not_implemented",
                "message": f"Report generation not implemented for {self.__class__.__name__}"
            },
            summary="Report generation not available"
        )
    
    async def get_base_metrics(self, config: ReportConfig) -> Dict[str, Any]:
        """Get base metrics common to all reports"""
        start_time = config.date_range[0] if config.date_range else datetime.now(timezone.utc) - timedelta(days=30)
        end_time = config.date_range[1] if config.date_range else datetime.now(timezone.utc)
        
        # In production, these would query actual databases
        return {
            "report_period": {
                "start_date": start_time.isoformat(),
                "end_date": end_time.isoformat(),
                "duration_days": (end_time - start_time).days
            },
            "generation_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "report_version": "1.0",
                "system_version": "2.0.0"
            }
        }


class InfringementSummaryGenerator(BaseReportGenerator):
    """Generator for infringement summary reports"""
    
    def __init__(self, surveillance_system):
        super().__init__(ReportType.INFRINGEMENT_SUMMARY, surveillance_system)
    
    async def generate(self, config: ReportConfig) -> ReportData:
        """Generate infringement summary report"""
        start_time = datetime.now()
        
        base_metrics = await self.get_base_metrics(config)
        
        # Simulate infringement data collection
        infringement_data = await self._collect_infringement_data(config)
        
        # Generate summary statistics
        summary_stats = await self._generate_summary_statistics(infringement_data, config)
        
        # Platform breakdown
        platform_breakdown = await self._generate_platform_breakdown(infringement_data)
        
        # Trend analysis
        trend_analysis = await self._generate_trend_analysis(infringement_data, config)
        
        # Top infringers
        top_infringers = await self._identify_top_infringers(infringement_data)
        
        # Recommendations
        recommendations = await self._generate_recommendations(summary_stats, trend_analysis)
        
        report_data = {
            **base_metrics,
            "summary": summary_stats,
            "platform_breakdown": platform_breakdown,
            "trend_analysis": trend_analysis,
            "top_infringers": top_infringers,
            "recommendations": recommendations if config.include_recommendations else None
        }
        
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return ReportData(
            report_id=config.report_id,
            config=config,
            data=report_data,
            metadata={"data_points": len(infringement_data)},
            generation_time_ms=generation_time
        )
    
    async def _collect_infringement_data(self, config: ReportConfig) -> List[Dict[str, Any]]:
        """Collect infringement data based on filters"""
        # Simulate data collection
        sample_data = []
        
        platforms = config.platforms or ["youtube", "tiktok", "instagram", "facebook"]
        
        for i in range(100):  # Simulate 100 infringements
            infringement = {
                "infringement_id": f"inf_{i:04d}",
                "creator_id": f"creator_{i % 10}",
                "content_id": f"content_{i % 20}",
                "platform": platforms[i % len(platforms)],
                "similarity_score": 0.6 + (i % 40) * 0.01,  # 0.6 to 0.99
                "detection_date": datetime.now(timezone.utc) - timedelta(days=i % 30),
                "status": ["detected", "processing", "takedown_sent", "resolved"][i % 4],
                "estimated_views": (i + 1) * 1000,
                "estimated_revenue_loss": (i + 1) * 10.5,
                "infringer_country": ["US", "UK", "CA", "AU", "DE", "FR"][i % 6],
                "content_type": ["video", "audio", "image", "text"][i % 4],
                "risk_level": ["low", "medium", "high", "critical"][i % 4]
            }
            
            # Apply creator filter
            if config.creator_ids and infringement["creator_id"] not in config.creator_ids:
                continue
            
            # Apply date filter
            if config.date_range:
                if not (config.date_range[0] <= infringement["detection_date"] <= config.date_range[1]):
                    continue
            
            sample_data.append(infringement)
        
        return sample_data
    
    async def _generate_summary_statistics(self, data: List[Dict[str, Any]], config: ReportConfig) -> Dict[str, Any]:
        """Generate summary statistics from infringement data"""
        if not data:
            return {"total_infringements": 0}
        
        total_infringements = len(data)
        total_estimated_loss = sum(item["estimated_revenue_loss"] for item in data)
        total_estimated_views = sum(item["estimated_views"] for item in data)
        
        similarity_scores = [item["similarity_score"] for item in data]
        avg_similarity = statistics.mean(similarity_scores) if similarity_scores else 0
        
        # Status breakdown
        status_counts = defaultdict(int)
        for item in data:
            status_counts[item["status"]] += 1
        
        # Risk level breakdown
        risk_counts = defaultdict(int)
        for item in data:
            risk_counts[item["risk_level"]] += 1
        
        # Content type breakdown
        content_type_counts = defaultdict(int)
        for item in data:
            content_type_counts[item["content_type"]] += 1
        
        return {
            "total_infringements": total_infringements,
            "total_estimated_revenue_loss": round(total_estimated_loss, 2),
            "total_estimated_views_lost": total_estimated_views,
            "average_similarity_score": round(avg_similarity, 3),
            "status_distribution": dict(status_counts),
            "risk_level_distribution": dict(risk_counts),
            "content_type_distribution": dict(content_type_counts),
            "high_risk_percentage": round((risk_counts["high"] + risk_counts["critical"]) / total_infringements * 100, 1) if total_infringements > 0 else 0
        }
    
    async def _generate_platform_breakdown(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate platform-specific breakdown"""
        platform_stats = defaultdict(lambda: {
            "count": 0,
            "estimated_loss": 0,
            "estimated_views": 0,
            "avg_similarity": 0,
            "similarities": []
        })
        
        for item in data:
            platform = item["platform"]
            platform_stats[platform]["count"] += 1
            platform_stats[platform]["estimated_loss"] += item["estimated_revenue_loss"]
            platform_stats[platform]["estimated_views"] += item["estimated_views"]
            platform_stats[platform]["similarities"].append(item["similarity_score"])
        
        # Calculate averages
        result = {}
        for platform, stats in platform_stats.items():
            if stats["similarities"]:
                avg_sim = statistics.mean(stats["similarities"])
            else:
                avg_sim = 0
            
            result[platform] = {
                "infringement_count": stats["count"],
                "estimated_revenue_loss": round(stats["estimated_loss"], 2),
                "estimated_views_lost": stats["estimated_views"],
                "average_similarity_score": round(avg_sim, 3),
                "percentage_of_total": round(stats["count"] / len(data) * 100, 1) if data else 0
            }
        
        return result
    
    async def _generate_trend_analysis(self, data: List[Dict[str, Any]], config: ReportConfig) -> Dict[str, Any]:
        """Generate trend analysis"""
        # Group data by day
        daily_counts = defaultdict(int)
        daily_losses = defaultdict(float)
        
        for item in data:
            date_key = item["detection_date"].date().isoformat()
            daily_counts[date_key] += 1
            daily_losses[date_key] += item["estimated_revenue_loss"]
        
        # Sort by date
        sorted_dates = sorted(daily_counts.keys())
        
        trend_data = {
            "daily_infringement_counts": [
                {"date": date, "count": daily_counts[date], "revenue_loss": round(daily_losses[date], 2)}
                for date in sorted_dates
            ]
        }
        
        # Calculate growth rate if we have enough data
        if len(sorted_dates) >= 7:
            recent_avg = statistics.mean([daily_counts[date] for date in sorted_dates[-7:]])
            older_avg = statistics.mean([daily_counts[date] for date in sorted_dates[:7]])
            
            if older_avg > 0:
                growth_rate = ((recent_avg - older_avg) / older_avg) * 100
            else:
                growth_rate = 0
            
            trend_data["week_over_week_growth"] = round(growth_rate, 2)
        
        return trend_data
    
    async def _identify_top_infringers(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify top infringers by various metrics"""
        infringer_stats = defaultdict(lambda: {
            "count": 0,
            "total_loss": 0,
            "total_views": 0,
            "countries": set(),
            "platforms": set(),
            "latest_infringement": None
        })
        
        # Simulate infringer identification (in production, this would use actual infringer data)
        for item in data:
            # Create a fake infringer ID based on some characteristics
            infringer_id = f"infringer_{hash(item['infringer_country'] + item['platform']) % 50:03d}"
            
            stats = infringer_stats[infringer_id]
            stats["count"] += 1
            stats["total_loss"] += item["estimated_revenue_loss"]
            stats["total_views"] += item["estimated_views"]
            stats["countries"].add(item["infringer_country"])
            stats["platforms"].add(item["platform"])
            
            if not stats["latest_infringement"] or item["detection_date"] > stats["latest_infringement"]:
                stats["latest_infringement"] = item["detection_date"]
        
        # Convert to list and sort
        top_infringers = []
        for infringer_id, stats in infringer_stats.items():
            top_infringers.append({
                "infringer_id": infringer_id,
                "infringement_count": stats["count"],
                "total_estimated_loss": round(stats["total_loss"], 2),
                "total_estimated_views": stats["total_views"],
                "active_countries": list(stats["countries"]),
                "active_platforms": list(stats["platforms"]),
                "latest_activity": stats["latest_infringement"].isoformat() if stats["latest_infringement"] else None,
                "threat_score": min(100, stats["count"] * 2 + stats["total_loss"] / 100)
            })
        
        # Sort by total loss and take top 10
        top_infringers.sort(key=lambda x: x["total_estimated_loss"], reverse=True)
        
        return {
            "top_by_revenue_impact": top_infringers[:10],
            "top_by_frequency": sorted(top_infringers, key=lambda x: x["infringement_count"], reverse=True)[:10]
        }
    
    async def _generate_recommendations(self, summary: Dict[str, Any], trends: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # High-risk infringements
        if summary.get("high_risk_percentage", 0) > 30:
            recommendations.append({
                "category": "Risk Management",
                "priority": "High",
                "recommendation": "High-risk infringements represent over 30% of total cases. Consider implementing enhanced monitoring and faster response protocols.",
                "action": "Implement automated high-priority takedown workflows"
            })
        
        # Revenue impact
        if summary.get("total_estimated_revenue_loss", 0) > 10000:
            recommendations.append({
                "category": "Revenue Protection",
                "priority": "Critical",
                "recommendation": f"Estimated revenue loss of ${summary['total_estimated_revenue_loss']:.2f} requires immediate attention.",
                "action": "Escalate high-value infringement cases to legal team"
            })
        
        # Platform-specific recommendations
        platform_counts = summary.get("platform_distribution", {})
        if platform_counts:
            highest_platform = max(platform_counts, key=platform_counts.get)
            if platform_counts[highest_platform] > len(platform_counts) * 2:
                recommendations.append({
                    "category": "Platform Focus",
                    "priority": "Medium",
                    "recommendation": f"{highest_platform.title()} shows disproportionately high infringement activity.",
                    "action": f"Implement enhanced monitoring and establish direct contact with {highest_platform.title()} content protection team"
                })
        
        # Growth trends
        growth_rate = trends.get("week_over_week_growth", 0)
        if growth_rate > 20:
            recommendations.append({
                "category": "Trend Analysis",
                "priority": "High",
                "recommendation": f"Infringement activity is growing at {growth_rate:.1f}% week-over-week.",
                "action": "Scale up monitoring resources and consider proactive content protection measures"
            })
        
        return recommendations


class CreatorProtectionGenerator(BaseReportGenerator):
    """Generator for creator protection reports"""
    
    def __init__(self, surveillance_system):
        super().__init__(ReportType.CREATOR_PROTECTION, surveillance_system)
    
    async def generate(self, config: ReportConfig) -> ReportData:
        """Generate creator protection report"""
        start_time = datetime.now()
        
        base_metrics = await self.get_base_metrics(config)
        
        # Protection metrics for each creator
        protection_metrics = await self._calculate_protection_metrics(config)
        
        # Content analysis
        content_analysis = await self._analyze_protected_content(config)
        
        # Threat landscape
        threat_landscape = await self._analyze_threat_landscape(config)
        
        # Protection effectiveness
        effectiveness_metrics = await self._calculate_effectiveness_metrics(config)
        
        report_data = {
            **base_metrics,
            "protection_metrics": protection_metrics,
            "content_analysis": content_analysis,
            "threat_landscape": threat_landscape,
            "effectiveness": effectiveness_metrics
        }
        
        generation_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return ReportData(
            report_id=config.report_id,
            config=config,
            data=report_data,
            generation_time_ms=generation_time
        )
    
    async def _calculate_protection_metrics(self, config: ReportConfig) -> Dict[str, Any]:
        """Calculate protection metrics for creators"""
        creator_metrics = {}
        
        creators = config.creator_ids or [f"creator_{i}" for i in range(5)]
        
        for creator_id in creators:
            # Simulate protection data
            metrics = {
                "creator_id": creator_id,
                "protected_content_count": 25 + (hash(creator_id) % 50),
                "active_protections": 23 + (hash(creator_id) % 10),
                "infringements_detected": 8 + (hash(creator_id) % 20),
                "infringements_resolved": 6 + (hash(creator_id) % 15),
                "estimated_revenue_protected": (hash(creator_id) % 10000) + 5000,
                "protection_score": 75 + (hash(creator_id) % 25),  # 75-100%
                "last_scan": (datetime.now(timezone.utc) - timedelta(hours=hash(creator_id) % 24)).isoformat(),
                "content_types": ["video", "audio", "image", "text"],
                "protected_platforms": ["youtube", "tiktok", "instagram", "facebook"]
            }
            
            creator_metrics[creator_id] = metrics
        
        return creator_metrics
    
    async def _analyze_protected_content(self, config: ReportConfig) -> Dict[str, Any]:
        """Analyze protected content across creators"""
        content_stats = {
            "total_protected_items": 0,
            "content_type_breakdown": defaultdict(int),
            "platform_coverage": defaultdict(int),
            "protection_method_distribution": {
                "ai_fingerprinting": 85,
                "watermarking": 60,
                "metadata_tracking": 70,
                "blockchain_registration": 35
            },
            "average_protection_score": 82.5
        }
        
        # Simulate content analysis
        for i in range(100):
            content_stats["total_protected_items"] += 1
            content_type = ["video", "audio", "image", "text"][i % 4]
            content_stats["content_type_breakdown"][content_type] += 1
            
            platform = ["youtube", "tiktok", "instagram", "facebook", "twitter"][i % 5]
            content_stats["platform_coverage"][platform] += 1
        
        content_stats["content_type_breakdown"] = dict(content_stats["content_type_breakdown"])
        content_stats["platform_coverage"] = dict(content_stats["platform_coverage"])
        
        return content_stats
    
    async def _analyze_threat_landscape(self, config: ReportConfig) -> Dict[str, Any]:
        """Analyze threat landscape for creators"""
        threat_analysis = {
            "active_threats": 45,
            "threat_sources": {
                "social_media_platforms": 65,
                "file_sharing_sites": 20,
                "streaming_platforms": 10,
                "commercial_websites": 5
            },
            "threat_severity_distribution": {
                "low": 30,
                "medium": 35,
                "high": 25,
                "critical": 10
            },
            "geographic_threat_map": {
                "US": 35,
                "UK": 15,
                "Canada": 12,
                "Australia": 8,
                "Germany": 6,
                "Others": 24
            },
            "trending_threats": [
                {
                    "type": "AI-generated derivatives",
                    "growth_rate": 45.2,
                    "severity": "high",
                    "description": "AI tools being used to create derivatives of original content"
                },
                {
                    "type": "Cross-platform repurposing",
                    "growth_rate": 32.1,
                    "severity": "medium", 
                    "description": "Content being reformatted and reposted across multiple platforms"
                },
                {
                    "type": "Remix culture violations",
                    "growth_rate": 28.7,
                    "severity": "medium",
                    "description": "Unauthorized remixes and mashups gaining popularity"
                }
            ]
        }
        
        return threat_analysis
    
    async def _calculate_effectiveness_metrics(self, config: ReportConfig) -> Dict[str, Any]:
        """Calculate protection effectiveness metrics"""
        effectiveness = {
            "detection_rate": 94.2,  # Percentage of infringements detected
            "response_time": {
                "average_hours": 4.2,
                "median_hours": 2.1,
                "percentile_95_hours": 12.5
            },
            "takedown_success_rate": 87.5,
            "false_positive_rate": 2.1,
            "creator_satisfaction_score": 4.3,  # Out of 5
            "cost_per_protection": 12.50,
            "roi_estimate": {
                "protection_cost": 2500,
                "revenue_saved": 45000,
                "roi_percentage": 1700
            },
            "improvement_trends": {
                "detection_accuracy": +5.2,  # Percentage point improvement
                "response_time": -15.3,  # Percentage improvement (negative = faster)
                "success_rate": +3.1
            }
        }
        
        return effectiveness


class ReportingEngine:
    """
    Advanced reporting and analytics engine for surveillance activities,
    infringement detection, and creator protection metrics
    """
    
    def __init__(self, surveillance_system):
        self.surveillance_system = surveillance_system
        self.generators: Dict[ReportType, BaseReportGenerator] = {}
        self.scheduled_reports: Dict[str, ReportConfig] = {}
        self.report_cache: Dict[str, ReportData] = {}
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize reporting engine"""
        try:
            # Initialize report generators
            self.generators[ReportType.INFRINGEMENT_SUMMARY] = InfringementSummaryGenerator(self.surveillance_system)
            self.generators[ReportType.CREATOR_PROTECTION] = CreatorProtectionGenerator(self.surveillance_system)
            
            # Initialize other generators
            self.generators[ReportType.PLATFORM_ANALYSIS] = PlatformAnalysisGenerator(self.surveillance_system)
            self.generators[ReportType.TAKEDOWN_EFFECTIVENESS] = TakedownEffectivenessGenerator(self.surveillance_system)
            self.generators[ReportType.CONTENT_DISTRIBUTION] = ContentDistributionGenerator(self.surveillance_system)
            self.generators[ReportType.THREAT_ANALYSIS] = ThreatAnalysisGenerator(self.surveillance_system)
            self.generators[ReportType.COMPLIANCE_AUDIT] = ComplianceAuditGenerator(self.surveillance_system)
            self.generators[ReportType.PERFORMANCE_METRICS] = PerformanceMetricsGenerator(self.surveillance_system)
            self.generators[ReportType.FINANCIAL_IMPACT] = FinancialImpactGenerator(self.surveillance_system)
            self.generators[ReportType.TREND_ANALYSIS] = TrendAnalysisGenerator(self.surveillance_system)
            
            logger.info(f"Initialized {len(self.generators)} report generators successfully")
            
            self.initialized = True
            logger.info(f"Reporting Engine initialized with {len(self.generators)} generators")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reporting Engine: {e}")
            raise
    
    async def generate_report(
        self,
        report_type: ReportType,
        title: str,
        format: ReportFormat = ReportFormat.JSON,
        period: ReportPeriod = ReportPeriod.MONTHLY,
        creator_ids: Optional[List[str]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        **kwargs
    ) -> ReportData:
        """Generate a report"""
        report_id = f"report_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        config = ReportConfig(
            report_id=report_id,
            report_type=report_type,
            title=title,
            description=kwargs.get("description", f"Generated {report_type.value} report"),
            format=format,
            period=period,
            creator_ids=creator_ids or [],
            date_range=date_range,
            **{k: v for k, v in kwargs.items() if k != "description"}
        )
        
        if report_type not in self.generators:
            raise ValueError(f"No generator available for report type: {report_type.value}")
        
        try:
            generator = self.generators[report_type]
            report_data = await generator.generate(config)
            
            # Cache report if requested
            if kwargs.get("cache", True):
                self.report_cache[report_id] = report_data
            
            # Format report if not JSON
            if format != ReportFormat.JSON:
                await self._format_report(report_data, format)
            
            logger.info(f"Report generated: {report_id} (type: {report_type.value}, format: {format.value})")
            
            return report_data
            
        except Exception as e:
            logger.error(f"Failed to generate report {report_id}: {e}")
            raise
    
    async def _format_report(self, report_data: ReportData, format: ReportFormat) -> None:
        """Format report in the requested format"""
        if format == ReportFormat.CSV:
            await self._format_as_csv(report_data)
        elif format == ReportFormat.HTML:
            await self._format_as_html(report_data)
        elif format == ReportFormat.PDF:
            await self._format_as_pdf(report_data)
        elif format == ReportFormat.EXCEL:
            await self._format_as_excel(report_data)
        elif format == ReportFormat.XML:
            await self._format_as_xml(report_data)
    
    async def _format_as_csv(self, report_data: ReportData) -> None:
        """Format report as CSV"""
        output = io.StringIO()
        
        # Write basic info
        output.write(f"Report ID,{report_data.report_id}\n")
        output.write(f"Generated At,{report_data.generated_at.isoformat()}\n")
        output.write(f"Report Type,{report_data.config.report_type.value}\n")
        output.write("\n")
        
        # Flatten and write data
        if "summary" in report_data.data:
            summary = report_data.data["summary"]
            output.write("Summary Statistics\n")
            for key, value in summary.items():
                if not isinstance(value, (dict, list)):
                    output.write(f"{key},{value}\n")
        
        report_data.file_path = f"/tmp/{report_data.report_id}.csv"
        # In production, save to actual file
        logger.info(f"Report formatted as CSV: {report_data.file_path}")
    
    async def _format_as_html(self, report_data: ReportData) -> None:
        """Format report as HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report_data.config.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .metric {{ background-color: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_data.config.title}</h1>
                <p><strong>Report ID:</strong> {report_data.report_id}</p>
                <p><strong>Generated:</strong> {report_data.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Type:</strong> {report_data.config.report_type.value.replace('_', ' ').title()}</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                {self._create_html_summary(report_data.data)}
            </div>
        </body>
        </html>
        """
        
        report_data.file_path = f"/tmp/{report_data.report_id}.html"
        # In production, save to actual file
        logger.info(f"Report formatted as HTML: {report_data.file_path}")
    
    def _create_html_summary(self, data: Dict[str, Any]) -> str:
        """Create HTML summary section"""
        html = ""
        
        if "summary" in data:
            summary = data["summary"]
            for key, value in summary.items():
                if not isinstance(value, (dict, list)):
                    html += f'<div class="metric"><strong>{key.replace("_", " ").title()}:</strong> {value}</div>'
        
        return html
    
    async def _format_as_pdf(self, report_data: ReportData) -> None:
        """Format report as PDF (placeholder)"""
        # In production, use libraries like reportlab or weasyprint
        report_data.file_path = f"/tmp/{report_data.report_id}.pdf"
        logger.info(f"Report formatted as PDF: {report_data.file_path}")
    
    async def _format_as_excel(self, report_data: ReportData) -> None:
        """Format report as Excel (placeholder)"""
        # In production, use libraries like openpyxl or xlsxwriter
        report_data.file_path = f"/tmp/{report_data.report_id}.xlsx"
        logger.info(f"Report formatted as Excel: {report_data.file_path}")
    
    async def _format_as_xml(self, report_data: ReportData) -> None:
        """Format report as XML (placeholder)"""
        report_data.file_path = f"/tmp/{report_data.report_id}.xml"
        logger.info(f"Report formatted as XML: {report_data.file_path}")
    
    async def schedule_report(
        self,
        report_type: ReportType,
        title: str,
        frequency: str,
        recipients: List[str],
        **kwargs
    ) -> str:
        """Schedule a recurring report"""
        report_id = f"scheduled_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        config = ReportConfig(
            report_id=report_id,
            report_type=report_type,
            title=title,
            description=kwargs.get("description", f"Scheduled {report_type.value} report"),
            format=kwargs.get("format", ReportFormat.JSON),
            period=kwargs.get("period", ReportPeriod.MONTHLY),
            scheduled=True,
            schedule_frequency=frequency,
            recipients=recipients,
            **{k: v for k, v in kwargs.items() if k not in ["description", "format", "period"]}
        )
        
        self.scheduled_reports[report_id] = config
        
        logger.info(f"Report scheduled: {report_id} (frequency: {frequency})")
        return report_id
    
    async def get_report(self, report_id: str) -> Optional[ReportData]:
        """Get a cached report"""
        return self.report_cache.get(report_id)
    
    async def list_reports(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available reports"""
        reports = []
        
        for report_id, report_data in self.report_cache.items():
            # Filter by creator if specified
            if creator_id and creator_id not in report_data.config.creator_ids:
                continue
            
            reports.append({
                "report_id": report_id,
                "title": report_data.config.title,
                "type": report_data.config.report_type.value,
                "format": report_data.config.format.value,
                "generated_at": report_data.generated_at.isoformat(),
                "file_size": report_data.file_size,
                "file_path": report_data.file_path
            })
        
        return sorted(reports, key=lambda x: x["generated_at"], reverse=True)
    
    async def delete_report(self, report_id: str) -> bool:
        """Delete a report"""
        if report_id in self.report_cache:
            report_data = self.report_cache.pop(report_id)
            
            # Delete file if it exists
            if report_data.file_path:
                # In production, delete actual file
                logger.info(f"Deleted report file: {report_data.file_path}")
            
            logger.info(f"Report deleted: {report_id}")
            return True
        
        return False
    
    async def get_report_statistics(self) -> Dict[str, Any]:
        """Get reporting statistics"""
        total_reports = len(self.report_cache)
        scheduled_reports = len(self.scheduled_reports)
        
        # Report type distribution
        type_counts = defaultdict(int)
        for report_data in self.report_cache.values():
            type_counts[report_data.config.report_type.value] += 1
        
        # Format distribution
        format_counts = defaultdict(int)
        for report_data in self.report_cache.values():
            format_counts[report_data.config.format.value] += 1
        
        # Generation time statistics
        generation_times = [report_data.generation_time_ms for report_data in self.report_cache.values()]
        avg_generation_time = statistics.mean(generation_times) if generation_times else 0
        
        return {
            "total_reports_generated": total_reports,
            "scheduled_reports": scheduled_reports,
            "report_type_distribution": dict(type_counts),
            "format_distribution": dict(format_counts),
            "average_generation_time_ms": round(avg_generation_time, 2),
            "cache_size": total_reports,
            "available_generators": len(self.generators)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on reporting engine"""
        return {
            "engine": "healthy" if self.initialized else "unhealthy",
            "generators_available": len(self.generators),
            "cached_reports": len(self.report_cache),
            "scheduled_reports": len(self.scheduled_reports),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown reporting engine"""
        logger.info("Shutting down Reporting Engine")
        
        # Clear cache
        self.report_cache.clear()
        self.scheduled_reports.clear()
        
        self.initialized = False
        logger.info("Reporting Engine shutdown complete")


# Export main components
__all__ = [
    "ReportingEngine",
    "ReportType",
    "ReportFormat",
    "ReportPeriod",
    "ReportConfig",
    "ReportData",
    "BaseReportGenerator",
    "InfringementSummaryGenerator",
    "CreatorProtectionGenerator"
]
