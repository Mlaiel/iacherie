"""Platform Monitoring Service - Service de surveillance multi-plateformes
======================================================================

Service centralisé de surveillance et monitoring en temps réel
de toutes les plateformes digitales pour protection de contenu.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor

from .web_monitor import WebContentMonitor
from .social_tracker import SocialMediaTracker
from .seo_crawler import SEOAnalyticsCrawler
from .piracy_detector import PiracyDetectionEngine
from .copyright_guardian import CopyrightGuardian
from ..ai.content_analysis import ContentAnalyzer
from ...utils.rate_limiter import RateLimiter
from ...utils.notification_manager import NotificationManager
from ...utils.metrics_collector import MetricsCollector


class MonitoringStatus(Enum):
    """
Statuts de surveillance"""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AlertPriority(Enum):
    """Priorités d'alertes"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class MonitoringTarget:
    """Cible de surveillance"""
    target_id: str
    target_type: str  # 'content', 'author', 'keyword', 'competitor'
    owner_id: str
    platforms: List[str]
    monitoring_rules: Dict[str, Any]
    created_at: datetime
    last_checked: Optional[datetime] = None
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    violation_count: int = 0
    alert_count: int = 0


@dataclass
class PlatformAlert:
    """
Alerte de plateforme"""
    alert_id: str
    target_id: str
    platform: str
    alert_type: str
    priority: AlertPriority
    message: str
    details: Dict[str, Any]
    created_at: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: str = ""


@dataclass
class MonitoringMetrics:
    """Métriques de surveillance"""
    targets_monitored: int
    platforms_covered: int
    violations_detected: int
    alerts_generated: int
    response_time_avg: float
    uptime_percentage: float
    last_updated: datetime


class PlatformMonitoringService:
    """
    Service centralisé de surveillance multi-plateformes
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le service de surveillance
        
        Args:
            config: Configuration du service
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Composants de surveillance
        self.web_monitor = WebContentMonitor(config.get('web_monitor', {}))
        self.social_tracker = SocialMediaTracker(config.get('social_tracker', {}))
        self.seo_crawler = SEOAnalyticsCrawler(config.get('seo_crawler', {}))
        self.piracy_detector = PiracyDetectionEngine(config.get('piracy_detector', {}))
        self.copyright_guardian = CopyrightGuardian(config.get('copyright_guardian', {}))
        
        # Services support
        self.content_analyzer = ContentAnalyzer()
        self.notification_manager = NotificationManager(config.get('notifications', {}))
        self.metrics_collector = MetricsCollector(config.get('metrics', {}))
        
        # Gestionnaire de taux
        self.rate_limiter = RateLimiter(
            max_requests=config.get('max_requests_per_minute', 120),
            window_seconds=60
        )
        
        # Données de surveillance
        self.monitoring_targets: Dict[str, MonitoringTarget] = {}
        self.platform_alerts: Dict[str, PlatformAlert] = {}
        self.monitoring_status = MonitoringStatus.STOPPED
        
        # Configuration des plateformes
        self.supported_platforms = {
            'youtube': {
                'name': 'YouTube',
                'api_available': True,
                'rate_limit': 100,
                'monitoring_capabilities': ['content', 'channel', 'comments']
            },
            'tiktok': {
                'name': 'TikTok',
                'api_available': False,
                'rate_limit': 50,
                'monitoring_capabilities': ['content', 'user', 'hashtag']
            },
            'instagram': {
                'name': 'Instagram',
                'api_available': True,
                'rate_limit': 200,
                'monitoring_capabilities': ['posts', 'stories', 'reels']
            },
            'twitter': {
                'name': 'Twitter/X',
                'api_available': True,
                'rate_limit': 300,
                'monitoring_capabilities': ['tweets', 'trends', 'users']
            },
            'facebook': {
                'name': 'Facebook',
                'api_available': True,
                'rate_limit': 200,
                'monitoring_capabilities': ['posts', 'pages', 'groups']
            },
            'linkedin': {
                'name': 'LinkedIn',
                'api_available': True,
                'rate_limit': 100,
                'monitoring_capabilities': ['posts', 'articles', 'companies']
            },
            'spotify': {
                'name': 'Spotify',
                'api_available': True,
                'rate_limit': 100,
                'monitoring_capabilities': ['tracks', 'playlists', 'artists']
            },
            'soundcloud': {
                'name': 'SoundCloud',
                'api_available': True,
                'rate_limit': 100,
                'monitoring_capabilities': ['tracks', 'users', 'playlists']
            }
        }
        
        # Métriques en temps réel
        self.real_time_metrics = MonitoringMetrics(
            targets_monitored=0,
            platforms_covered=0,
            violations_detected=0,
            alerts_generated=0,
            response_time_avg=0.0,
            uptime_percentage=100.0,
            last_updated=datetime.now()
        )
        
        # Websocket pour temps réel
        self.websocket_clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Pool de threads pour surveillance
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))

    async def add_monitoring_target(
        self,
        target_type: str,
        target_data: Dict[str, Any],
        owner_id: str,
        platforms: List[str],
        monitoring_rules: Dict[str, Any] = None
    ) -> str:
        """
        Ajoute une nouvelle cible de surveillance
        
        Args:
            target_type: Type de cible ('content', 'author', 'keyword', 'competitor')
            target_data: Données de la cible
            owner_id: Propriétaire de la surveillance
            platforms: Plateformes à surveiller
            monitoring_rules: Règles de surveillance
            
        Returns:
            str: ID de la cible créée
        """
        try:
            target_id = self._generate_target_id(target_type, target_data)
            
            # Validation des plateformes
            invalid_platforms = [p for p in platforms if p not in self.supported_platforms]
            if invalid_platforms:
                raise ValueError(f"Plateformes non supportées: {invalid_platforms}")
            
            # Création de la cible
            target = MonitoringTarget(
                target_id=target_id,
                target_type=target_type,
                owner_id=owner_id,
                platforms=platforms,
                monitoring_rules=monitoring_rules or {},
                created_at=datetime.now()
            )
            
            # Ajout aux différents composants de surveillance
            await self._register_target_with_components(target, target_data)
            
            # Sauvegarde
            self.monitoring_targets[target_id] = target
            
            # Mise à jour des métriques
            self._update_monitoring_metrics()
            
            # Notification
            await self._notify_target_added(target)
            
            self.logger.info(f"Cible de surveillance ajoutée: {target_id}")
            return target_id
            
        except Exception as e:
            self.logger.error(f"Erreur ajout cible surveillance: {e}")
            raise

    def _generate_target_id(self, target_type: str, target_data: Dict[str, Any]) -> str:
        """Génère un ID unique pour la cible"""
        import hashlib
        
        data_string = f"{target_type}_{target_data}_{datetime.now().timestamp()}"
        hash_suffix = hashlib.md5(data_string.encode()).hexdigest()[:8]
        
        return f"{target_type}_{hash_suffix}".upper()

    async def _register_target_with_components(
        self,
        target: MonitoringTarget,
        target_data: Dict[str, Any]
    ) -> None:
        """Enregistre la cible avec les composants appropriés"""
        try:
            if target.target_type == 'content':
                # Enregistrement pour protection copyright
                await self.copyright_guardian.register_copyright(
                    target.target_id, target.owner_id, target_data
                )
                
                # Enregistrement pour détection piratage
                await self.piracy_detector.register_protected_content(
                    target.target_id, target_data['url'], target_data['type'], target.owner_id
                )
                
                # Ajout au monitoring web
                from .web_monitor import MonitoringTarget as WebTarget
                web_target = WebTarget(
                    url=target_data['url'],
                    content_type=target_data['type'],
                    owner_id=target.owner_id,
                    fingerprint_hash="",  # Sera généré
                    monitoring_frequency=target.monitoring_rules.get('frequency', 24)
                )
                await self.web_monitor.add_monitoring_target(web_target)
            
            elif target.target_type == 'author':
                # Surveillance des contenus d'un auteur
                await self._setup_author_monitoring(target, target_data)
            
            elif target.target_type == 'keyword':
                # Surveillance par mots-clés
                await self._setup_keyword_monitoring(target, target_data)
            
            elif target.target_type == 'competitor':
                # Surveillance concurrentielle
                await self._setup_competitor_monitoring(target, target_data)
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement avec composants: {e}")

    async def _setup_author_monitoring(
        self,
        target: MonitoringTarget,
        target_data: Dict[str, Any]
    ) -> None:
        """Configure la surveillance d'un auteur"""
        author_name = target_data.get('author_name', '')
        
        # Génération de mots-clés de recherche
        search_keywords = [
            author_name,
            f'"{author_name}"',
            f'{author_name} content',
            f'{author_name} unauthorized'
        ]
        
        # Configuration surveillance sociale
        if 'social_handles' in target_data:
            for platform, handle in target_data['social_handles'].items():
                if platform in target.platforms:
                    # Ajout à la surveillance sociale
                    pass

    async def _setup_keyword_monitoring(
        self,
        target: MonitoringTarget,
        target_data: Dict[str, Any]
    ) -> None:
        """Configure la surveillance par mots-clés"""
        keywords = target_data.get('keywords', [])
        
        # Configuration SEO monitoring
        if any(p in ['google', 'bing', 'yahoo'] for p in target.platforms):
            # Surveillance rankings SEO
            pass

    async def _setup_competitor_monitoring(
        self,
        target: MonitoringTarget,
        target_data: Dict[str, Any]
    ) -> None:
        """
Configure la surveillance concurrentielle"""
        competitor_urls = target_data.get('competitor_urls', [])
        shared_keywords = target_data.get('shared_keywords', [])
        
        # Analyse concurrentielle
        for url in competitor_urls:
            # Ajout au SEO crawler pour analyse
            pass

    async def start_monitoring(self) -> None:
        """
Démarre le service de surveillance"""
        try:
            self.monitoring_status = MonitoringStatus.ACTIVE
            self.logger.info("Démarrage du service de surveillance multi-plateformes")
            
            # Démarrage des composants
            monitoring_tasks = [
                asyncio.create_task(self._run_web_monitoring()),
                asyncio.create_task(self._run_social_monitoring()),
                asyncio.create_task(self._run_seo_monitoring()),
                asyncio.create_task(self._run_piracy_monitoring()),
                asyncio.create_task(self._run_metrics_collection()),
                asyncio.create_task(self._run_alert_processing()),
                asyncio.create_task(self._run_websocket_server())
            ]
            
            # Surveillance continue
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage surveillance: {e}")
            self.monitoring_status = MonitoringStatus.ERROR

    async def _run_web_monitoring(self) -> None:
        """Exécute la surveillance web"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Surveillance web générale
                await self.web_monitor.start_monitoring()
                
                # Pause configurée
                await asyncio.sleep(self.config.get('web_monitoring_interval', 3600))
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance web: {e}")
                await asyncio.sleep(60)

    async def _run_social_monitoring(self) -> None:
        """Exécute la surveillance des réseaux sociaux"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Pour chaque cible de surveillance
                for target_id, target in self.monitoring_targets.items():
                    if target.status != MonitoringStatus.ACTIVE:
                        continue
                    
                    social_platforms = [
                        p for p in target.platforms 
                        if p in ['youtube', 'tiktok', 'instagram', 'twitter', 'facebook']
                    ]
                    
                    if social_platforms:
                        await self._monitor_target_on_social_platforms(target, social_platforms)
                
                await asyncio.sleep(self.config.get('social_monitoring_interval', 1800))
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance sociale: {e}")
                await asyncio.sleep(60)

    async def _monitor_target_on_social_platforms(
        self,
        target: MonitoringTarget,
        platforms: List[str]
    ) -> None:
        """Surveille une cible sur les plateformes sociales"""
        try:
            await self.rate_limiter.acquire()
            
            # Génération de mots-clés pour la recherche
            search_keywords = self._generate_search_keywords_for_target(target)
            
            # Surveillance sur chaque plateforme
            for platform in platforms:
                violations = await self._search_platform_for_violations(
                    platform, target, search_keywords
                )
                
                # Traitement des violations trouvées
                for violation in violations:
                    await self._process_violation_detection(target, violation, platform)
            
            # Mise à jour de la dernière vérification
            target.last_checked = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Erreur surveillance cible {target.target_id}: {e}")

    def _generate_search_keywords_for_target(self, target: MonitoringTarget) -> List[str]:
        """Génère des mots-clés de recherche pour une cible"""
        keywords = []
        
        # Mots-clés basés sur les règles de surveillance
        if 'keywords' in target.monitoring_rules:
            keywords.extend(target.monitoring_rules['keywords'])
        
        # Mots-clés par défaut selon le type
        if target.target_type == 'content':
            keywords.extend(['unauthorized', 'pirated', 'leaked'])
        elif target.target_type == 'author':
            keywords.extend(['content', 'work', 'creation'])
        
        return list(set(keywords))

    async def _search_platform_for_violations(
        self,
        platform: str,
        target: MonitoringTarget,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
Recherche de violations sur une plateforme"""
        violations = []
        
        try:
            if platform == 'youtube':
                violations = await self._search_youtube_violations(target, keywords)
            elif platform == 'tiktok':
                violations = await self._search_tiktok_violations(target, keywords)
            elif platform == 'instagram':
                violations = await self._search_instagram_violations(target, keywords)
            elif platform == 'twitter':
                violations = await self._search_twitter_violations(target, keywords)
            elif platform == 'facebook':
                violations = await self._search_facebook_violations(target, keywords)
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Erreur recherche {platform}: {e}")
            return []

    async def _search_youtube_violations(
        self,
        target: MonitoringTarget,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Recherche de violations sur YouTube"""
        # Utilise le social tracker
        # Implémentation spécialisée YouTube
        return []

    async def _search_tiktok_violations(
        self,
        target: MonitoringTarget,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
Recherche de violations sur TikTok"""
        # Implémentation spécialisée TikTok
        return []

    async def _search_instagram_violations(
        self,
        target: MonitoringTarget,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
Recherche de violations sur Instagram"""
        # Implémentation spécialisée Instagram
        return []

    async def _search_twitter_violations(
        self,
        target: MonitoringTarget,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
Recherche de violations sur Twitter"""
        # Implémentation spécialisée Twitter
        return []

    async def _search_facebook_violations(
        self,
        target: MonitoringTarget,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
Recherche de violations sur Facebook"""
        # Implémentation spécialisée Facebook
        return []

    async def _process_violation_detection(
        self,
        target: MonitoringTarget,
        violation: Dict[str, Any],
        platform: str
    ) -> None:
        """
Traite une violation détectée"""
        try:
            # Mise à jour des compteurs
            target.violation_count += 1
            
            # Création d'une alerte
            alert = await self._create_violation_alert(target, violation, platform)
            
            # Sauvegarde de l'alerte
            self.platform_alerts[alert.alert_id] = alert
            target.alert_count += 1
            
            # Notification si priorité élevée
            if alert.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH]:
                await self._send_immediate_notification(alert)
            
            # Actions automatiques si configurées
            if self.config.get('auto_actions_enabled', False):
                await self._trigger_automatic_actions(alert, violation)
            
        except Exception as e:
            self.logger.error(f"Erreur traitement violation: {e}")

    async def _create_violation_alert(
        self,
        target: MonitoringTarget,
        violation: Dict[str, Any],
        platform: str
    ) -> PlatformAlert:
        """Crée une alerte de violation"""
        alert_id = self._generate_alert_id()
        
        # Détermination de la priorité
        priority = self._determine_alert_priority(violation)
        
        alert = PlatformAlert(
            alert_id=alert_id,
            target_id=target.target_id,
            platform=platform,
            alert_type='violation_detected',
            priority=priority,
            message=f"Violation détectée sur {platform}",
            details={
                'violation_url': violation.get('url', ''),
                'similarity_score': violation.get('similarity_score', 0.0),
                'violation_type': violation.get('type', ''),
                'uploader': violation.get('uploader', ''),
                'view_count': violation.get('view_count', 0)
            },
            created_at=datetime.now()
        )
        
        return alert

    def _generate_alert_id(self) -> str:
        """Génère un ID unique pour l'alerte"""
        import uuid
        return f"ALT_{uuid.uuid4().hex[:8].upper()}"

    def _determine_alert_priority(self, violation: Dict[str, Any]) -> AlertPriority:
        """Détermine la priorité de l'alerte"""
        similarity_score = violation.get('similarity_score', 0.0)
        view_count = violation.get('view_count', 0)
        commercial_use = violation.get('commercial_use', False)
        
        if similarity_score > 0.95 and commercial_use:
            return AlertPriority.CRITICAL
        elif similarity_score > 0.9 or view_count > 10000:
            return AlertPriority.HIGH
        elif similarity_score > 0.8 or view_count > 1000:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW

    async def _send_immediate_notification(self, alert: PlatformAlert) -> None:
        """
Envoie une notification immédiate"""
        notification_data = {
            'type': 'violation_alert',
            'alert_id': alert.alert_id,
            'priority': alert.priority.value,
            'platform': alert.platform,
            'message': alert.message,
            'details': alert.details,
            'timestamp': alert.created_at.isoformat()
        }
        
        await self.notification_manager.send_immediate_alert(notification_data)

    async def _trigger_automatic_actions(
        self,
        alert: PlatformAlert,
        violation: Dict[str, Any]
    ) -> None:
        """
Déclenche des actions automatiques"""
        try:
            if alert.priority == AlertPriority.CRITICAL:
                # Actions d'urgence
                await self._execute_emergency_actions(alert, violation)
            
            elif alert.priority == AlertPriority.HIGH:
                # Actions rapides
                await self._execute_rapid_actions(alert, violation)
            
        except Exception as e:
            self.logger.error(f"Erreur actions automatiques: {e}")

    async def _execute_emergency_actions(
        self,
        alert: PlatformAlert,
        violation: Dict[str, Any]
    ) -> None:
        """Exécute des actions d'urgence"""
        # DMCA automatique
        if self.config.get('auto_dmca_critical', True):
            await self._send_automated_dmca(alert, violation)
        
        # Notification aux parties prenantes
        await self._notify_stakeholders_emergency(alert)

    async def _execute_rapid_actions(
        self,
        alert: PlatformAlert,
        violation: Dict[str, Any]
    ) -> None:
        """
Exécute des actions rapides"""
        # Collecte d'évidence
        await self._collect_evidence_automatically(alert, violation)
        
        # Préparation takedown
        await self._prepare_takedown_request(alert, violation)

    async def _send_automated_dmca(
        self,
        alert: PlatformAlert,
        try:
            logger.info(f"Executing _send_automated_dmca")
            
            # Implementation for _send_automated_dmca
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_send_automated_dmca completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing _notify_stakeholders_emergency")
            
            # Implementation for _notify_stakeholders_emergency
            # TODO: Add specific business logic here
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "_collect_evidence_automatically",
                        "value": alert if alert else 0,
                        "tags": self._get_metric_tags()
        try:
            logger.info(f"Executing _prepare_takedown_request")
            
            # Implementation for _prepare_takedown_request
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_prepare_takedown_request completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_prepare_takedown_request failed: {e}")
            raise
                    logger.info(f"Metric _collect_evidence_automatically collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection _collect_evidence_automatically failed: {e}")
                    return None
        except Exception as e:
            logger.error(f"_notify_stakeholders_emergency failed: {e}")
            raise
            logger.error(f"_send_automated_dmca failed: {e}")
            raise
    async def _notify_stakeholders_emergency(self, alert: PlatformAlert) -> None:
        """
Notifie les parties prenantes en urgence"""
        # Notifications d'urgence
        pass

    async def _collect_evidence_automatically(
        self,
        alert: PlatformAlert,
        try:
                    # Request validation
                    if not target:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__monitor_seo_for_target_request(target)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _monitor_seo_for_target failed: {e}")
                    return {"status": "error", "message": str(e)}
        alert: PlatformAlert,
        violation: Dict[str, Any]
    ) -> None:
        """
Collecte automatiquement les preuves"""
        # Collecte d'évidence
        pass

    async def _prepare_takedown_request(
        self,
        alert: PlatformAlert,
        violation: Dict[str, Any]
    ) -> None:
        """
Prépare une demande de takedown"""
        # Préparation takedown
        pass

    async def _run_seo_monitoring(self) -> None:
        """
Exécute la surveillance SEO"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Surveillance SEO
                seo_targets = [
                    t for t in self.monitoring_targets.values()
                    if 'seo' in t.monitoring_rules.get('types', [])
                ]
                
                for target in seo_targets:
                    await self._monitor_seo_for_target(target)
                
                await asyncio.sleep(self.config.get('seo_monitoring_interval', 7200))
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance SEO: {e}")
                await asyncio.sleep(60)

    async def _monitor_seo_for_target(self, target: MonitoringTarget) -> None:
        """Surveille le SEO pour une cible"""
        # Implémentation surveillance SEO
        pass

    async def _run_piracy_monitoring(self) -> None:
        """
Exécute la surveillance de piratage"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Surveillance piratage
                await self.piracy_detector.continuous_piracy_monitoring(
                    self.config.get('piracy_monitoring_interval', 3600)
                )
                
            except Exception as e:
                self.logger.error(f"Erreur surveillance piratage: {e}")
                await asyncio.sleep(60)

    async def _run_metrics_collection(self) -> None:
        """Collecte les métriques en temps réel"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Mise à jour des métriques
                self._update_monitoring_metrics()
                
                # Envoi aux clients WebSocket
                await self._broadcast_metrics_update()
                
                await asyncio.sleep(30)  # Mise à jour toutes les 30 secondes
                
            except Exception as e:
                self.logger.error(f"Erreur collecte métriques: {e}")
                await asyncio.sleep(60)

    def _update_monitoring_metrics(self) -> None:
        """Met à jour les métriques de surveillance"""
        self.real_time_metrics.targets_monitored = len(self.monitoring_targets)
        self.real_time_metrics.platforms_covered = len(set(
            platform for target in self.monitoring_targets.values()
            for platform in target.platforms
        ))
        self.real_time_metrics.violations_detected = sum(
            target.violation_count for target in self.monitoring_targets.values()
        )
        self.real_time_metrics.alerts_generated = len(self.platform_alerts)
        self.real_time_metrics.last_updated = datetime.now()

    async def _broadcast_metrics_update(self) -> None:
        """
Diffuse les métriques via WebSocket"""
        if self.websocket_clients:
            metrics_data = {
                'type': 'metrics_update',
                'data': asdict(self.real_time_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            # Envoi à tous les clients connectés
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(json.dumps(metrics_data, default=str))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
            
            # Nettoyage des clients déconnectés
            self.websocket_clients -= disconnected_clients

    async def _run_alert_processing(self) -> None:
        """
Traite les alertes en continu"""
        while self.monitoring_status == MonitoringStatus.ACTIVE:
            try:
                # Traitement des alertes non résolues
                unresolved_alerts = [
                    alert for alert in self.platform_alerts.values()
                    if not alert.resolved
                ]
                
                for alert in unresolved_alerts:
                    await self._process_alert(alert)
                
                await asyncio.sleep(60)  # Vérification chaque minute
                
            except Exception as e:
                self.logger.error(f"Erreur traitement alertes: {e}")
                await asyncio.sleep(60)

    async def _process_alert(self, alert: PlatformAlert) -> None:
        """Traite une alerte spécifique"""
        # Vérification si l'alerte nécessite un suivi
        if alert.priority == AlertPriority.CRITICAL:
            # Suivi critique toutes les 15 minutes
            if (datetime.now() - alert.created_at).total_seconds() > 900:
                await self._escalate_alert(alert)

    async def _escalate_alert(self, alert: PlatformAlert) -> None:
        """
Escalade une alerte"""
        # Escalade vers un niveau supérieur
        await self.notification_manager.send_escalation_notice(alert)

    async def _run_websocket_server(self) -> None:
        """
Démarre le serveur WebSocket pour temps réel"""
        try:
            async def handle_client(websocket, path):
                self.websocket_clients.add(websocket)
                try:
                    await websocket.wait_closed()
                finally:
                    self.websocket_clients.discard(websocket)
            
            # Démarrage du serveur WebSocket
            port = self.config.get('websocket_port', 8765)
            await websockets.serve(handle_client, "localhost", port)
            
            self.logger.info(f"Serveur WebSocket démarré sur le port {port}")
            
        except Exception as e:
            self.logger.error(f"Erreur serveur WebSocket: {e}")

    async def stop_monitoring(self) -> None:
        """Arrête le service de surveillance"""
        self.monitoring_status = MonitoringStatus.STOPPED
        self.logger.info("Service de surveillance arrêté")

    async def pause_monitoring(self) -> None:
        """Met en pause la surveillance"""
        self.monitoring_status = MonitoringStatus.PAUSED
        self.logger.info("Service de surveillance mis en pause")

    async def resume_monitoring(self) -> None:
        """Reprend la surveillance"""
        self.monitoring_status = MonitoringStatus.ACTIVE
        self.logger.info("Service de surveillance repris")

    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """
        Retourne les données du dashboard de surveillance
        
        Returns:
            Dict[str, Any]: Données du dashboard
        """
        return {
            'status': self.monitoring_status.value,
            'metrics': asdict(self.real_time_metrics),
            'targets_summary': {
                'total': len(self.monitoring_targets),
                'active': len([t for t in self.monitoring_targets.values() if t.status == MonitoringStatus.ACTIVE]),
                'by_type': self._get_targets_by_type_stats(),
                'top_platforms': self._get_top_platforms_stats()
            },
            'alerts_summary': {
                'total': len(self.platform_alerts),
                'unresolved': len([a for a in self.platform_alerts.values() if not a.resolved]),
                'by_priority': self._get_alerts_by_priority_stats(),
                'recent': self._get_recent_alerts()
            },
            'performance': {
                'uptime': self.real_time_metrics.uptime_percentage,
                'response_time': self.real_time_metrics.response_time_avg,
                'success_rate': self._calculate_monitoring_success_rate()
            }
        }

    def _get_targets_by_type_stats(self) -> Dict[str, int]:
        """
Statistiques des cibles par type"""
        stats = {}
        for target in self.monitoring_targets.values():
            target_type = target.target_type
            stats[target_type] = stats.get(target_type, 0) + 1
        return stats

    def _get_top_platforms_stats(self) -> List[Dict[str, Any]]:
        """
Statistiques des principales plateformes"""
        platform_counts = {}
        for target in self.monitoring_targets.values():
            for platform in target.platforms:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return [
            {'platform': platform, 'count': count}
            for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]

    def _get_alerts_by_priority_stats(self) -> Dict[str, int]:
        """
Statistiques des alertes par priorité"""
        stats = {}
        for alert in self.platform_alerts.values():
            priority = alert.priority.value
            stats[priority] = stats.get(priority, 0) + 1
        return stats

    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """
Alertes récentes"""
        recent_alerts = sorted(
            self.platform_alerts.values(),
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        return [
            {
                'alert_id': alert.alert_id,
                'platform': alert.platform,
                'priority': alert.priority.value,
                'message': alert.message,
                'created_at': alert.created_at.isoformat(),
                'resolved': alert.resolved
            }
            for alert in recent_alerts
        ]

    def _calculate_monitoring_success_rate(self) -> float:
        """
Calcule le taux de succès de surveillance"""
        total_targets = len(self.monitoring_targets)
        successful_targets = len([
            t for t in self.monitoring_targets.values()
            if t.last_checked and (datetime.now() - t.last_checked).total_seconds() < 86400
        ])
        
        return (successful_targets / total_targets * 100) if total_targets > 0 else 100.0

    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Acquitte une alerte
        
        Args:
            alert_id: ID de l'alerte
            user_id: Utilisateur qui acquitte
            
        Returns:
            bool: Succès de l'acquittement
        """
        if alert_id in self.platform_alerts:
            alert = self.platform_alerts[alert_id]
            alert.acknowledged = True
            
            self.logger.info(f"Alerte {alert_id} acquittée par {user_id}")
            return True
        
        return False

    async def resolve_alert(
        self,
        alert_id: str,
        resolution_notes: str,
        user_id: str
    ) -> bool:
        """
        Résout une alerte
        
        Args:
            alert_id: ID de l'alerte
            resolution_notes: Notes de résolution
            user_id: Utilisateur qui résout
            
        Returns:
            bool: Succès de la résolution
        """
        if alert_id in self.platform_alerts:
            alert = self.platform_alerts[alert_id]
            alert.resolved = True
            alert.resolution_notes = resolution_notes
            
            self.logger.info(f"Alerte {alert_id} résolue par {user_id}")
            return True
        
        return False

    async def _notify_target_added(self, target: MonitoringTarget) -> None:
        """Notifie qu'une cible a été ajoutée"""
        notification_data = {
            'type': 'target_added',
            'target_id': target.target_id,
            'target_type': target.target_type,
            'platforms': target.platforms,
            'owner_id': target.owner_id,
            'created_at': target.created_at.isoformat()
        }
        
        await self.notification_manager.send_system_notification(notification_data)
