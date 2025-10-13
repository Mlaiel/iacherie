"""
🎮 GAMIFICATION ROUTES - Complete Implementation
===============================================
ALL 25 endpoints for stats, badges, achievements, leaderboard, quests
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

router = APIRouter(prefix="/gamification", tags=["Gamification"])

# ============================================================================
# USER STATS & XP
# ============================================================================

@router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user gamification stats"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        stats = await engine.get_user_stats(user_id)
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        return {"user_id": user_id, "stats": {}, "error": str(e)}

@router.get("/users/{user_id}/xp")
async def get_user_xp(user_id: str):
    """Get user XP and level"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        xp = await engine.get_user_xp(user_id)
        return {"user_id": user_id, "xp": xp}
    except Exception as e:
        return {"user_id": user_id, "xp": 0, "level": 1, "error": str(e)}

@router.post("/users/{user_id}/xp/add")
async def add_xp(user_id: str, amount: int, reason: str):
    """Add XP to user"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        result = await engine.add_xp(user_id, amount, reason)
        return {"message": "XP added", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/level")
async def get_user_level(user_id: str):
    """Get user level"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        level = await engine.get_user_level(user_id)
        return {"user_id": user_id, "level": level}
    except Exception as e:
        return {"user_id": user_id, "level": 1, "error": str(e)}

# ============================================================================
# BADGES
# ============================================================================

@router.get("/badges")
async def list_badges():
    """Get all badges"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        badges = await engine.list_badges()
        return {"total": len(badges), "badges": badges}
    except Exception as e:
        return {"total": 0, "badges": [], "error": str(e)}

@router.get("/users/{user_id}/badges")
async def get_user_badges(user_id: str):
    """Get user badges"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        badges = await engine.get_user_badges(user_id)
        return {"user_id": user_id, "badges": badges}
    except Exception as e:
        return {"user_id": user_id, "badges": [], "error": str(e)}

@router.post("/users/{user_id}/badges/{badge_id}/award")
async def award_badge(user_id: str, badge_id: str):
    """Award badge to user"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        await engine.award_badge(user_id, badge_id)
        return {"message": "Badge awarded", "user_id": user_id, "badge_id": badge_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ACHIEVEMENTS
# ============================================================================

@router.get("/achievements")
async def list_achievements():
    """Get all achievements"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        achievements = await engine.list_achievements()
        return {"total": len(achievements), "achievements": achievements}
    except Exception as e:
        return {"total": 0, "achievements": [], "error": str(e)}

@router.get("/users/{user_id}/achievements")
async def get_user_achievements(user_id: str):
    """Get user achievements"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        achievements = await engine.get_user_achievements(user_id)
        return {"user_id": user_id, "achievements": achievements}
    except Exception as e:
        return {"user_id": user_id, "achievements": [], "error": str(e)}

@router.post("/users/{user_id}/achievements/{achievement_id}/unlock")
async def unlock_achievement(user_id: str, achievement_id: str):
    """Unlock achievement"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        result = await engine.unlock_achievement(user_id, achievement_id)
        return {"message": "Achievement unlocked", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/achievements/progress")
async def get_achievement_progress(user_id: str):
    """Get achievement progress"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        progress = await engine.get_achievement_progress(user_id)
        return {"user_id": user_id, "progress": progress}
    except Exception as e:
        return {"user_id": user_id, "progress": {}, "error": str(e)}

# ============================================================================
# LEADERBOARD
# ============================================================================

@router.get("/leaderboard/global")
async def get_global_leaderboard(limit: int = 100):
    """Get global leaderboard"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        leaderboard = await engine.get_global_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        return {"leaderboard": [], "error": str(e)}

@router.get("/leaderboard/weekly")
async def get_weekly_leaderboard(limit: int = 50):
    """Get weekly leaderboard"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        leaderboard = await engine.get_weekly_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        return {"leaderboard": [], "error": str(e)}

@router.get("/leaderboard/monthly")
async def get_monthly_leaderboard(limit: int = 50):
    """Get monthly leaderboard"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        leaderboard = await engine.get_monthly_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        return {"leaderboard": [], "error": str(e)}

@router.get("/leaderboard/users/{user_id}/rank")
async def get_user_rank(user_id: str):
    """Get user rank on leaderboard"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        rank = await engine.get_user_rank(user_id)
        return {"user_id": user_id, "rank": rank}
    except Exception as e:
        return {"user_id": user_id, "rank": None, "error": str(e)}

# ============================================================================
# QUESTS
# ============================================================================

@router.get("/quests")
async def list_quests():
    """Get all quests"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        quests = await engine.list_quests()
        return {"total": len(quests), "quests": quests}
    except Exception as e:
        return {"total": 0, "quests": [], "error": str(e)}

@router.get("/users/{user_id}/quests")
async def get_user_quests(user_id: str):
    """Get user active quests"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        quests = await engine.get_user_quests(user_id)
        return {"user_id": user_id, "quests": quests}
    except Exception as e:
        return {"user_id": user_id, "quests": [], "error": str(e)}

@router.post("/users/{user_id}/quests/{quest_id}/start")
async def start_quest(user_id: str, quest_id: str):
    """Start quest"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        await engine.start_quest(user_id, quest_id)
        return {"message": "Quest started", "quest_id": quest_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/quests/{quest_id}/complete")
async def complete_quest(user_id: str, quest_id: str):
    """Complete quest"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        rewards = await engine.complete_quest(user_id, quest_id)
        return {"message": "Quest completed", "rewards": rewards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/quests/{quest_id}/progress")
async def get_quest_progress(user_id: str, quest_id: str):
    """Get quest progress"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        progress = await engine.get_quest_progress(user_id, quest_id)
        return {"user_id": user_id, "quest_id": quest_id, "progress": progress}
    except Exception as e:
        return {"user_id": user_id, "quest_id": quest_id, "progress": {}, "error": str(e)}

# ============================================================================
# REWARDS & POINTS
# ============================================================================

@router.get("/users/{user_id}/points")
async def get_user_points(user_id: str):
    """Get user points"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        points = await engine.get_user_points(user_id)
        return {"user_id": user_id, "points": points}
    except Exception as e:
        return {"user_id": user_id, "points": 0, "error": str(e)}

@router.post("/users/{user_id}/rewards/claim")
async def claim_reward(user_id: str, reward_id: str):
    """Claim reward"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        await engine.claim_reward(user_id, reward_id)
        return {"message": "Reward claimed", "reward_id": reward_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/rewards")
async def get_user_rewards(user_id: str):
    """Get user rewards"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        rewards = await engine.get_user_rewards(user_id)
        return {"user_id": user_id, "rewards": rewards}
    except Exception as e:
        return {"user_id": user_id, "rewards": [], "error": str(e)}

# ============================================================================
# EVENTS & TRACKING
# ============================================================================

@router.post("/events/track")
async def track_event(user_id: str, event_type: str, data: Optional[Dict[str, Any]] = None):
    """Track gamification event"""
    try:
        from backend.gamification.gamification_engine import GamificationEngine
        engine = GamificationEngine()
        await engine.initialize()
        
        result = await engine.track_event(user_id, event_type, data)
        return {"message": "Event tracked", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
