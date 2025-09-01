# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test Content Handler Module

Tests for multi-format content processing, validation, and fingerprint preparation.

Author: Fahed Mlaiel (Legal Copyright)
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.
Propriété intellectuelle protégée sous toutes juridictions.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import hashlib
from PIL import Image
import numpy as np

from crawlers.handlers.content_handler import (
    ContentTypeDetector,
    ContentProcessor,
    ContentHandler,
    ContentMetadata,
    AudioMetadata,
    VideoMetadata,
    ImageMetadata,
    TextMetadata,
    ProcessingResult,
    create_content_handler
)


class TestContentTypeDetector:
    """Test suite for ContentTypeDetector class."""
    def test_init(self):
        """Test detector initialization."""
        detector = ContentTypeDetector()
        assert detector.supported_types == {
            'audio': ['mp3', 'wav', 'flac', 'm4a', 'aac', 'ogg'],
            'video': ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
            'text': ['txt', 'md', 'doc', 'docx', 'pdf', 'rtf']
        }

    def test_get_file_type_by_extension(self):
        """Test file type detection by extension."""
        detector = ContentTypeDetector()
        
        assert detector.get_file_type('test.mp3') == 'audio'
        assert detector.get_file_type('video.mp4') == 'video'
        assert detector.get_file_type('image.jpg') == 'image'
        assert detector.get_file_type('document.txt') == 'text'
        assert detector.get_file_type('unknown.xyz') == 'unknown'

    def test_get_file_type_case_insensitive(self):
        """Test case insensitive file type detection."""
        detector = ContentTypeDetector()
        
        assert detector.get_file_type('TEST.MP3') == 'audio'
        assert detector.get_file_type('Video.MP4') == 'video'
        assert detector.get_file_type('IMAGE.JPG') == 'image'

    def test_get_file_type_with_path(self):
        """Test file type detection with full path."""
        detector = ContentTypeDetector()
        
        assert detector.get_file_type('/path/to/file.mp3') == 'audio'
        assert detector.get_file_type('C:\\Users\\test\\video.mp4') == 'video'

    @patch('magic.from_file')
    def test_detect_by_magic_bytes(self, mock_magic):
        """Test MIME type detection using magic bytes."""
        mock_magic.return_value = 'audio/mpeg'
        detector = ContentTypeDetector()
        
        with tempfile.NamedTemporaryFile() as tmp:
            mime_type = detector.detect_by_magic_bytes(tmp.name)
            assert mime_type == 'audio/mpeg'

    def test_is_supported(self):
        """Test supported file type checking."""
        detector = ContentTypeDetector()
        
        assert detector.is_supported('audio', 'mp3')
        assert detector.is_supported('video', 'mp4')
        assert detector.is_supported('image', 'jpg')
        assert detector.is_supported('text', 'txt')
        assert not detector.is_supported('audio', 'xyz')

    @patch('magic.from_file')
    def test_validate_file(self, mock_magic):
        """Test comprehensive file validation."""
        mock_magic.return_value = 'audio/mpeg'
        detector = ContentTypeDetector()
        
        with tempfile.NamedTemporaryFile(suffix='.mp3') as tmp:
            tmp.write(b'fake mp3 content')
            tmp.flush()
            
            is_valid, content_type, mime_type = detector.validate_file(tmp.name)
            assert is_valid
            assert content_type == 'audio'
            assert mime_type == 'audio/mpeg'


class TestContentProcessor:
    """Test suite for ContentProcessor class."""
    def test_init(self):
        """Test processor initialization."""
        processor = ContentProcessor()
        assert processor.detector is not None
        assert hasattr(processor, 'audio_extractor')
        assert hasattr(processor, 'video_extractor')
        assert hasattr(processor, 'image_extractor')
        assert hasattr(processor, 'text_extractor')

    @pytest.mark.asyncio
    async def test_process_content_audio(self):
        """Test audio content processing."""
        processor = ContentProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b'fake mp3 content')
            file_path = tmp.name
        
        try:
            with patch.object(processor, '_extract_audio_metadata') as mock_extract:
                mock_extract.return_value = AudioMetadata(
                    duration=120.0,
                    sample_rate=44100,
                    channels=2,
                    bitrate=128000,
                    format='MP3'
                )
                
                result = await processor.process_content(file_path)
                assert isinstance(result, ProcessingResult)
                assert result.content_type == 'audio'
                assert result.file_size > 0
                assert isinstance(result.metadata, AudioMetadata)
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_process_content_video(self):
        """Test video content processing."""
        processor = ContentProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            tmp.write(b'fake mp4 content')
            file_path = tmp.name
        
        try:
            with patch.object(processor, '_extract_video_metadata') as mock_extract:
                mock_extract.return_value = VideoMetadata(
                    duration=300.0,
                    width=1920,
                    height=1080,
                    fps=30.0,
                    bitrate=2000000,
                    codec='H.264'
                )
                
                result = await processor.process_content(file_path)
                assert isinstance(result, ProcessingResult)
                assert result.content_type == 'video'
                assert isinstance(result.metadata, VideoMetadata)
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_process_content_image(self):
        """Test image content processing."""
        processor = ContentProcessor()
        
        # Create a real image file
        img = Image.new('RGB', (100, 100), color='red')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name, 'JPEG')
            file_path = tmp.name
        
        try:
            result = await processor.process_content(file_path)
            assert isinstance(result, ProcessingResult)
            assert result.content_type == 'image'
            assert isinstance(result.metadata, ImageMetadata)
            assert result.metadata.width == 100
            assert result.metadata.height == 100
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_process_content_text(self):
        """Test text content processing."""
        processor = ContentProcessor()
        
        text_content = "This is a test document with multiple words."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(text_content)
            file_path = tmp.name
        
        try:
            result = await processor.process_content(file_path)
            assert isinstance(result, ProcessingResult)
            assert result.content_type == 'text'
            assert isinstance(result.metadata, TextMetadata)
            assert result.metadata.word_count > 0
            assert result.metadata.language is not None
        finally:
            Path(file_path).unlink(missing_ok=True)

    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        processor = ContentProcessor()
        
        content = b'test content for hashing'
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            file_path = tmp.name
        
        try:
            hash_value = processor._calculate_file_hash(file_path)
            expected_hash = hashlib.sha256(content).hexdigest()
            assert hash_value == expected_hash
        finally:
            Path(file_path).unlink(missing_ok=True)

    @patch('librosa.load')
    def test_extract_audio_metadata(self, mock_librosa):
        """Test audio metadata extraction."""
        mock_librosa.return_value = (np.random.rand(44100), 44100)
        processor = ContentProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.mp3') as tmp:
            metadata = processor._extract_audio_metadata(tmp.name)
            assert isinstance(metadata, AudioMetadata)
            assert metadata.sample_rate == 44100

    @patch('cv2.VideoCapture')
    def test_extract_video_metadata(self, mock_cv2):
        """Test video metadata extraction."""
        mock_cap = MagicMock()
        mock_cap.get.side_effect = lambda prop: {
            3: 1920,  # WIDTH
            4: 1080,  # HEIGHT
            5: 30.0,  # FPS
            7: 900    # FRAME_COUNT
        }.get(prop, 0)
        mock_cv2.return_value = mock_cap
        
        processor = ContentProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.mp4') as tmp:
            metadata = processor._extract_video_metadata(tmp.name)
            assert isinstance(metadata, VideoMetadata)
            assert metadata.width == 1920
            assert metadata.height == 1080
            assert metadata.fps == 30.0

    def test_extract_image_metadata(self):
        """Test image metadata extraction."""
        processor = ContentProcessor()
        
        img = Image.new('RGB', (800, 600), color='blue')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name, 'JPEG')
            file_path = tmp.name
        
        try:
            metadata = processor._extract_image_metadata(file_path)
            assert isinstance(metadata, ImageMetadata)
            assert metadata.width == 800
            assert metadata.height == 600
            assert metadata.format == 'JPEG'
        finally:
            Path(file_path).unlink(missing_ok=True)

    def test_extract_text_metadata(self):
        """Test text metadata extraction."""
        processor = ContentProcessor()
        
        text_content = "Hello world! This is a test document."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(text_content)
            file_path = tmp.name
        
        try:
            metadata = processor._extract_text_metadata(file_path)
            assert isinstance(metadata, TextMetadata)
            assert metadata.word_count == 8
            assert metadata.char_count == len(text_content)
        finally:
            Path(file_path).unlink(missing_ok=True)


class TestContentHandler:
    """Test suite for ContentHandler class."""
    def test_init(self):
        """Test handler initialization."""
        handler = ContentHandler()
        assert handler.processor is not None
        assert handler.detector is not None

    @pytest.mark.asyncio
    async def test_handle_content_upload(self):
        """Test complete content upload handling."""
        handler = ContentHandler()
        
        # Create test file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Test content for upload')
            file_path = tmp.name
        
        try:
            with patch.object(handler.processor, 'process_content') as mock_process:
                mock_result = ProcessingResult(
                    file_path=file_path,
                    content_type='text',
                    file_size=23,
                    file_hash='test_hash',
                    metadata=TextMetadata(
                        encoding='utf-8',
                        word_count=4,
                        char_count=23,
                        language='en'
                    ),
                    fingerprint_data={'hash': 'test_hash'},
                    processing_time=0.1,
                    success=True
                )
                mock_process.return_value = mock_result
                
                result = await handler.handle_content_upload(file_path)
                assert result.success
                assert result.content_type == 'text'
                assert result.file_hash == 'test_hash'
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_validate_content(self):
        """Test content validation."""
        handler = ContentHandler()
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Valid content')
            file_path = tmp.name
        
        try:
            is_valid, errors = await handler.validate_content(file_path)
            assert is_valid
            assert len(errors) == 0
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_validate_content_invalid_file(self):
        """Test validation with invalid file."""
        handler = ContentHandler()
        
        is_valid, errors = await handler.validate_content('/nonexistent/file.txt')
        assert not is_valid
        assert len(errors) > 0
        assert any('not exist' in error for error in errors)

    @pytest.mark.asyncio
    async def test_prepare_for_fingerprinting(self):
        """Test fingerprint preparation."""
        handler = ContentHandler()
        
        result = ProcessingResult(
            file_path='/test/file.txt',
            content_type='text',
            file_size=100,
            file_hash='test_hash',
            metadata=TextMetadata(
                encoding='utf-8',
                word_count=10,
                char_count=100,
                language='en'
            ),
            fingerprint_data={},
            processing_time=0.1,
            success=True
        )
        
        fingerprint_data = await handler.prepare_for_fingerprinting(result)
        assert 'content_hash' in fingerprint_data
        assert 'metadata_hash' in fingerprint_data
        assert 'content_type' in fingerprint_data

    def test_create_content_handler(self):
        """Test factory function."""
        handler = create_content_handler()
        assert isinstance(handler, ContentHandler)


class TestIntegration:
    """Integration tests for content handler components."""
    @pytest.mark.asyncio
    async def test_end_to_end_processing(self):
        """Test complete end-to-end content processing."""
        handler = ContentHandler()
        
        # Create a real test file
        test_content = "This is a comprehensive test document for end-to-end processing."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(test_content)
            file_path = tmp.name
        
        try:
            # Validate content
            is_valid, errors = await handler.validate_content(file_path)
            assert is_valid, f"Validation failed: {errors}"
            
            # Process content
            result = await handler.handle_content_upload(file_path)
            assert result.success
            assert result.content_type == 'text'
            assert result.file_size > 0
            assert result.file_hash is not None
            assert isinstance(result.metadata, TextMetadata)
            
            # Prepare fingerprint
            fingerprint_data = await handler.prepare_for_fingerprinting(result)
            assert len(fingerprint_data) > 0
            assert 'content_hash' in fingerprint_data
            
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_multiple_file_types(self):
        """Test processing multiple file types."""
        handler = ContentHandler()
        results = []
        
        # Text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write('Test text content')
            results.append(await handler.handle_content_upload(tmp.name))
            Path(tmp.name).unlink(missing_ok=True)
        
        # Image file
        img = Image.new('RGB', (50, 50), color='green')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name, 'JPEG')
            results.append(await handler.handle_content_upload(tmp.name))
            Path(tmp.name).unlink(missing_ok=True)
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert results[0].content_type == 'text'
        assert results[1].content_type == 'image'


if __name__ == '__main__':
    pytest.main([str(Path(__file__))])
