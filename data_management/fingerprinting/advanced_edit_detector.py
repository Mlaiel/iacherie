"""🎬 Advanced Video Edit Detection Engine - IA Influencer Agent Platform Enterprise
===============================================================================
Module: backend/data_management/fingerprinting/advanced_edit_detector.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Video Edit Detection - Ultra Enterprise Production-Ready
Responsibility: Advanced edit detection using OpenCV, Deep Learning, and Computer Vision
=======================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC VIDEO EDIT DETECTION:
Video Input → Frame Extraction → Temporal Analysis → Spatial Analysis → 
Scene Detection → Cut Detection → Transition Detection → Deep Learning Features → 
Content-Aware Analysis → Edit Classification → Confidence Scoring

EDIT DETECTION TECHNOLOGIES:
├── 🎬 Temporal Edit Detection (Cuts, Transitions, Frame Manipulations)
├── 🔍 Spatial Edit Detection (Cropping, Scaling, Rotation, Color Modifications)
├── 🧠 Deep Learning Analysis (CNN-based Content Understanding)
├── 📊 Scene Change Detection (Advanced Boundary Detection)
├── 🌊 Motion Analysis (Optical Flow + Motion Vectors)
├── 🎨 Visual Features (Edge Detection, Histogram Analysis)
├── 📏 Geometric Transformations (Affine, Perspective, Distortions)
└── 🛡️ Edit Classification (Cut Types, Transition Types, Manipulation Types)
"""

from typing import Dict, List, Optional, Any, Union, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import cv2
import asyncio
import logging
import hashlib
import time
from datetime import datetime
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor

# Deep learning imports
try:
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available for deep learning features")

# Computer vision imports
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available for clustering analysis")

try:
    import scipy.stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available for statistical analysis")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

class EditType(Enum):
    """Types d'éditions détectées"""
    CUT = "cut"                          # Coupe franche
    FADE_IN = "fade_in"                  # Fondu entrant
    FADE_OUT = "fade_out"                # Fondu sortant
    CROSS_FADE = "cross_fade"            # Fondu enchaîné
    WIPE = "wipe"                        # Balayage
    DISSOLVE = "dissolve"                # Dissolution
    CROP = "crop"                        # Recadrage
    SCALE = "scale"                      # Redimensionnement
    ROTATION = "rotation"                # Rotation
    COLOR_CORRECTION = "color_correction" # Correction colorimétrique
    SPEED_CHANGE = "speed_change"        # Changement de vitesse
    REVERSE = "reverse"                  # Inversion temporelle
    UNKNOWN = "unknown"                  # Type inconnu

class EditConfidence(Enum):
    """Niveaux de confiance pour la détection"""
    LOW = "low"          # 0.0 - 0.3
    MEDIUM = "medium"    # 0.3 - 0.7
    HIGH = "high"        # 0.7 - 0.9
    VERY_HIGH = "very_high"  # 0.9 - 1.0

@dataclass
class EditDetection:
    """Résultat de détection d'une édition"""
    timestamp: float
    frame_index: int
    edit_type: EditType
    confidence: float
    confidence_level: EditConfidence
    description: str
    features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AdvancedEditConfig:
    """Configuration pour la détection d'éditions avancée"""
    
    # Paramètres généraux
    frame_extraction_rate: int = 5  # frames per second for analysis
    min_edit_duration: float = 0.1  # minimum duration for edit detection (seconds)
    
    # Détection de coupes
    cut_threshold: float = 0.3      # seuil pour détecter les coupes
    histogram_bins: int = 256       # bins pour l'analyse d'histogramme
    
    # Détection de transitions
    transition_window: int = 10     # fenêtre d'analyse pour les transitions (frames)
    fade_threshold: float = 0.15    # seuil pour détecter les fondus
    
    # Analyse spatiale
    crop_tolerance: float = 0.05    # tolérance pour détecter le recadrage
    scale_tolerance: float = 0.1    # tolérance pour détecter le redimensionnement
    rotation_tolerance: float = 1.0 # tolérance pour détecter la rotation (degrés)
    
    # Deep learning
    use_deep_features: bool = True
    cnn_model: str = "resnet50"
    feature_layer: str = "avgpool"
    
    # Performance
    use_gpu: bool = True
    batch_size: int = 8
    max_workers: int = 4

class AdvancedEditDetector:
    """Détecteur avancé d'éditions vidéo"""
    
    def __init__(self, config: Optional[AdvancedEditConfig] = None):
        self.config = config or AdvancedEditConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize deep learning models
        self.models = self._initialize_models()
        
        # Initialize feature extractors
        self.feature_extractors = self._initialize_feature_extractors()
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        self.logger.info("AdvancedEditDetector initialized successfully")
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialise les modèles deep learning"""
        models_dict = {}
        
        if TORCH_AVAILABLE and self.config.use_deep_features:
            try:
                # ResNet for feature extraction
                if self.config.cnn_model == "resnet50":
                    model = models.resnet50(pretrained=True)
                    # Remove classifier to get features
                    model = torch.nn.Sequential(*list(model.children())[:-1])
                elif self.config.cnn_model == "vgg16":
                    model = models.vgg16(pretrained=True)
                    model = model.features
                else:
                    model = models.resnet50(pretrained=True)
                    model = torch.nn.Sequential(*list(model.children())[:-1])
                
                model.eval()
                if self.config.use_gpu and torch.cuda.is_available():
                    model = model.cuda()
                
                models_dict['cnn'] = model
                self.logger.info(f"Loaded {self.config.cnn_model} model successfully")
                
            except Exception as e:
                self.logger.warning(f"Failed to load deep learning model: {e}")
        
        return models_dict
    
    def _initialize_feature_extractors(self) -> Dict[str, Any]:
        """Initialise les extracteurs de caractéristiques"""
        extractors = {}
        
        # Edge detection
        extractors['edge_detector'] = cv2.Canny
        
        # Optical flow
        extractors['optical_flow'] = cv2.calcOpticalFlowPyrLK
        
        # Feature detection
        if hasattr(cv2, 'ORB_create'):
            extractors['orb'] = cv2.ORB_create()
        
        if hasattr(cv2, 'SIFT_create'):
            try:
                extractors['sift'] = cv2.SIFT_create()
            except Exception:
                pass  # SIFT may not be available
        
        return extractors
    
    async def detect_edits(self, video_path: str) -> Dict[str, Any]:
        """
        Détecte les éditions dans une vidéo
        
        Args:
            video_path: Chemin vers le fichier vidéo
            
        Returns:
            Dictionnaire contenant les éditions détectées
        """
        try:
            start_time = time.time()
            
            # Extraction des frames
            frames = await self._extract_frames(video_path)
            if not frames:
                raise ValueError("No frames extracted from video")
            
            # Analyse temporelle
            temporal_edits = await self._detect_temporal_edits(frames)
            
            # Analyse spatiale
            spatial_edits = await self._detect_spatial_edits(frames)
            
            # Détection de scènes
            scene_changes = await self._detect_scene_changes(frames)
            
            # Deep learning analysis
            content_edits = []
            if self.config.use_deep_features and self.models.get('cnn'):
                content_edits = await self._detect_content_edits(frames)
            
            # Combinaison des résultats
            all_edits = temporal_edits + spatial_edits + scene_changes + content_edits
            
            # Classification et scoring
            classified_edits = await self._classify_and_score_edits(all_edits)
            
            processing_time = time.time() - start_time
            
            return {
                "video_path": video_path,
                "total_frames_analyzed": len(frames),
                "processing_time": processing_time,
                "edits_detected": len(classified_edits),
                "edits": classified_edits,
                "temporal_edits": len(temporal_edits),
                "spatial_edits": len(spatial_edits),
                "scene_changes": len(scene_changes),
                "content_edits": len(content_edits),
                "confidence_distribution": self._analyze_confidence_distribution(classified_edits),
                "metadata": {
                    "config": self.config.__dict__,
                    "models_used": list(self.models.keys()),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Edit detection failed: {e}")
            raise
    
    async def _extract_frames(self, video_path: str) -> List[Tuple[int, np.ndarray, float]]:
        """
        Extrait les frames de la vidéo avec timestamp
        
        Returns:
            Liste de tuples (frame_index, frame_array, timestamp)
        """
        frames = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame extraction interval
        frame_interval = max(1, int(fps / self.config.frame_extraction_rate))
        
        frame_idx = 0
        while frame_idx < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            timestamp = frame_idx / fps
            frames.append((frame_idx, frame, timestamp))
            
            frame_idx += frame_interval
        
        cap.release()
        return frames
    
    async def _detect_temporal_edits(self, frames: List[Tuple[int, np.ndarray, float]]) -> List[EditDetection]:
        """Détecte les éditions temporelles (coupes, transitions)"""
        edits = []
        
        for i in range(1, len(frames)):
            prev_frame = frames[i-1][1]
            curr_frame = frames[i][1]
            timestamp = frames[i][2]
            frame_idx = frames[i][0]
            
            # Analyse des histogrammes pour détecter les coupes
            cut_confidence = self._analyze_histogram_difference(prev_frame, curr_frame)
            
            if cut_confidence > self.config.cut_threshold:
                edit_type = EditType.CUT
                description = f"Cut detected with confidence {cut_confidence:.3f}"
                
                # Détection de fondus
                fade_confidence = self._detect_fade(prev_frame, curr_frame)
                if fade_confidence > self.config.fade_threshold:
                    if np.mean(curr_frame) < np.mean(prev_frame):
                        edit_type = EditType.FADE_OUT
                        description = f"Fade out detected with confidence {fade_confidence:.3f}"
                    else:
                        edit_type = EditType.FADE_IN
                        description = f"Fade in detected with confidence {fade_confidence:.3f}"
                
                edits.append(EditDetection(
                    timestamp=timestamp,
                    frame_index=frame_idx,
                    edit_type=edit_type,
                    confidence=cut_confidence,
                    confidence_level=self._get_confidence_level(cut_confidence),
                    description=description,
                    features={
                        "histogram_difference": cut_confidence,
                        "fade_confidence": fade_confidence
                    }
                ))
        
        return edits
    
    async def _detect_spatial_edits(self, frames: List[Tuple[int, np.ndarray, float]]) -> List[EditDetection]:
        """Détecte les éditions spatiales (crop, scale, rotation)"""
        edits = []
        
        for i in range(1, len(frames)):
            prev_frame = frames[i-1][1]
            curr_frame = frames[i][1]
            timestamp = frames[i][2]
            frame_idx = frames[i][0]
            
            # Détection de recadrage
            crop_confidence = self._detect_crop(prev_frame, curr_frame)
            
            # Détection de redimensionnement
            scale_confidence = self._detect_scale(prev_frame, curr_frame)
            
            # Détection de rotation
            rotation_confidence, rotation_angle = self._detect_rotation(prev_frame, curr_frame)
            
            # Détection de correction colorimétrique
            color_confidence = self._detect_color_correction(prev_frame, curr_frame)
            
            # Ajout des éditions détectées
            if crop_confidence > self.config.crop_tolerance:
                edits.append(EditDetection(
                    timestamp=timestamp,
                    frame_index=frame_idx,
                    edit_type=EditType.CROP,
                    confidence=crop_confidence,
                    confidence_level=self._get_confidence_level(crop_confidence),
                    description=f"Crop detected with confidence {crop_confidence:.3f}",
                    features={"crop_confidence": crop_confidence}
                ))
            
            if scale_confidence > self.config.scale_tolerance:
                edits.append(EditDetection(
                    timestamp=timestamp,
                    frame_index=frame_idx,
                    edit_type=EditType.SCALE,
                    confidence=scale_confidence,
                    confidence_level=self._get_confidence_level(scale_confidence),
                    description=f"Scale change detected with confidence {scale_confidence:.3f}",
                    features={"scale_confidence": scale_confidence}
                ))
            
            if rotation_confidence > self.config.rotation_tolerance:
                edits.append(EditDetection(
                    timestamp=timestamp,
                    frame_index=frame_idx,
                    edit_type=EditType.ROTATION,
                    confidence=rotation_confidence,
                    confidence_level=self._get_confidence_level(rotation_confidence / 90.0),  # Normalize to 0-1
                    description=f"Rotation detected: {rotation_angle:.1f}° with confidence {rotation_confidence:.3f}",
                    features={
                        "rotation_confidence": rotation_confidence,
                        "rotation_angle": rotation_angle
                    }
                ))
            
            if color_confidence > 0.3:  # threshold for color correction
                edits.append(EditDetection(
                    timestamp=timestamp,
                    frame_index=frame_idx,
                    edit_type=EditType.COLOR_CORRECTION,
                    confidence=color_confidence,
                    confidence_level=self._get_confidence_level(color_confidence),
                    description=f"Color correction detected with confidence {color_confidence:.3f}",
                    features={"color_confidence": color_confidence}
                ))
        
        return edits
    
    async def _detect_scene_changes(self, frames: List[Tuple[int, np.ndarray, float]]) -> List[EditDetection]:
        """Détecte les changements de scène"""
        edits = []
        
        for i in range(1, len(frames)):
            prev_frame = frames[i-1][1]
            curr_frame = frames[i][1]
            timestamp = frames[i][2]
            frame_idx = frames[i][0]
            
            # Analyse de l'optical flow pour détecter les changements de scène
            scene_confidence = self._analyze_optical_flow(prev_frame, curr_frame)
            
            # Analyse des caractéristiques d'edge pour détecter les changements structurels
            edge_confidence = self._analyze_edge_changes(prev_frame, curr_frame)
            
            # Combinaison des métriques
            combined_confidence = (scene_confidence + edge_confidence) / 2
            
            if combined_confidence > 0.4:  # threshold for scene change
                edits.append(EditDetection(
                    timestamp=timestamp,
                    frame_index=frame_idx,
                    edit_type=EditType.CUT,  # Scene change is often a cut
                    confidence=combined_confidence,
                    confidence_level=self._get_confidence_level(combined_confidence),
                    description=f"Scene change detected with confidence {combined_confidence:.3f}",
                    features={
                        "scene_confidence": scene_confidence,
                        "edge_confidence": edge_confidence,
                        "combined_confidence": combined_confidence
                    }
                ))
        
        return edits
    
    async def _detect_content_edits(self, frames: List[Tuple[int, np.ndarray, float]]) -> List[EditDetection]:
        """Détecte les éditions basées sur le contenu avec deep learning"""
        edits = []
        
        if not self.models.get('cnn'):
            return edits
        
        try:
            # Extract deep features for consecutive frames
            for i in range(1, len(frames)):
                prev_frame = frames[i-1][1]
                curr_frame = frames[i][1]
                timestamp = frames[i][2]
                frame_idx = frames[i][0]
                
                # Extract CNN features
                prev_features = self._extract_cnn_features(prev_frame)
                curr_features = self._extract_cnn_features(curr_frame)
                
                if prev_features is not None and curr_features is not None:
                    # Calculate feature similarity
                    similarity = self._calculate_feature_similarity(prev_features, curr_features)
                    content_confidence = 1.0 - similarity  # Higher difference = higher edit confidence
                    
                    if content_confidence > 0.5:  # threshold for content edit
                        edits.append(EditDetection(
                            timestamp=timestamp,
                            frame_index=frame_idx,
                            edit_type=EditType.UNKNOWN,  # Content-based edit type to be refined
                            confidence=content_confidence,
                            confidence_level=self._get_confidence_level(content_confidence),
                            description=f"Content-based edit detected with confidence {content_confidence:.3f}",
                            features={
                                "content_similarity": similarity,
                                "content_confidence": content_confidence
                            }
                        ))
        
        except Exception as e:
            self.logger.warning(f"Content edit detection failed: {e}")
        
        return edits
    
    def _analyze_histogram_difference(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Analyse la différence d'histogramme entre deux frames"""
        try:
            # Convert to grayscale for histogram analysis
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate histograms
            hist1 = cv2.calcHist([gray1], [0], None, [self.config.histogram_bins], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [self.config.histogram_bins], [0, 256])
            
            # Normalize histograms
            cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
            
            # Calculate difference using correlation
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Return difference (1 - correlation for high difference when correlation is low)
            return 1.0 - correlation
            
        except Exception as e:
            self.logger.warning(f"Histogram analysis failed: {e}")
            return 0.0
    
    def _detect_fade(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Détecte les fondus entre deux frames"""
        try:
            # Calculate mean brightness
            mean1 = np.mean(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY))
            mean2 = np.mean(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY))
            
            # Calculate brightness difference
            brightness_diff = abs(mean1 - mean2) / 255.0
            
            # Check for fade patterns (gradual brightness change)
            return brightness_diff
            
        except Exception as e:
            self.logger.warning(f"Fade detection failed: {e}")
            return 0.0
    
    def _detect_crop(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Détecte le recadrage entre deux frames"""
        try:
            # Use template matching to detect if one frame is a crop of another
            if frame1.shape == frame2.shape:
                return 0.0  # Same size, no crop
            
            # Simple crop detection using edge analysis
            edges1 = cv2.Canny(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), 50, 150)
            edges2 = cv2.Canny(cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY), 50, 150)
            
            # Count edge pixels
            edge_count1 = np.sum(edges1 > 0)
            edge_count2 = np.sum(edges2 > 0)
            
            # Calculate relative difference
            if edge_count1 > 0:
                crop_confidence = abs(edge_count1 - edge_count2) / edge_count1
                return min(crop_confidence, 1.0)
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"Crop detection failed: {e}")
            return 0.0
    
    def _detect_scale(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Détecte le redimensionnement entre deux frames"""
        try:
            # Resize both frames to same size for comparison
            h1, w1 = frame1.shape[:2]
            h2, w2 = frame2.shape[:2]
            
            # Calculate scale difference
            scale_x = w2 / w1 if w1 > 0 else 1.0
            scale_y = h2 / h1 if h1 > 0 else 1.0
            
            # Calculate scale confidence
            scale_diff = abs(1.0 - scale_x) + abs(1.0 - scale_y)
            
            return min(scale_diff / 2.0, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Scale detection failed: {e}")
            return 0.0
    
    def _detect_rotation(self, frame1: np.ndarray, frame2: np.ndarray) -> Tuple[float, float]:
        """Détecte la rotation entre deux frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Detect features using ORB
            if 'orb' in self.feature_extractors:
                orb = self.feature_extractors['orb']
                kp1, des1 = orb.detectAndCompute(gray1, None)
                kp2, des2 = orb.detectAndCompute(gray2, None)
                
                if des1 is not None and des2 is not None and len(des1) > 4 and len(des2) > 4:
                    # Match features
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                    matches = bf.match(des1, des2)
                    
                    if len(matches) > 4:
                        # Extract matched points
                        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                        
                        # Find homography
                        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                        
                        if M is not None:
                            # Extract rotation angle from homography matrix
                            angle = np.arctan2(M[1, 0], M[0, 0]) * 180 / np.pi
                            confidence = abs(angle)
                            
                            return confidence, angle
            
            return 0.0, 0.0
            
        except Exception as e:
            self.logger.warning(f"Rotation detection failed: {e}")
            return 0.0, 0.0
    
    def _detect_color_correction(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Détecte la correction colorimétrique entre deux frames"""
        try:
            # Convert to LAB color space for better color analysis
            lab1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2LAB)
            lab2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2LAB)
            
            # Calculate mean and std for each channel
            stats1 = [(np.mean(lab1[:, :, i]), np.std(lab1[:, :, i])) for i in range(3)]
            stats2 = [(np.mean(lab2[:, :, i]), np.std(lab2[:, :, i])) for i in range(3)]
            
            # Calculate differences
            total_diff = 0.0
            for (mean1, std1), (mean2, std2) in zip(stats1, stats2):
                mean_diff = abs(mean1 - mean2) / 255.0
                std_diff = abs(std1 - std2) / 255.0
                total_diff += mean_diff + std_diff
            
            return min(total_diff / 6.0, 1.0)  # Normalize by number of metrics
            
        except Exception as e:
            self.logger.warning(f"Color correction detection failed: {e}")
            return 0.0
    
    def _analyze_optical_flow(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Analyse le flux optique pour détecter les changements de scène"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate dense optical flow
            flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)[0]
            
            if flow is not None and len(flow) > 0:
                # Calculate flow magnitude
                magnitude = np.sqrt(flow[:, 0]**2 + flow[:, 1]**2)
                
                # Calculate flow statistics
                flow_mean = np.mean(magnitude)
                flow_std = np.std(magnitude)
                
                # Combine metrics for scene change confidence
                scene_confidence = min((flow_mean + flow_std) / 100.0, 1.0)
                
                return scene_confidence
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"Optical flow analysis failed: {e}")
            return 0.0
    
    def _analyze_edge_changes(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Analyse les changements d'edges pour détecter les modifications structurelles"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges1 = cv2.Canny(gray1, 50, 150)
            edges2 = cv2.Canny(gray2, 50, 150)
            
            # Calculate edge difference
            edge_diff = cv2.absdiff(edges1, edges2)
            
            # Calculate confidence based on edge changes
            total_pixels = edge_diff.shape[0] * edge_diff.shape[1]
            changed_pixels = np.sum(edge_diff > 0)
            
            confidence = changed_pixels / total_pixels if total_pixels > 0 else 0.0
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Edge analysis failed: {e}")
            return 0.0
    
    def _extract_cnn_features(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extrait les caractéristiques CNN d'un frame"""
        try:
            if not self.models.get('cnn'):
                return None
            
            # Preprocess frame
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_tensor = transform(rgb_frame).unsqueeze(0)
            
            if self.config.use_gpu and torch.cuda.is_available():
                input_tensor = input_tensor.cuda()
            
            # Extract features
            with torch.no_grad():
                features = self.models['cnn'](input_tensor)
                features = features.squeeze().cpu().numpy()
            
            return features
            
        except Exception as e:
            self.logger.warning(f"CNN feature extraction failed: {e}")
            return None
    
    def _calculate_feature_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calcule la similarité entre deux vecteurs de caractéristiques"""
        try:
            # Normalize features
            norm1 = features1 / (np.linalg.norm(features1) + 1e-8)
            norm2 = features2 / (np.linalg.norm(features2) + 1e-8)
            
            # Calculate cosine similarity
            similarity = np.dot(norm1, norm2)
            
            return max(0.0, min(similarity, 1.0))  # Clamp to [0, 1]
            
        except Exception as e:
            self.logger.warning(f"Feature similarity calculation failed: {e}")
            return 0.0
    
    async def _classify_and_score_edits(self, edits: List[EditDetection]) -> List[EditDetection]:
        """Classifie et score les éditions détectées"""
        classified_edits = []
        
        for edit in edits:
            # Update confidence level based on confidence score
            edit.confidence_level = self._get_confidence_level(edit.confidence)
            
            # Refine edit type based on features
            refined_edit = self._refine_edit_type(edit)
            
            classified_edits.append(refined_edit)
        
        # Sort by timestamp
        classified_edits.sort(key=lambda x: x.timestamp)
        
        return classified_edits
    
    def _get_confidence_level(self, confidence: float) -> EditConfidence:
        """Convertit le score de confiance en niveau"""
        if confidence >= 0.9:
            return EditConfidence.VERY_HIGH
        elif confidence >= 0.7:
            return EditConfidence.HIGH
        elif confidence >= 0.3:
            return EditConfidence.MEDIUM
        else:
            return EditConfidence.LOW
    
    def _refine_edit_type(self, edit: EditDetection) -> EditDetection:
        """Affine le type d'édition basé sur les caractéristiques"""
        # This can be extended with more sophisticated classification logic
        features = edit.features
        
        # Example refinement logic
        if edit.edit_type == EditType.UNKNOWN:
            if features.get('content_confidence', 0) > 0.8:
                # High content change suggests a cut or major edit
                edit.edit_type = EditType.CUT
                edit.description = "Major content change detected (classified as cut)"
        
        return edit
    
    def _analyze_confidence_distribution(self, edits: List[EditDetection]) -> Dict[str, Any]:
        """Analyse la distribution des niveaux de confiance"""
        if not edits:
            return {}
        
        confidences = [edit.confidence for edit in edits]
        levels = [edit.confidence_level.value for edit in edits]
        
        return {
            "mean_confidence": float(np.mean(confidences)),
            "std_confidence": float(np.std(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences)),
            "confidence_levels": {
                level: levels.count(level) for level in set(levels)
            }
        }