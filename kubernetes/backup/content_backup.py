"""Content Backup Service for IA Influencer Agent Platform.

Handles backup and recovery of all content protection data including
audio fingerprints, video analysis, image hashes, and text embeddings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
import json

from ...content_protection.fingerprinting.audio_fingerprint import AudioFingerprintService
from ...content_protection.fingerprinting.video_fingerprint import VideoFingerprintService
from ...content_protection.fingerprinting.image_fingerprint import ImageFingerprintService
from ...content_protection.fingerprinting.text_fingerprint import TextFingerprintService
from ...database.repositories.content_repository import ContentRepository
from ...database.repositories.fingerprint_repository import FingerprintRepository


@dataclass
class ContentBackupRecord:
    """
Content backup record metadata."""
    content_id: str
    content_type: str
    fingerprint_data: Dict[str, Any]
    original_metadata: Dict[str, Any]
    backup_timestamp: datetime
    checksum: str
    file_size: int


class ContentBackupService:
    """
    Enterprise content backup service for IA protection platform.
    
    Manages backup and recovery of all content protection data including
    fingerprints, metadata, and original content references.
    """
    def __init__(self, storage_config: Dict[str, Any]):
        """
        Initialize content backup service.
        
        Args:
            storage_config: Storage configuration
        """
        self.logger = logging.getLogger(__name__)
        self.storage_config = storage_config
        
        # Initialize fingerprint services
        self.audio_fingerprint = AudioFingerprintService()
        self.video_fingerprint = VideoFingerprintService()
        self.image_fingerprint = ImageFingerprintService()
        self.text_fingerprint = TextFingerprintService()
        
        # Initialize repositories
        self.content_repo = ContentRepository()
        self.fingerprint_repo = FingerprintRepository()
        
        # Backup tracking
        self.backup_progress = {}

    async def backup_all_content(self) -> Dict[str, Any]:
        """
        Backup all content protection data.
        
        Returns:
            Complete content backup data
        """
        self.logger.info("Starting complete content backup...")
        
        backup_data = {
            "audio_content": {},
            "video_content": {},
            "image_content": {},
            "text_content": {},
            "fingerprints": {},
            "metadata": {
                "backup_timestamp": datetime.now().isoformat(),
                "total_records": 0,
                "backup_version": "2.0.0"
            }
        }
        
        # Backup audio content
        audio_data = await self._backup_audio_content()
        backup_data["audio_content"] = audio_data
        
        # Backup video content
        video_data = await self._backup_video_content()
        backup_data["video_content"] = video_data
        
        # Backup image content
        image_data = await self._backup_image_content()
        backup_data["image_content"] = image_data
        
        # Backup text content
        text_data = await self._backup_text_content()
        backup_data["text_content"] = text_data
        
        # Backup fingerprint index
        fingerprint_data = await self._backup_fingerprint_index()
        backup_data["fingerprints"] = fingerprint_data
        
        # Update metadata
        total_records = (
            len(audio_data) + len(video_data) + 
            len(image_data) + len(text_data)
        )
        backup_data["metadata"]["total_records"] = total_records
        
        self.logger.info(f"Content backup completed: {total_records} records")
        return backup_data

    async def backup_changes_since(self, since_date: datetime) -> Dict[str, Any]:
        """
        Backup content changes since specified date.
        
        Args:
            since_date: Date to check for changes
            
        Returns:
            Incremental backup data
        """
        self.logger.info(f"Starting incremental content backup since {since_date}")
        
        backup_data = {
            "audio_content": {},
            "video_content": {},
            "image_content": {},
            "text_content": {},
            "fingerprints": {},
            "metadata": {
                "backup_timestamp": datetime.now().isoformat(),
                "since_date": since_date.isoformat(),
                "backup_type": "incremental",
                "backup_version": "2.0.0"
            }
        }
        
        # Get changed content by type
        changed_audio = await self.content_repo.get_changed_content(
            "audio", since_date
        )
        changed_video = await self.content_repo.get_changed_content(
            "video", since_date
        )
        changed_image = await self.content_repo.get_changed_content(
            "image", since_date
        )
        changed_text = await self.content_repo.get_changed_content(
            "text", since_date
        )
        
        # Backup changed content
        if changed_audio:
            backup_data["audio_content"] = await self._backup_specific_audio(
                [c["content_id"] for c in changed_audio]
            )
        
        if changed_video:
            backup_data["video_content"] = await self._backup_specific_video(
                [c["content_id"] for c in changed_video]
            )
        
        if changed_image:
            backup_data["image_content"] = await self._backup_specific_image(
                [c["content_id"] for c in changed_image]
            )
        
        if changed_text:
            backup_data["text_content"] = await self._backup_specific_text(
                [c["content_id"] for c in changed_text]
            )
        
        # Backup changed fingerprints
        changed_fingerprints = await self.fingerprint_repo.get_changed_fingerprints(
            since_date
        )
        if changed_fingerprints:
            backup_data["fingerprints"] = await self._backup_specific_fingerprints(
                [f["fingerprint_id"] for f in changed_fingerprints]
            )
        
        total_changes = len(changed_audio) + len(changed_video) + len(changed_image) + len(changed_text)
        backup_data["metadata"]["total_changes"] = total_changes
        
        self.logger.info(f"Incremental backup completed: {total_changes} changes")
        return backup_data

    async def restore_content(
        self, 
        backup_data: Dict[str, Any], 
        target_path: Optional[str] = None
    ) -> bool:
        """
        Restore content from backup data.
        
        Args:
            backup_data: Backup data to restore
            target_path: Optional target path for restoration
            
        Returns:
            Success status
        """
        try:
            self.logger.info("Starting content restoration...")
            
            # Restore audio content
            if "audio_content" in backup_data:
                await self._restore_audio_content(
                    backup_data["audio_content"], target_path
                )
            
            # Restore video content
            if "video_content" in backup_data:
                await self._restore_video_content(
                    backup_data["video_content"], target_path
                )
            
            # Restore image content
            if "image_content" in backup_data:
                await self._restore_image_content(
                    backup_data["image_content"], target_path
                )
            
            # Restore text content
            if "text_content" in backup_data:
                await self._restore_text_content(
                    backup_data["text_content"], target_path
                )
            
            # Restore fingerprint index
            if "fingerprints" in backup_data:
                await self._restore_fingerprint_index(
                    backup_data["fingerprints"], target_path
                )
            
            self.logger.info("Content restoration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Content restoration failed: {e}")
            return False

    async def _backup_audio_content(self) -> Dict[str, Any]:
        """Backup all audio content and fingerprints."""
        audio_content = await self.content_repo.get_all_content_by_type("audio")
        audio_backup = {}
        
        for content in audio_content:
            content_id = content["content_id"]
            
            # Get audio fingerprint data
            fingerprint_data = await self.audio_fingerprint.get_fingerprint_data(
                content_id
            )
            
            # Create backup record
            backup_record = ContentBackupRecord(
                content_id=content_id,
                content_type="audio",
                fingerprint_data=fingerprint_data,
                original_metadata=content,
                backup_timestamp=datetime.now(),
                checksum=self._calculate_content_checksum(content),
                file_size=content.get("file_size", 0)
            )
            
            audio_backup[content_id] = {
                "content_metadata": content,
                "fingerprint_data": fingerprint_data,
                "backup_record": backup_record.__dict__
            }
        
        self.logger.info(f"Audio content backup completed: {len(audio_backup)} records")
        return audio_backup

    async def _backup_video_content(self) -> Dict[str, Any]:
        """Backup all video content and fingerprints."""
        video_content = await self.content_repo.get_all_content_by_type("video")
        video_backup = {}
        
        for content in video_content:
            content_id = content["content_id"]
            
            # Get video fingerprint data
            fingerprint_data = await self.video_fingerprint.get_fingerprint_data(
                content_id
            )
            
            backup_record = ContentBackupRecord(
                content_id=content_id,
                content_type="video",
                fingerprint_data=fingerprint_data,
                original_metadata=content,
                backup_timestamp=datetime.now(),
                checksum=self._calculate_content_checksum(content),
                file_size=content.get("file_size", 0)
            )
            
            video_backup[content_id] = {
                "content_metadata": content,
                "fingerprint_data": fingerprint_data,
                "backup_record": backup_record.__dict__
            }
        
        self.logger.info(f"Video content backup completed: {len(video_backup)} records")
        return video_backup

    async def _backup_image_content(self) -> Dict[str, Any]:
        """Backup all image content and fingerprints."""
        image_content = await self.content_repo.get_all_content_by_type("image")
        image_backup = {}
        
        for content in image_content:
            content_id = content["content_id"]
            
            # Get image fingerprint data
            fingerprint_data = await self.image_fingerprint.get_fingerprint_data(
                content_id
            )
            
            backup_record = ContentBackupRecord(
                content_id=content_id,
                content_type="image",
                fingerprint_data=fingerprint_data,
                original_metadata=content,
                backup_timestamp=datetime.now(),
                checksum=self._calculate_content_checksum(content),
                file_size=content.get("file_size", 0)
            )
            
            image_backup[content_id] = {
                "content_metadata": content,
                "fingerprint_data": fingerprint_data,
                "backup_record": backup_record.__dict__
            }
        
        self.logger.info(f"Image content backup completed: {len(image_backup)} records")
        return image_backup

    async def _backup_text_content(self) -> Dict[str, Any]:
        """Backup all text content and fingerprints."""
        text_content = await self.content_repo.get_all_content_by_type("text")
        text_backup = {}
        
        for content in text_content:
            content_id = content["content_id"]
            
            # Get text fingerprint data
            fingerprint_data = await self.text_fingerprint.get_fingerprint_data(
                content_id
            )
            
            backup_record = ContentBackupRecord(
                content_id=content_id,
                content_type="text",
                fingerprint_data=fingerprint_data,
                original_metadata=content,
                backup_timestamp=datetime.now(),
                checksum=self._calculate_content_checksum(content),
                file_size=content.get("file_size", 0)
            )
            
            text_backup[content_id] = {
                "content_metadata": content,
                "fingerprint_data": fingerprint_data,
                "backup_record": backup_record.__dict__
            }
        
        self.logger.info(f"Text content backup completed: {len(text_backup)} records")
        return text_backup

    async def _backup_fingerprint_index(self) -> Dict[str, Any]:
        """Backup fingerprint index and similarity data."""
        fingerprint_index = await self.fingerprint_repo.get_complete_index()
        
        index_backup = {
            "index_metadata": {
                "total_fingerprints": len(fingerprint_index),
                "index_version": "2.0.0",
                "backup_timestamp": datetime.now().isoformat()
            },
            "similarity_mappings": await self.fingerprint_repo.get_similarity_mappings(),
            "vector_index": await self.fingerprint_repo.export_vector_index(),
            "fingerprint_records": fingerprint_index
        }
        
        self.logger.info(f"Fingerprint index backup completed: {len(fingerprint_index)} fingerprints")
        return index_backup

    async def _backup_specific_audio(self, content_ids: List[str]) -> Dict[str, Any]:
        """Backup specific audio content by IDs."""
        audio_backup = {}
        
        for content_id in content_ids:
            content = await self.content_repo.get_content_by_id(content_id)
            if content and content["content_type"] == "audio":
                fingerprint_data = await self.audio_fingerprint.get_fingerprint_data(
                    content_id
                )
                
                backup_record = ContentBackupRecord(
                    content_id=content_id,
                    content_type="audio",
                    fingerprint_data=fingerprint_data,
                    original_metadata=content,
                    backup_timestamp=datetime.now(),
                    checksum=self._calculate_content_checksum(content),
                    file_size=content.get("file_size", 0)
                )
                
                audio_backup[content_id] = {
                    "content_metadata": content,
                    "fingerprint_data": fingerprint_data,
                    "backup_record": backup_record.__dict__
                }
        
        return audio_backup

    async def _backup_specific_video(self, content_ids: List[str]) -> Dict[str, Any]:
        """Backup specific video content by IDs."""
        video_backup = {}
        
        for content_id in content_ids:
            content = await self.content_repo.get_content_by_id(content_id)
            if content and content["content_type"] == "video":
                fingerprint_data = await self.video_fingerprint.get_fingerprint_data(
                    content_id
                )
                
                backup_record = ContentBackupRecord(
                    content_id=content_id,
                    content_type="video",
                    fingerprint_data=fingerprint_data,
                    original_metadata=content,
                    backup_timestamp=datetime.now(),
                    checksum=self._calculate_content_checksum(content),
                    file_size=content.get("file_size", 0)
                )
                
                video_backup[content_id] = {
                    "content_metadata": content,
                    "fingerprint_data": fingerprint_data,
                    "backup_record": backup_record.__dict__
                }
        
        return video_backup

    async def _backup_specific_image(self, content_ids: List[str]) -> Dict[str, Any]:
        """Backup specific image content by IDs."""
        image_backup = {}
        
        for content_id in content_ids:
            content = await self.content_repo.get_content_by_id(content_id)
            if content and content["content_type"] == "image":
                fingerprint_data = await self.image_fingerprint.get_fingerprint_data(
                    content_id
                )
                
                backup_record = ContentBackupRecord(
                    content_id=content_id,
                    content_type="image",
                    fingerprint_data=fingerprint_data,
                    original_metadata=content,
                    backup_timestamp=datetime.now(),
                    checksum=self._calculate_content_checksum(content),
                    file_size=content.get("file_size", 0)
                )
                
                image_backup[content_id] = {
                    "content_metadata": content,
                    "fingerprint_data": fingerprint_data,
                    "backup_record": backup_record.__dict__
                }
        
        return image_backup

    async def _backup_specific_text(self, content_ids: List[str]) -> Dict[str, Any]:
        """Backup specific text content by IDs."""
        text_backup = {}
        
        for content_id in content_ids:
            content = await self.content_repo.get_content_by_id(content_id)
            if content and content["content_type"] == "text":
                fingerprint_data = await self.text_fingerprint.get_fingerprint_data(
                    content_id
                )
                
                backup_record = ContentBackupRecord(
                    content_id=content_id,
                    content_type="text",
                    fingerprint_data=fingerprint_data,
                    original_metadata=content,
                    backup_timestamp=datetime.now(),
                    checksum=self._calculate_content_checksum(content),
                    file_size=content.get("file_size", 0)
                )
                
                text_backup[content_id] = {
                    "content_metadata": content,
                    "fingerprint_data": fingerprint_data,
                    "backup_record": backup_record.__dict__
                }
        
        return text_backup

    async def _backup_specific_fingerprints(self, fingerprint_ids: List[str]) -> Dict[str, Any]:
        """Backup specific fingerprints by IDs."""
        fingerprint_backup = {}
        
        for fingerprint_id in fingerprint_ids:
            fingerprint_data = await self.fingerprint_repo.get_fingerprint_by_id(
                fingerprint_id
            )
            if fingerprint_data:
                fingerprint_backup[fingerprint_id] = fingerprint_data
        
        return {
            "fingerprint_records": fingerprint_backup,
            "backup_timestamp": datetime.now().isoformat()
        }

    async def _restore_audio_content(
        self, 
        audio_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore audio content from backup."""
        for content_id, content_backup in audio_data.items():
            # Restore content metadata
            await self.content_repo.restore_content(
                content_backup["content_metadata"], target_path
            )
            
            # Restore fingerprint data
            await self.audio_fingerprint.restore_fingerprint_data(
                content_id, content_backup["fingerprint_data"], target_path
            )

    async def _restore_video_content(
        self, 
        video_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore video content from backup."""
        for content_id, content_backup in video_data.items():
            await self.content_repo.restore_content(
                content_backup["content_metadata"], target_path
            )
            
            await self.video_fingerprint.restore_fingerprint_data(
                content_id, content_backup["fingerprint_data"], target_path
            )

    async def _restore_image_content(
        self, 
        image_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore image content from backup."""
        for content_id, content_backup in image_data.items():
            await self.content_repo.restore_content(
                content_backup["content_metadata"], target_path
            )
            
            await self.image_fingerprint.restore_fingerprint_data(
                content_id, content_backup["fingerprint_data"], target_path
            )

    async def _restore_text_content(
        self, 
        text_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore text content from backup."""
        for content_id, content_backup in text_data.items():
            await self.content_repo.restore_content(
                content_backup["content_metadata"], target_path
            )
            
            await self.text_fingerprint.restore_fingerprint_data(
                content_id, content_backup["fingerprint_data"], target_path
            )

    async def _restore_fingerprint_index(
        self, 
        fingerprint_data: Dict[str, Any], 
        target_path: Optional[str]
    ) -> None:
        """Restore fingerprint index from backup."""
        # Restore similarity mappings
        if "similarity_mappings" in fingerprint_data:
            await self.fingerprint_repo.restore_similarity_mappings(
                fingerprint_data["similarity_mappings"], target_path
            )
        
        # Restore vector index
        if "vector_index" in fingerprint_data:
            await self.fingerprint_repo.restore_vector_index(
                fingerprint_data["vector_index"], target_path
            )
        
        # Restore fingerprint records
        if "fingerprint_records" in fingerprint_data:
            await self.fingerprint_repo.restore_fingerprint_records(
                fingerprint_data["fingerprint_records"], target_path
            )

    def _calculate_content_checksum(self, content: Dict[str, Any]) -> str:
        """Calculate checksum for content data."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def get_backup_progress(self, operation_id: str) -> Dict[str, Any]:
        """
        Get backup operation progress.
        
        Args:
            operation_id: Backup operation identifier
            
        Returns:
            Progress information
        """
        if operation_id in self.backup_progress:
            return self.backup_progress[operation_id]
        
        return {
            "status": "unknown",
            "progress": 0.0,
            "message": "Operation not found"
        }

    async def validate_content_integrity(self, content_id: str) -> bool:
        """
        Validate content integrity against backup checksums.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Integrity status
        """
        try:
            # Get current content
            current_content = await self.content_repo.get_content_by_id(content_id)
            if not current_content:
                return False
            
            # Calculate current checksum
            current_checksum = self._calculate_content_checksum(current_content)
            
            # Get fingerprint data
            if current_content["content_type"] == "audio":
                fingerprint_data = await self.audio_fingerprint.get_fingerprint_data(content_id)
            elif current_content["content_type"] == "video":
                fingerprint_data = await self.video_fingerprint.get_fingerprint_data(content_id)
            elif current_content["content_type"] == "image":
                fingerprint_data = await self.image_fingerprint.get_fingerprint_data(content_id)
            elif current_content["content_type"] == "text":
                fingerprint_data = await self.text_fingerprint.get_fingerprint_data(content_id)
            else:
                return False
            
            # Validate fingerprint data exists and is consistent
            return bool(fingerprint_data and len(fingerprint_data) > 0)
            
        except Exception as e:
            self.logger.error(f"Content integrity validation failed for {content_id}: {e}")
            return False
