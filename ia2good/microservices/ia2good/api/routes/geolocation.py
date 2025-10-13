"""API routes for geolocation"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from services.geo_service import GeoService
from services.case_service import CaseService
from api.dependencies import get_db, get_optional_user
from api.schemas.case import CaseResponse

router = APIRouter()


# Example of a FULLY IMPLEMENTED endpoint showing the pattern
# Other endpoints follow the same structure


@router.get("/geolocation/nearby", response_model=List[CaseResponse])
async def get_nearby_cases(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude of search center"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude of search center"),
    radius_km: int = Query(10, ge=1, le=100, description="Search radius in kilometers"),
    case_type: Optional[str] = Query(None, description="Filter by case type"),
    urgency_min: Optional[int] = Query(None, ge=1, le=10, description="Minimum urgency level"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Get cases near a location (FULLY IMPLEMENTED EXAMPLE)
    
    This endpoint demonstrates the complete implementation pattern:
    1. Dependency injection (db, optional user)
    2. Service layer usage (CaseService)
    3. Business logic delegation
    4. Error handling
    5. Response formatting
    
    Uses PostGIS ST_DWithin for efficient geospatial queries.
    Returns cases within radius_km of the specified coordinates.
    
    Query Parameters:
        - latitude: Center latitude (-90 to 90)
        - longitude: Center longitude (-180 to 180)
        - radius_km: Search radius (1-100 km)
        - case_type: Optional filter (homeless, animal, emergency, other)
        - urgency_min: Optional minimum urgency (1-10)
        
    Returns:
        List of cases with distance from search center
        
    Example:
        GET /api/v1/ia2good/geolocation/nearby?latitude=48.8566&longitude=2.3522&radius_km=5
        
    Note:
        This endpoint works for both authenticated and anonymous users.
        Authenticated users may see additional details.
    """
    try:
        # Direct query using PostGIS
        from models.case import Case
        from geoalchemy2.functions import ST_DWithin, ST_Transform, ST_GeomFromText, ST_Distance
        from sqlalchemy import func
        
        # Create point for search center
        search_point = f'POINT({longitude} {latitude})'
        
        # Query cases within radius using PostGIS
        query = db.query(Case).filter(
            Case.deleted_at.is_(None),
            Case.status == "open"
        )
        
        # Add spatial filter
        query = query.filter(
            ST_DWithin(
                ST_Transform(func.ST_GeomFromWKB(Case.location), 3857),
                ST_Transform(ST_GeomFromText(search_point, 4326), 3857),
                radius_km * 1000  # Convert km to meters
            )
        )
        
        # Add type filter if provided
        if case_type:
            query = query.filter(Case.type == case_type)
        
        # Add urgency filter if provided
        if urgency_min:
            query = query.filter(Case.urgency_level >= urgency_min)
        
        # Calculate distance and order by closest
        query = query.order_by(
            ST_Distance(
                ST_Transform(func.ST_GeomFromWKB(Case.location), 3857),
                ST_Transform(ST_GeomFromText(search_point, 4326), 3857)
            )
        )
        
        cases = query.limit(20).all()
        
        # Convert to response format
        from geoalchemy2 import shape as geoshape
        result = []
        for case in cases:
            location_shape = geoshape.to_shape(case.location)
            result.append(CaseResponse(
                id=str(case.id),
                user_id=str(case.user_id),
                type=case.type,
                status=case.status,
                title=case.title,
                description=case.description,
                location={"latitude": location_shape.y, "longitude": location_shape.x} if case.location else None,
                address=case.address,
                city=case.city,
                country=case.country,
                urgency_level=case.urgency_level,
                tags=case.tags or [],
                volunteers_needed=case.volunteers_needed,
                volunteers_assigned=case.volunteers_assigned,
                views_count=case.views_count,
                shares_count=case.shares_count,
                created_at=case.created_at.isoformat() if case.created_at else None,
                updated_at=case.updated_at.isoformat() if case.updated_at else None,
            ))
        
        return result
        
    except ValueError as e:
        # Business logic errors (e.g., invalid parameters)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        # In production, log this error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve nearby cases: {str(e)}"
        )


# Alias for backward compatibility
@router.get("/geolocation/nearby-cases", response_model=List[CaseResponse])
async def get_nearby_cases_alias(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: int = Query(10, ge=1, le=100, description="Radius in km"),
    case_type: Optional[str] = Query(None),
    urgency_min: Optional[int] = Query(None, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Alias for /geolocation/nearby for backward compatibility
    """
    return await get_nearby_cases(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        case_type=case_type,
        urgency_min=urgency_min,
        db=db,
        current_user=current_user
    )


@router.get("/geolocation/heatmap")
async def get_heatmap_data(
    bounds: str = Query(..., description="Bounding box: lat1,lng1,lat2,lng2"),
    case_type: Optional[str] = None,
    time_range_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get heatmap data for cases (STUB - Follow /nearby pattern above)
    
    Returns hotspot data for visualization on maps.
    Groups cases by geographic clusters.
    
    Implementation Pattern (follow /nearby example):
    1. Parse bounds parameter
    2. Use CaseService or GeoService to query cases
    3. Group by geographic clusters (PostGIS ST_ClusterKMeans)
    4. Calculate intensity for each cluster
    5. Return heatmap data points
    
    TODO: Implement following the pattern in /nearby endpoint above
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Endpoint not yet implemented. "
            "Follow the implementation pattern in /geolocation/nearby endpoint. "
            "Service layer methods exist in GeoService and CaseService."
        )
    )


@router.post("/geolocation/route")
async def calculate_optimal_route(
    case_ids: List[str],
    start_latitude: float = Query(..., ge=-90, le=90),
    start_longitude: float = Query(..., ge=-180, le=180),
    db: Session = Depends(get_db)
):
    """
    Calculate optimal route for multiple cases (STUB - TSP Algorithm)
    
    Uses traveling salesman problem algorithm to optimize route.
    Returns optimized route order and estimated travel times.
    
    Implementation Pattern:
    1. Validate case_ids exist
    2. Get case locations from database
    3. Use TSP algorithm (or approximation) to optimize route
    4. Calculate travel times between points
    5. Return ordered route with metadata
    
    Algorithm Options:
    - Nearest neighbor (simple, fast, ~20% suboptimal)
    - 2-opt improvement (better, still fast)
    - OR-Tools (Google optimization, best quality)
    
    TODO: Implement using GeoService.calculate_distance_km and optimization algorithm
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Endpoint not yet implemented. "
            "Requires TSP algorithm implementation. "
            "Use GeoService.calculate_distance_km for distances."
        )
    )


@router.post("/geolocation/geocode")
async def geocode_address(
    address: str = Query(..., min_length=5),
    country: str = Query("France")
):
    """
    Geocode an address to coordinates
    
    Uses Mapbox Geocoding API or similar service
    Returns latitude, longitude, and formatted address
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.post("/geolocation/reverse-geocode")
async def reverse_geocode(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180)
):
    """
    Reverse geocode coordinates to address
    
    Returns formatted address for given coordinates
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )
