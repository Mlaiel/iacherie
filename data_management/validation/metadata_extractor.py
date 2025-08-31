"""🚀 Metadata Extractor - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/data_management/validation/metadata_extractor.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EXTRACTION MÉTADONNÉES AVANCÉE
Extraction complète de métadonnées multi-format avec IA
- EXIF/GPS pour images haute précision
- Tags audio ID3/FLAC/MP4 complets
- Métadonnées vidéo FFprobe/MediaInfo
- Analyse sémantique contenu avec IA
"""
from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed

# Image metadata
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

# Audio metadata
import eyed3
import mutagen
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

# Video metadata
import ffmpeg
import subprocess
from moviepy.editor import VideoFileClip

# Text analysis
import chardet
from langdetect import detect, LangDetectError
import textstat

# AI-powered analysis
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np

# Advanced extraction
import magic
import hashlib
import mimetypes
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class GeolocationData:
    """Données de géolocalisation"""    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    timestamp: Optional[str] = None
    accuracy: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

@dataclass
class TechnicalMetadata:
    """Métadonnées techniques"""    file_size: int
    file_format: str
    mime_type: str
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    file_hash: str = ""
    encoding: Optional[str] = None
    compression: Optional[str] = None
    quality_score: Optional[float] = None

@dataclass
class MediaDimensions:
    """Dimensions média"""    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    fps: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    aspect_ratio: Optional[str] = None

@dataclass
class CreativeMetadata:
    """Métadonnées créatives"""    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    copyright: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    genre: Optional[str] = None
    style: Optional[str] = None
    mood: Optional[str] = None
    theme: Optional[str] = None
    ai_generated_tags: List[str] = field(default_factory=list)

@dataclass
class BusinessMetadata:
    """Métadonnées business"""    license: Optional[str] = None
    usage_rights: Optional[str] = None
    commercial_use: Optional[bool] = None
    attribution_required: Optional[bool] = None
    monetization_allowed: Optional[bool] = None
    platform_restrictions: List[str] = field(default_factory=list)
    market_value: Optional[float] = None
    target_audience: List[str] = field(default_factory=list)

@dataclass
class ContentMetadata:
    """Métadonnées de contenu complètes"""    file_path: str
    technical: TechnicalMetadata
    dimensions: MediaDimensions
    creative: CreativeMetadata
    business: BusinessMetadata
    geolocation: Optional[GeolocationData] = None
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    extraction_version: str = "1.0.0"

class ImageMetadataExtractor:
    """Extracteur de métadonnées d'image avancé"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ImageMetadataExtractor")
        
        # Initialisation des modèles IA pour analyse d'image
        try:
            self.image_classifier = pipeline("image-classification", 
                                           model="google/vit-base-patch16-224")
            self.image_captioning = pipeline("image-to-text", 
                                           model="Salesforce/blip-image-captioning-base")
        except Exception as e:
            self.logger.warning(f"Impossible de charger les modèles IA image: {e}")
            self.image_classifier = None
            self.image_captioning = None
    
    def extract_metadata(self, file_path: str) -> ContentMetadata:
        """Extrait toutes les métadonnées d'une image"""        try:
            # Ouverture de l'image
            image = Image.open(file_path)
            
            # Métadonnées techniques
            technical = self._extract_technical_metadata(file_path, image)
            
            # Dimensions
            dimensions = self._extract_dimensions(image)
            
            # EXIF et géolocalisation
            exif_data = self._extract_exif_data(image)
            geolocation = self._extract_geolocation(exif_data)
            
            # Métadonnées créatives
            creative = self._extract_creative_metadata(image, exif_data)
            
            # Analyse IA
            ai_analysis = self._perform_ai_analysis(image, file_path)
            creative.ai_generated_tags = ai_analysis.get('tags', [])
            
            # Métadonnées business (par défaut)
            business = BusinessMetadata()
            
            return ContentMetadata(
                file_path=file_path,
                technical=technical,
                dimensions=dimensions,
                creative=creative,
                business=business,
                geolocation=geolocation,
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction métadonnées image {file_path}: {e}")
            return self._create_error_metadata(file_path, str(e))
    
    def _extract_technical_metadata(self, file_path: str, image: Image.Image) -> TechnicalMetadata:
        """Extrait les métadonnées techniques"""        file_stat = os.stat(file_path)
        
        # Hash du fichier
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return TechnicalMetadata(
            file_size=file_stat.st_size,
            file_format=image.format or Path(file_path).suffix[1:].upper(),
            mime_type=mime_type or 'application/octet-stream',
            creation_date=datetime.fromtimestamp(file_stat.st_ctime),
            modification_date=datetime.fromtimestamp(file_stat.st_mtime),
            file_hash=file_hash,
            compression=getattr(image, 'compression', None)
        )
    
    def _extract_dimensions(self, image: Image.Image) -> MediaDimensions:
        """Extrait les dimensions"""        width, height = image.size
        aspect_ratio = f"{width}:{height}"
        
        # Simplification du ratio
        from math import gcd
        ratio_gcd = gcd(width, height)
        simplified_ratio = f"{width//ratio_gcd}:{height//ratio_gcd}"
        
        return MediaDimensions(
            width=width,
            height=height,
            aspect_ratio=simplified_ratio
        )
    
    def _extract_exif_data(self, image: Image.Image) -> Dict[str, Any]:
        """Extrait les données EXIF"""        exif_data = {}
        
        try:
            # Données EXIF PIL
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
            
            # Données EXIF avec piexif pour plus de détails
            try:
                exif_dict = piexif.load(image.filename) if hasattr(image, 'filename') else {}
                
                # EXIF IFD
                if piexif.ExifIFD in exif_dict:
                    for tag_id, value in exif_dict[piexif.ExifIFD].items():
                        tag_name = piexif.TAGS['Exif'].get(tag_id, {}).get('name', f'Tag_{tag_id}')
                        exif_data[f'Exif_{tag_name}'] = value
                
                # GPS IFD
                if piexif.GPSIFD in exif_dict:
                    for tag_id, value in exif_dict[piexif.GPSIFD].items():
                        tag_name = piexif.TAGS['GPS'].get(tag_id, {}).get('name', f'GPS_{tag_id}')
                        exif_data[f'GPS_{tag_name}'] = value
                        
            except Exception as e:
                self.logger.debug(f"Erreur piexif: {e}")
                
        except Exception as e:
            self.logger.debug(f"Erreur extraction EXIF: {e}")
        
        return exif_data
    
    def _extract_geolocation(self, exif_data: Dict[str, Any]) -> Optional[GeolocationData]:
        """Extrait la géolocalisation depuis EXIF"""        try:
            # Recherche des données GPS
            gps_latitude = None
            gps_longitude = None
            gps_altitude = None
            
            # Différents formats possibles
            for key, value in exif_data.items():
                if 'GPS' in key and 'Latitude' in key and isinstance(value, (tuple, list)):
                    gps_latitude = self._convert_gps_coordinate(value, exif_data.get('GPS_GPSLatitudeRef', 'N'))
                elif 'GPS' in key and 'Longitude' in key and isinstance(value, (tuple, list)):
                    gps_longitude = self._convert_gps_coordinate(value, exif_data.get('GPS_GPSLongitudeRef', 'E'))
                elif 'GPS' in key and 'Altitude' in key:
                    gps_altitude = float(value) if isinstance(value, (int, float)) else None
            
            if gps_latitude is not None and gps_longitude is not None:
                return GeolocationData(
                    latitude=gps_latitude,
                    longitude=gps_longitude,
                    altitude=gps_altitude,
                    timestamp=exif_data.get('GPS_GPSTimeStamp', None)
                )
                
        except Exception as e:
            self.logger.debug(f"Erreur extraction géolocalisation: {e}")
        
        return None
    
    def _convert_gps_coordinate(self, coordinate: tuple, reference: str) -> float:
        """Convertit les coordonnées GPS EXIF en degrés décimaux"""        try:
            if len(coordinate) >= 3:
                degrees = float(coordinate[0])
                minutes = float(coordinate[1])
                seconds = float(coordinate[2])
                
                decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
                
                if reference in ['S', 'W']:
                    decimal = -decimal
                
                return decimal
        except Exception:
            pass
        
        return 0.0
    
    def _extract_creative_metadata(self, image: Image.Image, exif_data: Dict[str, Any]) -> CreativeMetadata:
        """Extrait les métadonnées créatives"""        creative = CreativeMetadata()
        
        # Titre et description depuis EXIF/IPTC
        creative.title = exif_data.get('ImageDescription', None)
        creative.description = exif_data.get('UserComment', None)
        creative.creator = exif_data.get('Artist', None)
        creative.copyright = exif_data.get('Copyright', None)
        
        # Mots-clés depuis EXIF
        keywords_raw = exif_data.get('Keywords', '')
        if keywords_raw:
            creative.keywords = [kw.strip() for kw in str(keywords_raw).split(',') if kw.strip()]
        
        # Informations appareil photo
        camera_make = exif_data.get('Make', '')
        camera_model = exif_data.get('Model', '')
        if camera_make or camera_model:
            creative.style = f"{camera_make} {camera_model}".strip()
        
        return creative
    
    def _perform_ai_analysis(self, image: Image.Image, file_path: str) -> Dict[str, Any]:
        """Effectue une analyse IA de l'image"""        ai_analysis = {}
        
        try:
            # Classification d'image
            if self.image_classifier:
                classifications = self.image_classifier(image)
                ai_analysis['classifications'] = classifications
                ai_analysis['tags'] = [item['label'] for item in classifications[:5]]
            
            # Génération de caption
            if self.image_captioning:
                caption = self.image_captioning(image)
                if caption:
                    ai_analysis['caption'] = caption[0].get('generated_text', '')
            
            # Analyse de couleur dominante
            dominant_colors = self._extract_dominant_colors(image)
            ai_analysis['dominant_colors'] = dominant_colors
            
            # Détection de visages/objets (basique)
            objects_detected = self._basic_object_detection(image)
            ai_analysis['objects'] = objects_detected
            
        except Exception as e:
            self.logger.debug(f"Erreur analyse IA image: {e}")
        
        return ai_analysis
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """Extrait les couleurs dominantes"""        try:
            # Redimensionner pour performance
            image_small = image.resize((150, 150))
            
            # Convertir en RGB si nécessaire
            if image_small.mode != 'RGB':
                image_small = image_small.convert('RGB')
            
            # Quantification des couleurs
            quantized = image_small.quantize(colors=num_colors)
            palette = quantized.getpalette()
            
            # Conversion en couleurs hex
            colors = []
            for i in range(num_colors):
                r = palette[i * 3]
                g = palette[i * 3 + 1]
                b = palette[i * 3 + 2]
                colors.append(f"#{r:02x}{g:02x}{b:02x}")
            
            return colors
            
        except Exception as e:
            self.logger.debug(f"Erreur extraction couleurs: {e}")
            return []
    
    def _basic_object_detection(self, image: Image.Image) -> List[str]:
        """Détection d'objets basique (peut être étendue avec YOLO)"""        objects = []
        
        try:
            # Analyse basique de la composition
            width, height = image.size
            
            # Portrait vs paysage
            if height > width:
                objects.append("portrait_orientation")
            else:
                objects.append("landscape_orientation")
            
            # Analyse de la luminosité
            if image.mode == 'RGB':
                grayscale = image.convert('L')
                histogram = grayscale.histogram()
                
                # Luminosité moyenne
                total_pixels = sum(histogram)
                weighted_sum = sum(i * histogram[i] for i in range(256))
                avg_brightness = weighted_sum / total_pixels
                
                if avg_brightness < 85:
                    objects.append("low_light")
                elif avg_brightness > 170:
                    objects.append("high_light")
                else:
                    objects.append("normal_light")
            
        except Exception as e:
            self.logger.debug(f"Erreur détection objets: {e}")
        
        return objects
    
    def _create_error_metadata(self, file_path: str, error: str) -> ContentMetadata:
        """Crée des métadonnées d'erreur"""        return ContentMetadata(
            file_path=file_path,
            technical=TechnicalMetadata(
                file_size=0,
                file_format="UNKNOWN",
                mime_type="application/octet-stream"
            ),
            dimensions=MediaDimensions(),
            creative=CreativeMetadata(),
            business=BusinessMetadata(),
            ai_analysis={"error": error}
        )

class AudioMetadataExtractor:
    """Extracteur de métadonnées audio avancé"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AudioMetadataExtractor")
        
        # Modèles IA pour analyse audio
        try:
            self.audio_classifier = pipeline("audio-classification", 
                                            model="facebook/wav2vec2-base")
        except Exception as e:
            self.logger.warning(f"Impossible de charger les modèles IA audio: {e}")
            self.audio_classifier = None
    
    def extract_metadata(self, file_path: str) -> ContentMetadata:
        """Extrait toutes les métadonnées d'un fichier audio"""        try:
            # Métadonnées techniques
            technical = self._extract_technical_metadata(file_path)
            
            # Tags audio avec mutagen
            audio_tags = self._extract_audio_tags(file_path)
            
            # Dimensions audio
            dimensions = self._extract_audio_dimensions(file_path)
            
            # Métadonnées créatives depuis tags
            creative = self._extract_creative_from_tags(audio_tags)
            
            # Analyse IA
            ai_analysis = self._perform_audio_ai_analysis(file_path)
            
            # Métadonnées business
            business = self._extract_business_metadata(audio_tags)
            
            return ContentMetadata(
                file_path=file_path,
                technical=technical,
                dimensions=dimensions,
                creative=creative,
                business=business,
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction métadonnées audio {file_path}: {e}")
            return self._create_error_metadata(file_path, str(e))
    
    def _extract_technical_metadata(self, file_path: str) -> TechnicalMetadata:
        """Extrait les métadonnées techniques audio"""        file_stat = os.stat(file_path)
        
        # Hash du fichier
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Format depuis extension
        file_format = Path(file_path).suffix[1:].upper()
        
        return TechnicalMetadata(
            file_size=file_stat.st_size,
            file_format=file_format,
            mime_type=mime_type or 'audio/unknown',
            creation_date=datetime.fromtimestamp(file_stat.st_ctime),
            modification_date=datetime.fromtimestamp(file_stat.st_mtime),
            file_hash=file_hash
        )
    
    def _extract_audio_tags(self, file_path: str) -> Dict[str, Any]:
        """Extrait les tags audio avec mutagen"""        tags = {}
        
        try:
            # Tentative avec mutagen
            audio_file = mutagen.File(file_path)
            
            if audio_file is not None:
                for key, value in audio_file.items():
                    # Normalisation des valeurs
                    if isinstance(value, list) and len(value) == 1:
                        tags[key] = value[0]
                    else:
                        tags[key] = value
            
            # Tentative avec eyed3 pour MP3
            if file_path.lower().endswith('.mp3'):
                try:
                    audiofile = eyed3.load(file_path)
                    if audiofile and audiofile.tag:
                        tag = audiofile.tag
                        tags.update({
                            'title': tag.title,
                            'artist': tag.artist,
                            'album': tag.album,
                            'album_artist': tag.album_artist,
                            'genre': str(tag.genre) if tag.genre else None,
                            'year': tag.getBestDate(),
                            'track_num': tag.track_num[0] if tag.track_num else None,
                            'total_tracks': tag.track_num[1] if tag.track_num and len(tag.track_num) > 1 else None
                        })
                except Exception as e:
                    self.logger.debug(f"Erreur eyed3: {e}")
                    
        except Exception as e:
            self.logger.debug(f"Erreur extraction tags: {e}")
        
        return tags
    
    def _extract_audio_dimensions(self, file_path: str) -> MediaDimensions:
        """Extrait les dimensions audio"""        dimensions = MediaDimensions()
        
        try:
            # Utilisation de mutagen pour les infos de base
            audio_file = mutagen.File(file_path)
            
            if audio_file:
                dimensions.duration = getattr(audio_file.info, 'length', None)
                dimensions.bitrate = getattr(audio_file.info, 'bitrate', None)
                dimensions.sample_rate = getattr(audio_file.info, 'sample_rate', None)
                dimensions.channels = getattr(audio_file.info, 'channels', None)
            
            # Complément avec ffprobe si disponible
            try:
                probe = ffmpeg.probe(file_path)
                audio_stream = next((stream for stream in probe['streams'] 
                                   if stream['codec_type'] == 'audio'), None)
                
                if audio_stream:
                    if not dimensions.sample_rate:
                        dimensions.sample_rate = int(audio_stream.get('sample_rate', 0))
                    if not dimensions.channels:
                        dimensions.channels = int(audio_stream.get('channels', 0))
                    if not dimensions.bitrate:
                        dimensions.bitrate = int(audio_stream.get('bit_rate', 0))
                    if not dimensions.duration:
                        dimensions.duration = float(audio_stream.get('duration', 0))
                        
            except Exception as e:
                self.logger.debug(f"Erreur ffprobe: {e}")
                
        except Exception as e:
            self.logger.debug(f"Erreur dimensions audio: {e}")
        
        return dimensions
    
    def _extract_creative_from_tags(self, tags: Dict[str, Any]) -> CreativeMetadata:
        """Extrait les métadonnées créatives depuis les tags"""        creative = CreativeMetadata()
        
        # Mapping des tags courants
        tag_mappings = {
            'title': ['TIT2', 'TITLE', '©nam', 'title'],
            'creator': ['TPE1', 'ARTIST', '©ART', 'artist'],
            'description': ['COMM::eng', 'COMMENT', '©cmt', 'comment'],
            'genre': ['TCON', 'GENRE', '©gen', 'genre'],
            'copyright': ['TCOP', 'COPYRIGHT', '©cpy', 'copyright']
        }
        
        # Extraction avec mapping flexible
        for field, possible_keys in tag_mappings.items():
            for key in possible_keys:
                if key in tags:
                    setattr(creative, field, str(tags[key]))
                    break
        
        # Album comme contexte
        album = None
        for key in ['TALB', 'ALBUM', '©alb', 'album']:
            if key in tags:
                album = str(tags[key])
                break
        
        if album:
            creative.theme = album
        
        # Mots-clés depuis tags divers
        keywords = []
        for key in ['KEYWORDS', 'TAGS', 'keywords', 'tags']:
            if key in tags:
                kw_value = str(tags[key])
                keywords.extend([kw.strip() for kw in kw_value.split(',') if kw.strip()])
        
        creative.keywords = keywords
        
        return creative
    
    def _extract_business_metadata(self, tags: Dict[str, Any]) -> BusinessMetadata:
        """Extrait les métadonnées business"""        business = BusinessMetadata()
        
        # Licence
        for key in ['LICENSE', 'licence', 'copyright']:
            if key in tags:
                business.license = str(tags[key])
                break
        
        # Détection usage commercial
        copyright_text = business.license or ''
        if 'creative commons' in copyright_text.lower():
            business.commercial_use = 'nc' not in copyright_text.lower()
            business.attribution_required = 'by' in copyright_text.lower()
        
        return business
    
    def _perform_audio_ai_analysis(self, file_path: str) -> Dict[str, Any]:
        """Effectue une analyse IA du fichier audio"""        ai_analysis = {}
        
        try:
            # Classification audio (nécessite conversion en format supporté)
            if self.audio_classifier:
                # Audio classification implementation using spectral features
                try:
                    import librosa
                    import numpy as np
                    
                    # Load audio file (30 seconds sample for classification)
                    y, sr = librosa.load(file_path, sr=22050, duration=30)
                    
                    # Extract MFCC features (Mel-frequency cepstral coefficients)
                    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    mfcc_mean = np.mean(mfccs, axis=1)
                    
                    # Extract spectral features
                    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
                    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
                    zero_crossings = librosa.feature.zero_crossing_rate(y)
                    
                    # Calculate tempo and rhythm features
                    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                    
                    # Simple rule-based classification based on audio characteristics
                    genre_prediction = self._classify_audio_genre(
                        mfcc_mean, 
                        np.mean(spectral_centroids), 
                        np.mean(spectral_rolloff),
                        np.mean(zero_crossings),
                        tempo
                    )
                    
                    # Add classification results to AI analysis
                    ai_analysis['genre_prediction'] = genre_prediction
                    ai_analysis['tempo_bpm'] = float(tempo)
                    ai_analysis['spectral_centroid'] = float(np.mean(spectral_centroids))
                    ai_analysis['spectral_rolloff'] = float(np.mean(spectral_rolloff))
                    ai_analysis['zero_crossing_rate'] = float(np.mean(zero_crossings))
                    ai_analysis['mfcc_features'] = mfcc_mean.tolist()
                    
                except Exception as e:
                    logger.warning(f"Audio classification failed: {e}")
                    ai_analysis['classification_error'] = str(e)
            else:
                # Fallback: Basic audio analysis without classification
                try:
                    import librosa
                    y, sr = librosa.load(file_path, sr=None, duration=10)  # Short sample
                    
                    # Basic tempo detection
                    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                    ai_analysis['tempo_bpm'] = float(tempo)
                    
                    # Energy analysis
                    rms_energy = librosa.feature.rms(y=y)
                    ai_analysis['energy_level'] = float(np.mean(rms_energy))
                    
                except Exception as e:
                    logger.warning(f"Basic audio analysis failed: {e}")
            
            # Analyse basique du spectre
            import librosa
            y, sr = librosa.load(file_path, sr=None, duration=30)  # 30 premières secondes
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            ai_analysis['tempo'] = float(tempo)
            
            # Caractéristiques spectrales
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            ai_analysis['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
            
            # Classification de genre basique
            if ai_analysis['spectral_centroid_mean'] > 3000:
                ai_analysis['predicted_genre'] = 'electronic/pop'
            elif ai_analysis['spectral_centroid_mean'] < 1500:
                ai_analysis['predicted_genre'] = 'classical/acoustic'
            else:
                ai_analysis['predicted_genre'] = 'rock/jazz'
            
            # Tags générés
            tags = ['music']
            if tempo > 120:
                tags.append('upbeat')
            elif tempo < 80:
                tags.append('slow')
            
            ai_analysis['generated_tags'] = tags
            
        except Exception as e:
            self.logger.debug(f"Erreur analyse IA audio: {e}")
        
        return ai_analysis
    
    def _classify_audio_genre(self, mfcc_mean, spectral_centroid, spectral_rolloff, zero_crossing_rate, tempo):
        """Simple rule-based audio genre classification"""        try:
            # Genre classification based on audio features
            # These are simplified rules - in production, you'd use a trained ML model
            
            # Electronic/Dance characteristics
            if tempo > 120 and spectral_centroid > 2500 and zero_crossing_rate > 0.1:
                return "electronic/dance"
            
            # Classical/Acoustic characteristics  
            elif tempo < 100 and spectral_centroid < 2000 and zero_crossing_rate < 0.05:
                return "classical/acoustic"
            
            # Rock/Metal characteristics
            elif spectral_rolloff > 4000 and zero_crossing_rate > 0.08:
                return "rock/metal"
            
            # Jazz characteristics
            elif 80 < tempo < 140 and 1500 < spectral_centroid < 3000:
                return "jazz/blues"
            
            # Pop characteristics
            elif 100 < tempo < 130 and 2000 < spectral_centroid < 3500:
                return "pop/mainstream"
            
            # Hip-hop/Rap characteristics
            elif tempo > 80 and spectral_centroid < 2200 and zero_crossing_rate > 0.06:
                return "hip-hop/rap"
            
            # Ambient/Chill characteristics
            elif tempo < 90 and spectral_centroid > 1800 and zero_crossing_rate < 0.04:
                return "ambient/chill"
            
            # Default fallback
            else:
                return "unknown/mixed"
                
        except Exception as e:
            logger.warning(f"Genre classification error: {e}")
            return "classification_failed"
    
    def _create_error_metadata(self, file_path: str, error: str) -> ContentMetadata:
        """Crée des métadonnées d'erreur"""        return ContentMetadata(
            file_path=file_path,
            technical=TechnicalMetadata(
                file_size=0,
                file_format="UNKNOWN",
                mime_type="audio/unknown"
            ),
            dimensions=MediaDimensions(),
            creative=CreativeMetadata(),
            business=BusinessMetadata(),
            ai_analysis={"error": error}
        )

class VideoMetadataExtractor:
    """Extracteur de métadonnées vidéo avancé"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VideoMetadataExtractor")
    
    def extract_metadata(self, file_path: str) -> ContentMetadata:
        """Extrait toutes les métadonnées d'un fichier vidéo"""        try:
            # Métadonnées techniques
            technical = self._extract_technical_metadata(file_path)
            
            # Informations vidéo avec ffprobe
            video_info = self._extract_video_info(file_path)
            
            # Dimensions vidéo
            dimensions = self._extract_video_dimensions(video_info)
            
            # Métadonnées créatives
            creative = self._extract_creative_from_video(video_info)
            
            # Analyse IA
            ai_analysis = self._perform_video_ai_analysis(file_path)
            
            # Métadonnées business
            business = BusinessMetadata()
            
            return ContentMetadata(
                file_path=file_path,
                technical=technical,
                dimensions=dimensions,
                creative=creative,
                business=business,
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction métadonnées vidéo {file_path}: {e}")
            return self._create_error_metadata(file_path, str(e))
    
    def _extract_technical_metadata(self, file_path: str) -> TechnicalMetadata:
        """Extrait les métadonnées techniques vidéo"""        file_stat = os.stat(file_path)
        
        # Hash du fichier
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Format depuis extension
        file_format = Path(file_path).suffix[1:].upper()
        
        return TechnicalMetadata(
            file_size=file_stat.st_size,
            file_format=file_format,
            mime_type=mime_type or 'video/unknown',
            creation_date=datetime.fromtimestamp(file_stat.st_ctime),
            modification_date=datetime.fromtimestamp(file_stat.st_mtime),
            file_hash=file_hash
        )
    
    def _extract_video_info(self, file_path: str) -> Dict[str, Any]:
        """Extrait les informations vidéo avec ffprobe"""        video_info = {}
        
        try:
            probe = ffmpeg.probe(file_path)
            
            # Informations générales
            video_info['format'] = probe.get('format', {})
            video_info['streams'] = probe.get('streams', [])
            
            # Stream vidéo principal
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            video_info['video_stream'] = video_stream
            
            # Stream audio principal
            audio_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'audio'), None)
            video_info['audio_stream'] = audio_stream
            
        except Exception as e:
            self.logger.debug(f"Erreur ffprobe: {e}")
        
        return video_info
    
    def _extract_video_dimensions(self, video_info: Dict[str, Any]) -> MediaDimensions:
        """Extrait les dimensions vidéo"""        dimensions = MediaDimensions()
        
        try:
            video_stream = video_info.get('video_stream')
            if video_stream:
                dimensions.width = int(video_stream.get('width', 0))
                dimensions.height = int(video_stream.get('height', 0))
                dimensions.fps = eval(video_stream.get('r_frame_rate', '0/1'))
                dimensions.duration = float(video_stream.get('duration', 0))
                
                # Aspect ratio
                if dimensions.width and dimensions.height:
                    from math import gcd
                    ratio_gcd = gcd(dimensions.width, dimensions.height)
                    dimensions.aspect_ratio = f"{dimensions.width//ratio_gcd}:{dimensions.height//ratio_gcd}"
            
            # Bitrate total
            format_info = video_info.get('format', {})
            if 'bit_rate' in format_info:
                dimensions.bitrate = int(format_info['bit_rate'])
            
            # Informations audio
            audio_stream = video_info.get('audio_stream')
            if audio_stream:
                dimensions.sample_rate = int(audio_stream.get('sample_rate', 0))
                dimensions.channels = int(audio_stream.get('channels', 0))
                
        except Exception as e:
            self.logger.debug(f"Erreur dimensions vidéo: {e}")
        
        return dimensions
    
    def _extract_creative_from_video(self, video_info: Dict[str, Any]) -> CreativeMetadata:
        """Extrait les métadonnées créatives depuis les tags vidéo"""        creative = CreativeMetadata()
        
        try:
            format_info = video_info.get('format', {})
            tags = format_info.get('tags', {})
            
            # Mapping des tags vidéo
            creative.title = tags.get('title') or tags.get('Title')
            creative.description = tags.get('comment') or tags.get('Comment')
            creative.creator = tags.get('artist') or tags.get('Artist')
            creative.copyright = tags.get('copyright') or tags.get('Copyright')
            
            # Genre depuis tags
            genre = tags.get('genre') or tags.get('Genre')
            if genre:
                creative.genre = genre
            
            # Codec comme style
            video_stream = video_info.get('video_stream')
            if video_stream:
                codec = video_stream.get('codec_name')
                if codec:
                    creative.style = f"Codec: {codec.upper()}"
                    
        except Exception as e:
            self.logger.debug(f"Erreur extraction créative vidéo: {e}")
        
        return creative
    
    def _perform_video_ai_analysis(self, file_path: str) -> Dict[str, Any]:
        """Effectue une analyse IA de la vidéo"""        ai_analysis = {}
        
        try:
            # Analyse d'une frame représentative
            cap = cv2.VideoCapture(file_path)
            
            if cap.isOpened():
                # Frame du milieu
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                mid_frame = frame_count // 2
                cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
                
                ret, frame = cap.read()
                if ret:
                    # Analyse de mouvement (basique)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Détection de contours pour activité
                    edges = cv2.Canny(gray, 50, 150)
                    edge_density = np.sum(edges > 0) / edges.size
                    
                    ai_analysis['edge_density'] = float(edge_density)
                    
                    if edge_density > 0.1:
                        ai_analysis['content_type'] = 'high_detail'
                    elif edge_density > 0.05:
                        ai_analysis['content_type'] = 'medium_detail'
                    else:
                        ai_analysis['content_type'] = 'low_detail'
                    
                    # Luminosité moyenne
                    avg_brightness = np.mean(gray)
                    ai_analysis['avg_brightness'] = float(avg_brightness)
                    
                    # Tags générés
                    tags = ['video']
                    if avg_brightness < 100:
                        tags.append('dark')
                    elif avg_brightness > 200:
                        tags.append('bright')
                    
                    if edge_density > 0.1:
                        tags.append('detailed')
                    
                    ai_analysis['generated_tags'] = tags
            
            cap.release()
            
        except Exception as e:
            self.logger.debug(f"Erreur analyse IA vidéo: {e}")
        
        return ai_analysis
    
    def _create_error_metadata(self, file_path: str, error: str) -> ContentMetadata:
        """Crée des métadonnées d'erreur"""        return ContentMetadata(
            file_path=file_path,
            technical=TechnicalMetadata(
                file_size=0,
                file_format="UNKNOWN",
                mime_type="video/unknown"
            ),
            dimensions=MediaDimensions(),
            creative=CreativeMetadata(),
            business=BusinessMetadata(),
            ai_analysis={"error": error}
        )

class TextMetadataExtractor:
    """Extracteur de métadonnées de texte avancé"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TextMetadataExtractor")
        
        # Modèles IA pour analyse de texte
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.summarizer = pipeline("summarization", 
                                     model="facebook/bart-large-cnn")
        except Exception as e:
            self.logger.warning(f"Impossible de charger les modèles IA texte: {e}")
            self.sentiment_analyzer = None
            self.summarizer = None
    
    def extract_metadata(self, file_path: str) -> ContentMetadata:
        """Extrait toutes les métadonnées d'un fichier texte"""        try:
            # Lecture du contenu
            content = self._read_text_content(file_path)
            
            # Métadonnées techniques
            technical = self._extract_technical_metadata(file_path, content)
            
            # Dimensions texte
            dimensions = self._extract_text_dimensions(content)
            
            # Métadonnées créatives
            creative = self._extract_creative_from_text(content)
            
            # Analyse IA
            ai_analysis = self._perform_text_ai_analysis(content)
            
            # Métadonnées business
            business = BusinessMetadata()
            
            return ContentMetadata(
                file_path=file_path,
                technical=technical,
                dimensions=dimensions,
                creative=creative,
                business=business,
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Erreur extraction métadonnées texte {file_path}: {e}")
            return self._create_error_metadata(file_path, str(e))
    
    def _read_text_content(self, file_path: str) -> str:
        """Lit le contenu du fichier texte avec détection d'encodage"""        try:
            # Détection d'encodage
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result['encoding'] or 'utf-8'
            
            # Lecture avec l'encodage détecté
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            self.logger.error(f"Erreur lecture fichier texte: {e}")
            return ""
    
    def _extract_technical_metadata(self, file_path: str, content: str) -> TechnicalMetadata:
        """Extrait les métadonnées techniques texte"""        file_stat = os.stat(file_path)
        
        # Hash du contenu
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Encodage
        encoding = 'utf-8'  # Par défaut après conversion
        
        return TechnicalMetadata(
            file_size=file_stat.st_size,
            file_format=Path(file_path).suffix[1:].upper() or 'TXT',
            mime_type=mime_type or 'text/plain',
            creation_date=datetime.fromtimestamp(file_stat.st_ctime),
            modification_date=datetime.fromtimestamp(file_stat.st_mtime),
            file_hash=content_hash,
            encoding=encoding
        )
    
    def _extract_text_dimensions(self, content: str) -> MediaDimensions:
        """Extrait les dimensions du texte"""        dimensions = MediaDimensions()
        
        # Statistiques basiques
        char_count = len(content)
        word_count = len(content.split())
        line_count = content.count('\n') + 1
        
        # Estimation temps de lecture (250 mots/minute)
        reading_time = word_count / 250 * 60  # en secondes
        
        # Utilisation créative des champs
        dimensions.width = word_count  # Nombre de mots
        dimensions.height = line_count  # Nombre de lignes
        dimensions.duration = reading_time  # Temps de lecture
        
        return dimensions
    
    def _extract_creative_from_text(self, content: str) -> CreativeMetadata:
        """Extrait les métadonnées créatives du texte"""        creative = CreativeMetadata()
        
        # Titre depuis la première ligne
        lines = content.split('\n')
        if lines:
            first_line = lines[0].strip()
            if len(first_line) < 100:  # Probablement un titre
                creative.title = first_line
        
        # Description depuis les premières phrases
        sentences = content.split('.')[:3]
        if sentences:
            creative.description = '. '.join(sentences).strip()[:200]
        
        # Détection de langue
        try:
            detected_lang = detect(content)
            creative.style = f"Language: {detected_lang}"
        except LangDetectError:
            creative.style = "Language: unknown"
        
        # Mots-clés par fréquence
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignorer mots courts
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top mots-clés
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        creative.keywords = [word for word, freq in top_words]
        
        return creative
    
    def _perform_text_ai_analysis(self, content: str) -> Dict[str, Any]:
        """Effectue une analyse IA du texte"""        ai_analysis = {}
        
        try:
            # Statistiques de lisibilité
            ai_analysis['readability'] = {
                'flesch_reading_ease': textstat.flesch_reading_ease(content),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(content),
                'automated_readability_index': textstat.automated_readability_index(content)
            }
            
            # Analyse de sentiment
            if self.sentiment_analyzer and len(content) < 512:  # Limite du modèle
                sentiment = self.sentiment_analyzer(content[:512])
                ai_analysis['sentiment'] = sentiment[0]
            
            # Résumé automatique
            if self.summarizer and len(content) > 100:
                # Troncature pour le modèle
                text_for_summary = content[:1024]
                summary = self.summarizer(text_for_summary, max_length=50, min_length=10)
                ai_analysis['summary'] = summary[0]['summary_text']
            
            # Classification basique du type de texte
            content_lower = content.lower()
            
            if any(word in content_lower for word in ['chapitre', 'chapter', 'introduction']):
                ai_analysis['text_type'] = 'book/document'
            elif any(word in content_lower for word in ['dear', 'sincerely', 'regards']):
                ai_analysis['text_type'] = 'letter/email'
            elif content.count('\n') > content.count('.'):
                ai_analysis['text_type'] = 'list/code'
            else:
                ai_analysis['text_type'] = 'article/essay'
            
            # Tags générés
            tags = ['text', ai_analysis.get('text_type', 'document')]
            
            readability_score = ai_analysis['readability']['flesch_reading_ease']
            if readability_score > 70:
                tags.append('easy_read')
            elif readability_score < 30:
                tags.append('difficult_read')
            
            ai_analysis['generated_tags'] = tags
            
        except Exception as e:
            self.logger.debug(f"Erreur analyse IA texte: {e}")
        
        return ai_analysis
    
    def _create_error_metadata(self, file_path: str, error: str) -> ContentMetadata:
        """Crée des métadonnées d'erreur"""        return ContentMetadata(
            file_path=file_path,
            technical=TechnicalMetadata(
                file_size=0,
                file_format="UNKNOWN",
                mime_type="text/plain"
            ),
            dimensions=MediaDimensions(),
            creative=CreativeMetadata(),
            business=BusinessMetadata(),
            ai_analysis={"error": error}
        )

class MetadataExtractor:
    """Extracteur de métadonnées principal multi-format"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MetadataExtractor")
        
        # Extracteurs spécialisés
        self.image_extractor = ImageMetadataExtractor()
        self.audio_extractor = AudioMetadataExtractor()
        self.video_extractor = VideoMetadataExtractor()
        self.text_extractor = TextMetadataExtractor()
        
        # Cache des métadonnées
        self._metadata_cache: Dict[str, ContentMetadata] = {}
        
        # Types de fichiers supportés
        self.supported_types = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'audio': ['.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
            'text': ['.txt', '.md', '.rst', '.doc', '.docx', '.pdf']
        }
    
    def extract_metadata(self, file_path: str, force_refresh: bool = False) -> ContentMetadata:
        """Extrait les métadonnées selon le type de fichier"""        
        # Vérification du cache
        if not force_refresh and file_path in self._metadata_cache:
            return self._metadata_cache[file_path]
        
        try:
            # Détection du type de contenu
            content_type = self._detect_content_type(file_path)
            
            # Extraction selon le type
            if content_type == 'image':
                metadata = self.image_extractor.extract_metadata(file_path)
            elif content_type == 'audio':
                metadata = self.audio_extractor.extract_metadata(file_path)
            elif content_type == 'video':
                metadata = self.video_extractor.extract_metadata(file_path)
            elif content_type == 'text':
                metadata = self.text_extractor.extract_metadata(file_path)
            else:
                metadata = self._create_unsupported_metadata(file_path, content_type)
            
            # Mise en cache
            self._metadata_cache[file_path] = metadata
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erreur extraction métadonnées {file_path}: {e}")
            return self._create_error_metadata(file_path, str(e))
    
    def _detect_content_type(self, file_path: str) -> str:
        """Détecte le type de contenu du fichier"""        file_extension = Path(file_path).suffix.lower()
        
        for content_type, extensions in self.supported_types.items():
            if file_extension in extensions:
                return content_type
        
        # Tentative avec magic/mimetype
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                if mime_type.startswith('image/'):
                    return 'image'
                elif mime_type.startswith('audio/'):
                    return 'audio'
                elif mime_type.startswith('video/'):
                    return 'video'
                elif mime_type.startswith('text/'):
                    return 'text'
        except Exception:
            pass
        
        return 'unknown'
    
    def _create_unsupported_metadata(self, file_path: str, content_type: str) -> ContentMetadata:
        """Crée des métadonnées pour fichier non supporté"""        file_stat = os.stat(file_path)
        
        technical = TechnicalMetadata(
            file_size=file_stat.st_size,
            file_format=Path(file_path).suffix[1:].upper() or 'UNKNOWN',
            mime_type=f'application/x-{content_type}',
            creation_date=datetime.fromtimestamp(file_stat.st_ctime),
            modification_date=datetime.fromtimestamp(file_stat.st_mtime)
        )
        
        return ContentMetadata(
            file_path=file_path,
            technical=technical,
            dimensions=MediaDimensions(),
            creative=CreativeMetadata(),
            business=BusinessMetadata(),
            ai_analysis={"status": f"unsupported_type_{content_type}"}
        )
    
    def _create_error_metadata(self, file_path: str, error: str) -> ContentMetadata:
        """Crée des métadonnées d'erreur"""        return ContentMetadata(
            file_path=file_path,
            technical=TechnicalMetadata(
                file_size=0,
                file_format="ERROR",
                mime_type="application/octet-stream"
            ),
            dimensions=MediaDimensions(),
            creative=CreativeMetadata(),
            business=BusinessMetadata(),
            ai_analysis={"error": error}
        )

class AsyncMetadataExtractor:
    """Version asynchrone de l'extracteur de métadonnées"""    
    def __init__(self, max_workers: int = 4):
        self.sync_extractor = MetadataExtractor()
        self.max_workers = max_workers
        self.logger = logging.getLogger(f"{__name__}.AsyncMetadataExtractor")
    
    async def extract_metadata(self, file_path: str, force_refresh: bool = False) -> ContentMetadata:
        """Extrait les métadonnées de manière asynchrone"""        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            metadata = await loop.run_in_executor(
                executor,
                self.sync_extractor.extract_metadata,
                file_path,
                force_refresh
            )
        
        return metadata
    
    async def extract_batch_metadata(self, file_paths: List[str], 
                                   force_refresh: bool = False) -> Dict[str, ContentMetadata]:
        """Extrait les métadonnées d'un lot de fichiers en parallèle"""        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            loop = asyncio.get_event_loop()
            
            # Création des tâches
            tasks = [
                loop.run_in_executor(
                    executor,
                    self.sync_extractor.extract_metadata,
                    file_path,
                    force_refresh
                )
                for file_path in file_paths
            ]
            
            # Exécution en parallèle
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Formatage des résultats
            metadata_results = {}
            for i, result in enumerate(results):
                file_path = file_paths[i]
                
                if isinstance(result, Exception):
                    metadata_results[file_path] = ContentMetadata(
                        file_path=file_path,
                        technical=TechnicalMetadata(
                            file_size=0,
                            file_format="ERROR",
                            mime_type="application/octet-stream"
                        ),
                        dimensions=MediaDimensions(),
                        creative=CreativeMetadata(),
                        business=BusinessMetadata(),
                        ai_analysis={"error": str(result)}
                    )
                else:
                    metadata_results[file_path] = result
            
            return metadata_results

# Export des classes principales
__all__ = [
    'MetadataExtractor',
    'AsyncMetadataExtractor',
    'ContentMetadata',
    'TechnicalMetadata',
    'MediaDimensions',
    'CreativeMetadata',
    'BusinessMetadata',
    'GeolocationData',
    'ImageMetadataExtractor',
    'AudioMetadataExtractor',
    'VideoMetadataExtractor',
    'TextMetadataExtractor'
]
