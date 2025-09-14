"""Edge MEC Enterprise
====================

Mobile Edge Computing Enterprise consolidé - Fusion de tous les composants MEC
en un système unifié pour optimisation créateurs Ainflue.

Consolidation des 8 fichiers MEC:
- context_awareness.py - Conscience contextuelle  
- device_manager.py - Gestion devices complète
- handover_controller.py - Orchestration handover
- location_services.py - Intelligence géolocalisation
- mobility_prediction.py - Prédiction mobilité IA
- proximity_detection.py - Optimisation proximité
- session_continuity.py - Continuité sessions
- __init__.py - Coordination edge computing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ AVIS JURIDIQUE - PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE
Cette architecture est la propriété exclusive de Fahed Mlaiel.
Toute utilisation non autorisée entraînera des poursuites judiciaires.
"""

import asyncio
import logging
import time
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
from abc import ABC, abstractmethod
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


# ============================================================================
# DEVICE MANAGEMENT - Consolidation device_manager.py
# ============================================================================

class DeviceType(str, Enum):
    """Types d'appareils mobiles."""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    IOT_SENSOR = "iot_sensor"
    VEHICLE = "vehicle"
    WEARABLE = "wearable"
    LAPTOP = "laptop"
    SMART_CAMERA = "smart_camera"
    DRONE = "drone"


class DeviceCapability(str, Enum):
    """Capacités des appareils."""
    COMPUTE = "compute"
    STORAGE = "storage"
    SENSING = "sensing"
    COMMUNICATION = "communication"
    VIDEO_PROCESSING = "video_processing"
    AUDIO_PROCESSING = "audio_processing"
    AI_ACCELERATION = "ai_acceleration"
    CONTENT_CREATION = "content_creation"


class DeviceStatus(str, Enum):
    """Statuts des appareils."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ROAMING = "roaming"
    OFFLINE = "offline"
    CHARGING = "charging"
    LOW_BATTERY = "low_battery"
    MAINTENANCE = "maintenance"


class NetworkType(str, Enum):
    """Types de réseaux."""
    WIFI = "wifi"
    CELLULAR_4G = "4g"
    CELLULAR_5G = "5g"
    BLUETOOTH = "bluetooth"
    LORA = "lora"
    SATELLITE = "satellite"


@dataclass
class DeviceResources:
    """Ressources d'un appareil."""
    cpu_cores: int
    cpu_frequency: float  # GHz
    memory_gb: float
    storage_gb: float
    battery_level: float  # 0-100%
    network_bandwidth: float  # Mbps
    gpu_available: bool = False
    ai_accelerator: bool = False


@dataclass
class LocationData:
    """Données de localisation."""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: float = 1.0  # meters
    timestamp: datetime = field(default_factory=datetime.utcnow)
    speed: Optional[float] = None  # km/h
    heading: Optional[float] = None  # degrees


@dataclass
class MobileDevice:
    """Appareil mobile avec capacités étendues."""
    device_id: str
    device_type: DeviceType
    capabilities: List[DeviceCapability]
    status: DeviceStatus
    resources: DeviceResources
    location: Optional[LocationData] = None
    network_type: NetworkType = NetworkType.WIFI
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    owner_id: Optional[str] = None
    creator_type: Optional[str] = None


# ============================================================================
# CONTEXT AWARENESS - Consolidation context_awareness.py
# ============================================================================

class ContextType(str, Enum):
    """Types de contexte."""
    LOCATION = "location"
    TEMPORAL = "temporal"
    ACTIVITY = "activity"
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    TECHNICAL = "technical"
    BUSINESS = "business"


class ActivityType(str, Enum):
    """Types d'activités."""
    CONTENT_CREATION = "content_creation"
    LIVE_STREAMING = "live_streaming"
    COLLABORATION = "collaboration"
    CONSUMPTION = "consumption"
    EDITING = "editing"
    UPLOADING = "uploading"
    INTERACTING = "interacting"


@dataclass
class ContextData:
    """Données contextuelles."""
    context_type: ContextType
    data: Dict[str, Any]
    confidence: float  # 0-1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_device: Optional[str] = None


@dataclass
class UserActivity:
    """Activité utilisateur."""
    activity_id: str
    user_id: str
    activity_type: ActivityType
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[LocationData] = None
    devices_used: List[str] = field(default_factory=list)
    content_metadata: Dict[str, Any] = field(default_factory=dict)


class ContextAwarenessEngine:
    """Moteur de conscience contextuelle."""
    
    def __init__(self) -> None:
        self.context_cache = {}
        self.activity_history = deque(maxlen=1000)
        self.context_rules = {}
    
    async def collect_context(self, device_id: str, sensors_data: Dict[str, Any]) -> ContextData:
        """Collecte les données contextuelles."""
        # Analyse du contexte temporel
        temporal_context = self._analyze_temporal_context()
        
        # Analyse du contexte d'activité
        activity_context = self._analyze_activity_context(sensors_data)
        
        # Analyse du contexte environnemental
        environmental_context = self._analyze_environmental_context(sensors_data)
        
        # Fusion des contextes
        context_data = ContextData(
            context_type=ContextType.ACTIVITY,
            data={
                "temporal": temporal_context,
                "activity": activity_context,
                "environmental": environmental_context
            },
            confidence=0.8,
            source_device=device_id
        )
        
        # Mise en cache
        self.context_cache[device_id] = context_data
        
        return context_data
    
    def _analyze_temporal_context(self) -> Dict[str, Any]:
        """Analyse le contexte temporel."""
        now = datetime.utcnow()
        hour = now.hour
        
        time_of_day = "morning" if 6 <= hour < 12 else \
                     "afternoon" if 12 <= hour < 18 else \
                     "evening" if 18 <= hour < 22 else "night"
        
        return {
            "time_of_day": time_of_day,
            "hour": hour,
            "day_of_week": now.weekday(),
            "is_weekend": now.weekday() >= 5
        }
    
    def _analyze_activity_context(self, sensors_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le contexte d'activité."""
        activity = "unknown"
        confidence = 0.5
        
        # Analyse basée sur les capteurs
        if sensors_data.get("camera_active"):
            activity = "content_creation"
            confidence = 0.9
        elif sensors_data.get("microphone_active"):
            activity = "live_streaming"
            confidence = 0.8
        elif sensors_data.get("screen_touch_frequency", 0) > 10:
            activity = "editing"
            confidence = 0.7
        
        return {
            "current_activity": activity,
            "confidence": confidence,
            "duration": sensors_data.get("activity_duration", 0)
        }
    
    def _analyze_environmental_context(self, sensors_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le contexte environnemental."""
        return {
            "noise_level": sensors_data.get("noise_level", 40),
            "light_level": sensors_data.get("light_level", 500),
            "network_quality": sensors_data.get("network_quality", "good"),
            "battery_status": sensors_data.get("battery_level", 80)
        }


# ============================================================================
# MOBILITY PREDICTION - Consolidation mobility_prediction.py
# ============================================================================

class MovementPattern(str, Enum):
    """Patterns de mouvement."""
    STATIONARY = "stationary"
    WALKING = "walking"
    DRIVING = "driving"
    PUBLIC_TRANSPORT = "public_transport"
    CYCLING = "cycling"
    FLYING = "flying"


@dataclass
class MobilityPrediction:
    """Prédiction de mobilité."""
    device_id: str
    predicted_location: LocationData
    confidence: float
    prediction_time: datetime
    movement_pattern: MovementPattern
    estimated_arrival: Optional[datetime] = None


class MobilityPredictionAI:
    """IA de prédiction de mobilité."""
    
    def __init__(self) -> None:
        self.location_history = defaultdict(list)
        self.movement_patterns = defaultdict(list)
        self.prediction_models = {}
    
    async def predict_mobility(self, device_id: str, current_location: LocationData,
                             historical_data: List[LocationData]) -> MobilityPrediction:
        """Prédit la mobilité future."""
        # Analyse du pattern de mouvement
        movement_pattern = self._analyze_movement_pattern(historical_data)
        
        # Prédiction de la prochaine localisation
        predicted_location = self._predict_next_location(current_location, historical_data)
        
        # Calcul de la confiance
        confidence = self._calculate_prediction_confidence(historical_data, movement_pattern)
        
        return MobilityPrediction(
            device_id=device_id,
            predicted_location=predicted_location,
            confidence=confidence,
            prediction_time=datetime.utcnow() + timedelta(minutes=15),
            movement_pattern=movement_pattern
        )
    
    def _analyze_movement_pattern(self, locations: List[LocationData]) -> MovementPattern:
        """Analyse le pattern de mouvement."""
        if len(locations) < 2:
            return MovementPattern.STATIONARY
        
        # Calcul de la vitesse moyenne
        total_distance = 0
        total_time = 0
        
        for i in range(1, len(locations)):
            prev_loc = locations[i-1]
            curr_loc = locations[i]
            
            distance = self._calculate_distance(prev_loc, curr_loc)
            time_diff = (curr_loc.timestamp - prev_loc.timestamp).total_seconds() / 3600  # hours
            
            if time_diff > 0:
                total_distance += distance
                total_time += time_diff
        
        if total_time == 0:
            return MovementPattern.STATIONARY
        
        avg_speed = total_distance / total_time  # km/h
        
        if avg_speed < 1:
            return MovementPattern.STATIONARY
        elif avg_speed < 8:
            return MovementPattern.WALKING
        elif avg_speed < 25:
            return MovementPattern.CYCLING
        elif avg_speed < 80:
            return MovementPattern.DRIVING
        else:
            return MovementPattern.FLYING
    
    def _predict_next_location(self, current: LocationData, 
                             history: List[LocationData]) -> LocationData:
        """Prédit la prochaine localisation."""
        if len(history) < 2:
            return current
        
        # Simple linear prediction based on last movement
        last_loc = history[-1]
        lat_diff = current.latitude - last_loc.latitude
        lon_diff = current.longitude - last_loc.longitude
        
        # Project forward
        predicted_lat = current.latitude + lat_diff
        predicted_lon = current.longitude + lon_diff
        
        return LocationData(
            latitude=predicted_lat,
            longitude=predicted_lon,
            timestamp=datetime.utcnow() + timedelta(minutes=15)
        )
    
    def _calculate_distance(self, loc1: LocationData, loc2: LocationData) -> float:
        """Calcule la distance entre deux points (Haversine)."""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(loc1.latitude)
        lat2_rad = math.radians(loc2.latitude)
        delta_lat = math.radians(loc2.latitude - loc1.latitude)
        delta_lon = math.radians(loc2.longitude - loc1.longitude)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _calculate_prediction_confidence(self, history: List[LocationData],
                                       pattern: MovementPattern) -> float:
        """Calcule la confiance de prédiction."""
        if len(history) < 3:
            return 0.3
        
        # Base confidence on pattern consistency and data quality
        base_confidence = 0.6
        
        if pattern == MovementPattern.STATIONARY:
            base_confidence = 0.9
        elif pattern in [MovementPattern.WALKING, MovementPattern.CYCLING]:
            base_confidence = 0.7
        elif pattern == MovementPattern.DRIVING:
            base_confidence = 0.6
        
        # Adjust based on data quality
        data_quality = min(1.0, len(history) / 10)
        
        return min(0.95, base_confidence * data_quality)


# ============================================================================
# HANDOVER CONTROLLER - Consolidation handover_controller.py
# ============================================================================

class HandoverType(str, Enum):
    """Types de handover."""
    HORIZONTAL = "horizontal"  # Same technology
    VERTICAL = "vertical"      # Different technology
    SOFT = "soft"             # Make-before-break
    HARD = "hard"             # Break-before-make


class HandoverReason(str, Enum):
    """Raisons de handover."""
    SIGNAL_QUALITY = "signal_quality"
    LOAD_BALANCING = "load_balancing"
    USER_MOBILITY = "user_mobility"
    NETWORK_OPTIMIZATION = "network_optimization"
    EMERGENCY = "emergency"
    COST_OPTIMIZATION = "cost_optimization"


@dataclass
class HandoverPolicy:
    """Politique de handover."""
    trigger_threshold: float
    hysteresis: float
    timeout: int  # seconds
    max_attempts: int = 3
    priority_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class HandoverRequest:
    """Demande de handover."""
    request_id: str
    device_id: str
    source_edge: str
    target_edge: str
    handover_type: HandoverType
    reason: HandoverReason
    priority: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None


class HandoverController:
    """Contrôleur de handover."""
    
    def __init__(self) -> None:
        self.active_handovers = {}
        self.handover_history = deque(maxlen=1000)
        self.policies = {}
        self.performance_metrics = {
            "success_rate": 0.95,
            "average_duration": 2.0,  # seconds
            "failure_count": 0
        }
    
    async def initiate_handover(self, request: HandoverRequest) -> bool:
        """Initie un handover."""
        try:
            logger.info(f"Initiating handover for device {request.device_id}")
            
            # Validate handover request
            if not self._validate_handover_request(request):
                return False
            
            # Check if handover is already in progress
            if request.device_id in self.active_handovers:
                logger.warning(f"Handover already in progress for device {request.device_id}")
                return False
            
            # Execute handover
            self.active_handovers[request.device_id] = request
            success = await self._execute_handover(request)
            
            # Update metrics
            self._update_handover_metrics(success)
            
            # Cleanup
            if request.device_id in self.active_handovers:
                del self.active_handovers[request.device_id]
            
            # Record in history
            self.handover_history.append({
                "request": request,
                "success": success,
                "completion_time": datetime.utcnow()
            })
            
            return success
            
        except Exception as e:
            logger.error(f"Handover failed for device {request.device_id}: {e}")
            return False
    
    async def _execute_handover(self, request: HandoverRequest) -> bool:
        """Exécute le handover."""
        if request.handover_type == HandoverType.SOFT:
            return await self._execute_soft_handover(request)
        else:
            return await self._execute_hard_handover(request)
    
    async def _execute_soft_handover(self, request: HandoverRequest) -> bool:
        """Exécute un soft handover (make-before-break)."""
        # 1. Establish connection to target
        target_connected = await self._connect_to_target(request.target_edge, request.device_id)
        if not target_connected:
            return False
        
        # 2. Transfer session state
        state_transferred = await self._transfer_session_state(request)
        if not state_transferred:
            await self._disconnect_from_target(request.target_edge, request.device_id)
            return False
        
        # 3. Switch traffic to target
        traffic_switched = await self._switch_traffic(request)
        if not traffic_switched:
            return False
        
        # 4. Release source connection
        await self._release_source_connection(request.source_edge, request.device_id)
        
        return True
    
    async def _execute_hard_handover(self, request: HandoverRequest) -> bool:
        """Exécute un hard handover (break-before-make)."""
        # 1. Release source connection
        await self._release_source_connection(request.source_edge, request.device_id)
        
        # 2. Connect to target
        target_connected = await self._connect_to_target(request.target_edge, request.device_id)
        if not target_connected:
            # Try to reconnect to source
            await self._connect_to_target(request.source_edge, request.device_id)
            return False
        
        # 3. Restore session state
        await self._restore_session_state(request)
        
        return True
    
    async def _connect_to_target(self, target_edge: str, device_id: str) -> bool:
        """Connecte à l'edge cible."""
        # Simulation de connexion
        await asyncio.sleep(0.1)
        return True
    
    async def _disconnect_from_target(self, target_edge: str, device_id: str) -> bool:
        """Déconnecte de l'edge cible."""
        await asyncio.sleep(0.05)
        return True
    
    async def _transfer_session_state(self, request: HandoverRequest) -> bool:
        """Transfère l'état de session."""
        # Simulation de transfert d'état
        await asyncio.sleep(0.2)
        return True
    
    async def _switch_traffic(self, request: HandoverRequest) -> bool:
        """Bascule le trafic."""
        await asyncio.sleep(0.1)
        return True
    
    async def _release_source_connection(self, source_edge -> None: str, device_id -> None: str) -> None:
        """Libère la connexion source."""
        await asyncio.sleep(0.05)
    
    async def _restore_session_state(self, request -> None: HandoverRequest) -> None:
        """Restaure l'état de session."""
        await asyncio.sleep(0.1)
    
    def _validate_handover_request(self, request: HandoverRequest) -> bool:
        """Valide la demande de handover."""
        if not request.device_id or not request.source_edge or not request.target_edge:
            return False
        return True
    
    def _update_handover_metrics(self, success -> None: bool) -> None:
        """Met à jour les métriques de handover."""
        if success:
            # Update success rate (exponential moving average)
            self.performance_metrics["success_rate"] = (
                0.9 * self.performance_metrics["success_rate"] + 0.1 * 1.0
            )
        else:
            self.performance_metrics["failure_count"] += 1
            self.performance_metrics["success_rate"] = (
                0.9 * self.performance_metrics["success_rate"] + 0.1 * 0.0
            )


# ============================================================================
# SESSION CONTINUITY - Consolidation session_continuity.py
# ============================================================================

class SessionState(str, Enum):
    """États de session."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    MIGRATING = "migrating"
    TERMINATED = "terminated"
    RECOVERING = "recovering"


@dataclass
class SessionInfo:
    """Informations de session."""
    session_id: str
    user_id: str
    device_id: str
    edge_node: str
    state: SessionState
    created_at: datetime
    last_activity: datetime
    session_data: Dict[str, Any] = field(default_factory=dict)
    checkpoint_data: Optional[bytes] = None


class SessionContinuityManager:
    """Gestionnaire de continuité de session."""
    
    def __init__(self) -> None:
        self.active_sessions = {}
        self.session_checkpoints = {}
        self.recovery_policies = {}
    
    async def create_session(self, user_id: str, device_id: str, edge_node: str) -> str:
        """Crée une nouvelle session."""
        session_id = str(uuid.uuid4())
        
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            edge_node=edge_node,
            state=SessionState.ACTIVE,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return session_id
    
    async def checkpoint_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Crée un checkpoint de session."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.session_data = session_data
        
        # Serialize session data for checkpointing
        checkpoint_data = json.dumps(session_data).encode()
        session.checkpoint_data = checkpoint_data
        
        self.session_checkpoints[session_id] = checkpoint_data
        
        logger.info(f"Checkpointed session {session_id}")
        return True
    
    async def migrate_session(self, session_id: str, target_edge: str) -> bool:
        """Migre une session vers un autre edge."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        session.state = SessionState.MIGRATING
        
        try:
            # Transfer session state to target edge
            success = await self._transfer_session_to_edge(session, target_edge)
            
            if success:
                session.edge_node = target_edge
                session.state = SessionState.ACTIVE
                logger.info(f"Migrated session {session_id} to {target_edge}")
            else:
                session.state = SessionState.ACTIVE  # Rollback
                logger.error(f"Failed to migrate session {session_id}")
            
            return success
            
        except Exception as e:
            session.state = SessionState.ACTIVE  # Rollback
            logger.error(f"Session migration failed: {e}")
            return False
    
    async def recover_session(self, session_id: str) -> bool:
        """Récupère une session après interruption."""
        if session_id not in self.session_checkpoints:
            return False
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            session.state = SessionState.RECOVERING
            
            # Restore session data from checkpoint
            checkpoint_data = self.session_checkpoints[session_id]
            session_data = json.loads(checkpoint_data.decode())
            session.session_data = session_data
            
            session.state = SessionState.ACTIVE
            session.last_activity = datetime.utcnow()
            
            logger.info(f"Recovered session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Session recovery failed: {e}")
            return False
    
    async def _transfer_session_to_edge(self, session: SessionInfo, target_edge: str) -> bool:
        """Transfère la session vers l'edge cible."""
        # Simulation du transfert
        await asyncio.sleep(0.1)
        return True


# ============================================================================
# PROXIMITY DETECTION & LOCATION SERVICES
# ============================================================================

class ProximityDetector:
    """Détecteur de proximité."""
    
    def __init__(self, detection_radius -> None: float = 100.0) -> None:  # meters
        self.detection_radius = detection_radius
        self.proximity_cache = {}
    
    async def detect_nearby_devices(self, device: MobileDevice, 
                                  all_devices: List[MobileDevice]) -> List[MobileDevice]:
        """Détecte les appareils à proximité."""
        if not device.location:
            return []
        
        nearby_devices = []
        
        for other_device in all_devices:
            if (other_device.device_id != device.device_id and 
                other_device.location and 
                other_device.status == DeviceStatus.ACTIVE):
                
                distance = self._calculate_distance(device.location, other_device.location)
                if distance <= self.detection_radius:
                    nearby_devices.append(other_device)
        
        return nearby_devices
    
    def _calculate_distance(self, loc1: LocationData, loc2: LocationData) -> float:
        """Calcule la distance entre deux points."""
        R = 6371000  # Earth radius in meters
        
        lat1_rad = math.radians(loc1.latitude)
        lat2_rad = math.radians(loc2.latitude)
        delta_lat = math.radians(loc2.latitude - loc1.latitude)
        delta_lon = math.radians(loc2.longitude - loc1.longitude)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c


class LocationServices:
    """Services de géolocalisation."""
    
    def __init__(self) -> None:
        self.location_cache = {}
        self.geofences = {}
    
    async def get_location(self, device_id: str) -> Optional[LocationData]:
        """Récupère la localisation d'un appareil."""
        return self.location_cache.get(device_id)
    
    async def update_location(self, device_id -> None: str, location -> None: LocationData) -> None:
        """Met à jour la localisation d'un appareil."""
        self.location_cache[device_id] = location
        
        # Check geofences
        await self._check_geofences(device_id, location)
    
    async def _check_geofences(self, device_id -> None: str, location -> None: LocationData) -> None:
        """Vérifie les geofences."""
        # Implementation for geofence checking
        pass


# ============================================================================
# MAIN MEC ENTERPRISE CLASS
# ============================================================================

class EdgeMECEnterprise:
    """Mobile Edge Computing Enterprise consolidé."""
    
    def __init__(self) -> None:
        # Device management
        self.devices: Dict[str, MobileDevice] = {}
        self.device_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Core components
        self.context_engine = ContextAwarenessEngine()
        self.mobility_ai = MobilityPredictionAI()
        self.handover_controller = HandoverController()
        self.session_manager = SessionContinuityManager()
        self.proximity_detector = ProximityDetector()
        self.location_services = LocationServices()
        
        # Performance metrics
        self.performance_metrics = {
            "active_devices": 0,
            "active_sessions": 0,
            "handover_success_rate": 0.95,
            "average_latency": 5.0,
            "context_accuracy": 0.85
        }
    
    # Device Management Suite
    async def register_device(self, device: MobileDevice) -> bool:
        """Enregistre un nouvel appareil."""
        self.devices[device.device_id] = device
        self.performance_metrics["active_devices"] = len(self.devices)
        logger.info(f"Registered device: {device.device_id}")
        return True
    
    async def update_device_status(self, device_id -> None: str, status -> None: DeviceStatus) -> None:
        """Met à jour le statut d'un appareil."""
        if device_id in self.devices:
            self.devices[device_id].status = status
            self.devices[device_id].last_seen = datetime.utcnow()
    
    async def get_device_info(self, device_id: str) -> Optional[MobileDevice]:
        """Récupère les informations d'un appareil."""
        return self.devices.get(device_id)
    
    async def get_nearby_devices(self, device_id: str) -> List[MobileDevice]:
        """Récupère les appareils à proximité."""
        device = self.devices.get(device_id)
        if not device:
            return []
        
        all_devices = list(self.devices.values())
        return await self.proximity_detector.detect_nearby_devices(device, all_devices)
    
    # Context Awareness Engine
    async def collect_device_context(self, device_id: str, 
                                   sensors_data: Dict[str, Any]) -> ContextData:
        """Collecte le contexte d'un appareil."""
        return await self.context_engine.collect_context(device_id, sensors_data)
    
    async def get_user_activity(self, user_id: str) -> Optional[UserActivity]:
        """Récupère l'activité utilisateur actuelle."""
        # Search for current activity
        for activity in reversed(self.context_engine.activity_history):
            if (hasattr(activity, 'user_id') and 
                activity.user_id == user_id and 
                activity.get('end_time') is None):
                return activity
        return None
    
    # Mobility Prediction AI
    async def predict_device_mobility(self, device_id: str) -> Optional[MobilityPrediction]:
        """Prédit la mobilité d'un appareil."""
        device = self.devices.get(device_id)
        if not device or not device.location:
            return None
        
        # Get location history (simplified)
        location_history = [device.location]  # In real implementation, fetch from history
        
        return await self.mobility_ai.predict_mobility(
            device_id, device.location, location_history
        )
    
    # Handover Orchestration
    async def initiate_handover(self, device_id: str, target_edge: str, 
                               reason: HandoverReason = HandoverReason.NETWORK_OPTIMIZATION) -> bool:
        """Initie un handover."""
        device = self.devices.get(device_id)
        if not device:
            return False
        
        request = HandoverRequest(
            request_id=str(uuid.uuid4()),
            device_id=device_id,
            source_edge=device.metadata.get("current_edge", "unknown"),
            target_edge=target_edge,
            handover_type=HandoverType.SOFT,
            reason=reason,
            priority=0.8
        )
        
        return await self.handover_controller.initiate_handover(request)
    
    # Session Continuity Management
    async def create_user_session(self, user_id: str, device_id: str, 
                                edge_node: str) -> str:
        """Crée une session utilisateur."""
        session_id = await self.session_manager.create_session(user_id, device_id, edge_node)
        self.performance_metrics["active_sessions"] += 1
        return session_id
    
    async def checkpoint_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Crée un checkpoint de session."""
        return await self.session_manager.checkpoint_session(session_id, session_data)
    
    async def migrate_session(self, session_id: str, target_edge: str) -> bool:
        """Migre une session."""
        return await self.session_manager.migrate_session(session_id, target_edge)
    
    # Location Intelligence
    async def update_device_location(self, device_id -> None: str, location -> None: LocationData) -> None:
        """Met à jour la localisation d'un appareil."""
        if device_id in self.devices:
            self.devices[device_id].location = location
            await self.location_services.update_location(device_id, location)
    
    async def get_device_location(self, device_id: str) -> Optional[LocationData]:
        """Récupère la localisation d'un appareil."""
        device = self.devices.get(device_id)
        return device.location if device else None
    
    # Proximity Optimization
    async def optimize_proximity_services(self, device_id: str) -> Dict[str, Any]:
        """Optimise les services basés sur la proximité."""
        nearby_devices = await self.get_nearby_devices(device_id)
        
        optimization_suggestions = []
        
        if nearby_devices:
            # Suggest collaborative processing
            collaboration_capable = [d for d in nearby_devices 
                                   if DeviceCapability.CONTENT_CREATION in d.capabilities]
            if collaboration_capable:
                optimization_suggestions.append("Enable collaborative content creation")
            
            # Suggest resource sharing
            high_resource_devices = [d for d in nearby_devices 
                                   if d.resources.cpu_cores > 4]
            if high_resource_devices:
                optimization_suggestions.append("Enable edge computing offloading")
        
        return {
            "nearby_devices_count": len(nearby_devices),
            "optimization_suggestions": optimization_suggestions,
            "collaboration_opportunities": len([d for d in nearby_devices 
                                              if DeviceCapability.CONTENT_CREATION in d.capabilities])
        }
    
    # Edge Computing Coordination
    async def coordinate_edge_processing(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordonne le traitement edge."""
        # Analyze task requirements
        required_capabilities = task_data.get("required_capabilities", [])
        processing_requirements = task_data.get("processing_requirements", {})
        
        # Find suitable devices
        suitable_devices = []
        for device in self.devices.values():
            if (device.status == DeviceStatus.ACTIVE and
                all(cap in device.capabilities for cap in required_capabilities)):
                suitable_devices.append(device)
        
        # Select optimal device
        optimal_device = self._select_optimal_device(suitable_devices, processing_requirements)
        
        coordination_result = {
            "selected_device": optimal_device.device_id if optimal_device else None,
            "available_devices": len(suitable_devices),
            "coordination_success": optimal_device is not None
        }
        
        return coordination_result
    
    def _select_optimal_device(self, devices: List[MobileDevice], 
                             requirements: Dict[str, Any]) -> Optional[MobileDevice]:
        """Sélectionne l'appareil optimal."""
        if not devices:
            return None
        
        # Simple scoring based on resources
        best_device = None
        best_score = 0
        
        for device in devices:
            score = (device.resources.cpu_cores * 0.3 +
                    device.resources.memory_gb * 0.2 +
                    device.resources.battery_level * 0.3 +
                    device.resources.network_bandwidth * 0.2)
            
            if score > best_score:
                best_score = score
                best_device = device
        
        return best_device
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance."""
        self.performance_metrics.update({
            "active_devices": len([d for d in self.devices.values() 
                                 if d.status == DeviceStatus.ACTIVE]),
            "handover_success_rate": self.handover_controller.performance_metrics["success_rate"]
        })
        
        return self.performance_metrics
    
    async def shutdown(self) -> None:
        """Arrête le système MEC."""
        logger.info("Shutting down EdgeMECEnterprise")


def create_edge_mec_enterprise() -> EdgeMECEnterprise:
    """Factory function pour créer une instance MEC Enterprise."""
    return EdgeMECEnterprise()


# Exports principaux
__all__ = [
    "EdgeMECEnterprise",
    "MobileDevice",
    "DeviceType", 
    "DeviceCapability",
    "DeviceStatus",
    "DeviceResources",
    "LocationData",
    "NetworkType",
    "ContextData",
    "ContextType",
    "ActivityType",
    "UserActivity",
    "ContextAwarenessEngine",
    "MobilityPrediction",
    "MovementPattern",
    "MobilityPredictionAI",
    "HandoverType",
    "HandoverReason",
    "HandoverPolicy",
    "HandoverRequest",
    "HandoverController",
    "SessionState",
    "SessionInfo",
    "SessionContinuityManager",
    "ProximityDetector",
    "LocationServices",
    "create_edge_mec_enterprise"
]