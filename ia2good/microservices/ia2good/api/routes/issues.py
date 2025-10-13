"""Issues API routes"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from geoalchemy2.functions import ST_GeomFromText, ST_DWithin, ST_Distance
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from api.dependencies import get_db, get_current_user
from api.schemas.issues import (
    IssueCreate, IssueUpdate, IssueResponse,
    IssueCommentCreate, IssueCommentResponse,
    IssueFollowCreate, IssueFollowResponse,
    IssueResolveCreate, IssueFilters
)
from models.issue import Issue, IssueComment, IssueFollower

router = APIRouter()


def issue_to_dict(issue: Issue) -> dict:
    """Convert Issue model to dict for response"""
    result = {
        'id': issue.id,
        'type': issue.type.value if hasattr(issue.type, 'value') else issue.type,
        'status': issue.status.value if hasattr(issue.status, 'value') else issue.status,
        'severity': issue.severity.value if hasattr(issue.severity, 'value') else issue.severity,
        'title': issue.title,
        'description': issue.description,
        'reported_by': issue.reported_by,
        'volunteer_id': issue.volunteer_id,
        'address': issue.address,
        'media_urls': issue.media_urls or [],
        'media_types': issue.media_types or [],
        'views_count': issue.views_count or 0,
        'followers_count': issue.followers_count or 0,
        'comments_count': issue.comments_count or 0,
        'shares_count': issue.shares_count or 0,
        'tags': issue.tags or [],
        'recommended_to': issue.recommended_to or [],
        'notified_organizations': [str(org) for org in (issue.notified_organizations or [])],
        'notified_authorities': issue.notified_authorities or [],
        'resolved_by': issue.resolved_by,
        'resolved_at': issue.resolved_at,
        'resolution_notes': issue.resolution_notes,
        'resolution_media': issue.resolution_media or [],
        'created_at': issue.created_at,
        'updated_at': issue.updated_at,
    }
    
    # Extract latitude/longitude from PostGIS geometry
    if issue.location:
        from geoalchemy2.shape import to_shape
        point = to_shape(issue.location)
        result['latitude'] = point.y
        result['longitude'] = point.x
    else:
        result['latitude'] = None
        result['longitude'] = None
    
    return result


@router.post("/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_data: IssueCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer un nouveau signalement (issue)
    
    Un volontaire peut signaler un problème avec localisation et médias
    """
    # Helper to get user_id from JWT
    def get_user_id(user_dict):
        return str(user_dict.get("user_id") or user_dict.get("id") or user_dict.get("sub"))
    
    # Create PostGIS geometry from coordinates
    location_wkb = None
    if issue_data.latitude and issue_data.longitude:
        point = Point(issue_data.longitude, issue_data.latitude)
        location_wkb = from_shape(point, srid=4326)
    
    # Create issue
    new_issue = Issue(
        type=issue_data.type,
        severity=issue_data.severity,
        title=issue_data.title,
        description=issue_data.description,
        reported_by=UUID(get_user_id(current_user)),
        location=location_wkb,
        address=issue_data.address,
        media_urls=issue_data.media_urls,
        media_types=issue_data.media_types,
        tags=issue_data.tags,
    )
    
    # Check if user has volunteer profile
    from models.volunteer import VolunteerProfile
    volunteer = db.query(VolunteerProfile).filter(VolunteerProfile.user_id == UUID(get_user_id(current_user))).first()
    if volunteer:
        new_issue.volunteer_id = volunteer.id
    
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    
    return IssueResponse(**issue_to_dict(new_issue))


@router.get("/issues", response_model=List[IssueResponse])
async def list_issues(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: float = Query(10.0, ge=0.1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lister les signalements avec filtres optionnels
    """
    query = db.query(Issue)
    
    # Filters
    if type:
        query = query.filter(Issue.type == type)
    
    if status:
        query = query.filter(Issue.status == status)
    
    if severity:
        query = query.filter(Issue.severity == severity)
    
    if tags:
        # Array overlap operator &&
        query = query.filter(Issue.tags.overlap(tags))
    
    # Geospatial filter
    if latitude and longitude:
        point_wkt = f'POINT({longitude} {latitude})'
        point_geom = ST_GeomFromText(point_wkt, 4326)
        query = query.filter(
            ST_DWithin(Issue.location, point_geom, radius_km * 1000, use_spheroid=True)
        )
    
    # Order by most recent
    query = query.order_by(Issue.created_at.desc())
    
    # Pagination
    issues = query.offset(skip).limit(limit).all()
    
    return [IssueResponse(**issue_to_dict(issue)) for issue in issues]


@router.get("/issues/nearby", response_model=List[IssueResponse])
async def get_nearby_issues(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(5.0, ge=0.1, le=50),
    type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Trouver les signalements à proximité d'une position
    """
    point_wkt = f'POINT({longitude} {latitude})'
    point_geom = ST_GeomFromText(point_wkt, 4326)
    
    query = db.query(Issue).filter(
        Issue.location.isnot(None),
        ST_DWithin(Issue.location, point_geom, radius_km * 1000, use_spheroid=True)
    )
    
    if type:
        query = query.filter(Issue.type == type)
    
    if severity:
        query = query.filter(Issue.severity == severity)
    
    # Order by distance
    query = query.order_by(
        ST_Distance(Issue.location, point_geom, use_spheroid=True)
    ).limit(limit)
    
    issues = query.all()
    return [IssueResponse(**issue_to_dict(issue)) for issue in issues]


@router.get("/issues/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtenir les détails d'un signalement
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Increment views
    issue.views_count = (issue.views_count or 0) + 1
    db.commit()
    
    return IssueResponse(**issue_to_dict(issue))


@router.put("/issues/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: UUID,
    issue_data: IssueUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour un signalement (créateur ou admin uniquement)
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check ownership or admin role
    if str(issue.reported_by) != current_user['id'] and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this issue"
        )
    
    # Update fields
    update_data = issue_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)
    
    issue.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(issue)
    
    return IssueResponse(**issue_to_dict(issue))


@router.post("/issues/{issue_id}/comments", response_model=IssueCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    issue_id: UUID,
    comment_data: IssueCommentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ajouter un commentaire à un signalement
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Create comment
    new_comment = IssueComment(
        issue_id=issue_id,
        user_id=UUID(current_user['id']),
        content=comment_data.content,
        media_urls=comment_data.media_urls,
        is_official='admin' in current_user.get('roles', [])
    )
    
    db.add(new_comment)
    
    # Update comments count
    issue.comments_count = (issue.comments_count or 0) + 1
    
    db.commit()
    db.refresh(new_comment)
    
    return IssueCommentResponse(
        id=new_comment.id,
        issue_id=new_comment.issue_id,
        user_id=new_comment.user_id,
        content=new_comment.content,
        media_urls=new_comment.media_urls or [],
        is_official=new_comment.is_official,
        likes_count=new_comment.likes_count or 0,
        created_at=new_comment.created_at
    )


@router.get("/issues/{issue_id}/comments", response_model=List[IssueCommentResponse])
async def get_comments(
    issue_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Obtenir les commentaires d'un signalement
    """
    comments = db.query(IssueComment).filter(
        IssueComment.issue_id == issue_id
    ).order_by(IssueComment.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        IssueCommentResponse(
            id=comment.id,
            issue_id=comment.issue_id,
            user_id=comment.user_id,
            content=comment.content,
            media_urls=comment.media_urls or [],
            is_official=comment.is_official,
            likes_count=comment.likes_count or 0,
            created_at=comment.created_at
        )
        for comment in comments
    ]


@router.post("/issues/{issue_id}/follow", response_model=IssueFollowResponse, status_code=status.HTTP_201_CREATED)
async def follow_issue(
    issue_id: UUID,
    follow_data: IssueFollowCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Suivre un signalement pour recevoir des notifications
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if already following
    existing = db.query(IssueFollower).filter(
        IssueFollower.issue_id == issue_id,
        IssueFollower.user_id == UUID(current_user['id'])
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this issue"
        )
    
    # Create follower
    new_follower = IssueFollower(
        issue_id=issue_id,
        user_id=UUID(current_user['id']),
        notify_on_update=follow_data.notify_on_update,
        notify_on_comment=follow_data.notify_on_comment,
        notify_on_resolution=follow_data.notify_on_resolution
    )
    
    db.add(new_follower)
    
    # Update followers count
    issue.followers_count = (issue.followers_count or 0) + 1
    
    db.commit()
    db.refresh(new_follower)
    
    return IssueFollowResponse(
        id=new_follower.id,
        issue_id=new_follower.issue_id,
        user_id=new_follower.user_id,
        notify_on_update=new_follower.notify_on_update,
        notify_on_comment=new_follower.notify_on_comment,
        notify_on_resolution=new_follower.notify_on_resolution,
        created_at=new_follower.created_at
    )


@router.delete("/issues/{issue_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_issue(
    issue_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ne plus suivre un signalement
    """
    follower = db.query(IssueFollower).filter(
        IssueFollower.issue_id == issue_id,
        IssueFollower.user_id == UUID(current_user['id'])
    ).first()
    
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this issue"
        )
    
    # Update followers count
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if issue and issue.followers_count > 0:
        issue.followers_count -= 1
    
    db.delete(follower)
    db.commit()


@router.post("/issues/{issue_id}/resolve", response_model=IssueResponse)
async def resolve_issue(
    issue_id: UUID,
    resolve_data: IssueResolveCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marquer un signalement comme résolu (admin, moderator, ou créateur)
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check authorization
    user_roles = current_user.get('roles', [])
    if (str(issue.reported_by) != current_user['id'] and
        'admin' not in user_roles and 'moderator' not in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to resolve this issue"
        )
    
    # Update issue
    issue.status = 'resolved'
    issue.resolved_by = UUID(current_user['id'])
    issue.resolved_at = datetime.utcnow()
    issue.resolution_notes = resolve_data.resolution_notes
    issue.resolution_media = resolve_data.resolution_media
    issue.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(issue)
    
    return IssueResponse(**issue_to_dict(issue))


@router.get("/issues/my/reported", response_model=List[IssueResponse])
async def get_my_issues(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir les signalements créés par l'utilisateur courant
    """
    issues = db.query(Issue).filter(
        Issue.reported_by == UUID(current_user['id'])
    ).order_by(Issue.created_at.desc()).all()
    
    return [IssueResponse(**issue_to_dict(issue)) for issue in issues]


@router.get("/issues/my/following", response_model=List[IssueResponse])
async def get_followed_issues(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir les signalements suivis par l'utilisateur courant
    """
    followers = db.query(IssueFollower).filter(
        IssueFollower.user_id == UUID(current_user['id'])
    ).all()
    
    issue_ids = [f.issue_id for f in followers]
    
    if not issue_ids:
        return []
    
    issues = db.query(Issue).filter(Issue.id.in_(issue_ids)).order_by(Issue.updated_at.desc()).all()
    
    return [IssueResponse(**issue_to_dict(issue)) for issue in issues]
