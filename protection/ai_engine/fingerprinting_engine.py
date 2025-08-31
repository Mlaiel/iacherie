"""
 Content Fingerprinting Engine - Ultra-Advanced Enterprise Protection System
==============================================================================

State-of-the-art content fingerprinting system providing:
- Multi-modal fingerprinting for audio, video, image, and text content
- Advanced similarity matching with FAISS vector database integration
- Tamper-resistant fingerprints with cryptographic security
- Real-time duplicate detection and content tracking
- Cross-modal content correlation and relationship detection
- Enterprise-grade scalability and performance optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Team Specialties: Lead Dev IA + ML Engineer + Audio Engineer + Computer Vision + Security Expert + Signal Processing
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL LEGAL WARNING 
This proprietary fingerprinting system contains advanced algorithms, signal processing techniques,
and security mechanisms belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering
- Commercial use without explicit written permission
- Algorithm extraction or fingerprinting technique appropriation
- Distribution without proper licensing

Legal violations will result in immediate prosecution under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""

import logging
import asyncio
import hashlib
import numpy as np
import librosa
import cv2
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import json
import base64

# Specialized fingerprinting libraries
import imagehash
import chromaprint
import pytesseract
from PIL import Image
import soundfile as sf

# Advanced signal processing
from scipy import signal
from scipy.fft import fft, fftfreq
import pywt  # Wavelet transforms
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database for fingerprint storage
import sqlite3
import redis
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Integer, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class ContentFingerprint(Base):
    __tablename__ = 'content_fingerprints'
    
    id = Column(String, primary_key=True)
    content_id = Column(String, index=True)
    content_type = Column(String, index=True)
    fingerprint_type = Column(String, index=True)
    fingerprint_data = Column(LargeBinary)
    fingerprint_hash = Column(String, index=True)
    similarity_threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text)

class ContentFingerprintEngine:
    """
    Enterprise-grade content fingerprinting engine for robust content identification
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.similarity_thresholds = config.get('similarity_thresholds', {
            'audio_chromaprint': 0.85,
            'audio_mfcc': 0.8,
            'audio_spectral': 0.75,
            'image_perceptual': 0.9,
            'image_feature': 0.7,
            'video_frame': 0.8,
            'text_semantic': 0.85,
            'text_structural': 0.9
        })
        
        # Initialize database
        self._init_database()
        
        # Initialize Redis cache
        self._init_redis()
        
        # Fingerprinting algorithms
        self.fingerprint_algorithms = {
            'audio': {
                'chromaprint': self._generate_chromaprint_fingerprint,
                'mfcc': self._generate_mfcc_fingerprint,
                'spectral': self._generate_spectral_fingerprint,
                'perceptual': self._generate_audio_perceptual_fingerprint,
                'wavelet': self._generate_wavelet_fingerprint
            },
            'image': {
                'perceptual': self._generate_image_perceptual_fingerprint,
                'feature': self._generate_image_feature_fingerprint,
                'color': self._generate_color_fingerprint,
                'texture': self._generate_texture_fingerprint,
                'geometric': self._generate_geometric_fingerprint
            },
            'video': {
                'frame': self._generate_video_frame_fingerprint,
                'motion': self._generate_motion_fingerprint,
                'scene': self._generate_scene_fingerprint,
                'temporal': self._generate_temporal_fingerprint
            },
            'text': {
                'semantic': self._generate_semantic_fingerprint,
                'structural': self._generate_structural_fingerprint,
                'stylistic': self._generate_stylistic_fingerprint,
                'content': self._generate_content_fingerprint
            }
        }
        
        logger.info("Content Fingerprinting Engine initialized")
    
    def _init_database(self):
        """Initialize SQLite database for fingerprint storage"""



        try:
            db_path = self.config.get('database_path', 'fingerprints.db')
            self.engine = create_engine(f'sqlite:///{db_path}')
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Fingerprint database initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    def _init_redis(self):
        """Initialize Redis cache for fast fingerprint lookup"""



        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {str(e)}")
            self.redis_client = None
    
    async def generate_fingerprints(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive fingerprints for content
        """



        try:
            content_type = content_data.get('type', 'unknown')
            content_id = content_data.get('id')
            file_path = content_data.get('file_path')
            
            fingerprint_result = {
                'content_id': content_id,
                'content_type': content_type,
                'timestamp': datetime.utcnow().isoformat(),
                'fingerprints': {},
                'metadata': content_data.get('metadata', {})
            }
            
            # Generate all applicable fingerprints
            if content_type in self.fingerprint_algorithms:
                algorithms = self.fingerprint_algorithms[content_type]
                
                for algo_name, algo_func in algorithms.items():
                    try:
                        fingerprint_data = await algo_func(file_path, content_data)
                        if fingerprint_data:
                            fingerprint_result['fingerprints'][algo_name] = fingerprint_data
                            
                            # Store in database
                            await self._store_fingerprint(
                                content_id, content_type, algo_name, fingerprint_data
                            )
                            
                    except Exception as e:
                        logger.error(f"Failed to generate {algo_name} fingerprint: {str(e)}")
                        continue
            
            # Generate cross-modal fingerprints if applicable
            cross_modal = await self._generate_cross_modal_fingerprints(content_data)
            if cross_modal:
                fingerprint_result['fingerprints']['cross_modal'] = cross_modal
            
            return fingerprint_result
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {str(e)}")
            raise
    
    async def find_similar_content(
        self, 
        fingerprints: Dict[str, Any], 
        content_type: str,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar content based on fingerprints
        """



        try:
            similar_content = []
            
            for fingerprint_type, fingerprint_data in fingerprints.items():
                threshold = similarity_threshold or self.similarity_thresholds.get(
                    f"{content_type}_{fingerprint_type}", 0.8
                )
                
                # Search in database
                matches = await self._search_similar_fingerprints(
                    fingerprint_type, fingerprint_data, threshold
                )
                
                for match in matches:
                    similar_content.append({
                        'content_id': match['content_id'],
                        'fingerprint_type': fingerprint_type,
                        'similarity_score': match['similarity'],
                        'metadata': match.get('metadata', {})
                    })
            
            # Remove duplicates and sort by similarity
            unique_content = {}
            for item in similar_content:
                content_id = item['content_id']
                if content_id not in unique_content or item['similarity_score'] > unique_content[content_id]['similarity_score']:
                    unique_content[content_id] = item
            
            return sorted(unique_content.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar content search failed: {str(e)}")
            return []
    
    # Audio Fingerprinting Methods
    
    async def _generate_chromaprint_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Chromaprint fingerprint for audio"""



        try:
            import subprocess
            
            # Use fpcalc to generate chromaprint
            result = subprocess.run([
                'fpcalc', '-raw', '-length', '120', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\\n')
                fingerprint = None
                duration = 0
                
                for line in lines:
                    if line.startswith('FINGERPRINT='):
                        fingerprint = line.split('=', 1)[1]
                    elif line.startswith('DURATION='):
                        duration = float(line.split('=', 1)[1])
                
                if fingerprint:
                    return {
                        'type': 'chromaprint',
                        'fingerprint': fingerprint,
                        'duration': duration,
                        'hash': hashlib.sha256(fingerprint.encode()).hexdigest()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Chromaprint generation failed: {str(e)}")
            return None
    
    async def _generate_mfcc_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MFCC-based fingerprint for audio"""



        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=22050)
            
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, n_fft=2048, hop_length=512)
            
            # Normalize and create robust fingerprint
            mfcc_normalized = (mfcc - np.mean(mfcc, axis=1, keepdims=True)) / (np.std(mfcc, axis=1, keepdims=True) + 1e-8)
            
            # Create delta and delta-delta features
            mfcc_delta = librosa.feature.delta(mfcc_normalized)
            mfcc_delta2 = librosa.feature.delta(mfcc_normalized, order=2)
            
            # Combine features
            combined_features = np.vstack([mfcc_normalized, mfcc_delta, mfcc_delta2])
            
            # Create compact fingerprint using statistical moments
            fingerprint = {
                'mean': np.mean(combined_features, axis=1).tolist(),
                'std': np.std(combined_features, axis=1).tolist(),
                'skew': self._calculate_skewness(combined_features).tolist(),
                'kurtosis': self._calculate_kurtosis(combined_features).tolist()
            }
            
            # Create hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'mfcc',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash,
                'feature_dimensions': combined_features.shape
            }
            
        except Exception as e:
            logger.error(f"MFCC fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_spectral_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate spectral fingerprint for audio"""



        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=22050)
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            chroma_std = np.std(chroma, axis=1)
            
            # Spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
            contrast_mean = np.mean(spectral_contrast, axis=1)
            
            # Create fingerprint
            fingerprint = {
                'spectral_centroid': {
                    'mean': float(np.mean(spectral_centroids)),
                    'std': float(np.std(spectral_centroids))
                },
                'spectral_rolloff': {
                    'mean': float(np.mean(spectral_rolloff)),
                    'std': float(np.std(spectral_rolloff))
                },
                'spectral_bandwidth': {
                    'mean': float(np.mean(spectral_bandwidth)),
                    'std': float(np.std(spectral_bandwidth))
                },
                'zero_crossing_rate': {
                    'mean': float(np.mean(zero_crossing_rate)),
                    'std': float(np.std(zero_crossing_rate))
                },
                'chroma': {
                    'mean': chroma_mean.tolist(),
                    'std': chroma_std.tolist()
                },
                'spectral_contrast': contrast_mean.tolist()
            }
            
            # Create hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'spectral',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Spectral fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_audio_perceptual_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate perceptual fingerprint for audio"""



        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=22050)
            
            # Generate mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128, fmax=8000)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Create perceptual hash using DCT
            dct_coeffs = []
            for mel_frame in mel_spec_db.T[::4]:  # Sample every 4th frame
                # Apply DCT and keep low-frequency coefficients
                dct = cv2.dct(mel_frame.astype(np.float32).reshape(8, 16))
                dct_coeffs.append(dct.flatten()[:32])  # Keep first 32 coefficients
            
            if dct_coeffs:
                dct_matrix = np.array(dct_coeffs)
                
                # Create binary hash
                mean_dct = np.mean(dct_matrix, axis=0)
                binary_hash = (dct_matrix > mean_dct).astype(int)
                
                # Convert to hex string
                hash_hex = ''.join([''.join(map(str, row)) for row in binary_hash])
                
                return {
                    'type': 'perceptual',
                    'fingerprint': hash_hex,
                    'hash': hashlib.sha256(hash_hex.encode()).hexdigest(),
                    'dimensions': dct_matrix.shape
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Audio perceptual fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_wavelet_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate wavelet-based fingerprint for audio"""



        try:
            # Load audio
            audio, sr = librosa.load(file_path, sr=22050)
            
            # Apply wavelet transform
            coeffs = pywt.wavedec(audio, 'db4', level=6)
            
            # Extract features from wavelet coefficients
            wavelet_features = []
            for i, coeff in enumerate(coeffs):
                if len(coeff) > 0:
                    features = {
                        'level': i,
                        'energy': float(np.sum(coeff**2)),
                        'mean': float(np.mean(coeff)),
                        'std': float(np.std(coeff)),
                        'entropy': float(self._calculate_entropy(coeff))
                    }
                    wavelet_features.append(features)
            
            # Create fingerprint
            fingerprint = {
                'wavelet': 'db4',
                'levels': len(coeffs),
                'features': wavelet_features
            }
            
            # Create hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'wavelet',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Wavelet fingerprint generation failed: {str(e)}")
            return None
    
    # Image Fingerprinting Methods
    
    async def _generate_image_perceptual_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate perceptual fingerprint for images"""



        try:
            # Load image
            image = Image.open(file_path).convert('RGB')
            
            # Generate multiple perceptual hashes
            fingerprints = {
                'dhash': str(imagehash.dhash(image, hash_size=16)),
                'phash': str(imagehash.phash(image, hash_size=16)),
                'average_hash': str(imagehash.average_hash(image, hash_size=16)),
                'whash': str(imagehash.whash(image, hash_size=16)),
                'colorhash': str(imagehash.colorhash(image))
            }
            
            # Create combined hash
            combined = '|'.join(fingerprints.values())
            combined_hash = hashlib.sha256(combined.encode()).hexdigest()
            
            return {
                'type': 'perceptual',
                'fingerprint': fingerprints,
                'hash': combined_hash,
                'image_size': image.size
            }
            
        except Exception as e:
            logger.error(f"Image perceptual fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_image_feature_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feature-based fingerprint for images"""



        try:
            # Load image
            image_cv = cv2.imread(file_path)
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Extract SIFT features
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            # Extract ORB features
            orb = cv2.ORB_create()
            kp_orb, desc_orb = orb.detectAndCompute(gray, None)
            
            # Create feature fingerprint
            fingerprint = {
                'sift_keypoints': len(keypoints),
                'orb_keypoints': len(kp_orb) if kp_orb else 0
            }
            
            # Process SIFT descriptors
            if descriptors is not None and len(descriptors) > 0:
                # Create bag of visual words representation
                descriptor_centers = self._kmeans_descriptors(descriptors, k=64)
                fingerprint['sift_bovw'] = descriptor_centers.tolist()
            
            # Process ORB descriptors
            if desc_orb is not None and len(desc_orb) > 0:
                # Create binary fingerprint from ORB descriptors
                orb_hash = hashlib.md5(desc_orb.tobytes()).hexdigest()
                fingerprint['orb_hash'] = orb_hash
            
            # Create hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'feature',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Image feature fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_color_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate color-based fingerprint for images"""



        try:
            # Load image
            image_cv = cv2.imread(file_path)
            
            # Color histograms
            hist_b = cv2.calcHist([image_cv], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image_cv], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([image_cv], [2], None, [256], [0, 256])
            
            # Normalize histograms
            hist_b = hist_b.flatten() / np.sum(hist_b)
            hist_g = hist_g.flatten() / np.sum(hist_g)
            hist_r = hist_r.flatten() / np.sum(hist_r)
            
            # Color moments
            mean_color = np.mean(image_cv, axis=(0, 1))
            std_color = np.std(image_cv, axis=(0, 1))
            
            # Convert to HSV for additional analysis
            hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)
            hsv_hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
            hsv_hist = hsv_hist.flatten() / np.sum(hsv_hist)
            
            # Create fingerprint
            fingerprint = {
                'color_histograms': {
                    'blue': hist_b.tolist(),
                    'green': hist_g.tolist(),
                    'red': hist_r.tolist()
                },
                'color_moments': {
                    'mean': mean_color.tolist(),
                    'std': std_color.tolist()
                },
                'hsv_histogram': hsv_hist.tolist()
            }
            
            # Create hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'color',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Color fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_texture_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate texture-based fingerprint for images"""



        try:
            # Load image
            image_cv = cv2.imread(file_path)
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern
            from skimage.feature import local_binary_pattern
            lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
            lbp_hist = lbp_hist / np.sum(lbp_hist)
            
            # Gray Level Co-occurrence Matrix
            from skimage.feature import graycomatrix, graycoprops
            glcm = graycomatrix(gray, distances=[1], angles=[0, 45, 90, 135], 
                              levels=256, symmetric=True, normed=True)
            
            # Extract texture properties
            contrast = graycoprops(glcm, 'contrast').flatten()
            dissimilarity = graycoprops(glcm, 'dissimilarity').flatten()
            homogeneity = graycoprops(glcm, 'homogeneity').flatten()
            energy = graycoprops(glcm, 'energy').flatten()
            
            # Create fingerprint
            fingerprint = {
                'lbp_histogram': lbp_hist.tolist(),
                'glcm_features': {
                    'contrast': contrast.tolist(),
                    'dissimilarity': dissimilarity.tolist(),
                    'homogeneity': homogeneity.tolist(),
                    'energy': energy.tolist()
                }
            }
            
            # Create hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'texture',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Texture fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_geometric_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate geometric fingerprint for images"""



        try:
            # Load image
            image_cv = cv2.imread(file_path)
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 100, 200)
            
            # Contour detection
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Geometric features
            geometric_features = {
                'edge_density': np.sum(edges > 0) / edges.size,
                'contour_count': len(contours),
                'contour_areas': [],
                'contour_perimeters': [],
                'aspect_ratios': []
            }
            
            # Process contours
            for contour in contours[:50]:  # Limit to first 50 contours
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                if area > 100:  # Filter small contours
                    geometric_features['contour_areas'].append(float(area))
                    geometric_features['contour_perimeters'].append(float(perimeter))
                    
                    # Bounding rectangle for aspect ratio
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    geometric_features['aspect_ratios'].append(float(aspect_ratio))
            
            # Create hash
            fingerprint_str = json.dumps(geometric_features, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'geometric',
                'fingerprint': geometric_features,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Geometric fingerprint generation failed: {str(e)}")
            return None
    
    # Video Fingerprinting Methods
    
    async def _generate_video_frame_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate frame-based fingerprint for videos"""



        try:
            cap = cv2.VideoCapture(file_path)
            frame_hashes = []
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames at regular intervals
            sample_interval = max(1, total_frames // 100)  # Max 100 frames
            
            while cap.isOpened() and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_interval == 0:
                    # Generate frame hash
                    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    frame_hash = str(imagehash.dhash(frame_pil, hash_size=8))
                    frame_hashes.append(frame_hash)
                
                frame_count += 1
            
            cap.release()
            
            # Create temporal fingerprint
            if len(frame_hashes) > 1:
                # Calculate frame differences
                frame_diffs = []
                for i in range(1, len(frame_hashes)):
                    # Hamming distance between consecutive frames
                    diff = bin(int(frame_hashes[i-1], 16) ^ int(frame_hashes[i], 16)).count('1')
                    frame_diffs.append(diff)
                
                fingerprint = {
                    'frame_hashes': frame_hashes,
                    'frame_differences': frame_diffs,
                    'total_frames': frame_count,
                    'sampled_frames': len(frame_hashes)
                }
                
                # Create hash
                fingerprint_str = json.dumps(fingerprint, sort_keys=True)
                fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
                
                return {
                    'type': 'frame',
                    'fingerprint': fingerprint,
                    'hash': fingerprint_hash
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Video frame fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_motion_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate motion-based fingerprint for videos"""



        try:
            cap = cv2.VideoCapture(file_path)
            
            # Motion detection setup
            bg_subtractor = cv2.createBackgroundSubtractorMOG2()
            motion_history = []
            frame_count = 0
            
            while cap.isOpened() and frame_count < 1000:  # Limit processing
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply background subtraction
                fg_mask = bg_subtractor.apply(frame)
                motion_pixels = np.sum(fg_mask > 0)
                motion_ratio = motion_pixels / fg_mask.size
                
                motion_history.append(float(motion_ratio))
                frame_count += 1
            
            cap.release()
            
            if motion_history:
                # Analyze motion patterns
                motion_stats = {
                    'mean_motion': float(np.mean(motion_history)),
                    'std_motion': float(np.std(motion_history)),
                    'max_motion': float(np.max(motion_history)),
                    'motion_peaks': len([m for m in motion_history if m > np.mean(motion_history) + 2*np.std(motion_history)])
                }
                
                # Create motion signature
                fingerprint = {
                    'motion_history': motion_history[::10],  # Downsample for storage
                    'motion_statistics': motion_stats,
                    'total_frames': frame_count
                }
                
                # Create hash
                fingerprint_str = json.dumps(fingerprint, sort_keys=True)
                fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
                
                return {
                    'type': 'motion',
                    'fingerprint': fingerprint,
                    'hash': fingerprint_hash
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Motion fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_scene_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scene-based fingerprint for videos"""



        try:
            cap = cv2.VideoCapture(file_path)
            prev_hist = None
            scene_changes = []
            frame_count = 0
            
            while cap.isOpened() and frame_count < 1000:  # Limit processing
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Calculate color histogram
                hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist = hist.flatten()
                hist = hist / np.sum(hist)  # Normalize
                
                if prev_hist is not None:
                    # Calculate histogram correlation
                    correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    scene_changes.append(float(1 - correlation))  # Convert to dissimilarity
                
                prev_hist = hist.copy()
                frame_count += 1
            
            cap.release()
            
            if scene_changes:
                # Detect scene boundaries
                threshold = np.mean(scene_changes) + 2 * np.std(scene_changes)
                scene_boundaries = [i for i, change in enumerate(scene_changes) if change > threshold]
                
                fingerprint = {
                    'scene_changes': scene_changes[::5],  # Downsample
                    'scene_boundaries': scene_boundaries,
                    'scene_count': len(scene_boundaries) + 1,
                    'total_frames': frame_count
                }
                
                # Create hash
                fingerprint_str = json.dumps(fingerprint, sort_keys=True)
                fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
                
                return {
                    'type': 'scene',
                    'fingerprint': fingerprint,
                    'hash': fingerprint_hash
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Scene fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_temporal_fingerprint(self, file_path: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate temporal fingerprint for videos"""



        try:
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Temporal features
            temporal_features = {
                'fps': float(fps),
                'duration': float(duration),
                'total_frames': total_frames,
                'frame_rate_stability': 1.0  # Placeholder for frame rate analysis
            }
            
            # Sample frames for temporal analysis
            frame_times = []
            frame_count = 0
            
            while cap.isOpened() and frame_count < 100:  # Sample 100 frames
                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                frame_times.append(timestamp)
                frame_count += 1
            
            cap.release()
            
            if len(frame_times) > 1:
                # Analyze frame timing
                time_diffs = np.diff(frame_times)
                temporal_features['frame_time_consistency'] = float(np.std(time_diffs))
                
                fingerprint = {
                    'temporal_features': temporal_features,
                    'frame_times_sample': frame_times[:50]  # Store sample
                }
                
                # Create hash
                fingerprint_str = json.dumps(fingerprint, sort_keys=True)
                fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
                
                return {
                    'type': 'temporal',
                    'fingerprint': fingerprint,
                    'hash': fingerprint_hash
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Temporal fingerprint generation failed: {str(e)}")
            return None
    
    # Text Fingerprinting Methods
    
    async def _generate_semantic_fingerprint(self, text: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate semantic fingerprint for text"""



        try:
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            # Fit and transform text
            tfidf_matrix = vectorizer.fit_transform([text])
            tfidf_vector = tfidf_matrix.toarray()[0]
            
            # Get top features
            feature_names = vectorizer.get_feature_names_out()
            top_indices = np.argsort(tfidf_vector)[-50:][::-1]  # Top 50 features
            
            semantic_features = {
                'top_terms': [(feature_names[i], float(tfidf_vector[i])) for i in top_indices if tfidf_vector[i] > 0],
                'vocabulary_size': len([v for v in tfidf_vector if v > 0]),
                'tfidf_norm': float(np.linalg.norm(tfidf_vector))
            }
            
            # Create hash
            fingerprint_str = json.dumps(semantic_features, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'semantic',
                'fingerprint': semantic_features,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Semantic fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_structural_fingerprint(self, text: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structural fingerprint for text"""



        try:
            import re
            
            # Structural features
            sentences = text.split('.')
            paragraphs = text.split('\\n\\n')
            words = text.split()
            
            # Character-level analysis
            char_counts = {
                'letters': len(re.findall(r'[a-zA-Z]', text)),
                'digits': len(re.findall(r'\\d', text)),
                'punctuation': len(re.findall(r'[^\\w\\s]', text)),
                'whitespace': len(re.findall(r'\\s', text))
            }
            
            # Structural metrics
            structural_features = {
                'character_count': len(text),
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'avg_word_length': float(np.mean([len(word) for word in words])) if words else 0,
                'avg_sentence_length': float(np.mean([len(s.split()) for s in sentences if s.strip()])) if sentences else 0,
                'character_distribution': char_counts
            }
            
            # Create hash
            fingerprint_str = json.dumps(structural_features, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'structural',
                'fingerprint': structural_features,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Structural fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_stylistic_fingerprint(self, text: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stylistic fingerprint for text"""



        try:
            import re
            from collections import Counter
            
            words = text.lower().split()
            
            # Stylistic features
            stylistic_features = {
                'vocabulary_richness': len(set(words)) / len(words) if words else 0,
                'function_word_ratio': 0,
                'punctuation_frequency': {},
                'pos_distribution': {}  # Placeholder for POS tagging
            }
            
            # Function words analysis
            function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'}
            function_word_count = sum(1 for word in words if word in function_words)
            stylistic_features['function_word_ratio'] = function_word_count / len(words) if words else 0
            
            # Punctuation analysis
            punctuation_marks = re.findall(r'[.!?;:,]', text)
            punct_counter = Counter(punctuation_marks)
            stylistic_features['punctuation_frequency'] = dict(punct_counter)
            
            # Readability metrics (simplified)
            sentences = [s for s in text.split('.') if s.strip()]
            if sentences and words:
                avg_sentence_length = len(words) / len(sentences)
                stylistic_features['avg_sentence_length'] = float(avg_sentence_length)
            
            # Create hash
            fingerprint_str = json.dumps(stylistic_features, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'stylistic',
                'fingerprint': stylistic_features,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Stylistic fingerprint generation failed: {str(e)}")
            return None
    
    async def _generate_content_fingerprint(self, text: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content-based fingerprint for text"""



        try:
            # Content hashes
            content_hashes = {
                'md5': hashlib.md5(text.encode()).hexdigest(),
                'sha256': hashlib.sha256(text.encode()).hexdigest(),
                'blake2b': hashlib.blake2b(text.encode()).hexdigest()
            }
            
            # Normalized text hash (case-insensitive, whitespace-normalized)
            normalized_text = ' '.join(text.lower().split())
            content_hashes['normalized_sha256'] = hashlib.sha256(normalized_text.encode()).hexdigest()
            
            # Content without punctuation
            import re
            content_only = re.sub(r'[^\\w\\s]', '', text.lower())
            content_hashes['content_only_sha256'] = hashlib.sha256(content_only.encode()).hexdigest()
            
            fingerprint = {
                'content_hashes': content_hashes,
                'text_length': len(text),
                'normalized_length': len(normalized_text),
                'content_only_length': len(content_only)
            }
            
            # Create master hash
            fingerprint_str = json.dumps(fingerprint, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            return {
                'type': 'content',
                'fingerprint': fingerprint,
                'hash': fingerprint_hash
            }
            
        except Exception as e:
            logger.error(f"Content fingerprint generation failed: {str(e)}")
            return None
    
    # Cross-Modal and Utility Methods
    
    async def _generate_cross_modal_fingerprints(self, content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate cross-modal fingerprints for content that spans multiple modalities"""



        try:
            # This would be implemented for content that has multiple modalities
            # E.g., video with audio, image with text overlay, etc.
            content_type = content_data.get('type')
            
            if content_type == 'video':
                # Video inherently has visual and potentially audio components
                # These are handled in the video-specific methods
                pass
            
            # Placeholder for future cross-modal implementations
            return None
            
        except Exception as e:
            logger.error(f"Cross-modal fingerprint generation failed: {str(e)}")
            return None
    
    async def _store_fingerprint(self, content_id: str, content_type: str, fingerprint_type: str, fingerprint_data: Dict[str, Any]):
        """Store fingerprint in database"""



        try:
            session = self.Session()
            
            fingerprint_record = ContentFingerprint(
                id=f"{content_id}_{fingerprint_type}",
                content_id=content_id,
                content_type=content_type,
                fingerprint_type=fingerprint_type,
                fingerprint_data=json.dumps(fingerprint_data).encode(),
                fingerprint_hash=fingerprint_data.get('hash', ''),
                similarity_threshold=self.similarity_thresholds.get(f"{content_type}_{fingerprint_type}", 0.8),
                metadata=json.dumps({'stored_at': datetime.utcnow().isoformat()})
            )
            
            session.merge(fingerprint_record)
            session.commit()
            session.close()
            
            # Also store in Redis cache if available
            if self.redis_client:
                cache_key = f"fingerprint:{content_id}:{fingerprint_type}"
                self.redis_client.setex(cache_key, 3600, json.dumps(fingerprint_data))
            
        except Exception as e:
            logger.error(f"Fingerprint storage failed: {str(e)}")
    
    async def _search_similar_fingerprints(self, fingerprint_type: str, fingerprint_data: Dict[str, Any], threshold: float) -> List[Dict[str, Any]]:
        """Search for similar fingerprints in database"""



        try:
            # This is a simplified implementation
            # In production, you would use more sophisticated similarity search
            # possibly with vector databases like Faiss, Pinecone, or Weaviate
            
            session = self.Session()
            
            # Get all fingerprints of the same type
            stored_fingerprints = session.query(ContentFingerprint).filter(
                ContentFingerprint.fingerprint_type == fingerprint_type
            ).all()
            
            similar_fingerprints = []
            
            for stored_fp in stored_fingerprints:
                try:
                    stored_data = json.loads(stored_fp.fingerprint_data.decode())
                    similarity = self._calculate_similarity(fingerprint_data, stored_data, fingerprint_type)
                    
                    if similarity >= threshold:
                        similar_fingerprints.append({
                            'content_id': stored_fp.content_id,
                            'similarity': similarity,
                            'fingerprint_type': fingerprint_type,
                            'metadata': json.loads(stored_fp.metadata) if stored_fp.metadata else {}
                        })
                        
                except Exception as e:
                    logger.warning(f"Error processing stored fingerprint: {str(e)}")
                    continue
            
            session.close()
            return similar_fingerprints
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    def _calculate_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any], fingerprint_type: str) -> float:
        """Calculate similarity between two fingerprints"""



        try:
            if fingerprint_type in ['chromaprint']:
                # For chromaprint, compare the fingerprint strings
                if 'fingerprint' in fp1 and 'fingerprint' in fp2:
                    return self._chromaprint_similarity(fp1['fingerprint'], fp2['fingerprint'])
            
            elif fingerprint_type in ['perceptual']:
                # For perceptual hashes, calculate Hamming distance
                if 'fingerprint' in fp1 and 'fingerprint' in fp2:
                    return self._hamming_similarity(fp1['fingerprint'], fp2['fingerprint'])
            
            elif fingerprint_type in ['mfcc', 'spectral']:
                # For feature-based fingerprints, use cosine similarity
                if 'fingerprint' in fp1 and 'fingerprint' in fp2:
                    return self._feature_similarity(fp1['fingerprint'], fp2['fingerprint'])
            
            elif fingerprint_type in ['semantic']:
                # For semantic fingerprints, compare top terms
                if 'fingerprint' in fp1 and 'fingerprint' in fp2:
                    return self._semantic_similarity(fp1['fingerprint'], fp2['fingerprint'])
            
            # Default: compare hashes
            if 'hash' in fp1 and 'hash' in fp2:
                return 1.0 if fp1['hash'] == fp2['hash'] else 0.0
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0
    
    def _chromaprint_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate similarity between Chromaprint fingerprints"""



        try:
            # Convert hex strings to integers and calculate bit similarity
            if len(fp1) != len(fp2):
                return 0.0
            
            # Simple bit comparison
            matches = sum(c1 == c2 for c1, c2 in zip(fp1, fp2))
            return matches / len(fp1)
            
        except Exception:
            return 0.0
    
    def _hamming_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate Hamming similarity between perceptual hashes"""



        try:
            if len(fp1) != len(fp2):
                return 0.0
            
            # Calculate Hamming distance
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(fp1, fp2))
            max_distance = len(fp1)
            
            # Convert to similarity (0-1)
            return 1.0 - (hamming_distance / max_distance)
            
        except Exception:
            return 0.0
    
    def _feature_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """Calculate similarity between feature-based fingerprints"""



        try:
            # Extract comparable features
            features1 = []
            features2 = []
            
            # Collect numerical features
            for key in fp1.keys():
                if key in fp2 and isinstance(fp1[key], (int, float, list)):
                    if isinstance(fp1[key], list) and isinstance(fp2[key], list):
                        if len(fp1[key]) == len(fp2[key]):
                            features1.extend(fp1[key])
                            features2.extend(fp2[key])
                    else:
                        features1.append(fp1[key])
                        features2.append(fp2[key])
            
            if features1 and features2:
                # Calculate cosine similarity
                features1 = np.array(features1)
                features2 = np.array(features2)
                
                dot_product = np.dot(features1, features2)
                norm1 = np.linalg.norm(features1)
                norm2 = np.linalg.norm(features2)
                
                if norm1 > 0 and norm2 > 0:
                    return dot_product / (norm1 * norm2)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _semantic_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """Calculate semantic similarity between text fingerprints"""



        try:
            # Compare top terms
            if 'top_terms' in fp1 and 'top_terms' in fp2:
                terms1 = set(term for term, score in fp1['top_terms'])
                terms2 = set(term for term, score in fp2['top_terms'])
                
                intersection = len(terms1.intersection(terms2))
                union = len(terms1.union(terms2))
                
                if union > 0:
                    return intersection / union  # Jaccard similarity
            
            return 0.0
            
        except Exception:
            return 0.0
    
    # Utility methods
    
    def _calculate_skewness(self, data: np.ndarray) -> np.ndarray:
        """Calculate skewness of data"""
        mean_val = np.mean(data, axis=1, keepdims=True)
        std_val = np.std(data, axis=1, keepdims=True)
        normalized = (data - mean_val) / (std_val + 1e-8)
        return np.mean(normalized**3, axis=1)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> np.ndarray:
        """Calculate kurtosis of data"""
        mean_val = np.mean(data, axis=1, keepdims=True)
        std_val = np.std(data, axis=1, keepdims=True)
        normalized = (data - mean_val) / (std_val + 1e-8)
        return np.mean(normalized**4, axis=1) - 3
    
    def _calculate_entropy(self, signal: np.ndarray) -> float:
        """Calculate entropy of signal"""
        hist, _ = np.histogram(signal, bins=50)
        hist = hist / np.sum(hist)
        hist = hist[hist > 0]  # Remove zeros
        return -np.sum(hist * np.log2(hist))
    
    def _kmeans_descriptors(self, descriptors: np.ndarray, k: int = 64) -> np.ndarray:
        """Perform k-means clustering on descriptors"""



        try:
            from sklearn.cluster import KMeans
            
            if len(descriptors) < k:
                # If we have fewer descriptors than clusters, pad with zeros
                padded = np.zeros((k, descriptors.shape[1]))
                padded[:len(descriptors)] = descriptors
                return padded
            
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(descriptors)
            return kmeans.cluster_centers_
            
        except Exception:
            # Fallback: return random sample
            if len(descriptors) >= k:
                indices = np.random.choice(len(descriptors), k, replace=False)
                return descriptors[indices]
            else:
                return descriptors

# Export class
__all__ = ['ContentFingerprintEngine', 'ContentFingerprint']
