"""Avatar Rendering - Moteur Rendu

Moteur de rendu haute performance pour avatars 3D avec pipeline PBR,
optimisation temps réel et support multi-plateforme.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import logging
import json
import math
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid

# Local imports
from .metahuman import MetaHumanQuality


class RenderingPipeline(Enum):
    """Pipelines de rendu supportés"""
    FORWARD = "forward"
    DEFERRED = "deferred"
    PBR = "pbr"  # Physically Based Rendering
    TOON = "toon"
    REALISTIC = "realistic"
    STYLIZED = "stylized"
    CINEMATIC = "cinematic"


class LightingModel(Enum):
    """Modèles d'éclairage"""
    LAMBERT = "lambert"
    PHONG = "phong"
    BLINN_PHONG = "blinn_phong"
    COOK_TORRANCE = "cook_torrance"
    OREN_NAYAR = "oren_nayar"
    SUBSURFACE = "subsurface"
    PHYSICALLY_BASED = "physically_based"


class RenderQuality(Enum):
    """Niveaux de qualité de rendu"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    CINEMATIC = "cinematic"


class MaterialType(Enum):
    """Types de matériaux"""
    SKIN = "skin"
    HAIR = "hair"
    FABRIC = "fabric"
    METAL = "metal"
    PLASTIC = "plastic"
    GLASS = "glass"
    LEATHER = "leather"
    RUBBER = "rubber"
    CERAMIC = "ceramic"
    ORGANIC = "organic"


class LightType(Enum):
    """Types de sources lumineuses"""
    DIRECTIONAL = "directional"
    POINT = "point"
    SPOT = "spot"
    AREA = "area"
    ENVIRONMENT = "environment"
    IMAGE_BASED = "image_based"


class LODLevel(Enum):
    """Niveaux de détail (Level of Detail)"""
    LOD0 = "lod0"  # Qualité maximale
    LOD1 = "lod1"  # Haute qualité
    LOD2 = "lod2"  # Qualité moyenne
    LOD3 = "lod3"  # Basse qualité
    LOD4 = "lod4"  # Très basse qualité


@dataclass
class MaterialProperties:
    """Propriétés d'un matériau"""
    material_id: str
    material_type: MaterialType
    diffuse_color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    metallic: float = 0.0
    roughness: float = 0.5
    normal_intensity: float = 1.0
    emission_color: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    emission_strength: float = 0.0
    subsurface_scattering: float = 0.0
    transmission: float = 0.0
    alpha: float = 1.0
    texture_maps: Dict[str, str] = field(default_factory=dict)
    custom_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LightSource:
    """Source lumineuse"""
    light_id: str
    light_type: LightType
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    intensity: float = 1.0
    range: float = 10.0
    cone_angle: float = 45.0  # Pour spot light
    falloff: float = 1.0
    shadows_enabled: bool = True
    shadow_quality: str = "medium"
    custom_properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderSettings:
    """Paramètres de rendu"""
    pipeline: RenderingPipeline = RenderingPipeline.PBR
    lighting_model: LightingModel = LightingModel.PHYSICALLY_BASED
    quality: RenderQuality = RenderQuality.HIGH
    resolution: Tuple[int, int] = (1920, 1080)
    fps_target: int = 60
    vsync_enabled: bool = True
    anti_aliasing: str = "msaa_4x"
    shadow_quality: str = "high"
    reflection_quality: str = "medium"
    ambient_occlusion: bool = True
    motion_blur: bool = False
    depth_of_field: bool = False
    bloom: bool = True
    tone_mapping: str = "aces"
    gamma_correction: float = 2.2
    lod_enabled: bool = True
    culling_enabled: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    frame_rate: float = 0.0
    frame_time: float = 0.0
    draw_calls: int = 0
    triangles_rendered: int = 0
    vertices_processed: int = 0
    texture_memory_mb: float = 0.0
    vertex_memory_mb: float = 0.0
    shader_switches: int = 0
    culled_objects: int = 0
    lod_switches: int = 0
    gpu_utilization: float = 0.0
    cpu_utilization: float = 0.0


class MaterialManager:
    """Gestion matériaux avancés"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.materials: Dict[str, MaterialProperties] = {}
        self._initialize_preset_materials()
    
    def _initialize_preset_materials(self):
        """Initialisation des matériaux prédéfinis"""
        presets = {
            "realistic_skin": MaterialProperties(
                material_id="realistic_skin",
                material_type=MaterialType.SKIN,
                diffuse_color=(0.9, 0.7, 0.6),
                metallic=0.0,
                roughness=0.3,
                subsurface_scattering=0.8,
                texture_maps={
                    "diffuse": "skin_diffuse.jpg",
                    "normal": "skin_normal.jpg",
                    "roughness": "skin_roughness.jpg",
                    "subsurface": "skin_sss.jpg"
                }
            ),
            "natural_hair": MaterialProperties(
                material_id="natural_hair",
                material_type=MaterialType.HAIR,
                diffuse_color=(0.3, 0.2, 0.1),
                metallic=0.0,
                roughness=0.8,
                alpha=0.9,
                texture_maps={
                    "diffuse": "hair_diffuse.jpg",
                    "alpha": "hair_alpha.jpg",
                    "normal": "hair_normal.jpg"
                }
            ),
            "cotton_fabric": MaterialProperties(
                material_id="cotton_fabric",
                material_type=MaterialType.FABRIC,
                diffuse_color=(0.8, 0.8, 0.9),
                metallic=0.0,
                roughness=0.7,
                texture_maps={
                    "diffuse": "fabric_diffuse.jpg",
                    "normal": "fabric_normal.jpg",
                    "roughness": "fabric_roughness.jpg"
                }
            ),
            "polished_metal": MaterialProperties(
                material_id="polished_metal",
                material_type=MaterialType.METAL,
                diffuse_color=(0.7, 0.7, 0.8),
                metallic=1.0,
                roughness=0.1,
                texture_maps={
                    "roughness": "metal_roughness.jpg",
                    "normal": "metal_normal.jpg"
                }
            )
        }
        
        self.materials.update(presets)
    
    async def create_material(self, material_spec: Dict[str, Any]) -> MaterialProperties:
        """Création d'un matériau personnalisé"""
        try:
            material = MaterialProperties(
                material_id=material_spec.get('id', str(uuid.uuid4())),
                material_type=MaterialType(material_spec.get('type', 'fabric')),
                diffuse_color=tuple(material_spec.get('diffuse_color', [0.8, 0.8, 0.8])),
                metallic=material_spec.get('metallic', 0.0),
                roughness=material_spec.get('roughness', 0.5),
                normal_intensity=material_spec.get('normal_intensity', 1.0),
                emission_color=tuple(material_spec.get('emission_color', [0.0, 0.0, 0.0])),
                emission_strength=material_spec.get('emission_strength', 0.0),
                subsurface_scattering=material_spec.get('subsurface_scattering', 0.0),
                alpha=material_spec.get('alpha', 1.0),
                texture_maps=material_spec.get('texture_maps', {}),
                custom_properties=material_spec.get('custom_properties', {})
            )
            
            self.materials[material.material_id] = material
            return material
            
        except Exception as e:
            self.logger.error(f"Erreur création matériau: {e}")
            raise
    
    async def optimize_material_for_quality(self, material_id: str, 
                                          quality: RenderQuality) -> MaterialProperties:
        """Optimisation d'un matériau selon la qualité"""
        if material_id not in self.materials:
            raise ValueError(f"Matériau {material_id} non trouvé")
        
        material = self.materials[material_id]
        optimized = MaterialProperties(**material.__dict__)
        
        # Optimisations selon la qualité
        if quality == RenderQuality.LOW:
            optimized.normal_intensity *= 0.5
            optimized.subsurface_scattering *= 0.3
            # Simplifier les texture maps
            simplified_maps = {
                key: value for key, value in optimized.texture_maps.items()
                if key in ['diffuse', 'normal']
            }
            optimized.texture_maps = simplified_maps
            
        elif quality == RenderQuality.MEDIUM:
            optimized.normal_intensity *= 0.8
            optimized.subsurface_scattering *= 0.6
            
        elif quality == RenderQuality.ULTRA:
            optimized.normal_intensity *= 1.2
            optimized.subsurface_scattering *= 1.1
            
        return optimized
    
    def get_material_presets(self) -> List[str]:
        """Liste des matériaux prédéfinis"""
        return list(self.materials.keys())


class LightingSystem:
    """Système éclairage professionnel"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.light_sources: Dict[str, LightSource] = {}
        self.environment_settings: Dict[str, Any] = {}
        self._initialize_lighting_presets()
    
    def _initialize_lighting_presets(self):
        """Initialisation des préréglages d'éclairage"""
        presets = {
            "studio_portrait": [
                LightSource(
                    light_id="key_light",
                    light_type=LightType.DIRECTIONAL,
                    position=(2.0, 3.0, 2.0),
                    rotation=(-45.0, 45.0, 0.0),
                    color=(1.0, 0.95, 0.9),
                    intensity=1.5
                ),
                LightSource(
                    light_id="fill_light",
                    light_type=LightType.AREA,
                    position=(-1.5, 2.0, 1.0),
                    color=(0.9, 0.95, 1.0),
                    intensity=0.6
                ),
                LightSource(
                    light_id="rim_light",
                    light_type=LightType.SPOT,
                    position=(0.0, 1.5, -2.0),
                    rotation=(0.0, 0.0, 180.0),
                    color=(1.0, 1.0, 1.0),
                    intensity=0.8,
                    cone_angle=30.0
                )
            ],
            "natural_outdoor": [
                LightSource(
                    light_id="sun_light",
                    light_type=LightType.DIRECTIONAL,
                    position=(0.0, 10.0, 5.0),
                    rotation=(-60.0, 30.0, 0.0),
                    color=(1.0, 0.98, 0.95),
                    intensity=2.0
                ),
                LightSource(
                    light_id="sky_light",
                    light_type=LightType.ENVIRONMENT,
                    color=(0.7, 0.8, 1.0),
                    intensity=0.4
                )
            ],
            "dramatic_evening": [
                LightSource(
                    light_id="warm_key",
                    light_type=LightType.SPOT,
                    position=(3.0, 2.0, 1.0),
                    rotation=(-30.0, 60.0, 0.0),
                    color=(1.0, 0.7, 0.4),
                    intensity=1.2,
                    cone_angle=45.0
                ),
                LightSource(
                    light_id="cool_fill",
                    light_type=LightType.AREA,
                    position=(-2.0, 1.0, -1.0),
                    color=(0.4, 0.6, 1.0),
                    intensity=0.3
                )
            ]
        }
        
        for preset_name, lights in presets.items():
            for light in lights:
                light_key = f"{preset_name}_{light.light_id}"
                self.light_sources[light_key] = light
    
    async def setup_lighting_preset(self, preset_name: str) -> List[LightSource]:
        """Configuration d'un préréglage d'éclairage"""
        try:
            preset_lights = [
                light for light_id, light in self.light_sources.items()
                if light_id.startswith(preset_name)
            ]
            
            if not preset_lights:
                raise ValueError(f"Préréglage {preset_name} non trouvé")
            
            return preset_lights
            
        except Exception as e:
            self.logger.error(f"Erreur configuration éclairage: {e}")
            raise
    
    async def create_custom_lighting(self, lighting_spec: Dict[str, Any]) -> List[LightSource]:
        """Création d'un éclairage personnalisé"""
        try:
            lights = []
            
            for light_data in lighting_spec.get('lights', []):
                light = LightSource(
                    light_id=light_data.get('id', str(uuid.uuid4())),
                    light_type=LightType(light_data.get('type', 'point')),
                    position=tuple(light_data.get('position', [0, 0, 0])),
                    rotation=tuple(light_data.get('rotation', [0, 0, 0])),
                    color=tuple(light_data.get('color', [1, 1, 1])),
                    intensity=light_data.get('intensity', 1.0),
                    range=light_data.get('range', 10.0),
                    cone_angle=light_data.get('cone_angle', 45.0),
                    shadows_enabled=light_data.get('shadows', True)
                )
                lights.append(light)
                self.light_sources[light.light_id] = light
            
            return lights
            
        except Exception as e:
            self.logger.error(f"Erreur création éclairage personnalisé: {e}")
            raise
    
    async def optimize_lighting_for_performance(self, target_fps: int) -> Dict[str, Any]:
        """Optimisation de l'éclairage pour la performance"""
        optimizations = {
            'shadow_quality_reduced': False,
            'lights_disabled': [],
            'lod_adjustments': {}
        }
        
        # Simulation d'optimisations basées sur le FPS cible
        if target_fps >= 60:
            optimizations['shadow_quality'] = 'high'
        elif target_fps >= 30:
            optimizations['shadow_quality'] = 'medium'
        else:
            optimizations['shadow_quality'] = 'low'
            optimizations['shadow_quality_reduced'] = True
        
        return optimizations


class PerformanceOptimizer:
    """Optimiseur performance rendu"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_metrics = PerformanceMetrics()
        self.target_fps = 60
        self.optimization_history: List[Dict[str, Any]] = []
    
    async def monitor_performance(self) -> PerformanceMetrics:
        """Surveillance de la performance en temps réel"""
        try:
            # Simulation de collecte de métriques
            metrics = PerformanceMetrics(
                frame_rate=random.uniform(45, 75),
                frame_time=1000 / random.uniform(45, 75),
                draw_calls=random.randint(100, 500),
                triangles_rendered=random.randint(50000, 200000),
                vertices_processed=random.randint(100000, 400000),
                texture_memory_mb=random.uniform(200, 800),
                vertex_memory_mb=random.uniform(50, 200),
                shader_switches=random.randint(20, 100),
                culled_objects=random.randint(10, 50),
                lod_switches=random.randint(5, 30),
                gpu_utilization=random.uniform(60, 90),
                cpu_utilization=random.uniform(40, 70)
            )
            
            self.current_metrics = metrics
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erreur surveillance performance: {e}")
            return PerformanceMetrics()
    
    async def optimize_for_target_fps(self, target_fps: int) -> Dict[str, Any]:
        """Optimisation automatique pour atteindre le FPS cible"""
        try:
            self.target_fps = target_fps
            current_fps = self.current_metrics.frame_rate
            
            optimizations = {
                'timestamp': datetime.now().isoformat(),
                'target_fps': target_fps,
                'current_fps': current_fps,
                'applied_optimizations': []
            }
            
            if current_fps < target_fps:
                # FPS trop bas, appliquer des optimisations
                fps_deficit = target_fps - current_fps
                
                if fps_deficit > 20:
                    # Optimisations agressives
                    optimizations['applied_optimizations'].extend([
                        'reduce_shadow_quality_to_low',
                        'disable_post_processing',
                        'force_lod2_minimum',
                        'reduce_texture_quality',
                        'disable_anti_aliasing'
                    ])
                elif fps_deficit > 10:
                    # Optimisations modérées
                    optimizations['applied_optimizations'].extend([
                        'reduce_shadow_quality_to_medium',
                        'enable_aggressive_culling',
                        'force_lod1_minimum',
                        'reduce_reflection_quality'
                    ])
                else:
                    # Optimisations légères
                    optimizations['applied_optimizations'].extend([
                        'enable_dynamic_lod',
                        'optimize_draw_calls',
                        'enable_instancing'
                    ])
            
            elif current_fps > target_fps * 1.2:
                # FPS trop élevé, on peut améliorer la qualité
                optimizations['applied_optimizations'].extend([
                    'increase_shadow_quality',
                    'enable_post_processing',
                    'increase_texture_quality',
                    'enable_anti_aliasing'
                ])
            
            self.optimization_history.append(optimizations)
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Erreur optimisation FPS: {e}")
            return {'error': str(e)}
    
    async def get_optimization_recommendations(self, render_settings: RenderSettings) -> List[str]:
        """Recommandations d'optimisation basées sur les paramètres actuels"""
        recommendations = []
        
        # Analyse des paramètres et métriques actuelles
        if self.current_metrics.frame_rate < 30:
            recommendations.extend([
                "Réduire la qualité des ombres",
                "Désactiver le motion blur",
                "Utiliser LOD plus agressif",
                "Réduire la résolution de rendu"
            ])
        
        if self.current_metrics.texture_memory_mb > 500:
            recommendations.append("Compresser les textures")
        
        if self.current_metrics.draw_calls > 300:
            recommendations.append("Optimiser les draw calls via batching")
        
        if render_settings.anti_aliasing == "msaa_8x":
            recommendations.append("Réduire l'anti-aliasing à MSAA 4x ou FXAA")
        
        return recommendations


class RenderingEngine:
    """Moteur rendu principal"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.material_manager = MaterialManager()
        self.lighting_system = LightingSystem()
        self.performance_optimizer = PerformanceOptimizer()
        self.render_settings = RenderSettings()
        self.active_materials: Dict[str, MaterialProperties] = {}
        self.active_lights: List[LightSource] = []
    
    async def initialize_renderer(self, settings: Optional[RenderSettings] = None) -> bool:
        """Initialisation du moteur de rendu"""
        try:
            if settings:
                self.render_settings = settings
            
            self.logger.info(f"Initialisation moteur rendu: {self.render_settings.pipeline.value}")
            
            # Initialisation des composants
            await self._initialize_graphics_context()
            await self._setup_default_lighting()
            await self._load_default_materials()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation renderer: {e}")
            return False
    
    async def _initialize_graphics_context(self) -> None:
        """Initialisation du contexte graphique"""
        # Simulation d'initialisation WebGL/OpenGL
        self.logger.info(f"Contexte graphique initialisé: {self.render_settings.resolution}")
    
    async def _setup_default_lighting(self) -> None:
        """Configuration de l'éclairage par défaut"""
        self.active_lights = await self.lighting_system.setup_lighting_preset("studio_portrait")
        self.logger.info(f"{len(self.active_lights)} sources lumineuses configurées")
    
    async def _load_default_materials(self) -> None:
        """Chargement des matériaux par défaut"""
        preset_materials = self.material_manager.get_material_presets()
        for material_id in preset_materials:
            self.active_materials[material_id] = self.material_manager.materials[material_id]
        
        self.logger.info(f"{len(self.active_materials)} matériaux chargés")
    
    async def render_avatar(self, avatar_data: Dict[str, Any], 
                          custom_settings: Optional[RenderSettings] = None) -> Dict[str, Any]:
        """Rendu complet d'un avatar"""
        try:
            settings = custom_settings or self.render_settings
            render_id = str(uuid.uuid4())
            
            self.logger.info(f"Début rendu avatar {render_id}")
            
            # Étape 1: Préparation des données
            mesh_data = await self._prepare_avatar_mesh(avatar_data)
            
            # Étape 2: Application des matériaux
            material_data = await self._apply_materials(avatar_data, settings.quality)
            
            # Étape 3: Configuration de l'éclairage
            lighting_data = await self._setup_scene_lighting(avatar_data)
            
            # Étape 4: Rendu principal
            render_result = await self._execute_render_pipeline(
                mesh_data, material_data, lighting_data, settings
            )
            
            # Étape 5: Post-traitement
            final_result = await self._apply_post_processing(render_result, settings)
            
            # Étape 6: Optimisation performance
            performance_metrics = await self.performance_optimizer.monitor_performance()
            
            return {
                'render_id': render_id,
                'success': True,
                'render_data': final_result,
                'performance_metrics': performance_metrics.__dict__,
                'render_time': datetime.now().isoformat(),
                'settings_used': settings.__dict__
            }
            
        except Exception as e:
            self.logger.error(f"Erreur rendu avatar: {e}")
            return {
                'render_id': str(uuid.uuid4()),
                'success': False,
                'error': str(e)
            }
    
    async def _prepare_avatar_mesh(self, avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Préparation des données de maillage"""
        # Simulation de préparation du mesh
        return {
            'vertices': random.randint(50000, 200000),
            'triangles': random.randint(25000, 100000),
            'uv_coordinates': True,
            'normals': True,
            'tangents': True,
            'vertex_colors': False
        }
    
    async def _apply_materials(self, avatar_data: Dict[str, Any], 
                             quality: RenderQuality) -> Dict[str, Any]:
        """Application des matériaux"""
        applied_materials = {}
        
        # Matériaux par défaut pour un avatar
        material_mappings = {
            'skin': 'realistic_skin',
            'hair': 'natural_hair',
            'clothing': 'cotton_fabric',
            'accessories': 'polished_metal'
        }
        
        for part, material_id in material_mappings.items():
            if material_id in self.active_materials:
                optimized_material = await self.material_manager.optimize_material_for_quality(
                    material_id, quality
                )
                applied_materials[part] = optimized_material.__dict__
        
        return applied_materials
    
    async def _setup_scene_lighting(self, avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Configuration de l'éclairage de scène"""
        return {
            'active_lights': [light.__dict__ for light in self.active_lights],
            'ambient_light': {'color': (0.2, 0.2, 0.25), 'intensity': 0.3},
            'environment_map': 'studio_environment.hdr',
            'shadows_enabled': True
        }
    
    async def _execute_render_pipeline(self, mesh_data: Dict[str, Any],
                                     material_data: Dict[str, Any],
                                     lighting_data: Dict[str, Any],
                                     settings: RenderSettings) -> Dict[str, Any]:
        """Exécution du pipeline de rendu"""
        # Simulation du rendu
        render_time = random.uniform(16.67, 33.33)  # 30-60 FPS
        
        return {
            'frame_buffer': f"rendered_frame_{uuid.uuid4().hex[:8]}.jpg",
            'depth_buffer': f"depth_{uuid.uuid4().hex[:8]}.exr",
            'normal_buffer': f"normals_{uuid.uuid4().hex[:8]}.exr",
            'render_time_ms': render_time,
            'draw_calls': random.randint(50, 200),
            'triangles_rendered': mesh_data['triangles']
        }
    
    async def _apply_post_processing(self, render_result: Dict[str, Any],
                                   settings: RenderSettings) -> Dict[str, Any]:
        """Application du post-traitement"""
        post_effects = []
        
        if settings.bloom:
            post_effects.append('bloom')
        if settings.tone_mapping:
            post_effects.append(f'tone_mapping_{settings.tone_mapping}')
        if settings.anti_aliasing:
            post_effects.append(f'anti_aliasing_{settings.anti_aliasing}')
        
        render_result['post_effects_applied'] = post_effects
        render_result['final_output'] = f"final_{uuid.uuid4().hex[:8]}.jpg"
        
        return render_result
    
    async def optimize_render_settings(self, target_performance: Dict[str, Any]) -> RenderSettings:
        """Optimisation automatique des paramètres de rendu"""
        try:
            target_fps = target_performance.get('fps', 60)
            target_quality = target_performance.get('quality', 'high')
            
            optimizations = await self.performance_optimizer.optimize_for_target_fps(target_fps)
            
            # Application des optimisations aux paramètres
            optimized_settings = RenderSettings(**self.render_settings.__dict__)
            
            for optimization in optimizations.get('applied_optimizations', []):
                if 'shadow_quality' in optimization:
                    if 'low' in optimization:
                        optimized_settings.shadow_quality = 'low'
                    elif 'medium' in optimization:
                        optimized_settings.shadow_quality = 'medium'
                
                elif 'anti_aliasing' in optimization:
                    if 'disable' in optimization:
                        optimized_settings.anti_aliasing = 'none'
                
                elif 'post_processing' in optimization:
                    if 'disable' in optimization:
                        optimized_settings.bloom = False
                        optimized_settings.motion_blur = False
            
            return optimized_settings
            
        except Exception as e:
            self.logger.error(f"Erreur optimisation paramètres: {e}")
            return self.render_settings
    
    def get_rendering_capabilities(self) -> Dict[str, Any]:
        """Capacités du moteur de rendu"""
        return {
            'supported_pipelines': [pipeline.value for pipeline in RenderingPipeline],
            'supported_lighting_models': [model.value for model in LightingModel],
            'supported_qualities': [quality.value for quality in RenderQuality],
            'max_lights': 8,
            'max_materials': 16,
            'lod_levels': [lod.value for lod in LODLevel],
            'supported_formats': ['jpg', 'png', 'exr', 'hdr'],
            'real_time_capable': True,
            'pbr_support': True,
            'subsurface_scattering': True,
            'motion_blur': True,
            'depth_of_field': True
        }


# Import pour éviter les erreurs de références circulaires
import random

__all__ = [
    'RenderingEngine',
    'MaterialManager',
    'LightingSystem', 
    'PerformanceOptimizer',
    'RenderingPipeline',
    'RenderQuality',
    'RenderSettings',
    'MaterialProperties',
    'MaterialType',
    'LightSource',
    'LightType',
    'LightingModel',
    'PerformanceMetrics',
    'LODLevel'
]