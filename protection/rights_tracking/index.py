"""Rights Tracking Module - Service Initialization and Entry Point
Point d'entrée principal du module de suivi des droits
Système d'initialisation et coordination des services
"""

import asyncio
import logging
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json

# Import des services principaux
from . import get_rights_tracking_service
from .ownership_registry import OwnershipRegistry
from .licensing_engine import LicensingEngine
from .usage_monitor import UsageMonitor
from .royalty_calculator import RoyaltyCalculator
from .territory_manager import TerritoryManager
from .database_manager import DatabaseManager
from .config import RightsTrackingConfig

# Configuration du logging
logger = logging.getLogger(__name__)


class RightsTrackingOrchestrator:
    """
Orchestrateur principal des services de suivi des droits"""
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config = RightsTrackingConfig(config_path)
        self.services = {}
        self.running = False
        self.health_status = {}
        self.startup_timestamp = None
        
        # Services à initialiser
        self.service_registry = {
            'database_manager': DatabaseManager,
            'ownership_registry': OwnershipRegistry,
            'licensing_engine': LicensingEngine,
            'usage_monitor': UsageMonitor,
            'royalty_calculator': RoyaltyCalculator,
            'territory_manager': TerritoryManager
        }
    
    async def initialize(self) -> bool:
        """
Initialise tous les services du module"""
        try:
            logger.info("🚀 Initialisation du module Rights Tracking...")
            self.startup_timestamp = datetime.utcnow()
            
            # 1. Initialisation de la base de données
            logger.info("📊 Initialisation de la base de données...")
            self.services['database_manager'] = DatabaseManager(self.config.database)
            await self.services['database_manager'].initialize()
            
            # 2. Chargement des configurations
            logger.info("⚙️ Chargement des configurations...")
            await self._load_configurations()
            
            # 3. Initialisation des services principaux
            logger.info("🔧 Initialisation des services principaux...")
            await self._initialize_core_services()
            
            # 4. Démarrage des tâches de surveillance
            logger.info("👁️ Démarrage des tâches de surveillance...")
            await self._start_monitoring_tasks()
            
            # 5. Vérification de l'état des services
            logger.info("✅ Vérification de l'état des services...")
            health_check = await self.health_check()
            
            if health_check['overall_status'] == 'healthy':
                self.running = True
                logger.info("🎉 Module Rights Tracking initialisé avec succès!")
                await self._log_startup_summary()
                return True
            else:
                logger.error("❌ Échec de l'initialisation du module")
                return False
                
        except Exception as e:
            logger.error(f"💥 Erreur critique lors de l'initialisation: {e}")
            await self.shutdown()
            return False
    
    async def _initialize_core_services(self) -> None:
        """Initialise les services principaux"""
        initialization_order = [
            'ownership_registry',
            'territory_manager', 
            'licensing_engine',
            'royalty_calculator',
            'usage_monitor'
        ]
        
        for service_name in initialization_order:
            try:
                logger.info(f"🔄 Initialisation de {service_name}...")
                
                service_class = self.service_registry[service_name]
                service_config = getattr(self.config, service_name, {})
                
                service_instance = service_class(service_config)
                await service_instance.initialize()
                
                self.services[service_name] = service_instance
                self.health_status[service_name] = 'healthy'
                
                logger.info(f"✅ {service_name} initialisé")
                
            except Exception as e:
                logger.error(f"❌ Erreur initialisation {service_name}: {e}")
                self.health_status[service_name] = 'error'
                raise
    
    async def _start_monitoring_tasks(self) -> None:
        """Démarre les tâches de surveillance en arrière-plan"""
        try:
            # Tâche de monitoring de santé général
            asyncio.create_task(self._health_monitoring_loop())
            
            # Tâche de nettoyage automatique
            asyncio.create_task(self._cleanup_task())
            
            # Tâche de sauvegarde automatique
            asyncio.create_task(self._backup_task())
            
            # Tâche de mise à jour des statistiques
            asyncio.create_task(self._statistics_update_task())
            
            logger.info("📈 Tâches de surveillance démarrées")
            
        except Exception as e:
            logger.error(f"Erreur démarrage tâches surveillance: {e}")
            raise
    
    async def _load_configurations(self) -> None:
        """Charge les configurations spécialisées"""
        try:
            # Chargement des templates de licence
            if hasattr(self.config, 'license_templates_path'):
                await self._load_license_templates()
            
            # Chargement des règles de tarification
            if hasattr(self.config, 'pricing_rules_path'):
                await self._load_pricing_rules()
            
            # Chargement des configurations territoriales
            if hasattr(self.config, 'territory_config_path'):
                await self._load_territory_configurations()
            
            logger.info("📋 Configurations chargées")
            
        except Exception as e:
            logger.error(f"Erreur chargement configurations: {e}")
            raise
    
    async def _load_license_templates(self) -> None:
        """Charge les templates de licence depuis fichier"""
        try:
            templates_path = Path(self.config.license_templates_path)
            if templates_path.exists():
                with open(templates_path, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                
                logger.info(f"📄 {len(templates_data)} templates de licence chargés")
            else:
                logger.warning("⚠️ Fichier templates de licence non trouvé, utilisation des defaults")
                
        except Exception as e:
            logger.error(f"Erreur chargement templates: {e}")
    
    async def _load_pricing_rules(self) -> None:
        """Charge les règles de tarification"""
        try:
            rules_path = Path(self.config.pricing_rules_path)
            if rules_path.exists():
                with open(rules_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                
                logger.info(f"💰 {len(rules_data)} règles de tarification chargées")
            else:
                logger.warning("⚠️ Fichier règles de tarification non trouvé")
                
        except Exception as e:
            logger.error(f"Erreur chargement règles tarification: {e}")
    
    async def _load_territory_configurations(self) -> None:
        """Charge les configurations territoriales"""
        try:
            territory_path = Path(self.config.territory_config_path)
            if territory_path.exists():
                with open(territory_path, 'r', encoding='utf-8') as f:
                    territory_data = json.load(f)
                
                logger.info(f"🌍 {len(territory_data)} configurations territoriales chargées")
            else:
                logger.warning("⚠️ Fichier configurations territoriales non trouvé")
                
        except Exception as e:
            logger.error(f"Erreur chargement configurations territoriales: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de santé de tous les services"""
        try:
            health_report = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'healthy',
                'services': {},
                'uptime_seconds': 0,
                'version': '1.0.0'
            }
            
            if self.startup_timestamp:
                uptime = (datetime.utcnow() - self.startup_timestamp).total_seconds()
                health_report['uptime_seconds'] = uptime
            
            # Vérification de chaque service
            unhealthy_services = 0
            for service_name, service_instance in self.services.items():
                try:
                    if hasattr(service_instance, 'health_check'):
                        service_health = await service_instance.health_check()
                    else:
                        # Service basique sans health check
                        service_health = {'status': 'healthy', 'details': 'No health check available'}
                    
                    health_report['services'][service_name] = service_health
                    
                    if service_health.get('status') != 'healthy':
                        unhealthy_services += 1
                        
                except Exception as e:
                    health_report['services'][service_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    unhealthy_services += 1
            
            # Détermination du statut global
            total_services = len(self.services)
            if unhealthy_services == 0:
                health_report['overall_status'] = 'healthy'
            elif unhealthy_services < total_services / 2:
                health_report['overall_status'] = 'degraded'
            else:
                health_report['overall_status'] = 'unhealthy'
            
            health_report['healthy_services'] = total_services - unhealthy_services
            health_report['total_services'] = total_services
            
            return health_report
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques de tous les services"""
        try:
            stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'module_uptime_seconds': 0,
                'services_stats': {}
            }
            
            if self.startup_timestamp:
                uptime = (datetime.utcnow() - self.startup_timestamp).total_seconds()
                stats['module_uptime_seconds'] = uptime
            
            # Collecte des statistiques de chaque service
            for service_name, service_instance in self.services.items():
                try:
                    if hasattr(service_instance, 'get_statistics'):
                        service_stats = await service_instance.get_statistics()
                        stats['services_stats'][service_name] = service_stats
                    else:
                        stats['services_stats'][service_name] = {
                            'status': 'running',
                            'stats_available': False
                        }
                        
                except Exception as e:
                    stats['services_stats'][service_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # Statistiques globales du module
            stats['global_metrics'] = await self._calculate_global_metrics()
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques: {e}")
            return {'error': str(e)}
    
    async def _calculate_global_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques globales du module"""
        try:
            metrics = {
                'total_rights_records': 0,
                'total_licenses': 0,
                'total_usage_events': 0,
                'total_royalty_calculations': 0,
                'active_territories': 0
            }
            
            # Agrégation des métriques des différents services
            if 'ownership_registry' in self.services:
                registry_stats = await self.services['ownership_registry'].get_statistics()
                metrics['total_rights_records'] = registry_stats.get('total_registered_contents', 0)
            
            if 'licensing_engine' in self.services:
                licensing_stats = await self.services['licensing_engine'].get_licensing_statistics()
                metrics['total_licenses'] = licensing_stats.get('total_licenses_generated', 0)
            
            if 'usage_monitor' in self.services:
                usage_stats = await self.services['usage_monitor'].get_monitoring_statistics()
                metrics['total_usage_events'] = usage_stats.get('total_events_processed', 0)
            
            if 'royalty_calculator' in self.services:
                royalty_stats = await self.services['royalty_calculator'].get_calculation_statistics()
                metrics['total_royalty_calculations'] = royalty_stats.get('total_calculations', 0)
            
            if 'territory_manager' in self.services:
                territory_stats = await self.services['territory_manager'].get_territory_statistics()
                metrics['active_territories'] = territory_stats.get('active_territories_count', 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques globales: {e}")
            return {}
    
    async def _health_monitoring_loop(self) -> None:
        """Boucle de surveillance de santé continue"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Vérification toutes les 5 minutes
                
                health_report = await self.health_check()
                
                if health_report['overall_status'] == 'unhealthy':
                    logger.warning("⚠️ Module Rights Tracking en état dégradé")
                    await self._handle_unhealthy_state(health_report)
                elif health_report['overall_status'] == 'degraded':
                    logger.info("🔶 Certains services du module sont dégradés")
                    await self._handle_degraded_state(health_report)
                
            except Exception as e:
                logger.error(f"Erreur surveillance santé: {e}")
    
    async def _cleanup_task(self) -> None:
        """Tâche de nettoyage automatique"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
                
                logger.info("🧹 Début du nettoyage automatique...")
                
                # Nettoyage des données expirées
                for service_name, service_instance in self.services.items():
                    if hasattr(service_instance, 'cleanup_expired_data'):
                        await service_instance.cleanup_expired_data()
                
                logger.info("✅ Nettoyage automatique terminé")
                
            except Exception as e:
                logger.error(f"Erreur nettoyage automatique: {e}")
    
    async def _backup_task(self) -> None:
        """Tâche de sauvegarde automatique"""
        while self.running:
            try:
                backup_interval = getattr(self.config, 'backup_interval_hours', 24) * 3600
                await asyncio.sleep(backup_interval)
                
                logger.info("💾 Début de la sauvegarde automatique...")
                
                backup_results = {}
                for service_name, service_instance in self.services.items():
                    if hasattr(service_instance, 'create_backup'):
                        try:
                            backup_path = await service_instance.create_backup()
                            backup_results[service_name] = {
                                'status': 'success',
                                'backup_path': backup_path
                            }
                        except Exception as e:
                            backup_results[service_name] = {
                                'status': 'error',
                                'error': str(e)
                            }
                
                logger.info(f"✅ Sauvegarde automatique terminée: {backup_results}")
                
            except Exception as e:
                logger.error(f"Erreur sauvegarde automatique: {e}")
    
    async def _statistics_update_task(self) -> None:
        """Tâche de mise à jour des statistiques"""
        while self.running:
            try:
                await asyncio.sleep(900)  # Mise à jour toutes les 15 minutes
                
                # Mise à jour des statistiques en cache
                stats = await self.get_service_statistics()
                
                # Optionnel: Sauvegarde des statistiques
                if hasattr(self.config, 'save_statistics') and self.config.save_statistics:
                    await self._save_statistics_snapshot(stats)
                
            except Exception as e:
                logger.error(f"Erreur mise à jour statistiques: {e}")
    
    async def _handle_unhealthy_state(self, health_report -> None: Dict[str, Any]) -> None:
        """Gère l'état de santé dégradé"""
        logger.error("🚨 Module en état critique - Actions correctives requises")
        
        # Tentative de redémarrage des services défaillants
        for service_name, service_health in health_report['services'].items():
            if service_health.get('status') != 'healthy':
                logger.warning(f"⚠️ Tentative de redémarrage de {service_name}")
                try:
                    if service_name in self.services:
                        await self._restart_service(service_name)
                except Exception as e:
                    logger.error(f"❌ Échec redémarrage {service_name}: {e}")
    
    async def _handle_degraded_state(self, health_report -> None: Dict[str, Any]) -> None:
        """Gère l'état dégradé"""
        logger.warning("🔶 Module en état dégradé - Surveillance renforcée")
        
        # Augmentation de la fréquence de surveillance
        # Notifications aux administrateurs
        # etc.
    
    async def _restart_service(self, service_name -> None: str) -> None:
        """Redémarre un service spécifique"""
        try:
            if service_name in self.services:
                # Arrêt propre du service
                service_instance = self.services[service_name]
                if hasattr(service_instance, 'shutdown'):
                    await service_instance.shutdown()
                
                # Suppression de l'ancienne instance
                del self.services[service_name]
                
                # Création d'une nouvelle instance
                service_class = self.service_registry[service_name]
                service_config = getattr(self.config, service_name, {})
                
                new_instance = service_class(service_config)
                await new_instance.initialize()
                
                self.services[service_name] = new_instance
                
                logger.info(f"✅ Service {service_name} redémarré avec succès")
                
        except Exception as e:
            logger.error(f"Erreur redémarrage service {service_name}: {e}")
            raise
    
    async def _save_statistics_snapshot(self, stats -> None: Dict[str, Any]) -> None:
        """Sauvegarde un snapshot des statistiques"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            stats_file = f"rights_tracking_stats_{timestamp}.json"
            
            stats_dir = Path(getattr(self.config, 'stats_directory', './stats'))
            stats_dir.mkdir(exist_ok=True)
            
            stats_path = stats_dir / stats_file
            
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"📊 Statistiques sauvegardées: {stats_path}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde statistiques: {e}")
    
    async def _log_startup_summary(self) -> None:
        """Log le résumé de démarrage"""
        try:
            uptime = (datetime.utcnow() - self.startup_timestamp).total_seconds()
            
            summary = f"""╔══════════════════════════════════════════════════════════╗
║             RIGHTS TRACKING MODULE - DÉMARRÉ             ║
╠══════════════════════════════════════════════════════════╣
║ 🕐 Temps de démarrage: {uptime:.2f} secondes                      ║
║ 🔧 Services initialisés: {len(self.services)}                               ║
║ 💾 Base de données: ✅ Connectée                         ║
║ 🌐 Configurations: ✅ Chargées                          ║
║ 📊 Surveillance: ✅ Active                              ║
║ 🚀 Statut: OPÉRATIONNEL                                ║
╚══════════════════════════════════════════════════════════╝
"""
            
            logger.info(summary)
            
        except Exception as e:
            logger.error(f"Erreur log résumé démarrage: {e}")
    
    async def shutdown(self) -> None:
        """Arrêt propre du module"""
        try:
            logger.info("🛑 Arrêt du module Rights Tracking...")
            self.running = False
            
            # Arrêt des services dans l'ordre inverse
            shutdown_order = list(reversed(list(self.services.keys())))
            
            for service_name in shutdown_order:
                try:
                    logger.info(f"🔄 Arrêt de {service_name}...")
                    service_instance = self.services[service_name]
                    
                    if hasattr(service_instance, 'shutdown'):
                        await service_instance.shutdown()
                    
                    logger.info(f"✅ {service_name} arrêté")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur arrêt {service_name}: {e}")
            
            # Nettoyage final
            self.services.clear()
            self.health_status.clear()
            
            logger.info("✅ Module Rights Tracking arrêté proprement")
            
        except Exception as e:
            logger.error(f"Erreur arrêt module: {e}")


# Instance globale de l'orchestrateur
_orchestrator: Optional[RightsTrackingOrchestrator] = None


async def initialize_rights_tracking_module(config_path: Optional[str] = None) -> bool:
    """Initialise le module de suivi des droits"""
    global _orchestrator
    
    try:
        if _orchestrator is not None:
            logger.warning("Module Rights Tracking déjà initialisé")
            return True
        
        _orchestrator = RightsTrackingOrchestrator(config_path)
        return await _orchestrator.initialize()
        
    except Exception as e:
        logger.error(f"Erreur initialisation module Rights Tracking: {e}")
        return False


async def shutdown_rights_tracking_module() -> None:
    """Arrête le module de suivi des droits"""
    global _orchestrator
    
    try:
        if _orchestrator is not None:
            await _orchestrator.shutdown()
            _orchestrator = None
            
    except Exception as e:
        logger.error(f"Erreur arrêt module Rights Tracking: {e}")


async def get_module_health() -> Dict[str, Any]:
    """Récupère l'état de santé du module"""
    global _orchestrator
    
    if _orchestrator is None:
        return {
            'overall_status': 'not_initialized',
            'error': 'Module not initialized'
        }
    
    return await _orchestrator.health_check()


async def get_module_statistics() -> Dict[str, Any]:
    """
Récupère les statistiques du module"""
    global _orchestrator
    
    if _orchestrator is None:
        return {'error': 'Module not initialized'}
    
    return await _orchestrator.get_service_statistics()


async def get_service_instance(service_name: str) -> Optional[Any]:
    """
Récupère une instance de service spécifique"""
    global _orchestrator
    
    if _orchestrator is None or service_name not in _orchestrator.services:
        return None
    
    return _orchestrator.services[service_name]


# Interface CLI pour tests et débogage
async def main() -> None:
    """
Point d'entrée principal pour l'exécution directe du module"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rights Tracking Module')
    parser.add_argument('--config', type=str, help='Chemin vers le fichier de configuration')
    parser.add_argument('--health-check', action='store_true', help='Effectue un health check')
    parser.add_argument('--stats', action='store_true', help='Affiche les statistiques')
    parser.add_argument('--daemon', action='store_true', help='Exécute en mode daemon')
    
    args = parser.parse_args()
    
    # Configuration du logging pour CLI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        if args.health_check:
            # Health check rapide
            success = await initialize_rights_tracking_module(args.config)
            if success:
                health = await get_module_health()
                print(f"Statut: {health['overall_status']}")
                print(f"Services sains: {health.get('healthy_services', 0)}/{health.get('total_services', 0)}")
            else:
                print("❌ Échec de l'initialisation")
                sys.exit(1)
        
        elif args.stats:
            # Affichage des statistiques
            success = await initialize_rights_tracking_module(args.config)
            if success:
                stats = await get_module_statistics()
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("❌ Échec de l'initialisation")
                sys.exit(1)
        
        elif args.daemon:
            # Mode daemon
            success = await initialize_rights_tracking_module(args.config)
            if success:
                logger.info("🚀 Module démarré en mode daemon")
                try:
                    while True:
                        await asyncio.sleep(60)
                except KeyboardInterrupt:
                    logger.info("⌨️ Interruption clavier reçue")
            else:
                logger.error("❌ Échec de l'initialisation")
                sys.exit(1)
        
        else:
            # Test rapide
            success = await initialize_rights_tracking_module(args.config)
            if success:
                print("✅ Module Rights Tracking initialisé avec succès")
                
                # Test basique
                rights_service = await get_rights_tracking_service()
                print(f"✅ Service principal accessible: {type(rights_service).__name__}")
                
            else:
                print("❌ Échec de l'initialisation")
                sys.exit(1)
        
    except Exception as e:
        logger.error(f"💥 Erreur exécution CLI: {e}")
        sys.exit(1)
    
    finally:
        # Nettoyage
        await shutdown_rights_tracking_module()


if __name__ == "__main__":
    asyncio.run(main())
