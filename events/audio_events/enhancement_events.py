"""Audio Enhancement Events - Industrial Grade Enhancement Event Management
==========================================================================

This module handles all events related to audio enhancement including AI enhancement,
upmixing, stem separation, mastering, and equalization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from ..core.base_event import BaseEvent


class EnhancementType(Enum):
    """Enhancement types"""
    AI_ENHANCEMENT = "ai_enhancement"
    NOISE_REDUCTION = "noise_reduction"
    MASTERING = "mastering"
    RESTORATION = "restoration"
    UPMIXING = "upmixing"


class NoiseType(Enum):
    """Noise types"""
    BACKGROUND = "background"
    HISS = "hiss"
    HUM = "hum"
    CLICK = "click"
    WIND = "wind"


class MasteringPreset(Enum):
    """Mastering presets"""
    STREAMING = "streaming"
    CD_MASTER = "cd_master"
    VINYL = "vinyl"
    RADIO = "radio"
    PODCAST = "podcast"


@dataclass
class AudioEnhancementStartedEvent(BaseEvent):
    """AudioEnhancementStartedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    filename: str
    enhancement_type: str
    enhancement_profile: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.started",
            data={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "enhancement_type": self.enhancement_type
            }
        )


@dataclass
class AudioEnhancementProgressEvent(BaseEvent):
    """AudioEnhancementProgressEvent class implementation"""
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    progress_percentage: float
    current_stage: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.progress",
            data={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "progress_percentage": self.progress_percentage
            }
        )


@dataclass
class AudioEnhancementCompletedEvent(BaseEvent):
    """AudioEnhancementCompletedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    filename: str
    enhancement_results: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.completed",
            data={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id)
            }
        )


@dataclass
class AudioEnhancementFailedEvent(BaseEvent):
    """AudioEnhancementFailedEvent class implementation"""
    user_id: UUID
    file_id: UUID
    enhancement_id: UUID
    error_code: str
    error_message: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.failed",
            data={
                "file_id": str(self.file_id),
                "enhancement_id": str(self.enhancement_id),
                "error_code": self.error_code
            }
        )


@dataclass
class AudioNoiseReductionEvent(BaseEvent):
    """AudioNoiseReductionEvent class implementation"""
    user_id: UUID
    file_id: UUID
    noise_reduction_id: UUID
    filename: str
    noise_types: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.noise_reduction",
            data={
                "file_id": str(self.file_id),
                "noise_reduction_id": str(self.noise_reduction_id)
            }
        )


@dataclass
class AudioMasteringEvent(BaseEvent):
    """AudioMasteringEvent class implementation"""
    user_id: UUID
    file_id: UUID
    mastering_id: UUID
    filename: str
    mastering_preset: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.mastering",
            data={
                "file_id": str(self.file_id),
                "mastering_id": str(self.mastering_id),
                "mastering_preset": self.mastering_preset
            }
        )


@dataclass
class AudioAIEnhancementEvent(BaseEvent):
    """AudioAIEnhancementEvent class implementation"""
    user_id: UUID
    file_id: UUID
    ai_enhancement_id: UUID
    filename: str
    ai_model: str
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.ai_enhancement",
            data={
                "file_id": str(self.file_id),
                "ai_enhancement_id": str(self.ai_enhancement_id),
                "ai_model": self.ai_model
            }
        )


@dataclass
class AudioUpmixingEvent(BaseEvent):
    """AudioUpmixingEvent class implementation"""
    user_id: UUID
    file_id: UUID
    upmixing_id: UUID
    filename: str
    target_channels: int
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.upmixing",
            data={
                "file_id": str(self.file_id),
                "upmixing_id": str(self.upmixing_id),
                "target_channels": self.target_channels
            }
        )


@dataclass
class AudioStemSeparationEvent(BaseEvent):
    """AudioStemSeparationEvent class implementation"""
    user_id: UUID
    file_id: UUID
    separation_id: UUID
    filename: str
    stems_extracted: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.stem_separation",
            data={
                "file_id": str(self.file_id),
                "separation_id": str(self.separation_id),
                "stems_count": len(self.stems_extracted)
            }
        )


@dataclass
class AudioEqualizationEvent(BaseEvent):
    """AudioEqualizationEvent class implementation"""
    user_id: UUID
    file_id: UUID
    eq_id: UUID
    filename: str
    eq_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.enhancement.equalization",
            data={
                "file_id": str(self.file_id),
                "eq_id": str(self.eq_id)
            }
        )