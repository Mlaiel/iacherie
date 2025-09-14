"""🎵 Musician Model - Audio Creator Specialization
===============================================
Module: models/creator_models/musician_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Musician Specialized Model - Production-Ready
Responsibility: Music creator management and audio content specialization

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This model provides specialized functionality for musicians:
- Audio content creation and management
- Album and track organization
- Music collaboration and features
- Streaming platform integration
- Music analytics and insights
- Genre classification and tagging
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

from .user_model import UserProfile, UserModel

class MusicGenre(Enum):
    """Music genre classification"""
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    CLASSICAL = "classical"
    JAZZ = "jazz"
    COUNTRY = "country"
    R_AND_B = "r_and_b"
    REGGAE = "reggae"
    FOLK = "folk"
    BLUES = "blues"
    METAL = "metal"
    INDIE = "indie"
    ALTERNATIVE = "alternative"
    WORLD = "world"
    INSTRUMENTAL = "instrumental"
    AMBIENT = "ambient"
    OTHER = "other"

class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"          # 128 kbps
    MEDIUM = "medium"    # 192 kbps
    HIGH = "high"        # 320 kbps
    LOSSLESS = "lossless" # FLAC/WAV

class CollaborationRole(Enum):
    """Collaboration roles in music"""
    LEAD_ARTIST = "lead_artist"
    FEATURED_ARTIST = "featured_artist"
    PRODUCER = "producer"
    SONGWRITER = "songwriter"
    COMPOSER = "composer"
    VOCALIST = "vocalist"
    INSTRUMENTALIST = "instrumentalist"
    ENGINEER = "engineer"

@dataclass
class AudioContent:
    """Audio content metadata"""
    id: str
    title: str
    duration_seconds: int
    file_size_bytes: int
    format: str  # mp3, wav, flac, etc.
    quality: AudioQuality
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2  # stereo
    bpm: Optional[int] = None
    key: Optional[str] = None  # Musical key
    loudness_lufs: Optional[float] = None
    fingerprint_hash: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "format": self.format,
            "quality": self.quality.value,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "channels": self.channels,
            "bpm": self.bpm,
            "key": self.key,
            "loudness_lufs": self.loudness_lufs,
            "fingerprint_hash": self.fingerprint_hash,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class Track:
    """Individual music track"""
    id: str
    title: str
    artist_id: str
    audio_content: AudioContent
    genres: List[MusicGenre] = field(default_factory=list)
    lyrics: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    collaborators: List[Dict[str, Any]] = field(default_factory=list)
    release_date: Optional[datetime] = None
    is_explicit: bool = False
    is_instrumental: bool = False
    copyright_info: Optional[str] = None
    isrc: Optional[str] = None  # International Standard Recording Code
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Post-initialization"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "artist_id": self.artist_id,
            "audio_content": self.audio_content.to_dict(),
            "genres": [genre.value for genre in self.genres],
            "lyrics": self.lyrics,
            "description": self.description,
            "tags": self.tags,
            "collaborators": self.collaborators,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "is_explicit": self.is_explicit,
            "is_instrumental": self.is_instrumental,
            "copyright_info": self.copyright_info,
            "isrc": self.isrc,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

@dataclass
class Album:
    """Music album collection"""
    id: str
    title: str
    artist_id: str
    tracks: List[Track] = field(default_factory=list)
    artwork_url: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    total_duration_seconds: int = 0
    primary_genre: Optional[MusicGenre] = None
    record_label: Optional[str] = None
    catalog_number: Optional[str] = None
    upc: Optional[str] = None  # Universal Product Code
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Post-initialization"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def add_track(self, track: Track):
        """Add track to album"""
        self.tracks.append(track)
        self.total_duration_seconds += track.audio_content.duration_seconds
        self.updated_at = datetime.now(timezone.utc)
    
    def get_total_duration_formatted(self) -> str:
        """Get formatted total duration"""
        hours = self.total_duration_seconds // 3600
        minutes = (self.total_duration_seconds % 3600) // 60
        seconds = self.total_duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "artist_id": self.artist_id,
            "tracks": [track.to_dict() for track in self.tracks],
            "track_count": len(self.tracks),
            "artwork_url": self.artwork_url,
            "description": self.description,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "total_duration_seconds": self.total_duration_seconds,
            "total_duration_formatted": self.get_total_duration_formatted(),
            "primary_genre": self.primary_genre.value if self.primary_genre else None,
            "record_label": self.record_label,
            "catalog_number": self.catalog_number,
            "upc": self.upc,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

@dataclass
class MusicianProfile:
    """Specialized musician profile"""
    user_profile: UserProfile
    stage_name: Optional[str] = None
    instruments: List[str] = field(default_factory=list)
    primary_genres: List[MusicGenre] = field(default_factory=list)
    music_influences: List[str] = field(default_factory=list)
    years_experience: Optional[int] = None
    record_label: Optional[str] = None
    booking_contact: Optional[str] = None
    manager_contact: Optional[str] = None
    press_kit_url: Optional[str] = None
    discography: List[Album] = field(default_factory=list)
    singles: List[Track] = field(default_factory=list)
    collaborations: List[Dict[str, Any]] = field(default_factory=list)
    streaming_stats: Dict[str, Any] = field(default_factory=dict)
    awards: List[Dict[str, Any]] = field(default_factory=list)
    upcoming_releases: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_display_name(self) -> str:
        """Get display name (stage name or user display name)"""
        return self.stage_name or self.user_profile.display_name
    
    def get_total_tracks(self) -> int:
        """Get total number of tracks"""
        album_tracks = sum(len(album.tracks) for album in self.discography)
        return album_tracks + len(self.singles)
    
    def get_total_albums(self) -> int:
        """Get total number of albums"""
        return len(self.discography)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_profile": self.user_profile.to_dict(),
            "stage_name": self.stage_name,
            "display_name": self.get_display_name(),
            "instruments": self.instruments,
            "primary_genres": [genre.value for genre in self.primary_genres],
            "music_influences": self.music_influences,
            "years_experience": self.years_experience,
            "record_label": self.record_label,
            "booking_contact": self.booking_contact,
            "manager_contact": self.manager_contact,
            "press_kit_url": self.press_kit_url,
            "discography": [album.to_dict() for album in self.discography],
            "singles": [track.to_dict() for track in self.singles],
            "collaborations": self.collaborations,
            "streaming_stats": self.streaming_stats,
            "awards": self.awards,
            "upcoming_releases": self.upcoming_releases,
            "total_tracks": self.get_total_tracks(),
            "total_albums": self.get_total_albums()
        }

class MusicianModel:
    """Musician Model - Audio Creator Specialization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def create_profile(user_data: Dict[str, Any]) -> MusicianProfile:
        """Create musician profile from user data"""
        try:
            # Create base user profile
            user_profile = UserModel.create_profile(user_data)
            
            # Extract musician-specific data
            musician_data = user_data.get("musician_data", {})
            
            # Parse genres
            genre_names = musician_data.get("primary_genres", [])
            primary_genres = []
            for genre_name in genre_names:
                try:
                    genre = MusicGenre(genre_name.lower())
                    primary_genres.append(genre)
                except ValueError:
                    pass  # Skip invalid genres
            
            # Create musician profile
            musician_profile = MusicianProfile(
                user_profile=user_profile,
                stage_name=musician_data.get("stage_name"),
                instruments=musician_data.get("instruments", []),
                primary_genres=primary_genres,
                music_influences=musician_data.get("music_influences", []),
                years_experience=musician_data.get("years_experience"),
                record_label=musician_data.get("record_label"),
                booking_contact=musician_data.get("booking_contact"),
                manager_contact=musician_data.get("manager_contact"),
                press_kit_url=musician_data.get("press_kit_url")
            )
            
            return musician_profile
            
        except Exception as e:
            logging.error(f"Failed to create musician profile: {e}")
            raise
    
    @staticmethod
    def create_track(track_data: Dict[str, Any], artist_id: str) -> Track:
        """Create a new track"""
        try:
            # Create audio content
            audio_data = track_data.get("audio_content", {})
            audio_content = AudioContent(
                id=audio_data.get("id", str(uuid.uuid4())),
                title=audio_data.get("title", track_data["title"]),
                duration_seconds=audio_data["duration_seconds"],
                file_size_bytes=audio_data["file_size_bytes"],
                format=audio_data.get("format", "mp3"),
                quality=AudioQuality(audio_data.get("quality", "medium")),
                sample_rate=audio_data.get("sample_rate", 44100),
                bit_depth=audio_data.get("bit_depth", 16),
                channels=audio_data.get("channels", 2),
                bpm=audio_data.get("bpm"),
                key=audio_data.get("key"),
                loudness_lufs=audio_data.get("loudness_lufs")
            )
            
            # Parse genres
            genre_names = track_data.get("genres", [])
            genres = []
            for genre_name in genre_names:
                try:
                    genre = MusicGenre(genre_name.lower())
                    genres.append(genre)
                except ValueError:
                    pass
            
            # Create track
            track = Track(
                id=track_data.get("id", str(uuid.uuid4())),
                title=track_data["title"],
                artist_id=artist_id,
                audio_content=audio_content,
                genres=genres,
                lyrics=track_data.get("lyrics"),
                description=track_data.get("description"),
                tags=track_data.get("tags", []),
                collaborators=track_data.get("collaborators", []),
                is_explicit=track_data.get("is_explicit", False),
                is_instrumental=track_data.get("is_instrumental", False),
                copyright_info=track_data.get("copyright_info"),
                isrc=track_data.get("isrc")
            )
            
            return track
            
        except Exception as e:
            logging.error(f"Failed to create track: {e}")
            raise
    
    @staticmethod
    def create_album(album_data: Dict[str, Any], artist_id: str) -> Album:
        """Create a new album"""
        try:
            # Parse primary genre
            primary_genre = None
            if album_data.get("primary_genre"):
                try:
                    primary_genre = MusicGenre(album_data["primary_genre"].lower())
                except ValueError:
                    pass
            
            # Create album
            album = Album(
                id=album_data.get("id", str(uuid.uuid4())),
                title=album_data["title"],
                artist_id=artist_id,
                artwork_url=album_data.get("artwork_url"),
                description=album_data.get("description"),
                primary_genre=primary_genre,
                record_label=album_data.get("record_label"),
                catalog_number=album_data.get("catalog_number"),
                upc=album_data.get("upc")
            )
            
            # Add tracks if provided
            for track_data in album_data.get("tracks", []):
                track = MusicianModel.create_track(track_data, artist_id)
                album.add_track(track)
            
            return album
            
        except Exception as e:
            logging.error(f"Failed to create album: {e}")
            raise
    
    @staticmethod
    def analyze_music_style(tracks: List[Track]) -> Dict[str, Any]:
        """Analyze musician's style based on tracks"""
        if not tracks:
            return {"error": "No tracks to analyze"}
        
        # Analyze genres
        genre_counts = {}
        for track in tracks:
            for genre in track.genres:
                genre_counts[genre.value] = genre_counts.get(genre.value, 0) + 1
        
        # Analyze BPM patterns
        bpms = [track.audio_content.bpm for track in tracks if track.audio_content.bpm]
        avg_bpm = sum(bpms) / len(bpms) if bpms else None
        
        # Analyze track lengths
        durations = [track.audio_content.duration_seconds for track in tracks]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Analyze collaboration patterns
        collaboration_count = sum(1 for track in tracks if track.collaborators)
        
        return {
            "total_tracks": len(tracks),
            "genre_distribution": genre_counts,
            "primary_genre": max(genre_counts.items(), key=lambda x: x[1])[0] if genre_counts else None,
            "average_bpm": round(avg_bpm, 1) if avg_bpm else None,
            "bpm_range": {
                "min": min(bpms) if bpms else None,
                "max": max(bpms) if bpms else None
            },
            "average_duration_seconds": round(avg_duration, 1),
            "average_duration_formatted": f"{int(avg_duration // 60)}:{int(avg_duration % 60):02d}",
            "collaboration_rate": round((collaboration_count / len(tracks)) * 100, 1),
            "instrumental_rate": round((sum(1 for track in tracks if track.is_instrumental) / len(tracks)) * 100, 1),
            "explicit_rate": round((sum(1 for track in tracks if track.is_explicit) / len(tracks)) * 100, 1)
        }
    
    @staticmethod
    def suggest_collaborations(musician_profile: MusicianProfile, potential_collaborators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest potential collaborations based on musical compatibility"""
        suggestions = []
        
        for collaborator in potential_collaborators:
            compatibility_score = 0
            reasons = []
            
            # Genre compatibility
            collaborator_genres = set(collaborator.get("primary_genres", []))
            musician_genres = set(genre.value for genre in musician_profile.primary_genres)
            genre_overlap = len(collaborator_genres.intersection(musician_genres))
            
            if genre_overlap > 0:
                compatibility_score += genre_overlap * 20
                reasons.append(f"Shared {genre_overlap} genre(s)")
            
            # Instrument complementarity
            collaborator_instruments = set(collaborator.get("instruments", []))
            musician_instruments = set(musician_profile.instruments)
            
            # Bonus for complementary instruments
            complementary_pairs = [
                ("vocals", "guitar"), ("guitar", "bass"), ("drums", "guitar"),
                ("piano", "vocals"), ("violin", "piano")
            ]
            
            for instrument1, instrument2 in complementary_pairs:
                if instrument1 in musician_instruments and instrument2 in collaborator_instruments:
                    compatibility_score += 15
                    reasons.append(f"Complementary instruments: {instrument1}/{instrument2}")
            
            # Experience level compatibility
            musician_exp = musician_profile.years_experience or 0
            collaborator_exp = collaborator.get("years_experience", 0)
            exp_diff = abs(musician_exp - collaborator_exp)
            
            if exp_diff <= 3:
                compatibility_score += 10
                reasons.append("Similar experience level")
            
            # Location proximity (if available)
            if (musician_profile.user_profile.location and 
                collaborator.get("location") == musician_profile.user_profile.location):
                compatibility_score += 25
                reasons.append("Same location")
            
            if compatibility_score > 30:  # Minimum threshold
                suggestions.append({
                    "collaborator": collaborator,
                    "compatibility_score": compatibility_score,
                    "reasons": reasons
                })
        
        # Sort by compatibility score
        suggestions.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        return suggestions[:10]  # Return top 10 suggestions

# Export components
__all__ = [
    'MusicianModel', 'MusicianProfile', 'Track', 'Album', 'AudioContent',
    'MusicGenre', 'AudioQuality', 'CollaborationRole'
]