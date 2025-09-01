"""Automated Stakeholder Reporting System
======================================

Automated reporting system for stakeholders and investors with customizable
reports, scheduled delivery, and comprehensive business intelligence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of automated reports"""
    EXECUTIVE_SUMMARY = "executive_summary"
    FINANCIAL_PERFORMANCE = "financial_performance"
    USER_ANALYTICS = "user_analytics"
    GROWTH_METRICS = "growth_metrics"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    OPERATIONAL_METRICS = "operational_metrics"
    RISK_ASSESSMENT = "risk_assessment"
    COMPREHENSIVE = "comprehensive"


class ReportFrequency(Enum):
    """Report delivery frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


class DeliveryFormat(Enum):
    """Report delivery formats"""
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"
    JSON = "json"
    POWERPOINT = "powerpoint"


@dataclass
class ReportRecipient:
    """Report recipient configuration"""
    name: str
    email: str
    role: str
    report_types: List[ReportType]
    delivery_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportTemplate:
    """Report template configuration"""
    template_id: str
    name: str
    report_type: ReportType
    sections: List[str]
    visualizations: List[str]
    custom_branding: bool = True
    executive_summary_length: str = "medium"  # short, medium, long
    include_recommendations: bool = True
    include_appendix: bool = True


@dataclass
class ReportSchedule:
    """Report delivery schedule"""
    schedule_id: str
    report_type: ReportType
    frequency: ReportFrequency
    delivery_time: str  # "09:00" or "monday_09:00"
    recipients: List[str]  # recipient IDs
    formats: List[DeliveryFormat]
    is_active: bool = True
    next_delivery: Optional[datetime] = None


@dataclass
class ReportMetrics:
    """Report metrics and data"""
    metric_id: str
    name: str
    value: Union[float, int, str]
    previous_value: Optional[Union[float, int, str]] = None
    change_percentage: Optional[float] = None
    trend: Optional[str] = None  # up, down, stable
    target: Optional[Union[float, int]] = None
    status: Optional[str] = None  # on_track, at_risk, critical
    visualization_type: str = "metric"  # metric, chart, gauge, table


class StakeholderReportingSystem:
    """
    Automated stakeholder reporting system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recipients: Dict[str, ReportRecipient] = {}
        self.templates: Dict[str, ReportTemplate] = {}
        self.schedules: Dict[str, ReportSchedule] = {}
        self.report_history: List[Dict[str, Any]] = []
        
        # Initialize default templates and schedules
        self._setup_default_templates()
        self._setup_default_recipients()
        self._setup_default_schedules()

    def _setup_default_templates(self):
        """Setup default report templates"""
        self.templates.update({
            "executive_weekly": ReportTemplate(
                template_id="executive_weekly",
                name="Executive Weekly Summary",
                report_type=ReportType.EXECUTIVE_SUMMARY,
                sections=[
                    "executive_summary",
                    "key_metrics",
                    "financial_highlights",
                    "user_growth",
                    "market_position",
                    "key_achievements",
                    "risks_and_challenges",
                    "upcoming_priorities"
                ],
                visualizations=[
                    "revenue_trend",
                    "user_growth_chart",
                    "key_metrics_dashboard"
                ],
                executive_summary_length="medium"
            ),
            "financial_monthly": ReportTemplate(
                template_id="financial_monthly",
                name="Monthly Financial Performance",
                report_type=ReportType.FINANCIAL_PERFORMANCE,
                sections=[
                    "financial_summary",
                    "revenue_analysis",
                    "cost_analysis",
                    "profitability_metrics",
                    "cash_flow",
                    "forecasting",
                    "variance_analysis"
                ],
                visualizations=[
                    "revenue_breakdown",
                    "cost_structure",
                    "profitability_trend",
                    "cash_flow_chart"
                ]
            ),
            "investor_quarterly": ReportTemplate(
                template_id="investor_quarterly",
                name="Quarterly Investor Report",
                report_type=ReportType.COMPREHENSIVE,
                sections=[
                    "executive_summary",
                    "financial_performance",
                    "user_metrics",
                    "product_development",
                    "market_analysis",
                    "competitive_position",
                    "team_updates",
                    "financial_projections",
                    "funding_status",
                    "risk_factors"
                ],
                visualizations=[
                    "comprehensive_dashboard",
                    "financial_trends",
                    "user_analytics",
                    "market_comparison"
                ],
                executive_summary_length="long",
                include_appendix=True
            )
        })

    def _setup_default_recipients(self):
        """Setup default report recipients"""
        self.recipients.update({
            "ceo": ReportRecipient(
                name="Chief Executive Officer",
                email="ceo@company.com",
                role="executive",
                report_types=[
                    ReportType.EXECUTIVE_SUMMARY,
                    ReportType.COMPREHENSIVE,
                    ReportType.COMPETITIVE_ANALYSIS
                ],
                delivery_preferences={
                    "format": DeliveryFormat.PDF,
                    "include_charts": True,
                    "priority": "high"
                }
            ),
            "cfo": ReportRecipient(
                name="Chief Financial Officer",
                email="cfo@company.com",
                role="executive",
                report_types=[
                    ReportType.FINANCIAL_PERFORMANCE,
                    ReportType.EXECUTIVE_SUMMARY,
                    ReportType.RISK_ASSESSMENT
                ],
                delivery_preferences={
                    "format": DeliveryFormat.EXCEL,
                    "include_raw_data": True
                }
            ),
            "investors": ReportRecipient(
                name="Investor Group",
                email="investors@company.com",
                role="investor",
                report_types=[
                    ReportType.COMPREHENSIVE,
                    ReportType.FINANCIAL_PERFORMANCE,
                    ReportType.GROWTH_METRICS
                ],
                delivery_preferences={
                    "format": DeliveryFormat.PDF,
                    "branding": "investor"
                }
            ),
            "board": ReportRecipient(
                name="Board of Directors",
                email="board@company.com",
                role="board",
                report_types=[
                    ReportType.COMPREHENSIVE,
                    ReportType.RISK_ASSESSMENT,
                    ReportType.COMPETITIVE_ANALYSIS
                ],
                delivery_preferences={
                    "format": DeliveryFormat.POWERPOINT,
                    "executive_focus": True
                }
            )
        })

    def _setup_default_schedules(self):
        """Setup default report schedules"""
        self.schedules.update({
            "daily_executive": ReportSchedule(
                schedule_id="daily_executive",
                report_type=ReportType.EXECUTIVE_SUMMARY,
                frequency=ReportFrequency.DAILY,
                delivery_time="08:00",
                recipients=["ceo", "cfo"],
                formats=[DeliveryFormat.PDF, DeliveryFormat.HTML]
            ),
            "weekly_comprehensive": ReportSchedule(
                schedule_id="weekly_comprehensive",
                report_type=ReportType.COMPREHENSIVE,
                frequency=ReportFrequency.WEEKLY,
                delivery_time="monday_09:00",
                recipients=["ceo", "cfo", "investors"],
                formats=[DeliveryFormat.PDF]
            ),
            "monthly_financial": ReportSchedule(
                schedule_id="monthly_financial",
                report_type=ReportType.FINANCIAL_PERFORMANCE,
                frequency=ReportFrequency.MONTHLY,
                delivery_time="first_tuesday_10:00",
                recipients=["cfo", "investors", "board"],
                formats=[DeliveryFormat.EXCEL, DeliveryFormat.PDF]
            ),
            "quarterly_investor": ReportSchedule(
                schedule_id="quarterly_investor",
                report_type=ReportType.COMPREHENSIVE,
                frequency=ReportFrequency.QUARTERLY,
                delivery_time="first_monday_09:00",
                recipients=["investors", "board"],
                formats=[DeliveryFormat.PDF, DeliveryFormat.POWERPOINT]
            )
        })

    async def generate_report(
        self,
        report_type: ReportType,
        template_id: Optional[str] = None,
        custom_sections: Optional[List[str]] = None,
        date_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """Generate a stakeholder report"""
        try:
            report_id = str(uuid.uuid4())
            generation_time = datetime.now(timezone.utc)
            
            # Get template
            template = self._get_report_template(report_type, template_id)
            
            # Determine sections to include
            sections = custom_sections or template.sections
            
            # Get date range
            if not date_range:
                date_range = self._get_default_date_range(report_type)
            
            # Generate report content
            report_content = await self._generate_report_content(
                report_type, sections, date_range, template
            )
            
            # Generate visualizations
            visualizations = await self._generate_visualizations(
                template.visualizations, date_range
            )
            
            # Create complete report
            report = {
                "report_id": report_id,
                "report_type": report_type.value,
                "template_id": template.template_id,
                "generated_at": generation_time,
                "date_range": date_range,
                "content": report_content,
                "visualizations": visualizations,
                "metadata": {
                    "generation_time_seconds": 0.0,  # Would be calculated
                    "data_sources": ["business_metrics", "user_analytics", "financial_data"],
                    "quality_score": 0.95  # Report quality assessment
                }
            }
            
            # Store report in history
            self.report_history.append({
                "report_id": report_id,
                "type": report_type.value,
                "generated_at": generation_time,
                "recipients": [],
                "status": "generated"
            })
            
            self.logger.info(f"Generated {report_type.value} report: {report_id}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            raise

    def _get_report_template(self, report_type: ReportType, template_id: Optional[str]) -> ReportTemplate:
        """Get report template"""
        if template_id and template_id in self.templates:
            return self.templates[template_id]
        
        # Find default template for report type
        for template in self.templates.values():
            if template.report_type == report_type:
                return template
        
        # Return default template
        return ReportTemplate(
            template_id="default",
            name="Default Report",
            report_type=report_type,
            sections=["summary", "metrics", "analysis"],
            visualizations=["basic_charts"]
        )

    def _get_default_date_range(self, report_type: ReportType) -> Dict[str, datetime]:
        """Get default date range for report type"""
        end_date = datetime.now(timezone.utc)
        
        if report_type in [ReportType.EXECUTIVE_SUMMARY, ReportType.OPERATIONAL_METRICS]:
            start_date = end_date - timedelta(days=7)  # Weekly
        elif report_type == ReportType.FINANCIAL_PERFORMANCE:
            start_date = end_date - timedelta(days=30)  # Monthly
        elif report_type == ReportType.COMPREHENSIVE:
            start_date = end_date - timedelta(days=90)  # Quarterly
        else:
            start_date = end_date - timedelta(days=30)  # Default monthly
        
        return {"start_date": start_date, "end_date": end_date}

    async def _generate_report_content(
        self,
        report_type: ReportType,
        sections: List[str],
        date_range: Dict[str, datetime],
        template: ReportTemplate
    ) -> Dict[str, Any]:
        """Generate report content for all sections"""
        content = {}
        
        for section in sections:
            section_content = await self._generate_section_content(
                section, report_type, date_range, template
            )
            content[section] = section_content
        
        return content

    async def _generate_section_content(
        self,
        section: str,
        report_type: ReportType,
        date_range: Dict[str, datetime],
        template: ReportTemplate
    ) -> Dict[str, Any]:
        """Generate content for a specific report section"""
        
        if section == "executive_summary":
            return await self._generate_executive_summary(date_range, template)
        elif section == "key_metrics":
            return await self._generate_key_metrics(date_range)
        elif section == "financial_highlights":
            return await self._generate_financial_highlights(date_range)
        elif section == "user_growth":
            return await self._generate_user_growth_analysis(date_range)
        elif section == "market_position":
            return await self._generate_market_position_analysis(date_range)
        elif section == "revenue_analysis":
            return await self._generate_revenue_analysis(date_range)
        elif section == "competitive_position":
            return await self._generate_competitive_analysis(date_range)
        elif section == "risk_factors":
            return await self._generate_risk_assessment(date_range)
        elif section == "forecasting":
            return await self._generate_forecasting_section(date_range)
        else:
            return {"content": f"Section '{section}' content would be generated here"}

    async def _generate_executive_summary(
        self, date_range: Dict[str, datetime], template: ReportTemplate
    ) -> Dict[str, Any]:
        """Generate executive summary section"""
        
        # Get key metrics for summary
        revenue_metrics = await self._get_revenue_metrics(date_range)
        user_metrics = await self._get_user_metrics(date_range)
        growth_metrics = await self._calculate_growth_metrics(date_range)
        
        summary_length = template.executive_summary_length
        
        if summary_length == "short":
            summary_text = self._generate_short_summary(revenue_metrics, user_metrics)
        elif summary_length == "long":
            summary_text = self._generate_long_summary(revenue_metrics, user_metrics, growth_metrics)
        else:  # medium
            summary_text = self._generate_medium_summary(revenue_metrics, user_metrics)
        
        return {
            "summary_text": summary_text,
            "key_highlights": [
                f"Revenue: ${revenue_metrics.get('total_revenue', 0):,.0f} ({growth_metrics.get('revenue_growth', 0):+.1%})",
                f"Active Users: {user_metrics.get('active_users', 0):,} ({growth_metrics.get('user_growth', 0):+.1%})",
                f"Retention Rate: {user_metrics.get('retention_rate', 0):.1%}",
                f"Market Position: {await self._get_market_position_summary()}"
            ],
            "period": f"{date_range['start_date'].strftime('%Y-%m-%d')} to {date_range['end_date'].strftime('%Y-%m-%d')}"
        }

    async def _generate_key_metrics(self, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Generate key metrics section"""
        
        metrics = [
            ReportMetrics(
                metric_id="mrr",
                name="Monthly Recurring Revenue",
                value=85000,
                previous_value=78000,
                change_percentage=8.97,
                trend="up",
                target=100000,
                status="on_track",
                visualization_type="metric"
            ),
            ReportMetrics(
                metric_id="arr",
                name="Annual Recurring Revenue",
                value=1020000,
                previous_value=936000,
                change_percentage=8.97,
                trend="up",
                target=1200000,
                status="on_track",
                visualization_type="metric"
            ),
            ReportMetrics(
                metric_id="cac",
                name="Customer Acquisition Cost",
                value=125,
                previous_value=140,
                change_percentage=-10.71,
                trend="down",
                target=100,
                status="improving",
                visualization_type="gauge"
            ),
            ReportMetrics(
                metric_id="ltv",
                name="Customer Lifetime Value",
                value=2500,
                previous_value=2300,
                change_percentage=8.70,
                trend="up",
                target=3000,
                status="on_track",
                visualization_type="metric"
            ),
            ReportMetrics(
                metric_id="churn_rate",
                name="Monthly Churn Rate",
                value=0.05,
                previous_value=0.07,
                change_percentage=-28.57,
                trend="down",
                target=0.03,
                status="improving",
                visualization_type="gauge"
            )
        ]
        
        return {
            "metrics": [asdict(metric) for metric in metrics],
            "summary": "Key business metrics show strong performance with revenue growth accelerating and churn declining.",
            "alerts": []
        }

    async def _generate_visualizations(
        self, visualization_types: List[str], date_range: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """Generate report visualizations"""
        
        visualizations = {}
        
        for viz_type in visualization_types:
            try:
                if viz_type == "revenue_trend":
                    viz_data = await self._create_revenue_trend_chart(date_range)
                elif viz_type == "user_growth_chart":
                    viz_data = await self._create_user_growth_chart(date_range)
                elif viz_type == "key_metrics_dashboard":
                    viz_data = await self._create_metrics_dashboard(date_range)
                elif viz_type == "competitive_analysis":
                    viz_data = await self._create_competitive_chart(date_range)
                else:
                    viz_data = {"type": viz_type, "data": "Visualization data would be generated"}
                
                visualizations[viz_type] = viz_data
                
            except Exception as e:
                self.logger.warning(f"Failed to generate visualization {viz_type}: {e}")
                visualizations[viz_type] = {"error": str(e)}
        
        return visualizations

    async def _create_revenue_trend_chart(self, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Create revenue trend visualization"""
        
        # Generate sample data for demonstration
        dates = pd.date_range(date_range['start_date'], date_range['end_date'], freq='D')
        revenue_data = []
        
        base_revenue = 75000
        for i, date in enumerate(dates):
            # Simulate revenue growth with some variance
            daily_revenue = base_revenue + (i * 150) + (i % 7 * 500)
            revenue_data.append({
                'date': date,
                'revenue': daily_revenue,
                'forecast': daily_revenue * 1.1  # Simple forecast
            })
        
        return {
            "chart_type": "line",
            "title": "Revenue Trend",
            "data": revenue_data,
            "x_axis": "date",
            "y_axis": "revenue",
            "forecast_line": True,
            "format": "currency"
        }

    async def _create_user_growth_chart(self, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Create user growth visualization"""
        
        # Generate sample data
        dates = pd.date_range(date_range['start_date'], date_range['end_date'], freq='D')
        user_data = []
        
        base_users = 42000
        for i, date in enumerate(dates):
            daily_active = base_users + (i * 50) + (i % 7 * 200)
            new_signups = 150 + (i % 7 * 20)
            user_data.append({
                'date': date,
                'active_users': daily_active,
                'new_signups': new_signups,
                'cumulative_users': base_users + (i * 150)
            })
        
        return {
            "chart_type": "multi_line",
            "title": "User Growth Metrics",
            "data": user_data,
            "x_axis": "date",
            "y_axes": ["active_users", "cumulative_users"],
            "secondary_y": "new_signups"
        }

    async def schedule_report_delivery(
        self,
        schedule_id: str,
        recipients: Optional[List[str]] = None,
        formats: Optional[List[DeliveryFormat]] = None
    ) -> bool:
        """Schedule automated report delivery"""
        try:
            if schedule_id not in self.schedules:
                raise ValueError(f"Schedule not found: {schedule_id}")
            
            schedule = self.schedules[schedule_id]
            
            # Override recipients and formats if provided
            if recipients:
                schedule.recipients = recipients
            if formats:
                schedule.formats = formats
            
            # Calculate next delivery time
            schedule.next_delivery = self._calculate_next_delivery(schedule)
            
            self.logger.info(f"Scheduled report delivery: {schedule_id} for {schedule.next_delivery}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule report delivery: {e}")
            return False

    def _calculate_next_delivery(self, schedule: ReportSchedule) -> datetime:
        """Calculate next delivery time for a schedule"""
        now = datetime.now(timezone.utc)
        
        if schedule.frequency == ReportFrequency.DAILY:
            # Next day at specified time
            next_delivery = now.replace(hour=int(schedule.delivery_time.split(':')[0]),
                                      minute=int(schedule.delivery_time.split(':')[1]),
                                      second=0, microsecond=0)
            if next_delivery <= now:
                next_delivery += timedelta(days=1)
        
        elif schedule.frequency == ReportFrequency.WEEKLY:
            # Next week at specified day and time
            next_delivery = now + timedelta(days=7)
            # Implementation would parse "monday_09:00" format
        
        elif schedule.frequency == ReportFrequency.MONTHLY:
            # Next month at specified day and time
            next_delivery = now + timedelta(days=30)
            # Implementation would handle month boundaries
        
        else:
            next_delivery = now + timedelta(days=1)  # Default
        
        return next_delivery

    async def deliver_scheduled_reports(self) -> List[Dict[str, Any]]:
        """Check and deliver any scheduled reports that are due"""
        delivered_reports = []
        current_time = datetime.now(timezone.utc)
        
        for schedule_id, schedule in self.schedules.items():
            if (schedule.is_active and 
                schedule.next_delivery and 
                schedule.next_delivery <= current_time):
                
                try:
                    # Generate report
                    report = await self.generate_report(schedule.report_type)
                    
                    # Deliver to recipients
                    delivery_results = await self._deliver_report(
                        report, schedule.recipients, schedule.formats
                    )
                    
                    delivered_reports.append({
                        "schedule_id": schedule_id,
                        "report_id": report["report_id"],
                        "delivered_at": current_time,
                        "recipients": schedule.recipients,
                        "delivery_results": delivery_results
                    })
                    
                    # Update next delivery time
                    schedule.next_delivery = self._calculate_next_delivery(schedule)
                    
                except Exception as e:
                    self.logger.error(f"Failed to deliver scheduled report {schedule_id}: {e}")
        
        return delivered_reports

    async def _deliver_report(
        self, report: Dict[str, Any], recipients: List[str], formats: List[DeliveryFormat]
    ) -> Dict[str, Any]:
        """Deliver report to recipients in specified formats"""
        delivery_results = {"success": [], "failed": []}
        
        for recipient_id in recipients:
            if recipient_id not in self.recipients:
                delivery_results["failed"].append(f"Unknown recipient: {recipient_id}")
                continue
            
            recipient = self.recipients[recipient_id]
            
            for format_type in formats:
                try:
                    # Format report for delivery
                    formatted_report = await self._format_report(report, format_type)
                    
                    # Send report (implementation would use actual email/delivery service)
                    success = await self._send_report(recipient, formatted_report, format_type)
                    
                    if success:
                        delivery_results["success"].append(f"{recipient_id}:{format_type.value}")
                    else:
                        delivery_results["failed"].append(f"{recipient_id}:{format_type.value}")
                        
                except Exception as e:
                    delivery_results["failed"].append(f"{recipient_id}:{format_type.value} - {str(e)}")
        
        return delivery_results

    async def _format_report(
        self, report: Dict[str, Any], format_type: DeliveryFormat
    ) -> Dict[str, Any]:
        """Format report for specific delivery format"""
        
        if format_type == DeliveryFormat.PDF:
            return await self._generate_pdf_report(report)
        elif format_type == DeliveryFormat.EXCEL:
            return await self._generate_excel_report(report)
        elif format_type == DeliveryFormat.HTML:
            return await self._generate_html_report(report)
        elif format_type == DeliveryFormat.JSON:
            return report  # Already in JSON format
        elif format_type == DeliveryFormat.POWERPOINT:
            return await self._generate_ppt_report(report)
        else:
            return report

    async def _generate_pdf_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF format report"""
        # Implementation would use PDF generation library
        return {
            "format": "pdf",
            "content": "PDF content would be generated here",
            "filename": f"report_{report['report_id']}.pdf"
        }

    async def _generate_excel_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Excel format report"""
        # Implementation would use Excel generation library
        return {
            "format": "excel",
            "content": "Excel content would be generated here",
            "filename": f"report_{report['report_id']}.xlsx"
        }

    async def _send_report(
        self, recipient: ReportRecipient, formatted_report: Dict[str, Any], format_type: DeliveryFormat
    ) -> bool:
        """Send report to recipient (mock implementation)"""
        # Implementation would use actual email service
        self.logger.info(f"Sending {format_type.value} report to {recipient.email}")
        return True

    # Helper methods for data retrieval (mock implementations)
    async def _get_revenue_metrics(self, date_range: Dict[str, datetime]) -> Dict[str, float]:
        """Get revenue metrics for date range"""
        return {
            "total_revenue": 85000,
            "recurring_revenue": 75000,
            "one_time_revenue": 10000,
            "growth_rate": 0.15
        }

    async def _get_user_metrics(self, date_range: Dict[str, datetime]) -> Dict[str, Any]:
        """Get user metrics for date range"""
        return {
            "active_users": 45000,
            "new_users": 3500,
            "retention_rate": 0.82,
            "engagement_score": 0.74
        }

    async def _calculate_growth_metrics(self, date_range: Dict[str, datetime]) -> Dict[str, float]:
        """Calculate growth metrics"""
        return {
            "revenue_growth": 0.15,
            "user_growth": 0.12,
            "engagement_growth": 0.08
        }

    def _generate_short_summary(self, revenue_metrics: Dict, user_metrics: Dict) -> str:
        """Generate short executive summary"""
        return f"""
        Q{datetime.now().month//3 + 1} Performance Summary:
        
        Revenue performance remains strong with ${revenue_metrics['total_revenue']:,} in monthly recurring revenue, 
        representing {revenue_metrics['growth_rate']:.1%} growth. User engagement continues to improve with 
        {user_metrics['active_users']:,} monthly active users and {user_metrics['retention_rate']:.1%} retention rate.
        """

    def _generate_medium_summary(self, revenue_metrics: Dict, user_metrics: Dict) -> str:
        """Generate medium executive summary"""
        return f"""
        Executive Summary - Business Performance Report
        
        Financial Performance:
        Our platform demonstrates continued strong financial performance with monthly recurring revenue 
        reaching ${revenue_metrics['total_revenue']:,}, marking a {revenue_metrics['growth_rate']:.1%} 
        increase from the previous period. Revenue diversification continues with balanced growth across 
        subscription tiers and partnership channels.
        
        User Growth & Engagement:
        User acquisition momentum remains strong with {user_metrics['active_users']:,} monthly active users, 
        while our retention metrics show healthy engagement with {user_metrics['retention_rate']:.1%} user 
        retention rate. User engagement scores indicate strong product-market fit and platform stickiness.
        
        Strategic Position:
        The platform maintains competitive advantages in AI-powered content protection and creator 
        monetization tools, positioning us well for continued growth in the creator economy market.
        """

    def _generate_long_summary(self, revenue_metrics: Dict, user_metrics: Dict, growth_metrics: Dict) -> str:
        """Generate comprehensive executive summary"""
        return f"""
        Comprehensive Executive Summary - Strategic Business Review
        
        Financial Excellence:
        Our financial performance this period demonstrates the strength of our business model and execution 
        capabilities. With monthly recurring revenue of ${revenue_metrics['total_revenue']:,} representing 
        {revenue_metrics['growth_rate']:.1%} growth, we continue to exceed investor expectations while 
        maintaining sustainable unit economics. The revenue mix shows healthy diversification across our 
        subscription tiers, API licensing, and partnership revenue streams.
        
        User Acquisition & Retention:
        User growth metrics reflect strong product-market fit with {user_metrics['active_users']:,} monthly 
        active users and industry-leading retention rates of {user_metrics['retention_rate']:.1%}. Our 
        user acquisition costs remain efficient at $125 per customer, while lifetime value continues to 
        expand to $2,500, maintaining a healthy 20:1 LTV/CAC ratio.
        
        Product & Technology Innovation:
        Continued investment in AI capabilities and user experience improvements drive engagement metrics, 
        with users spending an average of 18.5 minutes per session and completing 4.2 actions per visit. 
        Our collaboration features show 35% adoption rate among active users, creating network effects 
        that strengthen retention.
        
        Market Position & Competitive Landscape:
        The platform maintains differentiated positioning in the creator economy through proprietary AI 
        content protection technology and seamless monetization tools. Market intelligence indicates 
        growing recognition as a category leader, with increasing enterprise interest and partnership 
        opportunities.
        
        Strategic Outlook:
        Based on current performance trends and market opportunities, we remain confident in achieving 
        our targets of $100K monthly recurring revenue and 50K monthly active users by quarter end. 
        Strategic initiatives around enterprise expansion and international markets position us for 
        accelerated growth in upcoming periods.
        """

    async def _get_market_position_summary(self) -> str:
        """Get market position summary"""
        return "Leading position in AI-powered creator tools with 15% market share growth"

    def get_reporting_status(self) -> Dict[str, Any]:
        """Get reporting system status"""
        return {
            "active_schedules": len([s for s in self.schedules.values() if s.is_active]),
            "total_recipients": len(self.recipients),
            "available_templates": len(self.templates),
            "reports_generated": len(self.report_history),
            "next_scheduled_reports": [
                {
                    "schedule_id": schedule_id,
                    "report_type": schedule.report_type.value,
                    "next_delivery": schedule.next_delivery
                }
                for schedule_id, schedule in self.schedules.items()
                if schedule.is_active and schedule.next_delivery
            ]
        }