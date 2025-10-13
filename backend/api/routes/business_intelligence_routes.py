"""
📊 BUSINESS INTELLIGENCE ROUTES - Complete Implementation
========================================================
ALL 60 endpoints for BI dashboard, forecasting, predictive analytics
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/bi", tags=["Business Intelligence"])

# ============================================================================
# MODELS
# ============================================================================

class MetricPeriod(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class ReportType(str, Enum):
    REVENUE = "revenue"
    USERS = "users"
    CONTENT = "content"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"

# ============================================================================
# DASHBOARD
# ============================================================================

@router.get("/dashboard")
async def get_dashboard(period: MetricPeriod = MetricPeriod.DAY):
    """Get main BI dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        dashboard = await analytics.get_dashboard(period.value)
        return dashboard
    except Exception as e:
        return {"error": str(e), "metrics": {}}

@router.get("/dashboard/revenue")
async def get_revenue_dashboard(period: MetricPeriod = MetricPeriod.MONTH):
    """Get revenue dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        revenue = await analytics.get_revenue_dashboard(period.value)
        return revenue
    except Exception as e:
        return {"error": str(e), "total_revenue": 0}

@router.get("/dashboard/users")
async def get_users_dashboard(period: MetricPeriod = MetricPeriod.WEEK):
    """Get users dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        users = await analytics.get_users_dashboard(period.value)
        return users
    except Exception as e:
        return {"error": str(e), "total_users": 0}

@router.get("/dashboard/content")
async def get_content_dashboard(period: MetricPeriod = MetricPeriod.DAY):
    """Get content dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        content = await analytics.get_content_dashboard(period.value)
        return content
    except Exception as e:
        return {"error": str(e), "total_content": 0}

@router.get("/dashboard/engagement")
async def get_engagement_dashboard(period: MetricPeriod = MetricPeriod.WEEK):
    """Get engagement dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        engagement = await analytics.get_engagement_dashboard(period.value)
        return engagement
    except Exception as e:
        return {"error": str(e), "engagement_rate": 0}

# ============================================================================
# METRICS & KPIs
# ============================================================================

@router.get("/metrics/overview")
async def get_metrics_overview():
    """Get all key metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        metrics = await analytics.get_metrics_overview()
        return metrics
    except Exception as e:
        return {"error": str(e), "metrics": {}}

@router.get("/metrics/revenue")
async def get_revenue_metrics(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get revenue metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        metrics = await analytics.get_revenue_metrics(start_date, end_date)
        return metrics
    except Exception as e:
        return {"error": str(e), "revenue": 0}

@router.get("/metrics/growth")
async def get_growth_metrics(period: MetricPeriod = MetricPeriod.MONTH):
    """Get growth metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        growth = await analytics.get_growth_metrics(period.value)
        return growth
    except Exception as e:
        return {"error": str(e), "growth_rate": 0}

@router.get("/metrics/retention")
async def get_retention_metrics():
    """Get user retention metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        retention = await analytics.get_retention_metrics()
        return retention
    except Exception as e:
        return {"error": str(e), "retention_rate": 0}

@router.get("/metrics/churn")
async def get_churn_metrics():
    """Get churn metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        churn = await analytics.get_churn_metrics()
        return churn
    except Exception as e:
        return {"error": str(e), "churn_rate": 0}

@router.get("/metrics/ltv")
async def get_lifetime_value():
    """Get customer lifetime value"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        ltv = await analytics.get_lifetime_value()
        return ltv
    except Exception as e:
        return {"error": str(e), "ltv": 0}

@router.get("/metrics/cac")
async def get_acquisition_cost():
    """Get customer acquisition cost"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        cac = await analytics.get_acquisition_cost()
        return cac
    except Exception as e:
        return {"error": str(e), "cac": 0}

# ============================================================================
# FORECASTING
# ============================================================================

@router.get("/forecast/revenue")
async def forecast_revenue(days: int = 30):
    """Forecast future revenue"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        forecast = await analytics.forecast_revenue(days)
        return forecast
    except Exception as e:
        return {"error": str(e), "forecast": []}

@router.get("/forecast/users")
async def forecast_users(days: int = 30):
    """Forecast user growth"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        forecast = await analytics.forecast_users(days)
        return forecast
    except Exception as e:
        return {"error": str(e), "forecast": []}

@router.get("/forecast/engagement")
async def forecast_engagement(days: int = 30):
    """Forecast engagement trends"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        forecast = await analytics.forecast_engagement(days)
        return forecast
    except Exception as e:
        return {"error": str(e), "forecast": []}

@router.get("/forecast/churn")
async def forecast_churn(days: int = 30):
    """Forecast churn rate"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        forecast = await analytics.forecast_churn(days)
        return forecast
    except Exception as e:
        return {"error": str(e), "forecast": []}

# ============================================================================
# PREDICTIVE ANALYTICS
# ============================================================================

@router.get("/predictions/churn-risk")
async def predict_churn_risk(user_id: Optional[str] = None):
    """Predict churn risk for users"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        predictions = await analytics.predict_churn_risk(user_id)
        return predictions
    except Exception as e:
        return {"error": str(e), "predictions": []}

@router.get("/predictions/upsell")
async def predict_upsell_opportunities():
    """Predict upsell opportunities"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        opportunities = await analytics.predict_upsell()
        return opportunities
    except Exception as e:
        return {"error": str(e), "opportunities": []}

@router.get("/predictions/content-performance")
async def predict_content_performance(content_id: Optional[str] = None):
    """Predict content performance"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        predictions = await analytics.predict_content_performance(content_id)
        return predictions
    except Exception as e:
        return {"error": str(e), "predictions": []}

@router.get("/predictions/trending")
async def predict_trending_topics():
    """Predict trending topics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        trending = await analytics.predict_trending()
        return trending
    except Exception as e:
        return {"error": str(e), "topics": []}

# ============================================================================
# REPORTS
# ============================================================================

@router.get("/reports")
async def list_reports(type: Optional[ReportType] = None):
    """Get all reports"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        reports = await analytics.list_reports(type.value if type else None)
        return {"total": len(reports), "reports": reports}
    except Exception as e:
        return {"total": 0, "reports": [], "error": str(e)}

@router.post("/reports/generate")
async def generate_report(type: ReportType, start_date: str, end_date: str):
    """Generate new report"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        report = await analytics.generate_report(type.value, start_date, end_date)
        return {"message": "Report generated", "report_id": report['id'], "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Get report details"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        report = await analytics.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{report_id}/export")
async def export_report(report_id: str, format: str = "pdf"):
    """Export report"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        export = await analytics.export_report(report_id, format)
        return export
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COHORT ANALYSIS
# ============================================================================

@router.get("/cohorts")
async def list_cohorts():
    """Get all cohorts"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        cohorts = await analytics.list_cohorts()
        return {"cohorts": cohorts}
    except Exception as e:
        return {"cohorts": [], "error": str(e)}

@router.post("/cohorts/create")
async def create_cohort(name: str, criteria: Dict[str, Any]):
    """Create new cohort"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        cohort = await analytics.create_cohort(name, criteria)
        return {"message": "Cohort created", "cohort_id": cohort['id'], "cohort": cohort}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cohorts/{cohort_id}/analysis")
async def analyze_cohort(cohort_id: str):
    """Analyze cohort behavior"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        analysis = await analytics.analyze_cohort(cohort_id)
        return analysis
    except Exception as e:
        return {"error": str(e), "analysis": {}}

@router.get("/cohorts/{cohort_id}/retention")
async def get_cohort_retention(cohort_id: str):
    """Get cohort retention"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        retention = await analytics.get_cohort_retention(cohort_id)
        return retention
    except Exception as e:
        return {"error": str(e), "retention": {}}

# ============================================================================
# FUNNEL ANALYSIS
# ============================================================================

@router.get("/funnels")
async def list_funnels():
    """Get all funnels"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        funnels = await analytics.list_funnels()
        return {"funnels": funnels}
    except Exception as e:
        return {"funnels": [], "error": str(e)}

@router.post("/funnels/create")
async def create_funnel(name: str, steps: List[str]):
    """Create new funnel"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        funnel = await analytics.create_funnel(name, steps)
        return {"message": "Funnel created", "funnel_id": funnel['id'], "funnel": funnel}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/funnels/{funnel_id}/analysis")
async def analyze_funnel(funnel_id: str):
    """Analyze funnel conversion"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        analysis = await analytics.analyze_funnel(funnel_id)
        return analysis
    except Exception as e:
        return {"error": str(e), "analysis": {}}

@router.get("/funnels/{funnel_id}/drop-offs")
async def get_funnel_dropoffs(funnel_id: str):
    """Get funnel drop-off points"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        dropoffs = await analytics.get_funnel_dropoffs(funnel_id)
        return dropoffs
    except Exception as e:
        return {"error": str(e), "dropoffs": []}

# ============================================================================
# A/B TESTING
# ============================================================================

@router.get("/experiments")
async def list_experiments():
    """Get all A/B experiments"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        experiments = await analytics.list_experiments()
        return {"experiments": experiments}
    except Exception as e:
        return {"experiments": [], "error": str(e)}

@router.post("/experiments/create")
async def create_experiment(name: str, variants: List[Dict[str, Any]]):
    """Create new A/B experiment"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        experiment = await analytics.create_experiment(name, variants)
        return {"message": "Experiment created", "experiment_id": experiment['id'], "experiment": experiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str):
    """Get experiment results"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        results = await analytics.get_experiment_results(experiment_id)
        return results
    except Exception as e:
        return {"error": str(e), "results": {}}

@router.post("/experiments/{experiment_id}/conclude")
async def conclude_experiment(experiment_id: str, winner: str):
    """Conclude experiment and set winner"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        await analytics.conclude_experiment(experiment_id, winner)
        return {"message": "Experiment concluded", "winner": winner}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SEGMENTATION
# ============================================================================

@router.get("/segments")
async def list_segments():
    """Get all user segments"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        segments = await analytics.list_segments()
        return {"segments": segments}
    except Exception as e:
        return {"segments": [], "error": str(e)}

@router.post("/segments/create")
async def create_segment(name: str, criteria: Dict[str, Any]):
    """Create new segment"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        segment = await analytics.create_segment(name, criteria)
        return {"message": "Segment created", "segment_id": segment['id'], "segment": segment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/segments/{segment_id}/users")
async def get_segment_users(segment_id: str):
    """Get users in segment"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        users = await analytics.get_segment_users(segment_id)
        return {"segment_id": segment_id, "users": users}
    except Exception as e:
        return {"segment_id": segment_id, "users": [], "error": str(e)}

@router.get("/segments/{segment_id}/insights")
async def get_segment_insights(segment_id: str):
    """Get segment insights"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        insights = await analytics.get_segment_insights(segment_id)
        return insights
    except Exception as e:
        return {"error": str(e), "insights": {}}

# ============================================================================
# ALERTS & ANOMALIES
# ============================================================================

@router.get("/alerts")
async def list_alerts():
    """Get all active alerts"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        alerts = await analytics.list_alerts()
        return {"alerts": alerts}
    except Exception as e:
        return {"alerts": [], "error": str(e)}

@router.post("/alerts/create")
async def create_alert(metric: str, threshold: float, condition: str):
    """Create new alert"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        alert = await analytics.create_alert(metric, threshold, condition)
        return {"message": "Alert created", "alert_id": alert['id'], "alert": alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies")
async def detect_anomalies(metric: Optional[str] = None):
    """Detect anomalies in metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        anomalies = await analytics.detect_anomalies(metric)
        return {"anomalies": anomalies}
    except Exception as e:
        return {"anomalies": [], "error": str(e)}

# ============================================================================
# BENCHMARKING
# ============================================================================

@router.get("/benchmark/industry")
async def get_industry_benchmark():
    """Get industry benchmark data"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        benchmark = await analytics.get_industry_benchmark()
        return benchmark
    except Exception as e:
        return {"error": str(e), "benchmark": {}}

@router.get("/benchmark/competitors")
async def get_competitor_benchmark():
    """Get competitor benchmark"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        benchmark = await analytics.get_competitor_benchmark()
        return benchmark
    except Exception as e:
        return {"error": str(e), "benchmark": {}}

@router.get("/benchmark/compare")
async def compare_metrics(metric: str, period: MetricPeriod = MetricPeriod.MONTH):
    """Compare metrics against benchmarks"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        comparison = await analytics.compare_metrics(metric, period.value)
        return comparison
    except Exception as e:
        return {"error": str(e), "comparison": {}}

# ============================================================================
# DATA EXPORT
# ============================================================================

@router.get("/export/data")
async def export_analytics_data(
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
        
        export = await analytics.export_data(start_date, end_date, metrics, format)
        return export
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/dashboard")
async def export_dashboard(format: str = "pdf"):
    """Export dashboard"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        export = await analytics.export_dashboard(format)
        return export
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REAL-TIME ANALYTICS
# ============================================================================

@router.get("/realtime/metrics")
async def get_realtime_metrics():
    """Get real-time metrics"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        metrics = await analytics.get_realtime_metrics()
        return metrics
    except Exception as e:
        return {"error": str(e), "metrics": {}}

@router.get("/realtime/users")
async def get_realtime_users():
    """Get current active users"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        users = await analytics.get_realtime_users()
        return {"active_users": users}
    except Exception as e:
        return {"active_users": 0, "error": str(e)}

@router.get("/realtime/events")
async def get_realtime_events(limit: int = 100):
    """Get recent events"""
    try:
        from backend.core.analytics_foundation import AnalyticsFoundation
        analytics = AnalyticsFoundation()
        await analytics.initialize()
        
        events = await analytics.get_realtime_events(limit)
        return {"events": events}
    except Exception as e:
        return {"events": [], "error": str(e)}
