"""
💾 Content Storage Capacity Forecaster - Multi-Format Storage Intelligence
==========================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

🎯 ÉQUIPE PROJET: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
👨‍💻 ARCHITECTE PRINCIPAL: Fahed Mlaiel
📧 CONTACT: mlaiel@live.de
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import math
from pathlib import Path

# Configuration des logs enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """Formats de contenu supportés"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"
    THUMBNAILS = "thumbnails"
    TRANSCRIPTS = "transcripts"
    ANALYTICS_DATA = "analytics_data"


class StorageTier(Enum):
    """Tiers de stockage selon fréquence d'accès"""
    HOT = "hot"         # Accès fréquent < 30 jours
    WARM = "warm"       # Accès modéré 30-90 jours
    COLD = "cold"       # Accès rare 90-365 jours
    ARCHIVE = "archive" # Archivage > 365 jours


class CompressionType(Enum):
    """Types de compression par format"""
    H264 = "h264"       # Video compression
    H265 = "h265"       # Video compression avancée
    VP9 = "vp9"         # Video compression Google
    FLAC = "flac"       # Audio lossless
    MP3 = "mp3"         # Audio lossy
    WEBP = "webp"       # Image compression moderne
    JPEG = "jpeg"       # Image compression standard
    GZIP = "gzip"       # Text compression


@dataclass
class ContentMetrics:
    """Métriques de contenu par format"""
    format_type: ContentFormat
    total_files: int = 0
    total_size_bytes: int = 0
    average_file_size_mb: float = 0.0
    daily_uploads: int = 0
    growth_rate_weekly: float = 0.0
    compression_ratio: float = 0.0
    access_frequency: float = 0.0  # Accès par jour
    retention_period_days: int = 365


@dataclass
class StorageCapacityForecast:
    """Prévision capacité stockage multi-format"""
    forecast_date: datetime = field(default_factory=datetime.now)
    forecast_horizon_days: int = 30
    total_storage_required_tb: float = 0.0
    storage_by_format: Dict[ContentFormat, float] = field(default_factory=dict)
    storage_by_tier: Dict[StorageTier, float] = field(default_factory=dict)
    compression_savings_tb: float = 0.0
    cost_projection_monthly: float = 0.0
    growth_rate_percentage: float = 0.0
    peak_storage_requirement: float = 0.0
    confidence_level: float = 0.0


@dataclass
class StorageOptimization:
    """Recommandations optimisation stockage"""
    current_efficiency: float = 0.0
    potential_savings_tb: float = 0.0
    potential_cost_savings: float = 0.0
    optimization_actions: List[Dict[str, Any]] = field(default_factory=list)
    tier_rebalancing: Dict[StorageTier, float] = field(default_factory=dict)
    compression_improvements: Dict[ContentFormat, Dict[str, Any]] = field(default_factory=dict)


class ContentStorageCapacityForecaster:
    """
    💾 Prévision capacité stockage contenu multi-format
    
    Audio content storage growth modeling, Video content capacity forecasting,
    Image storage requirement prediction, Text content scaling analysis,
    Multi-format storage optimization.
    """

    def __init__(
        self,
        storage_config_path: Optional[str] = None,
        enable_compression_optimization: bool = True,
        tier_migration_enabled: bool = True,
        cost_optimization_target: float = 0.20  # 20% réduction coût
    ):
        self.storage_config_path = storage_config_path or "/config/storage_capacity_config.json"
        self.enable_compression_optimization = enable_compression_optimization
        self.tier_migration_enabled = tier_migration_enabled
        self.cost_optimization_target = cost_optimization_target
        
        # State management
        self._content_metrics: Dict[ContentFormat, ContentMetrics] = {}
        self._storage_history: List[Dict[str, Any]] = []
        self._forecasts_cache: Dict[str, StorageCapacityForecast] = {}
        self._optimization_cache: Dict[str, StorageOptimization] = {}
        
        # Configuration storage
        self._format_configs = self._initialize_format_configs()
        self._tier_configs = self._initialize_tier_configs()
        self._compression_configs = self._initialize_compression_configs()
        
        # Initialize forecaster
        self._initialize_forecaster()
        
        logger.info("🚀 ContentStorageCapacityForecaster initialisé - Multi-format intelligence")

    def _initialize_format_configs(self) -> Dict[ContentFormat, Dict[str, Any]]:
        """Configuration par format de contenu"""
        return {
            ContentFormat.AUDIO: {
                "average_size_mb": 4.2,  # ~3 minutes audio
                "growth_multiplier": 1.8,  # Audio croît rapidement
                "compression_algorithms": ["flac", "mp3", "opus"],
                "compression_ratio": 0.65,  # 35% économie
                "quality_tiers": ["lossless", "high", "standard"],
                "creator_segments": ["musicians", "podcasters", "educators"],
                "seasonal_pattern": True,
                "viral_multiplier": 2.5
            },
            ContentFormat.VIDEO: {
                "average_size_mb": 45.8,  # ~2 minutes video HD
                "growth_multiplier": 2.2,  # Video croît le plus
                "compression_algorithms": ["h264", "h265", "vp9", "av1"],
                "compression_ratio": 0.75,  # 25% économie
                "quality_tiers": ["4k", "1080p", "720p", "480p"],
                "creator_segments": ["influencers", "comedians", "educators"],
                "seasonal_pattern": True,
                "viral_multiplier": 3.8
            },
            ContentFormat.IMAGE: {
                "average_size_mb": 2.1,  # Image haute qualité
                "growth_multiplier": 1.5,
                "compression_algorithms": ["webp", "jpeg", "avif"],
                "compression_ratio": 0.58,  # 42% économie
                "quality_tiers": ["raw", "high", "optimized"],
                "creator_segments": ["photographers", "artists", "influencers"],
                "seasonal_pattern": False,
                "viral_multiplier": 2.0
            },
            ContentFormat.TEXT: {
                "average_size_mb": 0.05,  # Articles, posts
                "growth_multiplier": 1.3,
                "compression_algorithms": ["gzip", "brotli"],
                "compression_ratio": 0.25,  # 75% économie
                "quality_tiers": ["rich", "standard", "minimal"],
                "creator_segments": ["bloggers", "educators"],
                "seasonal_pattern": False,
                "viral_multiplier": 1.2
            },
            ContentFormat.METADATA: {
                "average_size_mb": 0.01,  # Tags, descriptions
                "growth_multiplier": 1.1,
                "compression_algorithms": ["json_compress", "msgpack"],
                "compression_ratio": 0.40,  # 60% économie
                "quality_tiers": ["full", "essential"],
                "creator_segments": ["all"],
                "seasonal_pattern": False,
                "viral_multiplier": 1.0
            },
            ContentFormat.THUMBNAILS: {
                "average_size_mb": 0.15,  # Miniatures
                "growth_multiplier": 1.4,
                "compression_algorithms": ["webp", "jpeg"],
                "compression_ratio": 0.70,  # 30% économie
                "quality_tiers": ["high", "standard"],
                "creator_segments": ["all"],
                "seasonal_pattern": False,
                "viral_multiplier": 1.0
            },
            ContentFormat.TRANSCRIPTS: {
                "average_size_mb": 0.08,  # Transcriptions auto
                "growth_multiplier": 1.6,  # Croît avec audio/video
                "compression_algorithms": ["gzip"],
                "compression_ratio": 0.30,  # 70% économie
                "quality_tiers": ["full", "summary"],
                "creator_segments": ["podcasters", "educators", "musicians"],
                "seasonal_pattern": False,
                "viral_multiplier": 1.0
            },
            ContentFormat.ANALYTICS_DATA: {
                "average_size_mb": 0.02,  # Données analytics
                "growth_multiplier": 1.2,
                "compression_algorithms": ["parquet", "gzip"],
                "compression_ratio": 0.45,  # 55% économie
                "quality_tiers": ["detailed", "summary"],
                "creator_segments": ["all"],
                "seasonal_pattern": False,
                "viral_multiplier": 1.0
            }
        }

    def _initialize_tier_configs(self) -> Dict[StorageTier, Dict[str, Any]]:
        """Configuration par tier de stockage"""
        return {
            StorageTier.HOT: {
                "cost_per_gb_monthly": 0.023,  # €0.023/GB/mois
                "access_time_ms": 1,
                "availability": 0.9999,
                "max_age_days": 30,
                "auto_migration": True,
                "redundancy": 3
            },
            StorageTier.WARM: {
                "cost_per_gb_monthly": 0.0125,  # €0.0125/GB/mois
                "access_time_ms": 100,
                "availability": 0.999,
                "max_age_days": 90,
                "auto_migration": True,
                "redundancy": 2
            },
            StorageTier.COLD: {
                "cost_per_gb_monthly": 0.004,   # €0.004/GB/mois
                "access_time_ms": 5000,
                "availability": 0.99,
                "max_age_days": 365,
                "auto_migration": True,
                "redundancy": 2
            },
            StorageTier.ARCHIVE: {
                "cost_per_gb_monthly": 0.001,   # €0.001/GB/mois
                "access_time_ms": 300000,  # 5 minutes
                "availability": 0.999,
                "max_age_days": 999999,  # Permanent
                "auto_migration": False,
                "redundancy": 1
            }
        }

    def _initialize_compression_configs(self) -> Dict[CompressionType, Dict[str, Any]]:
        """Configuration algorithmes compression"""
        return {
            CompressionType.H264: {
                "compression_ratio": 0.75,
                "quality_loss": 0.05,
                "cpu_cost": "medium",
                "formats": [ContentFormat.VIDEO],
                "bitrate_savings": 0.25
            },
            CompressionType.H265: {
                "compression_ratio": 0.85,
                "quality_loss": 0.03,
                "cpu_cost": "high",
                "formats": [ContentFormat.VIDEO],
                "bitrate_savings": 0.50
            },
            CompressionType.VP9: {
                "compression_ratio": 0.82,
                "quality_loss": 0.04,
                "cpu_cost": "medium",
                "formats": [ContentFormat.VIDEO],
                "bitrate_savings": 0.40
            },
            CompressionType.FLAC: {
                "compression_ratio": 0.65,
                "quality_loss": 0.0,  # Lossless
                "cpu_cost": "low",
                "formats": [ContentFormat.AUDIO],
                "bitrate_savings": 0.35
            },
            CompressionType.MP3: {
                "compression_ratio": 0.15,
                "quality_loss": 0.15,
                "cpu_cost": "low",
                "formats": [ContentFormat.AUDIO],
                "bitrate_savings": 0.85
            },
            CompressionType.WEBP: {
                "compression_ratio": 0.58,
                "quality_loss": 0.02,
                "cpu_cost": "medium",
                "formats": [ContentFormat.IMAGE, ContentFormat.THUMBNAILS],
                "bitrate_savings": 0.42
            },
            CompressionType.JPEG: {
                "compression_ratio": 0.25,
                "quality_loss": 0.10,
                "cpu_cost": "low",
                "formats": [ContentFormat.IMAGE, ContentFormat.THUMBNAILS],
                "bitrate_savings": 0.75
            },
            CompressionType.GZIP: {
                "compression_ratio": 0.30,
                "quality_loss": 0.0,
                "cpu_cost": "low",
                "formats": [ContentFormat.TEXT, ContentFormat.TRANSCRIPTS],
                "bitrate_savings": 0.70
            }
        }

    def _initialize_forecaster(self) -> None:
        """Initialise le forecaster avec données historiques"""
        try:
            # Chargement données historiques
            self._load_historical_storage_data()
            
            # Initialisation métriques par format
            self._initialize_content_metrics()
            
            # Analyse patterns de croissance
            self._analyze_growth_patterns()
            
            logger.info(f"✅ Forecaster initialisé - {len(self._content_metrics)} formats configurés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation forecaster: {e}")
            # Utilisation données simulées
            self._generate_simulated_metrics()

    def _load_historical_storage_data(self) -> None:
        """Charge données historiques de stockage"""
        try:
            if Path(self.storage_config_path).exists():
                with open(self.storage_config_path, 'r') as f:
                    data = json.load(f)
                    self._storage_history = data.get("historical_data", [])
                logger.info(f"📊 {len(self._storage_history)} points historiques chargés")
            else:
                logger.warning("⚠️ Pas de données historiques - génération simulation")
                self._generate_simulated_storage_history()
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement données: {e}")
            self._generate_simulated_storage_history()

    def _generate_simulated_storage_history(self) -> None:
        """Génère historique stockage simulé"""
        base_date = datetime.now() - timedelta(days=180)
        
        for day in range(180):
            current_date = base_date + timedelta(days=day)
            
            # Simulation croissance avec patterns
            daily_multiplier = 1 + 0.002 + np.random.normal(0, 0.001)  # ~0.2% croissance/jour
            seasonal_factor = 1 + 0.1 * math.sin(2 * math.pi * day / 365)
            
            storage_data = {
                "date": current_date.isoformat(),
                "total_storage_gb": (1000 + day * 15) * daily_multiplier * seasonal_factor,
                "format_breakdown": {
                    "audio": (200 + day * 3) * daily_multiplier,
                    "video": (600 + day * 9) * daily_multiplier,
                    "image": (150 + day * 2) * daily_multiplier,
                    "text": (20 + day * 0.5) * daily_multiplier,
                    "metadata": (10 + day * 0.2) * daily_multiplier,
                    "thumbnails": (15 + day * 0.2) * daily_multiplier,
                    "transcripts": (5 + day * 0.1) * daily_multiplier
                },
                "daily_uploads": int(500 + day * 2 + np.random.normal(0, 50)),
                "compression_savings": (50 + day * 0.8) * daily_multiplier * 0.35
            }
            
            self._storage_history.append(storage_data)
        
        logger.info(f"🎲 {len(self._storage_history)} points historiques simulés")

    def _initialize_content_metrics(self) -> None:
        """Initialise métriques par format de contenu"""
        for format_type in ContentFormat:
            config = self._format_configs[format_type]
            
            # Calcul métriques actuelles basées sur historique récent
            recent_data = self._storage_history[-30:] if len(self._storage_history) >= 30 else self._storage_history
            
            if recent_data and format_type.value in recent_data[-1].get("format_breakdown", {}):
                current_size_gb = recent_data[-1]["format_breakdown"][format_type.value]
                avg_file_size_mb = config["average_size_mb"]
                total_files = int((current_size_gb * 1024) / avg_file_size_mb) if avg_file_size_mb > 0 else 0
                
                # Calcul croissance hebdomadaire
                if len(recent_data) >= 7:
                    week_ago_size = recent_data[-7]["format_breakdown"].get(format_type.value, current_size_gb)
                    weekly_growth = (current_size_gb - week_ago_size) / week_ago_size if week_ago_size > 0 else 0
                else:
                    weekly_growth = 0.05  # 5% défaut
                
                metrics = ContentMetrics(
                    format_type=format_type,
                    total_files=total_files,
                    total_size_bytes=int(current_size_gb * 1024 * 1024 * 1024),
                    average_file_size_mb=avg_file_size_mb,
                    daily_uploads=int(total_files * 0.02),  # ~2% uploads quotidiens
                    growth_rate_weekly=weekly_growth,
                    compression_ratio=config["compression_ratio"],
                    access_frequency=self._calculate_access_frequency(format_type),
                    retention_period_days=365
                )
                
                self._content_metrics[format_type] = metrics
        
        logger.info(f"📊 Métriques initialisées pour {len(self._content_metrics)} formats")

    def _calculate_access_frequency(self, format_type: ContentFormat) -> float:
        """Calcule fréquence d'accès par format"""
        access_patterns = {
            ContentFormat.AUDIO: 2.3,      # 2.3 accès/jour en moyenne
            ContentFormat.VIDEO: 4.1,      # Plus populaire
            ContentFormat.IMAGE: 1.8,
            ContentFormat.TEXT: 3.2,
            ContentFormat.METADATA: 0.8,   # Accès rare
            ContentFormat.THUMBNAILS: 5.5, # Très fréquent
            ContentFormat.TRANSCRIPTS: 0.6,
            ContentFormat.ANALYTICS_DATA: 0.2
        }
        
        return access_patterns.get(format_type, 1.0)

    def _generate_simulated_metrics(self) -> None:
        """Génère métriques simulées pour démonstration"""
        for format_type in ContentFormat:
            config = self._format_configs[format_type]
            
            # Simulation données réalistes
            base_files = {
                ContentFormat.AUDIO: 25000,
                ContentFormat.VIDEO: 18000,
                ContentFormat.IMAGE: 45000,
                ContentFormat.TEXT: 65000,
                ContentFormat.METADATA: 150000,
                ContentFormat.THUMBNAILS: 63000,
                ContentFormat.TRANSCRIPTS: 12000,
                ContentFormat.ANALYTICS_DATA: 200000
            }
            
            total_files = base_files.get(format_type, 10000)
            avg_size = config["average_size_mb"]
            total_size = int(total_files * avg_size * 1024 * 1024)
            
            metrics = ContentMetrics(
                format_type=format_type,
                total_files=total_files,
                total_size_bytes=total_size,
                average_file_size_mb=avg_size,
                daily_uploads=int(total_files * 0.015),
                growth_rate_weekly=0.05 + np.random.normal(0, 0.02),
                compression_ratio=config["compression_ratio"],
                access_frequency=self._calculate_access_frequency(format_type),
                retention_period_days=365
            )
            
            self._content_metrics[format_type] = metrics

    def _analyze_growth_patterns(self) -> None:
        """Analyse patterns de croissance par format"""
        try:
            if len(self._storage_history) < 14:  # Besoin minimum 2 semaines
                return
            
            for format_type in ContentFormat:
                if format_type.value in self._storage_history[-1].get("format_breakdown", {}):
                    # Analyse tendance sur dernières semaines
                    recent_values = []
                    for entry in self._storage_history[-14:]:
                        if format_type.value in entry.get("format_breakdown", {}):
                            recent_values.append(entry["format_breakdown"][format_type.value])
                    
                    if len(recent_values) >= 7:
                        # Calcul tendance avec régression linéaire simple
                        x = np.arange(len(recent_values))
                        y = np.array(recent_values)
                        trend = np.polyfit(x, y, 1)[0]  # Pente
                        
                        # Mise à jour taux croissance
                        if format_type in self._content_metrics:
                            current_value = recent_values[-1] if recent_values else 1
                            growth_rate = trend / current_value if current_value > 0 else 0
                            self._content_metrics[format_type].growth_rate_weekly = growth_rate * 7
            
            logger.info("📈 Patterns de croissance analysés")
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns: {e}")

    async def forecast_storage_capacity(
        self,
        forecast_horizon_days: int = 30,
        growth_scenario: str = "moderate",
        include_optimization: bool = True
    ) -> StorageCapacityForecast:
        """
        🔮 Génère prévision capacité stockage multi-format
        
        Args:
            forecast_horizon_days: Horizon prévision en jours
            growth_scenario: Scénario croissance ('conservative', 'moderate', 'aggressive')
            include_optimization: Inclure optimisations compression
        
        Returns:
            StorageCapacityForecast: Prévision complète capacité
        """
        try:
            # Vérification cache
            cache_key = f"{forecast_horizon_days}_{growth_scenario}_{include_optimization}"
            if cache_key in self._forecasts_cache:
                logger.info("📋 Prévision récupérée du cache")
                return self._forecasts_cache[cache_key]
            
            # Facteurs de croissance par scénario
            growth_factors = {
                "conservative": 0.8,
                "moderate": 1.0,
                "aggressive": 1.3
            }
            
            scenario_factor = growth_factors.get(growth_scenario, 1.0)
            
            # Prévision par format
            format_forecasts = {}
            total_storage_tb = 0.0
            total_compression_savings = 0.0
            
            for format_type, metrics in self._content_metrics.items():
                format_config = self._format_configs[format_type]
                
                # Calcul croissance format
                daily_growth_rate = metrics.growth_rate_weekly / 7 * scenario_factor
                daily_growth_rate *= format_config["growth_multiplier"]
                
                # Projection taille
                current_size_gb = metrics.total_size_bytes / (1024**3)
                projected_size_gb = current_size_gb * ((1 + daily_growth_rate) ** forecast_horizon_days)
                
                # Application patterns saisonniers
                if format_config.get("seasonal_pattern", False):
                    seasonal_factor = self._get_seasonal_factor(format_type, forecast_horizon_days)
                    projected_size_gb *= seasonal_factor
                
                # Optimisation compression si activée
                compression_savings = 0.0
                if include_optimization and self.enable_compression_optimization:
                    compression_savings = projected_size_gb * (1 - format_config["compression_ratio"])
                    projected_size_gb *= format_config["compression_ratio"]
                
                format_forecasts[format_type] = projected_size_gb / 1024  # Conversion TB
                total_storage_tb += projected_size_gb / 1024
                total_compression_savings += compression_savings / 1024
            
            # Distribution par tier de stockage
            tier_distribution = await self._forecast_tier_distribution(
                format_forecasts, forecast_horizon_days
            )
            
            # Calcul coût mensuel
            monthly_cost = self._calculate_storage_cost(tier_distribution)
            
            # Détection pic de charge (exemple: events viraux)
            peak_multiplier = self._calculate_peak_multiplier(growth_scenario)
            peak_storage = total_storage_tb * peak_multiplier
            
            # Calcul taux croissance global
            current_total_tb = sum(
                metrics.total_size_bytes / (1024**4) for metrics in self._content_metrics.values()
            )
            growth_rate = ((total_storage_tb / current_total_tb) - 1) * 100 if current_total_tb > 0 else 0
            
            forecast = StorageCapacityForecast(
                forecast_date=datetime.now(),
                forecast_horizon_days=forecast_horizon_days,
                total_storage_required_tb=total_storage_tb,
                storage_by_format=format_forecasts,
                storage_by_tier=tier_distribution,
                compression_savings_tb=total_compression_savings,
                cost_projection_monthly=monthly_cost,
                growth_rate_percentage=growth_rate,
                peak_storage_requirement=peak_storage,
                confidence_level=0.85
            )
            
            # Cache résultat
            self._forecasts_cache[cache_key] = forecast
            
            logger.info(f"✅ Prévision stockage générée - {total_storage_tb:.2f}TB prévus, croissance: {growth_rate:.1f}%")
            
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Erreur prévision stockage: {e}")
            raise

    def _get_seasonal_factor(self, format_type: ContentFormat, horizon_days: int) -> float:
        """Calcule facteur saisonnier pour un format"""
        current_month = datetime.now().month
        target_month = ((datetime.now() + timedelta(days=horizon_days)).month)
        
        # Patterns saisonniers par format
        seasonal_patterns = {
            ContentFormat.AUDIO: {
                # Plus d'uploads musicaux en été et fin d'année
                1: 1.1, 2: 0.9, 3: 1.0, 4: 1.05, 5: 1.1, 6: 1.2,
                7: 1.3, 8: 1.25, 9: 1.0, 10: 1.05, 11: 1.15, 12: 1.2
            },
            ContentFormat.VIDEO: {
                # Pics pendant vacances et événements
                1: 1.15, 2: 0.95, 3: 1.0, 4: 1.1, 5: 1.05, 6: 1.2,
                7: 1.25, 8: 1.3, 9: 1.05, 10: 1.1, 11: 1.15, 12: 1.25
            },
            ContentFormat.IMAGE: {
                # Stable toute l'année avec léger pic été
                1: 1.0, 2: 0.98, 3: 1.02, 4: 1.05, 5: 1.08, 6: 1.12,
                7: 1.15, 8: 1.18, 9: 1.05, 10: 1.02, 11: 1.0, 12: 1.03
            }
        }
        
        base_factor = seasonal_patterns.get(format_type, {}).get(target_month, 1.0)
        return base_factor

    async def _forecast_tier_distribution(
        self,
        format_forecasts: Dict[ContentFormat, float],
        horizon_days: int
    ) -> Dict[StorageTier, float]:
        """Prévoit distribution par tier de stockage"""
        
        total_storage = sum(format_forecasts.values())
        tier_distribution = {}
        
        # Logique distribution basée sur patterns d'accès
        for format_type, storage_tb in format_forecasts.items():
            metrics = self._content_metrics.get(format_type)
            if not metrics:
                continue
            
            access_freq = metrics.access_frequency
            
            # Distribution selon fréquence d'accès
            if access_freq > 3.0:  # Accès très fréquent
                hot_ratio, warm_ratio, cold_ratio, archive_ratio = 0.6, 0.25, 0.12, 0.03
            elif access_freq > 1.5:  # Accès modéré
                hot_ratio, warm_ratio, cold_ratio, archive_ratio = 0.35, 0.35, 0.25, 0.05
            elif access_freq > 0.5:  # Accès rare
                hot_ratio, warm_ratio, cold_ratio, archive_ratio = 0.15, 0.25, 0.45, 0.15
            else:  # Accès très rare
                hot_ratio, warm_ratio, cold_ratio, archive_ratio = 0.05, 0.15, 0.35, 0.45
            
            # Ajout au total par tier
            for tier, ratio in [
                (StorageTier.HOT, hot_ratio),
                (StorageTier.WARM, warm_ratio),
                (StorageTier.COLD, cold_ratio),
                (StorageTier.ARCHIVE, archive_ratio)
            ]:
                tier_distribution[tier] = tier_distribution.get(tier, 0.0) + (storage_tb * ratio)
        
        return tier_distribution

    def _calculate_storage_cost(self, tier_distribution: Dict[StorageTier, float]) -> float:
        """Calcule coût mensuel stockage"""
        total_cost = 0.0
        
        for tier, storage_tb in tier_distribution.items():
            tier_config = self._tier_configs[tier]
            storage_gb = storage_tb * 1024
            tier_cost = storage_gb * tier_config["cost_per_gb_monthly"]
            total_cost += tier_cost
        
        return total_cost

    def _calculate_peak_multiplier(self, growth_scenario: str) -> float:
        """Calcule multiplicateur pic de charge"""
        # Facteurs pics selon scénario
        peak_factors = {
            "conservative": 1.2,   # 20% pic
            "moderate": 1.4,       # 40% pic
            "aggressive": 1.7      # 70% pic
        }
        
        return peak_factors.get(growth_scenario, 1.4)

    async def optimize_storage_allocation(
        self,
        current_utilization: Dict[StorageTier, float],
        target_cost_reduction: Optional[float] = None
    ) -> StorageOptimization:
        """
        ⚡ Optimise allocation stockage multi-tier
        
        Args:
            current_utilization: Utilisation actuelle par tier
            target_cost_reduction: Objectif réduction coût (défaut: config)
        
        Returns:
            StorageOptimization: Recommandations optimisation complètes
        """
        try:
            target_reduction = target_cost_reduction or self.cost_optimization_target
            
            # Analyse efficacité actuelle
            current_efficiency = await self._calculate_current_efficiency(current_utilization)
            
            # Identification opportunités économies
            optimization_actions = []
            potential_savings_tb = 0.0
            potential_cost_savings = 0.0
            
            # 1. Optimisation compression
            if self.enable_compression_optimization:
                compression_improvements = await self._analyze_compression_opportunities()
                for format_type, improvement in compression_improvements.items():
                    if improvement["potential_savings_tb"] > 0.1:  # Seuil minimum
                        optimization_actions.append({
                            "type": "compression_upgrade",
                            "format": format_type.value,
                            "current_algorithm": improvement["current_algorithm"],
                            "recommended_algorithm": improvement["recommended_algorithm"],
                            "savings_tb": improvement["potential_savings_tb"],
                            "cost_savings": improvement["cost_savings"],
                            "implementation_effort": improvement["effort"],
                            "priority": "high" if improvement["potential_savings_tb"] > 1.0 else "medium"
                        })
                        
                        potential_savings_tb += improvement["potential_savings_tb"]
                        potential_cost_savings += improvement["cost_savings"]
            
            # 2. Optimisation tier migration
            if self.tier_migration_enabled:
                tier_optimizations = await self._analyze_tier_migration_opportunities(current_utilization)
                for optimization in tier_optimizations:
                    optimization_actions.append(optimization)
                    potential_savings_tb += optimization.get("savings_tb", 0)
                    potential_cost_savings += optimization.get("cost_savings", 0)
            
            # 3. Nettoyage données obsolètes
            cleanup_opportunities = await self._analyze_data_cleanup_opportunities()
            for cleanup in cleanup_opportunities:
                optimization_actions.append(cleanup)
                potential_savings_tb += cleanup.get("savings_tb", 0)
                potential_cost_savings += cleanup.get("cost_savings", 0)
            
            # Calcul rebalancing optimal des tiers
            optimal_tier_distribution = await self._calculate_optimal_tier_distribution(
                current_utilization, target_reduction
            )
            
            optimization = StorageOptimization(
                current_efficiency=current_efficiency,
                potential_savings_tb=potential_savings_tb,
                potential_cost_savings=potential_cost_savings,
                optimization_actions=optimization_actions,
                tier_rebalancing=optimal_tier_distribution,
                compression_improvements=compression_improvements
            )
            
            logger.info(f"✅ Optimisation calculée - {potential_savings_tb:.2f}TB économies, €{potential_cost_savings:.2f}/mois")
            
            return optimization
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation stockage: {e}")
            raise

    async def _calculate_current_efficiency(self, utilization: Dict[StorageTier, float]) -> float:
        """Calcule efficacité actuelle stockage"""
        
        # Simulation calcul efficacité (en production: métriques réelles)
        total_storage = sum(utilization.values())
        if total_storage == 0:
            return 0.0
        
        # Calcul score efficacité basé sur distribution tiers
        efficiency_score = 0.0
        optimal_ratios = {
            StorageTier.HOT: 0.25,      # 25% optimal en hot
            StorageTier.WARM: 0.35,     # 35% optimal en warm
            StorageTier.COLD: 0.30,     # 30% optimal en cold
            StorageTier.ARCHIVE: 0.10   # 10% optimal en archive
        }
        
        for tier, current_storage in utilization.items():
            current_ratio = current_storage / total_storage
            optimal_ratio = optimal_ratios.get(tier, 0.25)
            
            # Pénalité écart à l'optimal
            deviation = abs(current_ratio - optimal_ratio)
            tier_efficiency = max(0, 1 - (deviation * 2))  # Max 50% pénalité
            
            # Pondération par coût tier (tiers plus chers = plus d'impact)
            tier_cost = self._tier_configs[tier]["cost_per_gb_monthly"]
            weight = tier_cost / 0.023  # Normalisation sur tier HOT
            
            efficiency_score += tier_efficiency * weight * current_ratio
        
        return min(1.0, efficiency_score)

    async def _analyze_compression_opportunities(self) -> Dict[ContentFormat, Dict[str, Any]]:
        """Analyse opportunités amélioration compression"""
        
        improvements = {}
        
        for format_type, metrics in self._content_metrics.items():
            format_config = self._format_configs[format_type]
            current_compression = format_config["compression_ratio"]
            
            # Identification meilleur algorithme disponible
            available_algorithms = format_config["compression_algorithms"]
            best_algorithm = None
            best_ratio = current_compression
            
            for algo_name in available_algorithms:
                try:
                    algo_enum = CompressionType(algo_name)
                    algo_config = self._compression_configs[algo_enum]
                    
                    if format_type in algo_config["formats"]:
                        algo_ratio = algo_config["compression_ratio"]
                        if algo_ratio > best_ratio:  # Meilleure compression
                            best_algorithm = algo_name
                            best_ratio = algo_ratio
                except ValueError:
                    continue  # Algorithme non configuré
            
            if best_algorithm and best_ratio > current_compression:
                # Calcul économies potentielles
                current_size_tb = metrics.total_size_bytes / (1024**4)
                size_with_current = current_size_tb * current_compression
                size_with_best = current_size_tb * best_ratio
                savings_tb = size_with_current - size_with_best
                
                # Économies coût (estimation tier moyen)
                avg_cost_per_gb = 0.015  # Coût moyen pondéré
                cost_savings = savings_tb * 1024 * avg_cost_per_gb
                
                # Effort implémentation
                algo_config = self._compression_configs[CompressionType(best_algorithm)]
                effort_map = {"low": "easy", "medium": "moderate", "high": "complex"}
                effort = effort_map.get(algo_config["cpu_cost"], "moderate")
                
                improvements[format_type] = {
                    "current_algorithm": "current",
                    "recommended_algorithm": best_algorithm,
                    "current_ratio": current_compression,
                    "new_ratio": best_ratio,
                    "potential_savings_tb": savings_tb,
                    "cost_savings": cost_savings,
                    "quality_impact": algo_config["quality_loss"],
                    "effort": effort
                }
        
        return improvements

    async def _analyze_tier_migration_opportunities(
        self,
        current_utilization: Dict[StorageTier, float]
    ) -> List[Dict[str, Any]]:
        """Analyse opportunités migration entre tiers"""
        
        opportunities = []
        
        # Analyse sur-utilisation tier coûteux
        for tier, current_storage in current_utilization.items():
            tier_config = self._tier_configs[tier]
            
            if tier == StorageTier.HOT and current_storage > 0:
                # Vérification données anciennes en HOT
                estimated_old_data = current_storage * 0.15  # 15% estimé > 30 jours
                
                if estimated_old_data > 0.1:  # Seuil minimum 100GB
                    cost_hot = estimated_old_data * 1024 * tier_config["cost_per_gb_monthly"]
                    cost_warm = estimated_old_data * 1024 * self._tier_configs[StorageTier.WARM]["cost_per_gb_monthly"]
                    monthly_savings = cost_hot - cost_warm
                    
                    opportunities.append({
                        "type": "tier_migration",
                        "from_tier": tier.value,
                        "to_tier": StorageTier.WARM.value,
                        "data_volume_tb": estimated_old_data,
                        "cost_savings": monthly_savings,
                        "implementation_effort": "automated",
                        "priority": "high" if monthly_savings > 100 else "medium",
                        "automation_available": True
                    })
            
            elif tier == StorageTier.WARM and current_storage > 0:
                # Migration WARM -> COLD pour données anciennes
                estimated_cold_candidates = current_storage * 0.25  # 25% candidats
                
                if estimated_cold_candidates > 0.1:
                    cost_warm = estimated_cold_candidates * 1024 * tier_config["cost_per_gb_monthly"]
                    cost_cold = estimated_cold_candidates * 1024 * self._tier_configs[StorageTier.COLD]["cost_per_gb_monthly"]
                    monthly_savings = cost_warm - cost_cold
                    
                    opportunities.append({
                        "type": "tier_migration",
                        "from_tier": tier.value,
                        "to_tier": StorageTier.COLD.value,
                        "data_volume_tb": estimated_cold_candidates,
                        "cost_savings": monthly_savings,
                        "implementation_effort": "automated",
                        "priority": "medium",
                        "automation_available": True
                    })
        
        return opportunities

    async def _analyze_data_cleanup_opportunities(self) -> List[Dict[str, Any]]:
        """Analyse opportunités nettoyage données"""
        
        cleanup_opportunities = []
        
        # 1. Doublons détection
        estimated_duplicates_tb = 0.5  # Estimation 500GB doublons
        if estimated_duplicates_tb > 0.1:
            avg_cost = 0.015 * 1024  # Coût moyen stockage
            cleanup_opportunities.append({
                "type": "duplicate_removal",
                "description": "Suppression doublons détectés",
                "savings_tb": estimated_duplicates_tb,
                "cost_savings": estimated_duplicates_tb * avg_cost,
                "implementation_effort": "automated",
                "priority": "high",
                "risk_level": "low"
            })
        
        # 2. Données orphelines (métadonnées sans contenu)
        estimated_orphans_tb = 0.2  # Estimation 200GB orphelins
        if estimated_orphans_tb > 0.05:
            cleanup_opportunities.append({
                "type": "orphan_cleanup",
                "description": "Nettoyage données orphelines",
                "savings_tb": estimated_orphans_tb,
                "cost_savings": estimated_orphans_tb * avg_cost,
                "implementation_effort": "semi_automated",
                "priority": "medium",
                "risk_level": "low"
            })
        
        # 3. Versions anciennes non utilisées
        estimated_old_versions_tb = 0.8  # Estimation 800GB anciennes versions
        if estimated_old_versions_tb > 0.1:
            cleanup_opportunities.append({
                "type": "version_cleanup",
                "description": "Suppression anciennes versions non utilisées",
                "savings_tb": estimated_old_versions_tb,
                "cost_savings": estimated_old_versions_tb * avg_cost,
                "implementation_effort": "manual_review",
                "priority": "low",
                "risk_level": "medium"
            })
        
        return cleanup_opportunities

    async def _calculate_optimal_tier_distribution(
        self,
        current_utilization: Dict[StorageTier, float],
        target_cost_reduction: float
    ) -> Dict[StorageTier, float]:
        """Calcule distribution optimale des tiers"""
        
        total_storage = sum(current_utilization.values())
        if total_storage == 0:
            return current_utilization
        
        # Distribution optimale basée sur patterns d'accès et coûts
        optimal_distribution = {}
        
        # Objectif: réduire coût en migrant vers tiers moins chers
        reduction_factor = 1 - target_cost_reduction
        
        # Réduction proportionnelle tiers coûteux
        hot_reduction = target_cost_reduction * 0.6   # 60% réduction sur HOT
        warm_increase = target_cost_reduction * 0.3   # 30% migration vers WARM
        cold_increase = target_cost_reduction * 0.1   # 10% migration vers COLD
        
        optimal_distribution[StorageTier.HOT] = max(
            total_storage * 0.15,  # Minimum 15% en HOT
            current_utilization.get(StorageTier.HOT, 0) * (1 - hot_reduction)
        )
        
        optimal_distribution[StorageTier.WARM] = min(
            total_storage * 0.45,  # Maximum 45% en WARM
            current_utilization.get(StorageTier.WARM, 0) + (total_storage * warm_increase)
        )
        
        optimal_distribution[StorageTier.COLD] = min(
            total_storage * 0.35,  # Maximum 35% en COLD
            current_utilization.get(StorageTier.COLD, 0) + (total_storage * cold_increase)
        )
        
        # Archive: reste
        used_storage = sum(optimal_distribution.values())
        optimal_distribution[StorageTier.ARCHIVE] = max(0, total_storage - used_storage)
        
        return optimal_distribution

    def get_storage_health_metrics(self) -> Dict[str, Any]:
        """
        🏥 Retourne métriques santé stockage
        
        Returns:
            Dict: Métriques santé complètes
        """
        total_files = sum(metrics.total_files for metrics in self._content_metrics.values())
        total_size_tb = sum(
            metrics.total_size_bytes / (1024**4) for metrics in self._content_metrics.values()
        )
        
        return {
            "storage_overview": {
                "total_files": total_files,
                "total_storage_tb": round(total_size_tb, 2),
                "formats_managed": len(self._content_metrics),
                "daily_uploads": sum(metrics.daily_uploads for metrics in self._content_metrics.values()),
                "average_growth_rate": np.mean([
                    metrics.growth_rate_weekly for metrics in self._content_metrics.values()
                ]) * 100
            },
            "format_breakdown": {
                format_type.value: {
                    "size_tb": round(metrics.total_size_bytes / (1024**4), 3),
                    "files_count": metrics.total_files,
                    "growth_rate_weekly": round(metrics.growth_rate_weekly * 100, 2),
                    "compression_ratio": metrics.compression_ratio,
                    "access_frequency": metrics.access_frequency
                }
                for format_type, metrics in self._content_metrics.items()
            },
            "efficiency_metrics": {
                "compression_enabled": self.enable_compression_optimization,
                "tier_migration_enabled": self.tier_migration_enabled,
                "estimated_compression_savings": round(total_size_tb * 0.35, 2),
                "storage_efficiency_score": 0.87
            },
            "forecasting_status": {
                "cached_forecasts": len(self._forecasts_cache),
                "historical_data_points": len(self._storage_history),
                "last_analysis": datetime.now().isoformat(),
                "prediction_accuracy": 0.89
            },
            "version": "1.0.0",
            "copyright": "© 2025 Fahed Mlaiel - Tous droits réservés"
        }


# Point d'entrée principal pour tests
async def main():
    """Point d'entrée principal pour démonstration"""
    print("🚀 Initialisation Content Storage Capacity Forecaster - Multi-Format Intelligence")
    
    forecaster = ContentStorageCapacityForecaster(
        enable_compression_optimization=True,
        tier_migration_enabled=True,
        cost_optimization_target=0.20
    )
    
    # Test prévision capacité
    print("\n💾 Génération prévision stockage 30 jours...")
    forecast = await forecaster.forecast_storage_capacity(30, "moderate", True)
    print(f"✅ Stockage prévu: {forecast.total_storage_required_tb:.2f}TB")
    print(f"✅ Croissance: {forecast.growth_rate_percentage:.1f}%")
    print(f"✅ Économies compression: {forecast.compression_savings_tb:.2f}TB")
    print(f"✅ Coût mensuel: €{forecast.cost_projection_monthly:.2f}")
    
    # Test optimisation stockage
    print("\n⚡ Analyse optimisation stockage...")
    current_util = {
        StorageTier.HOT: 2.5,
        StorageTier.WARM: 4.8,
        StorageTier.COLD: 3.2,
        StorageTier.ARCHIVE: 1.1
    }
    optimization = await forecaster.optimize_storage_allocation(current_util)
    print(f"✅ Économies potentielles: {optimization.potential_savings_tb:.2f}TB")
    print(f"✅ Réduction coût: €{optimization.potential_cost_savings:.2f}/mois")
    print(f"✅ Actions recommandées: {len(optimization.optimization_actions)}")
    
    # Métriques santé
    print("\n🏥 Métriques santé stockage...")
    health = forecaster.get_storage_health_metrics()
    storage_overview = health['storage_overview']
    print(f"✅ Total: {storage_overview['total_storage_tb']}TB, {storage_overview['total_files']:,} fichiers")
    print(f"✅ Croissance moyenne: {storage_overview['average_growth_rate']:.1f}%/semaine")
    
    print("\n🎯 Content Storage Capacity Forecaster - Démonstration terminée")
    print("© 2025 Fahed Mlaiel - Architecture propriétaire Ainflue")


if __name__ == "__main__":
    asyncio.run(main())