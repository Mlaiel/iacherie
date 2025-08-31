"""Advanced Multi-Modal Content Fingerprinting Processor
Professional Industrial Content Protection Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
License: Proprietary - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, or use without explicit written permission from Fahed Mlaiel
is strictly prohibited and may result in legal action.
"""import asyncio
import hashlib
import json
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
import cv2
import librosa
import imagehash
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.database import get_database
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.utils.media import MediaProcessor
from backend.utils.storage import CloudStorageManager

logger = logging.getLogger(__name__)


class ContentFingerprintProcessor:
    """Advanced multi-modal content fingerprinting engine for copyright protection"""    
    def __init__(self):
        self.db = get_database()
        self.security = SecurityManager()
        self.media_processor = MediaProcessor()
        self.storage = CloudStorageManager()
        self.similarity_threshold = 0.85
        
        # Audio fingerprinting parameters
        self.audio_params = {
            'sample_rate': 22050,
            'n_mfcc': 13,
            'n_fft': 2048,
            'hop_length': 512,
            'window_size': 2048
        }
        
        # Image fingerprinting parameters
        self.image_params = {
            'hash_size': 16,
            'resize_target': (256, 256),
            'color_channels': 3
        }
        
        # Text fingerprinting parameters
        self.text_params = {
            'ngram_range': (1, 3),
            'max_features': 10000,
            'min_df': 2,
            'max_df': 0.95
        }

    async def generate_fingerprint(
        self,
        content_id: str,
        content_type: str,
        file_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive fingerprint for any content type"""        try:
            logger.info(f"Generating fingerprint for content {content_id}")
            
            fingerprint_data = {
                'content_id': content_id,
                'content_type': content_type,
                'file_path': file_path,
                'metadata': metadata or {},
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'fingerprints': {}
            }
            
            # Generate type-specific fingerprints
            if content_type.startswith('audio'):
                fingerprint_data['fingerprints'] = await self._generate_audio_fingerprint(file_path)
            elif content_type.startswith('image'):
                fingerprint_data['fingerprints'] = await self._generate_image_fingerprint(file_path)
            elif content_type.startswith('video'):
                fingerprint_data['fingerprints'] = await self._generate_video_fingerprint(file_path)
            elif content_type.startswith('text'):
                fingerprint_data['fingerprints'] = await self._generate_text_fingerprint(file_path)
            else:
                fingerprint_data['fingerprints'] = await self._generate_binary_fingerprint(file_path)
            
            # Add universal hash
            fingerprint_data['fingerprints']['universal_hash'] = await self._generate_universal_hash(file_path)
            
            # Store in database
            await self._store_fingerprint(fingerprint_data)
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Error generating fingerprint for {content_id}: {str(e)}")
            raise ProcessingError(f"Fingerprint generation failed: {str(e)}")

    async def _generate_audio_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate advanced audio fingerprint using multiple techniques"""        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=self.audio_params['sample_rate'])
            
            # Spectral features
            mfccs = librosa.feature.mfcc(
                y=y, 
                sr=sr,
                n_mfcc=self.audio_params['n_mfcc'],
                n_fft=self.audio_params['n_fft'],
                hop_length=self.audio_params['hop_length']
            )
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Harmonic and percussive separation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            
            return {
                'mfcc_mean': np.mean(mfccs, axis=1).tolist(),
                'mfcc_std': np.std(mfccs, axis=1).tolist(),
                'chroma_mean': np.mean(chroma, axis=1).tolist(),
                'chroma_std': np.std(chroma, axis=1).tolist(),
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_centroid_std': float(np.std(spectral_centroids)),
                'zcr_mean': float(np.mean(zcr)),
                'zcr_std': float(np.std(zcr)),
                'tempo': float(tempo),
                'duration': float(len(y) / sr),
                'harmonic_ratio': float(np.mean(np.abs(y_harmonic)) / np.mean(np.abs(y))),
                'percussive_ratio': float(np.mean(np.abs(y_percussive)) / np.mean(np.abs(y)))
            }
            
        except Exception as e:
            logger.error(f"Audio fingerprint generation error: {str(e)}")
            raise ProcessingError(f"Audio fingerprint failed: {str(e)}")

    async def _generate_image_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate advanced image fingerprint using multiple hash algorithms"""        try:
            # Load image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Generate different hash types
            perceptual_hash = str(imagehash.phash(image, hash_size=self.image_params['hash_size']))
            average_hash = str(imagehash.average_hash(image, hash_size=self.image_params['hash_size']))
            difference_hash = str(imagehash.dhash(image, hash_size=self.image_params['hash_size']))
            wavelet_hash = str(imagehash.whash(image, hash_size=self.image_params['hash_size']))
            
            # Color histogram
            image_array = np.array(image.resize(self.image_params['resize_target']))
            color_hist = cv2.calcHist([image_array], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            # Edge detection
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Texture features (LBP-like)
            texture_features = self._calculate_texture_features(gray)
            
            return {
                'perceptual_hash': perceptual_hash,
                'average_hash': average_hash,
                'difference_hash': difference_hash,
                'wavelet_hash': wavelet_hash,
                'color_histogram': color_hist.flatten().tolist(),
                'edge_density': float(edge_density),
                'texture_features': texture_features,
                'dimensions': list(image.size),
                'aspect_ratio': float(image.size[0] / image.size[1])
            }
            
        except Exception as e:
            logger.error(f"Image fingerprint generation error: {str(e)}")
            raise ProcessingError(f"Image fingerprint failed: {str(e)}")

    async def _generate_video_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate advanced video fingerprint by sampling frames and audio"""        try:
            cap = cv2.VideoCapture(file_path)
            
            # Video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frames at regular intervals
            sample_count = min(10, frame_count)
            frame_indices = np.linspace(0, frame_count - 1, sample_count, dtype=int)
            
            frame_fingerprints = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert frame to PIL Image for hashing
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(frame_rgb)
                    
                    frame_hash = str(imagehash.phash(pil_frame, hash_size=8))
                    frame_fingerprints.append(frame_hash)
            
            cap.release()
            
            # Extract audio if available
            audio_fingerprint = {}
            try:
                # Try to extract audio track
                y, sr = librosa.load(file_path, sr=self.audio_params['sample_rate'])
                if len(y) > 0:
                    audio_fingerprint = await self._generate_audio_fingerprint(file_path)
            except:
                logger.warning(f"No audio track found in video: {file_path}")
            
            return {
                'frame_hashes': frame_fingerprints,
                'fps': float(fps),
                'duration': float(duration),
                'frame_count': int(frame_count),
                'audio_fingerprint': audio_fingerprint,
                'video_hash': hashlib.md5(''.join(frame_fingerprints).encode()).hexdigest()
            }
            
        except Exception as e:
            logger.error(f"Video fingerprint generation error: {str(e)}")
            raise ProcessingError(f"Video fingerprint failed: {str(e)}")

    async def _generate_text_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate advanced text fingerprint using NLP techniques"""        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Basic statistics
            word_count = len(text.split())
            char_count = len(text)
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                ngram_range=self.text_params['ngram_range'],
                max_features=self.text_params['max_features'],
                min_df=self.text_params['min_df'],
                max_df=self.text_params['max_df'],
                stop_words='english'
            )
            
            # Create corpus with the text (need at least 2 documents for TF-IDF)
            corpus = [text, "dummy text"]
            tfidf_matrix = vectorizer.fit_transform(corpus)
            
            # Get top features for the actual document
            feature_names = vectorizer.get_feature_names_out()
            doc_vector = tfidf_matrix[0].toarray().flatten()
            top_indices = np.argsort(doc_vector)[-50:]  # Top 50 features
            
            top_features = {
                feature_names[i]: float(doc_vector[i]) 
                for i in top_indices if doc_vector[i] > 0
            }
            
            # Character n-grams for stylometry
            char_ngrams = {}
            for n in range(2, 5):
                ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
                char_ngrams[f'{n}gram_count'] = len(set(ngrams))
            
            # Lexical diversity
            unique_words = len(set(text.lower().split()))
            lexical_diversity = unique_words / word_count if word_count > 0 else 0
            
            return {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': sentence_count,
                'lexical_diversity': float(lexical_diversity),
                'top_tfidf_features': top_features,
                'char_ngrams': char_ngrams,
                'text_hash': hashlib.sha256(text.encode()).hexdigest(),
                'length_stats': {
                    'avg_word_length': float(np.mean([len(word) for word in text.split()])) if word_count > 0 else 0,
                    'avg_sentence_length': float(word_count / sentence_count) if sentence_count > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Text fingerprint generation error: {str(e)}")
            raise ProcessingError(f"Text fingerprint failed: {str(e)}")

    async def _generate_binary_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate fingerprint for binary files"""        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            return {
                'file_size': len(content),
                'md5_hash': hashlib.md5(content).hexdigest(),
                'sha256_hash': hashlib.sha256(content).hexdigest(),
                'entropy': self._calculate_entropy(content)
            }
            
        except Exception as e:
            logger.error(f"Binary fingerprint generation error: {str(e)}")
            raise ProcessingError(f"Binary fingerprint failed: {str(e)}")

    async def _generate_universal_hash(self, file_path: str) -> str:
        """Generate universal hash for any file type"""        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.blake2b(content).hexdigest()
        except Exception as e:
            logger.error(f"Universal hash generation error: {str(e)}")
            return ""

    def _calculate_texture_features(self, gray_image: np.ndarray) -> List[float]:
        """Calculate texture features using statistical methods"""        try:
            # Calculate co-occurrence matrix features
            from skimage.feature import greycomatrix, greycoprops
            
            # Resize for consistent processing
            gray_resized = cv2.resize(gray_image, (64, 64))
            
            # Calculate GLCM
            glcm = greycomatrix(
                gray_resized, 
                distances=[1], 
                angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], 
                levels=256,
                symmetric=True, 
                normed=True
            )
            
            # Extract texture properties
            contrast = greycoprops(glcm, 'contrast').flatten()
            dissimilarity = greycoprops(glcm, 'dissimilarity').flatten()
            homogeneity = greycoprops(glcm, 'homogeneity').flatten()
            energy = greycoprops(glcm, 'energy').flatten()
            
            return np.concatenate([contrast, dissimilarity, homogeneity, energy]).tolist()
            
        except Exception:
            # Fallback to simple statistical features
            return [
                float(np.mean(gray_image)),
                float(np.std(gray_image)),
                float(np.min(gray_image)),
                float(np.max(gray_image))
            ]

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of binary data"""        if not data:
            return 0.0
        
        # Count byte frequencies
        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        data_len = len(data)
        for count in byte_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy

    async def _store_fingerprint(self, fingerprint_data: Dict[str, Any]) -> None:
        """Store fingerprint data in database"""        try:
            query = """            INSERT INTO content_fingerprints 
            (content_id, content_type, fingerprint_data, created_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (content_id) 
            DO UPDATE SET 
                fingerprint_data = EXCLUDED.fingerprint_data,
                updated_at = NOW()
            """            
            await self.db.execute(
                query,
                fingerprint_data['content_id'],
                fingerprint_data['content_type'],
                json.dumps(fingerprint_data['fingerprints']),
                datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error storing fingerprint: {str(e)}")
            raise ProcessingError(f"Fingerprint storage failed: {str(e)}")

    async def find_similar_content(
        self,
        fingerprint_data: Dict[str, Any],
        content_type: str,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """Find similar content based on fingerprint comparison"""        try:
            threshold = threshold or self.similarity_threshold
            
            # Get all fingerprints of the same type
            query = """            SELECT content_id, fingerprint_data, created_at
            FROM content_fingerprints
            WHERE content_type = $1
            """            
            rows = await self.db.fetch(query, content_type)
            
            similar_content = []
            for row in rows:
                stored_fingerprint = json.loads(row['fingerprint_data'])
                similarity = self._calculate_similarity(
                    fingerprint_data['fingerprints'],
                    stored_fingerprint,
                    content_type
                )
                
                if similarity >= threshold:
                    similar_content.append({
                        'content_id': row['content_id'],
                        'similarity': similarity,
                        'created_at': row['created_at'].isoformat()
                    })
            
            # Sort by similarity (descending)
            similar_content.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similar_content
            
        except Exception as e:
            logger.error(f"Error finding similar content: {str(e)}")
            raise ProcessingError(f"Similarity search failed: {str(e)}")

    def _calculate_similarity(
        self,
        fingerprint1: Dict[str, Any],
        fingerprint2: Dict[str, Any],
        content_type: str
    ) -> float:
        """Calculate similarity between two fingerprints"""        try:
            if content_type.startswith('audio'):
                return self._calculate_audio_similarity(fingerprint1, fingerprint2)
            elif content_type.startswith('image'):
                return self._calculate_image_similarity(fingerprint1, fingerprint2)
            elif content_type.startswith('video'):
                return self._calculate_video_similarity(fingerprint1, fingerprint2)
            elif content_type.startswith('text'):
                return self._calculate_text_similarity(fingerprint1, fingerprint2)
            else:
                return self._calculate_hash_similarity(fingerprint1, fingerprint2)
                
        except Exception as e:
            logger.warning(f"Error calculating similarity: {str(e)}")
            return 0.0

    def _calculate_audio_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between audio fingerprints"""        try:
            # Compare MFCC features
            mfcc1 = np.array(fp1.get('mfcc_mean', []))
            mfcc2 = np.array(fp2.get('mfcc_mean', []))
            
            if len(mfcc1) == 0 or len(mfcc2) == 0:
                return 0.0
            
            mfcc_similarity = cosine_similarity([mfcc1], [mfcc2])[0][0]
            
            # Compare chroma features
            chroma1 = np.array(fp1.get('chroma_mean', []))
            chroma2 = np.array(fp2.get('chroma_mean', []))
            
            chroma_similarity = 0.0
            if len(chroma1) > 0 and len(chroma2) > 0:
                chroma_similarity = cosine_similarity([chroma1], [chroma2])[0][0]
            
            # Compare tempo
            tempo1 = fp1.get('tempo', 0)
            tempo2 = fp2.get('tempo', 0)
            tempo_similarity = 1.0 - abs(tempo1 - tempo2) / max(tempo1, tempo2, 1)
            
            # Weighted average
            return (0.5 * mfcc_similarity + 0.3 * chroma_similarity + 0.2 * tempo_similarity)
            
        except Exception:
            return 0.0

    def _calculate_image_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between image fingerprints"""        try:
            # Compare perceptual hashes
            hash1 = fp1.get('perceptual_hash', '')
            hash2 = fp2.get('perceptual_hash', '')
            
            if not hash1 or not hash2:
                return 0.0
            
            # Calculate Hamming distance
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            hash_similarity = 1.0 - (hamming_distance / len(hash1))
            
            # Compare color histograms
            hist1 = np.array(fp1.get('color_histogram', []))
            hist2 = np.array(fp2.get('color_histogram', []))
            
            hist_similarity = 0.0
            if len(hist1) > 0 and len(hist2) > 0:
                hist_similarity = cosine_similarity([hist1], [hist2])[0][0]
            
            # Weighted average
            return (0.7 * hash_similarity + 0.3 * hist_similarity)
            
        except Exception:
            return 0.0

    def _calculate_video_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between video fingerprints"""        try:
            # Compare frame hashes
            frames1 = fp1.get('frame_hashes', [])
            frames2 = fp2.get('frame_hashes', [])
            
            if not frames1 or not frames2:
                return 0.0
            
            # Compare frame by frame
            min_frames = min(len(frames1), len(frames2))
            frame_similarities = []
            
            for i in range(min_frames):
                hash1, hash2 = frames1[i], frames2[i]
                hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                similarity = 1.0 - (hamming_distance / len(hash1))
                frame_similarities.append(similarity)
            
            frame_similarity = np.mean(frame_similarities)
            
            # Compare audio if available
            audio_similarity = 0.0
            audio1 = fp1.get('audio_fingerprint', {})
            audio2 = fp2.get('audio_fingerprint', {})
            
            if audio1 and audio2:
                audio_similarity = self._calculate_audio_similarity(audio1, audio2)
            
            # Weighted average
            if audio_similarity > 0:
                return (0.6 * frame_similarity + 0.4 * audio_similarity)
            else:
                return frame_similarity
                
        except Exception:
            return 0.0

    def _calculate_text_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between text fingerprints"""        try:
            # Compare TF-IDF features
            features1 = fp1.get('top_tfidf_features', {})
            features2 = fp2.get('top_tfidf_features', {})
            
            if not features1 or not features2:
                return 0.0
            
            # Find common features
            common_features = set(features1.keys()) & set(features2.keys())
            
            if not common_features:
                return 0.0
            
            # Calculate cosine similarity of common features
            vec1 = np.array([features1[f] for f in common_features])
            vec2 = np.array([features2[f] for f in common_features])
            
            similarity = cosine_similarity([vec1], [vec2])[0][0]
            
            # Adjust for feature overlap
            overlap_ratio = len(common_features) / max(len(features1), len(features2))
            
            return similarity * overlap_ratio
            
        except Exception:
            return 0.0

    def _calculate_hash_similarity(self, fp1: Dict, fp2: Dict) -> float:
        """Calculate similarity between hash fingerprints"""        try:
            hash1 = fp1.get('sha256_hash', '')
            hash2 = fp2.get('sha256_hash', '')
            
            if not hash1 or not hash2:
                return 0.0
            
            return 1.0 if hash1 == hash2 else 0.0
            
        except Exception:
            return 0.0

    async def cleanup_old_fingerprints(self, days_old: int = 365) -> int:
        """Clean up old fingerprint records"""        try:
            query = """            DELETE FROM content_fingerprints
            WHERE created_at < NOW() - INTERVAL '%s days'
            """            
            result = await self.db.execute(query, days_old)
            deleted_count = result.split()[-1] if result else 0
            
            logger.info(f"Cleaned up {deleted_count} old fingerprint records")
            return int(deleted_count)
            
        except Exception as e:
            logger.error(f"Error cleaning up fingerprints: {str(e)}")
            raise ProcessingError(f"Fingerprint cleanup failed: {str(e)}")
