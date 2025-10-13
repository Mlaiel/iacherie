"""Events API routes"""
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
from api.schemas.events import (
    EventCreate, EventUpdate, EventResponse,
    EventParticipantCreate, EventParticipantUpdate, EventParticipantResponse,
    EventUpdateCreate, EventUpdateResponse,
    EventCheckInCreate, EventImpactUpdate, EventFilters
)
from models.event import Event, EventParticipant
from models.event import EventUpdate as EventUpdateModel

router = APIRouter()


def event_to_dict(event: Event) -> dict:
    """Convert Event model to dict for response"""
    result = {
        'id': event.id,
        'type': event.type.value if hasattr(event.type, 'value') else event.type,
        'status': event.status.value if hasattr(event.status, 'value') else event.status,
        'title': event.title,
        'description': event.description,
        'objectives': event.objectives,
        'organizer_id': event.organizer_id,
        'co_organizers': event.co_organizers or [],
        'address': event.address,
        'venue_name': event.venue_name,
        'start_date': event.start_date,
        'end_date': event.end_date,
        'registration_deadline': event.registration_deadline,
        'capacity': event.capacity,
        'participants_count': event.participants_count or 0,
        'checked_in_count': event.checked_in_count or 0,
        'min_participants': event.min_participants,
        'cover_image': event.cover_image,
        'images': event.images or [],
        'videos': event.videos or [],
        'photos_after': event.photos_after or [],
        'required_skills': event.required_skills or [],
        'age_minimum': event.age_minimum,
        'equipment_needed': event.equipment_needed or [],
        'attendance_count': event.attendance_count or 0,
        'impact_summary': event.impact_summary,
        'impact_metrics': event.impact_metrics or {},
        'tags': event.tags or [],
        'created_at': event.created_at,
        'updated_at': event.updated_at,
        'published_at': event.published_at,
    }
    
    # Extract latitude/longitude from PostGIS geometry
    if event.location:
        from geoalchemy2.shape import to_shape
        point = to_shape(event.location)
        result['latitude'] = point.y
        result['longitude'] = point.x
    else:
        result['latitude'] = None
        result['longitude'] = None
    
    return result


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer un nouvel événement (organisations, admins, ou volunteers vérifiés)
    """
    # Check if user can create events
    user_roles = current_user.get('roles', [])
    if 'organization' not in user_roles and 'admin' not in user_roles and 'volunteer' not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations, admins, or volunteers can create events"
        )
    
    # Create PostGIS geometry from coordinates
    location_wkb = None
    if event_data.latitude and event_data.longitude:
        point = Point(event_data.longitude, event_data.latitude)
        location_wkb = from_shape(point, srid=4326)
    
    # Create event
    new_event = Event(
        type=event_data.type,
        title=event_data.title,
        description=event_data.description,
        objectives=event_data.objectives,
        organizer_id=UUID(current_user['id']),
        co_organizers=event_data.co_organizers,
        location=location_wkb,
        address=event_data.address,
        venue_name=event_data.venue_name,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        registration_deadline=event_data.registration_deadline,
        capacity=event_data.capacity,
        min_participants=event_data.min_participants,
        cover_image=event_data.cover_image,
        images=event_data.images,
        videos=event_data.videos,
        required_skills=event_data.required_skills,
        age_minimum=event_data.age_minimum,
        equipment_needed=event_data.equipment_needed,
        tags=event_data.tags,
        status='draft'
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return EventResponse(**event_to_dict(new_event))


@router.get("/events", response_model=List[EventResponse])
async def list_events(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    start_date_after: Optional[datetime] = Query(None),
    start_date_before: Optional[datetime] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: float = Query(10.0, ge=0.1, le=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lister les événements avec filtres optionnels
    """
    query = db.query(Event)
    
    # Only show published events (unless admin)
    query = query.filter(Event.status.in_(['published', 'ongoing', 'completed']))
    
    # Filters
    if type:
        query = query.filter(Event.type == type)
    
    if status:
        query = query.filter(Event.status == status)
    
    if tags:
        query = query.filter(Event.tags.overlap(tags))
    
    if start_date_after:
        query = query.filter(Event.start_date >= start_date_after)
    
    if start_date_before:
        query = query.filter(Event.start_date <= start_date_before)
    
    # Geospatial filter
    if latitude and longitude:
        point_wkt = f'POINT({longitude} {latitude})'
        point_geom = ST_GeomFromText(point_wkt, 4326)
        query = query.filter(
            ST_DWithin(Event.location, point_geom, radius_km * 1000, use_spheroid=True)
        )
    
    # Order by start date
    query = query.order_by(Event.start_date.asc())
    
    # Pagination
    events = query.offset(skip).limit(limit).all()
    
    return [EventResponse(**event_to_dict(event)) for event in events]


@router.get("/events/nearby", response_model=List[EventResponse])
async def get_nearby_events(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(5.0, ge=0.1, le=50),
    type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Trouver les événements à proximité d'une position
    """
    point_wkt = f'POINT({longitude} {latitude})'
    point_geom = ST_GeomFromText(point_wkt, 4326)
    
    query = db.query(Event).filter(
        Event.location.isnot(None),
        Event.status.in_(['published', 'ongoing']),
        ST_DWithin(Event.location, point_geom, radius_km * 1000, use_spheroid=True)
    )
    
    if type:
        query = query.filter(Event.type == type)
    
    # Order by distance
    query = query.order_by(
        ST_Distance(Event.location, point_geom, use_spheroid=True)
    ).limit(limit)
    
    events = query.all()
    return [EventResponse(**event_to_dict(event)) for event in events]


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtenir les détails d'un événement
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return EventResponse(**event_to_dict(event))


@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour un événement (organisateur ou co-organisateurs uniquement)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check ownership
    user_id = UUID(current_user['id'])
    if (event.organizer_id != user_id and
        user_id not in (event.co_organizers or []) and
        'admin' not in current_user.get('roles', [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this event"
        )
    
    # Update fields
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    
    return EventResponse(**event_to_dict(event))


@router.put("/events/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publier un événement (le rendre visible publiquement)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check ownership
    user_id = UUID(current_user['id'])
    if event.organizer_id != user_id and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this event"
        )
    
    event.status = 'published'
    event.published_at = datetime.utcnow()
    event.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(event)
    
    return EventResponse(**event_to_dict(event))


@router.post("/events/{event_id}/register", response_model=EventParticipantResponse, status_code=status.HTTP_201_CREATED)
async def register_for_event(
    event_id: UUID,
    participant_data: EventParticipantCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    S'inscrire à un événement
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.status not in ['published', 'ongoing']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register for this event"
        )
    
    # Check capacity
    if event.capacity and event.participants_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is full"
        )
    
    # Check if already registered
    existing = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == UUID(current_user['id'])
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for this event"
        )
    
    # Create participant
    new_participant = EventParticipant(
        event_id=event_id,
        user_id=UUID(current_user['id']),
        status='registered',
        role=participant_data.role,
        tasks_assigned=participant_data.tasks_assigned
    )
    
    db.add(new_participant)
    
    # Update participants count
    event.participants_count = (event.participants_count or 0) + 1
    
    db.commit()
    db.refresh(new_participant)
    
    return EventParticipantResponse(
        id=new_participant.id,
        event_id=new_participant.event_id,
        user_id=new_participant.user_id,
        status=new_participant.status.value if hasattr(new_participant.status, 'value') else new_participant.status,
        role=new_participant.role,
        tasks_assigned=new_participant.tasks_assigned or [],
        checked_in=new_participant.checked_in,
        checked_in_at=new_participant.checked_in_at,
        rating=new_participant.rating,
        feedback=new_participant.feedback,
        registered_at=new_participant.registered_at
    )


@router.get("/events/{event_id}/participants", response_model=List[EventParticipantResponse])
async def get_event_participants(
    event_id: UUID,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtenir la liste des participants d'un événement
    """
    query = db.query(EventParticipant).filter(EventParticipant.event_id == event_id)
    
    if status:
        query = query.filter(EventParticipant.status == status)
    
    participants = query.order_by(EventParticipant.registered_at.desc()).all()
    
    return [
        EventParticipantResponse(
            id=p.id,
            event_id=p.event_id,
            user_id=p.user_id,
            status=p.status.value if hasattr(p.status, 'value') else p.status,
            role=p.role,
            tasks_assigned=p.tasks_assigned or [],
            checked_in=p.checked_in,
            checked_in_at=p.checked_in_at,
            rating=p.rating,
            feedback=p.feedback,
            registered_at=p.registered_at
        )
        for p in participants
    ]


@router.post("/events/{event_id}/checkin", response_model=EventParticipantResponse)
async def checkin_to_event(
    event_id: UUID,
    checkin_data: EventCheckInCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check-in à un événement (participant lui-même ou organisateur)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Determine who to check-in
    target_user_id = checkin_data.user_id if checkin_data.user_id else UUID(current_user['id'])
    
    # If checking in someone else, must be organizer
    if target_user_id != UUID(current_user['id']):
        if event.organizer_id != UUID(current_user['id']) and 'admin' not in current_user.get('roles', []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organizers can check-in other participants"
            )
    
    # Find participant
    participant = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == target_user_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    if participant.checked_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in"
        )
    
    # Check-in
    participant.checked_in = True
    participant.checked_in_at = datetime.utcnow()
    participant.status = 'attended'
    
    # Update event checked-in count
    event.checked_in_count = (event.checked_in_count or 0) + 1
    
    db.commit()
    db.refresh(participant)
    
    return EventParticipantResponse(
        id=participant.id,
        event_id=participant.event_id,
        user_id=participant.user_id,
        status=participant.status.value if hasattr(participant.status, 'value') else participant.status,
        role=participant.role,
        tasks_assigned=participant.tasks_assigned or [],
        checked_in=participant.checked_in,
        checked_in_at=participant.checked_in_at,
        rating=participant.rating,
        feedback=participant.feedback,
        registered_at=participant.registered_at
    )


@router.post("/events/{event_id}/updates", response_model=EventUpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_event_update(
    event_id: UUID,
    update_data: EventUpdateCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Poster une annonce pour un événement (organisateur uniquement)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check authorization
    user_id = UUID(current_user['id'])
    if event.organizer_id != user_id and user_id not in (event.co_organizers or []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizers can post updates"
        )
    
    # Create update
    new_update = EventUpdateModel(
        event_id=event_id,
        author_id=user_id,
        title=update_data.title,
        content=update_data.content,
        media_urls=update_data.media_urls,
        update_type=update_data.update_type,
        notify_participants=update_data.notify_participants
    )
    
    db.add(new_update)
    db.commit()
    db.refresh(new_update)
    
    return EventUpdateResponse(
        id=new_update.id,
        event_id=new_update.event_id,
        author_id=new_update.author_id,
        title=new_update.title,
        content=new_update.content,
        media_urls=new_update.media_urls or [],
        update_type=new_update.update_type,
        notify_participants=new_update.notify_participants,
        created_at=new_update.created_at
    )


@router.get("/events/{event_id}/updates", response_model=List[EventUpdateResponse])
async def get_event_updates(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtenir les annonces d'un événement
    """
    updates = db.query(EventUpdateModel).filter(
        EventUpdateModel.event_id == event_id
    ).order_by(EventUpdateModel.created_at.desc()).all()
    
    return [
        EventUpdateResponse(
            id=u.id,
            event_id=u.event_id,
            author_id=u.author_id,
            title=u.title,
            content=u.content,
            media_urls=u.media_urls or [],
            update_type=u.update_type,
            notify_participants=u.notify_participants,
            created_at=u.created_at
        )
        for u in updates
    ]


@router.put("/events/{event_id}/impact", response_model=EventResponse)
async def update_event_impact(
    event_id: UUID,
    impact_data: EventImpactUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour l'impact de l'événement après réalisation (organisateur uniquement)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check authorization
    user_id = UUID(current_user['id'])
    if event.organizer_id != user_id and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizers can update impact"
        )
    
    # Update impact
    event.impact_summary = impact_data.impact_summary
    event.impact_metrics = impact_data.impact_metrics
    event.photos_after = impact_data.photos_after
    event.status = 'completed'
    event.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(event)
    
    return EventResponse(**event_to_dict(event))


@router.get("/events/my/organized", response_model=List[EventResponse])
async def get_my_organized_events(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir les événements organisés par l'utilisateur courant
    """
    user_id = UUID(current_user['id'])
    
    events = db.query(Event).filter(
        or_(
            Event.organizer_id == user_id,
            Event.co_organizers.contains([user_id])
        )
    ).order_by(Event.start_date.desc()).all()
    
    return [EventResponse(**event_to_dict(event)) for event in events]


@router.get("/events/my/participating", response_model=List[EventResponse])
async def get_my_participating_events(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtenir les événements auxquels l'utilisateur participe
    """
    participants = db.query(EventParticipant).filter(
        EventParticipant.user_id == UUID(current_user['id'])
    ).all()
    
    event_ids = [p.event_id for p in participants]
    
    if not event_ids:
        return []
    
    events = db.query(Event).filter(Event.id.in_(event_ids)).order_by(Event.start_date.asc()).all()
    
    return [EventResponse(**event_to_dict(event)) for event in events]
