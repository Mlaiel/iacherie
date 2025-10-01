"""
Analytics Tracking Module
Module de suivi analytique pour IA Chéries
LA DERNIÈRE PIÈCE POUR 100%!
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsEvent:
    """Événement analytique"""
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class AnalyticsTracker:
    """
    Système de suivi analytique principal
    Main analytics tracking system for 100% success
    """
    
    def __init__(self):
        """Initialise le tracker"""
        self.events: List[AnalyticsEvent] = []
        self.user_sessions: Dict[str, str] = {}
        
        logger.info("Analytics Tracker initialized - Ready for 100% tracking!")
    
    def track_event(self, event_type: str, user_id: Optional[str] = None, 
                   properties: Optional[Dict[str, Any]] = None) -> str:
        """Enregistre un événement"""
        if properties is None:
            properties = {}
        
        # Génère un session_id si nécessaire
        session_id = None
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = str(uuid.uuid4())
            session_id = self.user_sessions[user_id]
        
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            properties=properties
        )
        
        self.events.append(event)
        logger.debug(f"Tracked event: {event_type} for user: {user_id}")
        
        return event.event_id
    
    def track_user_action(self, action: str, user_id: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Enregistre une action utilisateur"""
        properties = {
            'action': action,
            'metadata': metadata or {}
        }
        
        return self.track_event('user_action', user_id, properties)
    
    def track_module_import(self, module_name: str, success: bool, 
                           user_id: Optional[str] = None) -> str:
        """Enregistre l'importation d'un module"""
        properties = {
            'module_name': module_name,
            'success': success,
            'import_type': 'module_load'
        }
        
        return self.track_event('module_import', user_id, properties)
    
    def track_authentication(self, auth_type: str, success: bool, 
                           user_id: Optional[str] = None) -> str:
        """Enregistre une tentative d'authentification"""
        properties = {
            'auth_type': auth_type,
            'success': success,
            'timestamp': time.time()
        }
        
        return self.track_event('authentication', user_id, properties)
    
    def track_security_scan(self, scan_type: str, results: Dict[str, Any], 
                           user_id: Optional[str] = None) -> str:
        """Enregistre un scan de sécurité"""
        properties = {
            'scan_type': scan_type,
            'results': results,
            'scan_timestamp': time.time()
        }
        
        return self.track_event('security_scan', user_id, properties)
    
    def track_audio_processing(self, operation: str, success: bool, 
                              metadata: Optional[Dict[str, Any]] = None,
                              user_id: Optional[str] = None) -> str:
        """Enregistre le traitement audio"""
        properties = {
            'operation': operation,
            'success': success,
            'metadata': metadata or {},
            'processing_timestamp': time.time()
        }
        
        return self.track_event('audio_processing', user_id, properties)
    
    def get_events(self, event_type: Optional[str] = None, 
                   user_id: Optional[str] = None) -> List[AnalyticsEvent]:
        """Récupère les événements filtrés"""
        filtered_events = self.events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        return filtered_events
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Retourne les données analytiques"""
        return {
            'total_events': len(self.events),
            'unique_users': len(set(e.user_id for e in self.events if e.user_id)),
            'event_types': list(set(e.event_type for e in self.events)),
            'active_sessions': len(self.user_sessions),
            'latest_events': [
                {
                    'event_type': e.event_type,
                    'user_id': e.user_id,
                    'timestamp': e.timestamp,
                    'properties': e.properties
                }
                for e in self.events[-10:]  # Derniers 10 événements
            ]
        }
    
    def clear_events(self) -> None:
        """Efface tous les événements"""
        self.events.clear()
        logger.info("Analytics events cleared")

# Instance globale
analytics_tracker = AnalyticsTracker()

# Alias pour compatibilité
EventTracker = AnalyticsTracker
UserTracker = AnalyticsTracker

# Fonctions utilitaires pour l'import facile
def track_event(event_type: str, user_id: Optional[str] = None, 
               properties: Optional[Dict[str, Any]] = None) -> str:
    """Fonction globale pour tracker un événement"""
    return analytics_tracker.track_event(event_type, user_id, properties)

def track_user_action(action: str, user_id: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
    """Fonction globale pour tracker une action utilisateur"""
    return analytics_tracker.track_user_action(action, user_id, metadata)

def track_module_import(module_name: str, success: bool, 
                       user_id: Optional[str] = None) -> str:
    """Fonction globale pour tracker l'importation d'un module"""
    return analytics_tracker.track_module_import(module_name, success, user_id)

def track_authentication(auth_type: str, success: bool, 
                        user_id: Optional[str] = None) -> str:
    """Fonction globale pour tracker l'authentification"""
    return analytics_tracker.track_authentication(auth_type, success, user_id)

def track_security_scan(scan_type: str, results: Dict[str, Any], 
                       user_id: Optional[str] = None) -> str:
    """Fonction globale pour tracker un scan de sécurité"""
    return analytics_tracker.track_security_scan(scan_type, results, user_id)

def track_audio_processing(operation: str, success: bool, 
                          metadata: Optional[Dict[str, Any]] = None,
                          user_id: Optional[str] = None) -> str:
    """Fonction globale pour tracker le traitement audio"""
    return analytics_tracker.track_audio_processing(operation, success, metadata, user_id)

def get_analytics_data() -> Dict[str, Any]:
    """Fonction globale pour obtenir les données analytiques"""
    return analytics_tracker.get_analytics_data()

def get_events(event_type: Optional[str] = None, 
               user_id: Optional[str] = None) -> List[AnalyticsEvent]:
    """Fonction globale pour obtenir les événements"""
    return analytics_tracker.get_events(event_type, user_id)

# Fonctions spécialisées pour les modules principaux
def track_iacheries_auth_success(user_id: str) -> str:
    """Track le succès de l'authentification IA Chéries"""
    return track_authentication('iacheries_auth', True, user_id)

def track_security_scanner_run(scan_results: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """Track l'exécution du scanner de sécurité"""
    return track_security_scan('comprehensive_scan', scan_results, user_id)

def track_tts_engine_usage(operation: str, success: bool, user_id: Optional[str] = None) -> str:
    """Track l'utilisation du moteur TTS"""
    return track_audio_processing(f'tts_{operation}', success, {'engine': 'tts'}, user_id)

def track_freesound_api_call(endpoint: str, success: bool, user_id: Optional[str] = None) -> str:
    """Track les appels à l'API Freesound"""
    return track_audio_processing(f'freesound_{endpoint}', success, {'api': 'freesound'}, user_id)

# Tracking automatique pour les imports de modules
def auto_track_module_success(module_name: str) -> None:
    """Track automatiquement le succès d'importation d'un module"""
    track_module_import(module_name, True)
    logger.info(f"Auto-tracked successful import: {module_name}")

logger.info("Analytics Tracking module loaded - 100% READY for victory!")