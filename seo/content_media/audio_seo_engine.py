"""Audio SEO Engine
Advanced SEO optimization for audio content, musicians, and podcasters.

Features:
- Audio metadata optimization
- Transcript generation and optimization
- Music genre and mood tagging
- Streaming platform optimization
- Audio accessibility enhancements

Author: Fahed Mlaiel (mlaiel@live.de)
Audio Engineer + SEO Expert expertise applied
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re

try:
    import librosa
    import numpy as np
    from pydub import AudioSegment
    from pydub.utils import which
    import speech_recognition as sr
    from transformers import pipeline
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, COMM, TXXX
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError as e:
    logging.warning(f"Optional audio dependencies not available: {e}")

logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"
    M4A = "m4a"
    OGG = "ogg"
    AAC = "aac"

class MusicGenre(Enum):
    """Music genres for categorization."""
    ROCK = "rock"
    POP = "pop"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    HIP_HOP = "hip-hop"
    COUNTRY = "country"
    FOLK = "folk"
    BLUES = "blues"
    REGGAE = "reggae"
    METAL = "metal"
    PUNK = "punk"
    FUNK = "funk"
    SOUL = "soul"
    RNB = "r&b"
    AMBIENT = "ambient"
    WORLD = "world"
    EXPERIMENTAL = "experimental"

@dataclass
class AudioMetadata:
    """Audio file metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    file_size: Optional[int] = None
    format: Optional[AudioFormat] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    danceability: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    speechiness: Optional[float] = None

@dataclass
class AudioTranscript:
    """Audio transcript with timestamps."""
    full_text: str
    segments: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    language: str = "en"
    speaker_labels: List[str] = field(default_factory=list)

@dataclass
class AudioSEOResult:
    """Result of audio SEO optimization."""
    original_metadata: AudioMetadata
    optimized_metadata: AudioMetadata
    transcript: Optional[AudioTranscript]
    seo_title: str
    seo_description: str
    keywords: List[str]
    hashtags: List[str]
    platform_optimizations: Dict[str, Dict[str, Any]]
    accessibility_features: Dict[str, Any]
    schema_markup: Dict[str, Any]
    optimization_score: float
    recommendations: List[str]

@dataclass
class AudioSEOConfig:
    """Configuration for audio SEO optimization."""
    target_platforms: List[str] = field(default_factory=lambda: ["spotify", "apple_music", "youtube", "soundcloud"])
    target_audience: str = "general"
    content_type: str = "music"  # music, podcast, audiobook, voice-over
    generate_transcript: bool = True
    optimize_metadata: bool = True
    generate_keywords: bool = True
    include_accessibility: bool = True
    target_genres: List[str] = field(default_factory=list)
    language: str = "en"

class AudioSEOEngine:
    """Advanced audio SEO optimization engine."""
    
    def __init__(self, spotify_client_id -> None: Optional[str] = None, spotify_client_secret -> None: Optional[str] = None) -> None:
        """Initialize the Audio SEO Engine.
        
        Args:
            spotify_client_id: Spotify API client ID
            spotify_client_secret: Spotify API client secret
        """
        self.spotify_client = None
        self.speech_recognizer = None
        self.music_classifier = None
        self.emotion_classifier = None
        self._setup_audio_tools()
        self._setup_spotify(spotify_client_id, spotify_client_secret)
        
        # Platform-specific requirements
        self.platform_requirements = self._load_platform_requirements()
        
        # Audio analysis cache
        self.analysis_cache = {}
        
    def _setup_audio_tools(self) -> None:
        """Setup audio processing tools."""
        try:
            # Setup speech recognition
            self.speech_recognizer = sr.Recognizer()
            
            # Setup music classification model
            try:
                self.music_classifier = pipeline(
                    "audio-classification",
                    model="MIT/ast-finetuned-audioset-10-10-0.4593"
                )
            except Exception as e:
                logger.warning(f"Could not load music classifier: {e}")
            
            # Setup emotion classification
            try:
                self.emotion_classifier = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base"
                )
            except Exception as e:
                logger.warning(f"Could not load emotion classifier: {e}")
                
        except Exception as e:
            logger.error(f"Error setting up audio tools: {e}")
    
    def _setup_spotify(self, client_id -> None: Optional[str], client_secret -> None: Optional[str]) -> None:
        """Setup Spotify API client."""
        try:
            if client_id and client_secret:
                credentials = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.spotify_client = spotipy.Spotify(client_credentials_manager=credentials)
                logger.info("Spotify API client initialized")
            else:
                logger.warning("Spotify credentials not provided")
        except Exception as e:
            logger.error(f"Error setting up Spotify client: {e}")
    
    def _load_platform_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific SEO requirements."""
        return {
            "spotify": {
                "title_max_length": 100,
                "description_max_length": 1000,
                "required_metadata": ["title", "artist", "album", "genre"],
                "preferred_formats": [AudioFormat.MP3, AudioFormat.FLAC],
                "min_quality": {"bitrate": 320, "sample_rate": 44100},
                "keywords_focus": ["mood", "genre", "energy", "tempo"]
            },
            "apple_music": {
                "title_max_length": 255,
                "description_max_length": 4000,
                "required_metadata": ["title", "artist", "album", "year"],
                "preferred_formats": [AudioFormat.M4A, AudioFormat.MP3],
                "min_quality": {"bitrate": 256, "sample_rate": 44100},
                "keywords_focus": ["genre", "mood", "instruments", "vocals"]
            },
            "youtube": {
                "title_max_length": 100,
                "description_max_length": 5000,
                "required_metadata": ["title", "description"],
                "preferred_formats": [AudioFormat.MP3, AudioFormat.WAV],
                "min_quality": {"bitrate": 128, "sample_rate": 44100},
                "keywords_focus": ["trending", "viral", "genre", "mood", "artist"]
            },
            "soundcloud": {
                "title_max_length": 100,
                "description_max_length": 4000,
                "required_metadata": ["title", "genre"],
                "preferred_formats": [AudioFormat.MP3, AudioFormat.FLAC],
                "min_quality": {"bitrate": 128, "sample_rate": 44100},
                "keywords_focus": ["genre", "underground", "independent", "emerging"]
            },
            "podcast_platforms": {
                "title_max_length": 255,
                "description_max_length": 4000,
                "required_metadata": ["title", "description", "category"],
                "preferred_formats": [AudioFormat.MP3],
                "min_quality": {"bitrate": 128, "sample_rate": 44100},
                "keywords_focus": ["topic", "guest", "episode", "series"]
            }
        }
    
    async def optimize_audio_seo(
        self,
        audio_file_path: str,
        config: AudioSEOConfig
    ) -> AudioSEOResult:
        """Optimize audio content for SEO across platforms.
        
        Args:
            audio_file_path: Path to audio file
            config: Optimization configuration
            
        Returns:
            AudioSEOResult with comprehensive optimization
        """
        try:
            # Extract original metadata
            original_metadata = await self._extract_audio_metadata(audio_file_path)
            
            # Analyze audio features
            audio_features = await self._analyze_audio_features(audio_file_path)
            
            # Generate transcript if requested
            transcript = None
            if config.generate_transcript:
                transcript = await self._generate_transcript(audio_file_path, config.language)
            
            # Optimize metadata
            optimized_metadata = await self._optimize_metadata(
                original_metadata, audio_features, config
            )
            
            # Generate SEO content
            seo_title, seo_description = await self._generate_seo_content(
                optimized_metadata, transcript, config
            )
            
            # Extract and optimize keywords
            keywords = await self._extract_keywords(
                optimized_metadata, transcript, audio_features, config
            )
            
            # Generate hashtags
            hashtags = await self._generate_hashtags(keywords, config)
            
            # Platform-specific optimizations
            platform_optimizations = await self._optimize_for_platforms(
                optimized_metadata, seo_title, seo_description, keywords, config
            )
            
            # Generate accessibility features
            accessibility_features = await self._generate_accessibility_features(
                transcript, optimized_metadata, config
            )
            
            # Generate schema markup
            schema_markup = await self._generate_audio_schema_markup(
                optimized_metadata, transcript, config
            )
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(
                original_metadata, optimized_metadata, transcript, config
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                original_metadata, optimized_metadata, config
            )
            
            return AudioSEOResult(
                original_metadata=original_metadata,
                optimized_metadata=optimized_metadata,
                transcript=transcript,
                seo_title=seo_title,
                seo_description=seo_description,
                keywords=keywords,
                hashtags=hashtags,
                platform_optimizations=platform_optimizations,
                accessibility_features=accessibility_features,
                schema_markup=schema_markup,
                optimization_score=optimization_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error optimizing audio SEO: {e}")
            raise
    
    async def _extract_audio_metadata(self, audio_file_path: str) -> AudioMetadata:
        """Extract metadata from audio file."""
        try:
            metadata = AudioMetadata()
            
            # Determine file format
            file_extension = os.path.splitext(audio_file_path)[1].lower()
            format_mapping = {
                '.mp3': AudioFormat.MP3,
                '.flac': AudioFormat.FLAC,
                '.wav': AudioFormat.WAV,
                '.m4a': AudioFormat.M4A,
                '.ogg': AudioFormat.OGG,
                '.aac': AudioFormat.AAC
            }
            metadata.format = format_mapping.get(file_extension, AudioFormat.MP3)
            
            # Extract metadata using mutagen
            try:
                if metadata.format == AudioFormat.MP3:
                    audio_file = MP3(audio_file_path)
                    if audio_file.tags:
                        metadata.title = str(audio_file.tags.get('TIT2', [''])[0])
                        metadata.artist = str(audio_file.tags.get('TPE1', [''])[0])
                        metadata.album = str(audio_file.tags.get('TALB', [''])[0])
                        metadata.genre = str(audio_file.tags.get('TCON', [''])[0])
                        year_tag = audio_file.tags.get('TDRC')
                        if year_tag:
                            try:
                                metadata.year = int(str(year_tag[0])[:4])
                            except:
                                pass
                    
                    metadata.duration = audio_file.info.length
                    metadata.bitrate = audio_file.info.bitrate
                    metadata.sample_rate = audio_file.info.sample_rate
                    metadata.channels = audio_file.info.channels
                
                elif metadata.format == AudioFormat.FLAC:
                    audio_file = FLAC(audio_file_path)
                    if audio_file.tags:
                        metadata.title = audio_file.tags.get('TITLE', [''])[0]
                        metadata.artist = audio_file.tags.get('ARTIST', [''])[0]
                        metadata.album = audio_file.tags.get('ALBUM', [''])[0]
                        metadata.genre = audio_file.tags.get('GENRE', [''])[0]
                        try:
                            metadata.year = int(audio_file.tags.get('DATE', [''])[0][:4])
                        except:
                            pass
                    
                    metadata.duration = audio_file.info.length
                    metadata.bitrate = audio_file.info.bitrate
                    metadata.sample_rate = audio_file.info.sample_rate
                    metadata.channels = audio_file.info.channels
                
                # Get file size
                metadata.file_size = os.path.getsize(audio_file_path)
                
            except Exception as metadata_error:
                logger.warning(f"Error extracting metadata: {metadata_error}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {e}")
            return AudioMetadata()
    
    async def _analyze_audio_features(self, audio_file_path: str) -> Dict[str, Any]:
        """Analyze audio features using librosa."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_file_path, sr=None)
            
            features = {}
            
            # Tempo and rhythm analysis
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_times'] = beats.tolist()
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)
            features['zero_crossing_rate_mean'] = float(np.mean(zcr))
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            
            # Chroma features (for key detection)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            features['onset_times'] = librosa.frames_to_time(onset_frames, sr=sr).tolist()
            
            # Energy and dynamics
            rms = librosa.feature.rms(y=y)[0]
            features['energy_mean'] = float(np.mean(rms))
            features['energy_variance'] = float(np.var(rms))
            
            # Harmonic vs percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            features['harmonic_ratio'] = float(np.mean(np.abs(y_harmonic)) / (np.mean(np.abs(y)) + 1e-8))
            features['percussive_ratio'] = float(np.mean(np.abs(y_percussive)) / (np.mean(np.abs(y)) + 1e-8))
            
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing audio features: {e}")
            return {}
    
    async def _generate_transcript(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> Optional[AudioTranscript]:
        """Generate transcript from audio file."""
        try:
            if not self.speech_recognizer:
                return None
            
            # Convert audio to WAV if needed
            temp_wav_path = None
            try:
                if not audio_file_path.lower().endswith('.wav'):
                    audio = AudioSegment.from_file(audio_file_path)
                    temp_wav_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
                    audio.export(temp_wav_path, format="wav")
                    wav_file_path = temp_wav_path
                else:
                    wav_file_path = audio_file_path
                
                # Recognize speech
                with sr.AudioFile(wav_file_path) as source:
                    audio_data = self.speech_recognizer.record(source)
                
                # Try different recognition engines
                try:
                    text = self.speech_recognizer.recognize_google(audio_data, language=language)
                    confidence = 0.8  # Google Speech-to-Text generally has good confidence
                except sr.UnknownValueError:
                    try:
                        text = self.speech_recognizer.recognize_sphinx(audio_data)
                        confidence = 0.6  # Sphinx typically has lower confidence
                    except:
                        return None
                except sr.RequestError:
                    return None
                
                # Create transcript object
                transcript = AudioTranscript(
                    full_text=text,
                    confidence=confidence,
                    language=language
                )
                
                # Segment transcript (simplified - would use more advanced segmentation in production)
                sentences = text.split('. ')
                segment_duration = 5.0  # Approximate 5 seconds per segment
                
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        segment = {
                            'text': sentence.strip(),
                            'start_time': i * segment_duration,
                            'end_time': (i + 1) * segment_duration,
                            'confidence': confidence
                        }
                        transcript.segments.append(segment)
                
                return transcript
                
            finally:
                # Clean up temporary file
                if temp_wav_path and os.path.exists(temp_wav_path):
                    os.unlink(temp_wav_path)
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return None
    
    async def _optimize_metadata(
        self,
        original_metadata: AudioMetadata,
        audio_features: Dict[str, Any],
        config: AudioSEOConfig
    ) -> AudioMetadata:
        """Optimize audio metadata for SEO."""
        try:
            optimized = AudioMetadata()
            
            # Copy original metadata
            for field in original_metadata.__dataclass_fields__:
                setattr(optimized, field, getattr(original_metadata, field))
            
            # Enhance with audio analysis
            if 'tempo' in audio_features:
                optimized.bpm = audio_features['tempo']
            
            # Determine mood from audio features
            if not optimized.mood:
                optimized.mood = self._classify_mood_from_features(audio_features)
            
            # Determine energy level
            if 'energy_mean' in audio_features:
                energy_normalized = min(audio_features['energy_mean'] * 10, 1.0)
                optimized.energy = energy_normalized
            
            # Classify genre if not present
            if not optimized.genre and config.target_genres:
                optimized.genre = self._classify_genre_from_features(audio_features, config.target_genres)
            
            # Enhance valence (positivity)
            if 'harmonic_ratio' in audio_features:
                optimized.valence = min(audio_features['harmonic_ratio'] * 1.2, 1.0)
            
            # Calculate danceability
            if 'tempo' in audio_features and 'percussive_ratio' in audio_features:
                tempo_factor = 1.0 if 120 <= audio_features['tempo'] <= 140 else 0.5
                optimized.danceability = min(audio_features['percussive_ratio'] * tempo_factor, 1.0)
            
            # Calculate acousticness
            if 'harmonic_ratio' in audio_features:
                optimized.acousticness = min(audio_features['harmonic_ratio'] * 0.8, 1.0)
            
            # Calculate instrumentalness
            if 'spectral_centroid_mean' in audio_features:
                # Higher spectral centroid often indicates more instrumental content
                optimized.instrumentalness = min(audio_features['spectral_centroid_mean'] / 5000, 1.0)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing metadata: {e}")
            return original_metadata
    
    def _classify_mood_from_features(self, features: Dict[str, Any]) -> str:
        """Classify mood from audio features."""
        try:
            # Simple mood classification based on audio features
            energy = features.get('energy_mean', 0.5)
            tempo = features.get('tempo', 120)
            harmonic_ratio = features.get('harmonic_ratio', 0.5)
            
            if energy > 0.7 and tempo > 140:
                return "energetic"
            elif energy > 0.6 and tempo > 120:
                return "upbeat"
            elif harmonic_ratio > 0.6 and tempo < 100:
                return "peaceful"
            elif energy < 0.3 and tempo < 80:
                return "melancholic"
            elif harmonic_ratio > 0.7:
                return "happy"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error classifying mood: {e}")
            return "neutral"
    
    def _classify_genre_from_features(
        self,
        features: Dict[str, Any],
        target_genres: List[str]
    ) -> str:
        """Classify genre from audio features."""
        try:
            # Simple genre classification
            tempo = features.get('tempo', 120)
            percussive_ratio = features.get('percussive_ratio', 0.5)
            harmonic_ratio = features.get('harmonic_ratio', 0.5)
            
            # Electronic/Dance music characteristics
            if percussive_ratio > 0.7 and tempo > 120:
                if "electronic" in target_genres:
                    return "electronic"
                elif "dance" in target_genres:
                    return "dance"
            
            # Rock music characteristics
            if percussive_ratio > 0.6 and 120 <= tempo <= 160:
                if "rock" in target_genres:
                    return "rock"
            
            # Classical music characteristics
            if harmonic_ratio > 0.8 and tempo < 120:
                if "classical" in target_genres:
                    return "classical"
            
            # Jazz characteristics
            if 0.4 < harmonic_ratio < 0.7 and 80 <= tempo <= 140:
                if "jazz" in target_genres:
                    return "jazz"
            
            # Default to first target genre or pop
            if target_genres:
                return target_genres[0]
            else:
                return "pop"
                
        except Exception as e:
            logger.error(f"Error classifying genre: {e}")
            return "pop"
    
    async def _generate_seo_content(
        self,
        metadata: AudioMetadata,
        transcript: Optional[AudioTranscript],
        config: AudioSEOConfig
    ) -> Tuple[str, str]:
        """Generate SEO-optimized title and description."""
        try:
            # Generate title
            title_parts = []
            
            if metadata.title:
                title_parts.append(metadata.title)
            
            if metadata.artist and metadata.artist not in (metadata.title or ""):
                title_parts.append(f"by {metadata.artist}")
            
            if metadata.genre and config.content_type == "music":
                title_parts.append(f"({metadata.genre.title()})")
            
            seo_title = " - ".join(title_parts) if title_parts else "Audio Content"
            
            # Generate description
            description_parts = []
            
            if config.content_type == "music":
                if metadata.artist and metadata.title:
                    description_parts.append(f"Listen to {metadata.title} by {metadata.artist}")
                
                if metadata.genre:
                    description_parts.append(f"A {metadata.genre} track")
                
                if metadata.mood:
                    description_parts.append(f"with a {metadata.mood} mood")
                
                if metadata.bpm:
                    description_parts.append(f"at {int(metadata.bpm)} BPM")
                
                if metadata.album:
                    description_parts.append(f"from the album {metadata.album}")
            
            elif config.content_type == "podcast":
                if metadata.title:
                    description_parts.append(f"Podcast episode: {metadata.title}")
                
                if transcript and len(transcript.full_text) > 50:
                    # Extract key topics from transcript
                    topics = self._extract_topics_from_transcript(transcript.full_text)
                    if topics:
                        description_parts.append(f"Topics covered: {', '.join(topics[:3])}")
            
            # Add transcript summary if available
            if transcript and len(transcript.full_text) > 100:
                summary = transcript.full_text[:200] + "..." if len(transcript.full_text) > 200 else transcript.full_text
                description_parts.append(f"Transcript: {summary}")
            
            seo_description = ". ".join(description_parts) if description_parts else "Quality audio content"
            
            return seo_title, seo_description
            
        except Exception as e:
            logger.error(f"Error generating SEO content: {e}")
            return "Audio Content", "Quality audio content"
    
    def _extract_topics_from_transcript(self, transcript_text: str) -> List[str]:
        """Extract key topics from transcript text."""
        try:
            # Simple keyword extraction (would use more advanced NLP in production)
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', transcript_text)
            
            # Filter common words
            stop_words = {'The', 'This', 'That', 'They', 'There', 'Then', 'When', 'Where', 'What', 'Who', 'Why', 'How'}
            topics = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Return most frequent topics
            from collections import Counter
            topic_counts = Counter(topics)
            return [topic for topic, count in topic_counts.most_common(5)]
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    async def _extract_keywords(
        self,
        metadata: AudioMetadata,
        transcript: Optional[AudioTranscript],
        audio_features: Dict[str, Any],
        config: AudioSEOConfig
    ) -> List[str]:
        """Extract SEO keywords from audio content."""
        try:
            keywords = set()
            
            # Metadata-based keywords
            if metadata.genre:
                keywords.add(metadata.genre.lower())
                keywords.add(f"{metadata.genre.lower()} music")
            
            if metadata.artist:
                keywords.add(metadata.artist.lower())
                keywords.add(f"{metadata.artist.lower()} songs")
            
            if metadata.mood:
                keywords.add(metadata.mood.lower())
                keywords.add(f"{metadata.mood.lower()} music")
            
            # Content type keywords
            if config.content_type == "music":
                keywords.update(["song", "track", "music", "audio"])
                
                if metadata.bpm:
                    if metadata.bpm > 140:
                        keywords.update(["high energy", "fast", "dance"])
                    elif metadata.bpm < 80:
                        keywords.update(["slow", "relaxing", "chill"])
                    else:
                        keywords.update(["medium tempo", "moderate"])
            
            elif config.content_type == "podcast":
                keywords.update(["podcast", "episode", "interview", "discussion"])
            
            elif config.content_type == "audiobook":
                keywords.update(["audiobook", "narration", "story", "book"])
            
            # Transcript-based keywords
            if transcript and transcript.full_text:
                # Extract important words from transcript
                transcript_keywords = self._extract_keywords_from_text(transcript.full_text)
                keywords.update(transcript_keywords)
            
            # Platform-specific keywords
            for platform in config.target_platforms:
                platform_focus = self.platform_requirements.get(platform, {}).get('keywords_focus', [])
                keywords.update(platform_focus)
            
            # Audio feature keywords
            if audio_features.get('energy_mean', 0) > 0.7:
                keywords.update(["energetic", "powerful", "intense"])
            elif audio_features.get('energy_mean', 0) < 0.3:
                keywords.update(["calm", "peaceful", "gentle"])
            
            return list(keywords)[:20]  # Limit to top 20 keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text content."""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Filter stop words
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'can', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'when',
                'where', 'why', 'how', 'not', 'no', 'yes', 'very', 'really', 'quite'
            }
            
            keywords = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Return most frequent keywords
            from collections import Counter
            keyword_counts = Counter(keywords)
            return [keyword for keyword, count in keyword_counts.most_common(10)]
            
        except Exception as e:
            logger.error(f"Error extracting keywords from text: {e}")
            return []
    
    async def _generate_hashtags(
        self,
        keywords: List[str],
        config: AudioSEOConfig
    ) -> List[str]:
        """Generate hashtags from keywords."""
        try:
            hashtags = []
            
            # Convert keywords to hashtags
            for keyword in keywords[:15]:  # Limit to 15 hashtags
                # Clean keyword for hashtag
                hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword)
                if len(hashtag) > 2:
                    hashtags.append(f"#{hashtag}")
            
            # Add content type hashtags
            if config.content_type == "music":
                hashtags.extend(["#music", "#newmusic", "#song", "#artist"])
            elif config.content_type == "podcast":
                hashtags.extend(["#podcast", "#podcasting", "#interview"])
            
            # Add platform-specific hashtags
            if "spotify" in config.target_platforms:
                hashtags.append("#spotify")
            if "youtube" in config.target_platforms:
                hashtags.append("#youtube")
            if "soundcloud" in config.target_platforms:
                hashtags.append("#soundcloud")
            
            return hashtags[:20]  # Limit to 20 hashtags
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {e}")
            return []
    
    async def _optimize_for_platforms(
        self,
        metadata: AudioMetadata,
        title: str,
        description: str,
        keywords: List[str],
        config: AudioSEOConfig
    ) -> Dict[str, Dict[str, Any]]:
        """Optimize content for specific platforms."""
        try:
            optimizations = {}
            
            for platform in config.target_platforms:
                platform_req = self.platform_requirements.get(platform, {})
                
                # Optimize title length
                max_title_length = platform_req.get('title_max_length', 100)
                optimized_title = title[:max_title_length] if len(title) > max_title_length else title
                
                # Optimize description length
                max_desc_length = platform_req.get('description_max_length', 1000)
                optimized_desc = description[:max_desc_length] if len(description) > max_desc_length else description
                
                # Platform-specific keyword focus
                platform_keywords = [kw for kw in keywords if any(focus in kw for focus in platform_req.get('keywords_focus', []))]
                
                # Quality recommendations
                quality_req = platform_req.get('min_quality', {})
                quality_status = "optimal"
                
                if metadata.bitrate and metadata.bitrate < quality_req.get('bitrate', 128):
                    quality_status = "below_recommended"
                
                if metadata.sample_rate and metadata.sample_rate < quality_req.get('sample_rate', 44100):
                    quality_status = "below_recommended"
                
                optimizations[platform] = {
                    'optimized_title': optimized_title,
                    'optimized_description': optimized_desc,
                    'focused_keywords': platform_keywords,
                    'quality_status': quality_status,
                    'recommended_format': platform_req.get('preferred_formats', [AudioFormat.MP3])[0].value,
                    'metadata_completeness': self._check_metadata_completeness(metadata, platform_req.get('required_metadata', []))
                }
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error optimizing for platforms: {e}")
            return {}
    
    def _check_metadata_completeness(self, metadata: AudioMetadata, required_fields: List[str]) -> float:
        """Check completeness of metadata against required fields."""
        try:
            total_fields = len(required_fields)
            if total_fields == 0:
                return 1.0
            
            present_fields = 0
            for field in required_fields:
                if hasattr(metadata, field) and getattr(metadata, field):
                    present_fields += 1
            
            return present_fields / total_fields
            
        except Exception as e:
            logger.error(f"Error checking metadata completeness: {e}")
            return 0.0
    
    async def _generate_accessibility_features(
        self,
        transcript: Optional[AudioTranscript],
        metadata: AudioMetadata,
        config: AudioSEOConfig
    ) -> Dict[str, Any]:
        """Generate accessibility features for audio content."""
        try:
            accessibility = {}
            
            # Transcript availability
            accessibility['has_transcript'] = transcript is not None
            
            if transcript:
                accessibility['transcript_quality'] = transcript.confidence
                accessibility['transcript_language'] = transcript.language
                accessibility['word_count'] = len(transcript.full_text.split())
                
                # Generate audio description
                if config.content_type == "music":
                    description = f"A {metadata.genre or 'musical'} track"
                    if metadata.bpm:
                        description += f" with a tempo of {int(metadata.bpm)} beats per minute"
                    if metadata.mood:
                        description += f" and a {metadata.mood} mood"
                    accessibility['audio_description'] = description
                
                # Time-coded captions
                if transcript.segments:
                    accessibility['has_captions'] = True
                    accessibility['caption_format'] = "SRT"  # Suggested format
            
            # Content warnings if applicable
            if self.emotion_classifier and transcript:
                try:
                    emotions = self.emotion_classifier(transcript.full_text[:512])
                    dominant_emotion = emotions[0]['label'] if emotions else 'neutral'
                    
                    if dominant_emotion in ['anger', 'fear', 'sadness']:
                        accessibility['content_warning'] = f"Content may contain {dominant_emotion}-related themes"
                except:
                    pass
            
            # Hearing accessibility
            accessibility['hearing_accessible'] = {
                'transcript_available': transcript is not None,
                'visual_cues_described': config.content_type != "music",  # Music doesn't need visual cues
                'speaker_identification': transcript and len(transcript.speaker_labels) > 0 if transcript else False
            }
            
            return accessibility
            
        except Exception as e:
            logger.error(f"Error generating accessibility features: {e}")
            return {}
    
    async def _generate_audio_schema_markup(
        self,
        metadata: AudioMetadata,
        transcript: Optional[AudioTranscript],
        config: AudioSEOConfig
    ) -> Dict[str, Any]:
        """Generate schema.org markup for audio content."""
        try:
            schema = {
                "@context": "https://schema.org",
                "@type": "AudioObject"
            }
            
            # Basic properties
            if metadata.title:
                schema["name"] = metadata.title
            
            if metadata.artist:
                schema["creator"] = {
                    "@type": "Person" if config.content_type == "music" else "Organization",
                    "name": metadata.artist
                }
            
            if metadata.duration:
                # Convert to ISO 8601 duration format
                duration_seconds = int(metadata.duration)
                hours = duration_seconds // 3600
                minutes = (duration_seconds % 3600) // 60
                seconds = duration_seconds % 60
                
                if hours > 0:
                    schema["duration"] = f"PT{hours}H{minutes}M{seconds}S"
                else:
                    schema["duration"] = f"PT{minutes}M{seconds}S"
            
            # Content type specific schema
            if config.content_type == "music":
                schema["@type"] = "MusicRecording"
                
                if metadata.album:
                    schema["inAlbum"] = {
                        "@type": "MusicAlbum",
                        "name": metadata.album
                    }
                
                if metadata.genre:
                    schema["genre"] = metadata.genre
                
                if metadata.year:
                    schema["datePublished"] = str(metadata.year)
            
            elif config.content_type == "podcast":
                schema["@type"] = "PodcastEpisode"
                
                if transcript:
                    schema["transcript"] = {
                        "@type": "MediaObject",
                        "encodingFormat": "text/plain",
                        "text": transcript.full_text
                    }
            
            # Technical properties
            if metadata.format:
                schema["encodingFormat"] = f"audio/{metadata.format.value}"
            
            if metadata.bitrate:
                schema["bitrate"] = f"{metadata.bitrate}k"
            
            # Accessibility
            if transcript:
                schema["accessibilityFeature"] = ["transcript", "captions"]
                schema["accessibilityHazard"] = "none"
                schema["accessibilityControl"] = ["fullKeyboardControl", "fullMouseControl"]
            
            return schema
            
        except Exception as e:
            logger.error(f"Error generating audio schema markup: {e}")
            return {}
    
    def _calculate_optimization_score(
        self,
        original_metadata: AudioMetadata,
        optimized_metadata: AudioMetadata,
        transcript: Optional[AudioTranscript],
        config: AudioSEOConfig
    ) -> float:
        """Calculate overall optimization score."""
        try:
            score_components = []
            
            # Metadata completeness (0-1)
            metadata_fields = ['title', 'artist', 'genre', 'duration']
            present_fields = sum(1 for field in metadata_fields if getattr(optimized_metadata, field))
            metadata_score = present_fields / len(metadata_fields)
            score_components.append(metadata_score * 0.3)
            
            # Transcript availability (0-1)
            transcript_score = 1.0 if transcript and transcript.confidence > 0.5 else 0.0
            score_components.append(transcript_score * 0.2)
            
            # Audio quality (0-1)
            quality_score = 0.5  # Base score
            if optimized_metadata.bitrate and optimized_metadata.bitrate >= 256:
                quality_score += 0.3
            if optimized_metadata.sample_rate and optimized_metadata.sample_rate >= 44100:
                quality_score += 0.2
            score_components.append(min(quality_score, 1.0) * 0.2)
            
            # Feature richness (0-1)
            feature_fields = ['bpm', 'mood', 'energy', 'valence']
            present_features = sum(1 for field in feature_fields if getattr(optimized_metadata, field))
            feature_score = present_features / len(feature_fields)
            score_components.append(feature_score * 0.2)
            
            # Platform optimization (0-1)
            platform_score = len(config.target_platforms) / 4  # Normalize to 4 platforms max
            score_components.append(min(platform_score, 1.0) * 0.1)
            
            return sum(score_components)
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return 0.0
    
    def _generate_recommendations(
        self,
        original_metadata: AudioMetadata,
        optimized_metadata: AudioMetadata,
        config: AudioSEOConfig
    ) -> List[str]:
        """Generate optimization recommendations."""
        try:
            recommendations = []
            
            # Metadata recommendations
            if not optimized_metadata.title:
                recommendations.append("Add a descriptive title to improve discoverability")
            
            if not optimized_metadata.artist:
                recommendations.append("Specify the artist/creator name for better attribution")
            
            if not optimized_metadata.genre:
                recommendations.append("Add genre information to help with categorization")
            
            # Quality recommendations
            if optimized_metadata.bitrate and optimized_metadata.bitrate < 256:
                recommendations.append(f"Consider increasing bitrate to 256+ kbps (current: {optimized_metadata.bitrate} kbps)")
            
            if optimized_metadata.sample_rate and optimized_metadata.sample_rate < 44100:
                recommendations.append(f"Consider using 44.1 kHz sample rate for better quality (current: {optimized_metadata.sample_rate} Hz)")
            
            # Content recommendations
            if config.generate_transcript and not config.content_type == "music":
                recommendations.append("Generate transcript for better accessibility and SEO")
            
            if config.content_type == "music" and not optimized_metadata.bpm:
                recommendations.append("Add BPM information for better music discovery")
            
            # Platform recommendations
            missing_platforms = {'spotify', 'apple_music', 'youtube', 'soundcloud'} - set(config.target_platforms)
            if missing_platforms:
                recommendations.append(f"Consider optimizing for additional platforms: {', '.join(missing_platforms)}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    async def batch_optimize_audio(
        self,
        audio_files: List[str],
        configs: List[AudioSEOConfig]
    ) -> List[AudioSEOResult]:
        """Optimize multiple audio files in batch."""
        try:
            tasks = [
                self.optimize_audio_seo(audio_file, config)
                for audio_file, config in zip(audio_files, configs)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log them
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error optimizing audio {i}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch audio optimization: {e}")
            return []