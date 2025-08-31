"""Content Protection Worker - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/content_protection_worker.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Content Protection Worker - AI-Powered Content Security
Responsibility: Advanced content fingerprinting, piracy detection, and protection enforcement
Technologies: Deep Learning, Computer Vision, NLP, Blockchain Timestamping, DMCA Automation
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Content intake → Multi-modal fingerprinting → Vector similarity search → 
Piracy detection → DMCA automation → Revenue protection → Blockchain timestamping
"""from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, AsyncGenerator
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import hashlib
import base64
from pathlib import Path
import aiofiles
import numpy as np
from PIL import Image
import cv2
import librosa
import torch
import torch.nn as nn
from transformers import CLIPModel, CLIPProcessor, AutoTokenizer, AutoModel
import tensorflow as tf

from ...ai.content_protection.fingerprint_engine import FingerprintEngine
from ...ai.content_protection.piracy_detector import PiracyDetector
from ...ai.content_protection.dmca_automation import DMCAAutomation
from ...blockchain.timestamping_service import TimestampingService
from ...security.content_validator import ContentValidator
from ...storage.vector_store import VectorStore
from ...monitoring.security_monitor import SecurityMonitor
from ...utils.media_processor import MediaProcessor
from ..parsers.content_parser import ContentParser

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for protection"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


class ProtectionLevel(Enum):
    """Protection levels"""    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class FingerprintType(Enum):
    """Fingerprint types"""    PERCEPTUAL_HASH = "perceptual_hash"
    CHROMAPRINT = "chromaprint"
    VISUAL_HASH = "visual_hash"
    SEMANTIC_VECTOR = "semantic_vector"
    SPECTRAL_SIGNATURE = "spectral_signature"
    TEXT_EMBEDDING = "text_embedding"


class DetectionStatus(Enum):
    """Detection status"""    SCANNING = "scanning"
    FOUND_MATCH = "found_match"
    FALSE_POSITIVE = "false_positive"
    DMCA_ISSUED = "dmca_issued"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


@dataclass
class ContentFingerprint:
    """Content fingerprint data structure"""    fingerprint_id: str
    content_id: str
    content_type: ContentType
    fingerprint_type: FingerprintType
    hash_value: str
    vector_embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    creator_id: str = ""
    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    blockchain_timestamp: Optional[str] = None


@dataclass
class PiracyDetection:
    """Piracy detection result"""    detection_id: str
    original_fingerprint_id: str
    detected_url: str
    platform: str
    similarity_score: float
    confidence_level: float
    detection_status: DetectionStatus
    evidence_data: Dict[str, Any]
    detected_at: datetime = field(default_factory=datetime.utcnow)
    dmca_notice_id: Optional[str] = None
    revenue_impact: Optional[float] = None


@dataclass
class ProtectionTask:
    """Content protection task"""    task_id: str
    content_path: str
    content_type: ContentType
    creator_id: str
    protection_level: ProtectionLevel
    enable_monitoring: bool = True
    enable_dmca: bool = True
    enable_blockchain: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContentProtectionWorker:
    """Advanced content protection worker with AI-powered security"""    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.worker_id = str(uuid.uuid4())
        self.is_running = False
        
        # Initialize AI models
        self._initialize_ai_models()
        
        # Initialize services
        self.fingerprint_engine = FingerprintEngine(self.config.get("fingerprint_config", {}))
        self.piracy_detector = PiracyDetector(self.config.get("piracy_config", {}))
        self.dmca_automation = DMCAAutomation(self.config.get("dmca_config", {}))
        self.timestamping_service = TimestampingService(self.config.get("blockchain_config", {}))
        self.content_validator = ContentValidator()
        self.vector_store = VectorStore(self.config.get("vector_store_config", {}))
        self.security_monitor = SecurityMonitor()
        self.media_processor = MediaProcessor()
        self.content_parser = ContentParser()
        
        # Performance tracking
        self.processing_stats = {
            "total_processed": 0,
            "successful_fingerprints": 0,
            "detections_found": 0,
            "dmca_notices_sent": 0,
            "average_processing_time": 0.0,
            "error_count": 0
        }
        
        # Active tasks tracking
        self.active_tasks: Dict[str, ProtectionTask] = {}
        self.processing_queue = asyncio.Queue()
        
        logger.info(f"🛡️ ContentProtectionWorker {self.worker_id} initialized")
    
    def _initialize_ai_models(self):
        """Initialize AI models for content analysis"""        try:
            # Initialize CLIP model for visual/text analysis
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
            
            # Initialize text embedding model
            self.text_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.text_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            
            # Move models to GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.clip_model.to(self.device)
            self.text_model.to(self.device)
            
            logger.info(f"✅ AI models initialized on device: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI models: {e}")
            # Fallback to CPU-only processing
            self.device = torch.device("cpu")
    
    async def start(self) -> bool:
        """Start the content protection worker"""        try:
            if self.is_running:
                logger.warning("ContentProtectionWorker is already running")
                return True
            
            self.is_running = True
            
            # Start processing loop
            asyncio.create_task(self._processing_loop())
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            logger.info(f"🚀 ContentProtectionWorker {self.worker_id} started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start ContentProtectionWorker: {e}")
            self.is_running = False
            return False
    
    async def stop(self) -> bool:
        """Stop the content protection worker"""        try:
            self.is_running = False
            
            # Wait for active tasks to complete
            timeout = 30  # 30 seconds timeout
            start_time = time.time()
            
            while self.active_tasks and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            logger.info(f"🛑 ContentProtectionWorker {self.worker_id} stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop ContentProtectionWorker: {e}")
            return False
    
    async def submit_protection_task(self, task: ProtectionTask) -> bool:
        """Submit a content protection task"""        try:
            if not self.is_running:
                logger.error("ContentProtectionWorker is not running")
                return False
            
            # Validate task
            if not self._validate_protection_task(task):
                logger.error(f"Invalid protection task: {task.task_id}")
                return False
            
            # Add to processing queue
            await self.processing_queue.put(task)
            self.active_tasks[task.task_id] = task
            
            logger.info(f"📝 Protection task submitted: {task.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to submit protection task: {e}")
            return False
    
    async def _processing_loop(self):
        """Main processing loop for protection tasks"""        while self.is_running:
            try:
                # Get task from queue (with timeout)
                try:
                    task = await asyncio.wait_for(
                        self.processing_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process the task
                await self._process_protection_task(task)
                
                # Mark task as processed
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Error in processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _process_protection_task(self, task: ProtectionTask):
        """Process a single protection task"""        start_time = time.time()
        
        try:
            logger.info(f"🔄 Processing protection task: {task.task_id}")
            
            # Step 1: Validate and parse content
            content_data = await self._parse_content(task)
            if not content_data:
                raise ValueError("Failed to parse content")
            
            # Step 2: Generate fingerprints
            fingerprints = await self._generate_fingerprints(task, content_data)
            if not fingerprints:
                raise ValueError("Failed to generate fingerprints")
            
            # Step 3: Store fingerprints
            await self._store_fingerprints(fingerprints)
            
            # Step 4: Enable monitoring if requested
            if task.enable_monitoring:
                await self._enable_content_monitoring(fingerprints)
            
            # Step 5: Blockchain timestamping if requested
            if task.enable_blockchain:
                await self._blockchain_timestamp(fingerprints)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, success=True)
            
            logger.info(f"✅ Protection task completed: {task.task_id} ({processing_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Failed to process protection task {task.task_id}: {e}")
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, success=False)
        
        finally:
            # Remove from active tasks
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
    
    async def _parse_content(self, task: ProtectionTask) -> Optional[Dict[str, Any]]:
        """Parse and validate content"""        try:
            content_path = Path(task.content_path)
            
            if not content_path.exists():
                raise FileNotFoundError(f"Content file not found: {task.content_path}")
            
            # Validate content
            validation_result = await self.content_validator.validate_file(
                str(content_path),
                task.content_type.value
            )
            
            if not validation_result.is_valid:
                raise ValueError(f"Invalid content: {validation_result.errors}")
            
            # Parse content based on type
            if task.content_type == ContentType.AUDIO:
                return await self._parse_audio_content(content_path)
            elif task.content_type == ContentType.VIDEO:
                return await self._parse_video_content(content_path)
            elif task.content_type == ContentType.IMAGE:
                return await self._parse_image_content(content_path)
            elif task.content_type == ContentType.TEXT:
                return await self._parse_text_content(content_path)
            else:
                return await self._parse_generic_content(content_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to parse content: {e}")
            return None
    
    async def _parse_audio_content(self, content_path: Path) -> Dict[str, Any]:
        """Parse audio content"""        try:
            # Load audio using librosa
            audio_data, sample_rate = librosa.load(str(content_path))
            
            # Extract audio features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            chroma = librosa.feature.chroma(y=audio_data, sr=sample_rate)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
            
            return {
                "type": "audio",
                "raw_data": audio_data,
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate,
                "features": {
                    "mfccs": mfccs,
                    "chroma": chroma,
                    "spectral_centroid": spectral_centroid
                },
                "metadata": {
                    "channels": 1 if len(audio_data.shape) == 1 else audio_data.shape[1],
                    "format": content_path.suffix.lower(),
                    "size_bytes": content_path.stat().st_size
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse audio content: {e}")
            raise
    
    async def _parse_video_content(self, content_path: Path) -> Dict[str, Any]:
        """Parse video content"""        try:
            # Open video using OpenCV
            cap = cv2.VideoCapture(str(content_path))
            
            if not cap.isOpened():
                raise ValueError("Cannot open video file")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Extract key frames (every second)
            key_frames = []
            frame_indices = list(range(0, frame_count, int(fps))) if fps > 0 else [0]
            
            for frame_idx in frame_indices[:10]:  # Limit to 10 key frames
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    key_frames.append(frame)
            
            cap.release()
            
            return {
                "type": "video",
                "key_frames": key_frames,
                "properties": {
                    "fps": fps,
                    "frame_count": frame_count,
                    "width": width,
                    "height": height,
                    "duration": duration
                },
                "metadata": {
                    "format": content_path.suffix.lower(),
                    "size_bytes": content_path.stat().st_size
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse video content: {e}")
            raise
    
    async def _parse_image_content(self, content_path: Path) -> Dict[str, Any]:
        """Parse image content"""        try:
            # Load image using PIL
            image = Image.open(content_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            return {
                "type": "image",
                "image_data": image_array,
                "pil_image": image,
                "properties": {
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                    "channels": len(image.getbands())
                },
                "metadata": {
                    "format": content_path.suffix.lower(),
                    "size_bytes": content_path.stat().st_size
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse image content: {e}")
            raise
    
    async def _parse_text_content(self, content_path: Path) -> Dict[str, Any]:
        """Parse text content"""        try:
            # Read text file
            async with aiofiles.open(content_path, 'r', encoding='utf-8') as f:
                text_content = await f.read()
            
            # Basic text analysis
            word_count = len(text_content.split())
            char_count = len(text_content)
            line_count = len(text_content.splitlines())
            
            # Extract language features if needed
            return {
                "type": "text",
                "content": text_content,
                "analysis": {
                    "word_count": word_count,
                    "char_count": char_count,
                    "line_count": line_count
                },
                "metadata": {
                    "format": content_path.suffix.lower(),
                    "size_bytes": content_path.stat().st_size,
                    "encoding": "utf-8"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse text content: {e}")
            raise
    
    async def _parse_generic_content(self, content_path: Path) -> Dict[str, Any]:
        """Parse generic content"""        try:
            # Basic file information
            file_stat = content_path.stat()
            
            # Generate basic hash
            async with aiofiles.open(content_path, 'rb') as f:
                content_bytes = await f.read()
            
            file_hash = hashlib.sha256(content_bytes).hexdigest()
            
            return {
                "type": "generic",
                "content_bytes": content_bytes,
                "file_hash": file_hash,
                "metadata": {
                    "format": content_path.suffix.lower(),
                    "size_bytes": file_stat.st_size,
                    "modified_time": datetime.fromtimestamp(file_stat.st_mtime)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse generic content: {e}")
            raise
    
    async def _generate_fingerprints(self, task: ProtectionTask, content_data: Dict[str, Any]) -> List[ContentFingerprint]:
        """Generate multiple fingerprints for content"""        try:
            fingerprints = []
            content_id = str(uuid.uuid4())
            
            # Generate different types of fingerprints based on content type
            if task.content_type == ContentType.AUDIO:
                fingerprints.extend(await self._generate_audio_fingerprints(
                    content_id, task, content_data
                ))
            elif task.content_type == ContentType.VIDEO:
                fingerprints.extend(await self._generate_video_fingerprints(
                    content_id, task, content_data
                ))
            elif task.content_type == ContentType.IMAGE:
                fingerprints.extend(await self._generate_image_fingerprints(
                    content_id, task, content_data
                ))
            elif task.content_type == ContentType.TEXT:
                fingerprints.extend(await self._generate_text_fingerprints(
                    content_id, task, content_data
                ))
            
            logger.info(f"✅ Generated {len(fingerprints)} fingerprints for content {content_id}")
            return fingerprints
            
        except Exception as e:
            logger.error(f"❌ Failed to generate fingerprints: {e}")
            return []
    
    async def _generate_audio_fingerprints(self, content_id: str, task: ProtectionTask, content_data: Dict[str, Any]) -> List[ContentFingerprint]:
        """Generate audio-specific fingerprints"""        fingerprints = []
        
        try:
            # Chromaprint fingerprint
            chroma_hash = await self.fingerprint_engine.generate_chromaprint(
                content_data["raw_data"],
                content_data["sample_rate"]
            )
            
            fingerprints.append(ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=task.content_type,
                fingerprint_type=FingerprintType.CHROMAPRINT,
                hash_value=chroma_hash,
                creator_id=task.creator_id,
                protection_level=task.protection_level,
                metadata={
                    "sample_rate": content_data["sample_rate"],
                    "duration": content_data["duration"],
                    "algorithm": "chromaprint"
                }
            ))
            
            # Spectral signature
            spectral_features = content_data["features"]["mfccs"]
            spectral_vector = np.mean(spectral_features, axis=1)
            spectral_hash = hashlib.sha256(spectral_vector.tobytes()).hexdigest()
            
            fingerprints.append(ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=task.content_type,
                fingerprint_type=FingerprintType.SPECTRAL_SIGNATURE,
                hash_value=spectral_hash,
                vector_embedding=spectral_vector,
                creator_id=task.creator_id,
                protection_level=task.protection_level,
                metadata={
                    "features": "mfcc",
                    "dimensions": len(spectral_vector),
                    "algorithm": "spectral_analysis"
                }
            ))
            
        except Exception as e:
            logger.error(f"❌ Failed to generate audio fingerprints: {e}")
        
        return fingerprints
    
    async def _generate_video_fingerprints(self, content_id: str, task: ProtectionTask, content_data: Dict[str, Any]) -> List[ContentFingerprint]:
        """Generate video-specific fingerprints"""        fingerprints = []
        
        try:
            # Visual hash for each key frame
            for i, frame in enumerate(content_data["key_frames"]):
                # Convert frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Generate perceptual hash
                visual_hash = await self.fingerprint_engine.generate_visual_hash(pil_image)
                
                fingerprints.append(ContentFingerprint(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=task.content_type,
                    fingerprint_type=FingerprintType.VISUAL_HASH,
                    hash_value=visual_hash,
                    creator_id=task.creator_id,
                    protection_level=task.protection_level,
                    metadata={
                        "frame_index": i,
                        "frame_time": i / content_data["properties"]["fps"],
                        "algorithm": "perceptual_hash"
                    }
                ))
            
            # CLIP embedding for visual content
            if content_data["key_frames"]:
                first_frame = content_data["key_frames"][0]
                frame_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Generate CLIP embedding
                inputs = self.clip_processor(images=pil_image, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)
                    clip_vector = image_features.cpu().numpy().flatten()
                
                clip_hash = hashlib.sha256(clip_vector.tobytes()).hexdigest()
                
                fingerprints.append(ContentFingerprint(
                    fingerprint_id=str(uuid.uuid4()),
                    content_id=content_id,
                    content_type=task.content_type,
                    fingerprint_type=FingerprintType.SEMANTIC_VECTOR,
                    hash_value=clip_hash,
                    vector_embedding=clip_vector,
                    creator_id=task.creator_id,
                    protection_level=task.protection_level,
                    metadata={
                        "model": "clip-vit-large-patch14",
                        "dimensions": len(clip_vector),
                        "algorithm": "clip_embedding"
                    }
                ))
            
        except Exception as e:
            logger.error(f"❌ Failed to generate video fingerprints: {e}")
        
        return fingerprints
    
    async def _generate_image_fingerprints(self, content_id: str, task: ProtectionTask, content_data: Dict[str, Any]) -> List[ContentFingerprint]:
        """Generate image-specific fingerprints"""        fingerprints = []
        
        try:
            image = content_data["pil_image"]
            
            # Perceptual hash
            perceptual_hash = await self.fingerprint_engine.generate_visual_hash(image)
            
            fingerprints.append(ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=task.content_type,
                fingerprint_type=FingerprintType.PERCEPTUAL_HASH,
                hash_value=perceptual_hash,
                creator_id=task.creator_id,
                protection_level=task.protection_level,
                metadata={
                    "algorithm": "perceptual_hash",
                    "image_size": f"{image.width}x{image.height}"
                }
            ))
            
            # CLIP embedding
            inputs = self.clip_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                clip_vector = image_features.cpu().numpy().flatten()
            
            clip_hash = hashlib.sha256(clip_vector.tobytes()).hexdigest()
            
            fingerprints.append(ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=task.content_type,
                fingerprint_type=FingerprintType.SEMANTIC_VECTOR,
                hash_value=clip_hash,
                vector_embedding=clip_vector,
                creator_id=task.creator_id,
                protection_level=task.protection_level,
                metadata={
                    "model": "clip-vit-large-patch14",
                    "dimensions": len(clip_vector),
                    "algorithm": "clip_embedding"
                }
            ))
            
        except Exception as e:
            logger.error(f"❌ Failed to generate image fingerprints: {e}")
        
        return fingerprints
    
    async def _generate_text_fingerprints(self, content_id: str, task: ProtectionTask, content_data: Dict[str, Any]) -> List[ContentFingerprint]:
        """Generate text-specific fingerprints"""        fingerprints = []
        
        try:
            text_content = content_data["content"]
            
            # Text hash
            text_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
            
            fingerprints.append(ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=task.content_type,
                fingerprint_type=FingerprintType.TEXT_EMBEDDING,
                hash_value=text_hash,
                creator_id=task.creator_id,
                protection_level=task.protection_level,
                metadata={
                    "algorithm": "sha256",
                    "text_length": len(text_content),
                    "word_count": content_data["analysis"]["word_count"]
                }
            ))
            
            # Semantic embedding
            inputs = self.text_tokenizer(
                text_content,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.text_model(**inputs)
                text_vector = outputs.last_hidden_state.mean(dim=1).cpu().numpy().flatten()
            
            semantic_hash = hashlib.sha256(text_vector.tobytes()).hexdigest()
            
            fingerprints.append(ContentFingerprint(
                fingerprint_id=str(uuid.uuid4()),
                content_id=content_id,
                content_type=task.content_type,
                fingerprint_type=FingerprintType.SEMANTIC_VECTOR,
                hash_value=semantic_hash,
                vector_embedding=text_vector,
                creator_id=task.creator_id,
                protection_level=task.protection_level,
                metadata={
                    "model": "all-MiniLM-L6-v2",
                    "dimensions": len(text_vector),
                    "algorithm": "semantic_embedding"
                }
            ))
            
        except Exception as e:
            logger.error(f"❌ Failed to generate text fingerprints: {e}")
        
        return fingerprints
    
    async def _store_fingerprints(self, fingerprints: List[ContentFingerprint]):
        """Store fingerprints in vector database"""        try:
            for fingerprint in fingerprints:
                # Store in vector database
                if fingerprint.vector_embedding is not None:
                    await self.vector_store.store_vector(
                        vector_id=fingerprint.fingerprint_id,
                        vector=fingerprint.vector_embedding,
                        metadata={
                            "content_id": fingerprint.content_id,
                            "content_type": fingerprint.content_type.value,
                            "fingerprint_type": fingerprint.fingerprint_type.value,
                            "creator_id": fingerprint.creator_id,
                            "protection_level": fingerprint.protection_level.value,
                            "created_at": fingerprint.created_at.isoformat(),
                            **fingerprint.metadata
                        }
                    )
            
            logger.info(f"✅ Stored {len(fingerprints)} fingerprints in vector database")
            
        except Exception as e:
            logger.error(f"❌ Failed to store fingerprints: {e}")
            raise
    
    async def _enable_content_monitoring(self, fingerprints: List[ContentFingerprint]):
        """Enable ongoing monitoring for content"""        try:
            for fingerprint in fingerprints:
                # Register with piracy detector
                await self.piracy_detector.register_content(
                    fingerprint.fingerprint_id,
                    fingerprint.hash_value,
                    fingerprint.vector_embedding,
                    fingerprint.metadata
                )
            
            logger.info(f"✅ Enabled monitoring for {len(fingerprints)} fingerprints")
            
        except Exception as e:
            logger.error(f"❌ Failed to enable content monitoring: {e}")
    
    async def _blockchain_timestamp(self, fingerprints: List[ContentFingerprint]):
        """Create blockchain timestamp for content"""        try:
            for fingerprint in fingerprints:
                # Create blockchain timestamp
                timestamp_id = await self.timestamping_service.create_timestamp(
                    fingerprint.hash_value,
                    {
                        "fingerprint_id": fingerprint.fingerprint_id,
                        "content_id": fingerprint.content_id,
                        "creator_id": fingerprint.creator_id,
                        "created_at": fingerprint.created_at.isoformat()
                    }
                )
                
                fingerprint.blockchain_timestamp = timestamp_id
            
            logger.info(f"✅ Created blockchain timestamps for {len(fingerprints)} fingerprints")
            
        except Exception as e:
            logger.error(f"❌ Failed to create blockchain timestamps: {e}")
    
    def _validate_protection_task(self, task: ProtectionTask) -> bool:
        """Validate protection task parameters"""        try:
            # Check required fields
            if not task.task_id or not task.content_path or not task.creator_id:
                return False
            
            # Check content path exists
            if not Path(task.content_path).exists():
                return False
            
            # Check content type is valid
            if task.content_type not in ContentType:
                return False
            
            # Check protection level is valid
            if task.protection_level not in ProtectionLevel:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating protection task: {e}")
            return False
    
    def _update_processing_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""        try:
            self.processing_stats["total_processed"] += 1
            
            if success:
                self.processing_stats["successful_fingerprints"] += 1
            else:
                self.processing_stats["error_count"] += 1
            
            # Update average processing time
            total_time = (
                self.processing_stats["average_processing_time"] * 
                (self.processing_stats["total_processed"] - 1) + 
                processing_time
            )
            self.processing_stats["average_processing_time"] = (
                total_time / self.processing_stats["total_processed"]
            )
            
        except Exception as e:
            logger.error(f"❌ Error updating processing stats: {e}")
    
    async def _monitoring_loop(self):
        """Monitoring loop for worker health"""        while self.is_running:
            try:
                # Report worker status
                await self.security_monitor.report_worker_status(
                    self.worker_id,
                    {
                        "active_tasks": len(self.active_tasks),
                        "queue_size": self.processing_queue.qsize(),
                        "stats": self.processing_stats.copy()
                    }
                )
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def get_worker_status(self) -> Dict[str, Any]:
        """Get current worker status"""        return {
            "worker_id": self.worker_id,
            "is_running": self.is_running,
            "active_tasks": len(self.active_tasks),
            "queue_size": self.processing_queue.qsize(),
            "device": str(self.device),
            "statistics": self.processing_stats.copy(),
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }


# Global worker instance
_content_protection_worker: Optional[ContentProtectionWorker] = None


async def get_content_protection_worker() -> Optional[ContentProtectionWorker]:
    """Get the global content protection worker instance"""    return _content_protection_worker


async def initialize_content_protection_worker(config: Dict[str, Any] = None) -> bool:
    """Initialize the content protection worker"""    global _content_protection_worker
    
    try:
        if _content_protection_worker is not None:
            logger.warning("ContentProtectionWorker already initialized")
            return True
        
        _content_protection_worker = ContentProtectionWorker(config)
        success = await _content_protection_worker.start()
        
        if success:
            logger.info("✅ ContentProtectionWorker initialized successfully")
        else:
            logger.error("❌ Failed to initialize ContentProtectionWorker")
            _content_protection_worker = None
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize ContentProtectionWorker: {e}")
        _content_protection_worker = None
        return False


async def shutdown_content_protection_worker() -> bool:
    """Shutdown the content protection worker"""    global _content_protection_worker
    
    try:
        if _content_protection_worker is None:
            logger.warning("ContentProtectionWorker not initialized")
            return True
        
        success = await _content_protection_worker.stop()
        _content_protection_worker = None
        
        if success:
            logger.info("✅ ContentProtectionWorker shutdown successfully")
        else:
            logger.error("❌ Failed to shutdown ContentProtectionWorker")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to shutdown ContentProtectionWorker: {e}")
        return False


# Export classes and functions
__all__ = [
    "ContentProtectionWorker",
    "ContentType",
    "ProtectionLevel",
    "FingerprintType",
    "DetectionStatus",
    "ContentFingerprint",
    "PiracyDetection",
    "ProtectionTask",
    "get_content_protection_worker",
    "initialize_content_protection_worker",
    "shutdown_content_protection_worker"
]
