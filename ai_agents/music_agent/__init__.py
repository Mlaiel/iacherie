"""Music Agent - Ultra-Advanced Music Intelligence System for Content Creators
===========================================================================

Professional-grade music AI system designed for musicians, artists, producers,
and composers with comprehensive composition analysis, AI generation, advanced
analytics, and rights protection capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED
This software is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any attempt to copy, distribute, or reverse engineer this code without explicit
written permission is strictly forbidden and will result in legal prosecution
under German and International Copyright Law.

Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
"""
from .music_orchestrator import MusicOrchestrator
from .spotify_integration import SpotifyIntegration
from .composition_analyzer import (
    CompositionAnalyzer,
    CompositionAnalysisResult,
    CompositionComplexity,
    HarmonyAnalysis,
    RhythmAnalysis,
    MelodyAnalysis,
    StructuralAnalysis
)
from .music_generator import (
    MusicGenerator,
    GeneratedTrack,
    GenerationParameters,
    GenerationResult,
    GenerationMode,
    InstrumentType,
    MusicStyle,
    EmotionalArc
)
from .artist_insights import (
    ArtistInsights,
    ComprehensiveInsights,
    PerformanceMetrics,
    AudienceInsights,
    MarketPosition,
    CreativeAnalysis,
    FinancialInsights,
    ArtistRecommendation,
    InsightType,
    RecommendationPriority
)

# Package metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"
__team__ = "Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert"

__all__ = [
    # Main classes
    "MusicOrchestrator",
    "SpotifyIntegration",
    "CompositionAnalyzer",
    "MusicGenerator", 
    "ArtistInsights",
    
    # Composition Analysis
    "CompositionAnalysisResult",
    "CompositionComplexity",
    "HarmonyAnalysis",
    "RhythmAnalysis",
    "MelodyAnalysis",
    "StructuralAnalysis",
    
    # Music Generation
    "GeneratedTrack",
    "GenerationParameters", 
    "GenerationResult",
    "GenerationMode",
    "InstrumentType",
    "MusicStyle",
    "EmotionalArc",
    
    # Artist Insights
    "ComprehensiveInsights",
    "PerformanceMetrics",
    "AudienceInsights",
    "MarketPosition",
    "CreativeAnalysis",
    "FinancialInsights",
    "ArtistRecommendation",
    "InsightType",
    "RecommendationPriority",
    
    # Factory functions
    "create_music_agent",
    "create_composition_analyzer",
    "create_music_generator",
    "create_artist_insights"
]

def create_music_agent():
    """Factory function to create configured music orchestrator"""    return MusicOrchestrator()

def create_composition_analyzer():
    """Factory function to create composition analyzer"""    return CompositionAnalyzer()

def create_music_generator():
    """Factory function to create music generator"""    return MusicGenerator()

def create_artist_insights():
    """Factory function to create artist insights engine"""    return ArtistInsights()

# Module information
def get_module_info():
    """Get module information and capabilities"""    return {
        "name": "Music Agent",
        "version": __version__,
        "author": __author__,
        "team": __team__,
        "license": __license__,
        "capabilities": [
            "Advanced Music Composition Analysis",
            "AI Music Generation & Arrangement", 
            "Professional Artist Analytics",
            "Spotify Platform Integration",
            "Rights Protection & Monitoring",
            "Revenue Optimization",
            "Collaboration Matching",
            "Market Intelligence"
        ],
        "supported_formats": [
            "Audio: WAV, MP3, FLAC, AAC",
            "MIDI: Standard MIDI Files",
            "Metadata: JSON, XML",
            "Scores: MusicXML, PDF"
        ],
        "integrations": [
            "Spotify Web API",
            "Audio Processing Libraries",
            "Machine Learning Models",
            "Analytics Platforms",
            "Rights Management Systems"
        ]
    }
