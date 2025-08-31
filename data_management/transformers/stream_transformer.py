"""🔄 Stream Processing Transformer - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/transformers/stream_transformer.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Fahed Mlaiel (mlaiel@live.de)
- ML Engineer: Fahed Mlaiel (mlaiel@live.de)
- AI Research Expert: Fahed Mlaiel (mlaiel@live.de)
- DevOps Engineer: Fahed Mlaiel (mlaiel@live.de)
- DBA: Fahed Mlaiel (mlaiel@live.de)
- Sécurité Expert: Fahed Mlaiel (mlaiel@live.de)
"""import asyncio
import logging
import time
import json
import queue
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

# Stream processing libraries
import numpy as np
import pandas as pd
from collections import deque
import redis
import aioredis
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

# Real-time processing
import cv2
import pyaudio
import wave
import librosa
import soundfile as sf
from PIL import Image

# Async processing
import asyncio
import aiofiles
import websockets

from ..models.stream_models import (
    StreamMetadata, StreamChunk, ProcessingResult,
    StreamState, RealtimeMetrics
)
from ...core.exceptions import StreamProcessingError, ValidationError
from ...core.config import get_settings
from ...utils.redis_manager import RedisManager
from ...utils.queue_manager import QueueManager

settings = get_settings()
logger = logging.getLogger(__name__)

class StreamType(Enum):
    """Types de flux supportés"""    AUDIO_REALTIME = "audio_realtime"
    VIDEO_REALTIME = "video_realtime"
    WEBCAM_STREAM = "webcam_stream"
    MICROPHONE_STREAM = "microphone_stream"
    FILE_STREAM = "file_stream"
    NETWORK_STREAM = "network_stream"
    WEBSOCKET_STREAM = "websocket_stream"
    KAFKA_STREAM = "kafka_stream"

class ProcessingMode(Enum):
    """Modes de traitement"""    REALTIME = "realtime"
    BUFFERED = "buffered"
    BATCH = "batch"
    SLIDING_WINDOW = "sliding_window"

class StreamFormat(Enum):
    """Formats de flux"""    RAW_AUDIO = "raw_audio"
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    RAW_VIDEO = "raw_video"
    MP4 = "mp4"
    AVI = "avi"
    MJPEG = "mjpeg"
    H264 = "h264"
    JSON = "json"
    BINARY = "binary"

@dataclass
class StreamConfig:
    """Configuration de flux"""    stream_type: StreamType
    processing_mode: ProcessingMode
    format: StreamFormat
    buffer_size: int = 8192
    chunk_duration: float = 0.1  # seconds
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    frame_rate: Optional[int] = None
    resolution: Optional[Tuple[int, int]] = None
    quality: str = "standard"
    compression: bool = False
    encryption: bool = False
    creator_type: Optional[str] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StreamProcessingResult:
    """Résultat de traitement de flux"""    success: bool
    stream_id: str
    chunk_id: str
    processed_data: Optional[Any]
    metadata: Dict[str, Any]
    processing_time: float
    latency: float
    quality_metrics: Dict[str, float]
    errors: List[str]
    warnings: List[str]

class AudioStreamProcessor:
    """Processeur de flux audio en temps réel"""    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        self.audio_buffer = deque(maxlen=config.buffer_size)
        
        # Configuration audio
        self.sample_rate = config.sample_rate or 44100
        self.channels = config.channels or 1
        self.chunk_size = int(self.sample_rate * config.chunk_duration)
        
        # Initialisation PyAudio
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        
        # Métriques temps réel
        self.metrics = {
            'chunks_processed': 0,
            'avg_processing_time': 0.0,
            'max_latency': 0.0,
            'audio_level': 0.0,
            'quality_score': 0.0
        }
    
    async def start_stream(self, source: Optional[str] = None) -> str:
        """Démarre le flux audio"""        
        try:
            stream_id = f"audio_stream_{uuid.uuid4().hex[:8]}"
            
            if source:
                # Flux depuis fichier
                await self._start_file_stream(source, stream_id)
            else:
                # Flux depuis microphone
                await self._start_microphone_stream(stream_id)
            
            self.is_processing = True
            logger.info(f"Flux audio démarré: {stream_id}")
            
            return stream_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage flux audio: {e}")
            raise StreamProcessingError(f"Échec démarrage flux: {e}")
    
    async def _start_microphone_stream(self, stream_id: str):
        """Démarre le flux depuis le microphone"""        
        def audio_callback(in_data, frame_count, time_info, status):
            if status:
                logger.warning(f"Statut audio callback: {status}")
            
            # Conversion des données audio
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            # Ajout au buffer
            self.audio_buffer.append({
                'timestamp': time.time(),
                'data': audio_data,
                'frame_count': frame_count
            })
            
            return (in_data, pyaudio.paContinue)
        
        # Ouverture du flux microphone
        self.stream = self.pyaudio.open(
            format=pyaudio.paFloat32,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=audio_callback
        )
        
        self.stream.start_stream()
    
    async def _start_file_stream(self, file_path: str, stream_id: str):
        """Démarre le flux depuis un fichier audio"""        
        try:
            # Chargement du fichier audio
            audio_data, sr = librosa.load(file_path, sr=self.sample_rate)
            
            # Simulation de streaming en chunks
            chunk_samples = int(sr * self.config.chunk_duration)
            
            for i in range(0, len(audio_data), chunk_samples):
                chunk = audio_data[i:i + chunk_samples]
                
                self.audio_buffer.append({
                    'timestamp': time.time(),
                    'data': chunk,
                    'frame_count': len(chunk)
                })
                
                # Attente pour simuler le temps réel
                await asyncio.sleep(self.config.chunk_duration)
                
        except Exception as e:
            logger.error(f"Erreur flux fichier audio {file_path}: {e}")
            raise
    
    async def process_stream(
        self,
        processor_func: Callable[[np.ndarray], Dict[str, Any]]
    ) -> AsyncGenerator[StreamProcessingResult, None]:
        """Traite le flux audio en temps réel"""        
        chunk_counter = 0
        
        while self.is_processing:
            try:
                # Récupération du chunk depuis le buffer
                if self.audio_buffer:
                    chunk_data = self.audio_buffer.popleft()
                    
                    start_time = time.time()
                    
                    # Traitement du chunk
                    processing_result = processor_func(chunk_data['data'])
                    
                    processing_time = time.time() - start_time
                    latency = time.time() - chunk_data['timestamp']
                    
                    # Mise à jour des métriques
                    self._update_metrics(processing_time, latency, chunk_data['data'])
                    
                    # Création du résultat
                    result = StreamProcessingResult(
                        success=True,
                        stream_id=f"audio_stream_{uuid.uuid4().hex[:8]}",
                        chunk_id=f"chunk_{chunk_counter}",
                        processed_data=processing_result,
                        metadata={
                            'chunk_size': len(chunk_data['data']),
                            'sample_rate': self.sample_rate,
                            'channels': self.channels,
                            'timestamp': chunk_data['timestamp']
                        },
                        processing_time=processing_time,
                        latency=latency,
                        quality_metrics=self._calculate_audio_quality(chunk_data['data']),
                        errors=[],
                        warnings=[]
                    )
                    
                    chunk_counter += 1
                    yield result
                
                else:
                    # Attente de nouveaux données
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Erreur traitement chunk audio: {e}")
                yield StreamProcessingResult(
                    success=False,
                    stream_id="error",
                    chunk_id=f"chunk_{chunk_counter}",
                    processed_data=None,
                    metadata={},
                    processing_time=0.0,
                    latency=0.0,
                    quality_metrics={},
                    errors=[str(e)],
                    warnings=[]
                )
    
    def _update_metrics(self, processing_time: float, latency: float, audio_data: np.ndarray):
        """Met à jour les métriques de performance"""        
        self.metrics['chunks_processed'] += 1
        
        # Moyenne mobile du temps de traitement
        alpha = 0.1
        self.metrics['avg_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self.metrics['avg_processing_time']
        )
        
        # Latence maximale
        self.metrics['max_latency'] = max(self.metrics['max_latency'], latency)
        
        # Niveau audio (RMS)
        if len(audio_data) > 0:
            rms = np.sqrt(np.mean(audio_data**2))
            self.metrics['audio_level'] = (
                alpha * rms + (1 - alpha) * self.metrics['audio_level']
            )
    
    def _calculate_audio_quality(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Calcule les métriques de qualité audio"""        
        if len(audio_data) == 0:
            return {}
        
        # RMS Energy
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Zero Crossing Rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # Spectral Centroid
        if len(audio_data) > 512:  # Minimum pour FFT
            spectral_centroid = np.mean(
                librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
            )
        else:
            spectral_centroid = 0.0
        
        return {
            'rms_energy': float(rms),
            'zero_crossing_rate': float(zcr),
            'spectral_centroid': float(spectral_centroid),
            'signal_strength': min(1.0, rms * 10)  # Normalisation
        }
    
    def stop_stream(self):
        """Arrête le flux audio"""        
        self.is_processing = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        self.pyaudio.terminate()
        logger.info("Flux audio arrêté")
    
    def get_metrics(self) -> Dict[str, float]:
        """Retourne les métriques actuelles"""        return self.metrics.copy()

class VideoStreamProcessor:
    """Processeur de flux vidéo en temps réel"""    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        self.frame_buffer = deque(maxlen=config.buffer_size)
        
        # Configuration vidéo
        self.frame_rate = config.frame_rate or 30
        self.resolution = config.resolution or (640, 480)
        self.frame_interval = 1.0 / self.frame_rate
        
        # Capture vidéo
        self.capture = None
        
        # Métriques temps réel
        self.metrics = {
            'frames_processed': 0,
            'avg_processing_time': 0.0,
            'max_latency': 0.0,
            'frame_rate': 0.0,
            'quality_score': 0.0
        }
    
    async def start_stream(self, source: Union[int, str] = 0) -> str:
        """Démarre le flux vidéo"""        
        try:
            stream_id = f"video_stream_{uuid.uuid4().hex[:8]}"
            
            # Initialisation de la capture
            self.capture = cv2.VideoCapture(source)
            
            if not self.capture.isOpened():
                raise StreamProcessingError(f"Impossible d'ouvrir la source vidéo: {source}")
            
            # Configuration de la capture
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.capture.set(cv2.CAP_PROP_FPS, self.frame_rate)
            
            # Démarrage de la capture en arrière-plan
            self.is_processing = True
            asyncio.create_task(self._capture_frames())
            
            logger.info(f"Flux vidéo démarré: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage flux vidéo: {e}")
            raise StreamProcessingError(f"Échec démarrage flux: {e}")
    
    async def _capture_frames(self):
        """Capture les frames en arrière-plan"""        
        frame_counter = 0
        last_frame_time = time.time()
        
        while self.is_processing and self.capture.isOpened():
            try:
                ret, frame = self.capture.read()
                
                if not ret:
                    logger.warning("Impossible de lire la frame")
                    await asyncio.sleep(self.frame_interval)
                    continue
                
                current_time = time.time()
                
                # Ajout de la frame au buffer
                self.frame_buffer.append({
                    'timestamp': current_time,
                    'frame': frame,
                    'frame_id': frame_counter
                })
                
                # Calcul du frame rate
                if frame_counter > 0:
                    actual_fps = 1.0 / (current_time - last_frame_time)
                    self.metrics['frame_rate'] = (
                        0.1 * actual_fps + 0.9 * self.metrics['frame_rate']
                    )
                
                last_frame_time = current_time
                frame_counter += 1
                
                # Attente pour respecter le frame rate
                await asyncio.sleep(max(0, self.frame_interval - (time.time() - current_time)))
                
            except Exception as e:
                logger.error(f"Erreur capture frame: {e}")
                await asyncio.sleep(0.1)
    
    async def process_stream(
        self,
        processor_func: Callable[[np.ndarray], Dict[str, Any]]
    ) -> AsyncGenerator[StreamProcessingResult, None]:
        """Traite le flux vidéo en temps réel"""        
        frame_counter = 0
        
        while self.is_processing:
            try:
                # Récupération de la frame depuis le buffer
                if self.frame_buffer:
                    frame_data = self.frame_buffer.popleft()
                    
                    start_time = time.time()
                    
                    # Traitement de la frame
                    processing_result = processor_func(frame_data['frame'])
                    
                    processing_time = time.time() - start_time
                    latency = time.time() - frame_data['timestamp']
                    
                    # Mise à jour des métriques
                    self._update_metrics(processing_time, latency, frame_data['frame'])
                    
                    # Création du résultat
                    result = StreamProcessingResult(
                        success=True,
                        stream_id=f"video_stream_{uuid.uuid4().hex[:8]}",
                        chunk_id=f"frame_{frame_counter}",
                        processed_data=processing_result,
                        metadata={
                            'frame_shape': frame_data['frame'].shape,
                            'frame_rate': self.frame_rate,
                            'resolution': self.resolution,
                            'timestamp': frame_data['timestamp']
                        },
                        processing_time=processing_time,
                        latency=latency,
                        quality_metrics=self._calculate_video_quality(frame_data['frame']),
                        errors=[],
                        warnings=[]
                    )
                    
                    frame_counter += 1
                    yield result
                
                else:
                    # Attente de nouvelles frames
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Erreur traitement frame vidéo: {e}")
                yield StreamProcessingResult(
                    success=False,
                    stream_id="error",
                    chunk_id=f"frame_{frame_counter}",
                    processed_data=None,
                    metadata={},
                    processing_time=0.0,
                    latency=0.0,
                    quality_metrics={},
                    errors=[str(e)],
                    warnings=[]
                )
    
    def _update_metrics(self, processing_time: float, latency: float, frame: np.ndarray):
        """Met à jour les métriques de performance"""        
        self.metrics['frames_processed'] += 1
        
        # Moyenne mobile du temps de traitement
        alpha = 0.1
        self.metrics['avg_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self.metrics['avg_processing_time']
        )
        
        # Latence maximale
        self.metrics['max_latency'] = max(self.metrics['max_latency'], latency)
    
    def _calculate_video_quality(self, frame: np.ndarray) -> Dict[str, float]:
        """Calcule les métriques de qualité vidéo"""        
        if frame is None or frame.size == 0:
            return {}
        
        # Conversion en niveaux de gris pour l'analyse
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Netteté (Laplacian variance)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Luminosité moyenne
        brightness = np.mean(gray)
        
        # Contraste (écart-type)
        contrast = np.std(gray)
        
        # Détection de mouvement (si frame précédente disponible)
        motion_score = 0.0
        if hasattr(self, 'previous_frame'):
            diff = cv2.absdiff(gray, self.previous_frame)
            motion_score = np.mean(diff)
        
        self.previous_frame = gray.copy()
        
        return {
            'sharpness': float(sharpness),
            'brightness': float(brightness),
            'contrast': float(contrast),
            'motion_score': float(motion_score),
            'quality_score': min(1.0, sharpness / 1000)  # Normalisation
        }
    
    def stop_stream(self):
        """Arrête le flux vidéo"""        
        self.is_processing = False
        
        if self.capture:
            self.capture.release()
        
        logger.info("Flux vidéo arrêté")
    
    def get_metrics(self) -> Dict[str, float]:
        """Retourne les métriques actuelles"""        return self.metrics.copy()

class WebSocketStreamProcessor:
    """Processeur de flux WebSocket en temps réel"""    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        self.message_buffer = deque(maxlen=config.buffer_size)
        
        # Métriques
        self.metrics = {
            'messages_processed': 0,
            'avg_processing_time': 0.0,
            'connection_count': 0,
            'data_throughput': 0.0
        }
    
    async def start_server(self, host: str = "localhost", port: int = 8765) -> str:
        """Démarre le serveur WebSocket"""        
        try:
            stream_id = f"websocket_stream_{uuid.uuid4().hex[:8]}"
            
            # Fonction de gestion des connexions
            async def handle_client(websocket, path):
                self.metrics['connection_count'] += 1
                logger.info(f"Nouvelle connexion WebSocket: {websocket.remote_address}")
                
                try:
                    async for message in websocket:
                        # Ajout du message au buffer
                        self.message_buffer.append({
                            'timestamp': time.time(),
                            'data': message,
                            'client': websocket.remote_address
                        })
                        
                        # Confirmation de réception
                        await websocket.send(json.dumps({
                            'status': 'received',
                            'timestamp': time.time()
                        }))
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"Connexion fermée: {websocket.remote_address}")
                finally:
                    self.metrics['connection_count'] -= 1
            
            # Démarrage du serveur
            self.server = await websockets.serve(handle_client, host, port)
            self.is_processing = True
            
            logger.info(f"Serveur WebSocket démarré sur {host}:{port} - ID: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage serveur WebSocket: {e}")
            raise StreamProcessingError(f"Échec démarrage serveur: {e}")
    
    async def process_stream(
        self,
        processor_func: Callable[[Any], Dict[str, Any]]
    ) -> AsyncGenerator[StreamProcessingResult, None]:
        """Traite le flux WebSocket en temps réel"""        
        message_counter = 0
        
        while self.is_processing:
            try:
                # Récupération du message depuis le buffer
                if self.message_buffer:
                    message_data = self.message_buffer.popleft()
                    
                    start_time = time.time()
                    
                    # Parsing du message
                    try:
                        if isinstance(message_data['data'], str):
                            parsed_data = json.loads(message_data['data'])
                        else:
                            parsed_data = message_data['data']
                    except json.JSONDecodeError:
                        parsed_data = {'raw_data': message_data['data']}
                    
                    # Traitement du message
                    processing_result = processor_func(parsed_data)
                    
                    processing_time = time.time() - start_time
                    latency = time.time() - message_data['timestamp']
                    
                    # Mise à jour des métriques
                    self._update_metrics(processing_time, len(str(message_data['data'])))
                    
                    # Création du résultat
                    result = StreamProcessingResult(
                        success=True,
                        stream_id=f"websocket_stream_{uuid.uuid4().hex[:8]}",
                        chunk_id=f"message_{message_counter}",
                        processed_data=processing_result,
                        metadata={
                            'client': str(message_data['client']),
                            'message_size': len(str(message_data['data'])),
                            'timestamp': message_data['timestamp']
                        },
                        processing_time=processing_time,
                        latency=latency,
                        quality_metrics={'message_integrity': 1.0},
                        errors=[],
                        warnings=[]
                    )
                    
                    message_counter += 1
                    yield result
                
                else:
                    # Attente de nouveaux messages
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Erreur traitement message WebSocket: {e}")
                yield StreamProcessingResult(
                    success=False,
                    stream_id="error",
                    chunk_id=f"message_{message_counter}",
                    processed_data=None,
                    metadata={},
                    processing_time=0.0,
                    latency=0.0,
                    quality_metrics={},
                    errors=[str(e)],
                    warnings=[]
                )
    
    def _update_metrics(self, processing_time: float, data_size: int):
        """Met à jour les métriques de performance"""        
        self.metrics['messages_processed'] += 1
        
        # Moyenne mobile du temps de traitement
        alpha = 0.1
        self.metrics['avg_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self.metrics['avg_processing_time']
        )
        
        # Débit de données (bytes/sec)
        self.metrics['data_throughput'] = (
            alpha * (data_size / max(processing_time, 0.001)) + 
            (1 - alpha) * self.metrics['data_throughput']
        )
    
    async def stop_server(self):
        """Arrête le serveur WebSocket"""        
        self.is_processing = False
        
        if hasattr(self, 'server'):
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("Serveur WebSocket arrêté")
    
    def get_metrics(self) -> Dict[str, float]:
        """Retourne les métriques actuelles"""        return self.metrics.copy()

class KafkaStreamProcessor:
    """Processeur de flux Kafka en temps réel"""    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_processing = False
        
        # Configuration Kafka
        self.bootstrap_servers = config.custom_parameters.get('bootstrap_servers', ['localhost:9092'])
        self.topic = config.custom_parameters.get('topic', 'content_stream')
        self.group_id = config.custom_parameters.get('group_id', 'ia_influencer_group')
        
        # Producer et Consumer
        self.producer = None
        self.consumer = None
        
        # Métriques
        self.metrics = {
            'messages_produced': 0,
            'messages_consumed': 0,
            'avg_processing_time': 0.0,
            'throughput': 0.0
        }
    
    async def start_producer(self) -> str:
        """Démarre le producteur Kafka"""        
        try:
            stream_id = f"kafka_producer_{uuid.uuid4().hex[:8]}"
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            
            logger.info(f"Producteur Kafka démarré - ID: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage producteur Kafka: {e}")
            raise StreamProcessingError(f"Échec démarrage producteur: {e}")
    
    async def start_consumer(self) -> str:
        """Démarre le consommateur Kafka"""        
        try:
            stream_id = f"kafka_consumer_{uuid.uuid4().hex[:8]}"
            
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True
            )
            
            self.is_processing = True
            logger.info(f"Consommateur Kafka démarré - ID: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage consommateur Kafka: {e}")
            raise StreamProcessingError(f"Échec démarrage consommateur: {e}")
    
    async def produce_message(self, data: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Produit un message vers Kafka"""        
        try:
            if not self.producer:
                raise StreamProcessingError("Producteur Kafka non initialisé")
            
            # Envoi du message
            future = self.producer.send(self.topic, value=data, key=key)
            
            # Attente de confirmation
            record_metadata = future.get(timeout=10)
            
            self.metrics['messages_produced'] += 1
            
            logger.debug(f"Message produit - Topic: {record_metadata.topic}, Partition: {record_metadata.partition}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur production message Kafka: {e}")
            return False
    
    async def consume_stream(
        self,
        processor_func: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> AsyncGenerator[StreamProcessingResult, None]:
        """Consomme et traite le flux Kafka"""        
        message_counter = 0
        
        try:
            while self.is_processing and self.consumer:
                # Polling des messages
                message_batch = self.consumer.poll(timeout_ms=100)
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            start_time = time.time()
                            
                            # Traitement du message
                            processing_result = processor_func(message.value)
                            
                            processing_time = time.time() - start_time
                            
                            # Mise à jour des métriques
                            self._update_metrics(processing_time)
                            
                            # Création du résultat
                            result = StreamProcessingResult(
                                success=True,
                                stream_id=f"kafka_stream_{uuid.uuid4().hex[:8]}",
                                chunk_id=f"message_{message_counter}",
                                processed_data=processing_result,
                                metadata={
                                    'topic': message.topic,
                                    'partition': message.partition,
                                    'offset': message.offset,
                                    'key': message.key.decode('utf-8') if message.key else None,
                                    'timestamp': message.timestamp
                                },
                                processing_time=processing_time,
                                latency=time.time() - (message.timestamp / 1000),
                                quality_metrics={'message_integrity': 1.0},
                                errors=[],
                                warnings=[]
                            )
                            
                            message_counter += 1
                            yield result
                            
                        except Exception as e:
                            logger.error(f"Erreur traitement message Kafka: {e}")
                            yield StreamProcessingResult(
                                success=False,
                                stream_id="error",
                                chunk_id=f"message_{message_counter}",
                                processed_data=None,
                                metadata={},
                                processing_time=0.0,
                                latency=0.0,
                                quality_metrics={},
                                errors=[str(e)],
                                warnings=[]
                            )
                
                # Petite pause si pas de messages
                if not message_batch:
                    await asyncio.sleep(0.01)
                    
        except Exception as e:
            logger.error(f"Erreur consommation flux Kafka: {e}")
            yield StreamProcessingResult(
                success=False,
                stream_id="error",
                chunk_id="kafka_error",
                processed_data=None,
                metadata={},
                processing_time=0.0,
                latency=0.0,
                quality_metrics={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _update_metrics(self, processing_time: float):
        """Met à jour les métriques Kafka"""        
        self.metrics['messages_consumed'] += 1
        
        # Moyenne mobile du temps de traitement
        alpha = 0.1
        self.metrics['avg_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self.metrics['avg_processing_time']
        )
        
        # Débit (messages/sec)
        if processing_time > 0:
            current_throughput = 1.0 / processing_time
            self.metrics['throughput'] = (
                alpha * current_throughput + 
                (1 - alpha) * self.metrics['throughput']
            )
    
    def stop_kafka(self):
        """Arrête les composants Kafka"""        
        self.is_processing = False
        
        if self.producer:
            self.producer.close()
        
        if self.consumer:
            self.consumer.close()
        
        logger.info("Flux Kafka arrêté")
    
    def get_metrics(self) -> Dict[str, float]:
        """Retourne les métriques Kafka"""        return self.metrics.copy()

class StreamTransformer:
    """Gestionnaire principal des flux en temps réel"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_streams = {}
        self.redis_manager = RedisManager()
        
        # Configuration par type de créateur
        self.creator_stream_configs = {
            'musician': {
                'preferred_formats': [StreamFormat.WAV, StreamFormat.FLAC],
                'quality': 'high',
                'buffer_size': 16384,
                'sample_rate': 48000
            },
            'photographer': {
                'preferred_formats': [StreamFormat.RAW_VIDEO, StreamFormat.MJPEG],
                'quality': 'ultra',
                'buffer_size': 4096,
                'frame_rate': 60
            },
            'influencer': {
                'preferred_formats': [StreamFormat.MP4, StreamFormat.H264],
                'quality': 'standard',
                'buffer_size': 8192,
                'frame_rate': 30
            },
            'blogger': {
                'preferred_formats': [StreamFormat.JSON],
                'quality': 'standard',
                'buffer_size': 1024
            },
            'comedian': {
                'preferred_formats': [StreamFormat.MP4, StreamFormat.WAV],
                'quality': 'high',
                'buffer_size': 12288,
                'frame_rate': 30
            }
        }
    
    def create_stream_processor(
        self,
        stream_config: StreamConfig
    ) -> Union[AudioStreamProcessor, VideoStreamProcessor, WebSocketStreamProcessor, KafkaStreamProcessor]:
        """Crée le processeur de flux approprié"""        
        if stream_config.stream_type in [StreamType.AUDIO_REALTIME, StreamType.MICROPHONE_STREAM]:
            return AudioStreamProcessor(stream_config)
        
        elif stream_config.stream_type in [StreamType.VIDEO_REALTIME, StreamType.WEBCAM_STREAM]:
            return VideoStreamProcessor(stream_config)
        
        elif stream_config.stream_type == StreamType.WEBSOCKET_STREAM:
            return WebSocketStreamProcessor(stream_config)
        
        elif stream_config.stream_type == StreamType.KAFKA_STREAM:
            return KafkaStreamProcessor(stream_config)
        
        else:
            raise ValueError(f"Type de flux non supporté: {stream_config.stream_type}")
    
    async def start_realtime_processing(
        self,
        stream_config: StreamConfig,
        processor_func: Callable[[Any], Dict[str, Any]],
        source: Optional[Union[str, int]] = None
    ) -> str:
        """Démarre le traitement en temps réel"""        
        try:
            # Création du processeur
            processor = self.create_stream_processor(stream_config)
            
            # Démarrage du flux
            if isinstance(processor, AudioStreamProcessor):
                stream_id = await processor.start_stream(source)
            elif isinstance(processor, VideoStreamProcessor):
                stream_id = await processor.start_stream(source or 0)
            elif isinstance(processor, WebSocketStreamProcessor):
                host = stream_config.custom_parameters.get('host', 'localhost')
                port = stream_config.custom_parameters.get('port', 8765)
                stream_id = await processor.start_server(host, port)
            elif isinstance(processor, KafkaStreamProcessor):
                if stream_config.custom_parameters.get('mode') == 'consumer':
                    stream_id = await processor.start_consumer()
                else:
                    stream_id = await processor.start_producer()
            else:
                raise ValueError("Type de processeur non reconnu")
            
            # Enregistrement du flux actif
            self.active_streams[stream_id] = {
                'processor': processor,
                'config': stream_config,
                'start_time': time.time()
            }
            
            # Démarrage du traitement asynchrone
            asyncio.create_task(
                self._process_stream_async(stream_id, processor, processor_func)
            )
            
            logger.info(f"Traitement temps réel démarré: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage traitement temps réel: {e}")
            raise StreamProcessingError(f"Échec démarrage: {e}")
    
    async def _process_stream_async(
        self,
        stream_id: str,
        processor: Any,
        processor_func: Callable[[Any], Dict[str, Any]]
    ):
        """Traite le flux de manière asynchrone"""        
        try:
            async for result in processor.process_stream(processor_func):
                # Stockage du résultat dans Redis pour monitoring
                await self._store_result_redis(stream_id, result)
                
                # Log des erreurs critiques
                if not result.success:
                    logger.error(f"Erreur traitement flux {stream_id}: {result.errors}")
                
        except Exception as e:
            logger.error(f"Erreur traitement flux asynchrone {stream_id}: {e}")
        finally:
            # Nettoyage
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
    
    async def _store_result_redis(self, stream_id: str, result: StreamProcessingResult):
        """Stocke le résultat dans Redis"""        
        try:
            # Conversion en dictionnaire sérialisable
            result_dict = {
                'success': result.success,
                'stream_id': result.stream_id,
                'chunk_id': result.chunk_id,
                'metadata': result.metadata,
                'processing_time': result.processing_time,
                'latency': result.latency,
                'quality_metrics': result.quality_metrics,
                'timestamp': time.time()
            }
            
            # Stockage avec expiration (1 heure)
            await self.redis_manager.set_with_expiry(
                f"stream_result:{stream_id}:{result.chunk_id}",
                json.dumps(result_dict),
                3600
            )
            
        except Exception as e:
            logger.warning(f"Erreur stockage Redis pour {stream_id}: {e}")
    
    def get_stream_metrics(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Retourne les métriques d'un flux"""        
        if stream_id not in self.active_streams:
            return None
        
        processor = self.active_streams[stream_id]['processor']
        start_time = self.active_streams[stream_id]['start_time']
        
        metrics = processor.get_metrics()
        metrics['uptime'] = time.time() - start_time
        metrics['stream_id'] = stream_id
        
        return metrics
    
    def get_all_streams_status(self) -> Dict[str, Dict[str, Any]]:
        """Retourne le statut de tous les flux actifs"""        
        status = {}
        
        for stream_id in self.active_streams:
            status[stream_id] = self.get_stream_metrics(stream_id)
        
        return status
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Arrête un flux spécifique"""        
        if stream_id not in self.active_streams:
            logger.warning(f"Flux non trouvé: {stream_id}")
            return False
        
        try:
            processor = self.active_streams[stream_id]['processor']
            
            # Arrêt selon le type de processeur
            if isinstance(processor, AudioStreamProcessor):
                processor.stop_stream()
            elif isinstance(processor, VideoStreamProcessor):
                processor.stop_stream()
            elif isinstance(processor, WebSocketStreamProcessor):
                await processor.stop_server()
            elif isinstance(processor, KafkaStreamProcessor):
                processor.stop_kafka()
            
            # Suppression de la liste active
            del self.active_streams[stream_id]
            
            logger.info(f"Flux arrêté: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur arrêt flux {stream_id}: {e}")
            return False
    
    async def stop_all_streams(self):
        """Arrête tous les flux actifs"""        
        stream_ids = list(self.active_streams.keys())
        
        for stream_id in stream_ids:
            await self.stop_stream(stream_id)
        
        logger.info("Tous les flux ont été arrêtés")
    
    def get_creator_optimized_config(
        self,
        creator_type: str,
        stream_type: StreamType,
        processing_mode: ProcessingMode = ProcessingMode.REALTIME
    ) -> StreamConfig:
        """Génère une configuration optimisée pour le créateur"""        
        creator_config = self.creator_stream_configs.get(
            creator_type,
            self.creator_stream_configs['influencer']
        )
        
        # Détection du format approprié
        if stream_type in [StreamType.AUDIO_REALTIME, StreamType.MICROPHONE_STREAM]:
            format_type = creator_config['preferred_formats'][0] if creator_config['preferred_formats'][0] in [StreamFormat.WAV, StreamFormat.MP3, StreamFormat.FLAC] else StreamFormat.WAV
            sample_rate = creator_config.get('sample_rate', 44100)
            channels = 2 if creator_type == 'musician' else 1
            frame_rate = None
            resolution = None
        
        elif stream_type in [StreamType.VIDEO_REALTIME, StreamType.WEBCAM_STREAM]:
            format_type = creator_config['preferred_formats'][0] if creator_config['preferred_formats'][0] in [StreamFormat.MP4, StreamFormat.AVI, StreamFormat.MJPEG] else StreamFormat.MP4
            sample_rate = None
            channels = None
            frame_rate = creator_config.get('frame_rate', 30)
            resolution = (1920, 1080) if creator_config['quality'] == 'high' else (1280, 720)
        
        else:
            format_type = StreamFormat.JSON
            sample_rate = None
            channels = None
            frame_rate = None
            resolution = None
        
        return StreamConfig(
            stream_type=stream_type,
            processing_mode=processing_mode,
            format=format_type,
            buffer_size=creator_config['buffer_size'],
            chunk_duration=0.1,
            sample_rate=sample_rate,
            channels=channels,
            frame_rate=frame_rate,
            resolution=resolution,
            quality=creator_config['quality'],
            compression=True,
            encryption=False,
            creator_type=creator_type
        )

# Instance globale
stream_transformer = StreamTransformer()

# Export des classes principales
__all__ = [
    'StreamTransformer',
    'AudioStreamProcessor',
    'VideoStreamProcessor',
    'WebSocketStreamProcessor',
    'KafkaStreamProcessor',
    'StreamConfig',
    'StreamProcessingResult',
    'StreamType',
    'ProcessingMode',
    'StreamFormat',
    'stream_transformer'
]
