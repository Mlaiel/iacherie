"""
Mobile Distribution Optimizer - Distribution Module
=================================================
Optimization distribution mobile avec native app integration
et mobile-first strategies.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class MobileOS(Enum):
    """Systèmes d'exploitation mobile."""
    IOS = "ios"
    ANDROID = "android"
    WINDOWS_MOBILE = "windows_mobile"
    HUAWEI_HARMONY = "huawei_harmony"

class DeviceCategory(Enum):
    """Catégories d'appareils."""
    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    FOLDABLE = "foldable"
    SMARTWATCH = "smartwatch"
    SMART_TV = "smart_tv"

class NetworkType(Enum):
    """Types de réseau."""
    WIFI = "wifi"
    CELLULAR_5G = "5g"
    CELLULAR_4G = "4g"
    CELLULAR_3G = "3g"
    SATELLITE = "satellite"

class MobileFormat(Enum):
    """Formats mobile optimisés."""
    VERTICAL_VIDEO = "vertical_video"
    SQUARE_VIDEO = "square_video"
    HORIZONTAL_VIDEO = "horizontal_video"
    MOBILE_STORY = "mobile_story"
    INTERACTIVE_CAROUSEL = "interactive_carousel"
    AMP_ARTICLE = "amp_article"

class AppIntegrationType(Enum):
    """Types d'intégration app."""
    NATIVE_SHARING = "native_sharing"
    IN_APP_BROWSER = "in_app_browser"
    DEEP_LINK = "deep_link"
    UNIVERSAL_LINK = "universal_link"
    CUSTOM_SCHEME = "custom_scheme"

@dataclass
class MobileDeviceProfile:
    """Profil appareil mobile."""
    device_id: str
    os: MobileOS
    os_version: str
    device_category: DeviceCategory
    screen_size: Tuple[int, int]
    screen_density: float
    network_capabilities: List[NetworkType]
    installed_apps: List[str]
    usage_patterns: Dict[str, Any]
    battery_optimization_preferences: Dict[str, Any]

@dataclass
class MobileOptimizationResult:
    """Résultat optimisation mobile."""
    original_content_id: str
    optimized_content_id: str
    target_os: MobileOS
    target_format: MobileFormat
    optimization_applied: List[str]
    file_size_reduction: float
    loading_time_improvement: float
    battery_impact_score: float
    user_experience_score: float

@dataclass
class AppIntegrationConfig:
    """Configuration intégration app."""
    app_id: str
    platform: str
    integration_type: AppIntegrationType
    deep_link_schema: str
    universal_link_domain: str
    sharing_parameters: Dict[str, Any]
    analytics_tracking: Dict[str, Any]

@dataclass
class PushNotificationStrategy:
    """Stratégie notifications push."""
    notification_id: str
    target_segments: List[str]
    timing_strategy: str
    personalization_level: str
    content_preview: Dict[str, Any]
    delivery_optimization: Dict[str, Any]
    expected_open_rate: float

class MobileDistributionOptimizer:
    """Optimization distribution mobile avec native app integration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.format_optimizer = MobileFormatOptimizer()
        self.app_integrator = AppIntegrationManager()
        self.bandwidth_optimizer = MobileBandwidthOptimizer()
        self.notification_manager = PushNotificationManager()
        self.analytics_integrator = MobileAnalyticsIntegrator()
        self.offline_sync_manager = OfflineSyncManager()
        self.device_profiler = MobileDeviceProfiler()
        
    async def mobile_format_optimization(
        self,
        content_data: Dict[str, Any],
        target_devices: List[MobileDeviceProfile],
        optimization_level: str = "aggressive"
    ) -> Dict[str, MobileOptimizationResult]:
        """Optimisation formats mobile avec adaptation appareil."""
        try:
            optimization_results = {}
            
            for device_profile in target_devices:
                device_id = device_profile.device_id
                
                # Analyse contraintes appareil
                device_constraints = await self._analyze_device_constraints(device_profile)
                
                # Sélection format optimal
                optimal_format = await self.format_optimizer.select_optimal_format(
                    content_data, device_profile, device_constraints
                )
                
                # Optimisation résolution/qualité
                resolution_optimization = await self.format_optimizer.optimize_resolution(
                    content_data, device_profile.screen_size, device_profile.screen_density
                )
                
                # Optimisation compression mobile
                compression_optimization = await self.format_optimizer.optimize_compression(
                    content_data, device_profile.network_capabilities, optimization_level
                )
                
                # Optimisation batterie
                battery_optimization = await self.format_optimizer.optimize_for_battery_life(
                    content_data, device_profile.battery_optimization_preferences
                )
                
                # Génération contenu optimisé
                optimized_content_id = f"{content_data.get('content_id', 'content')}_{device_id}_mobile"
                
                # Calcul métriques amélioration
                metrics = await self._calculate_optimization_metrics(
                    content_data, resolution_optimization, compression_optimization, battery_optimization
                )
                
                # Compilation optimisations appliquées
                optimizations_applied = [
                    f"format_conversion_to_{optimal_format.value}",
                    f"resolution_optimization_{resolution_optimization['target_resolution']}",
                    f"compression_{compression_optimization['compression_level']}",
                    f"battery_optimization_{battery_optimization['optimization_level']}"
                ]
                
                result = MobileOptimizationResult(
                    original_content_id=content_data.get('content_id', ''),
                    optimized_content_id=optimized_content_id,
                    target_os=device_profile.os,
                    target_format=optimal_format,
                    optimization_applied=optimizations_applied,
                    file_size_reduction=metrics['file_size_reduction'],
                    loading_time_improvement=metrics['loading_time_improvement'],
                    battery_impact_score=metrics['battery_impact_score'],
                    user_experience_score=metrics['user_experience_score']
                )
                
                optimization_results[device_id] = result
                
                self.logger.info(f"Mobile optimization completed for device {device_id}: {metrics['file_size_reduction']:.1%} size reduction")
                
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Mobile format optimization error: {e}")
            return {}
    
    async def app_deep_linking(
        self,
        content_data: Dict[str, Any],
        target_apps: List[str],
        platforms: List[str]
    ) -> Dict[str, AppIntegrationConfig]:
        """Configuration deep linking avec apps natives."""
        try:
            app_integrations = {}
            
            for app_id in target_apps:
                for platform in platforms:
                    integration_key = f"{app_id}_{platform}"
                    
                    # Analyse capacités app
                    app_capabilities = await self.app_integrator.analyze_app_capabilities(
                        app_id, platform
                    )
                    
                    # Sélection type intégration optimal
                    optimal_integration_type = await self.app_integrator.select_integration_type(
                        app_capabilities, content_data, platform
                    )
                    
                    # Configuration deep links
                    deep_link_config = await self.app_integrator.configure_deep_links(
                        app_id, platform, content_data, optimal_integration_type
                    )
                    
                    # Configuration universal links (iOS)
                    universal_link_config = {}
                    if platform == 'ios':
                        universal_link_config = await self.app_integrator.configure_universal_links(
                            app_id, content_data
                        )
                    
                    # Configuration paramètres partage
                    sharing_config = await self.app_integrator.configure_sharing_parameters(
                        app_id, platform, content_data
                    )
                    
                    # Configuration tracking analytics
                    analytics_config = await self.app_integrator.configure_analytics_tracking(
                        app_id, platform, content_data
                    )
                    
                    integration_config = AppIntegrationConfig(
                        app_id=app_id,
                        platform=platform,
                        integration_type=optimal_integration_type,
                        deep_link_schema=deep_link_config.get('schema', ''),
                        universal_link_domain=universal_link_config.get('domain', ''),
                        sharing_parameters=sharing_config,
                        analytics_tracking=analytics_config
                    )
                    
                    app_integrations[integration_key] = integration_config
                    
                    self.logger.info(f"App integration configured for {app_id} on {platform}")
                    
            return app_integrations
            
        except Exception as e:
            self.logger.error(f"App deep linking error: {e}")
            return {}
    
    async def mobile_bandwidth_optimization(
        self,
        content_data: Dict[str, Any],
        network_conditions: Dict[str, Any],
        data_usage_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimisation bande passante mobile avec adaptation réseau."""
        try:
            # Analyse conditions réseau
            network_analysis = await self.bandwidth_optimizer.analyze_network_conditions(
                network_conditions
            )
            
            # Optimisation adaptative qualité
            adaptive_quality = await self.bandwidth_optimizer.configure_adaptive_quality(
                content_data, network_analysis, data_usage_preferences
            )
            
            # Configuration progressive loading
            progressive_loading = await self.bandwidth_optimizer.configure_progressive_loading(
                content_data, network_analysis
            )
            
            # Optimisation caching mobile
            mobile_caching = await self.bandwidth_optimizer.optimize_mobile_caching(
                content_data, network_analysis, data_usage_preferences
            )
            
            # Configuration compression intelligente
            intelligent_compression = await self.bandwidth_optimizer.configure_intelligent_compression(
                content_data, network_analysis
            )
            
            # Estimation économies données
            data_savings = await self._calculate_data_savings(
                adaptive_quality, progressive_loading, mobile_caching, intelligent_compression
            )
            
            return {
                'network_analysis': network_analysis,
                'adaptive_quality_config': adaptive_quality,
                'progressive_loading_config': progressive_loading,
                'mobile_caching_config': mobile_caching,
                'intelligent_compression_config': intelligent_compression,
                'estimated_data_savings': data_savings,
                'optimization_summary': {
                    'bandwidth_reduction': data_savings.get('bandwidth_reduction', 0),
                    'loading_time_improvement': data_savings.get('loading_time_improvement', 0),
                    'user_experience_score': data_savings.get('user_experience_score', 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Mobile bandwidth optimization error: {e}")
            return {}
    
    async def push_notification_coordination(
        self,
        content_schedule: Dict[str, datetime],
        user_segments: List[Dict[str, Any]],
        engagement_goals: Dict[str, Any]
    ) -> List[PushNotificationStrategy]:
        """Coordination notifications push avec stratégies engagement."""
        try:
            notification_strategies = []
            
            for content_id, scheduled_time in content_schedule.items():
                for segment in user_segments:
                    segment_id = segment.get('segment_id')
                    
                    # Analyse préférences segment
                    segment_preferences = await self.notification_manager.analyze_segment_preferences(
                        segment
                    )
                    
                    # Optimisation timing notifications
                    optimal_timing = await self.notification_manager.optimize_notification_timing(
                        scheduled_time, segment_preferences, engagement_goals
                    )
                    
                    # Personnalisation contenu notification
                    personalized_content = await self.notification_manager.personalize_notification_content(
                        content_id, segment, engagement_goals
                    )
                    
                    # Configuration stratégie livraison
                    delivery_strategy = await self.notification_manager.configure_delivery_strategy(
                        segment, optimal_timing, engagement_goals
                    )
                    
                    # Prédiction taux ouverture
                    predicted_open_rate = await self.notification_manager.predict_open_rate(
                        segment, personalized_content, optimal_timing
                    )
                    
                    strategy = PushNotificationStrategy(
                        notification_id=f"{content_id}_{segment_id}_{int(optimal_timing.timestamp())}",
                        target_segments=[segment_id],
                        timing_strategy=optimal_timing.strftime("%Y-%m-%d %H:%M:%S"),
                        personalization_level=segment_preferences.get('personalization_level', 'medium'),
                        content_preview=personalized_content,
                        delivery_optimization=delivery_strategy,
                        expected_open_rate=predicted_open_rate
                    )
                    
                    notification_strategies.append(strategy)
                    
            # Tri par taux ouverture prédit
            notification_strategies.sort(key=lambda x: x.expected_open_rate, reverse=True)
            
            self.logger.info(f"Generated {len(notification_strategies)} push notification strategies")
            
            return notification_strategies
            
        except Exception as e:
            self.logger.error(f"Push notification coordination error: {e}")
            return []
    
    async def mobile_analytics_integration(
        self,
        content_data: Dict[str, Any],
        mobile_platforms: List[str],
        tracking_goals: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Intégration analytics mobile avec tracking avancé."""
        try:
            mobile_analytics = {}
            
            for platform in mobile_platforms:
                platform_analytics = {}
                
                # Configuration tracking événements
                event_tracking = await self.analytics_integrator.configure_event_tracking(
                    content_data, platform, tracking_goals
                )
                
                # Configuration attribution mobile
                attribution_config = await self.analytics_integrator.configure_mobile_attribution(
                    content_data, platform
                )
                
                # Configuration funnel tracking
                funnel_tracking = await self.analytics_integrator.configure_funnel_tracking(
                    content_data, platform, tracking_goals
                )
                
                # Configuration cohort analysis
                cohort_analysis = await self.analytics_integrator.configure_cohort_analysis(
                    content_data, platform
                )
                
                # Configuration real-time analytics
                realtime_analytics = await self.analytics_integrator.configure_realtime_analytics(
                    platform, tracking_goals
                )
                
                platform_analytics = {
                    'event_tracking': event_tracking,
                    'attribution_config': attribution_config,
                    'funnel_tracking': funnel_tracking,
                    'cohort_analysis': cohort_analysis,
                    'realtime_analytics': realtime_analytics,
                    'privacy_compliance': await self._configure_privacy_compliance(platform),
                    'data_export_config': await self._configure_data_export(platform)
                }
                
                mobile_analytics[platform] = platform_analytics
                
                self.logger.info(f"Mobile analytics configured for {platform}")
                
            return mobile_analytics
            
        except Exception as e:
            self.logger.error(f"Mobile analytics integration error: {e}")
            return {}
    
    async def offline_sync_capabilities(
        self,
        content_data: Dict[str, Any],
        sync_strategies: List[str],
        storage_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Capacités sync offline avec gestion intelligente stockage."""
        try:
            # Configuration sync offline
            offline_config = await self.offline_sync_manager.configure_offline_sync(
                content_data, storage_constraints
            )
            
            # Stratégies prioritisation contenu
            content_prioritization = await self.offline_sync_manager.configure_content_prioritization(
                content_data, sync_strategies, storage_constraints
            )
            
            # Configuration sync intelligent
            intelligent_sync = await self.offline_sync_manager.configure_intelligent_sync(
                content_data, sync_strategies
            )
            
            # Gestion stockage local
            local_storage_management = await self.offline_sync_manager.configure_local_storage(
                storage_constraints, content_prioritization
            )
            
            # Configuration sync différentiel
            differential_sync = await self.offline_sync_manager.configure_differential_sync(
                content_data, storage_constraints
            )
            
            # Métriques sync offline
            sync_metrics = await self._calculate_offline_sync_metrics(
                offline_config, content_prioritization, intelligent_sync
            )
            
            return {
                'offline_sync_config': offline_config,
                'content_prioritization': content_prioritization,
                'intelligent_sync_config': intelligent_sync,
                'local_storage_management': local_storage_management,
                'differential_sync_config': differential_sync,
                'sync_metrics': sync_metrics,
                'estimated_storage_usage': sync_metrics.get('storage_usage', 0),
                'sync_efficiency_score': sync_metrics.get('efficiency_score', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Offline sync capabilities error: {e}")
            return {}
    
    async def _analyze_device_constraints(self, device_profile: MobileDeviceProfile) -> Dict[str, Any]:
        """Analyse contraintes appareil."""
        constraints = {
            'max_resolution': device_profile.screen_size,
            'network_limitations': await self._assess_network_limitations(device_profile.network_capabilities),
            'storage_constraints': await self._assess_storage_constraints(device_profile),
            'battery_constraints': device_profile.battery_optimization_preferences.get('level', 'medium'),
            'processing_power': await self._assess_processing_power(device_profile)
        }
        
        return constraints
    
    async def _calculate_optimization_metrics(
        self,
        original_content: Dict[str, Any],
        resolution_opt: Dict[str, Any],
        compression_opt: Dict[str, Any],
        battery_opt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcul métriques optimisation."""
        # Simulation calculs - en production, utiliser métriques réelles
        file_size_reduction = (
            resolution_opt.get('size_reduction', 0.2) +
            compression_opt.get('size_reduction', 0.3) +
            battery_opt.get('size_reduction', 0.1)
        ) / 3
        
        loading_time_improvement = file_size_reduction * 0.8  # Corrélation approximative
        
        battery_impact_score = 0.8 + (battery_opt.get('optimization_level', 0.5) * 0.2)
        
        user_experience_score = (
            (1 - file_size_reduction) * 0.3 +
            loading_time_improvement * 0.4 +
            battery_impact_score * 0.3
        )
        
        return {
            'file_size_reduction': file_size_reduction,
            'loading_time_improvement': loading_time_improvement,
            'battery_impact_score': battery_impact_score,
            'user_experience_score': user_experience_score
        }

class MobileFormatOptimizer:
    """Optimiseur formats mobile."""
    
    async def select_optimal_format(
        self,
        content_data: Dict[str, Any],
        device_profile: MobileDeviceProfile,
        constraints: Dict[str, Any]
    ) -> MobileFormat:
        """Sélection format optimal mobile."""
        content_type = content_data.get('type', 'video')
        device_category = device_profile.device_category
        
        # Logique sélection format
        if content_type == 'video':
            if device_category == DeviceCategory.SMARTPHONE:
                return MobileFormat.VERTICAL_VIDEO
            elif device_category == DeviceCategory.TABLET:
                return MobileFormat.HORIZONTAL_VIDEO
            else:
                return MobileFormat.SQUARE_VIDEO
        elif content_type == 'image':
            return MobileFormat.MOBILE_STORY
        else:
            return MobileFormat.AMP_ARTICLE
    
    async def optimize_resolution(
        self,
        content_data: Dict[str, Any],
        screen_size: Tuple[int, int],
        screen_density: float
    ) -> Dict[str, Any]:
        """Optimisation résolution."""
        width, height = screen_size
        
        # Calcul résolution optimale
        optimal_width = min(width * screen_density, 1920)
        optimal_height = min(height * screen_density, 1080)
        
        # Calcul réduction taille fichier estimée
        original_pixels = content_data.get('width', 1920) * content_data.get('height', 1080)
        optimized_pixels = optimal_width * optimal_height
        size_reduction = 1 - (optimized_pixels / original_pixels)
        
        return {
            'target_resolution': f"{int(optimal_width)}x{int(optimal_height)}",
            'size_reduction': max(0, size_reduction),
            'quality_maintained': size_reduction < 0.5
        }

class AppIntegrationManager:
    """Gestionnaire intégration apps."""
    
    async def analyze_app_capabilities(self, app_id: str, platform: str) -> Dict[str, Any]:
        """Analyse capacités app."""
        # Simulation capacités app
        capabilities = {
            'supports_deep_links': True,
            'supports_universal_links': platform == 'ios',
            'supports_custom_schemes': True,
            'sharing_capabilities': ['native_share', 'in_app_browser'],
            'analytics_integration': True
        }
        
        return capabilities
    
    async def select_integration_type(
        self,
        capabilities: Dict[str, Any],
        content_data: Dict[str, Any],
        platform: str
    ) -> AppIntegrationType:
        """Sélection type intégration."""
        if platform == 'ios' and capabilities.get('supports_universal_links'):
            return AppIntegrationType.UNIVERSAL_LINK
        elif capabilities.get('supports_deep_links'):
            return AppIntegrationType.DEEP_LINK
        else:
            return AppIntegrationType.IN_APP_BROWSER

class MobileBandwidthOptimizer:
    """Optimiseur bande passante mobile."""
    
    async def analyze_network_conditions(self, network_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse conditions réseau."""
        return {
            'connection_type': network_conditions.get('type', 'wifi'),
            'bandwidth_mbps': network_conditions.get('bandwidth', 10),
            'latency_ms': network_conditions.get('latency', 50),
            'reliability_score': network_conditions.get('reliability', 0.9)
        }
    
    async def configure_adaptive_quality(
        self,
        content_data: Dict[str, Any],
        network_analysis: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configuration qualité adaptative."""
        bandwidth = network_analysis.get('bandwidth_mbps', 10)
        
        if bandwidth > 50:
            quality_levels = ['1080p', '720p', '480p']
        elif bandwidth > 10:
            quality_levels = ['720p', '480p', '360p']
        else:
            quality_levels = ['480p', '360p', '240p']
        
        return {
            'quality_levels': quality_levels,
            'default_quality': quality_levels[0],
            'adaptive_switching': True,
            'buffer_threshold': 5  # seconds
        }

class PushNotificationManager:
    """Gestionnaire notifications push."""
    
    async def analyze_segment_preferences(self, segment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse préférences segment."""
        return {
            'preferred_time_ranges': segment.get('active_hours', [9, 17]),
            'notification_frequency': segment.get('frequency_preference', 'medium'),
            'personalization_level': segment.get('personalization', 'high'),
            'engagement_history': segment.get('engagement_rate', 0.15)
        }
    
    async def predict_open_rate(
        self,
        segment: Dict[str, Any],
        content: Dict[str, Any],
        timing: datetime
    ) -> float:
        """Prédiction taux ouverture."""
        base_rate = segment.get('engagement_rate', 0.15)
        
        # Ajustements selon timing
        hour = timing.hour
        if 9 <= hour <= 17:  # Heures ouvrables
            time_multiplier = 1.2
        elif 19 <= hour <= 21:  # Soirée
            time_multiplier = 1.1
        else:
            time_multiplier = 0.8
        
        # Ajustement selon personnalisation
        personalization_multiplier = 1.0
        if content.get('personalization_level') == 'high':
            personalization_multiplier = 1.3
        
        predicted_rate = base_rate * time_multiplier * personalization_multiplier
        
        return min(predicted_rate, 0.8)  # Cap à 80%

class MobileAnalyticsIntegrator:
    """Intégrateur analytics mobile."""
    
    async def configure_event_tracking(
        self,
        content_data: Dict[str, Any],
        platform: str,
        goals: List[str]
    ) -> Dict[str, Any]:
        """Configuration tracking événements."""
        events = {
            'content_view': {'enabled': True, 'parameters': ['content_id', 'duration']},
            'content_share': {'enabled': True, 'parameters': ['platform', 'method']},
            'app_open': {'enabled': True, 'parameters': ['source', 'campaign']},
            'conversion': {'enabled': 'conversion' in goals, 'parameters': ['value', 'currency']}
        }
        
        return {
            'platform': platform,
            'events': events,
            'sampling_rate': 1.0,
            'real_time_enabled': True
        }

class OfflineSyncManager:
    """Gestionnaire sync offline."""
    
    async def configure_offline_sync(
        self,
        content_data: Dict[str, Any],
        storage_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configuration sync offline."""
        max_storage_mb = storage_constraints.get('max_storage_mb', 500)
        
        return {
            'sync_strategy': 'intelligent_priority',
            'max_storage_mb': max_storage_mb,
            'sync_triggers': ['wifi_available', 'charging', 'idle'],
            'cache_duration_hours': 24,
            'compression_enabled': True
        }
    
    async def configure_content_prioritization(
        self,
        content_data: Dict[str, Any],
        strategies: List[str],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configuration priorisation contenu."""
        return {
            'priority_factors': ['user_engagement', 'recency', 'size_efficiency'],
            'priority_weights': {'engagement': 0.5, 'recency': 0.3, 'size': 0.2},
            'max_items': constraints.get('max_cached_items', 100),
            'eviction_policy': 'lru_with_priority'
        }

class MobileDeviceProfiler:
    """Profileur appareils mobile."""
    
    async def create_device_profile(self, device_info: Dict[str, Any]) -> MobileDeviceProfile:
        """Création profil appareil."""
        return MobileDeviceProfile(
            device_id=device_info.get('device_id', 'unknown'),
            os=MobileOS(device_info.get('os', 'android')),
            os_version=device_info.get('os_version', '10.0'),
            device_category=DeviceCategory(device_info.get('category', 'smartphone')),
            screen_size=(device_info.get('screen_width', 1080), device_info.get('screen_height', 1920)),
            screen_density=device_info.get('screen_density', 2.0),
            network_capabilities=[NetworkType.WIFI, NetworkType.CELLULAR_4G],
            installed_apps=device_info.get('installed_apps', []),
            usage_patterns=device_info.get('usage_patterns', {}),
            battery_optimization_preferences=device_info.get('battery_prefs', {'level': 'medium'})
        )