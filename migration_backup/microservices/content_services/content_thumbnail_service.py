"""
📸 Content Thumbnail Service - Génération de Thumbnails Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service spécialisé de génération automatique de thumbnails pour tous types de contenu.
Support multi-format avec optimisation IA et génération intelligente.
"""

import asyncio
import io
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from pathlib import Path
import logging

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import waveform

logger = logging.getLogger(__name__)


class ContentThumbnailService:
    """Service de génération de thumbnails intelligents pour contenu multi-format"""
    
    def __init__(self):
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        self.supported_audio_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        self.thumbnail_sizes = {
            'small': (150, 150),
            'medium': (300, 300),
            'large': (600, 600),
            'youtube': (1280, 720),
            'instagram': (1080, 1080),
            'tiktok': (1080, 1920)
        }
    
    async def generate_thumbnail(
        self,
        content_id: str,
        file_path: str,
        content_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Génère un thumbnail pour le contenu spécifié"""
        try:
            options = options or {}
            
            # Déterminer le type de contenu
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension in self.supported_video_formats:
                thumbnail_data = await self._generate_video_thumbnail(
                    file_path, options
                )
            elif file_extension in self.supported_image_formats:
                thumbnail_data = await self._generate_image_thumbnail(
                    file_path, options
                )
            elif file_extension in self.supported_audio_formats:
                thumbnail_data = await self._generate_audio_thumbnail(
                    file_path, options
                )
            else:
                thumbnail_data = await self._generate_default_thumbnail(
                    content_type, options
                )
            
            return {
                'content_id': content_id,
                'thumbnail_data': thumbnail_data,
                'generated_at': datetime.utcnow().isoformat(),
                'status': 'success',
                'formats_generated': list(thumbnail_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Erreur génération thumbnail {content_id}: {e}")
            return {
                'content_id': content_id,
                'error': str(e),
                'status': 'error',
                'generated_at': datetime.utcnow().isoformat()
            }
    
    async def _generate_video_thumbnail(
        self,
        video_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, bytes]:
        """Génère des thumbnails pour vidéos"""
        thumbnails = {}
        
        try:
            # Extraire frame au milieu de la vidéo
            with VideoFileClip(video_path) as clip:
                duration = clip.duration
                frame_time = duration / 2  # Frame au milieu
                
                frame = clip.get_frame(frame_time)
                frame_image = Image.fromarray(frame)
                
                # Générer différentes tailles
                for size_name, dimensions in self.thumbnail_sizes.items():
                    resized = self._resize_with_aspect_ratio(frame_image, dimensions)
                    
                    # Amélioration IA optionnelle
                    if options.get('ai_enhancement', False):
                        resized = await self._ai_enhance_thumbnail(resized)
                    
                    # Convertir en bytes
                    img_bytes = io.BytesIO()
                    resized.save(img_bytes, format='JPEG', quality=90)
                    thumbnails[size_name] = img_bytes.getvalue()
                
        except Exception as e:
            logger.error(f"Erreur génération thumbnail vidéo: {e}")
            raise
        
        return thumbnails
    
    async def _generate_image_thumbnail(
        self,
        image_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, bytes]:
        """Génère des thumbnails pour images"""
        thumbnails = {}
        
        try:
            with Image.open(image_path) as img:
                # Convertir en RGB si nécessaire
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Générer différentes tailles
                for size_name, dimensions in self.thumbnail_sizes.items():
                    resized = self._resize_with_aspect_ratio(img, dimensions)
                    
                    # Amélioration IA optionnelle
                    if options.get('ai_enhancement', False):
                        resized = await self._ai_enhance_thumbnail(resized)
                    
                    # Convertir en bytes
                    img_bytes = io.BytesIO()
                    resized.save(img_bytes, format='JPEG', quality=90)
                    thumbnails[size_name] = img_bytes.getvalue()
                
        except Exception as e:
            logger.error(f"Erreur génération thumbnail image: {e}")
            raise
        
        return thumbnails
    
    async def _generate_audio_thumbnail(
        self,
        audio_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, bytes]:
        """Génère des thumbnails pour audio (waveform)"""
        thumbnails = {}
        
        try:
            # Générer waveform
            for size_name, dimensions in self.thumbnail_sizes.items():
                waveform_img = await self._create_waveform_image(
                    audio_path, dimensions
                )
                
                # Convertir en bytes
                img_bytes = io.BytesIO()
                waveform_img.save(img_bytes, format='PNG', quality=90)
                thumbnails[size_name] = img_bytes.getvalue()
                
        except Exception as e:
            logger.error(f"Erreur génération thumbnail audio: {e}")
            raise
        
        return thumbnails
    
    async def _generate_default_thumbnail(
        self,
        content_type: str,
        options: Dict[str, Any]
    ) -> Dict[str, bytes]:
        """Génère des thumbnails par défaut pour types non supportés"""
        thumbnails = {}
        
        try:
            for size_name, dimensions in self.thumbnail_sizes.items():
                # Créer image par défaut avec icône du type
                default_img = self._create_default_image(
                    dimensions, content_type
                )
                
                # Convertir en bytes
                img_bytes = io.BytesIO()
                default_img.save(img_bytes, format='PNG', quality=90)
                thumbnails[size_name] = img_bytes.getvalue()
                
        except Exception as e:
            logger.error(f"Erreur génération thumbnail par défaut: {e}")
            raise
        
        return thumbnails
    
    def _resize_with_aspect_ratio(
        self,
        image: Image.Image,
        target_size: tuple
    ) -> Image.Image:
        """Redimensionne en conservant le ratio d'aspect"""
        # Calculer la taille pour conserver le ratio
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Image plus large - ajuster par la largeur
            new_width = target_size[0]
            new_height = int(target_size[0] / img_ratio)
        else:
            # Image plus haute - ajuster par la hauteur
            new_height = target_size[1]
            new_width = int(target_size[1] * img_ratio)
        
        # Redimensionner
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Créer image finale avec fond
        final_img = Image.new('RGB', target_size, (255, 255, 255))
        
        # Centrer l'image redimensionnée
        x_offset = (target_size[0] - new_width) // 2
        y_offset = (target_size[1] - new_height) // 2
        final_img.paste(resized, (x_offset, y_offset))
        
        return final_img
    
    async def _ai_enhance_thumbnail(self, image: Image.Image) -> Image.Image:
        """Améliore le thumbnail avec IA (placeholder)"""
        # TODO: Intégrer modèle IA d'amélioration d'image
        # Pour l'instant, applique un filtre de netteté
        return image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    
    async def _create_waveform_image(
        self,
        audio_path: str,
        dimensions: tuple
    ) -> Image.Image:
        """Crée une image de waveform pour audio"""
        # Créer image de base
        img = Image.new('RGB', dimensions, (30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Simuler waveform (placeholder - à remplacer par vraie analyse audio)
        center_y = dimensions[1] // 2
        
        for x in range(0, dimensions[0], 2):
            # Hauteur aléatoire pour simuler waveform
            height = np.random.randint(10, dimensions[1] // 3)
            
            # Dessiner ligne verticale
            draw.line([
                (x, center_y - height // 2),
                (x, center_y + height // 2)
            ], fill=(100, 200, 255), width=1)
        
        return img
    
    def _create_default_image(
        self,
        dimensions: tuple,
        content_type: str
    ) -> Image.Image:
        """Crée une image par défaut avec icône du type"""
        img = Image.new('RGB', dimensions, (240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Dessiner cadre
        draw.rectangle([10, 10, dimensions[0]-10, dimensions[1]-10], 
                      outline=(200, 200, 200), width=2)
        
        # Ajouter texte du type
        try:
            font_size = min(dimensions) // 8
            # Font par défaut si pas de font spécifique
            draw.text(
                (dimensions[0]//2, dimensions[1]//2),
                content_type.upper(),
                fill=(100, 100, 100),
                anchor="mm"
            )
        except:
            pass
        
        return img
    
    async def generate_platform_thumbnails(
        self,
        content_id: str,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Génère des thumbnails optimisés pour plateformes spécifiques"""
        platform_specs = {
            'youtube': {'size': (1280, 720), 'format': 'JPEG'},
            'instagram': {'size': (1080, 1080), 'format': 'JPEG'},
            'tiktok': {'size': (1080, 1920), 'format': 'JPEG'},
            'facebook': {'size': (1200, 630), 'format': 'JPEG'},
            'twitter': {'size': (1200, 675), 'format': 'JPEG'}
        }
        
        results = {}
        
        for platform in platforms:
            if platform in platform_specs:
                spec = platform_specs[platform]
                # Générer thumbnail spécifique à la plateforme
                results[platform] = await self._generate_platform_specific_thumbnail(
                    content_id, spec
                )
        
        return results
    
    async def _generate_platform_specific_thumbnail(
        self,
        content_id: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère un thumbnail pour une plateforme spécifique"""
        # Placeholder - à implémenter selon les besoins spécifiques
        return {
            'content_id': content_id,
            'size': spec['size'],
            'format': spec['format'],
            'generated_at': datetime.utcnow().isoformat()
        }


# Instance globale du service
content_thumbnail_service = ContentThumbnailService()