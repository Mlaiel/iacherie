"""
Guardian Video Chat Routes
One-on-one and group video calls with WebRTC signaling
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import uuid

router = APIRouter()

# Models
class RoomConfig(BaseModel):
    room_id: Optional[str] = None
    name: str
    max_participants: int = 10
    is_public: bool = False
    mission_id: Optional[int] = None

class Participant(BaseModel):
    participant_id: str
    name: str
    is_video_enabled: bool = True
    is_audio_enabled: bool = True
    joined_at: datetime

# Storage
active_rooms: Dict[str, RoomConfig] = {}
room_participants: Dict[str, Dict[str, WebSocket]] = {}  # room_id -> {participant_id -> websocket}
participant_info: Dict[str, Participant] = {}  # participant_id -> info

# ============================================================================
# ROOM MANAGEMENT
# ============================================================================

@router.post("/rooms/create")
def create_room(config: RoomConfig):
    """Créer une salle de video chat"""
    if not config.room_id:
        config.room_id = str(uuid.uuid4())
    
    active_rooms[config.room_id] = config
    room_participants[config.room_id] = {}
    
    return {
        "success": True,
        "room_id": config.room_id,
        "join_url": f"ws://localhost:8001/api/guardian/videochat/room/{config.room_id}",
        "created_at": datetime.utcnow().isoformat()
    }

@router.get("/rooms")
def list_rooms():
    """Lister toutes les salles actives"""
    rooms_list = []
    for room_id, config in active_rooms.items():
        participants_count = len(room_participants.get(room_id, {}))
        rooms_list.append({
            "room_id": room_id,
            "name": config.name,
            "participants": participants_count,
            "max_participants": config.max_participants,
            "is_public": config.is_public,
            "mission_id": config.mission_id
        })
    
    return {
        "success": True,
        "total": len(rooms_list),
        "rooms": rooms_list
    }

@router.get("/rooms/{room_id}")
def get_room_info(room_id: str):
    """Obtenir les infos d'une salle"""
    if room_id not in active_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    config = active_rooms[room_id]
    participants = room_participants.get(room_id, {})
    
    participants_list = []
    for p_id in participants.keys():
        if p_id in participant_info:
            participants_list.append(participant_info[p_id].dict())
    
    return {
        "success": True,
        "room": {
            **config.dict(),
            "participants": participants_list,
            "participants_count": len(participants)
        }
    }

@router.delete("/rooms/{room_id}")
def close_room(room_id: str):
    """Fermer une salle"""
    if room_id not in active_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Disconnect all participants
    participants = room_participants.get(room_id, {})
    for ws in participants.values():
        try:
            import asyncio
            asyncio.create_task(ws.close())
        except:
            pass
    
    # Remove room
    del active_rooms[room_id]
    if room_id in room_participants:
        del room_participants[room_id]
    
    return {
        "success": True,
        "message": "Room closed"
    }

# ============================================================================
# WebRTC SIGNALING WebSocket
# ============================================================================

@router.websocket("/room/{room_id}")
async def videochat_websocket(websocket: WebSocket, room_id: str):
    """WebSocket pour WebRTC signaling"""
    await websocket.accept()
    
    # Check if room exists
    if room_id not in active_rooms:
        await websocket.send_json({"error": "Room not found"})
        await websocket.close()
        return
    
    # Check room capacity
    room_config = active_rooms[room_id]
    current_participants = len(room_participants.get(room_id, {}))
    if current_participants >= room_config.max_participants:
        await websocket.send_json({"error": "Room is full"})
        await websocket.close()
        return
    
    # Generate participant ID
    participant_id = str(uuid.uuid4())
    
    # Add participant to room
    if room_id not in room_participants:
        room_participants[room_id] = {}
    room_participants[room_id][participant_id] = websocket
    
    # Create participant info
    participant_info[participant_id] = Participant(
        participant_id=participant_id,
        name=f"Participant_{participant_id[:8]}",
        joined_at=datetime.utcnow()
    )
    
    # Send welcome message with participant ID
    await websocket.send_json({
        "type": "welcome",
        "participant_id": participant_id,
        "room_id": room_id,
        "room_name": room_config.name
    })
    
    # Notify other participants
    await broadcast_to_room(room_id, {
        "type": "participant_joined",
        "participant_id": participant_id,
        "timestamp": datetime.utcnow().isoformat()
    }, exclude=participant_id)
    
    # Send list of existing participants
    existing_participants = [
        p_id for p_id in room_participants[room_id].keys() 
        if p_id != participant_id
    ]
    await websocket.send_json({
        "type": "participants_list",
        "participants": existing_participants
    })
    
    try:
        while True:
            # Receive WebRTC signaling messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "offer":
                # Forward offer to target participant
                target_id = message.get("target")
                if target_id and target_id in room_participants[room_id]:
                    target_ws = room_participants[room_id][target_id]
                    await target_ws.send_json({
                        "type": "offer",
                        "from": participant_id,
                        "sdp": message.get("sdp")
                    })
            
            elif msg_type == "answer":
                # Forward answer to target participant
                target_id = message.get("target")
                if target_id and target_id in room_participants[room_id]:
                    target_ws = room_participants[room_id][target_id]
                    await target_ws.send_json({
                        "type": "answer",
                        "from": participant_id,
                        "sdp": message.get("sdp")
                    })
            
            elif msg_type == "ice_candidate":
                # Forward ICE candidate to target participant
                target_id = message.get("target")
                if target_id and target_id in room_participants[room_id]:
                    target_ws = room_participants[room_id][target_id]
                    await target_ws.send_json({
                        "type": "ice_candidate",
                        "from": participant_id,
                        "candidate": message.get("candidate")
                    })
            
            elif msg_type == "toggle_video":
                # Update participant info
                if participant_id in participant_info:
                    participant_info[participant_id].is_video_enabled = message.get("enabled", True)
                # Notify others
                await broadcast_to_room(room_id, {
                    "type": "participant_video_toggle",
                    "participant_id": participant_id,
                    "enabled": message.get("enabled", True)
                }, exclude=participant_id)
            
            elif msg_type == "toggle_audio":
                # Update participant info
                if participant_id in participant_info:
                    participant_info[participant_id].is_audio_enabled = message.get("enabled", True)
                # Notify others
                await broadcast_to_room(room_id, {
                    "type": "participant_audio_toggle",
                    "participant_id": participant_id,
                    "enabled": message.get("enabled", True)
                }, exclude=participant_id)
            
            elif msg_type == "chat_message":
                # Broadcast chat message
                await broadcast_to_room(room_id, {
                    "type": "chat_message",
                    "from": participant_id,
                    "message": message.get("message"),
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Remove participant
        if room_id in room_participants and participant_id in room_participants[room_id]:
            del room_participants[room_id][participant_id]
        
        if participant_id in participant_info:
            del participant_info[participant_id]
        
        # Notify others
        await broadcast_to_room(room_id, {
            "type": "participant_left",
            "participant_id": participant_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Clean up empty room
        if room_id in room_participants and len(room_participants[room_id]) == 0:
            if room_id in active_rooms:
                del active_rooms[room_id]
            del room_participants[room_id]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def broadcast_to_room(room_id: str, message: dict, exclude: Optional[str] = None):
    """Envoyer un message à tous les participants d'une salle"""
    if room_id not in room_participants:
        return
    
    for participant_id, ws in room_participants[room_id].items():
        if participant_id != exclude:
            try:
                await ws.send_json(message)
            except:
                pass

# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/rooms/{room_id}/stats")
def get_room_stats(room_id: str):
    """Obtenir les statistiques d'une salle"""
    if room_id not in active_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participants = room_participants.get(room_id, {})
    
    participants_details = []
    for p_id in participants.keys():
        if p_id in participant_info:
            info = participant_info[p_id]
            participants_details.append({
                "id": info.participant_id[:8],
                "name": info.name,
                "video": info.is_video_enabled,
                "audio": info.is_audio_enabled,
                "joined_at": info.joined_at.isoformat()
            })
    
    return {
        "success": True,
        "room_id": room_id,
        "total_participants": len(participants),
        "participants": participants_details,
        "timestamp": datetime.utcnow().isoformat()
    }
