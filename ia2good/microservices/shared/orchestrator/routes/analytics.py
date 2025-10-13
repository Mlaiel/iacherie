"""
Analytics API Routes
Aggregated analytics from all modules
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.analytics_service import analytics_service

router = APIRouter()


@router.get("/overview")
async def get_platform_overview():
    """
    Get overall platform analytics
    
    Returns metrics from:
    - MedCare: Consultations, prescriptions
    - IA2GOOD: Volunteers, cases
    - EduVerify: Learners, quizzes, chatrooms
    """
    try:
        overview = await analytics_service.get_platform_overview()
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track/accessibility")
async def track_accessibility_usage(
    feature: str,
    module: str,
    user_id: Optional[str] = None,
):
    """
    Track accessibility feature usage
    
    **Parameters:**
    - feature: screen_reader, captions, tts, visual_alerts
    - module: medcare, ia2good, eduverify
    - user_id: Optional user identifier
    """
    try:
        result = await analytics_service.track_accessibility_usage(
            feature=feature,
            module=module,
            user_id=user_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accessibility/report")
async def get_accessibility_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Generate accessibility usage report
    
    **Query Parameters:**
    - start_date: ISO format (default: 30 days ago)
    - end_date: ISO format (default: today)
    """
    try:
        # Default to last 30 days
        end = datetime.now() if not end_date else datetime.fromisoformat(end_date)
        start = (end - timedelta(days=30)) if not start_date else datetime.fromisoformat(start_date)
        
        report = await analytics_service.get_accessibility_report(
            start_date=start,
            end_date=end,
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
