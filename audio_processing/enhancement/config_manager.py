"""
Audio Enhancement Configuration Manager
======================================

Professional configuration management system for audio enhancement parameters,
presets, and adaptive processing settings. Provides preset management,
parameter validation, and adaptive configuration for different content types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""

import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import logging
import yaml
from copy import deepcopy

from .processor import EnhancementParameters, ContentType
from .quality_analyzer import QualityLevel


class PresetCategory(Enum):
    """Enhancement preset categories"""
    MUSIC_PRODUCTION = "music_production"
    PODCAST_BROADCAST = "podcast_broadcast" 
    VOICE_RECORDING = "voice_recording"
    LIVE_STREAMING = "live_streaming"
    AUDIOBOOK_NARRATION = "audiobook_narration"
    SOUND_DESIGN = "sound_design"
    RESTORATION = "restoration"
    MASTERING = "mastering"
    CUSTOM = "custom"


@dataclass
class EnhancementPreset:
    """Professional enhancement preset configuration"""
    name: str
    category: PresetCategory
    description: str
    parameters: EnhancementParameters
    target_quality: QualityLevel = QualityLevel.GOOD
    content_types: List[ContentType] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    created_timestamp: float = field(default_factory=lambda: __import__('time').time())
    modified_timestamp: float = field(default_factory=lambda: __import__('time').time())
    version: str = "1.0.0"
    author: str = "System"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary"""
        data = asdict(self)
        data['category'] = self.category.value
        data['target_quality'] = self.target_quality.value
        data['content_types'] = [ct.value for ct in self.content_types]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancementPreset':
        """Create preset from dictionary"""
        # Handle parameters
        params_data = data.get('parameters', {})
        parameters = EnhancementParameters(**params_data)
        
        # Handle enums
        category = PresetCategory(data.get('category', PresetCategory.CUSTOM.value))
        target_quality = QualityLevel(data.get('target_quality', QualityLevel.GOOD.value))
        content_types = [ContentType(ct) for ct in data.get('content_types', [])]
        
        return cls(
            name=data.get('name', 'Unnamed Preset'),
            category=category,
            description=data.get('description', ''),
            parameters=parameters,
            target_quality=target_quality,
            content_types=content_types,
            use_cases=data.get('use_cases', []),
            created_timestamp=data.get('created_timestamp', 0),
            modified_timestamp=data.get('modified_timestamp', 0),
            version=data.get('version', '1.0.0'),
            author=data.get('author', 'System')
        )


@dataclass
class AdaptiveConfig:
    """Adaptive enhancement configuration"""
    enable_content_detection: bool = True
    enable_quality_monitoring: bool = True
    enable_performance_adaptation: bool = True
    
    # Content detection thresholds
    speech_detection_threshold: float = 0.7
    music_detection_threshold: float = 0.6
    noise_detection_threshold: float = 0.8
    
    # Quality adaptation
    target_quality_score: float = 75.0
    quality_adaptation_sensitivity: float = 0.5
    
    # Performance adaptation
    max_cpu_usage_percent: float = 80.0
    latency_target_ms: float = 50.0
    
    # Learning parameters
    enable_learning: bool = False
    learning_rate: float = 0.1
    adaptation_window: int = 100


class EnhancementConfigManager:
    """
    Professional Audio Enhancement Configuration Manager
    
    Comprehensive configuration management system for audio enhancement,
    providing preset management, parameter validation, and adaptive processing.
    """
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """Initialize configuration manager"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration directory
        if config_dir is None:
            config_dir = Path.cwd() / "config" / "audio_enhancement"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.presets_file = self.config_dir / "presets.json"
        self.adaptive_config_file = self.config_dir / "adaptive_config.yaml"
        
        # Loaded configurations
        self.presets: Dict[str, EnhancementPreset] = {}
        self.adaptive_config = AdaptiveConfig()
        
        # Load configurations
        self._load_default_presets()
        self.load_presets()
        self.load_adaptive_config()
        
        self.logger.info(f"Configuration manager initialized with {len(self.presets)} presets")
    
    def _load_default_presets(self):
        """Load default enhancement presets"""
        default_presets = self._create_default_presets()
        for preset in default_presets:
            self.presets[preset.name] = preset
    
    def _create_default_presets(self) -> List[EnhancementPreset]:
        """Create default enhancement presets"""
        presets = []
        
        # Music Production Preset
        music_params = EnhancementParameters(
            noise_reduction_strength=0.3,
            spectral_enhancement_gain=0.4,
            dynamic_range_target=0.8,
            stereo_width=1.2,
            harmonic_emphasis=0.4,
            vocal_clarity=0.2,
            mastering_loudness_lufs=-16.0,
            restoration_strength=0.2,
            preserve_original_character=True,
            adaptive_processing=True,
            multiband_processing=True,
            high_quality_mode=True
        )
        
        music_preset = EnhancementPreset(
            name="Music Production",
            category=PresetCategory.MUSIC_PRODUCTION,
            description="Professional music production enhancement with balanced dynamics and clarity",
            parameters=music_params,
            target_quality=QualityLevel.EXCELLENT,
            content_types=[ContentType.MUSIC, ContentType.INSTRUMENT],
            use_cases=["Studio recording", "Music mixing", "Track mastering", "Audio production"]
        )
        presets.append(music_preset)
        
        # Podcast Enhancement Preset
        podcast_params = EnhancementParameters(
            noise_reduction_strength=0.7,
            spectral_enhancement_gain=0.3,
            dynamic_range_target=0.9,
            stereo_width=1.0,
            harmonic_emphasis=0.2,
            vocal_clarity=0.8,
            mastering_loudness_lufs=-18.0,
            restoration_strength=0.5,
            preserve_original_character=True,
            adaptive_processing=True,
            multiband_processing=True,
            high_quality_mode=True
        )
        
        podcast_preset = EnhancementPreset(
            name="Podcast Enhancement",
            category=PresetCategory.PODCAST_BROADCAST,
            description="Optimized for speech clarity and noise reduction in podcast content",
            parameters=podcast_params,
            target_quality=QualityLevel.GOOD,
            content_types=[ContentType.SPEECH, ContentType.PODCAST],
            use_cases=["Podcast recording", "Interview enhancement", "Voice broadcast", "Speech clarity"]
        )
        presets.append(podcast_preset)
        
        # Live Streaming Preset
        streaming_params = EnhancementParameters(
            noise_reduction_strength=0.6,
            spectral_enhancement_gain=0.3,
            dynamic_range_target=0.85,
            stereo_width=1.1,
            harmonic_emphasis=0.3,
            vocal_clarity=0.6,
            mastering_loudness_lufs=-20.0,
            restoration_strength=0.3,
            preserve_original_character=True,
            adaptive_processing=True,
            multiband_processing=False,  # Reduced for real-time
            high_quality_mode=False
        )
        
        streaming_preset = EnhancementPreset(
            name="Live Streaming",
            category=PresetCategory.LIVE_STREAMING,
            description="Real-time enhancement optimized for live streaming and broadcasting",
            parameters=streaming_params,
            target_quality=QualityLevel.GOOD,
            content_types=[ContentType.SPEECH, ContentType.MUSIC, ContentType.GENERAL],
            use_cases=["Live streaming", "Real-time broadcast", "Gaming audio", "Webinar hosting"]
        )
        presets.append(streaming_preset)
        
        # Voice Recording Preset
        voice_params = EnhancementParameters(
            noise_reduction_strength=0.5,
            spectral_enhancement_gain=0.2,
            dynamic_range_target=0.75,
            stereo_width=1.0,
            harmonic_emphasis=0.1,
            vocal_clarity=0.9,
            mastering_loudness_lufs=-20.0,
            restoration_strength=0.4,
            preserve_original_character=True,
            adaptive_processing=True,
            multiband_processing=True,
            high_quality_mode=True
        )
        
        voice_preset = EnhancementPreset(
            name="Voice Recording",
            category=PresetCategory.VOICE_RECORDING,
            description="Professional voice recording enhancement for narration and voiceovers",
            parameters=voice_params,
            target_quality=QualityLevel.EXCELLENT,
            content_types=[ContentType.SPEECH, ContentType.VOICEOVER, ContentType.AUDIOBOOK],
            use_cases=["Voice recording", "Narration", "Voiceover work", "Audio book production"]
        )
        presets.append(voice_preset)
        
        # Audio Restoration Preset
        restoration_params = EnhancementParameters(
            noise_reduction_strength=0.8,
            spectral_enhancement_gain=0.2,
            dynamic_range_target=0.7,
            stereo_width=1.0,
            harmonic_emphasis=0.1,
            vocal_clarity=0.5,
            mastering_loudness_lufs=-18.0,
            restoration_strength=0.9,
            preserve_original_character=True,
            adaptive_processing=True,
            multiband_processing=True,
            high_quality_mode=True
        )
        
        restoration_preset = EnhancementPreset(
            name="Audio Restoration",
            category=PresetCategory.RESTORATION,
            description="Specialized for restoring and cleaning up degraded audio content",
            parameters=restoration_params,
            target_quality=QualityLevel.GOOD,
            content_types=[ContentType.GENERAL],
            use_cases=["Audio restoration", "Noise removal", "Archive digitization", "Quality improvement"]
        )
        presets.append(restoration_preset)
        
        # Mastering Preset
        mastering_params = EnhancementParameters(
            noise_reduction_strength=0.2,
            spectral_enhancement_gain=0.5,
            dynamic_range_target=0.75,
            stereo_width=1.15,
            harmonic_emphasis=0.3,
            vocal_clarity=0.3,
            mastering_loudness_lufs=-14.0,
            restoration_strength=0.1,
            preserve_original_character=False,
            adaptive_processing=False,
            multiband_processing=True,
            high_quality_mode=True
        )
        
        mastering_preset = EnhancementPreset(
            name="Audio Mastering",
            category=PresetCategory.MASTERING,
            description="Professional audio mastering with dynamics control and spectral shaping",
            parameters=mastering_params,
            target_quality=QualityLevel.EXCELLENT,
            content_types=[ContentType.MUSIC],
            use_cases=["Audio mastering", "Final mix processing", "Commercial release preparation"]
        )
        presets.append(mastering_preset)
        
        return presets
    
    def get_preset(self, name: str) -> Optional[EnhancementPreset]:
        """Get preset by name"""



        return self.presets.get(name)
    
    def list_presets(self, category: Optional[PresetCategory] = None) -> List[str]:
        """List available presets, optionally filtered by category"""
        if category is None:
            return list(self.presets.keys())
        
        return [name for name, preset in self.presets.items() 
                if preset.category == category]
    
    def add_preset(self, preset: EnhancementPreset, overwrite: bool = False):
        """Add new preset"""
        if preset.name in self.presets and not overwrite:
            raise ValueError(f"Preset '{preset.name}' already exists. Use overwrite=True to replace.")
        
        preset.modified_timestamp = __import__('time').time()
        self.presets[preset.name] = preset
        
        self.logger.info(f"Added preset: {preset.name}")
    
    def update_preset(self, name: str, **kwargs):
        """Update existing preset parameters"""
        if name not in self.presets:
            raise ValueError(f"Preset '{name}' not found")
        
        preset = self.presets[name]
        preset.modified_timestamp = __import__('time').time()
        
        # Update parameters if provided
        if 'parameters' in kwargs:
            preset.parameters = kwargs['parameters']
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(preset, key) and key != 'parameters':
                setattr(preset, key, value)
        
        self.logger.info(f"Updated preset: {name}")
    
    def delete_preset(self, name: str):
        """Delete preset"""
        if name not in self.presets:
            raise ValueError(f"Preset '{name}' not found")
        
        del self.presets[name]
        self.logger.info(f"Deleted preset: {name}")
    
    def duplicate_preset(self, source_name: str, new_name: str) -> EnhancementPreset:
        """Duplicate existing preset with new name"""
        if source_name not in self.presets:
            raise ValueError(f"Source preset '{source_name}' not found")
        
        if new_name in self.presets:
            raise ValueError(f"Preset '{new_name}' already exists")
        
        source_preset = self.presets[source_name]
        new_preset = EnhancementPreset(
            name=new_name,
            category=source_preset.category,
            description=f"Copy of {source_preset.description}",
            parameters=EnhancementParameters(**asdict(source_preset.parameters)),
            target_quality=source_preset.target_quality,
            content_types=source_preset.content_types.copy(),
            use_cases=source_preset.use_cases.copy(),
            version="1.0.0",
            author="User"
        )
        
        self.presets[new_name] = new_preset
        self.logger.info(f"Duplicated preset '{source_name}' as '{new_name}'")
        
        return new_preset
    
    def get_preset_for_content(self, content_type: ContentType, 
                              quality_target: Optional[QualityLevel] = None) -> Optional[EnhancementPreset]:
        """Get best preset for specific content type and quality target"""
        matching_presets = []
        
        for preset in self.presets.values():
            # Check content type match
            if content_type in preset.content_types or ContentType.GENERAL in preset.content_types:
                score = 1.0
                
                # Boost score for exact content type match
                if content_type in preset.content_types:
                    score += 0.5
                
                # Consider quality target
                if quality_target is not None:
                    quality_diff = abs(preset.target_quality.value - quality_target.value)
                    score += max(0, 1.0 - quality_diff * 0.2)
                
                matching_presets.append((preset, score))
        
        if not matching_presets:
            # Fallback to general preset
            for preset in self.presets.values():
                if preset.category == PresetCategory.CUSTOM:
                    return preset
            return None
        
        # Return highest scoring preset
        best_preset = max(matching_presets, key=lambda x: x[1])[0]
        self.logger.debug(f"Selected preset '{best_preset.name}' for {content_type.value}")
        
        return best_preset
    
    def create_adaptive_parameters(self, 
                                  base_preset: EnhancementPreset,
                                  content_analysis: Dict[str, Any],
                                  quality_metrics: Optional[Dict[str, float]] = None) -> EnhancementParameters:
        """Create adaptive parameters based on content analysis and quality metrics"""
        adapted_params = EnhancementParameters(**asdict(base_preset.parameters))
        
        if not self.adaptive_config.enable_content_detection:
            return adapted_params
        
        # Adapt based on content analysis
        if 'noise_level' in content_analysis:
            noise_level = content_analysis['noise_level']
            # Increase noise reduction for noisy content
            adapted_params.noise_reduction_strength = min(1.0, 
                adapted_params.noise_reduction_strength + noise_level * 0.3)
        
        if 'dynamic_range' in content_analysis:
            dynamic_range = content_analysis['dynamic_range']
            # Adjust compression based on existing dynamic range
            if dynamic_range < 6:  # Heavily compressed
                adapted_params.dynamic_range_target = max(0.5, dynamic_range / 12)
            elif dynamic_range > 20:  # Very dynamic
                adapted_params.dynamic_range_target = min(0.9, 0.6 + (dynamic_range - 20) / 40)
        
        if 'spectral_content' in content_analysis:
            spectral_info = content_analysis['spectral_content']
            # Adapt spectral enhancement
            if spectral_info.get('high_frequency_energy', 0) < 0.3:
                adapted_params.spectral_enhancement_gain *= 1.3
            elif spectral_info.get('high_frequency_energy', 0) > 0.8:
                adapted_params.spectral_enhancement_gain *= 0.7
        
        if 'speech_probability' in content_analysis:
            speech_prob = content_analysis['speech_probability']
            if speech_prob > self.adaptive_config.speech_detection_threshold:
                # Optimize for speech
                adapted_params.vocal_clarity = min(1.0, adapted_params.vocal_clarity + 0.3)
                adapted_params.stereo_width = 1.0  # Keep speech mono-focused
        
        # Adapt based on quality metrics
        if quality_metrics and self.adaptive_config.enable_quality_monitoring:
            current_quality = quality_metrics.get('overall_quality_score', 50.0)
            target_quality = self.adaptive_config.target_quality_score
            
            quality_diff = target_quality - current_quality
            adaptation_factor = quality_diff * self.adaptive_config.quality_adaptation_sensitivity / 100
            
            if quality_diff > 10:  # Significant improvement needed
                adapted_params.noise_reduction_strength = min(1.0, 
                    adapted_params.noise_reduction_strength + adaptation_factor)
                adapted_params.spectral_enhancement_gain = min(1.0,
                    adapted_params.spectral_enhancement_gain + adaptation_factor)
        
        self.logger.debug("Created adaptive parameters based on content analysis")
        return adapted_params
    
    def save_presets(self):
        """Save presets to file"""



        try:
            presets_data = {
                name: preset.to_dict() 
                for name, preset in self.presets.items()
            }
            
            with open(self.presets_file, 'w') as f:
                json.dump(presets_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved {len(self.presets)} presets to {self.presets_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save presets: {str(e)}")
            raise
    
    def load_presets(self):
        """Load presets from file"""



        try:
            if not self.presets_file.exists():
                self.logger.info("No presets file found, using defaults only")
                return
            
            with open(self.presets_file, 'r') as f:
                presets_data = json.load(f)
            
            loaded_presets = {}
            for name, preset_dict in presets_data.items():
                try:
                    preset = EnhancementPreset.from_dict(preset_dict)
                    loaded_presets[name] = preset
                except Exception as e:
                    self.logger.warning(f"Failed to load preset '{name}': {str(e)}")
            
            # Merge with existing presets (loaded presets take precedence)
            self.presets.update(loaded_presets)
            
            self.logger.info(f"Loaded {len(loaded_presets)} presets from file")
            
        except Exception as e:
            self.logger.error(f"Failed to load presets: {str(e)}")
    
    def save_adaptive_config(self):
        """Save adaptive configuration to file"""



        try:
            config_data = asdict(self.adaptive_config)
            
            with open(self.adaptive_config_file, 'w') as f:
                yaml.dump(config_data, f, indent=2)
            
            self.logger.info(f"Saved adaptive config to {self.adaptive_config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save adaptive config: {str(e)}")
            raise
    
    def load_adaptive_config(self):
        """Load adaptive configuration from file"""



        try:
            if not self.adaptive_config_file.exists():
                self.logger.info("No adaptive config file found, using defaults")
                return
            
            with open(self.adaptive_config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if config_data:
                self.adaptive_config = AdaptiveConfig(**config_data)
                self.logger.info("Loaded adaptive configuration from file")
            
        except Exception as e:
            self.logger.error(f"Failed to load adaptive config: {str(e)}")
    
    def validate_parameters(self, parameters: EnhancementParameters) -> List[str]:
        """Validate enhancement parameters and return any warnings"""
        warnings = []
        
        # Check parameter ranges
        if not 0.0 <= parameters.noise_reduction_strength <= 1.0:
            warnings.append("Noise reduction strength should be between 0.0 and 1.0")
        
        if not 0.0 <= parameters.spectral_enhancement_gain <= 1.0:
            warnings.append("Spectral enhancement gain should be between 0.0 and 1.0")
        
        if not 0.1 <= parameters.dynamic_range_target <= 1.0:
            warnings.append("Dynamic range target should be between 0.1 and 1.0")
        
        if not 0.5 <= parameters.stereo_width <= 2.0:
            warnings.append("Stereo width should be between 0.5 and 2.0")
        
        if not -30.0 <= parameters.mastering_loudness_lufs <= -6.0:
            warnings.append("Mastering loudness should be between -30.0 and -6.0 LUFS")
        
        # Check parameter combinations
        if (parameters.noise_reduction_strength > 0.8 and 
            parameters.preserve_original_character):
            warnings.append("High noise reduction may conflict with character preservation")
        
        if (parameters.spectral_enhancement_gain > 0.7 and 
            not parameters.high_quality_mode):
            warnings.append("High spectral enhancement recommended with high quality mode")
        
        return warnings
    
    def get_preset_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded presets"""
        if not self.presets:
            return {}
        
        categories = {}
        content_types = {}
        quality_levels = {}
        
        for preset in self.presets.values():
            # Category statistics
            cat = preset.category.value
            categories[cat] = categories.get(cat, 0) + 1
            
            # Content type statistics
            for ct in preset.content_types:
                ct_name = ct.value
                content_types[ct_name] = content_types.get(ct_name, 0) + 1
            
            # Quality level statistics
            ql = preset.target_quality.value
            quality_levels[ql] = quality_levels.get(ql, 0) + 1
        
        return {
            'total_presets': len(self.presets),
            'categories': categories,
            'content_types': content_types,
            'quality_levels': quality_levels,
            'recent_presets': [
                preset.name for preset in 
                sorted(self.presets.values(), key=lambda p: p.modified_timestamp, reverse=True)[:5]
            ]
        }
    
    def export_preset(self, name: str, file_path: Union[str, Path]):
        """Export single preset to file"""
        if name not in self.presets:
            raise ValueError(f"Preset '{name}' not found")
        
        preset_data = self.presets[name].to_dict()
        
        with open(file_path, 'w') as f:
            json.dump(preset_data, f, indent=2, default=str)
        
        self.logger.info(f"Exported preset '{name}' to {file_path}")
    
    def import_preset(self, file_path: Union[str, Path], overwrite: bool = False):
        """Import preset from file"""
        with open(file_path, 'r') as f:
            preset_data = json.load(f)
        
        preset = EnhancementPreset.from_dict(preset_data)
        self.add_preset(preset, overwrite=overwrite)
        
        self.logger.info(f"Imported preset '{preset.name}' from {file_path}")
