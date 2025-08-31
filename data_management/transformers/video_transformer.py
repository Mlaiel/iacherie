"""� Video Transformation Engine - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/data_management/transformers/video_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Video Processing Expert: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
"""
import asyncio
import logging
import time
import tempfile
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from moviepy.video.fx import resize, rotate, crop
from moviepy.audio.fx import audio_normalize
import torch
from torchvision import transforms
import face_recognition
from ultralytics import YOLO

from ..models.video_models import VideoMetadata, VideoQualityMetrics
from ...core.exceptions import VideoProcessingError, ValidationError
from ...core.config import get_settings
from ...utils.file_manager import FileManager
from ...utils.validation import validate_video_file

settings = get_settings()
logger = logging.getLogger(__name__)

class VideoFormat(Enum):
    """Formats vidéo supportés"""    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    M4V = "m4v"

class VideoCodec(Enum):
    """Codecs vidéo supportés"""    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    VP8 = "libvpx"
    AV1 = "libaom-av1"

class VideoQuality(Enum):
    """Niveaux de qualité vidéo"""    ULTRA = "ultra"      # 4K, bitrate élevé
    HIGH = "high"        # 1080p, bitrate optimisé
    STANDARD = "standard" # 720p, bitrate équilibré
    LOW = "low"          # 480p, bitrate compressé

class ContentType(Enum):
    """Types de contenu pour optimisation"""    MUSIC_VIDEO = "music_video"
    SOCIAL_MEDIA = "social_media"
    PODCAST = "podcast"
    TUTORIAL = "tutorial"
    GAMING = "gaming"
    VLOG = "vlog"
    LIVE_STREAM = "live_stream"

@dataclass
class VideoProcessingResult:
    """Résultat du traitement vidéo"""    success: bool
    input_file: str
    output_file: Optional[str]
    original_metadata: VideoMetadata
    processed_metadata: VideoMetadata
    quality_metrics: VideoQualityMetrics
    processing_time: float
    operations_performed: List[str]
    warnings: List[str]
    errors: List[str]

class VideoAnalyzer:
    """Analyseur vidéo intelligent pour créateurs de contenu"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chargement du modèle YOLO pour détection d'objets
        try:
            self.yolo_model = YOLO('yolov8n.pt')  # Version nano pour rapidité
        except Exception as e:
            self.logger.warning(f"YOLO non disponible: {e}")
            self.yolo_model = None
        
        # Transformations pour analyse IA
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def analyze_video_file(self, video_path: str) -> VideoMetadata:
        """Analyse complète d'un fichier vidéo"""        try:
            # Ouverture avec OpenCV pour analyse basique
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise VideoProcessingError(f"Impossible d'ouvrir la vidéo: {video_path}")
            
            # Métadonnées basiques
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Analyse des frames pour contenu
            scene_changes = self._detect_scene_changes(cap)
            motion_level = self._analyze_motion(cap)
            face_detection_results = self._analyze_faces(cap)
            object_detection_results = self._analyze_objects(cap)
            
            cap.release()
            
            # Analyse audio si présent
            audio_info = self._analyze_video_audio(video_path)
            
            # Calcul du bitrate estimé
            file_size = Path(video_path).stat().st_size
            bitrate = (file_size * 8) / duration if duration > 0 else 0
            
            # Classification automatique du contenu
            content_classification = self._classify_content_type(
                scene_changes, motion_level, face_detection_results, audio_info
            )
            
            return VideoMetadata(
                filename=Path(video_path).name,
                format=Path(video_path).suffix.lower().lstrip('.'),
                duration=float(duration),
                width=int(width),
                height=int(height),
                fps=float(fps),
                bitrate=int(bitrate),
                file_size=int(file_size),
                codec=self._detect_codec(video_path),
                
                # Métriques d'analyse
                scene_changes=len(scene_changes),
                motion_level=float(motion_level),
                faces_detected=len(face_detection_results),
                objects_detected=len(object_detection_results),
                
                # Audio
                has_audio=audio_info['has_audio'],
                audio_channels=audio_info.get('channels', 0),
                audio_sample_rate=audio_info.get('sample_rate', 0),
                
                # Classification
                content_type=content_classification,
                quality_score=self._calculate_quality_score(width, height, fps, bitrate),
                
                # Métadonnées étendues
                color_space="unknown",
                aspect_ratio=f"{width}:{height}",
                is_hdr=False,
                
                # Tags automatiques
                tags=self._generate_content_tags(face_detection_results, object_detection_results)
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse vidéo {video_path}: {e}")
            raise VideoProcessingError(f"Échec analyse vidéo: {str(e)}")
    
    def _detect_scene_changes(self, cap: cv2.VideoCapture) -> List[int]:
        """Détecte les changements de scène dans la vidéo"""        scene_changes = []
        prev_frame = None
        frame_idx = 0
        threshold = 0.3
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        # Analyse tous les 30 frames pour performance
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % 30 == 0:  # Échantillonnage
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (64, 64))  # Réduction pour rapidité
                
                if prev_frame is not None:
                    # Calcul de la différence
                    diff = cv2.absdiff(prev_frame, gray)
                    mean_diff = np.mean(diff) / 255.0
                    
                    if mean_diff > threshold:
                        scene_changes.append(frame_idx)
                
                prev_frame = gray
            
            frame_idx += 1
        
        return scene_changes
    
    def _analyze_motion(self, cap: cv2.VideoCapture) -> float:
        """Analyse le niveau de mouvement dans la vidéo"""        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        motion_scores = []
        prev_frame = None
        
        # Analyse échantillonnée
        for i in range(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 60):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (64, 64))
            
            if prev_frame is not None:
                # Calcul du flux optique
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_frame, gray, 
                    np.array([[32, 32]], dtype=np.float32), 
                    None
                )[0]
                
                if flow is not None:
                    motion_magnitude = np.linalg.norm(flow)
                    motion_scores.append(motion_magnitude)
            
            prev_frame = gray
        
        return np.mean(motion_scores) if motion_scores else 0.0
    
    def _analyze_faces(self, cap: cv2.VideoCapture) -> List[Dict[str, Any]]:
        """Détecte et analyse les visages dans la vidéo"""        faces_info = []
        
        try:
            # Analyse sur quelques frames représentatives
            frame_indices = [
                int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * ratio)
                for ratio in [0.1, 0.3, 0.5, 0.7, 0.9]
            ]
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Conversion pour face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Détection des visages
                face_locations = face_recognition.face_locations(rgb_frame)
                
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    
                    # Calcul de la taille du visage
                    face_width = right - left
                    face_height = bottom - top
                    face_area = face_width * face_height
                    
                    faces_info.append({
                        'frame_index': frame_idx,
                        'location': face_location,
                        'size': face_area,
                        'center': ((left + right) // 2, (top + bottom) // 2)
                    })
            
        except Exception as e:
            self.logger.warning(f"Erreur détection visages: {e}")
        
        return faces_info
    
    def _analyze_objects(self, cap: cv2.VideoCapture) -> List[Dict[str, Any]]:
        """Détecte les objets dans la vidéo avec YOLO"""        objects_info = []
        
        if not self.yolo_model:
            return objects_info
        
        try:
            # Analyse sur frames échantillonnées
            frame_indices = [
                int(cap.get(cv2.CAP_PROP_FRAME_COUNT) * ratio)
                for ratio in [0.2, 0.5, 0.8]
            ]
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Détection YOLO
                results = self.yolo_model(frame)
                
                for result in results:
                    if result.boxes is not None:
                        for box in result.boxes:
                            objects_info.append({
                                'frame_index': frame_idx,
                                'class': result.names[int(box.cls)],
                                'confidence': float(box.conf),
                                'bbox': box.xyxy.tolist()[0]
                            })
            
        except Exception as e:
            self.logger.warning(f"Erreur détection objets: {e}")
        
        return objects_info
    
    def _analyze_video_audio(self, video_path: str) -> Dict[str, Any]:
        """Analyse la piste audio de la vidéo"""        try:
            # Utilisation de ffprobe pour info audio
            probe = ffmpeg.probe(video_path)
            
            audio_streams = [
                stream for stream in probe['streams']
                if stream['codec_type'] == 'audio'
            ]
            
            if audio_streams:
                audio_stream = audio_streams[0]
                return {
                    'has_audio': True,
                    'channels': int(audio_stream.get('channels', 0)),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'codec': audio_stream.get('codec_name', 'unknown')
                }
            else:
                return {'has_audio': False}
                
        except Exception as e:
            self.logger.warning(f"Erreur analyse audio: {e}")
            return {'has_audio': False}
    
    def _detect_codec(self, video_path: str) -> str:
        """Détecte le codec vidéo"""        try:
            probe = ffmpeg.probe(video_path)
            video_streams = [
                stream for stream in probe['streams']
                if stream['codec_type'] == 'video'
            ]
            
            if video_streams:
                return video_streams[0].get('codec_name', 'unknown')
            
        except Exception:
            pass
        
        return 'unknown'
    
    def _classify_content_type(
        self,
        scene_changes: List[int],
        motion_level: float,
        faces: List[Dict],
        audio_info: Dict
    ) -> str:
        """Classifie automatiquement le type de contenu"""        
        # Calcul des métriques
        scene_change_rate = len(scene_changes)
        face_density = len(faces)
        has_audio = audio_info.get('has_audio', False)
        
        # Logique de classification basée sur heuristiques
        if face_density > 10 and motion_level < 0.5:
            return ContentType.PODCAST.value
        elif scene_change_rate > 20 and motion_level > 0.8:
            return ContentType.MUSIC_VIDEO.value
        elif face_density > 5 and has_audio:
            return ContentType.VLOG.value
        elif motion_level > 1.0:
            return ContentType.GAMING.value
        else:
            return ContentType.SOCIAL_MEDIA.value
    
    def _calculate_quality_score(self, width: int, height: int, fps: float, bitrate: int) -> float:
        """Calcule un score de qualité global"""        
        # Normalisation des métriques
        resolution_score = min(1.0, (width * height) / (1920 * 1080))
        fps_score = min(1.0, fps / 60.0)
        bitrate_score = min(1.0, bitrate / (1920 * 1080 * 0.1))  # ~0.1 bits par pixel
        
        # Score pondéré
        quality_score = (resolution_score * 0.4 + fps_score * 0.3 + bitrate_score * 0.3)
        
        return round(quality_score, 3)
    
    def _generate_content_tags(
        self,
        faces: List[Dict],
        objects: List[Dict]
    ) -> List[str]:
        """Génère des tags automatiques basés sur le contenu détecté"""        
        tags = []
        
        # Tags basés sur les visages
        if len(faces) > 0:
            tags.append("people")
            if len(faces) == 1:
                tags.append("single_person")
            else:
                tags.append("multiple_people")
        
        # Tags basés sur les objets détectés
        object_classes = [obj['class'] for obj in objects]
        unique_objects = set(object_classes)
        
        # Mapping des objets vers tags génériques
        object_tag_mapping = {
            'person': 'people',
            'car': 'vehicle',
            'truck': 'vehicle',
            'bicycle': 'vehicle',
            'dog': 'animal',
            'cat': 'animal',
            'bird': 'animal',
            'laptop': 'technology',
            'cell phone': 'technology',
            'book': 'education',
            'chair': 'furniture',
            'dining table': 'furniture'
        }
        
        for obj_class in unique_objects:
            if obj_class in object_tag_mapping:
                tag = object_tag_mapping[obj_class]
                if tag not in tags:
                    tags.append(tag)
            else:
                tags.append(obj_class)
        
        return tags[:10]  # Limite à 10 tags

class VideoEnhancer:
    """Améliorateur vidéo IA pour créateurs de contenu"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enhance_video(
        self,
        video_path: str,
        enhancement_type: str = "balanced",
        intensity: float = 0.5
    ) -> str:
        """Améliore la qualité vidéo avec traitement IA"""        
        try:
            temp_output = tempfile.mktemp(suffix='.mp4')
            
            if enhancement_type == "upscale":
                return self._upscale_video(video_path, temp_output, intensity)
            elif enhancement_type == "stabilize":
                return self._stabilize_video(video_path, temp_output, intensity)
            elif enhancement_type == "color_correct":
                return self._color_correct_video(video_path, temp_output, intensity)
            elif enhancement_type == "denoise":
                return self._denoise_video(video_path, temp_output, intensity)
            else:  # balanced
                return self._balanced_enhancement(video_path, temp_output, intensity)
            
        except Exception as e:
            self.logger.error(f"Erreur amélioration vidéo: {e}")
            return video_path
    
    def _upscale_video(self, input_path: str, output_path: str, intensity: float) -> str:
        """Upscale la vidéo avec algorithmes IA"""        
        try:
            # Utilisation de ffmpeg avec filtres d'upscaling
            scale_factor = 1 + intensity
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'scale', 
                                 f'iw*{scale_factor}', f'ih*{scale_factor}',
                                 flags='lanczos')
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=18)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur upscale: {e}")
            return input_path
    
    def _stabilize_video(self, input_path: str, output_path: str, intensity: float) -> str:
        """Stabilise la vidéo"""        
        try:
            # Stabilisation avec vidstab de ffmpeg
            smoothing = int(10 + intensity * 20)
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'vidstabdetect', shakiness=10, accuracy=15)
            stream = ffmpeg.filter(stream, 'vidstabtransform', 
                                 smoothing=smoothing, 
                                 interpol='bilinear')
            stream = ffmpeg.output(stream, output_path, vcodec='libx264')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.warning(f"Stabilisation échouée, utilisation MoviePy: {e}")
            return self._stabilize_with_moviepy(input_path, output_path)
    
    def _stabilize_with_moviepy(self, input_path: str, output_path: str) -> str:
        """Stabilisation basique avec MoviePy"""        try:
            clip = VideoFileClip(input_path)
            # MoviePy n'a pas de stabilisation native, retour du fichier original
            clip.write_videofile(output_path, verbose=False, logger=None)
            clip.close()
            return output_path
        except Exception:
            return input_path
    
    def _color_correct_video(self, input_path: str, output_path: str, intensity: float) -> str:
        """Correction colorimétrique"""        
        try:
            # Correction avec filtres ffmpeg
            brightness = intensity * 0.1
            contrast = 1 + intensity * 0.2
            saturation = 1 + intensity * 0.3
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'eq', 
                                 brightness=brightness,
                                 contrast=contrast,
                                 saturation=saturation)
            stream = ffmpeg.output(stream, output_path, vcodec='libx264')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur correction couleur: {e}")
            return input_path
    
    def _denoise_video(self, input_path: str, output_path: str, intensity: float) -> str:
        """Réduction de bruit vidéo"""        
        try:
            # Débruitage avec filtre hqdn3d
            luma_strength = intensity * 4
            chroma_strength = intensity * 3
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'hqdn3d', 
                                 luma_strength, chroma_strength)
            stream = ffmpeg.output(stream, output_path, vcodec='libx264')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur débruitage: {e}")
            return input_path
    
    def _balanced_enhancement(self, input_path: str, output_path: str, intensity: float) -> str:
        """Amélioration équilibrée"""        
        try:
            # Combinaison de plusieurs filtres
            stream = ffmpeg.input(input_path)
            
            # Légère correction colorimétrique
            stream = ffmpeg.filter(stream, 'eq', 
                                 contrast=1 + intensity * 0.1,
                                 saturation=1 + intensity * 0.15)
            
            # Léger débruitage
            stream = ffmpeg.filter(stream, 'hqdn3d', intensity * 2)
            
            # Sharpening subtil
            stream = ffmpeg.filter(stream, 'unsharp', 
                                 luma_msize_x=5, luma_msize_y=5,
                                 luma_amount=intensity * 0.5)
            
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=20)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur amélioration équilibrée: {e}")
            return input_path

class VideoTransformer:
    """Transformateur vidéo principal pour créateurs de contenu"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.file_manager = FileManager()
        self.analyzer = VideoAnalyzer()
        self.enhancer = VideoEnhancer()
        
        # Presets optimisés par plateforme
        self.platform_presets = {
            'youtube': {
                'resolution': [1920, 1080],
                'fps': 30,
                'codec': VideoCodec.H264,
                'bitrate': '5M',
                'audio_bitrate': '128k'
            },
            'tiktok': {
                'resolution': [1080, 1920],  # 9:16
                'fps': 30,
                'codec': VideoCodec.H264,
                'bitrate': '3M',
                'audio_bitrate': '128k'
            },
            'instagram': {
                'resolution': [1080, 1080],  # 1:1
                'fps': 30,
                'codec': VideoCodec.H264,
                'bitrate': '3.5M',
                'audio_bitrate': '128k'
            },
            'twitter': {
                'resolution': [1280, 720],
                'fps': 30,
                'codec': VideoCodec.H264,
                'bitrate': '2M',
                'audio_bitrate': '128k'
            }
        }
    
    def transform(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """Transformation vidéo selon configuration"""        
        start_time = time.time()
        operations = []
        warnings = []
        errors = []
        
        try:
            # Validation du fichier d'entrée
            if not validate_video_file(input_path):
                raise ValidationError(f"Fichier vidéo invalide: {input_path}")
            
            # Analyse du fichier source
            original_metadata = self.analyzer.analyze_video_file(input_path)
            operations.append("Analyse métadonnées")
            
            # Préparation du chemin de sortie
            if not output_path:
                output_path = self._generate_output_path(input_path, config)
            
            # Application des transformations selon le type
            temp_path = input_path
            
            if config.type.value == 'video_resize':
                temp_path = self._resize_video(temp_path, config.parameters, output_path)
                operations.append("Redimensionnement")
                
            elif config.type.value == 'video_convert':
                temp_path = self._convert_video(temp_path, config.parameters, output_path)
                operations.append("Conversion format")
                
            elif config.type.value == 'video_compress':
                temp_path = self._compress_video(temp_path, config.parameters, output_path)
                operations.append("Compression")
                
            elif config.type.value == 'video_extract_audio':
                temp_path = self._extract_audio(temp_path, config.parameters, output_path)
                operations.append("Extraction audio")
            
            # Si le fichier temporaire est différent de l'output final
            if temp_path != output_path and Path(temp_path).exists():
                shutil.move(temp_path, output_path)
            
            # Analyse finale
            if Path(output_path).exists():
                processed_metadata = self.analyzer.analyze_video_file(output_path)
                
                # Calcul des métriques de qualité
                quality_metrics = self._calculate_quality_metrics(
                    original_metadata, processed_metadata
                )
            else:
                raise VideoProcessingError("Fichier de sortie non créé")
            
            processing_time = time.time() - start_time
            
            from . import TransformationResult, TransformationType
            return TransformationResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                transformation_type=TransformationType(config.type.value),
                metadata={
                    'original': original_metadata.__dict__,
                    'processed': processed_metadata.__dict__,
                    'quality_metrics': quality_metrics.__dict__
                },
                errors=errors,
                warnings=warnings,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Erreur transformation vidéo {input_path}: {e}")
            processing_time = time.time() - start_time
            
            from . import TransformationResult, TransformationType
            return TransformationResult(
                success=False,
                input_path=input_path,
                output_path=None,
                transformation_type=TransformationType(config.type.value),
                metadata={},
                errors=[str(e)],
                warnings=warnings,
                processing_time=processing_time
            )
    
    def _resize_video(
        self,
        input_path: str,
        params: Dict[str, Any],
        output_path: str
    ) -> str:
        """Redimensionne la vidéo"""        
        target_resolution = params.get('resolution', [1920, 1080])
        maintain_aspect = params.get('maintain_aspect', True)
        platform = params.get('platform')
        
        # Utilisation du preset de plateforme si spécifié
        if platform and platform in self.platform_presets:
            preset = self.platform_presets[platform]
            target_resolution = preset['resolution']
        
        try:
            stream = ffmpeg.input(input_path)
            
            if maintain_aspect:
                # Redimensionnement avec conservation du ratio
                stream = ffmpeg.filter(
                    stream, 'scale',
                    width=target_resolution[0],
                    height=target_resolution[1],
                    force_original_aspect_ratio='decrease'
                )
                # Padding si nécessaire
                stream = ffmpeg.filter(
                    stream, 'pad',
                    width=target_resolution[0],
                    height=target_resolution[1],
                    x='(ow-iw)/2',
                    y='(oh-ih)/2',
                    color='black'
                )
            else:
                # Redimensionnement forcé
                stream = ffmpeg.filter(
                    stream, 'scale',
                    width=target_resolution[0],
                    height=target_resolution[1]
                )
            
            stream = ffmpeg.output(stream, output_path, vcodec='libx264')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur redimensionnement: {e}")
            raise VideoProcessingError(f"Échec redimensionnement: {str(e)}")
    
    def _convert_video(
        self,
        input_path: str,
        params: Dict[str, Any],
        output_path: str
    ) -> str:
        """Convertit le format vidéo"""        
        target_format = params.get('format', 'mp4')
        codec = params.get('codec', 'libx264')
        bitrate = params.get('bitrate', '2M')
        fps = params.get('fps')
        
        try:
            stream = ffmpeg.input(input_path)
            
            output_params = {
                'vcodec': codec,
                'b:v': bitrate
            }
            
            if fps:
                output_params['r'] = fps
            
            # Codec audio par défaut
            output_params['acodec'] = 'aac'
            output_params['b:a'] = '128k'
            
            stream = ffmpeg.output(stream, output_path, **output_params)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur conversion: {e}")
            raise VideoProcessingError(f"Échec conversion: {str(e)}")
    
    def _compress_video(
        self,
        input_path: str,
        params: Dict[str, Any],
        output_path: str
    ) -> str:
        """Compresse la vidéo"""        
        quality = params.get('quality', 'standard')
        target_bitrate = params.get('bitrate', '2M')
        two_pass = params.get('two_pass', False)
        
        # Mapping qualité vers CRF
        crf_mapping = {
            'ultra': 18,
            'high': 23,
            'standard': 28,
            'low': 35
        }
        
        crf = crf_mapping.get(quality, 28)
        
        try:
            if two_pass:
                # Encodage 2 passes pour meilleure qualité
                return self._two_pass_encode(input_path, output_path, target_bitrate)
            else:
                # Encodage simple avec CRF
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(
                    stream, output_path,
                    vcodec='libx264',
                    crf=crf,
                    acodec='aac',
                    **{'b:a': '128k'}
                )
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                
                return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur compression: {e}")
            raise VideoProcessingError(f"Échec compression: {str(e)}")
    
    def _two_pass_encode(self, input_path: str, output_path: str, bitrate: str) -> str:
        """Encodage vidéo en 2 passes"""        
        try:
            # Première passe
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream, '/dev/null',
                vcodec='libx264',
                **{'b:v': bitrate},
                **{'pass': 1},
                f='/dev/null'
            )
            ffmpeg.run(stream, quiet=True)
            
            # Deuxième passe
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream, output_path,
                vcodec='libx264',
                **{'b:v': bitrate},
                **{'pass': 2},
                acodec='aac',
                **{'b:a': '128k'}
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Nettoyage des fichiers temporaires
            temp_files = ['ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree']
            for temp_file in temp_files:
                if Path(temp_file).exists():
                    Path(temp_file).unlink()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur encodage 2 passes: {e}")
            # Fallback vers encodage simple
            return self._compress_video(input_path, {'quality': 'standard'}, output_path)
    
    def _extract_audio(
        self,
        input_path: str,
        params: Dict[str, Any],
        output_path: str
    ) -> str:
        """Extrait la piste audio de la vidéo"""        
        audio_format = params.get('format', 'mp3')
        audio_bitrate = params.get('bitrate', '192k')
        
        try:
            stream = ffmpeg.input(input_path)
            
            # Configuration selon le format de sortie
            if audio_format == 'mp3':
                stream = ffmpeg.output(stream, output_path, acodec='mp3', **{'b:a': audio_bitrate})
            elif audio_format == 'wav':
                stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le')
            elif audio_format == 'flac':
                stream = ffmpeg.output(stream, output_path, acodec='flac')
            else:
                stream = ffmpeg.output(stream, output_path, acodec='aac', **{'b:a': audio_bitrate})
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erreur extraction audio: {e}")
            raise VideoProcessingError(f"Échec extraction audio: {str(e)}")
    
    def _generate_output_path(self, input_path: str, config: 'TransformationConfig') -> str:
        """Génère le chemin de sortie automatiquement"""        
        input_path_obj = Path(input_path)
        
        # Détermination de l'extension selon la transformation
        if config.type.value == 'video_extract_audio':
            audio_format = config.parameters.get('format', 'mp3')
            output_format = audio_format
        else:
            output_format = config.output_format or input_path_obj.suffix.lstrip('.')
        
        # Nom de fichier avec suffixe de transformation
        transform_suffix = config.type.value.replace('video_', '')
        new_name = f"{input_path_obj.stem}_{transform_suffix}.{output_format}"
        
        return str(input_path_obj.parent / new_name)
    
    def _calculate_quality_metrics(
        self,
        original: VideoMetadata,
        processed: VideoMetadata
    ) -> VideoQualityMetrics:
        """Calcule les métriques de qualité de la transformation"""        
        # Calcul des changements de résolution
        resolution_change = (processed.width * processed.height) / (original.width * original.height)
        
        # Calcul du changement de bitrate
        bitrate_change = processed.bitrate / original.bitrate if original.bitrate > 0 else 1.0
        
        # Score de qualité basé sur la conservation des métriques
        quality_score = min(1.0, (resolution_change + bitrate_change) / 2.0)
        
        return VideoQualityMetrics(
            psnr_db=None,  # Nécessiterait comparaison frame par frame
            ssim_score=None,  # Calcul complexe
            bitrate_efficiency=bitrate_change,
            compression_ratio=original.file_size / processed.file_size if processed.file_size > 0 else 1.0,
            encoding_speed=None,  # Non mesuré
            visual_quality_score=quality_score,
            artifacts_detected=[],
            motion_smoothness=1.0  # Estimation par défaut
        )

class AsyncVideoTransformer:
    """Version asynchrone du transformateur vidéo"""    
    def __init__(self):
        self.sync_transformer = VideoTransformer()
        self.logger = logging.getLogger(__name__)
    
    async def transform_async(
        self,
        input_path: str,
        config: 'TransformationConfig',
        output_path: Optional[str] = None
    ) -> 'TransformationResult':
        """Transformation vidéo asynchrone"""        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.sync_transformer.transform,
            input_path,
            config,
            output_path
        )
    
    async def transform_batch_async(
        self,
        inputs: List[Tuple[str, 'TransformationConfig']],
        max_concurrent: int = 2  # Moins de concurrence pour vidéo
    ) -> List['TransformationResult']:
        """Transformation en lot asynchrone"""        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def transform_single(input_config_tuple):
            async with semaphore:
                input_path, config = input_config_tuple
                return await self.transform_async(input_path, config)
        
        tasks = [transform_single(item) for item in inputs]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Export des classes
__all__ = [
    'VideoTransformer',
    'AsyncVideoTransformer',
    'VideoAnalyzer',
    'VideoEnhancer',
    'VideoFormat',
    'VideoCodec',
    'VideoQuality',
    'ContentType',
    'VideoProcessingResult'
]
