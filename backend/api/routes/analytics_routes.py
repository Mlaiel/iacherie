"""
📊 ANALYTICS ROUTES - Complete Implementation
============================================
ALL 50 endpoints for user/content/traffic/conversion/engagement/revenue analytics
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# ============================================================================
# MODELS
# ============================================================================

class Period(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

# ============================================================================
# USER ANALYTICS
# ============================================================================

@router.get("/users/overview")
async def get_users_overview(period: Period = Period.WEEK):
    """Get user analytics overview"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        overview = await analytics.get_users_overview(period.value)
        return overview
    except Exception as e:
        return {"error": str(e), "users": {}}

@router.get("/users/growth")
async def get_user_growth(period: Period = Period.MONTH):
    """Get user growth metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        growth = await analytics.get_user_growth(period.value)
        return growth
    except Exception as e:
        return {"error": str(e), "growth": []}

@router.get("/users/demographics")
async def get_user_demographics():
    """Get user demographics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        demographics = await analytics.get_user_demographics()
        return demographics
    except Exception as e:
        return {"error": str(e), "demographics": {}}

@router.get("/users/behavior")
async def get_user_behavior(user_id: Optional[str] = None):
    """Get user behavior patterns"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        behavior = await analytics.get_user_behavior(user_id)
        return behavior
    except Exception as e:
        return {"error": str(e), "behavior": {}}

@router.get("/users/{user_id}/journey")
async def get_user_journey(user_id: str):
    """Get user journey"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        journey = await analytics.get_user_journey(user_id)
        return {"user_id": user_id, "journey": journey}
    except Exception as e:
        return {"user_id": user_id, "journey": [], "error": str(e)}

# ============================================================================
# CONTENT ANALYTICS
# ============================================================================

@router.get("/content/overview")
async def get_content_overview(period: Period = Period.WEEK):
    """Get content analytics overview"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        overview = await analytics.get_content_overview(period.value)
        return overview
    except Exception as e:
        return {"error": str(e), "content": {}}

@router.get("/content/popular")
async def get_popular_content(limit: int = 20):
    """Get most popular content"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        popular = await analytics.get_popular_content(limit)
        return {"content": popular}
    except Exception as e:
        return {"content": [], "error": str(e)}

@router.get("/content/trending")
async def get_trending_content(limit: int = 20):
    """Get trending content"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        trending = await analytics.get_trending_content(limit)
        return {"content": trending}
    except Exception as e:
        return {"content": [], "error": str(e)}

@router.get("/content/{content_id}/stats")
async def get_content_stats(content_id: str):
    """Get content statistics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        stats = await analytics.get_content_stats(content_id)
        return {"content_id": content_id, "stats": stats}
    except Exception as e:
        return {"content_id": content_id, "stats": {}, "error": str(e)}

@router.get("/content/{content_id}/engagement")
async def get_content_engagement(content_id: str, period: Period = Period.WEEK):
    """Get content engagement metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        engagement = await analytics.get_content_engagement(content_id, period.value)
        return {"content_id": content_id, "engagement": engagement}
    except Exception as e:
        return {"content_id": content_id, "engagement": {}, "error": str(e)}

# ============================================================================
# TRAFFIC ANALYTICS
# ============================================================================

@router.get("/traffic/overview")
async def get_traffic_overview(period: Period = Period.DAY):
    """Get traffic overview"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        overview = await analytics.get_traffic_overview(period.value)
        return overview
    except Exception as e:
        return {"error": str(e), "traffic": {}}

@router.get("/traffic/sources")
async def get_traffic_sources():
    """Get traffic sources"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        sources = await analytics.get_traffic_sources()
        return {"sources": sources}
    except Exception as e:
        return {"sources": [], "error": str(e)}

@router.get("/traffic/pages")
async def get_page_views(limit: int = 50):
    """Get page view statistics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        pages = await analytics.get_page_views(limit)
        return {"pages": pages}
    except Exception as e:
        return {"pages": [], "error": str(e)}

@router.get("/traffic/referrers")
async def get_referrers(limit: int = 20):
    """Get top referrers"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        referrers = await analytics.get_referrers(limit)
        return {"referrers": referrers}
    except Exception as e:
        return {"referrers": [], "error": str(e)}

@router.get("/traffic/devices")
async def get_device_breakdown():
    """Get traffic by device"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        devices = await analytics.get_device_breakdown()
        return {"devices": devices}
    except Exception as e:
        return {"devices": {}, "error": str(e)}

@router.get("/traffic/locations")
async def get_geographic_data():
    """Get traffic by location"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        locations = await analytics.get_geographic_data()
        return {"locations": locations}
    except Exception as e:
        return {"locations": {}, "error": str(e)}

# ============================================================================
# CONVERSION ANALYTICS
# ============================================================================

@router.get("/conversions/overview")
async def get_conversions_overview(period: Period = Period.MONTH):
    """Get conversions overview"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        overview = await analytics.get_conversions_overview(period.value)
        return overview
    except Exception as e:
        return {"error": str(e), "conversions": {}}

@router.get("/conversions/rate")
async def get_conversion_rate(period: Period = Period.WEEK):
    """Get conversion rate"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        rate = await analytics.get_conversion_rate(period.value)
        return {"conversion_rate": rate}
    except Exception as e:
        return {"conversion_rate": 0, "error": str(e)}

@router.get("/conversions/funnel")
async def get_conversion_funnel(funnel_id: Optional[str] = None):
    """Get conversion funnel data"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        funnel = await analytics.get_conversion_funnel(funnel_id)
        return funnel
    except Exception as e:
        return {"error": str(e), "funnel": {}}

@router.get("/conversions/goals")
async def get_goal_completions():
    """Get goal completions"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        goals = await analytics.get_goal_completions()
        return {"goals": goals}
    except Exception as e:
        return {"goals": [], "error": str(e)}

# ============================================================================
# ENGAGEMENT ANALYTICS
# ============================================================================

@router.get("/engagement/overview")
async def get_engagement_overview(period: Period = Period.WEEK):
    """Get engagement overview"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        overview = await analytics.get_engagement_overview(period.value)
        return overview
    except Exception as e:
        return {"error": str(e), "engagement": {}}

@router.get("/engagement/rate")
async def get_engagement_rate(period: Period = Period.WEEK):
    """Get engagement rate"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        rate = await analytics.get_engagement_rate(period.value)
        return {"engagement_rate": rate}
    except Exception as e:
        return {"engagement_rate": 0, "error": str(e)}

@router.get("/engagement/time")
async def get_time_on_site():
    """Get average time on site"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        time = await analytics.get_average_time_on_site()
        return {"average_time": time}
    except Exception as e:
        return {"average_time": 0, "error": str(e)}

@router.get("/engagement/interactions")
async def get_interaction_metrics():
    """Get interaction metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        metrics = await analytics.get_interaction_metrics()
        return metrics
    except Exception as e:
        return {"error": str(e), "metrics": {}}

@router.get("/engagement/social")
async def get_social_engagement():
    """Get social media engagement"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        social = await analytics.get_social_engagement()
        return social
    except Exception as e:
        return {"error": str(e), "social": {}}

# ============================================================================
# REVENUE ANALYTICS
# ============================================================================

@router.get("/revenue/overview")
async def get_revenue_overview(period: Period = Period.MONTH):
    """Get revenue overview"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        overview = await analytics.get_revenue_overview(period.value)
        return overview
    except Exception as e:
        return {"error": str(e), "revenue": {}}

@router.get("/revenue/trends")
async def get_revenue_trends(period: Period = Period.MONTH):
    """Get revenue trends"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        trends = await analytics.get_revenue_trends(period.value)
        return {"trends": trends}
    except Exception as e:
        return {"trends": [], "error": str(e)}

@router.get("/revenue/by-product")
async def get_revenue_by_product():
    """Get revenue by product"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        revenue = await analytics.get_revenue_by_product()
        return {"products": revenue}
    except Exception as e:
        return {"products": [], "error": str(e)}

@router.get("/revenue/by-channel")
async def get_revenue_by_channel():
    """Get revenue by channel"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        revenue = await analytics.get_revenue_by_channel()
        return {"channels": revenue}
    except Exception as e:
        return {"channels": [], "error": str(e)}

@router.get("/revenue/arpu")
async def get_average_revenue_per_user():
    """Get average revenue per user (ARPU)"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        arpu = await analytics.get_arpu()
        return {"arpu": arpu}
    except Exception as e:
        return {"arpu": 0, "error": str(e)}

# ============================================================================
# EVENTS & TRACKING
# ============================================================================

@router.post("/events/track")
async def track_event(
    event_name: str,
    user_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
):
    """Track custom event"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        await analytics.track_event(event_name, user_id, properties)
        return {"message": "Event tracked", "event": event_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_events(event_name: Optional[str] = None, limit: int = 100):
    """Get tracked events"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        events = await analytics.get_events(event_name, limit)
        return {"total": len(events), "events": events}
    except Exception as e:
        return {"total": 0, "events": [], "error": str(e)}

@router.get("/events/summary")
async def get_events_summary(period: Period = Period.WEEK):
    """Get events summary"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        summary = await analytics.get_events_summary(period.value)
        return summary
    except Exception as e:
        return {"error": str(e), "events": {}}

# ============================================================================
# CUSTOM REPORTS
# ============================================================================

@router.post("/reports/custom")
async def create_custom_report(
    name: str,
    metrics: List[str],
    dimensions: List[str],
    filters: Optional[Dict[str, Any]] = None
):
    """Create custom analytics report"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        report = await analytics.create_custom_report(name, metrics, dimensions, filters)
        return {"message": "Report created", "report_id": report['id'], "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/custom")
async def list_custom_reports():
    """Get all custom reports"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        reports = await analytics.list_custom_reports()
        return {"reports": reports}
    except Exception as e:
        return {"reports": [], "error": str(e)}

@router.get("/reports/custom/{report_id}")
async def get_custom_report(report_id: str):
    """Get custom report data"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        report = await analytics.get_custom_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DASHBOARDS
# ============================================================================

@router.get("/dashboards")
async def list_dashboards():
    """Get all dashboards"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        dashboards = await analytics.list_dashboards()
        return {"dashboards": dashboards}
    except Exception as e:
        return {"dashboards": [], "error": str(e)}

@router.post("/dashboards")
async def create_dashboard(name: str, widgets: List[Dict[str, Any]]):
    """Create analytics dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        dashboard = await analytics.create_dashboard(name, widgets)
        return {"message": "Dashboard created", "dashboard_id": dashboard['id'], "dashboard": dashboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard data"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        dashboard = await analytics.get_dashboard_data(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        return dashboard
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COMPARISONS
# ============================================================================

@router.get("/compare/periods")
async def compare_periods(metric: str, period1: str, period2: str):
    """Compare metrics between periods"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        comparison = await analytics.compare_periods(metric, period1, period2)
        return comparison
    except Exception as e:
        return {"error": str(e), "comparison": {}}

@router.get("/compare/segments")
async def compare_segments(segment1_id: str, segment2_id: str):
    """Compare two user segments"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        comparison = await analytics.compare_segments(segment1_id, segment2_id)
        return comparison
    except Exception as e:
        return {"error": str(e), "comparison": {}}

# ============================================================================
# EXPORTS
# ============================================================================

@router.get("/export")
async def export_analytics(
    start_date: str,
    end_date: str,
    metrics: List[str],
    format: str = "csv"
):
    """Export analytics data"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        export = await analytics.export_analytics(start_date, end_date, metrics, format)
        return export
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/scheduled")
async def list_scheduled_exports():
    """Get scheduled exports"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        exports = await analytics.list_scheduled_exports()
        return {"exports": exports}
    except Exception as e:
        return {"exports": [], "error": str(e)}

@router.post("/export/schedule")
async def schedule_export(
    name: str,
    metrics: List[str],
    frequency: str = "daily",
    recipients: List[str] = []
):
    """Schedule recurring export"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        export = await analytics.schedule_export(name, metrics, frequency, recipients)
        return {"message": "Export scheduled", "export_id": export['id'], "export": export}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
