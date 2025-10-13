"""
WebRTC Signaling API Routes
Handles WebSocket connections for real-time WebRTC signaling
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Optional
import logging
import json
from uuid import UUID

from services.signaling_service import get_signaling_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/medcare/webrtc", tags=["WebRTC"])


@router.post("/rooms/{consultation_id}", status_code=201)
async def create_webrtc_room(consultation_id: UUID):
    """
    Create a WebRTC room for video consultation
    
    Returns ICE server configuration and room details
    """
    try:
        signaling = get_signaling_service()
        result = signaling.create_room(str(consultation_id))
        
        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating WebRTC room: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room: {str(e)}"
        )


@router.get("/rooms/{consultation_id}/status")
async def get_room_status(consultation_id: UUID):
    """
    Get current status of a WebRTC room
    """
    try:
        signaling = get_signaling_service()
        result = signaling.get_room_status(str(consultation_id))
        
        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result['error']
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting room status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get("/stats")
async def get_webrtc_stats():
    """
    Get statistics about active WebRTC rooms
    """
    try:
        signaling = get_signaling_service()
        return signaling.get_active_rooms()
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.websocket("/signal/{consultation_id}")
async def websocket_signaling(
    websocket: WebSocket,
    consultation_id: str,
    user_id: str,
    role: str  # 'patient' or 'doctor'
):
    """
    WebSocket endpoint for WebRTC signaling
    
    Handles:
    - SDP offer/answer exchange
    - ICE candidate forwarding
    - Connection status updates
    
    Query parameters:
    - user_id: User identifier
    - role: 'patient' or 'doctor'
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: {user_id} ({role}) in room {consultation_id}")
    
    signaling = get_signaling_service()
    
    try:
        # Join room
        join_result = await signaling.join_room(
            consultation_id,
            user_id,
            role,
            websocket
        )
        
        if 'error' in join_result:
            await websocket.send_json({'error': join_result['error']})
            await websocket.close()
            return
        
        # Send join confirmation
        await websocket.send_json({
            'type': 'joined',
            'data': join_result
        })
        
        # Handle incoming messages
        while True:
            try:
                message = await websocket.receive_json()
                await handle_signaling_message(
                    signaling,
                    consultation_id,
                    user_id,
                    message,
                    websocket
                )
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {user_id}")
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'Invalid JSON'
                })
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await websocket.send_json({
                    'type': 'error',
                    'message': str(e)
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during setup: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Leave room on disconnect
        await signaling.leave_room(consultation_id, user_id)


async def handle_signaling_message(
    signaling,
    consultation_id: str,
    user_id: str,
    message: dict,
    websocket: WebSocket
):
    """
    Handle WebRTC signaling messages
    
    Message types:
    - offer: WebRTC offer (SDP)
    - answer: WebRTC answer (SDP)
    - ice-candidate: ICE candidate
    """
    msg_type = message.get('type')
    
    if msg_type == 'offer':
        # Handle SDP offer
        result = await signaling.handle_offer(
            consultation_id,
            user_id,
            message.get('sdp')
        )
        await websocket.send_json({
            'type': 'offer-sent',
            'data': result
        })
    
    elif msg_type == 'answer':
        # Handle SDP answer
        result = await signaling.handle_answer(
            consultation_id,
            user_id,
            message.get('sdp')
        )
        await websocket.send_json({
            'type': 'answer-sent',
            'data': result
        })
    
    elif msg_type == 'ice-candidate':
        # Handle ICE candidate
        result = await signaling.handle_ice_candidate(
            consultation_id,
            user_id,
            message.get('candidate')
        )
        # No need to send confirmation for ICE candidates
    
    elif msg_type == 'ping':
        # Keepalive ping
        await websocket.send_json({'type': 'pong'})
    
    else:
        logger.warning(f"Unknown message type: {msg_type}")
        await websocket.send_json({
            'type': 'error',
            'message': f'Unknown message type: {msg_type}'
        })
