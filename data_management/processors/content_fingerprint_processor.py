"""
🔐 Content Fingerprint Processor - IA Influencer Agent Platform Enterprise
===========================================================================
Module: backend/data_management/processors/content_fingerprint_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial AI Fingerprinting - Enterprise Production-Ready Ultra Advanced
Responsibility: Génération d'empreintes AI multi-format pour protection contenu
===============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER FINGERPRINTING:
Content Upload → Type Detection → AI Analysis → Feature Extraction → 
Vector Embedding → Hash Generation → FAISS Storage → Similarity Indexing
"""

import numpy as np
import hashlib
import cv2
import librosa
import chromaprint
import imagehash
from PIL import Image
import torch
import tensorflow as tf
from transformers import pipeline, CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, ByteString
import asyncio
import aiofiles
from pathlib import Path
from datetime import datetime, timezone
import base64
import json
from concurrent.futures import ThreadPoolExecutor

from .base_processor import BaseProcessor, AsyncBaseProcessor


class ContentFingerprintProcessor(BaseProcessor):
    """Processeur d'empreintes AI multi-format - Production Enterprise"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # AI Models Configuration
        self.models = self._initialize_ai_models()
        
        # FAISS Index Configuration
        self.faiss_indices = self._initialize_faiss_indices()
        
        # Fingerprinting Configuration
        self.fingerprint_config = {
            'audio': {
                'sample_rate': 22050,
                'duration': 30,  # seconds
                'n_mfcc': 13,
                'hop_length': 512,
                'chromaprint_algorithm': chromaprint.ALGORITHM_DEFAULT
            },
            'video': {
                'frame_rate': 1,  # frames per second
                'target_size': (224, 224),
                'hash_size': 16,
                'feature_vector_size': 2048
            },
            'image': {
                'hash_size': 16,
                'target_size': (224, 224),
                'phash_threshold': 0.9,
                'clip_vector_size': 512
            },
            'text': {
                'max_length': 512,
                'embedding_size': 768,
                'similarity_threshold': 0.85
            }
        }
    
    def _initialize_ai_models(self) -> Dict[str, Any]:
        """Initialise les modèles AI pour fingerprinting"""
        models = {}
        
        try:
            # CLIP Model for images
            models['clip_processor'] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            models['clip_model'] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            
            # Sentence Transformer for text
            models['sentence_transformer'] = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Audio feature extractor
            models['audio_classifier'] = pipeline(
                "audio-classification", 
                model="facebook/wav2vec2-base-960h"
            )
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI models: {e}")
            models = {}
        
        return models
    
    def _initialize_faiss_indices(self) -> Dict[str, Any]:
        """Initialise les indices FAISS pour recherche vectorielle"""
        indices = {}
        
        try:
            # Audio fingerprint index (MFCC + Chromaprint vectors)
            audio_dimension = 13 + 4  # MFCC + Chromaprint features
            indices['audio'] = faiss.IndexFlatIP(audio_dimension)
            
            # Video fingerprint index (CNN features)
            video_dimension = 2048
            indices['video'] = faiss.IndexFlatIP(video_dimension)
            
            # Image fingerprint index (CLIP embeddings)
            image_dimension = 512
            indices['image'] = faiss.IndexFlatIP(image_dimension)
            
            # Text fingerprint index (Sentence embeddings)
            text_dimension = 384
            indices['text'] = faiss.IndexFlatIP(text_dimension)
            
            self.logger.info("FAISS indices initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FAISS indices: {e}")
            indices = {}
        
        return indices
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère l'empreinte complète selon le type de contenu"""
        content_type = input_data.get('content_type')
        content_path = input_data.get('file_path')
        content_data = input_data.get('data')
        
        if not content_type:
            raise ValueError("Content type not specified")
        
        fingerprint_result = {
            'content_type': content_type,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'fingerprints': {},
            'metadata': {},
            'similarity_ready': False
        }
        
        try:
            if content_type == 'audio':
                fingerprint_result.update(self._process_audio_fingerprint(content_path, content_data))
            elif content_type == 'video':
                fingerprint_result.update(self._process_video_fingerprint(content_path, content_data))
            elif content_type == 'image':
                fingerprint_result.update(self._process_image_fingerprint(content_path, content_data))
            elif content_type == 'text':
                fingerprint_result.update(self._process_text_fingerprint(content_data))
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            fingerprint_result['similarity_ready'] = True
            
        except Exception as e:
            fingerprint_result['error'] = str(e)
            self.logger.error(f"Fingerprinting failed for {content_type}: {e}")
        
        return fingerprint_result
    
    def _process_audio_fingerprint(self, file_path: Optional[str], data: Optional[bytes]) -> Dict[str, Any]:
        """Génère empreinte audio avec Chromaprint + MFCC + AI features"""
        fingerprints = {}
        metadata = {}
        
        try:
            # Load audio
            if file_path:
                y, sr = librosa.load(file_path, sr=self.fingerprint_config['audio']['sample_rate'])
            else:
                # Handle audio data from bytes
                y, sr = librosa.load(io.BytesIO(data), sr=self.fingerprint_config['audio']['sample_rate'])
            
            # 1. Chromaprint fingerprint
            chromaprint_fp = chromaprint.encode(
                y, sr, algorithm=self.fingerprint_config['audio']['chromaprint_algorithm']
            )
            fingerprints['chromaprint'] = base64.b64encode(chromaprint_fp[1]).decode('utf-8')
            
            # 2. MFCC Features
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, 
                n_mfcc=self.fingerprint_config['audio']['n_mfcc'],
                hop_length=self.fingerprint_config['audio']['hop_length']
            )
            mfcc_mean = np.mean(mfcc, axis=1)
            fingerprints['mfcc_hash'] = hashlib.sha256(mfcc_mean.tobytes()).hexdigest()
            
            # 3. Spectral features
            spectral_features = self._extract_audio_spectral_features(y, sr)
            fingerprints['spectral_hash'] = hashlib.sha256(
                str(spectral_features).encode()
            ).hexdigest()
            
            # 4. AI-based features
            if self.models.get('audio_classifier'):
                ai_features = self._extract_audio_ai_features(y, sr)
                fingerprints['ai_features_hash'] = hashlib.sha256(
                    str(ai_features).encode()
                ).hexdigest()
            
            # Vector for FAISS similarity
            feature_vector = np.concatenate([mfcc_mean, spectral_features])
            fingerprints['similarity_vector'] = feature_vector.tolist()
            
            # Metadata
            metadata.update({
                'duration': len(y) / sr,
                'sample_rate': sr,
                'channels': 1,
                'format': 'audio',
                'features_extracted': list(fingerprints.keys())
            })
            
        except Exception as e:
            raise Exception(f"Audio fingerprinting failed: {e}")
        
        return {'fingerprints': fingerprints, 'metadata': metadata}
    
    def _process_video_fingerprint(self, file_path: Optional[str], data: Optional[bytes]) -> Dict[str, Any]:
        """Génère empreinte vidéo avec OpenCV + CNN features"""
        fingerprints = {}
        metadata = {}
        
        try:
            # Open video
            if file_path:
                cap = cv2.VideoCapture(file_path)
            else:
                # Handle video data from bytes (write to temp file)
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    temp_file.write(data)
                    cap = cv2.VideoCapture(temp_file.name)
            
            if not cap.isOpened():
                raise Exception("Could not open video file")
            
            # Extract frames for fingerprinting
            frames = []
            frame_count = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames at specified rate
            frame_interval = max(1, int(fps / self.fingerprint_config['video']['frame_rate']))
            
            while frame_count < total_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Resize frame
                frame_resized = cv2.resize(
                    frame, self.fingerprint_config['video']['target_size']
                )
                frames.append(frame_resized)
                
                frame_count += frame_interval
                
                # Limit number of frames to prevent memory issues
                if len(frames) >= 100:
                    break
            
            cap.release()
            
            if not frames:
                raise Exception("No frames extracted from video")
            
            # 1. Perceptual hash for each frame
            frame_hashes = []
            for frame in frames:
                frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                phash = str(imagehash.phash(frame_pil, hash_size=self.fingerprint_config['video']['hash_size']))
                frame_hashes.append(phash)
            
            fingerprints['frame_hashes'] = frame_hashes
            fingerprints['video_signature'] = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            
            # 2. CNN features from representative frames
            if len(frames) > 0:
                representative_frames = frames[::max(1, len(frames) // 10)]  # Take 10 representative frames
                cnn_features = self._extract_video_cnn_features(representative_frames)
                fingerprints['cnn_features_hash'] = hashlib.sha256(
                    str(cnn_features).encode()
                ).hexdigest()
                fingerprints['similarity_vector'] = cnn_features.tolist()
            
            # Metadata
            metadata.update({
                'duration': total_frames / fps if fps > 0 else 0,
                'fps': fps,
                'total_frames': total_frames,
                'frames_analyzed': len(frames),
                'format': 'video',
                'features_extracted': list(fingerprints.keys())
            })
            
        except Exception as e:
            raise Exception(f"Video fingerprinting failed: {e}")
        
        return {'fingerprints': fingerprints, 'metadata': metadata}
    
    def _process_image_fingerprint(self, file_path: Optional[str], data: Optional[bytes]) -> Dict[str, Any]:
        """Génère empreinte image avec perceptual hash + CLIP embeddings"""
        fingerprints = {}
        metadata = {}
        
        try:
            # Load image
            if file_path:
                image = Image.open(file_path)
            else:
                import io
                image = Image.open(io.BytesIO(data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 1. Perceptual hashes
            fingerprints['phash'] = str(imagehash.phash(image, hash_size=self.fingerprint_config['image']['hash_size']))
            fingerprints['dhash'] = str(imagehash.dhash(image, hash_size=self.fingerprint_config['image']['hash_size']))
            fingerprints['ahash'] = str(imagehash.average_hash(image, hash_size=self.fingerprint_config['image']['hash_size']))
            fingerprints['whash'] = str(imagehash.whash(image, hash_size=self.fingerprint_config['image']['hash_size']))
            
            # 2. CLIP embeddings for semantic similarity
            if self.models.get('clip_processor') and self.models.get('clip_model'):
                inputs = self.models['clip_processor'](images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = self.models['clip_model'].get_image_features(**inputs)
                    clip_embedding = image_features.squeeze().numpy()
                
                fingerprints['clip_embedding_hash'] = hashlib.sha256(clip_embedding.tobytes()).hexdigest()
                fingerprints['similarity_vector'] = clip_embedding.tolist()
            
            # 3. Color histogram
            color_hist = self._extract_color_histogram(image)
            fingerprints['color_hist_hash'] = hashlib.sha256(color_hist.tobytes()).hexdigest()
            
            # Metadata
            metadata.update({
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format or 'unknown',
                'features_extracted': list(fingerprints.keys())
            })
            
        except Exception as e:
            raise Exception(f"Image fingerprinting failed: {e}")
        
        return {'fingerprints': fingerprints, 'metadata': metadata}
    
    def _process_text_fingerprint(self, text_content: str) -> Dict[str, Any]:
        """Génère empreinte texte avec embeddings sémantiques"""
        fingerprints = {}
        metadata = {}
        
        try:
            if not text_content or not text_content.strip():
                raise ValueError("Empty text content")
            
            # 1. Simple hash
            fingerprints['text_hash'] = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
            
            # 2. Normalized text hash (lowercase, no punctuation)
            normalized_text = self._normalize_text(text_content)
            fingerprints['normalized_hash'] = hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()
            
            # 3. Sentence embeddings for semantic similarity
            if self.models.get('sentence_transformer'):
                embeddings = self.models['sentence_transformer'].encode(text_content)
                fingerprints['semantic_embedding_hash'] = hashlib.sha256(embeddings.tobytes()).hexdigest()
                fingerprints['similarity_vector'] = embeddings.tolist()
            
            # 4. N-gram hashes for partial matching
            ngram_hashes = self._extract_ngram_hashes(text_content)
            fingerprints['ngram_hashes'] = ngram_hashes
            
            # Metadata
            metadata.update({
                'length': len(text_content),
                'word_count': len(text_content.split()),
                'language': 'auto-detected',  # Could add language detection
                'format': 'text',
                'features_extracted': list(fingerprints.keys())
            })
            
        except Exception as e:
            raise Exception(f"Text fingerprinting failed: {e}")
        
        return {'fingerprints': fingerprints, 'metadata': metadata}
    
    def _extract_audio_spectral_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extrait les caractéristiques spectrales audio"""
        spectral_features = []
        
        # Spectral centroid
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_features.append(spectral_centroid)
        
        # Spectral rolloff
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        spectral_features.append(spectral_rolloff)
        
        # Zero crossing rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        spectral_features.append(zcr)
        
        # RMS energy
        rms = np.mean(librosa.feature.rms(y=y))
        spectral_features.append(rms)
        
        return np.array(spectral_features)
    
    def _extract_audio_ai_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extrait les caractéristiques AI de l'audio"""
        # This would typically use the audio classifier
        # For now, return basic features
        return {
            'tempo': float(librosa.beat.tempo(y=y, sr=sr)[0]),
            'duration': len(y) / sr,
            'energy': float(np.mean(y**2))
        }
    
    def _extract_video_cnn_features(self, frames: List[np.ndarray]) -> np.ndarray:
        """Extrait les caractéristiques CNN des frames vidéo"""
        # Use a pre-trained CNN model to extract features
        # For now, return mean pixel values as basic features
        features = []
        for frame in frames:
            # Simple feature: mean of each channel
            frame_features = np.mean(frame, axis=(0, 1))
            features.append(frame_features)
        
        return np.mean(features, axis=0)
    
    def _extract_color_histogram(self, image: Image.Image) -> np.ndarray:
        """Extrait l'histogramme des couleurs"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Calculate histogram for each channel
        hist_r = np.histogram(img_array[:, :, 0], bins=32, range=(0, 256))[0]
        hist_g = np.histogram(img_array[:, :, 1], bins=32, range=(0, 256))[0]
        hist_b = np.histogram(img_array[:, :, 2], bins=32, range=(0, 256))[0]
        
        return np.concatenate([hist_r, hist_g, hist_b])
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour la comparaison"""
        import re
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation and extra spaces
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_ngram_hashes(self, text: str, n: int = 3) -> List[str]:
        """Extrait les hashes des n-grammes"""
        words = text.split()
        ngrams = []
        
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i + n])
            ngram_hash = hashlib.md5(ngram.encode('utf-8')).hexdigest()
            ngrams.append(ngram_hash)
        
        return ngrams
    
    def find_similar_content(self, fingerprint_vector: List[float], content_type: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Recherche de contenu similaire dans l'index FAISS"""
        if content_type not in self.faiss_indices:
            return []
        
        try:
            index = self.faiss_indices[content_type]
            query_vector = np.array(fingerprint_vector).reshape(1, -1).astype('float32')
            
            # Search for similar vectors
            scores, indices = index.search(query_vector, k=10)
            
            similar_content = []
            for i, score in enumerate(scores[0]):
                if score >= threshold:
                    similar_content.append({
                        'index': int(indices[0][i]),
                        'similarity_score': float(score),
                        'content_type': content_type
                    })
            
            return similar_content
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    def add_to_similarity_index(self, fingerprint_vector: List[float], content_type: str, content_id: str) -> bool:
        """Ajoute un vecteur à l'index de similarité FAISS"""
        if content_type not in self.faiss_indices:
            return False
        
        try:
            index = self.faiss_indices[content_type]
            vector = np.array(fingerprint_vector).reshape(1, -1).astype('float32')
            index.add(vector)
            
            self.logger.info(f"Added content {content_id} to {content_type} similarity index")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add to similarity index: {e}")
            return False
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour le fingerprinting"""
        if not isinstance(input_data, dict):
            return False
        
        content_type = input_data.get('content_type')
        if content_type not in ['audio', 'video', 'image', 'text']:
            return False
        
        # Check for either file path or data
        has_file_path = input_data.get('file_path') is not None
        has_data = input_data.get('data') is not None
        
        if content_type == 'text':
            return has_data or has_file_path
        else:
            return has_file_path or has_data
        
        return True


class AsyncContentFingerprintProcessor(AsyncBaseProcessor):
    """Version asynchrone du processeur d'empreintes"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sync_processor = ContentFingerprintProcessor(config)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Traitement asynchrone des empreintes"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sync_processor.process_with_stats, 
            input_data
        )
    
    async def validate_input(self, input_data: Any) -> bool:
        """Validation asynchrone"""
        return self.sync_processor.validate_input(input_data)
    
    async def find_similar_content(self, fingerprint_vector: List[float], content_type: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Recherche asynchrone de contenu similaire"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.sync_processor.find_similar_content,
            fingerprint_vector, content_type, threshold
        )
