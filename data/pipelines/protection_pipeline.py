"""
Protection Pipeline for AI-Powered Content Rights Management
===========================================================

Professional content protection system with AI fingerprinting, violation detection,
and automated takedown management for digital creators.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel - Advanced AI fingerprinting architecture
- ML Engineer: Deep learning models for content similarity detection
- Security Engineer: Advanced threat detection and content validation
- Backend Senior Engineer: High-performance violation processing
- Legal Tech Engineer: Automated DMCA and takedown procedures

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
This proprietary AI protection technology belongs exclusively to Fahed Mlaiel.
Unauthorized use, reverse engineering, or intellectual property theft will
result in immediate prosecution under international copyright and patent laws.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from uuid import uuid4
from enum import Enum

import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
import cv2
import librosa
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.config import get_settings
from backend.core.database import AsyncDatabaseSession
from backend.core.exceptions import (
    ProtectionError,
    FingerprintingError,
    ViolationDetectionError,
    TakedownError
)
from backend.data.fingerprinting import (
    AudioFingerprinter, 
    VideoFingerprinter,
    ImageFingerprinter, 
    TextFingerprinter
)
from backend.data.crawlers import PlatformCrawler
from backend.data.storage import StorageManager
from backend.models.protection import (
    FingerprintModel,
    ViolationAlert,
    TakedownRequest,
    ProtectionStatus
)
from backend.utils.logging import get_logger
from backend.utils.notifications import NotificationManager

logger = get_logger(__name__)
settings = get_settings()


class ViolationType(str, Enum):
    """Types of content violations"""
    EXACT_COPY = "exact_copy"
    PARTIAL_COPY = "partial_copy"
    REMIXED = "remixed"
    CROPPED = "cropped"
    FILTERED = "filtered"
    SPED_UP = "sped_up"
    SLOWED_DOWN = "slowed_down"
    REVERSED = "reversed"


class ProtectionLevel(str, Enum):
    """Protection sensitivity levels"""
    STRICT = "strict"      # 95%+ similarity threshold
    STANDARD = "standard"  # 85%+ similarity threshold
    RELAXED = "relaxed"    # 75%+ similarity threshold


class FingerprintingEngine:
    """
    Advanced AI-powered fingerprinting engine for multi-format content protection
    """
    
    def __init__(self):
        self.audio_fingerprinter = AudioFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        
        # Load CLIP model for cross-modal similarity
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Similarity thresholds by protection level
        self.similarity_thresholds = {
            ProtectionLevel.STRICT: 0.95,
            ProtectionLevel.STANDARD: 0.85,
            ProtectionLevel.RELAXED: 0.75
        }

    async def generate_fingerprint(
        self, 
        content_id: str, 
        content_type: str, 
        file_path: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI fingerprint for content protection
        """
        try:
            logger.info(f"Generating fingerprint for content {content_id}")
            
            fingerprint_data = {
                "content_id": content_id,
                "content_type": content_type,
                "timestamp": datetime.utcnow().isoformat(),
                "fingerprint_version": "2.0.0"
            }
            
            if content_type == "audio":
                fingerprint_data.update(
                    await self._generate_audio_fingerprint(file_path)
                )
            elif content_type == "video":
                fingerprint_data.update(
                    await self._generate_video_fingerprint(file_path)
                )
            elif content_type == "image":
                fingerprint_data.update(
                    await self._generate_image_fingerprint(file_path)
                )
            elif content_type == "text":
                fingerprint_data.update(
                    await self._generate_text_fingerprint(file_path)
                )
            else:
                raise FingerprintingError(f"Unsupported content type: {content_type}")
            
            # Generate cross-modal CLIP embedding for advanced similarity
            clip_embedding = await self._generate_clip_embedding(file_path, content_type)
            fingerprint_data["clip_embedding"] = clip_embedding.tolist()
            
            logger.info(f"Fingerprint generated successfully for {content_id}")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed for {content_id}: {str(e)}")
            raise FingerprintingError(f"Fingerprinting failed: {str(e)}")

    async def _generate_audio_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate audio-specific fingerprint"""
        try:
            # Load audio
            y, sr = librosa.load(file_path, sr=22050)
            
            # Generate multiple audio fingerprints
            fingerprints = {}
            
            # 1. Chromagram fingerprint
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            fingerprints["chroma"] = chroma.flatten().tolist()
            
            # 2. MFCC fingerprint
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            fingerprints["mfcc"] = mfcc.flatten().tolist()
            
            # 3. Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            fingerprints["spectral_centroid"] = spectral_centroids.flatten().tolist()
            
            # 4. Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            fingerprints["tempo"] = float(tempo)
            fingerprints["beat_frames"] = beats.tolist()
            
            # 5. Hash-based fingerprint for exact matching
            audio_hash = self.audio_fingerprinter.generate_hash(y, sr)
            fingerprints["audio_hash"] = audio_hash
            
            return {"audio_fingerprint": fingerprints}
            
        except Exception as e:
            raise FingerprintingError(f"Audio fingerprinting failed: {str(e)}")

    async def _generate_video_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate video-specific fingerprint"""
        try:
            cap = cv2.VideoCapture(file_path)
            fingerprints = {}
            
            # Extract key frames
            frames = []
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames uniformly
            frame_interval = max(1, total_frames // 20)  # Max 20 frames
            
            while cap.isOpened() and len(frames) < 20:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frames.append(frame)
                
                frame_count += 1
            
            cap.release()
            
            if not frames:
                raise FingerprintingError("No frames extracted from video")
            
            # 1. Perceptual hash for each frame
            frame_hashes = []
            for frame in frames:
                # Convert to grayscale and resize
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (8, 8))
                
                # Calculate DCT and hash
                dct = cv2.dct(np.float32(resized))
                hash_value = "".join([
                    "1" if dct[i, j] > np.median(dct) else "0"
                    for i in range(8) for j in range(8)
                ])
                frame_hashes.append(hash_value)
            
            fingerprints["frame_hashes"] = frame_hashes
            
            # 2. Color histogram for each frame
            color_histograms = []
            for frame in frames:
                # Calculate color histogram
                hist_b = cv2.calcHist([frame], [0], None, [32], [0, 256])
                hist_g = cv2.calcHist([frame], [1], None, [32], [0, 256])
                hist_r = cv2.calcHist([frame], [2], None, [32], [0, 256])
                
                combined_hist = np.concatenate([hist_b, hist_g, hist_r]).flatten()
                color_histograms.append(combined_hist.tolist())
            
            fingerprints["color_histograms"] = color_histograms
            
            # 3. Motion vectors (optical flow)
            if len(frames) >= 2:
                motion_vectors = []
                for i in range(len(frames) - 1):
                    gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                    gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                    
                    # Calculate optical flow
                    flow = cv2.calcOpticalFlowPyrLK(
                        gray1, gray2, 
                        np.array([[100, 100]], dtype=np.float32), 
                        None
                    )[0]
                    
                    if flow is not None:
                        motion_vectors.append(flow.flatten().tolist())
                
                fingerprints["motion_vectors"] = motion_vectors
            
            return {"video_fingerprint": fingerprints}
            
        except Exception as e:
            raise FingerprintingError(f"Video fingerprinting failed: {str(e)}")

    async def _generate_image_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate image-specific fingerprint"""
        try:
            import cv2
            from PIL import Image
            import imagehash
            
            # Load image
            image = cv2.imread(file_path)
            pil_image = Image.open(file_path)
            
            fingerprints = {}
            
            # 1. Perceptual hashes
            fingerprints["average_hash"] = str(imagehash.average_hash(pil_image))
            fingerprints["phash"] = str(imagehash.phash(pil_image))
            fingerprints["dhash"] = str(imagehash.dhash(pil_image))
            fingerprints["whash"] = str(imagehash.whash(pil_image))
            
            # 2. Color histogram
            hist_b = cv2.calcHist([image], [0], None, [64], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [64], [0, 256])
            hist_r = cv2.calcHist([image], [2], None, [64], [0, 256])
            color_hist = np.concatenate([hist_b, hist_g, hist_r]).flatten()
            fingerprints["color_histogram"] = color_hist.tolist()
            
            # 3. SIFT features
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            if descriptors is not None and len(descriptors) > 0:
                # Use first 50 descriptors or all if less than 50
                desc_subset = descriptors[:50] if len(descriptors) > 50 else descriptors
                fingerprints["sift_descriptors"] = desc_subset.flatten().tolist()
            else:
                fingerprints["sift_descriptors"] = []
            
            # 4. Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_histogram = cv2.calcHist([edges], [0], None, [32], [0, 256])
            fingerprints["edge_histogram"] = edge_histogram.flatten().tolist()
            
            return {"image_fingerprint": fingerprints}
            
        except Exception as e:
            raise FingerprintingError(f"Image fingerprinting failed: {str(e)}")

    async def _generate_text_fingerprint(self, file_path: str) -> Dict[str, Any]:
        """Generate text-specific fingerprint"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            fingerprints = {}
            
            # 1. N-gram hashes
            from collections import Counter
            import hashlib
            
            # Character n-grams
            char_ngrams = [text[i:i+5] for i in range(len(text)-4)]
            char_ngram_hash = hashlib.md5(
                "".join(sorted(set(char_ngrams))).encode()
            ).hexdigest()
            fingerprints["char_ngram_hash"] = char_ngram_hash
            
            # Word n-grams
            words = text.lower().split()
            word_bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            word_bigram_hash = hashlib.md5(
                "".join(sorted(set(word_bigrams))).encode()
            ).hexdigest()
            fingerprints["word_bigram_hash"] = word_bigram_hash
            
            # 2. Semantic embedding using BERT
            embeddings = await self.text_fingerprinter.generate_embeddings(text)
            fingerprints["semantic_embedding"] = embeddings.tolist()
            
            # 3. Statistical features
            fingerprints["text_stats"] = {
                "char_count": len(text),
                "word_count": len(words),
                "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
                "vocab_size": len(set(words)),
                "sentence_count": text.count('.') + text.count('!') + text.count('?')
            }
            
            return {"text_fingerprint": fingerprints}
            
        except Exception as e:
            raise FingerprintingError(f"Text fingerprinting failed: {str(e)}")

    async def _generate_clip_embedding(
        self, 
        file_path: str, 
        content_type: str
    ) -> np.ndarray:
        """Generate CLIP embedding for cross-modal similarity"""
        try:
            if content_type == "image":
                from PIL import Image
                image = Image.open(file_path)
                inputs = self.clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)
                return image_features.numpy().flatten()
            
            elif content_type in ["audio", "video", "text"]:
                # For non-image content, generate a text description
                # This would ideally use the content metadata or AI-generated description
                description = f"This is a {content_type} content file"
                inputs = self.clip_processor(text=[description], return_tensors="pt")
                with torch.no_grad():
                    text_features = self.clip_model.get_text_features(**inputs)
                return text_features.numpy().flatten()
            
            else:
                # Fallback: zero embedding
                return np.zeros(512)
                
        except Exception as e:
            logger.warning(f"CLIP embedding generation failed: {str(e)}")
            return np.zeros(512)

    async def compare_fingerprints(
        self,
        fingerprint1: Dict[str, Any],
        fingerprint2: Dict[str, Any],
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    ) -> Tuple[float, ViolationType]:
        """
        Compare two fingerprints and return similarity score and violation type
        """
        try:
            content_type = fingerprint1.get("content_type")
            threshold = self.similarity_thresholds[protection_level]
            
            if content_type == "audio":
                similarity = await self._compare_audio_fingerprints(
                    fingerprint1["audio_fingerprint"],
                    fingerprint2["audio_fingerprint"]
                )
            elif content_type == "video":
                similarity = await self._compare_video_fingerprints(
                    fingerprint1["video_fingerprint"],
                    fingerprint2["video_fingerprint"]
                )
            elif content_type == "image":
                similarity = await self._compare_image_fingerprints(
                    fingerprint1["image_fingerprint"],
                    fingerprint2["image_fingerprint"]
                )
            elif content_type == "text":
                similarity = await self._compare_text_fingerprints(
                    fingerprint1["text_fingerprint"],
                    fingerprint2["text_fingerprint"]
                )
            else:
                raise ViolationDetectionError(f"Unsupported content type: {content_type}")
            
            # Determine violation type based on similarity score
            violation_type = self._determine_violation_type(similarity, content_type)
            
            return similarity, violation_type
            
        except Exception as e:
            logger.error(f"Fingerprint comparison failed: {str(e)}")
            raise ViolationDetectionError(f"Comparison failed: {str(e)}")

    async def _compare_audio_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare audio fingerprints"""
        similarities = []
        
        # Compare MFCC features
        if "mfcc" in fp1 and "mfcc" in fp2:
            mfcc_sim = cosine_similarity(
                [fp1["mfcc"]], [fp2["mfcc"]]
            )[0][0]
            similarities.append(mfcc_sim * 0.4)  # 40% weight
        
        # Compare chroma features
        if "chroma" in fp1 and "chroma" in fp2:
            chroma_sim = cosine_similarity(
                [fp1["chroma"]], [fp2["chroma"]]
            )[0][0]
            similarities.append(chroma_sim * 0.3)  # 30% weight
        
        # Compare tempo
        if "tempo" in fp1 and "tempo" in fp2:
            tempo_diff = abs(fp1["tempo"] - fp2["tempo"])
            tempo_sim = max(0, 1 - (tempo_diff / 100))  # Normalize by 100 BPM
            similarities.append(tempo_sim * 0.2)  # 20% weight
        
        # Compare hash for exact matching
        if "audio_hash" in fp1 and "audio_hash" in fp2:
            hash_sim = 1.0 if fp1["audio_hash"] == fp2["audio_hash"] else 0.0
            similarities.append(hash_sim * 0.1)  # 10% weight
        
        return sum(similarities) if similarities else 0.0

    async def _compare_video_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare video fingerprints"""
        similarities = []
        
        # Compare frame hashes
        if "frame_hashes" in fp1 and "frame_hashes" in fp2:
            hashes1 = fp1["frame_hashes"]
            hashes2 = fp2["frame_hashes"]
            
            # Calculate Hamming distance for each hash pair
            hash_similarities = []
            for h1, h2 in zip(hashes1, hashes2):
                if len(h1) == len(h2):
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(h1, h2))
                    similarity = 1.0 - (hamming_dist / len(h1))
                    hash_similarities.append(similarity)
            
            if hash_similarities:
                avg_hash_sim = sum(hash_similarities) / len(hash_similarities)
                similarities.append(avg_hash_sim * 0.5)  # 50% weight
        
        # Compare color histograms
        if "color_histograms" in fp1 and "color_histograms" in fp2:
            hists1 = fp1["color_histograms"]
            hists2 = fp2["color_histograms"]
            
            hist_similarities = []
            for hist1, hist2 in zip(hists1, hists2):
                hist_sim = cosine_similarity([hist1], [hist2])[0][0]
                hist_similarities.append(hist_sim)
            
            if hist_similarities:
                avg_hist_sim = sum(hist_similarities) / len(hist_similarities)
                similarities.append(avg_hist_sim * 0.3)  # 30% weight
        
        # Compare motion vectors
        if "motion_vectors" in fp1 and "motion_vectors" in fp2:
            vectors1 = fp1["motion_vectors"]
            vectors2 = fp2["motion_vectors"]
            
            if vectors1 and vectors2:
                motion_similarities = []
                for vec1, vec2 in zip(vectors1, vectors2):
                    if len(vec1) == len(vec2):
                        motion_sim = cosine_similarity([vec1], [vec2])[0][0]
                        motion_similarities.append(motion_sim)
                
                if motion_similarities:
                    avg_motion_sim = sum(motion_similarities) / len(motion_similarities)
                    similarities.append(avg_motion_sim * 0.2)  # 20% weight
        
        return sum(similarities) if similarities else 0.0

    async def _compare_image_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare image fingerprints"""
        similarities = []
        
        # Compare perceptual hashes
        hash_types = ["average_hash", "phash", "dhash", "whash"]
        for hash_type in hash_types:
            if hash_type in fp1 and hash_type in fp2:
                # Calculate Hamming distance
                hash1 = fp1[hash_type]
                hash2 = fp2[hash_type]
                
                if len(hash1) == len(hash2):
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                    similarity = 1.0 - (hamming_dist / len(hash1))
                    similarities.append(similarity * 0.15)  # 15% weight each
        
        # Compare color histogram
        if "color_histogram" in fp1 and "color_histogram" in fp2:
            color_sim = cosine_similarity(
                [fp1["color_histogram"]], [fp2["color_histogram"]]
            )[0][0]
            similarities.append(color_sim * 0.25)  # 25% weight
        
        # Compare SIFT descriptors
        if "sift_descriptors" in fp1 and "sift_descriptors" in fp2:
            if fp1["sift_descriptors"] and fp2["sift_descriptors"]:
                sift_sim = cosine_similarity(
                    [fp1["sift_descriptors"]], [fp2["sift_descriptors"]]
                )[0][0]
                similarities.append(sift_sim * 0.15)  # 15% weight
        
        return sum(similarities) if similarities else 0.0

    async def _compare_text_fingerprints(
        self, 
        fp1: Dict[str, Any], 
        fp2: Dict[str, Any]
    ) -> float:
        """Compare text fingerprints"""
        similarities = []
        
        # Compare n-gram hashes
        if "char_ngram_hash" in fp1 and "char_ngram_hash" in fp2:
            char_sim = 1.0 if fp1["char_ngram_hash"] == fp2["char_ngram_hash"] else 0.0
            similarities.append(char_sim * 0.2)  # 20% weight
        
        if "word_bigram_hash" in fp1 and "word_bigram_hash" in fp2:
            word_sim = 1.0 if fp1["word_bigram_hash"] == fp2["word_bigram_hash"] else 0.0
            similarities.append(word_sim * 0.2)  # 20% weight
        
        # Compare semantic embeddings
        if "semantic_embedding" in fp1 and "semantic_embedding" in fp2:
            semantic_sim = cosine_similarity(
                [fp1["semantic_embedding"]], [fp2["semantic_embedding"]]
            )[0][0]
            similarities.append(semantic_sim * 0.5)  # 50% weight
        
        # Compare statistical features
        if "text_stats" in fp1 and "text_stats" in fp2:
            stats1 = fp1["text_stats"]
            stats2 = fp2["text_stats"]
            
            # Calculate statistical similarity
            stat_sims = []
            for key in ["char_count", "word_count", "avg_word_length", "vocab_size"]:
                if key in stats1 and key in stats2:
                    val1, val2 = stats1[key], stats2[key]
                    if val1 > 0 and val2 > 0:
                        ratio = min(val1, val2) / max(val1, val2)
                        stat_sims.append(ratio)
            
            if stat_sims:
                avg_stat_sim = sum(stat_sims) / len(stat_sims)
                similarities.append(avg_stat_sim * 0.1)  # 10% weight
        
        return sum(similarities) if similarities else 0.0

    def _determine_violation_type(
        self, 
        similarity: float, 
        content_type: str
    ) -> ViolationType:
        """Determine violation type based on similarity score"""
        if similarity >= 0.98:
            return ViolationType.EXACT_COPY
        elif similarity >= 0.90:
            return ViolationType.PARTIAL_COPY
        elif similarity >= 0.80:
            if content_type == "audio":
                return ViolationType.SPED_UP  # Could be speed/pitch change
            elif content_type == "image":
                return ViolationType.CROPPED  # Could be cropped/resized
            elif content_type == "video":
                return ViolationType.FILTERED  # Could be filtered/edited
            else:
                return ViolationType.REMIXED
        else:
            return ViolationType.REMIXED


class ProtectionPipeline:
    """
    Comprehensive content protection pipeline orchestrating fingerprinting,
    monitoring, violation detection, and automated takedown processes
    """
    
    def __init__(self):
        self.fingerprinting_engine = FingerprintingEngine()
        self.platform_crawler = PlatformCrawler()
        self.storage_manager = StorageManager()
        self.notification_manager = NotificationManager()

    async def protect_content(
        self,
        content_id: str,
        user_id: int,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Initiate comprehensive protection for uploaded content
        """
        try:
            logger.info(f"Starting content protection for {content_id}")
            
            # Step 1: Generate fingerprint
            fingerprint_data = await self._generate_content_fingerprint(content_id)
            
            # Step 2: Save fingerprint to database
            fingerprint_model = await self._save_fingerprint(
                content_id, user_id, fingerprint_data, protection_level
            )
            
            # Step 3: Start monitoring
            monitoring_id = await self._initiate_monitoring(
                fingerprint_model.id, protection_level
            )
            
            # Step 4: Schedule periodic scans
            await self._schedule_protection_scans(fingerprint_model.id)
            
            return {
                "protection_id": fingerprint_model.id,
                "monitoring_id": monitoring_id,
                "protection_level": protection_level.value,
                "status": "active",
                "fingerprint_generated": True,
                "monitoring_started": True
            }
            
        except Exception as e:
            logger.error(f"Content protection failed for {content_id}: {str(e)}")
            raise ProtectionError(f"Protection failed: {str(e)}")

    async def scan_for_violations(
        self,
        fingerprint_id: str,
        platforms: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan platforms for content violations
        """
        try:
            # Get fingerprint data
            async with AsyncDatabaseSession() as session:
                fingerprint = await session.get(FingerprintModel, fingerprint_id)
                if not fingerprint:
                    raise ProtectionError("Fingerprint not found")
            
            # Default platforms if not specified
            if not platforms:
                platforms = ["youtube", "instagram", "tiktok", "twitter"]
            
            violations = []
            
            for platform in platforms:
                try:
                    platform_violations = await self._scan_platform_for_violations(
                        fingerprint, platform
                    )
                    violations.extend(platform_violations)
                    
                except Exception as e:
                    logger.error(f"Platform scan failed for {platform}: {str(e)}")
                    continue
            
            # Save detected violations
            for violation in violations:
                await self._save_violation_alert(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Violation scan failed: {str(e)}")
            raise ViolationDetectionError(f"Scan failed: {str(e)}")

    async def process_takedown_request(
        self,
        violation_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Process automated takedown request for detected violation
        """
        try:
            # Get violation details
            async with AsyncDatabaseSession() as session:
                violation = await session.get(ViolationAlert, violation_id)
                if not violation or violation.user_id != user_id:
                    raise TakedownError("Violation not found or unauthorized")
            
            # Generate takedown request
            takedown_data = await self._generate_takedown_request(violation)
            
            # Submit to platform
            submission_result = await self._submit_takedown_to_platform(
                violation.platform, takedown_data
            )
            
            # Save takedown request
            takedown_model = await self._save_takedown_request(
                violation_id, takedown_data, submission_result
            )
            
            # Update violation status
            violation.status = "takedown_submitted"
            violation.takedown_id = takedown_model.id
            
            # Send notification
            await self.notification_manager.send_takedown_notification(
                user_id, violation, takedown_model
            )
            
            return {
                "takedown_id": takedown_model.id,
                "status": "submitted",
                "platform": violation.platform,
                "submission_result": submission_result
            }
            
        except Exception as e:
            logger.error(f"Takedown processing failed: {str(e)}")
            raise TakedownError(f"Takedown failed: {str(e)}")

    async def get_protection_status(
        self,
        user_id: int,
        content_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive protection status for user's content
        """
        async with AsyncDatabaseSession() as session:
            query = session.query(FingerprintModel).filter(
                FingerprintModel.user_id == user_id
            )
            
            if content_id:
                query = query.filter(FingerprintModel.content_id == content_id)
            
            fingerprints = await query.all()
            
            status_data = {
                "total_protected_content": len(fingerprints),
                "active_monitoring": 0,
                "violations_detected": 0,
                "takedowns_submitted": 0,
                "content_status": []
            }
            
            for fingerprint in fingerprints:
                # Count violations
                violations = await session.query(ViolationAlert).filter(
                    ViolationAlert.fingerprint_id == fingerprint.id
                ).all()
                
                # Count takedowns
                takedowns = await session.query(TakedownRequest).filter(
                    TakedownRequest.fingerprint_id == fingerprint.id
                ).all()
                
                status_data["violations_detected"] += len(violations)
                status_data["takedowns_submitted"] += len(takedowns)
                
                if fingerprint.status == "active":
                    status_data["active_monitoring"] += 1
                
                content_status = {
                    "content_id": fingerprint.content_id,
                    "protection_level": fingerprint.protection_level,
                    "violations": len(violations),
                    "takedowns": len(takedowns),
                    "last_scan": fingerprint.last_scan_at.isoformat() if fingerprint.last_scan_at else None,
                    "status": fingerprint.status
                }
                
                status_data["content_status"].append(content_status)
            
            return status_data

    # Private helper methods for complete protection implementation
    async def _generate_content_fingerprint(self, content_id: str) -> Dict[str, Any]:
        """Generate comprehensive fingerprint for content"""
        try:
            # Retrieve content metadata and file path
            async with AsyncDatabaseSession() as session:
                from backend.models.content import ContentModel
                content = await session.get(ContentModel, content_id)
                if not content:
                    raise ProtectionError("Content not found")
                
                file_path = await self.storage_manager.get_content_path(content.storage_path)
                
                # Generate fingerprint using the fingerprinting engine
                fingerprint_data = await self.fingerprinting_engine.generate_fingerprint(
                    content_id, content.content_type, file_path
                )
                
                return fingerprint_data
                
        except Exception as e:
            raise ProtectionError(f"Fingerprint generation failed: {str(e)}")

    async def _save_fingerprint(
        self,
        content_id: str,
        user_id: int,
        fingerprint_data: Dict[str, Any],
        protection_level: ProtectionLevel
    ) -> FingerprintModel:
        """Save fingerprint to database with full metadata"""
        async with AsyncDatabaseSession() as session:
            fingerprint_model = FingerprintModel(
                id=str(uuid4()),
                content_id=content_id,
                user_id=user_id,
                fingerprint_data=fingerprint_data,
                protection_level=protection_level.value,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_scan_at=None,
                scan_frequency_hours=24,  # Default daily scans
                similarity_threshold=self.fingerprinting_engine.similarity_thresholds[protection_level]
            )
            
            session.add(fingerprint_model)
            await session.commit()
            await session.refresh(fingerprint_model)
            
            logger.info(f"Fingerprint saved: {fingerprint_model.id} for content {content_id}")
            return fingerprint_model

    async def _initiate_monitoring(
        self,
        fingerprint_id: str,
        protection_level: ProtectionLevel
    ) -> str:
        """Initiate comprehensive content monitoring across platforms"""
        try:
            monitoring_id = str(uuid4())
            
            # Schedule immediate scan
            from backend.tasks.protection import schedule_violation_scan
            await schedule_violation_scan.delay(
                fingerprint_id=fingerprint_id,
                platforms=["youtube", "instagram", "tiktok", "twitter", "facebook"],
                monitoring_id=monitoring_id
            )
            
            # Set up recurring monitoring based on protection level
            scan_frequency = {
                ProtectionLevel.STRICT: 6,    # Every 6 hours
                ProtectionLevel.STANDARD: 24, # Daily
                ProtectionLevel.RELAXED: 72   # Every 3 days
            }
            
            from backend.tasks.protection import setup_recurring_scan
            await setup_recurring_scan.delay(
                fingerprint_id=fingerprint_id,
                frequency_hours=scan_frequency[protection_level],
                monitoring_id=monitoring_id
            )
            
            logger.info(f"Monitoring initiated: {monitoring_id} for fingerprint {fingerprint_id}")
            return monitoring_id
            
        except Exception as e:
            raise ProtectionError(f"Monitoring initiation failed: {str(e)}")

    async def _schedule_protection_scans(self, fingerprint_id: str):
        """Schedule comprehensive protection scanning tasks"""
        try:
            # Schedule platform-specific scans
            platforms = {
                "youtube": {"priority": "high", "scan_depth": "deep"},
                "instagram": {"priority": "high", "scan_depth": "medium"},
                "tiktok": {"priority": "high", "scan_depth": "deep"},
                "twitter": {"priority": "medium", "scan_depth": "medium"},
                "facebook": {"priority": "medium", "scan_depth": "medium"},
                "soundcloud": {"priority": "low", "scan_depth": "shallow"},
                "vimeo": {"priority": "low", "scan_depth": "shallow"}
            }
            
            for platform, config in platforms.items():
                from backend.tasks.protection import schedule_platform_scan
                await schedule_platform_scan.delay(
                    fingerprint_id=fingerprint_id,
                    platform=platform,
                    scan_config=config
                )
            
            # Schedule DMCA monitoring
            from backend.tasks.protection import schedule_dmca_monitoring
            await schedule_dmca_monitoring.delay(fingerprint_id=fingerprint_id)
            
            logger.info(f"Protection scans scheduled for fingerprint {fingerprint_id}")
            
        except Exception as e:
            logger.error(f"Protection scan scheduling failed: {str(e)}")

    async def _scan_platform_for_violations(
        self,
        fingerprint: FingerprintModel,
        platform: str
    ) -> List[Dict[str, Any]]:
        """Scan specific platform for content violations using AI matching"""
        try:
            violations = []
            
            # Get platform-specific crawler
            crawler = await self.platform_crawler.get_platform_crawler(platform)
            
            # Search for potential matches based on content metadata
            async with AsyncDatabaseSession() as session:
                from backend.models.content import ContentModel
                content = await session.get(ContentModel, fingerprint.content_id)
                
                search_queries = await self._generate_search_queries(content, fingerprint)
                
                for query in search_queries:
                    try:
                        search_results = await crawler.search_content(
                            query=query,
                            content_type=content.content_type,
                            max_results=50
                        )
                        
                        for result in search_results:
                            # Download and analyze potential violation
                            violation_data = await self._analyze_potential_violation(
                                fingerprint, result, platform
                            )
                            
                            if violation_data and violation_data["similarity"] > fingerprint.similarity_threshold:
                                violations.append(violation_data)
                                
                    except Exception as e:
                        logger.warning(f"Search query failed for {query}: {str(e)}")
                        continue
            
            logger.info(f"Found {len(violations)} violations on {platform} for fingerprint {fingerprint.id}")
            return violations
            
        except Exception as e:
            logger.error(f"Platform scan failed for {platform}: {str(e)}")
            return []

    async def _generate_search_queries(
        self, 
        content: 'ContentModel', 
        fingerprint: FingerprintModel
    ) -> List[str]:
        """Generate intelligent search queries for content discovery"""
        queries = []
        
        # Basic metadata queries
        if content.filename:
            # Remove extension and clean filename
            clean_name = content.filename.split('.')[0].replace('_', ' ').replace('-', ' ')
            queries.append(clean_name)
        
        if content.description:
            # Extract keywords from description
            keywords = content.description.split()[:5]  # First 5 words
            queries.append(' '.join(keywords))
        
        if content.tags:
            # Use tags as search terms
            for tag in content.tags[:3]:  # First 3 tags
                queries.append(tag)
        
        # Content-type specific queries
        if content.content_type == "audio":
            queries.extend([
                f"{clean_name} music",
                f"{clean_name} song",
                f"{clean_name} audio"
            ])
        elif content.content_type == "video":
            queries.extend([
                f"{clean_name} video",
                f"{clean_name} clip",
                f"{clean_name} movie"
            ])
        elif content.content_type == "image":
            queries.extend([
                f"{clean_name} image",
                f"{clean_name} photo",
                f"{clean_name} picture"
            ])
        
        # AI-generated queries based on fingerprint data
        if hasattr(fingerprint, 'fingerprint_data') and fingerprint.fingerprint_data:
            ai_queries = await self._generate_ai_search_queries(fingerprint.fingerprint_data)
            queries.extend(ai_queries)
        
        return list(set(queries))  # Remove duplicates

    async def _generate_ai_search_queries(self, fingerprint_data: Dict[str, Any]) -> List[str]:
        """Generate AI-powered search queries based on content analysis"""
        queries = []
        
        try:
            # Use CLIP embeddings to generate descriptive queries
            if "clip_embedding" in fingerprint_data:
                # This would ideally use a reverse lookup or similarity search
                # to find descriptive terms for the content
                queries.append("similar content")
            
            # Content-specific query generation
            if "audio_fingerprint" in fingerprint_data:
                audio_fp = fingerprint_data["audio_fingerprint"]
                if "tempo" in audio_fp:
                    tempo = audio_fp["tempo"]
                    if tempo > 120:
                        queries.append("fast music")
                    elif tempo < 80:
                        queries.append("slow music")
            
            if "image_fingerprint" in fingerprint_data:
                # Generate queries based on image characteristics
                queries.extend(["high quality image", "professional photo"])
            
            if "video_fingerprint" in fingerprint_data:
                # Generate queries based on video characteristics
                queries.extend(["high quality video", "professional video"])
            
        except Exception as e:
            logger.warning(f"AI query generation failed: {str(e)}")
        
        return queries

    async def _analyze_potential_violation(
        self,
        fingerprint: FingerprintModel,
        search_result: Dict[str, Any],
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze potential violation using AI fingerprint comparison"""
        try:
            # Download content for analysis
            content_url = search_result.get("content_url")
            if not content_url:
                return None
            
            # Create temporary file for analysis
            temp_file = await self._download_content_for_analysis(content_url, platform)
            if not temp_file:
                return None
            
            try:
                # Generate fingerprint for potential violation
                violation_fingerprint = await self.fingerprinting_engine.generate_fingerprint(
                    search_result.get("id", "unknown"),
                    fingerprint.fingerprint_data.get("content_type"),
                    temp_file
                )
                
                # Compare fingerprints
                similarity, violation_type = await self.fingerprinting_engine.compare_fingerprints(
                    fingerprint.fingerprint_data,
                    violation_fingerprint,
                    ProtectionLevel(fingerprint.protection_level)
                )
                
                if similarity > fingerprint.similarity_threshold:
                    return {
                        "fingerprint_id": fingerprint.id,
                        "platform": platform,
                        "detected_url": search_result.get("url"),
                        "content_url": content_url,
                        "similarity": similarity,
                        "violation_type": violation_type.value,
                        "platform_content_id": search_result.get("id"),
                        "title": search_result.get("title"),
                        "description": search_result.get("description"),
                        "uploader": search_result.get("uploader"),
                        "upload_date": search_result.get("upload_date"),
                        "view_count": search_result.get("view_count"),
                        "detected_at": datetime.utcnow()
                    }
                
            finally:
                # Cleanup temporary file
                if temp_file and Path(temp_file).exists():
                    Path(temp_file).unlink()
            
            return None
            
        except Exception as e:
            logger.error(f"Violation analysis failed: {str(e)}")
            return None

    async def _download_content_for_analysis(
        self, 
        content_url: str, 
        platform: str
    ) -> Optional[str]:
        """Download content temporarily for fingerprint analysis"""
        try:
            import aiohttp
            import tempfile
            
            async with aiohttp.ClientSession() as session:
                async with session.get(content_url, timeout=30) as response:
                    if response.status == 200:
                        # Create temporary file
                        temp_file = tempfile.NamedTemporaryFile(delete=False)
                        
                        # Download content in chunks
                        async for chunk in response.content.iter_chunked(8192):
                            temp_file.write(chunk)
                        
                        temp_file.close()
                        return temp_file.name
                    
        except Exception as e:
            logger.warning(f"Content download failed for {content_url}: {str(e)}")
        
        return None

    async def _save_violation_alert(self, violation_data: Dict[str, Any]):
        """Save violation alert to database with comprehensive metadata"""
        async with AsyncDatabaseSession() as session:
            violation_alert = ViolationAlert(
                id=str(uuid4()),
                fingerprint_id=violation_data["fingerprint_id"],
                user_id=violation_data.get("user_id"),
                platform=violation_data["platform"],
                detected_url=violation_data["detected_url"],
                content_url=violation_data.get("content_url"),
                similarity_score=violation_data["similarity"],
                violation_type=violation_data["violation_type"],
                platform_content_id=violation_data.get("platform_content_id"),
                title=violation_data.get("title"),
                description=violation_data.get("description"),
                uploader=violation_data.get("uploader"),
                upload_date=violation_data.get("upload_date"),
                view_count=violation_data.get("view_count", 0),
                status="pending",
                evidence_data=violation_data,
                detected_at=violation_data.get("detected_at", datetime.utcnow()),
                created_at=datetime.utcnow()
            )
            
            session.add(violation_alert)
            await session.commit()
            
            # Send real-time notification
            await self.notification_manager.send_violation_alert(violation_alert)
            
            logger.info(f"Violation alert saved: {violation_alert.id}")

    async def _generate_takedown_request(
        self,
        violation: ViolationAlert
    ) -> Dict[str, Any]:
        """Generate comprehensive automated takedown request with legal compliance"""
        try:
            # Get original content information
            async with AsyncDatabaseSession() as session:
                fingerprint = await session.get(FingerprintModel, violation.fingerprint_id)
                from backend.models.content import ContentModel
                original_content = await session.get(ContentModel, fingerprint.content_id)
                from backend.models.users import User
                user = await session.get(User, violation.user_id)
            
            # Generate platform-specific takedown request
            takedown_data = {
                "platform": violation.platform,
                "violation_id": violation.id,
                "request_type": "copyright_infringement",
                "severity": self._determine_takedown_severity(violation.similarity_score),
                
                # Original content information
                "original_content": {
                    "title": original_content.filename,
                    "description": original_content.description,
                    "upload_date": original_content.created_at.isoformat(),
                    "content_type": original_content.content_type,
                    "copyright_owner": user.full_name or user.username
                },
                
                # Infringing content information
                "infringing_content": {
                    "url": violation.detected_url,
                    "platform_id": violation.platform_content_id,
                    "title": violation.title,
                    "uploader": violation.uploader,
                    "similarity_score": violation.similarity_score,
                    "violation_type": violation.violation_type
                },
                
                # Legal information
                "legal_basis": self._generate_legal_basis(violation),
                "dmca_notice": self._generate_dmca_notice(violation, user, original_content),
                
                # Contact information
                "contact_info": {
                    "name": user.full_name or user.username,
                    "email": user.email,
                    "phone": user.phone_number,
                    "address": user.address
                },
                
                # Evidence
                "evidence": {
                    "similarity_analysis": violation.evidence_data,
                    "timestamp": violation.detected_at.isoformat(),
                    "fingerprint_data": fingerprint.fingerprint_data
                },
                
                "requested_action": "complete_removal",
                "urgency": "normal",
                "follow_up_required": True
            }
            
            return takedown_data
            
        except Exception as e:
            raise TakedownError(f"Takedown request generation failed: {str(e)}")

    def _determine_takedown_severity(self, similarity_score: float) -> str:
        """Determine takedown request severity based on similarity"""
        if similarity_score >= 0.98:
            return "critical"
        elif similarity_score >= 0.90:
            return "high"
        elif similarity_score >= 0.80:
            return "medium"
        else:
            return "low"

    def _generate_legal_basis(self, violation: ViolationAlert) -> str:
        """Generate legal basis for takedown request"""
        return f"""
        This takedown request is submitted under the Digital Millennium Copyright Act (DMCA) 
        and applicable international copyright laws. The infringing content at {violation.detected_url} 
        contains substantial similarity ({violation.similarity_score:.2%}) to the original copyrighted 
        work owned by the rights holder. The unauthorized use constitutes {violation.violation_type} 
        and infringes upon the exclusive rights of the copyright owner.
        """

    def _generate_dmca_notice(
        self, 
        violation: ViolationAlert, 
        user: 'User', 
        original_content: 'ContentModel'
    ) -> str:
        """Generate formal DMCA takedown notice"""
        return f"""
        DMCA TAKEDOWN NOTICE
        
        To: {violation.platform.title()} Copyright Department
        
        I, {user.full_name or user.username}, am the copyright owner of the original work 
        titled "{original_content.filename}" created on {original_content.created_at.strftime('%Y-%m-%d')}.
        
        I have identified infringing content at the following URL:
        {violation.detected_url}
        
        The infringing content shows {violation.similarity_score:.2%} similarity to my original work 
        and constitutes unauthorized use of my copyrighted material.
        
        I have a good faith belief that the use of this material is not authorized by the copyright 
        owner, its agent, or the law.
        
        I swear, under penalty of perjury, that the information in this notification is accurate 
        and that I am the copyright owner or am authorized to act on behalf of the copyright owner.
        
        Contact Information:
        Name: {user.full_name or user.username}
        Email: {user.email}
        Date: {datetime.utcnow().strftime('%Y-%m-%d')}
        
        Requested Action: Complete removal of infringing content
        """

    async def _submit_takedown_to_platform(
        self,
        platform: str,
        takedown_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit takedown request to platform using official APIs/forms"""
        try:
            platform_handlers = {
                "youtube": self._submit_youtube_takedown,
                "instagram": self._submit_instagram_takedown,
                "tiktok": self._submit_tiktok_takedown,
                "twitter": self._submit_twitter_takedown,
                "facebook": self._submit_facebook_takedown
            }
            
            handler = platform_handlers.get(platform)
            if not handler:
                raise TakedownError(f"No takedown handler for platform: {platform}")
            
            submission_result = await handler(takedown_data)
            
            return {
                "platform": platform,
                "submission_id": submission_result.get("submission_id"),
                "status": submission_result.get("status", "submitted"),
                "reference_number": submission_result.get("reference_number"),
                "estimated_processing_time": submission_result.get("processing_time"),
                "submitted_at": datetime.utcnow().isoformat(),
                "follow_up_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Platform submission failed for {platform}: {str(e)}")
            raise TakedownError(f"Submission failed: {str(e)}")

    async def _submit_youtube_takedown(self, takedown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit takedown to YouTube using official API"""
        try:
            from backend.integrations.youtube import YouTubeAPI
            youtube_api = YouTubeAPI()
            
            # Submit copyright claim
            result = await youtube_api.submit_copyright_claim(
                video_url=takedown_data["infringing_content"]["url"],
                dmca_notice=takedown_data["dmca_notice"],
                evidence=takedown_data["evidence"]
            )
            
            return {
                "submission_id": result.get("claim_id"),
                "status": "submitted",
                "reference_number": result.get("reference"),
                "processing_time": "3-5 business days"
            }
            
        except Exception as e:
            logger.error(f"YouTube takedown submission failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _submit_instagram_takedown(self, takedown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit takedown to Instagram using official reporting"""
        try:
            from backend.integrations.instagram import InstagramAPI
            instagram_api = InstagramAPI()
            
            result = await instagram_api.submit_copyright_report(
                post_url=takedown_data["infringing_content"]["url"],
                dmca_notice=takedown_data["dmca_notice"]
            )
            
            return {
                "submission_id": result.get("report_id"),
                "status": "submitted",
                "reference_number": result.get("reference"),
                "processing_time": "24-48 hours"
            }
            
        except Exception as e:
            logger.error(f"Instagram takedown submission failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _submit_tiktok_takedown(self, takedown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit takedown to TikTok using official reporting"""
        try:
            from backend.integrations.tiktok import TikTokAPI
            tiktok_api = TikTokAPI()
            
            result = await tiktok_api.submit_copyright_report(
                video_url=takedown_data["infringing_content"]["url"],
                dmca_notice=takedown_data["dmca_notice"]
            )
            
            return {
                "submission_id": result.get("report_id"),
                "status": "submitted",
                "reference_number": result.get("reference"),
                "processing_time": "2-3 business days"
            }
            
        except Exception as e:
            logger.error(f"TikTok takedown submission failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _submit_twitter_takedown(self, takedown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit takedown to Twitter using official reporting"""
        try:
            from backend.integrations.twitter import TwitterAPI
            twitter_api = TwitterAPI()
            
            result = await twitter_api.submit_copyright_report(
                tweet_url=takedown_data["infringing_content"]["url"],
                dmca_notice=takedown_data["dmca_notice"]
            )
            
            return {
                "submission_id": result.get("report_id"),
                "status": "submitted",
                "reference_number": result.get("reference"),
                "processing_time": "1-2 business days"
            }
            
        except Exception as e:
            logger.error(f"Twitter takedown submission failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _submit_facebook_takedown(self, takedown_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit takedown to Facebook using official reporting"""
        try:
            from backend.integrations.facebook import FacebookAPI
            facebook_api = FacebookAPI()
            
            result = await facebook_api.submit_copyright_report(
                post_url=takedown_data["infringing_content"]["url"],
                dmca_notice=takedown_data["dmca_notice"]
            )
            
            return {
                "submission_id": result.get("report_id"),
                "status": "submitted",
                "reference_number": result.get("reference"),
                "processing_time": "24-72 hours"
            }
            
        except Exception as e:
            logger.error(f"Facebook takedown submission failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def _save_takedown_request(
        self,
        violation_id: str,
        takedown_data: Dict[str, Any],
        submission_result: Dict[str, Any]
    ) -> TakedownRequest:
        """Save comprehensive takedown request to database"""
        async with AsyncDatabaseSession() as session:
            takedown_request = TakedownRequest(
                id=str(uuid4()),
                violation_id=violation_id,
                fingerprint_id=takedown_data.get("fingerprint_id"),
                platform=takedown_data["platform"],
                submission_id=submission_result.get("submission_id"),
                reference_number=submission_result.get("reference_number"),
                takedown_data=takedown_data,
                submission_result=submission_result,
                status=submission_result.get("status", "submitted"),
                submitted_at=datetime.utcnow(),
                estimated_processing_time=submission_result.get("processing_time"),
                follow_up_date=datetime.utcnow() + timedelta(days=7),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(takedown_request)
            await session.commit()
            await session.refresh(takedown_request)
            
            logger.info(f"Takedown request saved: {takedown_request.id}")
            return takedown_request

    async def update_protection_settings(
        self,
        fingerprint_id: str,
        user_id: int,
        new_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update protection settings for existing fingerprint"""
        async with AsyncDatabaseSession() as session:
            fingerprint = await session.get(FingerprintModel, fingerprint_id)
            if not fingerprint or fingerprint.user_id != user_id:
                raise ProtectionError("Fingerprint not found or unauthorized")
            
            # Update settings
            if "protection_level" in new_settings:
                fingerprint.protection_level = new_settings["protection_level"]
                fingerprint.similarity_threshold = self.fingerprinting_engine.similarity_thresholds[
                    ProtectionLevel(new_settings["protection_level"])
                ]
            
            if "scan_frequency_hours" in new_settings:
                fingerprint.scan_frequency_hours = new_settings["scan_frequency_hours"]
            
            if "monitoring_platforms" in new_settings:
                fingerprint.monitoring_platforms = new_settings["monitoring_platforms"]
            
            fingerprint.updated_at = datetime.utcnow()
            await session.commit()
            
            return {
                "fingerprint_id": fingerprint_id,
                "settings_updated": True,
                "new_protection_level": fingerprint.protection_level,
                "new_scan_frequency": fingerprint.scan_frequency_hours
            }

    async def get_violation_statistics(
        self,
        user_id: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive violation statistics for user"""
        async with AsyncDatabaseSession() as session:
            since_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Get user's fingerprints
            fingerprints = await session.query(FingerprintModel).filter(
                FingerprintModel.user_id == user_id
            ).all()
            
            fingerprint_ids = [fp.id for fp in fingerprints]
            
            if not fingerprint_ids:
                return {"error": "No protected content found"}
            
            # Get violations
            violations = await session.query(ViolationAlert).filter(
                ViolationAlert.fingerprint_id.in_(fingerprint_ids),
                ViolationAlert.detected_at >= since_date
            ).all()
            
            # Get takedowns
            takedowns = await session.query(TakedownRequest).filter(
                TakedownRequest.fingerprint_id.in_(fingerprint_ids),
                TakedownRequest.submitted_at >= since_date
            ).all()
            
            # Calculate statistics
            platform_stats = {}
            violation_type_stats = {}
            
            for violation in violations:
                # Platform statistics
                platform = violation.platform
                if platform not in platform_stats:
                    platform_stats[platform] = {"count": 0, "avg_similarity": 0}
                platform_stats[platform]["count"] += 1
                platform_stats[platform]["avg_similarity"] = (
                    platform_stats[platform]["avg_similarity"] + violation.similarity_score
                ) / platform_stats[platform]["count"]
                
                # Violation type statistics
                vtype = violation.violation_type
                if vtype not in violation_type_stats:
                    violation_type_stats[vtype] = 0
                violation_type_stats[vtype] += 1
            
            return {
                "period_days": period_days,
                "total_violations": len(violations),
                "total_takedowns": len(takedowns),
                "protected_content_count": len(fingerprints),
                "platform_breakdown": platform_stats,
                "violation_type_breakdown": violation_type_stats,
                "takedown_success_rate": self._calculate_takedown_success_rate(takedowns),
                "most_targeted_platform": max(platform_stats.keys(), key=lambda k: platform_stats[k]["count"]) if platform_stats else None,
                "most_common_violation": max(violation_type_stats.keys(), key=violation_type_stats.get) if violation_type_stats else None
            }

    def _calculate_takedown_success_rate(self, takedowns: List[TakedownRequest]) -> float:
        """Calculate takedown success rate"""
        if not takedowns:
            return 0.0
        
        successful = sum(1 for td in takedowns if td.status in ["successful", "completed", "removed"])
        return (successful / len(takedowns)) * 100
