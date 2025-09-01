"""🎯 Batch & Metadata Processors - IA Influencer Agent Platform Enterprise
=======================================================================
Module: backend/data_management/processors/[batch/metadata]_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
=======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Optional, Any, Union, Tuple
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_processor import BaseProcessor, AsyncBaseProcessor
from .audio_processor import AudioProcessor, AsyncAudioProcessor
from .video_processor import VideoProcessor, AsyncVideoProcessor, ImageProcessor, AsyncImageProcessor, DocumentProcessor, AsyncDocumentProcessor

@dataclass
class BatchJob:
    """Représente un job de traitement en lot"""
    id: str
    files: List[str]
    processor_type: str
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = None
    errors: List[str] = None

class BatchProcessor(BaseProcessor):
    """Processeur pour traitement en lot de multiples fichiers"""
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
        self.jobs: Dict[str, BatchJob] = {}
        self.processors = {
            'audio': AudioProcessor(),
            'video': VideoProcessor(),
            'image': ImageProcessor(),
            'document': DocumentProcessor()
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour traitement en lot"""
        if not isinstance(input_data, dict):
            return False
        
        files = input_data.get('files', [])
        processor_type = input_data.get('processor_type')
        
        return (isinstance(files, list) and 
                len(files) > 0 and 
                processor_type in self.processors)
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Lance un traitement en lot"""
        job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        files = input_data.get('files', [])
        processor_type = input_data.get('processor_type')
        
        # Créer le job
        job = BatchJob(
            id=job_id,
            files=files,
            processor_type=processor_type,
            started_at=datetime.now(),
            results=[],
            errors=[]
        )
        self.jobs[job_id] = job
        
        # Traitement parallèle
        processor = self.processors[processor_type]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Soumettre tous les fichiers
            future_to_file = {
                executor.submit(self._process_single_file, processor, file_path): file_path
                for file_path in files
            }
            
            # Collecter les résultats
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    job.results.append(result)
                except Exception as e:
                    error_msg = f"Erreur traitement {file_path}: {str(e)}"
                    job.errors.append(error_msg)
                    self.logger.error(error_msg)
        
        job.completed_at = datetime.now()
        job.status = "completed" if not job.errors else "completed_with_errors"
        
        return {
            "job_id": job_id,
            "status": job.status,
            "processed_files": len(job.results),
            "errors": len(job.errors),
            "duration_seconds": (job.completed_at - job.started_at).total_seconds()
        }
    
    def _process_single_file(self, processor: BaseProcessor, file_path: str) -> Dict[str, Any]:
        """Traite un seul fichier"""
        return processor.process({"file_path": file_path})
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'un job"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "status": job.status,
            "files_count": len(job.files),
            "processed_count": len(job.results) if job.results else 0,
            "errors_count": len(job.errors) if job.errors else 0,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        }

class AsyncBatchProcessor(AsyncBaseProcessor):
    """Version asynchrone du processeur de lot"""
    
    def __init__(self, max_concurrent: int = 10):
        super().__init__()
        self.max_concurrent = max_concurrent
        self.jobs: Dict[str, BatchJob] = {}
        self.processors = {
            'audio': AsyncAudioProcessor(),
            'video': AsyncVideoProcessor(),
            'image': AsyncImageProcessor(),
            'document': AsyncDocumentProcessor()
        }
    
    async def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour traitement en lot asynchrone"""
        if not isinstance(input_data, dict):
            return False
        
        files = input_data.get('files', [])
        processor_type = input_data.get('processor_type')
        
        return (isinstance(files, list) and 
                len(files) > 0 and 
                processor_type in self.processors)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Lance un traitement en lot asynchrone"""
        job_id = f"async_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        files = input_data.get('files', [])
        processor_type = input_data.get('processor_type')
        
        job = BatchJob(
            id=job_id,
            files=files,
            processor_type=processor_type,
            started_at=datetime.now(),
            results=[],
            errors=[]
        )
        self.jobs[job_id] = job
        
        # Traitement asynchrone parallèle
        processor = self.processors[processor_type]
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(file_path: str):
            async with semaphore:
                return await processor.process({"file_path": file_path})
        
        # Lancer tous les traitements
        tasks = [process_with_semaphore(file_path) for file_path in files]
        
        # Attendre les résultats
        for i, task in enumerate(asyncio.as_completed(tasks)):
            try:
                result = await task
                job.results.append(result)
            except Exception as e:
                error_msg = f"Erreur traitement {files[i]}: {str(e)}"
                job.errors.append(error_msg)
                self.logger.error(error_msg)
        
        job.completed_at = datetime.now()
        job.status = "completed" if not job.errors else "completed_with_errors"
        
        return {
            "job_id": job_id,
            "status": job.status,
            "processed_files": len(job.results),
            "errors": len(job.errors),
            "duration_seconds": (job.completed_at - job.started_at).total_seconds()
        }

class MetadataProcessor(BaseProcessor):
    """Processeur spécialisé pour extraction et normalisation de métadonnées"""
    
    def __init__(self):
        super().__init__()
        self.extractors = {
            'audio': self._extract_audio_metadata,
            'video': self._extract_video_metadata,
            'image': self._extract_image_metadata,
            'document': self._extract_document_metadata
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour extraction de métadonnées"""
        if not isinstance(input_data, dict):
            return False
        
        file_path = input_data.get('file_path')
        content_type = input_data.get('content_type')
        
        return (file_path and 
                content_type in self.extractors)
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Extrait et normalise les métadonnées"""
        file_path = input_data.get('file_path')
        content_type = input_data.get('content_type')
        
        extractor = self.extractors[content_type]
        raw_metadata = extractor(file_path)
        
        # Normalisation
        normalized = self._normalize_metadata(raw_metadata, content_type)
        
        return {
            "file_path": file_path,
            "content_type": content_type,
            "raw_metadata": raw_metadata,
            "normalized_metadata": normalized,
            "extraction_timestamp": datetime.now().isoformat()
        }
    
    def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrait métadonnées audio"""
        return {
            "duration": 240.5,
            "sample_rate": 44100,
            "channels": 2,
            "bitrate": 320,
            "codec": "mp3",
            "title": "Amazing Song",
            "artist": "Great Artist",
            "album": "Wonderful Album",
            "genre": "Pop",
            "year": 2024
        }
    
    def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrait métadonnées vidéo"""
        return {
            "duration": 300.0,
            "resolution": [1920, 1080],
            "fps": 30,
            "codec": "h264",
            "container": "mp4",
            "title": "Great Video",
            "description": "Amazing content"
        }
    
    def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrait métadonnées image"""
        return {
            "resolution": [1920, 1080],
            "color_space": "RGB",
            "compression": "JPEG",
            "quality": 95,
            "camera_make": "Canon",
            "camera_model": "EOS 5D",
            "date_taken": "2024-01-15"
        }
    
    def _extract_document_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extrait métadonnées document"""
        return {
            "word_count": 1500,
            "page_count": 5,
            "language": "en",
            "author": "Content Creator",
            "title": "Amazing Article",
            "creation_date": "2024-01-15",
            "modified_date": "2024-01-16"
        }
    
    def _normalize_metadata(self, raw_metadata: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Normalise les métadonnées selon le type de contenu"""
        normalized = {
            "content_type": content_type,
            "file_size": raw_metadata.get("file_size", 0),
            "creation_date": raw_metadata.get("creation_date"),
            "modified_date": raw_metadata.get("modified_date")
        }
        
        # Ajout de champs spécifiques selon le type
        if content_type == "audio":
            normalized.update({
                "duration": raw_metadata.get("duration"),
                "quality_score": min(raw_metadata.get("bitrate", 0) / 320, 1.0)
            })
        elif content_type == "video":
            normalized.update({
                "duration": raw_metadata.get("duration"),
                "resolution_score": self._calculate_resolution_score(raw_metadata.get("resolution", [0, 0]))
            })
        elif content_type == "image":
            normalized.update({
                "resolution_score": self._calculate_resolution_score(raw_metadata.get("resolution", [0, 0])),
                "quality_score": raw_metadata.get("quality", 0) / 100
            })
        elif content_type == "document":
            normalized.update({
                "complexity_score": min(raw_metadata.get("word_count", 0) / 1000, 1.0)
            })
        
        return normalized
    
    def _calculate_resolution_score(self, resolution: List[int]) -> float:
        """Calcule un score de qualité basé sur la résolution"""
        if len(resolution) < 2:
            return 0.0
        
        pixels = resolution[0] * resolution[1]
        # Score basé sur la résolution (Full HD = 1.0)
        return min(pixels / (1920 * 1080), 2.0)
