"""
Music Composition Template for AI-Powered Content Generation

Enterprise-grade music composition prompt engineering template optimized for the Creator Economy.
Provides advanced prompt structures for generating high-quality music compositions across
multiple genres, styles, and platforms with built-in optimization for engagement and monetization.

Author: AI Expert Team Lead by Fahed Mlaiel
Contact: contact@fahedmlaiel.fr | https://fahedmlaiel.fr
Copyright (c) 2024 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact for licensing terms
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicGenre(Enum):
    """Supported music genres"""
    POP = "pop"
    ROCK = "rock"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip_hop"
    R_AND_B = "r_and_b"
    COUNTRY = "country"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    FOLK = "folk"
    REGGAE = "reggae"
    BLUES = "blues"
    FUNK = "funk"
    AMBIENT = "ambient"
    TECHNO = "techno"
    HOUSE = "house"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    METAL = "metal"
    PUNK = "punk"
    WORLD = "world"

class MusicMood(Enum):
    """Music mood options"""
    UPBEAT = "upbeat"
    MELANCHOLIC = "melancholic"
    ENERGETIC = "energetic"
    RELAXING = "relaxing"
    ROMANTIC = "romantic"
    AGGRESSIVE = "aggressive"
    PEACEFUL = "peaceful"
    MYSTERIOUS = "mysterious"
    DRAMATIC = "dramatic"
    HAPPY = "happy"
    SAD = "sad"
    INSPIRING = "inspiring"
    DARK = "dark"
    BRIGHT = "bright"
    NOSTALGIC = "nostalgic"

class MusicLength(Enum):
    """Music composition length"""
    INTRO = "intro"           # 5-15 seconds
    JINGLE = "jingle"         # 15-30 seconds
    SHORT = "short"           # 30-90 seconds
    STANDARD = "standard"     # 2-4 minutes
    EXTENDED = "extended"     # 4-7 minutes
    EPIC = "epic"            # 7+ minutes

class MusicPurpose(Enum):
    """Music purpose/usage"""
    BACKGROUND_MUSIC = "background_music"
    INTRO_OUTRO = "intro_outro"
    COMMERCIAL = "commercial"
    PODCAST_MUSIC = "podcast_music"
    VIDEO_SOUNDTRACK = "video_soundtrack"
    SOCIAL_MEDIA = "social_media"
    LIVESTREAM = "livestream"
    MEDITATION = "meditation"
    WORKOUT = "workout"
    STUDY_FOCUS = "study_focus"
    GAMING = "gaming"
    PRESENTATION = "presentation"

@dataclass
class MusicCompositionPrompt:
    """Music composition prompt configuration"""
    genre: MusicGenre
    mood: MusicMood
    length: MusicLength
    purpose: MusicPurpose
    title: str
    duration_seconds: float
    tempo_bpm: Optional[int] = None
    key_signature: str = ""
    instruments: List[str] = field(default_factory=list)
    vocal_elements: str = ""
    lyrics_theme: str = ""
    target_audience: str = ""
    platform_optimization: str = ""
    reference_artists: List[str] = field(default_factory=list)
    cultural_elements: List[str] = field(default_factory=list)
    production_style: str = ""
    mixing_notes: str = ""
    mastering_requirements: str = ""
    copyright_considerations: str = ""
    monetization_strategy: str = ""
    licensing_type: str = ""

class MusicCompositionTemplate:
    """
    Advanced music composition template for AI content generation
    
    Optimized for Creator Economy with platform-specific formatting, licensing considerations,
    and monetization strategies. Supports all major music platforms and usage types.
    """
    
    def __init__(self):
        self.template_version = "1.0.0"
        self.creator_economy_features = True
        self.licensing_optimization = True
        self.platform_optimization = True
        
        # Platform specifications for music
        self.platform_specs = {
            "spotify": {
                "optimal_length": "3-4 minutes",
                "format_requirements": "44.1 kHz, 16-bit minimum",
                "loudness_standard": "-14 LUFS",
                "features": ["spatial_audio", "podcast_integration", "playlist_optimization"]
            },
            "youtube": {
                "optimal_length": "3-5 minutes for music videos",
                "format_requirements": "48 kHz, 24-bit preferred",
                "loudness_standard": "-13 LUFS",
                "features": ["content_id", "monetization", "shorts_integration"]
            },
            "apple_music": {
                "optimal_length": "3-4 minutes",
                "format_requirements": "44.1 kHz, 24-bit",
                "loudness_standard": "-16 LUFS",
                "features": ["spatial_audio", "lossless", "lyrics_integration"]
            },
            "tiktok": {
                "optimal_length": "15-60 seconds",
                "format_requirements": "44.1 kHz, 16-bit",
                "loudness_standard": "-12 LUFS",
                "features": ["viral_potential", "dance_trends", "creator_fund"]
            },
            "instagram": {
                "optimal_length": "30-90 seconds for reels",
                "format_requirements": "44.1 kHz, 16-bit",
                "loudness_standard": "-12 LUFS",  
                "features": ["stories_integration", "reels_optimization", "live_streaming"]
            }
        }
        
        # Licensing types and considerations
        self.licensing_options = {
            "royalty_free": "One-time payment, unlimited usage rights",
            "creative_commons": "Free with attribution requirements",
            "exclusive": "Full ownership transfer to buyer",
            "non_exclusive": "Multiple licensing allowed",
            "sync_licensing": "Specific media synchronization rights",
            "performance_licensing": "Live performance and broadcast rights"
        }
        
    def generate_prompt(self, config: MusicCompositionPrompt) -> Dict[str, Any]:
        """
        Generate optimized music composition prompt
        
        Args:
            config: Music composition configuration
            
        Returns:
            Dictionary containing optimized prompt and metadata
        """
        try:
            # Build comprehensive prompt
            prompt_components = {
                "system_prompt": self._build_system_prompt(config),
                "user_prompt": self._build_user_prompt(config),
                "composition_structure": self._build_composition_structure(config),
                "technical_requirements": self._build_technical_requirements(config),
                "creative_direction": self._build_creative_direction(config),
                "production_notes": self._build_production_notes(config),
                "platform_optimization": self._build_platform_optimization(config),
                "licensing_guidance": self._build_licensing_guidance(config),
                "monetization_strategy": self._build_monetization_strategy(config)
            }
            
            # Combine into final prompt
            final_prompt = self._combine_prompt_components(prompt_components)
            
            # Generate metadata
            metadata = self._generate_metadata(config)
            
            logger.info(f"Generated music composition prompt for {config.genre.value} in {config.mood.value} mood")
            
            return {
                "prompt": final_prompt,
                "metadata": metadata,
                "config": config,
                "optimization_score": self._calculate_optimization_score(config),
                "commercial_potential": self._estimate_commercial_potential(config),
                "platform_suitability": self._analyze_platform_suitability(config),
                "licensing_recommendations": self._recommend_licensing(config)
            }
            
        except Exception as e:
            logger.error(f"Error generating music composition prompt: {str(e)}")
            raise
    
    def _build_system_prompt(self, config: MusicCompositionPrompt) -> str:
        """Build system prompt for music composition"""
        duration_minutes = config.duration_seconds / 60
        
        return f"""You are a master music composer and producer specializing in {config.genre.value} music for the Creator Economy.

Your expertise includes:
- Professional music composition and arrangement across all genres
- Music production, mixing, and mastering techniques
- Creator Economy music licensing and monetization
- Platform-specific music optimization and distribution
- Copyright law and music licensing best practices
- Sync licensing for media and commercial applications

Creating: {config.title}
Genre: {config.genre.value}
Mood: {config.mood.value}
Length: {config.length.value} ({duration_minutes:.1f} minutes)
Purpose: {config.purpose.value}
Target Audience: {config.target_audience or 'General music audience'}

Focus on:
- Creating commercially viable and platform-optimized music
- Ensuring copyright compliance and licensing clarity
- Maximizing monetization potential across platforms
- Building memorable and engaging musical content
- Professional production standards and technical excellence
- Creator brand building through signature musical style"""

    def _build_user_prompt(self, config: MusicCompositionPrompt) -> str:
        """Build user prompt with composition specifications"""
        tempo_info = f"\nTempo: {config.tempo_bpm} BPM" if config.tempo_bpm else ""
        key_info = f"\nKey: {config.key_signature}" if config.key_signature else ""
        instruments_info = f"\nInstruments: {', '.join(config.instruments)}" if config.instruments else ""
        vocal_info = f"\nVocal Elements: {config.vocal_elements}" if config.vocal_elements else ""
        lyrics_info = f"\nLyrics Theme: {config.lyrics_theme}" if config.lyrics_theme else ""
        references_info = f"\nReference Artists/Style: {', '.join(config.reference_artists)}" if config.reference_artists else ""
        cultural_info = f"\nCultural Elements: {', '.join(config.cultural_elements)}" if config.cultural_elements else ""
        
        return f"""Create a complete music composition specification for: {config.title}

Genre: {config.genre.value}
Mood: {config.mood.value}
Duration: {config.duration_seconds} seconds
Purpose: {config.purpose.value}
Platform: {config.platform_optimization or 'Multi-platform'}{tempo_info}{key_info}{instruments_info}{vocal_info}{lyrics_info}{references_info}{cultural_info}

Composition Requirements:
- Create detailed musical arrangement and structure
- Specify chord progressions, melody lines, and harmonies
- Include rhythm patterns and drum arrangements
- Design for {config.purpose.value} usage optimization
- Ensure commercial viability and licensing potential
- Include production notes for mixing and mastering

Creator Economy Optimization:
- Design for maximum platform engagement and algorithmic favor
- Create memorable hooks and distinctive musical elements
- Include viral potential and shareability factors
- Optimize for target audience preferences and trends
- Build composer/producer brand recognition and style
- Ensure cross-platform adaptability and repurposing potential"""

    def _build_composition_structure(self, config: MusicCompositionPrompt) -> str:
        """Build composition structure based on length and purpose"""
        duration_seconds = config.duration_seconds
        
        if config.length == MusicLength.INTRO:
            structure = """
COMPOSITION STRUCTURE (Intro/Jingle):
- Immediate hook (0-2 seconds)
- Main theme development (2-8 seconds)  
- Brand element/signature (8-12 seconds)
- Resolution/fade (12-15 seconds)"""
        elif config.length == MusicLength.SHORT:
            structure = """
COMPOSITION STRUCTURE (Short Form):
- Hook/Opening (0-5 seconds)
- Verse/Main theme (5-20 seconds)
- Chorus/Climax (20-45 seconds)
- Outro/Resolution (45-60+ seconds)"""
        elif config.length == MusicLength.STANDARD:
            structure = """
COMPOSITION STRUCTURE (Standard Song):
- Intro (0-15 seconds)
- Verse 1 (15-45 seconds)
- Chorus 1 (45-75 seconds)
- Verse 2 (75-105 seconds)
- Chorus 2 (105-135 seconds)
- Bridge/Solo (135-165 seconds)
- Final Chorus (165-195 seconds)
- Outro (195+ seconds)"""
        else:
            structure = """
COMPOSITION STRUCTURE (Extended/Epic):
- Extended intro with build-up
- Multiple verse and chorus sections
- Instrumental breaks and solos
- Dynamic sections with varying intensity
- Epic climax and extended outro"""
        
        return f"""{structure}

Arrangement Details:
- Specify instrumentation for each section
- Include dynamic changes and intensity variations
- Mark key signature and tempo changes
- Include breakdown and build-up sections
- Design transitions and bridges
- Create memorable hooks and motifs throughout"""

    def _build_technical_requirements(self, config: MusicCompositionPrompt) -> str:
        """Build technical requirements for production"""
        platform = config.platform_optimization.lower() if config.platform_optimization else ""
        specs = self.platform_specs.get(platform, {})
        
        return f"""
TECHNICAL REQUIREMENTS:

Audio Specifications:
- Sample Rate: {specs.get('format_requirements', '44.1 kHz, 24-bit recommended')}
- Loudness Target: {specs.get('loudness_standard', '-14 LUFS (streaming standard)')}
- Dynamic Range: Maintain appropriate dynamics for genre and platform
- Frequency Response: Full spectrum with genre-appropriate EQ curve
- Stereo Imaging: Wide stereo field with mono compatibility

Production Standards:
- Professional mixing with clarity and separation
- Mastering for streaming platforms and digital distribution
- Phase coherence and mono compatibility
- Headroom management for mastering process
- Quality control for all delivery formats

File Deliverables:
- High-resolution master (24-bit/96kHz minimum)
- Streaming-optimized version (16-bit/44.1kHz)
- Platform-specific formats as required
- Instrumental and vocal stems if applicable
- MIDI files and project files for licensing"""

    def _build_creative_direction(self, config: MusicCompositionPrompt) -> str:
        """Build creative direction and artistic vision"""
        production_style = f"Production Style: {config.production_style}" if config.production_style else "Production Style: Modern, clean, and professional"
        
        return f"""
CREATIVE DIRECTION:

Artistic Vision:
- Capture {config.mood.value} mood through harmonic choices and rhythmic elements
- Incorporate {config.genre.value} genre conventions while maintaining originality
- Create emotional journey that engages listeners throughout
- Include signature elements that build composer brand recognition
- Balance familiarity with innovation for commercial appeal

Musical Elements:
- Melody: Memorable, singable themes with strong hooks
- Harmony: Genre-appropriate chord progressions with interesting variations
- Rhythm: Compelling groove that drives the composition forward
- Texture: Rich but not cluttered, with clear instrument separation
- Dynamics: Strategic use of loud/soft sections for emotional impact

{production_style}
- Modern production techniques with timeless musical foundations
- Competitive loudness while maintaining musical dynamics
- Genre-appropriate sound design and effects processing
- Professional vocal production (if applicable)
- Mixing that translates well across all playback systems"""

    def _build_production_notes(self, config: MusicCompositionPrompt) -> str:
        """Build production, mixing, and mastering notes"""
        mixing_notes = config.mixing_notes or "Standard professional mixing practices"
        mastering_notes = config.mastering_requirements or "Streaming-optimized mastering"
        
        return f"""
PRODUCTION NOTES:

Recording Considerations:
- High-quality source recordings with appropriate microphone techniques
- Proper acoustic treatment and recording environment
- Multiple takes and comping for best performance
- DI and amplified recordings where appropriate
- Room tone and ambient recordings for texture

Mixing Guidelines:
{mixing_notes}
- EQ: Surgical cuts and musical boosts, complementary frequency distribution
- Compression: Musical compression that enhances rather than flattens
- Reverb/Delay: Spatial effects that support the emotional narrative
- Automation: Dynamic automation for musical expression
- Effects: Genre-appropriate processing that serves the song

Mastering Requirements:
{mastering_notes}
- Loudness optimization for target platforms
- EQ for frequency balance and translation
- Dynamics processing for consistency and impact
- Stereo enhancement and imaging optimization
- Quality control and format optimization"""

    def _build_platform_optimization(self, config: MusicCompositionPrompt) -> str:
        """Build platform-specific optimization"""
        if not config.platform_optimization:
            return "PLATFORM OPTIMIZATION: Multi-platform optimization for maximum reach and engagement"
            
        platform = config.platform_optimization.lower()
        specs = self.platform_specs.get(platform, {})
        
        return f"""
PLATFORM OPTIMIZATION for {platform.upper()}:

Platform Requirements:
- Optimal Length: {specs.get('optimal_length', 'Standard song length')}
- Technical Specs: {specs.get('format_requirements', 'High-quality audio')}
- Loudness Standard: {specs.get('loudness_standard', 'Platform appropriate')}
- Special Features: {', '.join(specs.get('features', []))}

Content Optimization:
- Structure for platform consumption patterns
- Hook placement for algorithm optimization
- Engagement elements for platform-specific features
- Metadata optimization for discovery
- Visual content integration (if applicable)

Distribution Strategy:
- Release timing for maximum platform visibility
- Playlist targeting and curator outreach
- Cross-platform promotional content creation
- Social media integration and viral elements
- Community engagement and fan interaction features"""

    def _build_licensing_guidance(self, config: MusicCompositionPrompt) -> str:
        """Build licensing and copyright guidance"""
        licensing_type = config.licensing_type or "royalty_free"
        copyright_notes = config.copyright_considerations or "Original composition with no copyright conflicts"
        
        return f"""
LICENSING AND LEGAL GUIDANCE:

Licensing Type: {licensing_type}
Description: {self.licensing_options.get(licensing_type, 'Custom licensing arrangement')}

Copyright Considerations:
{copyright_notes}
- Ensure all musical elements are original or properly licensed
- Clear any samples or interpolations used
- Document all contributors and their rights
- Register composition with performing rights organizations
- Maintain detailed creation and ownership records

Usage Rights:
- Define permitted use cases and restrictions
- Specify territory and duration limitations
- Include synchronization rights for media usage
- Address derivative works and remix permissions
- Set royalty and payment structures

Creator Protection:
- Watermark demo versions appropriately
- Protect against unauthorized usage
- Implement content ID and recognition systems
- Monitor usage across platforms and media
- Establish enforcement procedures for violations"""

    def _build_monetization_strategy(self, config: MusicCompositionPrompt) -> str:
        """Build monetization strategy"""
        strategy = config.monetization_strategy or "Multi-revenue stream approach"
        
        return f"""
MONETIZATION STRATEGY:

Primary Strategy: {strategy}

Revenue Streams:
- Streaming platforms (Spotify, Apple Music, etc.)
- Sync licensing for video, film, and commercial use
- Direct sales and digital downloads
- Live performance and concert usage
- Sample licensing and remix permissions
- Educational licensing for instructional content

Creator Economy Integration:
- Background music for content creators
- Podcast intro/outro licensing
- Social media content soundtracks
- YouTube monetization and content ID
- Brand partnership and commercial licensing
- Creator collaboration and featuring opportunities

Pricing Strategy:
- Competitive streaming royalty optimization
- Tiered licensing for different usage levels
- Premium pricing for exclusive or custom work
- Volume discounts for bulk licensing
- Creator-friendly pricing for small businesses
- Regular review and market adjustment

Long-term Value:
- Build catalog value through consistent quality
- Develop signature style for brand recognition
- Create series or themed collections
- Establish relationships with music supervisors
- Build direct-to-fan monetization channels
- Explore NFT and digital collectible opportunities"""

    def _combine_prompt_components(self, components: Dict[str, str]) -> str:
        """Combine all prompt components into final prompt"""
        return f"""{components['system_prompt']}

{components['user_prompt']}

{components['composition_structure']}

{components['technical_requirements']}

{components['creative_direction']}

{components['production_notes']}

{components['platform_optimization']}

{components['licensing_guidance']}

{components['monetization_strategy']}

Now create the complete music composition specification following all these guidelines. Include detailed musical notation descriptions, production notes, and commercial optimization strategies."""

    def _generate_metadata(self, config: MusicCompositionPrompt) -> Dict[str, Any]:
        """Generate metadata for the composition"""
        return {
            "template_version": self.template_version,
            "genre": config.genre.value,
            "mood": config.mood.value,
            "length": config.length.value,
            "purpose": config.purpose.value,
            "duration_seconds": config.duration_seconds,
            "duration_minutes": config.duration_seconds / 60,
            "tempo_bpm": config.tempo_bpm,
            "key_signature": config.key_signature,
            "instruments_count": len(config.instruments),
            "has_vocals": bool(config.vocal_elements),
            "has_lyrics": bool(config.lyrics_theme),
            "reference_artists_count": len(config.reference_artists),
            "cultural_elements_count": len(config.cultural_elements),
            "platform": config.platform_optimization,
            "licensing_type": config.licensing_type,
            "commercial_potential": bool(config.monetization_strategy),
            "creation_timestamp": datetime.now().isoformat(),
            "creator_economy_optimized": True
        }

    def _calculate_optimization_score(self, config: MusicCompositionPrompt) -> float:
        """Calculate optimization score based on configuration"""
        score = 0.5  # Base score
        
        # Add points for configuration completeness
        if config.tempo_bpm:
            score += 0.1
        if config.key_signature:
            score += 0.05
        if config.instruments:
            score += 0.1
        if config.platform_optimization:
            score += 0.1
        if config.monetization_strategy:
            score += 0.1
        if config.reference_artists:
            score += 0.05
        if config.licensing_type:
            score += 0.1
        
        return min(score, 1.0)

    def _estimate_commercial_potential(self, config: MusicCompositionPrompt) -> str:
        """Estimate commercial potential"""
        score = self._calculate_optimization_score(config)
        
        # Boost score for commercial-friendly purposes
        if config.purpose in [MusicPurpose.COMMERCIAL, MusicPurpose.VIDEO_SOUNDTRACK, MusicPurpose.BACKGROUND_MUSIC]:
            score += 0.1
            
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium-High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low-Medium"

    def _analyze_platform_suitability(self, config: MusicCompositionPrompt) -> Dict[str, str]:
        """Analyze suitability for different platforms"""
        suitability = {}
        duration = config.duration_seconds
        
        # Spotify
        if 120 <= duration <= 300:  # 2-5 minutes
            suitability["spotify"] = "Excellent"
        elif duration < 120 or duration > 300:
            suitability["spotify"] = "Good"
        else:
            suitability["spotify"] = "Fair"
            
        # TikTok
        if duration <= 60:
            suitability["tiktok"] = "Excellent"
        elif duration <= 180:
            suitability["tiktok"] = "Good (can be edited)"
        else:
            suitability["tiktok"] = "Poor (too long)"
            
        # YouTube
        if 180 <= duration <= 360:  # 3-6 minutes
            suitability["youtube"] = "Excellent"
        else:
            suitability["youtube"] = "Good"
            
        # Instagram
        if duration <= 90:
            suitability["instagram"] = "Excellent for Reels"
        elif duration <= 240:
            suitability["instagram"] = "Good for posts"
        else:
            suitability["instagram"] = "Fair (needs editing)"
            
        return suitability

    def _recommend_licensing(self, config: MusicCompositionPrompt) -> List[str]:
        """Recommend licensing types based on composition"""
        recommendations = []
        
        if config.purpose == MusicPurpose.BACKGROUND_MUSIC:
            recommendations.append("royalty_free - Ideal for content creator usage")
            recommendations.append("sync_licensing - For commercial video usage")
            
        elif config.purpose == MusicPurpose.COMMERCIAL:
            recommendations.append("exclusive - Maximum value for commercial use")
            recommendations.append("sync_licensing - Specific commercial campaign rights")
            
        elif config.purpose in [MusicPurpose.SOCIAL_MEDIA, MusicPurpose.VIDEO_SOUNDTRACK]:
            recommendations.append("creative_commons - Viral potential with attribution")
            recommendations.append("non_exclusive - Multiple creator usage")
            
        else:
            recommendations.append("royalty_free - Flexible usage rights")
            recommendations.append("non_exclusive - Multiple licensing opportunities")
            
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Example configuration
    config = MusicCompositionPrompt(
        genre=MusicGenre.ELECTRONIC,
        mood=MusicMood.UPBEAT,
        length=MusicLength.STANDARD,
        purpose=MusicPurpose.VIDEO_SOUNDTRACK,
        title="Digital Dreams - Creator Anthem",
        duration_seconds=180.0,
        tempo_bpm=128,
        key_signature="C Major",
        instruments=["synthesizers", "digital drums", "bass", "lead synth", "pads"],
        vocal_elements="Vocal chops and effects",
        target_audience="content creators and digital entrepreneurs",
        platform_optimization="youtube",
        reference_artists=["Daft Punk", "Deadmau5", "Justice"],
        production_style="Modern electronic with retro influences",
        mixing_notes="Wide stereo image with punchy drums and clear bass",
        mastering_requirements="Streaming optimized with good dynamics",
        copyright_considerations="100% original composition",
        monetization_strategy="Creator licensing and sync opportunities",
        licensing_type="royalty_free"
    )
    
    # Generate prompt
    template = MusicCompositionTemplate()
    result = template.generate_prompt(config)
    
    print("=== MUSIC COMPOSITION TEMPLATE EXAMPLE ===")
    print(f"Optimization Score: {result['optimization_score']:.2f}")
    print(f"Commercial Potential: {result['commercial_potential']}")
    print(f"Platform Suitability: {result['platform_suitability']}")
    print(f"Licensing Recommendations: {result['licensing_recommendations']}")
    print("\n" + "="*50)
    print(result['prompt'])