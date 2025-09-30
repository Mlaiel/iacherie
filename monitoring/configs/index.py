#!/usr/bin/env python3
"""
🎛️ Monitoring Configuration Orchestrator - Creator Economy Enterprise
=====================================================================

Orchestrateur central des configurations monitoring pour l'écosystème IA Chérie Creator Economy.
Gestion intelligente des configurations avec validation, hot-reload et optimisation Creator-specific.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  PROTECTION INTELLECTUELLE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 AVERTISSEMENT LÉGAL:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Équipe Experte: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import os
import logging
import yaml
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
from functools import lru_cache

import aiofiles
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from pydantic import BaseModel, validator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("iacherie.monitoring.config")


class CreatorTier(str, Enum):
    """Niveaux de créateurs IA Chérie avec SLA différenciés"""
    PREMIUM = "premium"
    STANDARD = "standard" 
    BASIC = "basic"
    ENTERPRISE = "enterprise"


class ConfigType(str, Enum):
    """Types de configuration monitoring supportés"""
    CREATOR_ECONOMY = "creator_economy"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    ALERTMANAGER = "alertmanager"
    AI_ML = "ai_ml"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    SEO_PERFORMANCE = "seo_performance"
    DISTRIBUTION = "distribution"
    GAMIFICATION = "gamification"
    SECURITY_COMPLIANCE = "security_compliance"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


@dataclass
class ConfigMetadata:
    """Métadonnées de configuration avec traçabilité"""
    config_type: ConfigType
    file_path: Path
    last_modified: datetime
    version: str
    checksum: str
    creator_specific: bool = False
    tier_restrictions: List[CreatorTier] = field(default_factory=list)
    validation_status: str = "pending"
    reload_count: int = 0


class ConfigurationManager:
    """
    🎛️ Gestionnaire central des configurations monitoring Creator Economy
    
    Features Enterprise:
    - Hot-reload sans restart des services
    - Validation schemas avancée avec règles métier
    - Configuration Creator-specific par tier
    - Cache distribué avec Redis
    - Monitoring de la santé des configurations
    - Audit trail complet
    - Rollback automatique en cas d'erreur
    """
    
    def __init__(self, config_dir: str = "/home/runner/work/IA Chérie/IA Chérie/monitoring/configs"):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, ConfigMetadata] = {}
        self.redis_client: Optional[aioredis.Redis] = None
        self.file_observer: Optional[Observer] = None
        self.validation_rules: Dict[ConfigType, callable] = {}
        self.config_templates: Dict[ConfigType, Dict] = {}
        self.creator_customizations: Dict[str, Dict] = {}
        
        self._initialize_validation_rules()
        self._load_config_templates()
    
    async def initialize(self) -> None:
        """Initialisation complète du gestionnaire de configuration"""
        try:
            # Connexion Redis pour cache distribué
            self.redis_client = await aioredis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True
            )
            
            # Chargement initial des configurations
            await self._load_all_configurations()
            
            # Démarrage monitoring hot-reload
            self._start_file_watcher()
            
            # Validation initiale complète
            await self._validate_all_configurations()
            
            logger.info("🎛️ Configuration Manager initialisé avec succès")
            logger.info(f"📊 {len(self.configs)} configurations chargées")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Configuration Manager: {e}")
            raise
    
    def _initialize_validation_rules(self) -> None:
        """Initialisation des règles de validation par type de config"""
        self.validation_rules = {
            ConfigType.CREATOR_ECONOMY: self._validate_creator_economy_config,
            ConfigType.PROMETHEUS: self._validate_prometheus_config,
            ConfigType.GRAFANA: self._validate_grafana_config,
            ConfigType.ALERTMANAGER: self._validate_alertmanager_config,
            ConfigType.AI_ML: self._validate_ai_ml_config,
            ConfigType.CONTENT_PROTECTION: self._validate_content_protection_config,
            ConfigType.MONETIZATION: self._validate_monetization_config,
            ConfigType.COLLABORATION: self._validate_collaboration_config,
            ConfigType.SEO_PERFORMANCE: self._validate_seo_performance_config,
            ConfigType.DISTRIBUTION: self._validate_distribution_config,
            ConfigType.GAMIFICATION: self._validate_gamification_config,
            ConfigType.SECURITY_COMPLIANCE: self._validate_security_compliance_config,
            ConfigType.PERFORMANCE_OPTIMIZATION: self._validate_performance_optimization_config,
        }
    
    def _load_config_templates(self) -> None:
        """Chargement des templates de configuration Creator Economy"""
        self.config_templates = {
            ConfigType.CREATOR_ECONOMY: {
                "version": "1.0.0",
                "creator_metrics": {
                    "musicians": {
                        "audio_processing_latency_ms": {"sla": 100, "critical": 500},
                        "streaming_quality_score": {"min": 0.95, "target": 0.99},
                        "collaboration_success_rate": {"min": 0.75, "target": 0.90}
                    },
                    "bloggers": {
                        "seo_ranking_performance": {"track_keywords": True, "alert_drop": 5},
                        "content_delivery_ms": {"sla": 2000, "critical": 5000},
                        "engagement_analytics": {"track_real_time": True}
                    },
                    "photographers": {
                        "image_processing_ms": {"sla": 200, "critical": 1000},
                        "storage_utilization_percent": {"warning": 80, "critical": 95},
                        "visual_ai_accuracy": {"min": 0.92, "target": 0.98}
                    }
                },
                "tier_differentiation": {
                    "premium": {"sla_multiplier": 0.5, "priority": "highest"},
                    "standard": {"sla_multiplier": 1.0, "priority": "high"},
                    "basic": {"sla_multiplier": 2.0, "priority": "normal"}
                }
            }
        }
    
    async def _load_all_configurations(self) -> None:
        """Chargement de toutes les configurations depuis le système de fichiers"""
        config_files = [
            "creator_economy_monitoring_config.yaml",
            "prometheus_creator_metrics.yaml", 
            "grafana_creator_dashboards.yaml",
            "alertmanager_creator_rules.yaml",
            "ai_ml_monitoring_config.yaml",
            "content_protection_monitoring.yaml",
            "monetization_metrics_config.yaml",
            "collaboration_monitoring_config.yaml",
            "seo_performance_monitoring.yaml",
            "distribution_channel_monitoring.yaml",
            "gamification_metrics_config.yaml",
            "creator_tier_monitoring_config.yaml",
            "multi_format_content_monitoring.yaml",
            "security_compliance_monitoring.yaml",
            "performance_optimization_config.yaml"
        ]
        
        for config_file in config_files:
            file_path = self.config_dir / config_file
            if file_path.exists():
                await self._load_configuration_file(file_path)
            else:
                logger.warning(f"📄 Configuration manquante: {config_file}")

    async def _load_configuration_file(self, file_path: Path) -> None:
        """Chargement d'un fichier de configuration avec gestion d'erreurs"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Parse YAML/JSON selon l'extension
            if file_path.suffix in ['.yaml', '.yml']:
                config_data = yaml.safe_load(content)
            elif file_path.suffix == '.json':
                config_data = json.loads(content)
            else:
                logger.warning(f"⚠️ Format non supporté: {file_path}")
                return
            
            # Génération métadonnées
            file_stat = file_path.stat()
            checksum = hashlib.sha256(content.encode()).hexdigest()
            
            config_name = file_path.stem
            config_type = self._determine_config_type(config_name)
            
            metadata = ConfigMetadata(
                config_type=config_type,
                file_path=file_path,
                last_modified=datetime.fromtimestamp(file_stat.st_mtime),
                version=config_data.get('version', '1.0.0'),
                checksum=checksum,
                creator_specific=self._is_creator_specific(config_data),
                tier_restrictions=self._extract_tier_restrictions(config_data)
            )
            
            # Stockage en mémoire et cache
            self.configs[config_name] = config_data
            self.metadata[config_name] = metadata
            
            # Cache Redis pour accès distribué
            if self.redis_client:
                await self.redis_client.setex(
                    f"iacherie:config:{config_name}",
                    3600,  # TTL 1 heure
                    json.dumps(config_data, default=str)
                )
            
            logger.info(f"✅ Configuration chargée: {config_name} (v{metadata.version})")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement {file_path}: {e}")
            raise
    
    def _determine_config_type(self, config_name: str) -> ConfigType:
        """Détermination du type de configuration basé sur le nom"""
        if "creator_economy" in config_name:
            return ConfigType.CREATOR_ECONOMY
        elif "prometheus" in config_name:
            return ConfigType.PROMETHEUS
        elif "grafana" in config_name:
            return ConfigType.GRAFANA
        elif "alertmanager" in config_name:
            return ConfigType.ALERTMANAGER
        elif "ai_ml" in config_name:
            return ConfigType.AI_ML
        elif "content_protection" in config_name:
            return ConfigType.CONTENT_PROTECTION
        elif "monetization" in config_name:
            return ConfigType.MONETIZATION
        elif "collaboration" in config_name:
            return ConfigType.COLLABORATION
        elif "seo_performance" in config_name:
            return ConfigType.SEO_PERFORMANCE
        elif "distribution" in config_name:
            return ConfigType.DISTRIBUTION
        elif "gamification" in config_name:
            return ConfigType.GAMIFICATION
        elif "security_compliance" in config_name:
            return ConfigType.SECURITY_COMPLIANCE
        elif "performance_optimization" in config_name:
            return ConfigType.PERFORMANCE_OPTIMIZATION
        else:
            return ConfigType.CREATOR_ECONOMY  # Default
    
    def _is_creator_specific(self, config_data: Dict) -> bool:
        """Vérification si la configuration est spécifique aux créateurs"""
        creator_indicators = [
            "creator_metrics", "creator_tiers", "creator_types",
            "musicians", "bloggers", "photographers", "influencers"
        ]
        return any(indicator in str(config_data) for indicator in creator_indicators)
    
    def _extract_tier_restrictions(self, config_data: Dict) -> List[CreatorTier]:
        """Extraction des restrictions par tier de créateur"""
        restrictions = []
        if isinstance(config_data, dict):
            tier_config = config_data.get('tier_restrictions', {})
            for tier_name in tier_config.keys():
                try:
                    restrictions.append(CreatorTier(tier_name))
                except ValueError:
                    continue
        return restrictions
    
    async def get_configuration(self, config_name: str, creator_tier: Optional[CreatorTier] = None) -> Optional[Dict[str, Any]]:
        """
        Récupération d'une configuration avec personnalisation Creator-specific
        
        Args:
            config_name: Nom de la configuration
            creator_tier: Tier du créateur pour personnalisation
            
        Returns:
            Configuration personnalisée ou None si non trouvée
        """
        base_config = self.configs.get(config_name)
        if not base_config:
            # Tentative récupération depuis Redis
            if self.redis_client:
                cached_config = await self.redis_client.get(f"iacherie:config:{config_name}")
                if cached_config:
                    base_config = json.loads(cached_config)
                    self.configs[config_name] = base_config
        
        if not base_config:
            logger.warning(f"⚠️ Configuration non trouvée: {config_name}")
            return None
        
        # Application personnalisation tier si applicable
        if creator_tier and self._has_tier_customization(config_name, creator_tier):
            return self._apply_tier_customization(base_config, creator_tier)
        
        return base_config.copy()
    
    def _has_tier_customization(self, config_name: str, tier: CreatorTier) -> bool:
        """Vérification existence personnalisation pour un tier"""
        metadata = self.metadata.get(config_name)
        return metadata and (not metadata.tier_restrictions or tier in metadata.tier_restrictions)
    
    def _apply_tier_customization(self, base_config: Dict, tier: CreatorTier) -> Dict:
        """Application des personnalisations spécifiques au tier"""
        config = base_config.copy()
        
        # Ajustements SLA selon le tier
        if "sla" in config or "performance" in config:
            tier_multipliers = {
                CreatorTier.PREMIUM: 0.5,    # SLA plus strict pour premium
                CreatorTier.STANDARD: 1.0,   # SLA standard
                CreatorTier.BASIC: 2.0,      # SLA plus souple pour basic
                CreatorTier.ENTERPRISE: 0.3  # SLA ultra-strict pour enterprise
            }
            
            multiplier = tier_multipliers.get(tier, 1.0)
            self._adjust_sla_values(config, multiplier)
        
        return config
    
    def _adjust_sla_values(self, config: Dict, multiplier: float) -> None:
        """Ajustement récursif des valeurs SLA dans la configuration"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._adjust_sla_values(value, multiplier)
            elif key.endswith(('_ms', '_latency', '_timeout')) and isinstance(value, (int, float)):
                config[key] = int(value * multiplier)
    
    async def _validate_all_configurations(self) -> None:
        """Validation complète de toutes les configurations chargées"""
        validation_tasks = []
        
        for config_name, config_data in self.configs.items():
            metadata = self.metadata.get(config_name)
            if metadata:
                validation_tasks.append(
                    self._validate_single_configuration(config_name, config_data, metadata.config_type)
                )
        
        if validation_tasks:
            results = await asyncio.gather(*validation_tasks, return_exceptions=True)
            
            valid_count = sum(1 for result in results if result is True)
            total_count = len(results)
            
            logger.info(f"✅ Validation terminée: {valid_count}/{total_count} configurations valides")
    
    async def _validate_single_configuration(self, config_name: str, config_data: Dict, config_type: ConfigType) -> bool:
        """Validation d'une configuration individuelle"""
        try:
            validator = self.validation_rules.get(config_type)
            if validator:
                is_valid = await validator(config_data)
                
                # Mise à jour métadonnées
                if config_name in self.metadata:
                    self.metadata[config_name].validation_status = "valid" if is_valid else "invalid"
                
                return is_valid
            else:
                logger.warning(f"⚠️ Pas de validateur pour: {config_type}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erreur validation {config_name}: {e}")
            if config_name in self.metadata:
                self.metadata[config_name].validation_status = "error"
            return False
    
    # Validation Rules Implementation
    async def _validate_creator_economy_config(self, config: Dict) -> bool:
        """Validation spécifique Creator Economy configuration"""
        required_fields = ["creator_metrics", "tier_differentiation"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"❌ Champ manquant Creator Economy: {field}")
                return False
        
        # Validation des métriques créateurs
        creator_metrics = config.get("creator_metrics", {})
        required_creator_types = ["musicians", "bloggers", "photographers"]
        
        for creator_type in required_creator_types:
            if creator_type not in creator_metrics:
                logger.warning(f"⚠️ Type créateur manquant: {creator_type}")
        
        return True
    
    async def _validate_prometheus_config(self, config: Dict) -> bool:
        """Validation configuration Prometheus"""
        if "scrape_configs" not in config:
            logger.error("❌ scrape_configs manquant dans Prometheus config")
            return False
        
        scrape_configs = config["scrape_configs"]
        for scrape_config in scrape_configs:
            if "job_name" not in scrape_config:
                logger.error("❌ job_name manquant dans scrape_config")
                return False
        
        return True
    
    async def _validate_grafana_config(self, config: Dict) -> bool:
        """Validation configuration Grafana"""
        if "dashboards" not in config:
            logger.error("❌ dashboards manquant dans Grafana config")
            return False
        return True
    
    async def _validate_alertmanager_config(self, config: Dict) -> bool:
        """Validation configuration AlertManager"""
        if "groups" not in config:
            logger.error("❌ groups manquant dans AlertManager config")
            return False
        return True
    
    async def _validate_ai_ml_config(self, config: Dict) -> bool:
        """Validation configuration AI/ML"""
        required_sections = ["ml_monitoring", "model_performance", "inference_monitoring"]
        for section in required_sections:
            if section not in config:
                logger.error(f"❌ Section manquante AI/ML: {section}")
                return False
        return True
    
    async def _validate_content_protection_config(self, config: Dict) -> bool:
        """Validation configuration protection contenu"""
        if "protection_monitoring" not in config:
            logger.error("❌ protection_monitoring manquant")
            return False
        return True
    
    async def _validate_monetization_config(self, config: Dict) -> bool:
        """Validation configuration monétisation"""
        if "monetization_tracking" not in config:
            logger.error("❌ monetization_tracking manquant")
            return False
        return True
    
    async def _validate_collaboration_config(self, config: Dict) -> bool:
        """Validation configuration collaboration"""
        if "collaboration_metrics" not in config:
            logger.error("❌ collaboration_metrics manquant")
            return False
        return True
    
    async def _validate_seo_performance_config(self, config: Dict) -> bool:
        """Validation configuration SEO performance"""
        if "seo_monitoring" not in config:
            logger.error("❌ seo_monitoring manquant")
            return False
        return True
    
    async def _validate_distribution_config(self, config: Dict) -> bool:
        """Validation configuration distribution"""
        if "distribution_monitoring" not in config:
            logger.error("❌ distribution_monitoring manquant")
            return False
        return True
    
    async def _validate_gamification_config(self, config: Dict) -> bool:
        """Validation configuration gamification"""
        if "gamification_tracking" not in config:
            logger.error("❌ gamification_tracking manquant")
            return False
        return True
    
    async def _validate_security_compliance_config(self, config: Dict) -> bool:
        """Validation configuration sécurité compliance"""
        if "security_monitoring" not in config:
            logger.error("❌ security_monitoring manquant")
            return False
        return True
    
    async def _validate_performance_optimization_config(self, config: Dict) -> bool:
        """Validation configuration optimisation performance"""
        if "performance_optimization" not in config:
            logger.error("❌ performance_optimization manquant")
            return False
        return True
    
    def _start_file_watcher(self) -> None:
        """Démarrage du monitoring hot-reload des fichiers de configuration"""
        event_handler = ConfigFileEventHandler(self)
        self.file_observer = Observer()
        self.file_observer.schedule(event_handler, str(self.config_dir), recursive=False)
        self.file_observer.start()
        logger.info("🔄 Hot-reload activé pour les configurations")
    
    async def hot_reload_configuration(self, file_path: Path) -> bool:
        """Hot-reload d'une configuration modifiée"""
        try:
            config_name = file_path.stem
            old_checksum = self.metadata.get(config_name, {}).checksum if config_name in self.metadata else None
            
            # Rechargement
            await self._load_configuration_file(file_path)
            
            new_metadata = self.metadata.get(config_name)
            if new_metadata and new_metadata.checksum != old_checksum:
                new_metadata.reload_count += 1
                logger.info(f"🔄 Hot-reload réussi: {config_name} (reload #{new_metadata.reload_count})")
                
                # Validation post-reload
                config_data = self.configs.get(config_name)
                if config_data:
                    is_valid = await self._validate_single_configuration(
                        config_name, config_data, new_metadata.config_type
                    )
                    if not is_valid:
                        logger.error(f"❌ Configuration invalide après reload: {config_name}")
                        return False
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur hot-reload {file_path}: {e}")
            return False
    
    async def get_configuration_status(self) -> Dict[str, Any]:
        """Récupération du statut complet des configurations"""
        status = {
            "total_configurations": len(self.configs),
            "valid_configurations": sum(
                1 for meta in self.metadata.values() 
                if meta.validation_status == "valid"
            ),
            "invalid_configurations": sum(
                1 for meta in self.metadata.values() 
                if meta.validation_status == "invalid"
            ),
            "configurations": {}
        }
        
        for config_name, metadata in self.metadata.items():
            status["configurations"][config_name] = {
                "type": metadata.config_type.value,
                "version": metadata.version,
                "last_modified": metadata.last_modified.isoformat(),
                "validation_status": metadata.validation_status,
                "reload_count": metadata.reload_count,
                "creator_specific": metadata.creator_specific,
                "tier_restrictions": [tier.value for tier in metadata.tier_restrictions]
            }
        
        return status
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources avant arrêt"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("🔄 Configuration Manager arrêté proprement")


class ConfigFileEventHandler(FileSystemEventHandler):
    """Handler pour le monitoring des changements de fichiers de configuration"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        super().__init__()
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.yaml', '.yml', '.json')):
            file_path = Path(event.src_path)
            asyncio.create_task(self.config_manager.hot_reload_configuration(file_path))


# Factory Pattern pour instanciation
@lru_cache(maxsize=1)
def get_configuration_manager() -> ConfigurationManager:
    """Factory singleton pour le gestionnaire de configuration"""
    return ConfigurationManager()


# Interface publique pour les autres modules
async def get_config(config_name: str, creator_tier: Optional[CreatorTier] = None) -> Optional[Dict[str, Any]]:
    """Interface publique pour récupération de configuration"""
    manager = get_configuration_manager()
    if not hasattr(manager, 'redis_client') or manager.redis_client is None:
        await manager.initialize()
    
    return await manager.get_configuration(config_name, creator_tier)


async def get_all_config_status() -> Dict[str, Any]:
    """Interface publique pour récupération du statut des configurations"""
    manager = get_configuration_manager()
    if not hasattr(manager, 'redis_client') or manager.redis_client is None:
        await manager.initialize()
    
    return await manager.get_configuration_status()


if __name__ == "__main__":
    """Mode développement - Test du gestionnaire de configuration"""
    async def main():
        manager = ConfigurationManager()
        await manager.initialize()
        
        # Test récupération configuration
        config = await manager.get_configuration("creator_economy_monitoring_config")
        if config:
            print("✅ Configuration Creator Economy chargée avec succès")
        
        # Test statut
        status = await manager.get_configuration_status()
        print(f"📊 Statut: {status['total_configurations']} configurations")
        
        await manager.cleanup()
    
    asyncio.run(main())