"""IA Influencer Agent - Content Protection Service
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced content protection service orchestrating fingerprinting and monitoring
"""
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import mimetypes

from .audio_processor import AudioFingerprintProcessor, AudioFingerprint
from .video_processor import VideoFingerprintProcessor, VideoFingerprint
from .image_processor import ImageFingerprintProcessor, ImageFingerprint  
from .text_processor import TextFingerprintProcessor, TextFingerprint
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class ContentProtectionService:
    """
    Professional content protection service
    Orchestrates multi-format content fingerprinting, duplicate detection, and copyright protection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content protection service"""
        self.config = config or self._get_default_config()
        
        # Initialize processors
        self.audio_processor = AudioFingerprintProcessor(self.config.get('audio'))
        self.video_processor = VideoFingerprintProcessor(self.config.get('video'))
        self.image_processor = ImageFingerprintProcessor(self.config.get('image'))
        self.text_processor = TextFingerprintProcessor(self.config.get('text'))
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.config.get('database'))
        
        # Supported file types
        self.supported_extensions = {
            'audio': {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma'},
            'video': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'},
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
            'text': {'.txt', '.md', '.rtf', '.doc', '.docx', '.pdf'}
        }
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'similarity_threshold': 0.85,
            'batch_size': 50,
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'enable_parallel_processing': True,
            'duplicate_action': 'flag',  # 'flag', 'block', 'quarantine'
            'audio': {},
            'video': {},
            'image': {},
            'text': {},
            'database': {}
        }
    
    async def initialize(self):
        """Initialize the content protection service"""
        try:
            await self.db_manager.initialize()
            logger.info("Content protection service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize content protection service: {str(e)}")
            raise
    
    def get_content_type(self, file_path: Path) -> Optional[str]:
        """Determine content type from file extension"""
        extension = file_path.suffix.lower()
        
        for content_type, extensions in self.supported_extensions.items():
            if extension in extensions:
                return content_type
        
        # Fallback to MIME type detection
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('text/'):
                return 'text'
        
        return None
    
    async def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file for content protection
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Processing result with fingerprint ID and duplicate information
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.config['max_file_size']:
                raise ValueError(f"File too large: {file_size} bytes (max: {self.config['max_file_size']})")
            
            # Determine content type
            content_type = self.get_content_type(file_path)
            if not content_type:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            # Process file based on content type
            if content_type == 'audio':
                fingerprint = await self.audio_processor.process_audio_file(file_path)
                fingerprint_id = await self.db_manager.store_audio_fingerprint(fingerprint, file_path)
            elif content_type == 'video':
                fingerprint = await self.video_processor.process_video_file(file_path)
                fingerprint_id = await self.db_manager.store_video_fingerprint(fingerprint, file_path)
            elif content_type == 'image':
                fingerprint = await self.image_processor.process_image_file(file_path)
                fingerprint_id = await self.db_manager.store_image_fingerprint(fingerprint, file_path)
            elif content_type == 'text':
                fingerprint = await self.text_processor.process_text_file(file_path)
                fingerprint_id = await self.db_manager.store_text_fingerprint(fingerprint, file_path)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Find similar content
            similar_matches = await self.db_manager.find_similar_fingerprints(
                fingerprint, 
                self.config['similarity_threshold']
            )
            
            # Filter out self-match
            similar_matches = [(fid, score) for fid, score in similar_matches if fid != fingerprint_id]
            
            # Determine if content is a duplicate
            is_duplicate = len(similar_matches) > 0
            
            result = {
                'fingerprint_id': fingerprint_id,
                'content_type': content_type,
                'file_path': str(file_path),
                'content_hash': fingerprint.content_hash,
                'is_duplicate': is_duplicate,
                'similar_matches': similar_matches[:5],  # Top 5 matches
                'action_taken': self._determine_action(is_duplicate),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Store similarity matches for caching
            for match_id, similarity_score in similar_matches:
                await self.db_manager.store_similarity_match(
                    fingerprint_id, match_id, similarity_score, content_type
                )
            
            logger.info(f"Processed {file_path.name}: {'duplicate' if is_duplicate else 'original'}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def process_text_content(self, text_content: str, identifier: str = None) -> Dict[str, Any]:
        """
        Process text content for protection (without file)
        
        Args:
            text_content: Raw text content
            identifier: Optional identifier for the content
            
        Returns:
            Processing result with fingerprint ID and duplicate information
        """
        try:
            # Process text content
            fingerprint = await self.text_processor.process_text_content(text_content)
            fingerprint_id = await self.db_manager.store_text_fingerprint(fingerprint)
            
            # Find similar content
            similar_matches = await self.db_manager.find_similar_fingerprints(
                fingerprint, 
                self.config['similarity_threshold']
            )
            
            # Filter out self-match
            similar_matches = [(fid, score) for fid, score in similar_matches if fid != fingerprint_id]
            
            # Determine if content is a duplicate
            is_duplicate = len(similar_matches) > 0
            
            result = {
                'fingerprint_id': fingerprint_id,
                'content_type': 'text',
                'identifier': identifier,
                'content_hash': fingerprint.content_hash,
                'is_duplicate': is_duplicate,
                'similar_matches': similar_matches[:5],  # Top 5 matches
                'action_taken': self._determine_action(is_duplicate),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Store similarity matches for caching
            for match_id, similarity_score in similar_matches:
                await self.db_manager.store_similarity_match(
                    fingerprint_id, match_id, similarity_score, 'text'
                )
            
            logger.info(f"Processed text content: {'duplicate' if is_duplicate else 'original'}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing text content: {str(e)}")
            return {
                'identifier': identifier,
                'error': str(e),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
    
    async def batch_process_files(self, file_paths: List[Path], max_concurrent: int = None) -> List[Dict[str, Any]]:
        """
        Process multiple files concurrently
        
        Args:
            file_paths: List of file paths to process
            max_concurrent: Maximum concurrent processing tasks
            
        Returns:
            List of processing results
        """
        max_concurrent = max_concurrent or self.config.get('max_concurrent', 10)
        
        # Create semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.process_file(file_path)
        
        # Process files concurrently
        tasks = [process_with_semaphore(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'file_path': str(file_paths[i]),
                    'error': str(result),
                    'processed_at': datetime.now(timezone.utc).isoformat()
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def scan_directory(self, directory_path: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Scan directory for content protection
        
        Args:
            directory_path: Directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of processing results
        """
        try:
            if not directory_path.exists() or not directory_path.is_dir():
                raise ValueError(f"Invalid directory: {directory_path}")
            
            # Find all supported files
            file_paths = []
            
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in directory_path.glob(pattern):
                if file_path.is_file() and self.get_content_type(file_path):
                    file_paths.append(file_path)
            
            logger.info(f"Found {len(file_paths)} files to process in {directory_path}")
            
            # Process files in batches
            batch_size = self.config.get('batch_size', 50)
            all_results = []
            
            for i in range(0, len(file_paths), batch_size):
                batch = file_paths[i:i + batch_size]
                batch_results = await self.batch_process_files(batch)
                all_results.extend(batch_results)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory_path}: {str(e)}")
            return [{
                'directory': str(directory_path),
                'error': str(e),
                'processed_at': datetime.now(timezone.utc).isoformat()
            }]
    
    def _determine_action(self, is_duplicate: bool) -> str:
        """Determine action to take based on duplicate status"""
        if not is_duplicate:
            return 'allowed'
        
        action = self.config.get('duplicate_action', 'flag')
        
        if action == 'flag':
            return 'flagged_as_duplicate'
        elif action == 'block':
            return 'blocked_duplicate'
        elif action == 'quarantine':
            return 'quarantined_duplicate'
        else:
            return 'flagged_as_duplicate'
    
    async def get_protection_status(self, fingerprint_id: int) -> Dict[str, Any]:
        """Get protection status for a specific fingerprint"""
        try:
            fingerprint = await self.db_manager.get_fingerprint(fingerprint_id)
            if not fingerprint:
                return {'error': 'Fingerprint not found'}
            
            # Get similarity matches
            similarity_matches = await self.db_manager.get_similarity_matches(fingerprint_id)
            
            return {
                'fingerprint_id': fingerprint_id,
                'content_hash': fingerprint.content_hash,
                'similar_matches_count': len(similarity_matches),
                'similar_matches': similarity_matches[:10],  # Top 10 matches
                'protection_level': self._calculate_protection_level(len(similarity_matches))
            }
            
        except Exception as e:
            logger.error(f"Error getting protection status: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_protection_level(self, match_count: int) -> str:
        """Calculate protection level based on number of matches"""
        if match_count == 0:
            return 'original'
        elif match_count < 5:
            return 'low_risk'
        elif match_count < 20:
            return 'medium_risk'
        else:
            return 'high_risk'
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        try:
            db_stats = await self.db_manager.get_statistics()
            
            return {
                'service_name': 'IA Influencer Content Protection',
                'version': '1.0.0',
                'author': 'Fahed Mlaiel <mlaiel@live.de>',
                'database_stats': db_stats,
                'supported_formats': {
                    'audio': list(self.supported_extensions['audio']),
                    'video': list(self.supported_extensions['video']),
                    'image': list(self.supported_extensions['image']),
                    'text': list(self.supported_extensions['text'])
                },
                'configuration': {
                    'similarity_threshold': self.config['similarity_threshold'],
                    'max_file_size': self.config['max_file_size'],
                    'duplicate_action': self.config['duplicate_action']
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting service statistics: {str(e)}")
            return {'error': str(e)}
    
    async def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """Cleanup old protection data"""
        try:
            deleted_count = await self.db_manager.cleanup_old_records(days_to_keep)
            
            return {
                'cleaned_records': deleted_count,
                'days_kept': days_to_keep,
                'cleanup_date': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return {'error': str(e)}
    
    async def close(self):
        """Close the content protection service"""
        try:
            await self.db_manager.close()
            logger.info("Content protection service closed successfully")
        except Exception as e:
            logger.error(f"Error closing service: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
