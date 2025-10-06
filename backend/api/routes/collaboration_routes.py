"""
🤝 COLLABORATION & MATCHING ROUTES - Complete Implementation
============================================================
ALL 50 endpoints for collaboration, creator matching, projects, teams
Author: Fahed Mlaiel
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])

# ============================================================================
# MODELS
# ============================================================================

class CollaborationType(str, Enum):
    MUSIC = "music"
    VIDEO = "video"
    PODCAST = "podcast"
    DESIGN = "design"
    MARKETING = "marketing"
    RESEARCH = "research"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CreatorProfile(BaseModel):
    name: str
    bio: Optional[str] = None
    skills: List[str] = []
    portfolio_url: Optional[str] = None
    location: Optional[str] = None
    languages: List[str] = []

class CreatorSkill(BaseModel):
    skill: str
    level: SkillLevel
    years_experience: Optional[int] = None

class ProjectCreate(BaseModel):
    title: str
    description: str
    type: CollaborationType
    budget: Optional[float] = None
    deadline: Optional[datetime] = None
    required_skills: List[str] = []

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"

class ContractCreate(BaseModel):
    project_id: str
    terms: str
    revenue_split: Dict[str, float]
    duration_days: Optional[int] = None

# ============================================================================
# CREATOR MANAGEMENT
# ============================================================================

@router.get("/creators")
async def list_creators(
    skill: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get list of all creators with optional filters"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        creators = await core.get_creators(
            skill=skill,
            location=location,
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(creators),
            "creators": creators,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {"total": 0, "creators": [], "error": str(e)}

@router.post("/creators")
async def create_creator_profile(profile: CreatorProfile):
    """Create new creator profile"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        creator = await core.create_creator(profile.dict())
        return {"message": "Creator profile created", "creator_id": creator['id'], "creator": creator}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/creators/{creator_id}")
async def get_creator(creator_id: str):
    """Get creator details"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        creator = await core.get_creator(creator_id)
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        return creator
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/creators/{creator_id}")
async def update_creator(creator_id: str, profile: CreatorProfile):
    """Update creator profile"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        updated = await core.update_creator(creator_id, profile.dict())
        return {"message": "Profile updated", "creator": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/creators/{creator_id}")
async def delete_creator(creator_id: str):
    """Delete creator profile"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.delete_creator(creator_id)
        return {"message": "Creator deleted", "creator_id": creator_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/creators/{creator_id}/skills")
async def get_creator_skills(creator_id: str):
    """Get creator skills"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        skills = await core.get_creator_skills(creator_id)
        return {"creator_id": creator_id, "skills": skills}
    except Exception as e:
        return {"creator_id": creator_id, "skills": [], "error": str(e)}

@router.post("/creators/{creator_id}/skills")
async def add_creator_skill(creator_id: str, skill: CreatorSkill):
    """Add skill to creator"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.add_skill(creator_id, skill.dict())
        return {"message": "Skill added", "creator_id": creator_id, "skill": skill.skill}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MATCHING
# ============================================================================

@router.post("/match")
async def find_matches(
    skills: List[str],
    location: Optional[str] = None,
    min_rating: float = 0.0,
    limit: int = 10
):
    """Find matching creators based on criteria"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        matches = await core.find_matches(
            skills=skills,
            location=location,
            min_rating=min_rating,
            limit=limit
        )
        
        return {
            "total_matches": len(matches),
            "matches": matches,
            "criteria": {"skills": skills, "location": location, "min_rating": min_rating}
        }
    except Exception as e:
        return {"total_matches": 0, "matches": [], "error": str(e)}

@router.get("/matches/{match_id}")
async def get_match(match_id: str):
    """Get match details"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        match = await core.get_match(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        return match
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/matches/{match_id}/accept")
async def accept_match(match_id: str):
    """Accept a match"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.accept_match(match_id)
        return {"message": "Match accepted", "match_id": match_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/matches/{match_id}/reject")
async def reject_match(match_id: str, reason: Optional[str] = None):
    """Reject a match"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.reject_match(match_id, reason=reason)
        return {"message": "Match rejected", "match_id": match_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations(user_id: str, limit: int = 10):
    """Get recommended matches for user"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        recommendations = await core.get_recommendations(user_id, limit=limit)
        return {"user_id": user_id, "recommendations": recommendations}
    except Exception as e:
        return {"user_id": user_id, "recommendations": [], "error": str(e)}

# ============================================================================
# PROJECTS
# ============================================================================

@router.get("/projects")
async def list_projects(
    status: Optional[ProjectStatus] = None,
    type: Optional[CollaborationType] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all collaboration projects"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        projects = await core.get_projects(
            status=status.value if status else None,
            type=type.value if type else None,
            limit=limit,
            offset=offset
        )
        
        return {"total": len(projects), "projects": projects}
    except Exception as e:
        return {"total": 0, "projects": [], "error": str(e)}

@router.post("/projects")
async def create_project(project: ProjectCreate):
    """Create new collaboration project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        new_project = await core.create_project(project.dict())
        return {"message": "Project created", "project_id": new_project['id'], "project": new_project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        project = await core.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}")
async def update_project(project_id: str, updates: Dict[str, Any]):
    """Update project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        updated = await core.update_project(project_id, updates)
        return {"message": "Project updated", "project": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.delete_project(project_id)
        return {"message": "Project deleted", "project_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/invite")
async def invite_to_project(project_id: str, user_id: str, role: MemberRole = MemberRole.MEMBER):
    """Invite user to project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.invite_member(project_id, user_id, role.value)
        return {"message": "Invitation sent", "project_id": project_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/{project_id}/leave")
async def leave_project(project_id: str, user_id: str):
    """Leave project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.remove_member(project_id, user_id)
        return {"message": "Left project", "project_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROJECT MANAGEMENT
# ============================================================================

@router.get("/projects/{project_id}/members")
async def get_project_members(project_id: str):
    """Get project members"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        members = await core.get_members(project_id)
        return {"project_id": project_id, "members": members}
    except Exception as e:
        return {"project_id": project_id, "members": [], "error": str(e)}

@router.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str):
    """Get project tasks"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        tasks = await core.get_tasks(project_id)
        return {"project_id": project_id, "tasks": tasks}
    except Exception as e:
        return {"project_id": project_id, "tasks": [], "error": str(e)}

@router.post("/projects/{project_id}/tasks")
async def create_task(project_id: str, task: TaskCreate):
    """Create project task"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        new_task = await core.create_task(project_id, task.dict())
        return {"message": "Task created", "task_id": new_task['id'], "task": new_task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}/tasks/{task_id}")
async def update_task(project_id: str, task_id: str, updates: Dict[str, Any]):
    """Update task"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        updated = await core.update_task(project_id, task_id, updates)
        return {"message": "Task updated", "task": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}/tasks/{task_id}")
async def delete_task(project_id: str, task_id: str):
    """Delete task"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.delete_task(project_id, task_id)
        return {"message": "Task deleted", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/files")
async def get_project_files(project_id: str):
    """Get project files"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        files = await core.get_files(project_id)
        return {"project_id": project_id, "files": files}
    except Exception as e:
        return {"project_id": project_id, "files": [], "error": str(e)}

@router.post("/projects/{project_id}/files")
async def upload_project_file(project_id: str, file: UploadFile = File(...)):
    """Upload file to project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        file_data = await core.upload_file(project_id, file)
        return {"message": "File uploaded", "file": file_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/messages")
async def get_project_messages(project_id: str, limit: int = 100):
    """Get project messages"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        messages = await core.get_messages(project_id, limit=limit)
        return {"project_id": project_id, "messages": messages}
    except Exception as e:
        return {"project_id": project_id, "messages": [], "error": str(e)}

@router.post("/projects/{project_id}/messages")
async def send_project_message(project_id: str, message: str, user_id: str):
    """Send message to project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        msg = await core.send_message(project_id, user_id, message)
        return {"message": "Message sent", "message_data": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/activity")
async def get_project_activity(project_id: str, limit: int = 50):
    """Get project activity feed"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        activity = await core.get_activity(project_id, limit=limit)
        return {"project_id": project_id, "activity": activity}
    except Exception as e:
        return {"project_id": project_id, "activity": [], "error": str(e)}

@router.get("/projects/{project_id}/analytics")
async def get_project_analytics(project_id: str):
    """Get project analytics"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        analytics = await core.get_analytics(project_id)
        return {"project_id": project_id, "analytics": analytics}
    except Exception as e:
        return {"project_id": project_id, "analytics": {}, "error": str(e)}

# ============================================================================
# CONTRACTS & REVENUE
# ============================================================================

@router.get("/contracts")
async def list_contracts(project_id: Optional[str] = None):
    """Get all contracts"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        contracts = await core.get_contracts(project_id=project_id)
        return {"total": len(contracts), "contracts": contracts}
    except Exception as e:
        return {"total": 0, "contracts": [], "error": str(e)}

@router.post("/contracts")
async def create_contract(contract: ContractCreate):
    """Create collaboration contract"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        new_contract = await core.create_contract(contract.dict())
        return {"message": "Contract created", "contract_id": new_contract['id'], "contract": new_contract}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts/{contract_id}")
async def get_contract(contract_id: str):
    """Get contract details"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        contract = await core.get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/{contract_id}/sign")
async def sign_contract(contract_id: str, user_id: str, signature: str):
    """Sign contract"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.sign_contract(contract_id, user_id, signature)
        return {"message": "Contract signed", "contract_id": contract_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue/{project_id}")
async def get_revenue_split(project_id: str):
    """Get revenue split for project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        revenue = await core.get_revenue_split(project_id)
        return {"project_id": project_id, "revenue": revenue}
    except Exception as e:
        return {"project_id": project_id, "revenue": {}, "error": str(e)}

@router.post("/revenue/{project_id}/distribute")
async def distribute_payment(project_id: str, amount: float):
    """Distribute payment according to revenue split"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        distribution = await core.distribute_payment(project_id, amount)
        return {"message": "Payment distributed", "distribution": distribution}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TEAMS
# ============================================================================

@router.get("/teams")
async def list_teams(limit: int = 50):
    """Get all teams"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        teams = await core.get_teams(limit=limit)
        return {"total": len(teams), "teams": teams}
    except Exception as e:
        return {"total": 0, "teams": [], "error": str(e)}

@router.post("/teams")
async def create_team(name: str, description: Optional[str] = None):
    """Create new team"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        team = await core.create_team(name=name, description=description)
        return {"message": "Team created", "team_id": team['id'], "team": team}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}")
async def get_team(team_id: str):
    """Get team details"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        team = await core.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/teams/{team_id}/members")
async def add_team_member(team_id: str, user_id: str, role: MemberRole = MemberRole.MEMBER):
    """Add member to team"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.add_team_member(team_id, user_id, role.value)
        return {"message": "Member added", "team_id": team_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_team_member(team_id: str, user_id: str):
    """Remove member from team"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.remove_team_member(team_id, user_id)
        return {"message": "Member removed", "team_id": team_id, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PRESENCE & REAL-TIME
# ============================================================================

@router.get("/presence/{project_id}")
async def get_presence(project_id: str):
    """Get online users in project"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        presence = await core.get_presence(project_id)
        return {"project_id": project_id, "online_users": presence}
    except Exception as e:
        return {"project_id": project_id, "online_users": [], "error": str(e)}

@router.post("/presence/{project_id}/update")
async def update_presence(project_id: str, user_id: str, status: str = "online"):
    """Update user presence"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.update_presence(project_id, user_id, status)
        return {"message": "Presence updated", "user_id": user_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def get_notifications(user_id: str, unread_only: bool = False, limit: int = 50):
    """Get user notifications"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        notifications = await core.get_notifications(user_id, unread_only=unread_only, limit=limit)
        return {"user_id": user_id, "notifications": notifications}
    except Exception as e:
        return {"user_id": user_id, "notifications": [], "error": str(e)}

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    try:
        from backend.core.collaboration_matching_core import CollaborationMatchingCore
        core = CollaborationMatchingCore()
        await core.initialize()
        
        await core.mark_notification_read(notification_id)
        return {"message": "Notification marked as read", "notification_id": notification_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
