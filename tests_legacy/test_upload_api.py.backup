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

"""Integration tests for Ainflue upload API endpoints.
Tests the complete upload workflow and fingerprinting process.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import httpx
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Test configurations
API_BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = "/tmp/test_files"

class TestUploadAPI:
    """Test suite for upload API endpoints."""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        # Create test files directory
        os.makedirs(TEST_FILES_DIR, exist_ok=True)
        
        # Create sample test files
        self.create_test_files()
        
        # Mock API client
        self.client = httpx.AsyncClient(base_url=API_BASE_URL)
        
        yield
        
        # Cleanup
        await self.client.aclose()
    
    def create_test_files(self):
        """Create sample test files for upload testing."""
        # Audio file (MP3)
        self.audio_file = Path(TEST_FILES_DIR) / "test_audio.mp3"
        with open(self.audio_file, "wb") as f:
            # Create a minimal MP3-like file structure
            f.write(b"ID3\x03\x00\x00\x00")  # MP3 header
            f.write(b"\x00" * 1024)  # 1KB of data
        
        # Video file (MP4)
        self.video_file = Path(TEST_FILES_DIR) / "test_video.mp4"
        with open(self.video_file, "wb") as f:
            # Create a minimal MP4-like file structure
            f.write(b"\x00\x00\x00\x20ftypmp42")  # MP4 header
            f.write(b"\x00" * 2048)  # 2KB of data
        
        # Image file (PNG)
        self.image_file = Path(TEST_FILES_DIR) / "test_image.png"
        with open(self.image_file, "wb") as f:
            # Create a minimal PNG file structure
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG signature
            f.write(b"\x00" * 512)  # 512B of data
        
        # Text file
        self.text_file = Path(TEST_FILES_DIR) / "test_text.txt"
        with open(self.text_file, "w") as f:
            f.write("This is a test text file for content protection.\n")
            f.write("It contains sample content for testing purposes.")
    
    @pytest.mark.asyncio
    async def test_upload_audio_file(self):
        """Test uploading an audio file."""
        with open(self.audio_file, "rb") as f:
            files = {"file": ("test_audio.mp3", f, "audio/mpeg")}
            data = {
                "title": "Test Audio Track",
                "description": "Sample audio for testing",
                "enable_monitoring": True
            }
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 201
            content = response.json()
            
            assert content["title"] == "Test Audio Track"
            assert content["content_type"] == "audio"
            assert content["protection_status"] in ["pending", "protected"]
            assert "id" in content
            assert "fingerprint_id" in content
    
    @pytest.mark.asyncio
    async def test_upload_video_file(self):
        """Test uploading a video file."""
        with open(self.video_file, "rb") as f:
            files = {"file": ("test_video.mp4", f, "video/mp4")}
            data = {
                "title": "Test Video Content",
                "description": "Sample video for testing",
                "enable_monitoring": True
            }
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 201
            content = response.json()
            
            assert content["title"] == "Test Video Content"
            assert content["content_type"] == "video"
            assert content["monitoring_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_upload_image_file(self):
        """Test uploading an image file."""
        with open(self.image_file, "rb") as f:
            files = {"file": ("test_image.png", f, "image/png")}
            data = {
                "title": "Test Image",
                "description": "Sample image for testing"
            }
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 201
            content = response.json()
            
            assert content["title"] == "Test Image"
            assert content["content_type"] == "image"
    
    @pytest.mark.asyncio
    async def test_upload_text_file(self):
        """Test uploading a text file."""
        with open(self.text_file, "rb") as f:
            files = {"file": ("test_text.txt", f, "text/plain")}
            data = {
                "title": "Test Text Content",
                "description": "Sample text for testing"
            }
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 201
            content = response.json()
            
            assert content["title"] == "Test Text Content"
            assert content["content_type"] == "text"
    
    @pytest.mark.asyncio
    async def test_upload_file_size_limit(self):
        """Test file size limit enforcement."""
        # Create a large file (simulate oversized upload)
        large_file = Path(TEST_FILES_DIR) / "large_file.mp3"
        with open(large_file, "wb") as f:
            f.write(b"\x00" * (105 * 1024 * 1024))  # 105MB file
        
        with open(large_file, "rb") as f:
            files = {"file": ("large_file.mp3", f, "audio/mpeg")}
            data = {"title": "Large File", "description": "Too large"}
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 413  # Payload too large
            
        # Cleanup
        os.remove(large_file)
    
    @pytest.mark.asyncio
    async def test_upload_unsupported_format(self):
        """Test uploading unsupported file format."""
        unsupported_file = Path(TEST_FILES_DIR) / "test.xyz"
        with open(unsupported_file, "wb") as f:
            f.write(b"unsupported content")
        
        with open(unsupported_file, "rb") as f:
            files = {"file": ("test.xyz", f, "application/xyz")}
            data = {"title": "Unsupported File"}
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 400
            error = response.json()
            assert "unsupported" in error["error"].lower()
        
        # Cleanup
        os.remove(unsupported_file)
    
    @pytest.mark.asyncio
    async def test_upload_missing_title(self):
        """Test upload with missing required title."""
        with open(self.audio_file, "rb") as f:
            files = {"file": ("test_audio.mp3", f, "audio/mpeg")}
            data = {"description": "Missing title"}
            
            response = await self.client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 400
            error = response.json()
            assert "title" in error["error"].lower()
    
    @pytest.mark.asyncio
    async def test_fingerprinting_process(self):
        """Test the fingerprinting process after upload."""
        # Upload a file first
        with open(self.audio_file, "rb") as f:
            files = {"file": ("test_audio.mp3", f, "audio/mpeg")}
            data = {"title": "Test Fingerprinting", "description": "Test"}
            
            response = await self.client.post("/api/content", files=files, data=data)
            content = response.json()
            content_id = content["id"]
        
        # Test fingerprint generation
        fingerprint_data = {
            "algorithm": "chromaprint",
            "quality": "balanced"
        }
        
        response = await self.client.post(
            f"/api/fingerprint/{content_id}",
            json=fingerprint_data
        )
        
        assert response.status_code == 200
        fingerprint = response.json()
        
        assert fingerprint["content_id"] == content_id
        assert fingerprint["fingerprint_type"] == "audio"
        assert fingerprint["algorithm"] == "chromaprint"
        assert "hash_value" in fingerprint
        assert fingerprint["confidence_score"] > 0
    
    @pytest.mark.asyncio
    async def test_content_retrieval(self):
        """Test retrieving uploaded content."""
        # Upload a file first
        with open(self.image_file, "rb") as f:
            files = {"file": ("test_image.png", f, "image/png")}
            data = {"title": "Test Retrieval", "description": "Test"}
            
            response = await self.client.post("/api/content", files=files, data=data)
            content = response.json()
            content_id = content["id"]
        
        # Retrieve the content
        response = await self.client.get(f"/api/content/{content_id}")
        
        assert response.status_code == 200
        retrieved_content = response.json()
        
        assert retrieved_content["id"] == content_id
        assert retrieved_content["title"] == "Test Retrieval"
        assert retrieved_content["content_type"] == "image"
    
    @pytest.mark.asyncio
    async def test_content_list(self):
        """Test listing user content."""
        # Upload multiple files
        files_to_upload = [
            (self.audio_file, "audio/mpeg", "Test Audio"),
            (self.video_file, "video/mp4", "Test Video"),
            (self.image_file, "image/png", "Test Image")
        ]
        
        uploaded_ids = []
        for file_path, mime_type, title in files_to_upload:
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, mime_type)}
                data = {"title": title, "description": "Test"}
                
                response = await self.client.post("/api/content", files=files, data=data)
                content = response.json()
                uploaded_ids.append(content["id"])
        
        # List content
        response = await self.client.get("/api/content")
        
        assert response.status_code == 200
        content_list = response.json()
        
        assert "items" in content_list
        assert len(content_list["items"]) >= 3
        
        # Check that our uploaded content is in the list
        retrieved_ids = [item["id"] for item in content_list["items"]]
        for uploaded_id in uploaded_ids:
            assert uploaded_id in retrieved_ids
    
    @pytest.mark.asyncio
    async def test_content_filtering(self):
        """Test content filtering by type."""
        # Upload different types
        with open(self.audio_file, "rb") as f:
            files = {"file": ("audio.mp3", f, "audio/mpeg")}
            data = {"title": "Audio Content", "description": "Test"}
            await self.client.post("/api/content", files=files, data=data)
        
        with open(self.video_file, "rb") as f:
            files = {"file": ("video.mp4", f, "video/mp4")}
            data = {"title": "Video Content", "description": "Test"}
            await self.client.post("/api/content", files=files, data=data)
        
        # Filter by audio content
        response = await self.client.get("/api/content?content_type=audio")
        
        assert response.status_code == 200
        content_list = response.json()
        
        # All returned items should be audio
        for item in content_list["items"]:
            assert item["content_type"] == "audio"
    
    @pytest.mark.asyncio
    async def test_upload_authentication(self):
        """Test upload requires authentication."""
        # Create client without authentication
        unauth_client = httpx.AsyncClient(base_url=API_BASE_URL)
        
        with open(self.audio_file, "rb") as f:
            files = {"file": ("test.mp3", f, "audio/mpeg")}
            data = {"title": "Test Auth", "description": "Test"}
            
            response = await unauth_client.post("/api/content", files=files, data=data)
            
            assert response.status_code == 401
        
        await unauth_client.aclose()
    
    @pytest.mark.asyncio
    async def test_upload_rate_limiting(self):
        """Test upload rate limiting."""
        # Simulate multiple rapid uploads
        for i in range(5):
            with open(self.audio_file, "rb") as f:
                files = {"file": (f"test{i}.mp3", f, "audio/mpeg")}
                data = {"title": f"Test {i}", "description": "Rate limit test"}
                
                response = await self.client.post("/api/content", files=files, data=data)
                
                # First few should succeed, then rate limiting kicks in
                if i < 3:
                    assert response.status_code == 201
                else:
                    # Should hit rate limit
                    assert response.status_code in [429, 201]  # 429 = Too Many Requests
    
    @pytest.mark.asyncio
    async def test_concurrent_uploads(self):
        """Test handling concurrent uploads."""
        async def upload_file(file_path, title):
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "audio/mpeg")}
                data = {"title": title, "description": "Concurrent test"}
                
                response = await self.client.post("/api/content", files=files, data=data)
                return response.status_code
        
        # Create multiple concurrent uploads
        tasks = [
            upload_file(self.audio_file, f"Concurrent {i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All uploads should succeed
        for status_code in results:
            assert status_code == 201
    
    @pytest.mark.asyncio
    async def test_upload_metadata_extraction(self):
        """Test metadata extraction from uploaded files."""
        with open(self.audio_file, "rb") as f:
            files = {"file": ("test_audio.mp3", f, "audio/mpeg")}
            data = {"title": "Metadata Test", "description": "Test metadata"}
            
            response = await self.client.post("/api/content", files=files, data=data)
            content = response.json()
        
        # Check that metadata was extracted
        assert "metadata" in content
        assert "file_size" in content
        assert content["file_size"] > 0
        
        # For audio files, duration might be extracted
        if content["content_type"] == "audio":
            assert "duration" in content


class TestFingerprintingPerformance:
    """Performance tests for fingerprinting system."""
    
    @pytest.mark.asyncio
    async def test_fingerprinting_speed(self):
        """Test fingerprinting processing time."""
        client = httpx.AsyncClient(base_url=API_BASE_URL)
        
        # Create a test file
        test_file = Path(TEST_FILES_DIR) / "perf_test.mp3"
        with open(test_file, "wb") as f:
            f.write(b"ID3\x03\x00\x00\x00" + b"\x00" * 5120)  # 5KB MP3
        
        try:
            # Upload file
            with open(test_file, "rb") as f:
                files = {"file": ("perf_test.mp3", f, "audio/mpeg")}
                data = {"title": "Performance Test", "description": "Speed test"}
                
                start_time = asyncio.get_event_loop().time()
                response = await client.post("/api/content", files=files, data=data)
                upload_time = asyncio.get_event_loop().time() - start_time
                
                assert response.status_code == 201
                content = response.json()
                content_id = content["id"]
            
            # Test fingerprinting speed
            fingerprint_data = {"algorithm": "chromaprint", "quality": "fast"}
            
            start_time = asyncio.get_event_loop().time()
            response = await client.post(f"/api/fingerprint/{content_id}", json=fingerprint_data)
            fingerprint_time = asyncio.get_event_loop().time() - start_time
            
            assert response.status_code == 200
            fingerprint = response.json()
            
            # Performance assertions
            assert upload_time < 5.0  # Upload should take less than 5 seconds
            assert fingerprint_time < 30.0  # Fingerprinting should take less than 30 seconds
            assert fingerprint["processing_time"] < 30.0
            
        finally:
            await client.aclose()
            if test_file.exists():
                os.remove(test_file)


if __name__ == '__main__':
    # Run tests
    pytest.main([str(Path(__file__)), '-v', '--asyncio-mode=auto'])