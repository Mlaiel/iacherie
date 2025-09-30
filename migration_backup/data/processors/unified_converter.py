#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚠️ AVERTISSEMENT: Ce module fait partie du système propriétaire Ainflue
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
© 2024 Ainflue - Tous droits réservés
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime
from enum import Enum

try:
    import ffmpeg
    import pillow_heif
    from PIL import Image, ImageEnhance
    import pydub
    from moviepy.editor import VideoFileClip, AudioFileClip
    import fitz  # PyMuPDF
    import python_docx
    import pandas as pd
    import cv2
    import numpy as np
except ImportError as e:
    logging.warning(f"Dépendance optionnelle manquante: {e}")

from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
from .image_processor import ImageProcessor
from .text_processor import TextProcessor
from .metadata_processor import MetadataProcessor


class ConversionFormat(Enum):
    """Formats de conversion supportés"""
    # Audio
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    
    # Video
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    
    # Image
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    HEIC = "heic"
    
    # Document
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"


class ConversionProfile(Enum):
    """Profils de conversion optimisés"""
    # Qualité
    ULTRA_HIGH = "ultra_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    # Usage spécialisé
    WEB_OPTIMIZED = "web_optimized"
    MOBILE_OPTIMIZED = "mobile_optimized"
    STREAMING = "streaming"
    ARCHIVE = "archive"
    
    # Plateformes
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"


class UnifiedConverter:
    """
    Convertisseur unifié multi-format avec optimisations IA
    
    Supports:
    - Audio: MP3, WAV, FLAC, OGG, M4A
    - Video: MP4, AVI, MOV, MKV, WEBM
    - Image: JPEG, PNG, WEBP, AVIF, HEIC
    - Document: PDF, DOCX, TXT, MD, HTML
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "ainflue_converter"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Processeurs spécialisés
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        self.metadata_processor = MetadataProcessor()
        
        # Configuration des profils
        self._init_conversion_profiles()
        
        # Statistiques
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'formats_converted': set(),
            'total_size_processed': 0
        }
    
    def _init_conversion_profiles(self):
        """Initialise les profils de conversion"""
        self.profiles = {
            # Profils audio
            ConversionProfile.ULTRA_HIGH: {
                'audio': {'bitrate': '320k', 'sample_rate': 48000, 'codec': 'libmp3lame'},
                'video': {'bitrate': '8000k', 'resolution': '3840x2160', 'fps': 60},
                'image': {'quality': 100, 'optimize': False}
            },
            ConversionProfile.HIGH: {
                'audio': {'bitrate': '192k', 'sample_rate': 44100, 'codec': 'libmp3lame'},
                'video': {'bitrate': '4000k', 'resolution': '1920x1080', 'fps': 30},
                'image': {'quality': 90, 'optimize': True}
            },
            ConversionProfile.MEDIUM: {
                'audio': {'bitrate': '128k', 'sample_rate': 44100, 'codec': 'libmp3lame'},
                'video': {'bitrate': '2000k', 'resolution': '1280x720', 'fps': 30},
                'image': {'quality': 80, 'optimize': True}
            },
            ConversionProfile.WEB_OPTIMIZED: {
                'audio': {'bitrate': '128k', 'sample_rate': 44100, 'codec': 'libmp3lame'},
                'video': {'bitrate': '1500k', 'resolution': '1280x720', 'fps': 30, 'codec': 'libx264'},
                'image': {'quality': 85, 'optimize': True, 'progressive': True}
            },
            ConversionProfile.MOBILE_OPTIMIZED: {
                'audio': {'bitrate': '96k', 'sample_rate': 44100, 'codec': 'aac'},
                'video': {'bitrate': '1000k', 'resolution': '854x480', 'fps': 24, 'codec': 'libx264'},
                'image': {'quality': 75, 'optimize': True, 'format': 'webp'}
            },
            ConversionProfile.YOUTUBE: {
                'video': {'bitrate': '8000k', 'resolution': '1920x1080', 'fps': 30, 'codec': 'libx264'},
                'audio': {'bitrate': '192k', 'sample_rate': 48000, 'codec': 'aac'}
            },
            ConversionProfile.INSTAGRAM: {
                'video': {'bitrate': '3500k', 'resolution': '1080x1080', 'fps': 30, 'codec': 'libx264'},
                'audio': {'bitrate': '128k', 'sample_rate': 44100, 'codec': 'aac'},
                'image': {'quality': 85, 'format': 'jpeg', 'max_size': (1080, 1080)}
            },
            ConversionProfile.TIKTOK: {
                'video': {'bitrate': '2000k', 'resolution': '1080x1920', 'fps': 30, 'codec': 'libx264'},
                'audio': {'bitrate': '128k', 'sample_rate': 44100, 'codec': 'aac'}
            }
        }
    
    async def convert_file(
        self,
        input_path: Path,
        output_format: ConversionFormat,
        profile: ConversionProfile = ConversionProfile.HIGH,
        output_path: Optional[Path] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Convertit un fichier vers le format spécifié
        
        Args:
            input_path: Chemin du fichier source
            output_format: Format de sortie
            profile: Profil de conversion
            output_path: Chemin de sortie (optionnel)
            metadata: Métadonnées à préserver
            
        Returns:
            Résultat de conversion avec statistiques
        """
        try:
            if not input_path.exists():
                raise FileNotFoundError(f"Fichier source introuvable: {input_path}")
            
            # Détection du type de fichier
            file_type = self._detect_file_type(input_path)
            if not file_type:
                raise ValueError(f"Type de fichier non supporté: {input_path}")
            
            # Génération du chemin de sortie
            if not output_path:
                output_path = self._generate_output_path(input_path, output_format)
            
            start_time = datetime.now()
            file_size = input_path.stat().st_size
            
            # Conversion selon le type
            result = await self._convert_by_type(
                input_path, output_path, file_type, output_format, profile, metadata
            )
            
            # Mise à jour des statistiques
            conversion_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, file_size, str(output_format.value))
            
            result.update({
                'success': True,
                'input_path': str(input_path),
                'output_path': str(output_path),
                'input_size': file_size,
                'output_size': output_path.stat().st_size if output_path.exists() else 0,
                'conversion_time': conversion_time,
                'compression_ratio': self._calculate_compression_ratio(
                    file_size, output_path.stat().st_size if output_path.exists() else 0
                )
            })
            
            self.logger.info(f"Conversion réussie: {input_path} -> {output_path}")
            return result
            
        except Exception as e:
            self._update_stats(False, 0, str(output_format.value))
            self.logger.error(f"Erreur de conversion: {e}")
            return {
                'success': False,
                'error': str(e),
                'input_path': str(input_path),
                'output_format': output_format.value
            }
    
    async def batch_convert(
        self,
        input_files: List[Path],
        output_format: ConversionFormat,
        profile: ConversionProfile = ConversionProfile.HIGH,
        output_dir: Optional[Path] = None,
        max_concurrent: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Conversion par lot avec traitement concurrent
        
        Args:
            input_files: Liste des fichiers à convertir
            output_format: Format de sortie
            profile: Profil de conversion
            output_dir: Répertoire de sortie
            max_concurrent: Nombre max de conversions simultanées
            
        Returns:
            Liste des résultats de conversion
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def convert_with_semaphore(file_path: Path) -> Dict[str, Any]:
            async with semaphore:
                output_path = None
                if output_dir:
                    output_path = output_dir / f"{file_path.stem}.{output_format.value}"
                return await self.convert_file(file_path, output_format, profile, output_path)
        
        tasks = [convert_with_semaphore(file_path) for file_path in input_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'input_path': str(input_files[i]),
                    'output_format': output_format.value
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _convert_by_type(
        self,
        input_path: Path,
        output_path: Path,
        file_type: str,
        output_format: ConversionFormat,
        profile: ConversionProfile,
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Conversion selon le type de fichier"""
        
        if file_type == 'audio':
            return await self._convert_audio(input_path, output_path, output_format, profile, metadata)
        elif file_type == 'video':
            return await self._convert_video(input_path, output_path, output_format, profile, metadata)
        elif file_type == 'image':
            return await self._convert_image(input_path, output_path, output_format, profile, metadata)
        elif file_type == 'document':
            return await self._convert_document(input_path, output_path, output_format, profile, metadata)
        else:
            raise ValueError(f"Type de fichier non supporté: {file_type}")
    
    async def _convert_audio(
        self,
        input_path: Path,
        output_path: Path,
        output_format: ConversionFormat,
        profile: ConversionProfile,
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Conversion audio avec optimisations"""
        
        profile_settings = self.profiles.get(profile, {}).get('audio', {})
        
        try:
            # Utilisation de FFmpeg pour une conversion optimisée
            input_stream = ffmpeg.input(str(input_path))
            
            # Configuration de l'encodage
            kwargs = {}
            if 'bitrate' in profile_settings:
                kwargs['audio_bitrate'] = profile_settings['bitrate']
            if 'sample_rate' in profile_settings:
                kwargs['ar'] = profile_settings['sample_rate']
            if 'codec' in profile_settings:
                kwargs['acodec'] = profile_settings['codec']
            
            # Préservation des métadonnées
            if metadata:
                for key, value in metadata.items():
                    if key in ['title', 'artist', 'album', 'genre']:
                        kwargs[f'metadata:{key}'] = value
            
            output_stream = ffmpeg.output(input_stream, str(output_path), **kwargs)
            await asyncio.create_subprocess_exec(
                *ffmpeg.compile(output_stream, overwrite_output=True),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Analyse post-conversion
            analysis = await self.audio_processor.analyze_audio(output_path)
            
            return {
                'type': 'audio',
                'format': output_format.value,
                'profile': profile.value,
                'analysis': analysis,
                'metadata_preserved': bool(metadata)
            }
            
        except Exception as e:
            # Fallback avec pydub
            self.logger.warning(f"FFmpeg échec, fallback pydub: {e}")
            audio = pydub.AudioSegment.from_file(str(input_path))
            
            # Application des paramètres du profil
            if 'sample_rate' in profile_settings:
                audio = audio.set_frame_rate(profile_settings['sample_rate'])
            
            # Export
            export_params = {}
            if 'bitrate' in profile_settings:
                export_params['bitrate'] = profile_settings['bitrate']
            
            audio.export(str(output_path), format=output_format.value, **export_params)
            
            return {
                'type': 'audio',
                'format': output_format.value,
                'profile': profile.value,
                'fallback_used': True
            }
    
    async def _convert_video(
        self,
        input_path: Path,
        output_path: Path,
        output_format: ConversionFormat,
        profile: ConversionProfile,
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Conversion vidéo avec optimisations"""
        
        profile_settings = self.profiles.get(profile, {}).get('video', {})
        
        try:
            # Configuration FFmpeg
            input_stream = ffmpeg.input(str(input_path))
            
            kwargs = {}
            if 'bitrate' in profile_settings:
                kwargs['video_bitrate'] = profile_settings['bitrate']
            if 'resolution' in profile_settings:
                width, height = profile_settings['resolution'].split('x')
                kwargs['s'] = f"{width}x{height}"
            if 'fps' in profile_settings:
                kwargs['r'] = profile_settings['fps']
            if 'codec' in profile_settings:
                kwargs['vcodec'] = profile_settings['codec']
            
            # Paramètres audio
            audio_settings = self.profiles.get(profile, {}).get('audio', {})
            if audio_settings:
                if 'codec' in audio_settings:
                    kwargs['acodec'] = audio_settings['codec']
                if 'bitrate' in audio_settings:
                    kwargs['audio_bitrate'] = audio_settings['bitrate']
            
            output_stream = ffmpeg.output(input_stream, str(output_path), **kwargs)
            process = await asyncio.create_subprocess_exec(
                *ffmpeg.compile(output_stream, overwrite_output=True),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            # Analyse post-conversion
            analysis = await self.video_processor.analyze_video(output_path)
            
            return {
                'type': 'video',
                'format': output_format.value,
                'profile': profile.value,
                'analysis': analysis,
                'has_audio': analysis.get('has_audio', False)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur conversion vidéo: {e}")
            raise
    
    async def _convert_image(
        self,
        input_path: Path,
        output_path: Path,
        output_format: ConversionFormat,
        profile: ConversionProfile,
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Conversion image avec optimisations"""
        
        profile_settings = self.profiles.get(profile, {}).get('image', {})
        
        try:
            # Support HEIC/HEIF
            if input_path.suffix.lower() in ['.heic', '.heif']:
                pillow_heif.register_heif_opener()
            
            with Image.open(input_path) as img:
                # Conversion en RGB si nécessaire
                if img.mode in ('RGBA', 'LA', 'P'):
                    if output_format in [ConversionFormat.JPEG]:
                        # Fond blanc pour JPEG
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif output_format in [ConversionFormat.PNG, ConversionFormat.WEBP]:
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionnement si spécifié
                if 'max_size' in profile_settings:
                    max_width, max_height = profile_settings['max_size']
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Amélioration de l'image si profile élevé
                if profile in [ConversionProfile.ULTRA_HIGH, ConversionProfile.HIGH]:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.1)  # Légère amélioration
                
                # Paramètres de sauvegarde
                save_kwargs = {}
                if 'quality' in profile_settings:
                    save_kwargs['quality'] = profile_settings['quality']
                if 'optimize' in profile_settings:
                    save_kwargs['optimize'] = profile_settings['optimize']
                if 'progressive' in profile_settings and output_format == ConversionFormat.JPEG:
                    save_kwargs['progressive'] = profile_settings['progressive']
                
                # Préservation des métadonnées EXIF
                if metadata and output_format in [ConversionFormat.JPEG]:
                    save_kwargs['exif'] = img.info.get('exif', b'')
                
                # Sauvegarde
                img.save(output_path, format=output_format.value.upper(), **save_kwargs)
                
                # Analyse post-conversion
                analysis = await self.image_processor.analyze_image(output_path)
                
                return {
                    'type': 'image',
                    'format': output_format.value,
                    'profile': profile.value,
                    'analysis': analysis,
                    'original_size': img.size if 'img' in locals() else None
                }
                
        except Exception as e:
            self.logger.error(f"Erreur conversion image: {e}")
            raise
    
    async def _convert_document(
        self,
        input_path: Path,
        output_path: Path,
        output_format: ConversionFormat,
        profile: ConversionProfile,
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """Conversion de documents"""
        
        input_ext = input_path.suffix.lower()
        
        try:
            if input_ext == '.pdf' and output_format == ConversionFormat.TXT:
                # PDF vers texte
                doc = fitz.open(input_path)
                text_content = ""
                for page in doc:
                    text_content += page.get_text()
                doc.close()
                
                output_path.write_text(text_content, encoding='utf-8')
                
            elif input_ext == '.docx' and output_format == ConversionFormat.TXT:
                # DOCX vers texte
                doc = python_docx.Document(input_path)
                text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                output_path.write_text(text_content, encoding='utf-8')
                
            elif output_format == ConversionFormat.PDF:
                # Conversion vers PDF (nécessite une bibliothèque spécialisée)
                raise NotImplementedError("Conversion vers PDF non implémentée")
                
            else:
                raise ValueError(f"Conversion {input_ext} -> {output_format.value} non supportée")
            
            # Analyse du document
            analysis = await self.text_processor.analyze_text(output_path.read_text(encoding='utf-8'))
            
            return {
                'type': 'document',
                'format': output_format.value,
                'profile': profile.value,
                'analysis': analysis
            }
            
        except Exception as e:
            self.logger.error(f"Erreur conversion document: {e}")
            raise
    
    def _detect_file_type(self, file_path: Path) -> Optional[str]:
        """Détecte le type de fichier"""
        ext = file_path.suffix.lower()
        
        audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
        image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.heic', '.heif', '.bmp', '.tiff'}
        document_exts = {'.pdf', '.docx', '.txt', '.md', '.html', '.rtf'}
        
        if ext in audio_exts:
            return 'audio'
        elif ext in video_exts:
            return 'video'
        elif ext in image_exts:
            return 'image'
        elif ext in document_exts:
            return 'document'
        
        return None
    
    def _generate_output_path(self, input_path: Path, output_format: ConversionFormat) -> Path:
        """Génère le chemin de sortie"""
        return input_path.parent / f"{input_path.stem}.{output_format.value}"
    
    def _calculate_compression_ratio(self, input_size: int, output_size: int) -> float:
        """Calcule le ratio de compression"""
        if input_size == 0:
            return 0.0
        return (input_size - output_size) / input_size * 100
    
    def _update_stats(self, success: bool, file_size: int, format_type: str):
        """Met à jour les statistiques"""
        self.conversion_stats['total_conversions'] += 1
        if success:
            self.conversion_stats['successful_conversions'] += 1
            self.conversion_stats['total_size_processed'] += file_size
            self.conversion_stats['formats_converted'].add(format_type)
        else:
            self.conversion_stats['failed_conversions'] += 1
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Retourne les formats supportés par type"""
        return {
            'audio': ['mp3', 'wav', 'flac', 'ogg', 'm4a'],
            'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
            'image': ['jpeg', 'png', 'webp', 'avif', 'heic'],
            'document': ['pdf', 'docx', 'txt', 'md', 'html']
        }
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de conversion"""
        stats = self.conversion_stats.copy()
        stats['formats_converted'] = list(stats['formats_converted'])
        stats['success_rate'] = (
            stats['successful_conversions'] / stats['total_conversions'] * 100
            if stats['total_conversions'] > 0 else 0
        )
        return stats
    
    async def optimize_for_platform(
        self,
        input_path: Path,
        platform: str,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Optimise un fichier pour une plateforme spécifique
        
        Args:
            input_path: Fichier source
            platform: Plateforme cible (youtube, instagram, tiktok, etc.)
            output_dir: Répertoire de sortie
            
        Returns:
            Résultat d'optimisation
        """
        platform_profiles = {
            'youtube': ConversionProfile.YOUTUBE,
            'instagram': ConversionProfile.INSTAGRAM,
            'tiktok': ConversionProfile.TIKTOK,
            'web': ConversionProfile.WEB_OPTIMIZED,
            'mobile': ConversionProfile.MOBILE_OPTIMIZED
        }
        
        profile = platform_profiles.get(platform.lower())
        if not profile:
            raise ValueError(f"Plateforme non supportée: {platform}")
        
        # Détection du format optimal
        file_type = self._detect_file_type(input_path)
        if file_type == 'video':
            output_format = ConversionFormat.MP4
        elif file_type == 'audio':
            output_format = ConversionFormat.MP3
        elif file_type == 'image':
            output_format = ConversionFormat.JPEG
        else:
            raise ValueError(f"Type de fichier non optimisable pour plateforme: {file_type}")
        
        # Génération du chemin de sortie
        if not output_dir:
            output_dir = input_path.parent
        
        output_path = output_dir / f"{input_path.stem}_{platform}.{output_format.value}"
        
        return await self.convert_file(input_path, output_format, profile, output_path)
    
    async def cleanup_cache(self, max_age_hours: int = 24):
        """Nettoie le cache de conversion"""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.cache_dir.rglob('*'):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (max_age_hours * 3600):
                        file_path.unlink()
                        self.logger.debug(f"Cache nettoyé: {file_path}")
            
            # Suppression des dossiers vides
            for dir_path in self.cache_dir.rglob('*'):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    
        except Exception as e:
            self.logger.error(f"Erreur nettoyage cache: {e}")


# Instance globale pour l'utilisation dans l'application
converter = UnifiedConverter()


async def convert_file_simple(
    input_path: str,
    output_format: str,
    quality: str = "high"
) -> Dict[str, Any]:
    """
    Interface simplifiée pour conversion de fichier
    
    Args:
        input_path: Chemin du fichier source
        output_format: Format de sortie (mp3, mp4, jpeg, etc.)
        quality: Qualité (ultra_high, high, medium, low, web_optimized)
        
    Returns:
        Résultat de conversion
    """
    try:
        format_enum = ConversionFormat(output_format.lower())
        profile_enum = ConversionProfile(quality.lower())
        
        return await converter.convert_file(
            Path(input_path),
            format_enum,
            profile_enum
        )
    except ValueError as e:
        return {
            'success': False,
            'error': f"Format ou qualité invalide: {e}"
        }


if __name__ == "__main__":
    # Test de conversion
    import sys
    
    async def test_conversion():
        if len(sys.argv) < 3:
            print("Usage: python unified_converter.py <input_file> <output_format>")
            return
        
        input_file = sys.argv[1]
        output_format = sys.argv[2]
        
        result = await convert_file_simple(input_file, output_format)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test_conversion())
