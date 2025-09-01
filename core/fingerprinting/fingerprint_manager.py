"""IA Influencer Agent - Fingerprint Manager
Central management system for all fingerprinting operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .audio_fingerprint import AudioFingerprintEngine
from .video_fingerprint import VideoFingerprintEngine  
from .image_fingerprint import ImageFingerprintEngine

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """
Supported content types for fingerprinting"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class FingerprintRequest:
    """Request object for fingerprinting operations"""
    file_path: str
    content_type: ContentType
    methods: Optional[List[str]] = None
    priority: int = 1
    metadata: Optional[Dict] = None


@dataclass
class FingerprintResult:
    """
Result object for fingerprinting operations"""
    request_id: str
    file_path: str
    content_type: ContentType
    fingerprint_data: Dict
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class FingerprintManager:
    """
    Central manager for coordinating all fingerprinting operations
    across audio, video, and image content types
    """
    
    def __init__(self):
        """
Initialize the fingerprint manager with all engines"""
        self.audio_engine = AudioFingerprintEngine()
        self.video_engine = VideoFingerprintEngine()
        self.image_engine = ImageFingerprintEngine()
        
        # File extension mappings
        self.audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
        
        # Processing queue
        self.processing_queue = asyncio.Queue()
        self.results_cache = {}
        self.active_tasks = {}
        
        logger.info("FingerprintManager initialized with all engines")
    
    def detect_content_type(self, file_path: Union[str, Path]) -> ContentType:
        """
        Detect content type based on file extension
        
        Args:
            file_path: Path to the content file
        
        Returns:
            Detected content type
        """
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            
            if extension in self.audio_extensions:
                return ContentType.AUDIO
            elif extension in self.video_extensions:
                return ContentType.VIDEO
            elif extension in self.image_extensions:
                return ContentType.IMAGE
            else:
                return ContentType.UNKNOWN
                
        except Exception as e:
            logger.error(f"Error detecting content type: {str(e)}")
            return ContentType.UNKNOWN
    
    async def extract_fingerprint(
        self,
        file_path: Union[str, Path],
        content_type: Optional[ContentType] = None,
        methods: Optional[List[str]] = None,
        request_id: Optional[str] = None
    ) -> FingerprintResult:
        """
        Extract fingerprint from content file
        
        Args:
            file_path: Path to content file
            content_type: Type of content (auto-detected if None)
            methods: Specific methods to use for fingerprinting
            request_id: Unique identifier for this request
        
        Returns:
            FingerprintResult with extracted data
        """
        start_time = time.time()
        
        if request_id is None:
            request_id = f"fp_{int(time.time() * 1000)}"
        
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Auto-detect content type if not provided
            if content_type is None:
                content_type = self.detect_content_type(file_path)
                
            if content_type == ContentType.UNKNOWN:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            # Route to appropriate engine
            fingerprint_data = await self._route_to_engine(file_path, content_type, methods)
            
            # Add manager metadata
            fingerprint_data['manager_info'] = {
                'request_id': request_id,
                'content_type': content_type.value,
                'processing_engine': f"{content_type.value}_fingerprint_engine",
                'processing_time': time.time() - start_time,
                'processed_at': time.time()
            }
            
            result = FingerprintResult(
                request_id=request_id,
                file_path=str(file_path),
                content_type=content_type,
                fingerprint_data=fingerprint_data,
                processing_time=time.time() - start_time,
                success=True
            )
            
            # Cache result
            self.results_cache[request_id] = result
            
            logger.info(f"Successfully processed fingerprint request {request_id}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing fingerprint: {str(e)}"
            logger.error(error_msg)
            
            result = FingerprintResult(
                request_id=request_id,
                file_path=str(file_path),
                content_type=content_type or ContentType.UNKNOWN,
                fingerprint_data={},
                processing_time=time.time() - start_time,
                success=False,
                error_message=error_msg
            )
            
            return result
    
    async def _route_to_engine(
        self,
        file_path: Path,
        content_type: ContentType,
        methods: Optional[List[str]]
    ) -> Dict:
        """Route fingerprinting request to appropriate engine"""
        try:
            if content_type == ContentType.AUDIO:
                return await self.audio_engine.extract_fingerprint(file_path, methods)
            elif content_type == ContentType.VIDEO:
                return await self.video_engine.extract_fingerprint(file_path, methods)
            elif content_type == ContentType.IMAGE:
                return await self.image_engine.extract_fingerprint(file_path, methods)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error in engine routing: {str(e)}")
            raise
    
    async def batch_extract_fingerprints(
        self,
        file_paths: List[Union[str, Path]],
        methods_by_type: Optional[Dict[ContentType, List[str]]] = None
    ) -> List[FingerprintResult]:
        """
        Extract fingerprints from multiple files in batch
        
        Args:
            file_paths: List of file paths to process
            methods_by_type: Specific methods for each content type
        
        Returns:
            List of fingerprint results
        """
        try:
            # Group files by content type
            files_by_type = {
                ContentType.AUDIO: [],
                ContentType.VIDEO: [],
                ContentType.IMAGE: []
            }
            
            for file_path in file_paths:
                content_type = self.detect_content_type(file_path)
                if content_type != ContentType.UNKNOWN:
                    files_by_type[content_type].append(file_path)
            
            # Process each content type in parallel
            tasks = []
            
            for content_type, files in files_by_type.items():
                if files:
                    methods = methods_by_type.get(content_type) if methods_by_type else None
                    task = self._batch_process_type(files, content_type, methods)
                    tasks.append(task)
            
            # Wait for all tasks to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            all_results = []
            for result_group in batch_results:
                if isinstance(result_group, Exception):
                    logger.error(f"Batch processing error: {str(result_group)}")
                else:
                    all_results.extend(result_group)
            
            logger.info(f"Batch processed {len(all_results)} files")
            return all_results
            
        except Exception as e:
            logger.error(f"Error in batch fingerprinting: {str(e)}")
            raise
    
    async def _batch_process_type(
        self,
        file_paths: List[Union[str, Path]],
        content_type: ContentType,
        methods: Optional[List[str]]
    ) -> List[FingerprintResult]:
        """Process batch of files of same content type"""
        try:
            tasks = []
            for file_path in file_paths:
                task = self.extract_fingerprint(file_path, content_type, methods)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = FingerprintResult(
                        request_id=f"batch_error_{int(time.time() * 1000)}_{i}",
                        file_path=str(file_paths[i]),
                        content_type=content_type,
                        fingerprint_data={},
                        processing_time=0.0,
                        success=False,
                        error_message=str(result)
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch type processing: {str(e)}")
            raise
    
    async def compare_fingerprints(
        self,
        fingerprint1: FingerprintResult,
        fingerprint2: FingerprintResult
    ) -> Dict[str, float]:
        """
        Compare two fingerprints and return similarity scores
        
        Args:
            fingerprint1: First fingerprint result
            fingerprint2: Second fingerprint result
        
        Returns:
            Dictionary with similarity scores
        """
        try:
            if not fingerprint1.success or not fingerprint2.success:
                return {'overall': 0.0, 'error': 'One or both fingerprints failed'}
            
            if fingerprint1.content_type != fingerprint2.content_type:
                return {'overall': 0.0, 'error': 'Different content types'}
            
            # Route to appropriate engine for comparison
            content_type = fingerprint1.content_type
            
            if content_type == ContentType.AUDIO:
                return await self.audio_engine.compare_fingerprints(
                    fingerprint1.fingerprint_data,
                    fingerprint2.fingerprint_data
                )
            elif content_type == ContentType.VIDEO:
                return await self.video_engine.compare_fingerprints(
                    fingerprint1.fingerprint_data,
                    fingerprint2.fingerprint_data
                )
            elif content_type == ContentType.IMAGE:
                return await self.image_engine.compare_fingerprints(
                    fingerprint1.fingerprint_data,
                    fingerprint2.fingerprint_data
                )
            else:
                return {'overall': 0.0, 'error': f'Unsupported content type: {content_type}'}
                
        except Exception as e:
            logger.error(f"Error comparing fingerprints: {str(e)}")
            return {'overall': 0.0, 'error': str(e)}
    
    async def find_similar_content(
        self,
        target_fingerprint: FingerprintResult,
        candidate_fingerprints: List[FingerprintResult],
        similarity_threshold: float = 0.8
    ) -> List[Tuple[FingerprintResult, float]]:
        """
        Find similar content from a list of candidates
        
        Args:
            target_fingerprint: Target fingerprint to match against
            candidate_fingerprints: List of candidate fingerprints
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of tuples (fingerprint, similarity_score) sorted by similarity
        """
        try:
            similar_results = []
            
            # Compare target with each candidate
            for candidate in candidate_fingerprints:
                if candidate.content_type == target_fingerprint.content_type:
                    similarity_scores = await self.compare_fingerprints(target_fingerprint, candidate)
                    overall_similarity = similarity_scores.get('overall', 0.0)
                    
                    if overall_similarity >= similarity_threshold:
                        similar_results.append((candidate, overall_similarity))
            
            # Sort by similarity score (descending)
            similar_results.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Found {len(similar_results)} similar items above threshold {similarity_threshold}")
            return similar_results
            
        except Exception as e:
            logger.error(f"Error finding similar content: {str(e)}")
            return []
    
    def get_cached_result(self, request_id: str) -> Optional[FingerprintResult]:
        """Get cached fingerprint result by request ID"""
        return self.results_cache.get(request_id)
    
    def clear_cache(self, older_than_hours: Optional[int] = None):
        """
Clear results cache, optionally only entries older than specified hours"""
        try:
            if older_than_hours is None:
                # Clear all cache
                self.results_cache.clear()
                logger.info("Cleared all cached results")
            else:
                # Clear entries older than specified time
                cutoff_time = time.time() - (older_than_hours * 3600)
                expired_keys = []
                
                for request_id, result in self.results_cache.items():
                    processed_at = result.fingerprint_data.get('manager_info', {}).get('processed_at', 0)
                    if processed_at < cutoff_time:
                        expired_keys.append(request_id)
                
                for key in expired_keys:
                    del self.results_cache[key]
                
                logger.info(f"Cleared {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
    
    def export_fingerprint(self, result: FingerprintResult, file_path: Union[str, Path]) -> bool:
        """
        Export fingerprint result to JSON file
        
        Args:
            result: Fingerprint result to export
            file_path: Output file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            output_data = {
                'request_id': result.request_id,
                'file_path': result.file_path,
                'content_type': result.content_type.value,
                'fingerprint_data': result.fingerprint_data,
                'processing_time': result.processing_time,
                'success': result.success,
                'error_message': result.error_message,
                'exported_at': time.time()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported fingerprint to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting fingerprint: {str(e)}")
            return False
    
    def import_fingerprint(self, file_path: Union[str, Path]) -> Optional[FingerprintResult]:
        """
        Import fingerprint result from JSON file
        
        Args:
            file_path: Input file path
        
        Returns:
            FingerprintResult if successful, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            result = FingerprintResult(
                request_id=data['request_id'],
                file_path=data['file_path'],
                content_type=ContentType(data['content_type']),
                fingerprint_data=data['fingerprint_data'],
                processing_time=data['processing_time'],
                success=data['success'],
                error_message=data.get('error_message')
            )
            
            # Add to cache
            self.results_cache[result.request_id] = result
            
            logger.info(f"Imported fingerprint from {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error importing fingerprint: {str(e)}")
            return None
    
    def get_manager_stats(self) -> Dict[str, any]:
        """Get statistics about the fingerprint manager"""
        try:
            cache_stats = {
                'total_cached': len(self.results_cache),
                'successful': sum(1 for r in self.results_cache.values() if r.success),
                'failed': sum(1 for r in self.results_cache.values() if not r.success)
            }
            
            content_type_stats = {
                'audio': sum(1 for r in self.results_cache.values() if r.content_type == ContentType.AUDIO),
                'video': sum(1 for r in self.results_cache.values() if r.content_type == ContentType.VIDEO),
                'image': sum(1 for r in self.results_cache.values() if r.content_type == ContentType.IMAGE)
            }
            
            return {
                'manager': 'FingerprintManager',
                'version': '1.0.0',
                'cache_stats': cache_stats,
                'content_type_stats': content_type_stats,
                'active_tasks': len(self.active_tasks),
                'supported_content_types': [ct.value for ct in ContentType if ct != ContentType.UNKNOWN],
                'supported_extensions': {
                    'audio': list(self.audio_extensions),
                    'video': list(self.video_extensions),
                    'image': list(self.image_extensions)
                },
                'engines': {
                    'audio': self.audio_engine.get_engine_info(),
                    'video': self.video_engine.get_engine_info(),
                    'image': self.image_engine.get_engine_info()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting manager stats: {str(e)}")
            return {'error': str(e)}
