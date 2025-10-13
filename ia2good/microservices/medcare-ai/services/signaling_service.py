"""
WebRTC Signaling Service
Handles SDP offer/answer exchange and ICE candidates for peer-to-peer video calls
"""
import logging
import json
from typing import Dict, Set, Optional
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


class SignalingService:
    """
    Manages WebRTC signaling between peers
    
    Handles:
    - SDP (Session Description Protocol) exchange
    - ICE (Interactive Connectivity Establishment) candidates
    - Room management for 1-on-1 consultations
    """
    
    def __init__(self):
        # Active rooms: {consultation_id: {'patient': ws, 'doctor': ws}}
        self.rooms: Dict[str, Dict[str, any]] = {}
        
        # Pending offers/answers: {consultation_id: {'offer': sdp, 'answer': sdp}}
        self.signaling_data: Dict[str, Dict] = defaultdict(dict)
        
        # ICE candidates buffer: {consultation_id: {user_id: [candidates]}}
        self.ice_candidates: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        
        logger.info("WebRTC Signaling Service initialized")
    
    def create_room(self, consultation_id: str) -> Dict:
        """
        Create a new consultation room
        
        Args:
            consultation_id: Unique consultation identifier
            
        Returns:
            Room information with TURN/STUN configuration
        """
        if consultation_id in self.rooms:
            logger.warning(f"Room {consultation_id} already exists")
            return {'error': 'Room already exists'}
        
        self.rooms[consultation_id] = {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'participants': {},
            'status': 'waiting'
        }
        
        logger.info(f"Created WebRTC room: {consultation_id}")
        
        # Return ICE server configuration
        return {
            'room_id': consultation_id,
            'ice_servers': self._get_ice_servers(),
            'status': 'ready'
        }
    
    def _get_ice_servers(self) -> list:
        """
        Get TURN/STUN server configuration
        
        Uses free public servers:
        - Google STUN servers (free, reliable)
        - Metered.ca TURN server (50GB/month free)
        """
        return [
            # Google public STUN servers
            {'urls': 'stun:stun.l.google.com:19302'},
            {'urls': 'stun:stun1.l.google.com:19302'},
            {'urls': 'stun:stun2.l.google.com:19302'},
            
            # Metered.ca free TURN server (50GB/month)
            # Sign up at https://www.metered.ca/tools/openrelay/
            {
                'urls': 'turn:a.relay.metered.ca:80',
                'username': 'openrelayproject',
                'credential': 'openrelayproject'
            },
            {
                'urls': 'turn:a.relay.metered.ca:80?transport=tcp',
                'username': 'openrelayproject',
                'credential': 'openrelayproject'
            },
            {
                'urls': 'turn:a.relay.metered.ca:443',
                'username': 'openrelayproject',
                'credential': 'openrelayproject'
            },
            
            # Backup: Twilio STUN (free tier)
            {'urls': 'stun:global.stun.twilio.com:3478'}
        ]
    
    async def join_room(
        self, 
        consultation_id: str, 
        user_id: str, 
        role: str,
        websocket: any
    ) -> Dict:
        """
        User joins a consultation room
        
        Args:
            consultation_id: Room ID
            user_id: User identifier
            role: 'patient' or 'doctor'
            websocket: WebSocket connection
            
        Returns:
            Join status and room info
        """
        if consultation_id not in self.rooms:
            logger.error(f"Room {consultation_id} not found")
            return {'error': 'Room not found'}
        
        room = self.rooms[consultation_id]
        room['participants'][role] = {
            'user_id': user_id,
            'websocket': websocket,
            'joined_at': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"User {user_id} ({role}) joined room {consultation_id}")
        
        # Check if both participants are present
        if len(room['participants']) == 2:
            room['status'] = 'active'
            logger.info(f"Room {consultation_id} is now active with both participants")
        
        return {
            'status': 'joined',
            'room': consultation_id,
            'role': role,
            'participants_count': len(room['participants']),
            'ice_servers': self._get_ice_servers()
        }
    
    async def handle_offer(
        self,
        consultation_id: str,
        user_id: str,
        sdp: str
    ) -> Dict:
        """
        Handle WebRTC offer (SDP)
        
        The caller creates an offer and sends it to the callee
        """
        if consultation_id not in self.rooms:
            return {'error': 'Room not found'}
        
        self.signaling_data[consultation_id]['offer'] = {
            'from': user_id,
            'sdp': sdp,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Received offer from {user_id} in room {consultation_id}")
        
        # Notify other participant
        await self._notify_other_participant(
            consultation_id,
            user_id,
            {
                'type': 'offer',
                'sdp': sdp,
                'from': user_id
            }
        )
        
        return {'status': 'offer_sent'}
    
    async def handle_answer(
        self,
        consultation_id: str,
        user_id: str,
        sdp: str
    ) -> Dict:
        """
        Handle WebRTC answer (SDP)
        
        The callee creates an answer in response to the offer
        """
        if consultation_id not in self.rooms:
            return {'error': 'Room not found'}
        
        self.signaling_data[consultation_id]['answer'] = {
            'from': user_id,
            'sdp': sdp,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Received answer from {user_id} in room {consultation_id}")
        
        # Notify other participant
        await self._notify_other_participant(
            consultation_id,
            user_id,
            {
                'type': 'answer',
                'sdp': sdp,
                'from': user_id
            }
        )
        
        return {'status': 'answer_sent'}
    
    async def handle_ice_candidate(
        self,
        consultation_id: str,
        user_id: str,
        candidate: Dict
    ) -> Dict:
        """
        Handle ICE candidate
        
        ICE candidates are potential network paths for connection
        """
        if consultation_id not in self.rooms:
            return {'error': 'Room not found'}
        
        # Store candidate
        self.ice_candidates[consultation_id][user_id].append({
            'candidate': candidate,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        logger.debug(f"Received ICE candidate from {user_id} in room {consultation_id}")
        
        # Forward to other participant
        await self._notify_other_participant(
            consultation_id,
            user_id,
            {
                'type': 'ice-candidate',
                'candidate': candidate,
                'from': user_id
            }
        )
        
        return {'status': 'candidate_forwarded'}
    
    async def _notify_other_participant(
        self,
        consultation_id: str,
        sender_id: str,
        message: Dict
    ):
        """
        Send message to the other participant in the room
        """
        room = self.rooms.get(consultation_id)
        if not room:
            return
        
        # Find other participant
        for role, participant in room['participants'].items():
            if participant['user_id'] != sender_id:
                ws = participant.get('websocket')
                if ws:
                    try:
                        await ws.send_json(message)
                        logger.debug(f"Notified {participant['user_id']} in room {consultation_id}")
                    except Exception as e:
                        logger.error(f"Error notifying participant: {e}")
    
    async def leave_room(self, consultation_id: str, user_id: str) -> Dict:
        """
        User leaves consultation room
        """
        if consultation_id not in self.rooms:
            return {'error': 'Room not found'}
        
        room = self.rooms[consultation_id]
        
        # Remove participant
        for role, participant in list(room['participants'].items()):
            if participant['user_id'] == user_id:
                del room['participants'][role]
                logger.info(f"User {user_id} left room {consultation_id}")
                break
        
        # Notify other participant
        await self._notify_other_participant(
            consultation_id,
            user_id,
            {'type': 'participant-left', 'user_id': user_id}
        )
        
        # Clean up if room is empty
        if len(room['participants']) == 0:
            self._cleanup_room(consultation_id)
        
        return {'status': 'left'}
    
    def _cleanup_room(self, consultation_id: str):
        """
        Clean up room and associated data
        """
        if consultation_id in self.rooms:
            del self.rooms[consultation_id]
        if consultation_id in self.signaling_data:
            del self.signaling_data[consultation_id]
        if consultation_id in self.ice_candidates:
            del self.ice_candidates[consultation_id]
        
        logger.info(f"Cleaned up room {consultation_id}")
    
    def get_room_status(self, consultation_id: str) -> Dict:
        """
        Get current room status
        """
        if consultation_id not in self.rooms:
            return {'error': 'Room not found'}
        
        room = self.rooms[consultation_id]
        return {
            'room_id': consultation_id,
            'status': room['status'],
            'participants': [
                {
                    'role': role,
                    'user_id': p['user_id'],
                    'joined_at': p['joined_at']
                }
                for role, p in room['participants'].items()
            ],
            'created_at': room['created_at']
        }
    
    def get_active_rooms(self) -> Dict:
        """
        Get statistics about active rooms
        """
        return {
            'total_rooms': len(self.rooms),
            'active_rooms': sum(1 for r in self.rooms.values() if r['status'] == 'active'),
            'waiting_rooms': sum(1 for r in self.rooms.values() if r['status'] == 'waiting')
        }


# Global signaling service instance
_signaling_service = None


def get_signaling_service() -> SignalingService:
    """Get or create global signaling service instance"""
    global _signaling_service
    if _signaling_service is None:
        _signaling_service = SignalingService()
    return _signaling_service
