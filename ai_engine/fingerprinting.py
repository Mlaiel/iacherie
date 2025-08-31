"""Advanced AI Fingerprinting Engine
Multi-modal content fingerprinting with high-precision similarity matching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import hashlib
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import cv2
from PIL import Image
import io

# Audio fingerprinting
import librosa
from chromaprint import chromaprint

# Video fingerprinting  
import imagehash

# Text fingerprinting
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch

# Image fingerprinting
from torchvision import transforms, models
import clip

from ..config import settings
from ..core.logging import logger


class AudioFingerprinter:
    """Advanced audio fingerprinting using multiple algorithms"""    
    def __init__(self):
        self.sample_rate = 22050
        self.duration_limit = 300  # 5 minutes for fingerprinting
    
    async def generate_fingerprint(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Generate comprehensive audio fingerprint"""        try:
            fingerprint_data = {}
            
            # Chromaprint fingerprint (industry standard)
            chromaprint_fp = await self._generate_chromaprint(audio_data)
            fingerprint_data["chromaprint"] = chromaprint_fp
            
            # Spectral fingerprint
            spectral_fp = await self._generate_spectral_fingerprint(audio_data)
            fingerprint_data["spectral"] = spectral_fp
            
            # MFCC-based fingerprint
            mfcc_fp = await self._generate_mfcc_fingerprint(audio_data)
            fingerprint_data["mfcc"] = mfcc_fp
            
            # Chroma fingerprint
            chroma_fp = await self._generate_chroma_fingerprint(audio_data)
            fingerprint_data["chroma"] = chroma_fp
            
            # Combined hash
            combined_hash = await self._generate_combined_hash(fingerprint_data)
            fingerprint_data["combined_hash"] = combined_hash
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Audio fingerprinting failed: {str(e)}")
            raise
    
    async def _generate_chromaprint(self, audio_data: np.ndarray) -> str:
        """Generate Chromaprint fingerprint"""        # Convert to format expected by chromaprint
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Generate fingerprint
        fingerprint = chromaprint.encode_fingerprint(
            chromaprint.hash_fingerprint(audio_int16, self.sample_rate)
        )
        
        return fingerprint
    
    async def _generate_spectral_fingerprint(self, audio_data: np.ndarray) -> List[float]:
        """Generate spectral-based fingerprint"""        # Compute spectrogram
        stft = librosa.stft(audio_data, n_fft=2048, hop_length=512)
        magnitude = np.abs(stft)
        
        # Extract spectral features
        spectral_centroids = librosa.feature.spectral_centroid(S=magnitude, sr=self.sample_rate)
        spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude, sr=self.sample_rate)
        spectral_flux = np.diff(magnitude, axis=1)
        
        # Combine features into fingerprint
        fingerprint = np.concatenate([
            np.mean(spectral_centroids, axis=1),
            np.mean(spectral_rolloff, axis=1),
            np.mean(spectral_flux, axis=1)[:50]  # Limit size
        ])
        
        return fingerprint.tolist()
    
    async def _generate_mfcc_fingerprint(self, audio_data: np.ndarray) -> List[List[float]]:
        """Generate MFCC-based fingerprint"""        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
        
        # Statistical summary
        mfcc_mean = np.mean(mfccs, axis=1)
        mfcc_std = np.std(mfccs, axis=1)
        mfcc_delta = np.mean(librosa.feature.delta(mfccs), axis=1)
        
        return [mfcc_mean.tolist(), mfcc_std.tolist(), mfcc_delta.tolist()]
    
    async def _generate_chroma_fingerprint(self, audio_data: np.ndarray) -> List[float]:
        """Generate chroma-based fingerprint"""        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
        
        # Compress to fingerprint
        chroma_mean = np.mean(chroma, axis=1)
        chroma_std = np.std(chroma, axis=1)
        
        return np.concatenate([chroma_mean, chroma_std]).tolist()
    
    async def _generate_combined_hash(self, fingerprint_data: Dict) -> str:
        """Generate combined hash from all fingerprints"""        # Combine all fingerprint data
        combined_str = ""
        for key, value in fingerprint_data.items():
            if key != "combined_hash":
                combined_str += str(value)
        
        return hashlib.sha256(combined_str.encode()).hexdigest()


class VideoFingerprinter:
    """Advanced video fingerprinting using frame analysis"""    
    def __init__(self):
        self.frame_sample_rate = 1  # 1 frame per second
        self.max_frames = 100  # Limit number of frames
    
    async def generate_fingerprint(self, video_frames: List[np.ndarray], 
                                 fps: float) -> Dict[str, Any]:
        """Generate comprehensive video fingerprint"""        try:
            fingerprint_data = {}
            
            # Sample frames
            sampled_frames = await self._sample_frames(video_frames, fps)
            
            # Perceptual hash fingerprint
            phash_fp = await self._generate_phash_fingerprint(sampled_frames)
            fingerprint_data["phash"] = phash_fp
            
            # Histogram fingerprint
            hist_fp = await self._generate_histogram_fingerprint(sampled_frames)
            fingerprint_data["histogram"] = hist_fp
            
            # Edge fingerprint
            edge_fp = await self._generate_edge_fingerprint(sampled_frames)
            fingerprint_data["edge"] = edge_fp
            
            # Temporal fingerprint
            temporal_fp = await self._generate_temporal_fingerprint(sampled_frames)
            fingerprint_data["temporal"] = temporal_fp
            
            # Combined hash
            combined_hash = await self._generate_combined_hash(fingerprint_data)
            fingerprint_data["combined_hash"] = combined_hash
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Video fingerprinting failed: {str(e)}")
            raise
    
    async def _sample_frames(self, frames: List[np.ndarray], fps: float) -> List[np.ndarray]:
        """Sample frames at regular intervals"""        if not frames:
            return []
        
        # Calculate sampling interval
        total_frames = len(frames)
        sample_interval = max(1, int(fps / self.frame_sample_rate))
        
        # Sample frames
        sampled = frames[::sample_interval][:self.max_frames]
        return sampled
    
    async def _generate_phash_fingerprint(self, frames: List[np.ndarray]) -> List[str]:
        """Generate perceptual hash for each frame"""        hashes = []
        for frame in frames:
            # Convert to PIL Image
            if frame.shape[2] == 3:  # RGB
                image = Image.fromarray(frame)
            else:  # BGR
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Generate perceptual hash
            phash = str(imagehash.phash(image))
            hashes.append(phash)
        
        return hashes
    
    async def _generate_histogram_fingerprint(self, frames: List[np.ndarray]) -> List[List[float]]:
        """Generate color histogram fingerprint"""        histograms = []
        
        for frame in frames:
            # Convert to RGB if needed
            if frame.shape[2] == 3:
                rgb_frame = frame
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calculate histograms for each channel
            hist_r = cv2.calcHist([rgb_frame], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([rgb_frame], [1], None, [32], [0, 256])
            hist_b = cv2.calcHist([rgb_frame], [2], None, [32], [0, 256])
            
            # Normalize and combine
            combined_hist = np.concatenate([
                hist_r.flatten(), hist_g.flatten(), hist_b.flatten()
            ])
            combined_hist = combined_hist / np.sum(combined_hist)
            
            histograms.append(combined_hist.tolist())
        
        return histograms
    
    async def _generate_edge_fingerprint(self, frames: List[np.ndarray]) -> List[float]:
        """Generate edge-based fingerprint"""        edge_features = []
        
        for frame in frames:
            # Convert to grayscale
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            else:
                gray = frame
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Edge statistics
            edge_density = np.sum(edges > 0) / edges.size
            edge_features.append(edge_density)
        
        return edge_features
    
    async def _generate_temporal_fingerprint(self, frames: List[np.ndarray]) -> List[float]:
        """Generate temporal motion fingerprint"""        if len(frames) < 2:
            return []
        
        motion_features = []
        
        for i in range(1, len(frames)):
            prev_frame = frames[i-1]
            curr_frame = frames[i]
            
            # Convert to grayscale
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY) if len(prev_frame.shape) == 3 else prev_frame
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY) if len(curr_frame.shape) == 3 else curr_frame
            
            # Calculate optical flow
            flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
            
            # Motion magnitude
            if flow[1] is not None:
                motion_mag = np.mean(np.sqrt(flow[1][:, 0]**2 + flow[1][:, 1]**2))
                motion_features.append(float(motion_mag))
            else:
                motion_features.append(0.0)
        
        return motion_features
    
    async def _generate_combined_hash(self, fingerprint_data: Dict) -> str:
        """Generate combined hash from all fingerprints"""        combined_str = ""
        for key, value in fingerprint_data.items():
            if key != "combined_hash":
                combined_str += str(value)
        
        return hashlib.sha256(combined_str.encode()).hexdigest()


class ImageFingerprinter:
    """Advanced image fingerprinting using multiple algorithms"""    
    def __init__(self):
        # Load CLIP model for semantic fingerprinting
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
        except:
            self.clip_model = None
            logger.warning("CLIP model not available, semantic fingerprinting disabled")
    
    async def generate_fingerprint(self, image: Image.Image) -> Dict[str, Any]:
        """Generate comprehensive image fingerprint"""        try:
            fingerprint_data = {}
            
            # Perceptual hashes
            phash_fp = await self._generate_perceptual_hashes(image)
            fingerprint_data["perceptual_hashes"] = phash_fp
            
            # Color histogram fingerprint
            hist_fp = await self._generate_color_histogram(image)
            fingerprint_data["color_histogram"] = hist_fp
            
            # Texture fingerprint
            texture_fp = await self._generate_texture_fingerprint(image)
            fingerprint_data["texture"] = texture_fp
            
            # Semantic fingerprint (if CLIP available)
            if self.clip_model:
                semantic_fp = await self._generate_semantic_fingerprint(image)
                fingerprint_data["semantic"] = semantic_fp
            
            # Combined hash
            combined_hash = await self._generate_combined_hash(fingerprint_data)
            fingerprint_data["combined_hash"] = combined_hash
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Image fingerprinting failed: {str(e)}")
            raise
    
    async def _generate_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Generate multiple perceptual hashes"""        return {
            "phash": str(imagehash.phash(image)),
            "dhash": str(imagehash.dhash(image)),
            "whash": str(imagehash.whash(image)),
            "average_hash": str(imagehash.average_hash(image))
        }
    
    async def _generate_color_histogram(self, image: Image.Image) -> List[float]:
        """Generate color histogram fingerprint"""        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Calculate histograms
        hist_r = np.histogram(img_array[:,:,0], bins=32, range=(0, 255))[0]
        hist_g = np.histogram(img_array[:,:,1], bins=32, range=(0, 255))[0]
        hist_b = np.histogram(img_array[:,:,2], bins=32, range=(0, 255))[0]
        
        # Normalize and combine
        combined_hist = np.concatenate([hist_r, hist_g, hist_b])
        combined_hist = combined_hist / np.sum(combined_hist)
        
        return combined_hist.tolist()
    
    async def _generate_texture_fingerprint(self, image: Image.Image) -> Dict[str, float]:
        """Generate texture-based fingerprint"""        # Convert to grayscale
        gray_image = image.convert('L')
        img_array = np.array(gray_image)
        
        # Texture features
        features = {}
        
        # Local Binary Pattern (simplified)
        features["contrast"] = float(np.std(img_array))
        features["homogeneity"] = float(np.var(img_array))
        
        # Edge density
        edges = cv2.Canny(img_array, 50, 150)
        features["edge_density"] = float(np.sum(edges > 0) / edges.size)
        
        return features
    
    async def _generate_semantic_fingerprint(self, image: Image.Image) -> List[float]:
        """Generate semantic fingerprint using CLIP"""        if not self.clip_model:
            return []
        
        try:
            # Preprocess image
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten().tolist()
            
        except Exception as e:
            logger.error(f"Semantic fingerprinting failed: {str(e)}")
            return []
    
    async def _generate_combined_hash(self, fingerprint_data: Dict) -> str:
        """Generate combined hash from all fingerprints"""        combined_str = ""
        for key, value in fingerprint_data.items():
            if key != "combined_hash":
                combined_str += str(value)
        
        return hashlib.sha256(combined_str.encode()).hexdigest()


class TextFingerprinter:
    """Advanced text fingerprinting using NLP models"""    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load models
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            self.sentence_model = None
            logger.warning("Sentence transformer not available")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
            self.model = AutoModel.from_pretrained('bert-base-uncased')
        except:
            self.tokenizer = None
            self.model = None
            logger.warning("BERT model not available")
    
    async def generate_fingerprint(self, text: str) -> Dict[str, Any]:
        """Generate comprehensive text fingerprint"""        try:
            fingerprint_data = {}
            
            # Lexical fingerprint
            lexical_fp = await self._generate_lexical_fingerprint(text)
            fingerprint_data["lexical"] = lexical_fp
            
            # N-gram fingerprint
            ngram_fp = await self._generate_ngram_fingerprint(text)
            fingerprint_data["ngram"] = ngram_fp
            
            # Semantic fingerprint
            if self.sentence_model:
                semantic_fp = await self._generate_semantic_fingerprint(text)
                fingerprint_data["semantic"] = semantic_fp
            
            # Structural fingerprint
            structural_fp = await self._generate_structural_fingerprint(text)
            fingerprint_data["structural"] = structural_fp
            
            # Combined hash
            combined_hash = await self._generate_combined_hash(fingerprint_data)
            fingerprint_data["combined_hash"] = combined_hash
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Text fingerprinting failed: {str(e)}")
            raise
    
    async def _generate_lexical_fingerprint(self, text: str) -> Dict[str, Any]:
        """Generate lexical-based fingerprint"""        words = text.lower().split()
        
        # Word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Most common words (limit to top 50)
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
        
        # Character frequency
        char_freq = {}
        for char in text.lower():
            if char.isalpha():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        return {
            "word_frequency": dict(sorted_words),
            "character_frequency": char_freq,
            "vocabulary_size": len(word_freq),
            "total_words": len(words)
        }
    
    async def _generate_ngram_fingerprint(self, text: str) -> Dict[str, List[str]]:
        """Generate n-gram based fingerprint"""        words = text.lower().split()
        
        fingerprints = {}
        
        # Generate 2-grams and 3-grams
        for n in [2, 3]:
            ngrams = []
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngrams.append(ngram)
            
            # Get most frequent n-grams
            ngram_freq = {}
            for ngram in ngrams:
                ngram_freq[ngram] = ngram_freq.get(ngram, 0) + 1
            
            sorted_ngrams = sorted(ngram_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            fingerprints[f"{n}gram"] = [ngram for ngram, _ in sorted_ngrams]
        
        return fingerprints
    
    async def _generate_semantic_fingerprint(self, text: str) -> List[float]:
        """Generate semantic fingerprint using sentence transformers"""        if not self.sentence_model:
            return []
        
        try:
            # Split text into sentences for better processing
            sentences = text.split('. ')[:50]  # Limit to 50 sentences
            
            # Generate embeddings
            embeddings = self.sentence_model.encode(sentences)
            
            # Average embeddings
            avg_embedding = np.mean(embeddings, axis=0)
            
            return avg_embedding.tolist()
            
        except Exception as e:
            logger.error(f"Semantic fingerprinting failed: {str(e)}")
            return []
    
    async def _generate_structural_fingerprint(self, text: str) -> Dict[str, Any]:
        """Generate structural fingerprint"""        return {
            "sentence_count": text.count('.') + text.count('!') + text.count('?'),
            "paragraph_count": text.count('\n\n') + 1,
            "punctuation_density": sum(1 for c in text if c in '.,!?;:') / len(text),
            "avg_word_length": np.mean([len(word) for word in text.split()]),
            "capitalization_ratio": sum(1 for c in text if c.isupper()) / len(text)
        }
    
    async def _generate_combined_hash(self, fingerprint_data: Dict) -> str:
        """Generate combined hash from all fingerprints"""        combined_str = ""
        for key, value in fingerprint_data.items():
            if key != "combined_hash":
                combined_str += str(value)
        
        return hashlib.sha256(combined_str.encode()).hexdigest()


class FingerprintEngine:
    """Main fingerprinting engine orchestrator"""    
    def __init__(self):
        self.audio_fingerprinter = AudioFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
    
    async def generate_fingerprint(self, content_type: str, content_data: Any) -> Dict[str, Any]:
        """Generate fingerprint for any content type"""        try:
            logger.info(f"Generating fingerprint for {content_type} content")
            
            if content_type == "audio":
                return await self.audio_fingerprinter.generate_fingerprint(content_data)
            elif content_type == "video":
                # Expect (frames, fps) tuple for video
                frames, fps = content_data
                return await self.video_fingerprinter.generate_fingerprint(frames, fps)
            elif content_type == "image":
                return await self.image_fingerprinter.generate_fingerprint(content_data)
            elif content_type == "text":
                return await self.text_fingerprinter.generate_fingerprint(content_data)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Fingerprint generation failed for {content_type}: {str(e)}")
            raise
    
    async def compare_fingerprints(self, fp1: Dict[str, Any], fp2: Dict[str, Any], 
                                 content_type: str) -> float:
        """Compare two fingerprints and return similarity score"""        try:
            if content_type == "audio":
                return await self._compare_audio_fingerprints(fp1, fp2)
            elif content_type == "video":
                return await self._compare_video_fingerprints(fp1, fp2)
            elif content_type == "image":
                return await self._compare_image_fingerprints(fp1, fp2)
            elif content_type == "text":
                return await self._compare_text_fingerprints(fp1, fp2)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Fingerprint comparison failed: {str(e)}")
            return 0.0
    
    async def _compare_audio_fingerprints(self, fp1: Dict, fp2: Dict) -> float:
        """Compare audio fingerprints"""        scores = []
        
        # Compare MFCC features
        if "mfcc" in fp1 and "mfcc" in fp2:
            mfcc_score = self._cosine_similarity(fp1["mfcc"][0], fp2["mfcc"][0])
            scores.append(mfcc_score)
        
        # Compare spectral features
        if "spectral" in fp1 and "spectral" in fp2:
            spectral_score = self._cosine_similarity(fp1["spectral"], fp2["spectral"])
            scores.append(spectral_score)
        
        # Compare chroma features
        if "chroma" in fp1 and "chroma" in fp2:
            chroma_score = self._cosine_similarity(fp1["chroma"], fp2["chroma"])
            scores.append(chroma_score)
        
        return np.mean(scores) if scores else 0.0
    
    async def _compare_video_fingerprints(self, fp1: Dict, fp2: Dict) -> float:
        """Compare video fingerprints"""        scores = []
        
        # Compare perceptual hashes
        if "phash" in fp1 and "phash" in fp2:
            phash_score = self._compare_phash_sequences(fp1["phash"], fp2["phash"])
            scores.append(phash_score)
        
        # Compare histograms
        if "histogram" in fp1 and "histogram" in fp2:
            hist_score = self._compare_histogram_sequences(fp1["histogram"], fp2["histogram"])
            scores.append(hist_score)
        
        return np.mean(scores) if scores else 0.0
    
    async def _compare_image_fingerprints(self, fp1: Dict, fp2: Dict) -> float:
        """Compare image fingerprints"""        scores = []
        
        # Compare perceptual hashes
        if "perceptual_hashes" in fp1 and "perceptual_hashes" in fp2:
            phash_score = self._compare_image_hashes(fp1["perceptual_hashes"], fp2["perceptual_hashes"])
            scores.append(phash_score)
        
        # Compare semantic features
        if "semantic" in fp1 and "semantic" in fp2:
            semantic_score = self._cosine_similarity(fp1["semantic"], fp2["semantic"])
            scores.append(semantic_score)
        
        # Compare color histograms
        if "color_histogram" in fp1 and "color_histogram" in fp2:
            hist_score = self._cosine_similarity(fp1["color_histogram"], fp2["color_histogram"])
            scores.append(hist_score)
        
        return np.mean(scores) if scores else 0.0
    
    async def _compare_text_fingerprints(self, fp1: Dict, fp2: Dict) -> float:
        """Compare text fingerprints"""        scores = []
        
        # Compare semantic features
        if "semantic" in fp1 and "semantic" in fp2:
            semantic_score = self._cosine_similarity(fp1["semantic"], fp2["semantic"])
            scores.append(semantic_score)
        
        # Compare n-gram features
        if "ngram" in fp1 and "ngram" in fp2:
            ngram_score = self._compare_ngrams(fp1["ngram"], fp2["ngram"])
            scores.append(ngram_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""        if len(vec1) != len(vec2):
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _compare_phash_sequences(self, seq1: List[str], seq2: List[str]) -> float:
        """Compare sequences of perceptual hashes"""        if not seq1 or not seq2:
            return 0.0
        
        # Find best alignment and compare
        max_score = 0.0
        for i in range(max(1, len(seq1) - len(seq2) + 1)):
            score = 0.0
            count = 0
            for j in range(min(len(seq1) - i, len(seq2))):
                # Compare hashes (simplified)
                if seq1[i + j] == seq2[j]:
                    score += 1.0
                count += 1
            
            if count > 0:
                max_score = max(max_score, score / count)
        
        return max_score
    
    def _compare_histogram_sequences(self, seq1: List[List[float]], seq2: List[List[float]]) -> float:
        """Compare sequences of histograms"""        if not seq1 or not seq2:
            return 0.0
        
        scores = []
        min_len = min(len(seq1), len(seq2))
        
        for i in range(min_len):
            score = self._cosine_similarity(seq1[i], seq2[i])
            scores.append(score)
        
        return np.mean(scores) if scores else 0.0
    
    def _compare_image_hashes(self, hashes1: Dict[str, str], hashes2: Dict[str, str]) -> float:
        """Compare image hash dictionaries"""        scores = []
        
        for hash_type in hashes1:
            if hash_type in hashes2:
                # Simple string comparison for hashes
                similarity = 1.0 if hashes1[hash_type] == hashes2[hash_type] else 0.0
                scores.append(similarity)
        
        return np.mean(scores) if scores else 0.0
    
    def _compare_ngrams(self, ngrams1: Dict, ngrams2: Dict) -> float:
        """Compare n-gram dictionaries"""        scores = []
        
        for n in ngrams1:
            if n in ngrams2:
                set1 = set(ngrams1[n])
                set2 = set(ngrams2[n])
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                jaccard = intersection / union if union > 0 else 0.0
                scores.append(jaccard)
        
        return np.mean(scores) if scores else 0.0


# Global fingerprint engine instance
fingerprint_engine = FingerprintEngine()