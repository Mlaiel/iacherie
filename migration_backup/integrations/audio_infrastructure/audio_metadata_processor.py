"""🏷️ Enterprise Audio Metadata Processor - Advanced Tag Management
==============================================================

Processeur de métadonnées audio enterprise avec gestion avancée des tags,
extraction automatique et enrichissement IA pour Ainflue.

Expert Roles Implementation:
🎵 Audio Engineer: Standards métadonnées + formats audio + tag preservation
🏗️ Backend Senior: Base de données métadonnées + indexation + API management
🤖 Lead Dev IA: Auto-tagging IA + enrichissement contenu + ML classification
🧠 ML Engineer: Modèles reconnaissance + extraction features + content analysis
🔒 Sécurité: Métadonnées privacy + sanitization + secure tag processing
⚙️ DevOps: Pipeline métadonnées + batch processing + automation
🔗 Microservices: Services métadonnées + API enrichissement + integration
⚡ Performance: Processing rapide + cache métadonnées + optimisation mémoire

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Enterprise Production
Date: 16 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture de traitement métadonnées audio est la propriété intellectuelle EXCLUSIVE de
Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
import numpy as np
import librosa
import soundfile as sf
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, TRCK, TPE2, TXXX, APIC
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
import aiofiles
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import aiohttp
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetadataStandard(Enum):
    """Standards de métadonnées"""
    ID3V2 = "id3v2"  # MP3
    VORBIS_COMMENT = "vorbis"  # OGG, FLAC
    MP4_METADATA = "mp4"  # AAC, M4A
    APE = "ape"  # APE, WavPack
    RIFF_INFO = "riff"  # WAV
    BWF = "bwf"  # Broadcast Wave Format
    CUSTOM = "custom"

class TagType(Enum):
    """Types de tags métadonnées"""
    # Tags standards
    TITLE = "title"
    ARTIST = "artist"
    ALBUM = "album"
    ALBUM_ARTIST = "albumartist"
    DATE = "date"
    YEAR = "year"
    GENRE = "genre"
    TRACK_NUMBER = "tracknumber"
    TRACK_TOTAL = "tracktotal"
    DISC_NUMBER = "discnumber"
    DISC_TOTAL = "disctotal"
    
    # Tags étendus
    COMPOSER = "composer"
    CONDUCTOR = "conductor"
    LYRICIST = "lyricist"
    PRODUCER = "producer"
    ENGINEER = "engineer"
    MIXER = "mixer"
    MASTERED_BY = "masteredby"
    
    # Tags techniques
    ENCODER = "encoder"
    ENCODING_SETTINGS = "encodingsettings"
    BPM = "bpm"
    KEY = "key"
    MOOD = "mood"
    ENERGY = "energy"
    DANCEABILITY = "danceability"
    
    # Tags business
    ISRC = "isrc"
    CATALOG_NUMBER = "catalognumber"
    BARCODE = "barcode"
    COPYRIGHT = "copyright"
    PUBLISHER = "publisher"
    LABEL = "label"
    LICENSE = "license"
    
    # Tags Ainflue spécifiques
    CREATOR_ID = "ainflue_creator_id"
    CONTENT_TYPE = "ainflue_content_type"
    PROTECTION_LEVEL = "ainflue_protection"
    COLLABORATION_INFO = "ainflue_collaboration"
    MONETIZATION = "ainflue_monetization"
    
    # Tags techniques étendus
    LOUDNESS_LUFS = "loudness_lufs"
    TRUE_PEAK = "true_peak"
    DYNAMIC_RANGE = "dynamic_range"
    AUDIO_FINGERPRINT = "audio_fingerprint"

class ImageType(Enum):
    """Types d'images"""
    COVER_FRONT = "cover_front"
    COVER_BACK = "cover_back"
    LEAFLET = "leaflet"
    MEDIA = "media"
    ARTIST = "artist"
    CONDUCTOR = "conductor"
    BAND = "band"
    COMPOSER = "composer"
    LYRICIST = "lyricist"
    RECORDING_LOCATION = "recording_location"
    DURING_RECORDING = "during_recording"
    DURING_PERFORMANCE = "during_performance"
    VIDEO_CAPTURE = "video_capture"
    OTHER = "other"

@dataclass
class AudioImage:
    """Image associée à l'audio"""
    image_type: ImageType
    data: bytes
    mime_type: str
    description: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    color_depth: Optional[int] = None
    indexed_colors: Optional[int] = None

@dataclass
class AudioMetadata:
    """Métadonnées audio complètes"""
    # Informations de base
    tags: Dict[TagType, Any] = field(default_factory=dict)
    images: List[AudioImage] = field(default_factory=list)
    
    # Métadonnées techniques
    technical_info: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées calculées
    computed_tags: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées d'enrichissement
    enriched_tags: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées de traçabilité
    processing_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timestamp de création/modification
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    # Standard source
    source_standard: Optional[MetadataStandard] = None

@dataclass
class MetadataProcessingConfig:
    """Configuration du traitement des métadonnées"""
    preserve_original: bool = True
    auto_detect_encoding: bool = True
    sanitize_tags: bool = True
    extract_images: bool = True
    compress_images: bool = False
    max_image_size: int = 1024 * 1024  # 1MB
    enable_ai_enrichment: bool = True
    enable_audio_analysis: bool = True
    enable_lyrics_extraction: bool = True
    custom_tag_mapping: Dict[str, TagType] = field(default_factory=dict)

class MetadataExtractor:
    """Extracteur de métadonnées pour différents formats"""
    
    def __init__(self):
        self.supported_formats = {
            '.mp3': self._extract_mp3_metadata,
            '.flac': self._extract_flac_metadata,
            '.m4a': self._extract_mp4_metadata,
            '.mp4': self._extract_mp4_metadata,
            '.ogg': self._extract_ogg_metadata,
            '.wav': self._extract_wav_metadata,
            '.wv': self._extract_wavpack_metadata,
            '.ape': self._extract_ape_metadata
        }
    
    async def extract_metadata(
        self,
        file_path: str,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées d'un fichier audio"""
        
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Extraire avec mutagen
        mutagen_file = MutagenFile(file_path)
        if mutagen_file is None:
            raise ValueError(f"Could not read metadata from: {file_path}")
        
        # Utiliser l'extracteur spécifique
        extractor = self.supported_formats[file_extension]
        metadata = await extractor(mutagen_file, config)
        
        # Ajouter les informations techniques de base
        await self._add_technical_info(metadata, file_path, mutagen_file)
        
        # Analyser l'audio si activé
        if config.enable_audio_analysis:
            await self._add_audio_analysis(metadata, file_path)
        
        return metadata
    
    async def _extract_mp3_metadata(
        self,
        mutagen_file,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées MP3 (ID3)"""
        metadata = AudioMetadata(source_standard=MetadataStandard.ID3V2)
        
        # Tags ID3 standards
        tag_mapping = {
            'TIT2': TagType.TITLE,
            'TPE1': TagType.ARTIST,
            'TALB': TagType.ALBUM,
            'TPE2': TagType.ALBUM_ARTIST,
            'TDRC': TagType.DATE,
            'TCON': TagType.GENRE,
            'TRCK': TagType.TRACK_NUMBER,
            'TPOS': TagType.DISC_NUMBER,
            'TCOM': TagType.COMPOSER,
            'TPUB': TagType.PUBLISHER,
            'TCOP': TagType.COPYRIGHT,
            'TENC': TagType.ENCODER,
            'TBPM': TagType.BPM,
            'TKEY': TagType.KEY,
            'TSRC': TagType.ISRC
        }
        
        # Extraire les tags standards
        for id3_tag, tag_type in tag_mapping.items():
            if id3_tag in mutagen_file:
                value = str(mutagen_file[id3_tag][0])
                if config.sanitize_tags:
                    value = self._sanitize_tag_value(value)
                metadata.tags[tag_type] = value
        
        # Traiter les tags TXXX (user-defined)
        for tag in mutagen_file.values():
            if hasattr(tag, 'desc') and tag.desc:
                desc = tag.desc.lower()
                if desc in config.custom_tag_mapping:
                    tag_type = config.custom_tag_mapping[desc]
                    value = str(tag.text[0]) if tag.text else ""
                    if config.sanitize_tags:
                        value = self._sanitize_tag_value(value)
                    metadata.tags[tag_type] = value
        
        # Extraire les images (APIC frames)
        if config.extract_images:
            await self._extract_id3_images(mutagen_file, metadata, config)
        
        return metadata
    
    async def _extract_flac_metadata(
        self,
        mutagen_file: FLAC,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées FLAC (Vorbis Comments)"""
        metadata = AudioMetadata(source_standard=MetadataStandard.VORBIS_COMMENT)
        
        # Tags Vorbis standards
        tag_mapping = {
            'TITLE': TagType.TITLE,
            'ARTIST': TagType.ARTIST,
            'ALBUM': TagType.ALBUM,
            'ALBUMARTIST': TagType.ALBUM_ARTIST,
            'DATE': TagType.DATE,
            'GENRE': TagType.GENRE,
            'TRACKNUMBER': TagType.TRACK_NUMBER,
            'TRACKTOTAL': TagType.TRACK_TOTAL,
            'DISCNUMBER': TagType.DISC_NUMBER,
            'DISCTOTAL': TagType.DISC_TOTAL,
            'COMPOSER': TagType.COMPOSER,
            'PERFORMER': TagType.ARTIST,
            'COPYRIGHT': TagType.COPYRIGHT,
            'ENCODER': TagType.ENCODER,
            'BPM': TagType.BPM,
            'ISRC': TagType.ISRC
        }
        
        # Extraire les tags
        for vorbis_tag, tag_type in tag_mapping.items():
            if vorbis_tag in mutagen_file:
                value = mutagen_file[vorbis_tag][0]
                if config.sanitize_tags:
                    value = self._sanitize_tag_value(value)
                metadata.tags[tag_type] = value
        
        # Extraire les images des blocs FLAC
        if config.extract_images and hasattr(mutagen_file, 'pictures'):
            await self._extract_flac_images(mutagen_file, metadata, config)
        
        return metadata
    
    async def _extract_mp4_metadata(
        self,
        mutagen_file: MP4,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées MP4/M4A"""
        metadata = AudioMetadata(source_standard=MetadataStandard.MP4_METADATA)
        
        # Tags MP4 standards
        tag_mapping = {
            '\xa9nam': TagType.TITLE,
            '\xa9ART': TagType.ARTIST,
            '\xa9alb': TagType.ALBUM,
            'aART': TagType.ALBUM_ARTIST,
            '\xa9day': TagType.DATE,
            '\xa9gen': TagType.GENRE,
            'trkn': TagType.TRACK_NUMBER,
            'disk': TagType.DISC_NUMBER,
            '\xa9wrt': TagType.COMPOSER,
            '\xa9cpy': TagType.COPYRIGHT,
            '\xa9too': TagType.ENCODER,
            'tmpo': TagType.BPM
        }
        
        # Extraire les tags
        for mp4_tag, tag_type in tag_mapping.items():
            if mp4_tag in mutagen_file:
                value = mutagen_file[mp4_tag][0]
                # Traitement spécial pour certains tags
                if mp4_tag in ['trkn', 'disk']:
                    if isinstance(value, tuple):
                        value = f"{value[0]}/{value[1]}" if len(value) > 1 and value[1] else str(value[0])
                if config.sanitize_tags:
                    value = self._sanitize_tag_value(str(value))
                metadata.tags[tag_type] = value
        
        # Extraire les images (covr)
        if config.extract_images and 'covr' in mutagen_file:
            await self._extract_mp4_images(mutagen_file, metadata, config)
        
        return metadata
    
    async def _extract_ogg_metadata(
        self,
        mutagen_file: OggVorbis,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées OGG Vorbis"""
        # Même méthode que FLAC car utilise Vorbis Comments
        return await self._extract_flac_metadata(mutagen_file, config)
    
    async def _extract_wav_metadata(
        self,
        mutagen_file,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées WAV (RIFF INFO)"""
        metadata = AudioMetadata(source_standard=MetadataStandard.RIFF_INFO)
        
        # WAV peut contenir des tags ID3 ou RIFF INFO
        if hasattr(mutagen_file, 'tags') and mutagen_file.tags:
            # Déléguer à l'extracteur ID3 si présent
            return await self._extract_mp3_metadata(mutagen_file.tags, config)
        
        return metadata
    
    async def _extract_wavpack_metadata(
        self,
        mutagen_file,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées WavPack (APE tags)"""
        metadata = AudioMetadata(source_standard=MetadataStandard.APE)
        
        # Tags APE similaires aux Vorbis Comments
        ape_tag_mapping = {
            'Title': TagType.TITLE,
            'Artist': TagType.ARTIST,
            'Album': TagType.ALBUM,
            'AlbumArtist': TagType.ALBUM_ARTIST,
            'Year': TagType.YEAR,
            'Genre': TagType.GENRE,
            'Track': TagType.TRACK_NUMBER,
            'Composer': TagType.COMPOSER,
            'Copyright': TagType.COPYRIGHT,
            'Encoder': TagType.ENCODER
        }
        
        for ape_tag, tag_type in ape_tag_mapping.items():
            if ape_tag in mutagen_file:
                value = str(mutagen_file[ape_tag][0])
                if config.sanitize_tags:
                    value = self._sanitize_tag_value(value)
                metadata.tags[tag_type] = value
        
        return metadata
    
    async def _extract_ape_metadata(
        self,
        mutagen_file,
        config: MetadataProcessingConfig
    ) -> AudioMetadata:
        """Extrait les métadonnées APE (Monkey's Audio)"""
        return await self._extract_wavpack_metadata(mutagen_file, config)
    
    async def _extract_id3_images(
        self,
        mutagen_file,
        metadata: AudioMetadata,
        config: MetadataProcessingConfig
    ):
        """Extrait les images ID3 (APIC frames)"""
        for tag in mutagen_file.values():
            if hasattr(tag, 'type') and hasattr(tag, 'data'):  # APIC frame
                try:
                    # Déterminer le type d'image
                    image_type = self._map_id3_image_type(tag.type)
                    
                    # Traiter l'image
                    processed_data = await self._process_image(
                        tag.data, tag.mime, config
                    )
                    
                    if processed_data:
                        # Obtenir les dimensions de l'image
                        width, height = await self._get_image_dimensions(processed_data)
                        
                        image = AudioImage(
                            image_type=image_type,
                            data=processed_data,
                            mime_type=tag.mime,
                            description=getattr(tag, 'desc', ''),
                            width=width,
                            height=height
                        )
                        metadata.images.append(image)
                        
                except Exception as e:
                    logger.warning(f"Failed to extract ID3 image: {e}")
    
    async def _extract_flac_images(
        self,
        mutagen_file: FLAC,
        metadata: AudioMetadata,
        config: MetadataProcessingConfig
    ):
        """Extrait les images FLAC"""
        for picture in mutagen_file.pictures:
            try:
                # Mapper le type d'image
                image_type = self._map_flac_image_type(picture.type)
                
                # Traiter l'image
                processed_data = await self._process_image(
                    picture.data, picture.mime, config
                )
                
                if processed_data:
                    image = AudioImage(
                        image_type=image_type,
                        data=processed_data,
                        mime_type=picture.mime,
                        description=picture.desc,
                        width=picture.width,
                        height=picture.height,
                        color_depth=picture.depth,
                        indexed_colors=picture.colors
                    )
                    metadata.images.append(image)
                    
            except Exception as e:
                logger.warning(f"Failed to extract FLAC image: {e}")
    
    async def _extract_mp4_images(
        self,
        mutagen_file: MP4,
        metadata: AudioMetadata,
        config: MetadataProcessingConfig
    ):
        """Extrait les images MP4"""
        for cover_data in mutagen_file['covr']:
            try:
                # Déterminer le type MIME
                if cover_data.imageformat == MP4.AtomDataType.JPEG:
                    mime_type = 'image/jpeg'
                elif cover_data.imageformat == MP4.AtomDataType.PNG:
                    mime_type = 'image/png'
                else:
                    mime_type = 'image/unknown'
                
                # Traiter l'image
                processed_data = await self._process_image(
                    bytes(cover_data), mime_type, config
                )
                
                if processed_data:
                    width, height = await self._get_image_dimensions(processed_data)
                    
                    image = AudioImage(
                        image_type=ImageType.COVER_FRONT,  # MP4 ne spécifie pas le type
                        data=processed_data,
                        mime_type=mime_type,
                        width=width,
                        height=height
                    )
                    metadata.images.append(image)
                    
            except Exception as e:
                logger.warning(f"Failed to extract MP4 image: {e}")
    
    async def _process_image(
        self,
        image_data: bytes,
        mime_type: str,
        config: MetadataProcessingConfig
    ) -> Optional[bytes]:
        """Traite une image (compression, redimensionnement)"""
        
        if len(image_data) > config.max_image_size:
            if not config.compress_images:
                logger.warning(f"Image too large ({len(image_data)} bytes), skipping")
                return None
            
            # Compresser l'image
            try:
                image = Image.open(io.BytesIO(image_data))
                
                # Calculer la nouvelle taille
                max_dimension = 1024  # pixels
                if max(image.size) > max_dimension:
                    ratio = max_dimension / max(image.size)
                    new_size = tuple(int(dim * ratio) for dim in image.size)
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Sauvegarder avec compression
                output = io.BytesIO()
                format_name = 'JPEG' if 'jpeg' in mime_type.lower() else 'PNG'
                
                if format_name == 'JPEG':
                    if image.mode in ['RGBA', 'LA', 'P']:
                        image = image.convert('RGB')
                    image.save(output, format=format_name, quality=85, optimize=True)
                else:
                    image.save(output, format=format_name, optimize=True)
                
                compressed_data = output.getvalue()
                
                if len(compressed_data) <= config.max_image_size:
                    return compressed_data
                else:
                    logger.warning("Image still too large after compression, skipping")
                    return None
                    
            except Exception as e:
                logger.warning(f"Image compression failed: {e}")
                return None
        
        return image_data
    
    async def _get_image_dimensions(self, image_data: bytes) -> tuple[Optional[int], Optional[int]]:
        """Obtient les dimensions d'une image"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return image.size
        except Exception:
            return None, None
    
    def _map_id3_image_type(self, id3_type: int) -> ImageType:
        """Mappe les types d'images ID3 vers notre enum"""
        mapping = {
            0: ImageType.OTHER,
            3: ImageType.COVER_FRONT,
            4: ImageType.COVER_BACK,
            5: ImageType.LEAFLET,
            6: ImageType.MEDIA,
            8: ImageType.ARTIST,
            9: ImageType.CONDUCTOR,
            10: ImageType.BAND,
            11: ImageType.COMPOSER,
            12: ImageType.LYRICIST,
            13: ImageType.RECORDING_LOCATION,
            14: ImageType.DURING_RECORDING,
            15: ImageType.DURING_PERFORMANCE,
            16: ImageType.VIDEO_CAPTURE
        }
        return mapping.get(id3_type, ImageType.OTHER)
    
    def _map_flac_image_type(self, flac_type: int) -> ImageType:
        """Mappe les types d'images FLAC vers notre enum"""
        # FLAC utilise le même système que ID3v2
        return self._map_id3_image_type(flac_type)
    
    def _sanitize_tag_value(self, value: str) -> str:
        """Nettoie et valide une valeur de tag"""
        if not isinstance(value, str):
            value = str(value)
        
        # Supprimer les caractères de contrôle
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        
        # Limiter la longueur
        max_length = 1000
        if len(value) > max_length:
            value = value[:max_length]
        
        # Nettoyer les espaces
        value = value.strip()
        
        return value
    
    async def _add_technical_info(
        self,
        metadata: AudioMetadata,
        file_path: str,
        mutagen_file
    ):
        """Ajoute les informations techniques"""
        file_stat = Path(file_path).stat()
        
        metadata.technical_info.update({
            'file_size': file_stat.st_size,
            'file_modified': datetime.fromtimestamp(file_stat.st_mtime),
            'file_format': Path(file_path).suffix.lower(),
            'duration': getattr(mutagen_file.info, 'length', 0),
            'bitrate': getattr(mutagen_file.info, 'bitrate', 0),
            'sample_rate': getattr(mutagen_file.info, 'sample_rate', 0),
            'channels': getattr(mutagen_file.info, 'channels', 0),
            'bits_per_sample': getattr(mutagen_file.info, 'bits_per_sample', 0)
        })
    
    async def _add_audio_analysis(
        self,
        metadata: AudioMetadata,
        file_path: str
    ):
        """Ajoute l'analyse audio automatique"""
        try:
            # Charger l'audio pour analyse
            audio, sample_rate = librosa.load(file_path, duration=60)  # Analyser 60s max
            
            # Analyse tempo/BPM
            tempo, _ = librosa.beat.tempo(y=audio, sr=sample_rate)
            metadata.computed_tags['computed_bpm'] = float(tempo)
            
            # Analyse tonalité
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            key_profile = np.mean(chroma, axis=1)
            estimated_key = np.argmax(key_profile)
            
            # Mapping des clés
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            metadata.computed_tags['computed_key'] = keys[estimated_key]
            
            # Analyse loudness
            rms = librosa.feature.rms(y=audio)[0]
            metadata.computed_tags['computed_loudness'] = float(np.mean(rms))
            
            # Caractéristiques spectrales
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            metadata.computed_tags['spectral_centroid'] = float(np.mean(spectral_centroids))
            
            zero_crossings = librosa.zero_crossings(audio, pad=False)
            metadata.computed_tags['zero_crossing_rate'] = float(np.mean(zero_crossings))
            
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")

class MetadataEnricher:
    """Enrichisseur de métadonnées avec IA et services externes"""
    
    def __init__(self):
        self.musicbrainz_api = "https://musicbrainz.org/ws/2"
        self.acoustid_api = "https://api.acoustid.org/v2"
        self.lastfm_api = "http://ws.audioscrobbler.com/2.0"
        
        # Cache pour éviter les requêtes répétées
        self.cache = {}
    
    async def enrich_metadata(
        self,
        metadata: AudioMetadata,
        audio_file_path: Optional[str] = None
    ) -> AudioMetadata:
        """Enrichit les métadonnées avec des services externes"""
        
        enriched = metadata
        
        # Enrichissement par reconnaissance audio
        if audio_file_path:
            await self._enrich_with_audio_fingerprint(enriched, audio_file_path)
        
        # Enrichissement par recherche textuelle
        await self._enrich_with_text_search(enriched)
        
        # Enrichissement par IA
        await self._enrich_with_ai_analysis(enriched, audio_file_path)
        
        return enriched
    
    async def _enrich_with_audio_fingerprint(
        self,
        metadata: AudioMetadata,
        audio_file_path: str
    ):
        """Enrichit via fingerprinting audio (AcoustID/MusicBrainz)"""
        try:
            # Générer le fingerprint acoustique
            fingerprint = await self._generate_acoustic_fingerprint(audio_file_path)
            
            if fingerprint:
                # Rechercher dans AcoustID
                results = await self._query_acoustid(fingerprint)
                
                if results and 'results' in results:
                    for result in results['results'][:3]:  # Top 3 résultats
                        if 'recordings' in result:
                            recording = result['recordings'][0]
                            
                            # Enrichir avec les données trouvées
                            if 'title' in recording:
                                metadata.enriched_tags['acoustid_title'] = recording['title']
                            
                            if 'artists' in recording and recording['artists']:
                                metadata.enriched_tags['acoustid_artist'] = recording['artists'][0]['name']
                            
                            if 'releases' in recording and recording['releases']:
                                release = recording['releases'][0]
                                metadata.enriched_tags['acoustid_album'] = release.get('title', '')
                            
                            break
                            
        except Exception as e:
            logger.warning(f"Audio fingerprint enrichment failed: {e}")
    
    async def _enrich_with_text_search(self, metadata: AudioMetadata):
        """Enrichit via recherche textuelle"""
        try:
            # Construire une requête de recherche
            title = metadata.tags.get(TagType.TITLE, '')
            artist = metadata.tags.get(TagType.ARTIST, '')
            
            if title and artist:
                # Rechercher dans MusicBrainz
                results = await self._search_musicbrainz(title, artist)
                
                if results and 'recordings' in results:
                    recording = results['recordings'][0]
                    
                    # Enrichir avec des données supplémentaires
                    if 'isrcs' in recording and recording['isrcs']:
                        metadata.enriched_tags['musicbrainz_isrc'] = recording['isrcs'][0]
                    
                    if 'length' in recording:
                        metadata.enriched_tags['musicbrainz_duration'] = recording['length'] / 1000
                    
                    # Informations sur les releases
                    if 'releases' in recording and recording['releases']:
                        release = recording['releases'][0]
                        
                        if 'date' in release:
                            metadata.enriched_tags['musicbrainz_date'] = release['date']
                        
                        if 'label-info' in release and release['label-info']:
                            label_info = release['label-info'][0]
                            if 'label' in label_info:
                                metadata.enriched_tags['musicbrainz_label'] = label_info['label']['name']
                        
        except Exception as e:
            logger.warning(f"Text search enrichment failed: {e}")
    
    async def _enrich_with_ai_analysis(
        self,
        metadata: AudioMetadata,
        audio_file_path: Optional[str]
    ):
        """Enrichit avec analyse IA"""
        try:
            if audio_file_path:
                # Analyse du contenu audio avec ML
                await self._analyze_audio_content(metadata, audio_file_path)
            
            # Analyse des tags existants
            await self._analyze_existing_tags(metadata)
            
        except Exception as e:
            logger.warning(f"AI enrichment failed: {e}")
    
    async def _analyze_audio_content(
        self,
        metadata: AudioMetadata,
        audio_file_path: str
    ):
        """Analyse le contenu audio avec ML"""
        try:
            # Charger l'audio
            audio, sample_rate = librosa.load(audio_file_path, duration=30)
            
            # Classification de genre basique (simulation ML)
            await self._classify_genre(metadata, audio, sample_rate)
            
            # Analyse d'émotion/mood
            await self._analyze_mood(metadata, audio, sample_rate)
            
            # Détection d'instruments
            await self._detect_instruments(metadata, audio, sample_rate)
            
        except Exception as e:
            logger.warning(f"Audio content analysis failed: {e}")
    
    async def _classify_genre(
        self,
        metadata: AudioMetadata,
        audio: np.ndarray,
        sample_rate: int
    ):
        """Classification de genre (simulation ML)"""
        # Extraction de features pour classification
        
        # Tempo
        tempo = librosa.beat.tempo(y=audio, sr=sample_rate)[0]
        
        # Caractéristiques spectrales
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sample_rate))
        
        # Harmonie
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        harmonic_complexity = np.std(chroma)
        
        # Classification heuristique simple (remplacer par un vrai modèle ML)
        if tempo > 120 and spectral_centroid > 2000:
            if harmonic_complexity > 0.3:
                predicted_genre = "Electronic"
            else:
                predicted_genre = "Pop"
        elif tempo < 80:
            predicted_genre = "Classical" if harmonic_complexity > 0.4 else "Ambient"
        elif 80 <= tempo <= 120:
            if spectral_rolloff > 4000:
                predicted_genre = "Rock"
            else:
                predicted_genre = "Jazz"
        else:
            predicted_genre = "Dance"
        
        metadata.enriched_tags['ai_predicted_genre'] = predicted_genre
        metadata.enriched_tags['ai_genre_confidence'] = 0.75  # Simulation
    
    async def _analyze_mood(
        self,
        metadata: AudioMetadata,
        audio: np.ndarray,
        sample_rate: int
    ):
        """Analyse d'émotion/mood"""
        # Features pour l'analyse d'émotion
        
        # Énergie
        rms = np.mean(librosa.feature.rms(y=audio))
        
        # Variabilité tonale
        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        tonal_variability = np.std(chroma)
        
        # Tempo
        tempo = librosa.beat.tempo(y=audio, sr=sample_rate)[0]
        
        # Classification heuristique de mood
        if rms > 0.1 and tempo > 120:
            mood = "Energetic"
            energy = 0.8
        elif rms < 0.05 and tempo < 80:
            mood = "Calm"
            energy = 0.2
        elif tonal_variability > 0.3:
            mood = "Complex"
            energy = 0.6
        else:
            mood = "Neutral"
            energy = 0.5
        
        metadata.enriched_tags['ai_predicted_mood'] = mood
        metadata.enriched_tags['ai_energy_level'] = energy
        metadata.enriched_tags['ai_danceability'] = min(1.0, tempo / 140) if tempo > 60 else 0.1
    
    async def _detect_instruments(
        self,
        metadata: AudioMetadata,
        audio: np.ndarray,
        sample_rate: int
    ):
        """Détection d'instruments (simulation)"""
        # Analyse spectrale pour détection d'instruments
        
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        
        # Bandes de fréquence typiques pour différents instruments
        freq_bins = librosa.fft_frequencies(sr=sample_rate)
        
        # Batterie (basses fréquences + percussive)
        low_freq_energy = np.mean(magnitude[freq_bins < 200])
        
        # Instruments à cordes (moyennes fréquences)
        mid_freq_energy = np.mean(magnitude[(freq_bins >= 200) & (freq_bins < 2000)])
        
        # Voix/instruments aigus (hautes fréquences)
        high_freq_energy = np.mean(magnitude[freq_bins >= 2000])
        
        detected_instruments = []
        
        if low_freq_energy > 0.1:
            detected_instruments.append("Drums/Percussion")
        
        if mid_freq_energy > 0.15:
            detected_instruments.append("Strings/Guitar")
        
        if high_freq_energy > 0.1:
            detected_instruments.append("Vocals/Brass")
        
        metadata.enriched_tags['ai_detected_instruments'] = detected_instruments
    
    async def _analyze_existing_tags(self, metadata: AudioMetadata):
        """Analyse les tags existants pour détecter des patterns"""
        
        # Analyser le titre pour extraire des informations
        title = metadata.tags.get(TagType.TITLE, '')
        if title:
            # Détecter les features/collaborations
            if 'feat.' in title.lower() or 'ft.' in title.lower():
                metadata.enriched_tags['has_featured_artist'] = True
            
            # Détecter les versions (remix, acoustic, etc.)
            version_keywords = ['remix', 'acoustic', 'live', 'instrumental', 'radio edit']
            for keyword in version_keywords:
                if keyword in title.lower():
                    metadata.enriched_tags['version_type'] = keyword
                    break
        
        # Analyser l'artiste pour détecter les collaborations
        artist = metadata.tags.get(TagType.ARTIST, '')
        if artist and ('&' in artist or 'and' in artist.lower() or ',' in artist):
            metadata.enriched_tags['is_collaboration'] = True
    
    async def _generate_acoustic_fingerprint(self, audio_file_path: str) -> Optional[str]:
        """Génère un fingerprint acoustique (simulation)"""
        # Dans une vraie implémentation, utiliser AcoustID/Chromaprint
        try:
            audio, sample_rate = librosa.load(audio_file_path, duration=120)
            
            # Simulation d'un fingerprint
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            fingerprint_data = np.mean(chroma, axis=1)
            
            # Encoder en base64 pour simulation
            fingerprint = base64.b64encode(fingerprint_data.tobytes()).decode()
            return fingerprint[:50]  # Truncate pour simulation
            
        except Exception as e:
            logger.warning(f"Fingerprint generation failed: {e}")
            return None
    
    async def _query_acoustid(self, fingerprint: str) -> Optional[Dict]:
        """Requête AcoustID (simulation)"""
        # Simulation de réponse AcoustID
        return {
            "results": [{
                "recordings": [{
                    "title": "Example Song",
                    "artists": [{"name": "Example Artist"}],
                    "releases": [{"title": "Example Album"}]
                }]
            }]
        }
    
    async def _search_musicbrainz(self, title: str, artist: str) -> Optional[Dict]:
        """Recherche MusicBrainz (simulation)"""
        # Simulation de réponse MusicBrainz
        return {
            "recordings": [{
                "title": title,
                "length": 180000,  # 3 minutes en ms
                "isrcs": ["GBUM71505078"],
                "releases": [{
                    "title": "Example Album",
                    "date": "2023-01-01",
                    "label-info": [{
                        "label": {"name": "Example Label"}
                    }]
                }]
            }]
        }

class AudioMetadataProcessor:
    """Processeur principal de métadonnées audio enterprise"""
    
    def __init__(self, config: Optional[MetadataProcessingConfig] = None):
        """Initialise le processeur de métadonnées"""
        self.config = config or MetadataProcessingConfig()
        self.extractor = MetadataExtractor()
        self.enricher = MetadataEnricher()
        
        # Base de données de métadonnées (en mémoire pour la démo)
        self.metadata_database = {}
        
        # Cache Redis
        self.redis_client = None
        
        # Statistiques
        self.stats = {
            'total_processed': 0,
            'extraction_times': [],
            'enrichment_times': [],
            'error_count': 0,
            'format_distribution': {},
            'tag_completeness': []
        }
        
        logger.info("AudioMetadataProcessor initialized successfully")
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialise la connexion Redis"""
        try:
            self.redis_client = await aioredis.from_url(redis_url)
            logger.info("Redis connection established for metadata caching")
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}")
    
    async def process_metadata(
        self,
        file_path: str,
        enable_enrichment: bool = True
    ) -> AudioMetadata:
        """Traite les métadonnées d'un fichier audio"""
        start_time = time.time()
        
        try:
            # Vérifier le cache
            file_hash = await self._calculate_file_hash(file_path)
            cached_metadata = await self._get_cached_metadata(file_hash)
            
            if cached_metadata:
                logger.info(f"Using cached metadata for {Path(file_path).name}")
                return cached_metadata
            
            # Extraction des métadonnées
            extraction_start = time.time()
            metadata = await self.extractor.extract_metadata(file_path, self.config)
            extraction_time = time.time() - extraction_start
            
            # Enrichissement si activé
            enrichment_time = 0
            if enable_enrichment and self.config.enable_ai_enrichment:
                enrichment_start = time.time()
                metadata = await self.enricher.enrich_metadata(metadata, file_path)
                enrichment_time = time.time() - enrichment_start
            
            # Ajouter l'historique de traitement
            processing_record = {
                'timestamp': datetime.now().isoformat(),
                'extraction_time': extraction_time,
                'enrichment_time': enrichment_time,
                'config_hash': hashlib.md5(str(self.config.__dict__).encode()).hexdigest()[:8]
            }
            metadata.processing_history.append(processing_record)
            metadata.modified_at = datetime.now()
            
            # Stocker dans la base de données
            self.metadata_database[file_hash] = metadata
            
            # Mettre en cache
            await self._cache_metadata(file_hash, metadata)
            
            # Mettre à jour les statistiques
            await self._update_stats(file_path, extraction_time, enrichment_time, metadata)
            
            return metadata
            
        except Exception as e:
            self.stats['error_count'] += 1
            logger.error(f"Metadata processing failed for {file_path}: {e}")
            raise
    
    async def batch_process_directory(
        self,
        directory_path: str,
        file_pattern: str = "*.{mp3,flac,m4a,ogg,wav}",
        max_workers: int = 4
    ) -> Dict[str, AudioMetadata]:
        """Traite les métadonnées de tous les fichiers d'un répertoire"""
        
        directory = Path(directory_path)
        supported_extensions = {'.mp3', '.flac', '.m4a', '.mp4', '.ogg', '.wav', '.wv', '.ape'}
        
        # Collecter tous les fichiers audio
        audio_files = []
        for ext in supported_extensions:
            pattern = f"*{ext}"
            audio_files.extend(directory.rglob(pattern))
        
        results = {}
        
        # Traitement parallèle avec semaphore
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_file(file_path):
            async with semaphore:
                try:
                    metadata = await self.process_metadata(str(file_path))
                    return str(file_path), metadata
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    return str(file_path), None
        
        # Lancer tous les traitements
        tasks = [process_file(file_path) for file_path in audio_files]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collecter les résultats
        for result in task_results:
            if isinstance(result, tuple) and result[1] is not None:
                file_path, metadata = result
                results[file_path] = metadata
        
        logger.info(f"Processed {len(results)} files successfully out of {len(audio_files)} total")
        return results
    
    async def export_metadata(
        self,
        metadata: AudioMetadata,
        output_path: str,
        format_type: str = "json"
    ):
        """Exporte les métadonnées vers un fichier"""
        
        if format_type.lower() == "json":
            await self._export_json(metadata, output_path)
        elif format_type.lower() == "xml":
            await self._export_xml(metadata, output_path)
        elif format_type.lower() == "csv":
            await self._export_csv([metadata], output_path)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    async def _export_json(self, metadata: AudioMetadata, output_path: str):
        """Exporte en JSON"""
        # Convertir en format sérialisable
        export_data = {
            'tags': {tag.value: value for tag, value in metadata.tags.items()},
            'technical_info': metadata.technical_info,
            'computed_tags': metadata.computed_tags,
            'enriched_tags': metadata.enriched_tags,
            'images': [
                {
                    'type': img.image_type.value,
                    'mime_type': img.mime_type,
                    'description': img.description,
                    'width': img.width,
                    'height': img.height,
                    'size_bytes': len(img.data),
                    'data_base64': base64.b64encode(img.data).decode()
                }
                for img in metadata.images
            ],
            'processing_history': metadata.processing_history,
            'created_at': metadata.created_at.isoformat(),
            'modified_at': metadata.modified_at.isoformat(),
            'source_standard': metadata.source_standard.value if metadata.source_standard else None
        }
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(export_data, indent=2, ensure_ascii=False))
    
    async def _export_xml(self, metadata: AudioMetadata, output_path: str):
        """Exporte en XML"""
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<audio_metadata>')
        
        # Tags
        xml_content.append('  <tags>')
        for tag, value in metadata.tags.items():
            xml_content.append(f'    <{tag.value}>{self._escape_xml(str(value))}</{tag.value}>')
        xml_content.append('  </tags>')
        
        # Technical info
        xml_content.append('  <technical_info>')
        for key, value in metadata.technical_info.items():
            xml_content.append(f'    <{key}>{self._escape_xml(str(value))}</{key}>')
        xml_content.append('  </technical_info>')
        
        xml_content.append('</audio_metadata>')
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write('\n'.join(xml_content))
    
    async def _export_csv(self, metadata_list: List[AudioMetadata], output_path: str):
        """Exporte en CSV"""
        # Collecter toutes les clés possibles
        all_tags = set()
        for metadata in metadata_list:
            all_tags.update(tag.value for tag in metadata.tags.keys())
        
        csv_lines = []
        
        # En-tête
        header = ['file_path'] + sorted(all_tags) + ['duration', 'bitrate', 'sample_rate']
        csv_lines.append(','.join(header))
        
        # Données
        for metadata in metadata_list:
            row = ['']  # file_path sera rempli par l'appelant
            
            for tag in sorted(all_tags):
                tag_enum = None
                for t in TagType:
                    if t.value == tag:
                        tag_enum = t
                        break
                
                value = metadata.tags.get(tag_enum, '') if tag_enum else ''
                row.append(f'"{self._escape_csv(str(value))}"')
            
            # Info techniques
            row.extend([
                str(metadata.technical_info.get('duration', '')),
                str(metadata.technical_info.get('bitrate', '')),
                str(metadata.technical_info.get('sample_rate', ''))
            ])
            
            csv_lines.append(','.join(row))
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write('\n'.join(csv_lines))
    
    def _escape_xml(self, text: str) -> str:
        """Échappe les caractères XML"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _escape_csv(self, text: str) -> str:
        """Échappe les caractères CSV"""
        return text.replace('"', '""')
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule un hash pour identifier le fichier"""
        file_stat = Path(file_path).stat()
        hash_input = f"{file_path}:{file_stat.st_size}:{file_stat.st_mtime}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def _get_cached_metadata(self, file_hash: str) -> Optional[AudioMetadata]:
        """Récupère les métadonnées du cache"""
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(f"metadata:{file_hash}")
                if cached_data:
                    # Désérialiser (implémentation simplifiée)
                    return None  # Pour cette démo, on skip la désérialisation
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")
        
        return self.metadata_database.get(file_hash)
    
    async def _cache_metadata(self, file_hash: str, metadata: AudioMetadata):
        """Met en cache les métadonnées"""
        if self.redis_client:
            try:
                # Sérialiser et mettre en cache (implémentation simplifiée)
                await self.redis_client.setex(
                    f"metadata:{file_hash}",
                    3600,  # 1 heure
                    "cached"  # Pour cette démo
                )
            except Exception as e:
                logger.warning(f"Cache storage failed: {e}")
    
    async def _update_stats(
        self,
        file_path: str,
        extraction_time: float,
        enrichment_time: float,
        metadata: AudioMetadata
    ):
        """Met à jour les statistiques"""
        self.stats['total_processed'] += 1
        self.stats['extraction_times'].append(extraction_time)
        self.stats['enrichment_times'].append(enrichment_time)
        
        # Distribution des formats
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.stats['format_distribution']:
            self.stats['format_distribution'][file_ext] = 0
        self.stats['format_distribution'][file_ext] += 1
        
        # Complétude des tags
        total_possible_tags = len(TagType)
        filled_tags = len(metadata.tags)
        completeness = filled_tags / total_possible_tags
        self.stats['tag_completeness'].append(completeness)
        
        # Limiter la taille des listes
        for key in ['extraction_times', 'enrichment_times', 'tag_completeness']:
            if len(self.stats[key]) > 1000:
                self.stats[key] = self.stats[key][-1000:]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du processeur"""
        stats = self.stats.copy()
        
        if stats['extraction_times']:
            stats['average_extraction_time'] = np.mean(stats['extraction_times'])
            
        if stats['enrichment_times']:
            stats['average_enrichment_time'] = np.mean(stats['enrichment_times'])
            
        if stats['tag_completeness']:
            stats['average_tag_completeness'] = np.mean(stats['tag_completeness'])
        
        return stats

# Factory functions
async def create_audio_metadata_processor(
    config: Optional[MetadataProcessingConfig] = None
) -> AudioMetadataProcessor:
    """Crée une instance du processeur de métadonnées"""
    processor = AudioMetadataProcessor(config)
    return processor

async def create_metadata_config(
    enable_ai_enrichment: bool = True,
    enable_audio_analysis: bool = True,
    max_image_size: int = 1024 * 1024
) -> MetadataProcessingConfig:
    """Crée une configuration de traitement des métadonnées"""
    return MetadataProcessingConfig(
        enable_ai_enrichment=enable_ai_enrichment,
        enable_audio_analysis=enable_audio_analysis,
        max_image_size=max_image_size
    )

# Export des classes et fonctions principales
__all__ = [
    'AudioMetadataProcessor',
    'MetadataStandard',
    'TagType',
    'ImageType',
    'AudioImage',
    'AudioMetadata',
    'MetadataProcessingConfig',
    'MetadataExtractor',
    'MetadataEnricher',
    'create_audio_metadata_processor',
    'create_metadata_config'
]