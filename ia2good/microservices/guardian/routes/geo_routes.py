"""
Guardian Geo Routes - Real-time Map and Location Tracking
Carte géographique en temps réel pour missions et volontaires
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json

router = APIRouter()

# Models
class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    timestamp: Optional[datetime] = None

class MissionLocation(BaseModel):
    mission_id: int
    location: Location
    status: str = "active"
    volunteers_count: int = 0
    category: str

class VolunteerLocation(BaseModel):
    volunteer_id: int
    location: Location
    active: bool = True
    mission_id: Optional[int] = None

class GeoRegion(BaseModel):
    name: str
    bounds: Dict[str, float]  # {north, south, east, west}
    missions_count: int = 0
    volunteers_count: int = 0

class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    intensity: float

# In-memory storage for real-time tracking
active_missions_locations: Dict[int, MissionLocation] = {}
active_volunteers_locations: Dict[int, VolunteerLocation] = {}
active_websocket_connections: List[WebSocket] = []

# ============================================================================
# MISSION LOCATIONS
# ============================================================================

@router.post("/missions/{mission_id}/location")
def set_mission_location(mission_id: int, location: Location, category: str = "humanitarian"):
    """Définir la localisation d'une mission"""
    mission_loc = MissionLocation(
        mission_id=mission_id,
        location=location,
        status="active",
        category=category
    )
    active_missions_locations[mission_id] = mission_loc
    
    # Broadcast to all connected clients
    broadcast_update({
        "type": "mission_location_update",
        "data": mission_loc.dict()
    })
    
    return {
        "success": True,
        "mission_id": mission_id,
        "location": location.dict()
    }

@router.get("/missions/locations")
def get_all_mission_locations():
    """Obtenir toutes les localisations de missions"""
    return {
        "success": True,
        "total": len(active_missions_locations),
        "missions": [m.dict() for m in active_missions_locations.values()]
    }

@router.get("/missions/{mission_id}/location")
def get_mission_location(mission_id: int):
    """Obtenir la localisation d'une mission spécifique"""
    if mission_id not in active_missions_locations:
        raise HTTPException(status_code=404, detail="Mission location not found")
    
    return {
        "success": True,
        "mission": active_missions_locations[mission_id].dict()
    }

# ============================================================================
# VOLUNTEER LOCATIONS (Real-time tracking)
# ============================================================================

@router.post("/volunteers/{volunteer_id}/location")
def update_volunteer_location(volunteer_id: int, location: Location, mission_id: Optional[int] = None):
    """Mettre à jour la localisation d'un volontaire en temps réel"""
    volunteer_loc = VolunteerLocation(
        volunteer_id=volunteer_id,
        location=location,
        active=True,
        mission_id=mission_id
    )
    active_volunteers_locations[volunteer_id] = volunteer_loc
    
    # Update mission volunteer count
    if mission_id and mission_id in active_missions_locations:
        active_missions_locations[mission_id].volunteers_count += 1
    
    # Broadcast to all connected clients
    broadcast_update({
        "type": "volunteer_location_update",
        "data": volunteer_loc.dict()
    })
    
    return {
        "success": True,
        "volunteer_id": volunteer_id,
        "location": location.dict()
    }

@router.get("/volunteers/locations")
def get_all_volunteer_locations():
    """Obtenir toutes les localisations de volontaires actifs"""
    return {
        "success": True,
        "total": len(active_volunteers_locations),
        "volunteers": [v.dict() for v in active_volunteers_locations.values()]
    }

@router.get("/volunteers/{volunteer_id}/location")
def get_volunteer_location(volunteer_id: int):
    """Obtenir la localisation d'un volontaire spécifique"""
    if volunteer_id not in active_volunteers_locations:
        raise HTTPException(status_code=404, detail="Volunteer location not found")
    
    return {
        "success": True,
        "volunteer": active_volunteers_locations[volunteer_id].dict()
    }

# ============================================================================
# HEATMAP & ANALYTICS
# ============================================================================

@router.get("/heatmap")
def get_mission_heatmap(category: Optional[str] = None):
    """Générer une heatmap des missions actives"""
    heatmap_points = []
    
    for mission in active_missions_locations.values():
        if category and mission.category != category:
            continue
        
        heatmap_points.append(HeatmapPoint(
            latitude=mission.location.latitude,
            longitude=mission.location.longitude,
            intensity=float(mission.volunteers_count) / 10.0  # Normalize intensity
        ))
    
    return {
        "success": True,
        "total_points": len(heatmap_points),
        "points": [p.dict() for p in heatmap_points]
    }

@router.get("/regions")
def get_active_regions():
    """Obtenir les régions avec activité humanitaire"""
    # Example regions (can be extended with real data)
    regions = [
        GeoRegion(
            name="Los Angeles County",
            bounds={"north": 34.8, "south": 33.7, "east": -117.6, "west": -118.7},
            missions_count=len([m for m in active_missions_locations.values()]),
            volunteers_count=len(active_volunteers_locations)
        )
    ]
    
    return {
        "success": True,
        "regions": [r.dict() for r in regions]
    }

@router.get("/nearby-missions")
def find_nearby_missions(lat: float, lon: float, radius_km: float = 10.0):
    """Trouver les missions à proximité d'une localisation"""
    import math
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km (Haversine formula)"""
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    nearby = []
    for mission in active_missions_locations.values():
        distance = calculate_distance(
            lat, lon,
            mission.location.latitude,
            mission.location.longitude
        )
        if distance <= radius_km:
            mission_dict = mission.dict()
            mission_dict["distance_km"] = round(distance, 2)
            nearby.append(mission_dict)
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "success": True,
        "search_location": {"latitude": lat, "longitude": lon},
        "radius_km": radius_km,
        "total_found": len(nearby),
        "missions": nearby
    }

# ============================================================================
# WEBSOCKET - Real-time Updates
# ============================================================================

@router.websocket("/ws/map")
async def websocket_map_updates(websocket: WebSocket):
    """WebSocket pour mises à jour de carte en temps réel"""
    await websocket.accept()
    active_websocket_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "data": {
                "missions": [m.dict() for m in active_missions_locations.values()],
                "volunteers": [v.dict() for v in active_volunteers_locations.values()]
            }
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "update_location":
                # Client sending location update
                volunteer_id = message.get("volunteer_id")
                location = message.get("location")
                if volunteer_id and location:
                    update_volunteer_location(
                        volunteer_id,
                        Location(**location),
                        message.get("mission_id")
                    )
    
    except WebSocketDisconnect:
        active_websocket_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_websocket_connections:
            active_websocket_connections.remove(websocket)

def broadcast_update(message: dict):
    """Diffuser une mise à jour à tous les clients WebSocket connectés"""
    for connection in active_websocket_connections:
        try:
            import asyncio
            asyncio.create_task(connection.send_json(message))
        except:
            pass

# ============================================================================
# ROUTE PLANNING
# ============================================================================

@router.get("/route")
def plan_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """Planifier un itinéraire entre deux points"""
    # Simple straight-line route (can be enhanced with real routing API)
    import math
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    distance = calculate_distance(start_lat, start_lon, end_lat, end_lon)
    estimated_time = distance / 5  # Assuming 5 km/h walking speed
    
    return {
        "success": True,
        "start": {"latitude": start_lat, "longitude": start_lon},
        "end": {"latitude": end_lat, "longitude": end_lon},
        "distance_km": round(distance, 2),
        "estimated_time_hours": round(estimated_time, 2),
        "route_type": "straight_line",
        "waypoints": [
            {"latitude": start_lat, "longitude": start_lon},
            {"latitude": end_lat, "longitude": end_lon}
        ]
    }

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/statistics")
def get_geo_statistics():
    """Obtenir les statistiques géographiques"""
    missions_by_category = {}
    for mission in active_missions_locations.values():
        missions_by_category[mission.category] = missions_by_category.get(mission.category, 0) + 1
    
    return {
        "success": True,
        "timestamp": datetime.utcnow().isoformat(),
        "total_missions": len(active_missions_locations),
        "total_volunteers": len(active_volunteers_locations),
        "active_volunteers": len([v for v in active_volunteers_locations.values() if v.active]),
        "missions_by_category": missions_by_category,
        "total_websocket_connections": len(active_websocket_connections)
    }
