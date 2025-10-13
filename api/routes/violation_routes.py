"""
Violation Detection Routes
"""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
async def get_violations():
    """Get all detected violations"""
    violations = [
        {
            "id": "violation_001",
            "content_id": "content_123",
            "platform": "youtube",
            "url": "https://youtube.com/watch?v=example",
            "type": "copyright_infringement",
            "status": "detected",
            "confidence": 98.5,
            "detected_at": "2025-09-04T10:30:00Z"
        },
        {
            "id": "violation_002", 
            "content_id": "content_456",
            "platform": "tiktok",
            "url": "https://tiktok.com/@user/video/example",
            "type": "unauthorized_distribution",
            "status": "takedown_sent",
            "confidence": 95.2,
            "detected_at": "2025-09-04T09:15:00Z"
        }
    ]
    return {"violations": violations, "total": len(violations)}

@router.get("/{violation_id}")
async def get_violation_details(violation_id: str):
    """Get violation details"""
    return {
        "id": violation_id,
        "content_id": "content_123",
        "platform": "youtube",
        "url": "https://youtube.com/watch?v=example",
        "type": "copyright_infringement",
        "status": "resolved",
        "confidence": 98.5,
        "evidence": {
            "fingerprint_match": True,
            "audio_similarity": 98.7,
            "metadata_match": True
        },
        "actions_taken": [
            {"action": "dmca_takedown", "date": "2025-09-04T11:00:00Z"},
            {"action": "content_removed", "date": "2025-09-04T12:30:00Z"}
        ]
    }

__all__ = ["router"]
