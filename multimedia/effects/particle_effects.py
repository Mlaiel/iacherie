"""Particle Effects Engine
Advanced particle systems for dynamic video content and visual effects.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
import math
import random
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class ParticleConfig:
    """Configuration for individual particles."""
    position: Tuple[float, float] = (0.0, 0.0)
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0)
    size: float = 3.0
    color: Tuple[int, int, int] = (255, 255, 255)
    alpha: float = 1.0
    life_time: float = 1.0
    fade_rate: float = 0.01

@dataclass
class ParticleSystemConfig:
    """Configuration for particle systems."""
    particle_count: int = 100
    spawn_rate: float = 10.0  # particles per second
    gravity: Tuple[float, float] = (0.0, 98.0)  # pixels per second^2
    wind: Tuple[float, float] = (0.0, 0.0)
    size_range: Tuple[float, float] = (1.0, 5.0)
    speed_range: Tuple[float, float] = (10.0, 50.0)
    lifetime_range: Tuple[float, float] = (1.0, 3.0)
    color_palette: List[Tuple[int, int, int]] = field(default_factory=lambda: [(255, 255, 255)])
    blend_mode: str = "alpha"  # alpha, additive, multiply
    particle_shape: str = "circle"  # circle, square, star, custom

class Particle:
    """Individual particle with physics simulation."""
    
    def __init__(self, config: ParticleConfig):
        self.x, self.y = config.position
        self.vx, self.vy = config.velocity
        self.ax, self.ay = config.acceleration
        self.size = config.size
        self.color = config.color
        self.alpha = config.alpha
        self.max_lifetime = config.life_time
        self.lifetime = config.life_time
        self.fade_rate = config.fade_rate
        self.active = True
    
    def update(self, dt: float, gravity: Tuple[float, float], wind: Tuple[float, float]):
        """Update particle physics."""
        if not self.active:
            return
        
        # Apply forces
        gx, gy = gravity
        wx, wy = wind
        
        self.ax = wx * 0.1  # Wind has less effect
        self.ay = gy
        
        # Update velocity
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Update lifetime and alpha
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
        else:
            # Fade out over time
            self.alpha = max(0.0, self.lifetime / self.max_lifetime)
    
    def render(self, frame: np.ndarray):
        """Render particle to frame."""
        if not self.active or self.alpha <= 0:
            return
        
        h, w = frame.shape[:2]
        x, y = int(self.x), int(self.y)
        
        # Check bounds
        if x < 0 or x >= w or y < 0 or y >= h:
            return
        
        # Render based on size and alpha
        radius = max(1, int(self.size))
        color = self.color
        alpha = self.alpha
        
        # Create particle overlay
        overlay = frame.copy()
        cv2.circle(overlay, (x, y), radius, color, -1)
        
        # Blend with alpha
        frame[max(0, y-radius):min(h, y+radius+1), max(0, x-radius):min(w, x+radius+1)] = \
            cv2.addWeighted(
                frame[max(0, y-radius):min(h, y+radius+1), max(0, x-radius):min(w, x+radius+1)],
                1 - alpha,
                overlay[max(0, y-radius):min(h, y+radius+1), max(0, x-radius):min(w, x+radius+1)],
                alpha,
                0
            )

class ParticleSystem:
    """Complete particle system with emitters and physics."""
    
    def __init__(self, config: ParticleSystemConfig):
        self.config = config
        self.particles: List[Particle] = []
        self.time_since_spawn = 0.0
        self.emitter_position = (0, 0)
        
    def set_emitter_position(self, position: Tuple[float, float]):
        """Set the position where new particles spawn."""
        self.emitter_position = position
    
    def spawn_particle(self):
        """Spawn a new particle at the emitter position."""
        if len(self.particles) >= self.config.particle_count:
            return
        
        # Random properties within ranges
        size = random.uniform(*self.config.size_range)
        speed = random.uniform(*self.config.speed_range)
        lifetime = random.uniform(*self.config.lifetime_range)
        color = random.choice(self.config.color_palette)
        
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Add some variation to spawn position
        spawn_x = self.emitter_position[0] + random.uniform(-10, 10)
        spawn_y = self.emitter_position[1] + random.uniform(-10, 10)
        
        particle_config = ParticleConfig(
            position=(spawn_x, spawn_y),
            velocity=(vx, vy),
            size=size,
            color=color,
            life_time=lifetime
        )
        
        particle = Particle(particle_config)
        self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles in the system."""
        # Update existing particles
        active_particles = []
        for particle in self.particles:
            particle.update(dt, self.config.gravity, self.config.wind)
            if particle.active:
                active_particles.append(particle)
        
        self.particles = active_particles
        
        # Spawn new particles
        self.time_since_spawn += dt
        spawn_interval = 1.0 / self.config.spawn_rate
        
        while self.time_since_spawn >= spawn_interval:
            self.spawn_particle()
            self.time_since_spawn -= spawn_interval
    
    def render(self, frame: np.ndarray):
        """Render all particles to the frame."""
        for particle in self.particles:
            particle.render(frame)

class EffectPresets:
    """Predefined particle effect presets."""
    
    @staticmethod
    def snow_effect() -> ParticleSystemConfig:
        """Snow falling effect."""
        return ParticleSystemConfig(
            particle_count=200,
            spawn_rate=20.0,
            gravity=(0.0, 30.0),
            wind=(-5.0, 0.0),
            size_range=(2.0, 6.0),
            speed_range=(5.0, 15.0),
            lifetime_range=(3.0, 6.0),
            color_palette=[(255, 255, 255), (240, 240, 255), (220, 220, 255)]
        )
    
    @staticmethod
    def rain_effect() -> ParticleSystemConfig:
        """Rain drops effect."""
        return ParticleSystemConfig(
            particle_count=300,
            spawn_rate=50.0,
            gravity=(0.0, 200.0),
            wind=(-20.0, 0.0),
            size_range=(1.0, 3.0),
            speed_range=(100.0, 150.0),
            lifetime_range=(1.0, 2.0),
            color_palette=[(100, 150, 255), (120, 160, 255), (80, 140, 255)]
        )
    
    @staticmethod
    def fire_effect() -> ParticleSystemConfig:
        """Fire particles effect."""
        return ParticleSystemConfig(
            particle_count=150,
            spawn_rate=30.0,
            gravity=(0.0, -50.0),  # Upward
            wind=(5.0, 0.0),
            size_range=(3.0, 8.0),
            speed_range=(20.0, 40.0),
            lifetime_range=(0.8, 2.0),
            color_palette=[
                (255, 100, 0),    # Orange
                (255, 50, 0),     # Red-orange
                (255, 200, 0),    # Yellow
                (255, 0, 0),      # Red
                (200, 50, 0)      # Dark red
            ]
        )
    
    @staticmethod
    def sparkles_effect() -> ParticleSystemConfig:
        """Magical sparkles effect."""
        return ParticleSystemConfig(
            particle_count=100,
            spawn_rate=15.0,
            gravity=(0.0, 0.0),
            wind=(0.0, 0.0),
            size_range=(1.0, 4.0),
            speed_range=(10.0, 30.0),
            lifetime_range=(2.0, 4.0),
            color_palette=[
                (255, 255, 100),  # Bright yellow
                (255, 100, 255),  # Magenta
                (100, 255, 255),  # Cyan
                (255, 255, 255),  # White
                (200, 200, 255)   # Light blue
            ]
        )
    
    @staticmethod
    def smoke_effect() -> ParticleSystemConfig:
        """Smoke particles effect."""
        return ParticleSystemConfig(
            particle_count=80,
            spawn_rate=10.0,
            gravity=(0.0, -20.0),  # Slight upward
            wind=(10.0, 0.0),
            size_range=(5.0, 15.0),
            speed_range=(5.0, 20.0),
            lifetime_range=(3.0, 6.0),
            color_palette=[
                (100, 100, 100),  # Gray
                (120, 120, 120),  # Light gray
                (80, 80, 80),     # Dark gray
                (60, 60, 60),     # Darker gray
                (140, 140, 140)   # Very light gray
            ]
        )
    
    @staticmethod
    def leaves_effect() -> ParticleSystemConfig:
        """Falling leaves effect."""
        return ParticleSystemConfig(
            particle_count=50,
            spawn_rate=5.0,
            gravity=(0.0, 40.0),
            wind=(15.0, 0.0),
            size_range=(4.0, 10.0),
            speed_range=(10.0, 25.0),
            lifetime_range=(4.0, 8.0),
            color_palette=[
                (50, 150, 50),    # Green
                (200, 150, 50),   # Yellow-green
                (200, 100, 50),   # Orange
                (150, 50, 50),    # Red-brown
                (100, 50, 0)      # Brown
            ]
        )

class ParticleEffectsEngine:
    """Enterprise particle effects engine for dynamic visual content."""
    
    def __init__(self):
        self.particle_systems: List[ParticleSystem] = []
        
    async def add_particles(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        particle_type: str = "snow",
        density: float = 0.5,
        custom_config: Optional[ParticleSystemConfig] = None
    ) -> Dict[str, any]:
        """Add particle effects to video."""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Adding {particle_type} particles: {input_path}")
            
            # Get particle system configuration
            if custom_config:
                system_config = custom_config
            else:
                preset_configs = {
                    "snow": EffectPresets.snow_effect(),
                    "rain": EffectPresets.rain_effect(),
                    "fire": EffectPresets.fire_effect(),
                    "sparkles": EffectPresets.sparkles_effect(),
                    "smoke": EffectPresets.smoke_effect(),
                    "leaves": EffectPresets.leaves_effect()
                }
                
                if particle_type not in preset_configs:
                    logger.warning(f"Unknown particle type: {particle_type}, using snow")
                    particle_type = "snow"
                
                system_config = preset_configs[particle_type]
            
            # Adjust density
            system_config.particle_count = int(system_config.particle_count * density)
            system_config.spawn_rate *= density
            
            # Open video
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Create particle system
            particle_system = ParticleSystem(system_config)
            
            # Set emitter position (top of screen for most effects)
            if particle_type in ["snow", "rain", "leaves"]:
                emitter_y = -20  # Above screen
            elif particle_type == "fire":
                emitter_y = height + 20  # Below screen (fire goes up)
            else:
                emitter_y = height // 2  # Middle
            
            particle_system.set_emitter_position((width // 2, emitter_y))
            
            frame_count = 0
            dt = 1.0 / fps  # Time delta per frame
            
            logger.info(f"Processing {total_frames} frames with {particle_type} particles")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Update particle system
                particle_system.update(dt)
                
                # Render particles on frame
                particle_system.render(frame)
                
                # Write frame
                out.write(frame)
                frame_count += 1
                
                # Progress logging
                if frame_count % 100 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
            
            cap.release()
            out.release()
            
            logger.info("Particle effects added successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "particle_type": particle_type,
                "density": density,
                "frames_processed": frame_count,
                "particles_spawned": len(particle_system.particles),
                "system_config": {
                    "particle_count": system_config.particle_count,
                    "spawn_rate": system_config.spawn_rate,
                    "gravity": system_config.gravity,
                    "wind": system_config.wind
                }
            }
            
        except Exception as e:
            logger.error(f"Particle effects failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "particle_type": particle_type
            }
    
    async def create_particle_overlay(
        self,
        width: int,
        height: int,
        duration: float,
        particle_type: str = "sparkles",
        density: float = 0.5,
        fps: int = 30
    ) -> np.ndarray:
        """Create a particle effect overlay as numpy array."""
        try:
            logger.info(f"Creating {particle_type} overlay: {width}x{height}, {duration}s")
            
            # Get configuration
            preset_configs = {
                "snow": EffectPresets.snow_effect(),
                "rain": EffectPresets.rain_effect(),
                "fire": EffectPresets.fire_effect(),
                "sparkles": EffectPresets.sparkles_effect(),
                "smoke": EffectPresets.smoke_effect(),
                "leaves": EffectPresets.leaves_effect()
            }
            
            if particle_type not in preset_configs:
                particle_type = "sparkles"
            
            system_config = preset_configs[particle_type]
            system_config.particle_count = int(system_config.particle_count * density)
            system_config.spawn_rate *= density
            
            # Create particle system
            particle_system = ParticleSystem(system_config)
            particle_system.set_emitter_position((width // 2, -20))
            
            # Generate frames
            total_frames = int(fps * duration)
            frames = []
            dt = 1.0 / fps
            
            for frame_idx in range(total_frames):
                # Create transparent frame
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Update and render particles
                particle_system.update(dt)
                particle_system.render(frame)
                
                frames.append(frame)
            
            return np.array(frames)
            
        except Exception as e:
            logger.error(f"Particle overlay creation failed: {str(e)}")
            return np.zeros((1, height, width, 3), dtype=np.uint8)
    
    async def multi_particle_effect(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        effects: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """Apply multiple particle effects simultaneously."""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying multi-particle effects: {input_path}")
            
            # Open video
            cap = cv2.VideoCapture(str(input_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {input_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Create multiple particle systems
            particle_systems = []
            for effect in effects:
                effect_type = effect.get("type", "snow")
                density = effect.get("density", 0.5)
                position = effect.get("position", (width // 2, -20))
                
                # Get preset config
                preset_configs = {
                    "snow": EffectPresets.snow_effect(),
                    "rain": EffectPresets.rain_effect(),
                    "fire": EffectPresets.fire_effect(),
                    "sparkles": EffectPresets.sparkles_effect(),
                    "smoke": EffectPresets.smoke_effect(),
                    "leaves": EffectPresets.leaves_effect()
                }
                
                config = preset_configs.get(effect_type, EffectPresets.sparkles_effect())
                config.particle_count = int(config.particle_count * density)
                config.spawn_rate *= density
                
                system = ParticleSystem(config)
                system.set_emitter_position(position)
                particle_systems.append(system)
            
            frame_count = 0
            dt = 1.0 / fps
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Update and render all particle systems
                for system in particle_systems:
                    system.update(dt)
                    system.render(frame)
                
                out.write(frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            logger.info("Multi-particle effects applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "effects_applied": len(effects),
                "frames_processed": frame_count
            }
            
        except Exception as e:
            logger.error(f"Multi-particle effects failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path)
            }