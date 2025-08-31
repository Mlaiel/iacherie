# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Comprehensive API endpoint tests
Tests all critical API routes for functionality, security, and performance
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timedelta

# Mock fastapi if not available
try:
    from fastapi.testclient import TestClient
    import jwt
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    pytest.skip("FastAPI dependencies not available", allow_module_level=True)

# Import modules under test if available
try:
    from main import app
    from api.routes import auth, content, protection, fingerprinting, monetization
    from core.security import create_access_token, verify_token
except ImportError as e:
    pytest.skip(f"API modules not available: {e}", allow_module_level=True)


class TestAuthAPI:
    """Test suite for authentication APIs"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_data(self):
        return {
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User",
            "user_type": "creator"
        }
    
    def test_user_registration(self, client, mock_user_data):
        """Test user registration endpoint"""
        response = client.post("/api/auth/register", json=mock_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["user"]["email"] == mock_user_data["email"]
    
    def test_user_login(self, client, mock_user_data):
        """Test user login endpoint"""
        # First register a user
        client.post("/api/auth/register", json=mock_user_data)
        
        # Then try to login
        login_data = {
            "email": mock_user_data["email"],
            "password": mock_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_token_refresh(self, client, mock_user_data):
        """Test token refresh endpoint"""
        # Register and login
        client.post("/api/auth/register", json=mock_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": mock_user_data["email"],
            "password": mock_user_data["password"]
        })
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_protected_route_access(self, client, mock_user_data):
        """Test access to protected routes with valid token"""
        # Register and login
        client.post("/api/auth/register", json=mock_user_data)
        login_response = client.post("/api/auth/login", json={
            "email": mock_user_data["email"],
            "password": mock_user_data["password"]
        })
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Access protected route
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == mock_user_data["email"]
    
    def test_invalid_token_access(self, client):
        """Test access with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/profile", headers=headers)
        
        assert response.status_code == 401
    
    def test_password_reset_request(self, client, mock_user_data):
        """Test password reset request"""
        # Register user first
        client.post("/api/auth/register", json=mock_user_data)
        
        response = client.post("/api/auth/reset-password-request", json={
            "email": mock_user_data["email"]
        })
        
        assert response.status_code == 200
        assert "reset_token_sent" in response.json()


class TestContentAPI:
    """Test suite for content management APIs"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authorization headers for testing"""
        user_data = {
            "email": "creator@example.com",
            "password": "password123",
            "name": "Creator User",
            "user_type": "creator"
        }
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    @pytest.fixture
    def sample_content_data(self):
        return {
            "title": "Test Audio Track",
            "description": "A test audio track for fingerprinting",
            "content_type": "audio",
            "genre": "electronic",
            "tags": ["test", "electronic", "original"],
            "is_public": True
        }
    
    def test_create_content(self, client, auth_headers, sample_content_data):
        """Test content creation"""
        response = client.post(
            "/api/content/create",
            json=sample_content_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_content_data["title"]
        assert "content_id" in data
        assert "created_at" in data
    
    def test_get_content_list(self, client, auth_headers, sample_content_data):
        """Test getting user's content list"""
        # Create some content first
        for i in range(3):
            content_data = sample_content_data.copy()
            content_data["title"] = f"Test Track {i+1}"
            client.post("/api/content/create", json=content_data, headers=auth_headers)
        
        response = client.get("/api/content/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3
        assert "total" in data
        assert "page" in data
    
    def test_get_content_by_id(self, client, auth_headers, sample_content_data):
        """Test getting specific content by ID"""
        # Create content
        create_response = client.post(
            "/api/content/create",
            json=sample_content_data,
            headers=auth_headers
        )
        content_id = create_response.json()["content_id"]
        
        # Get content by ID
        response = client.get(f"/api/content/{content_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content_id"] == content_id
        assert data["title"] == sample_content_data["title"]
    
    def test_update_content(self, client, auth_headers, sample_content_data):
        """Test content update"""
        # Create content
        create_response = client.post(
            "/api/content/create",
            json=sample_content_data,
            headers=auth_headers
        )
        content_id = create_response.json()["content_id"]
        
        # Update content
        update_data = {"title": "Updated Test Track", "description": "Updated description"}
        response = client.put(
            f"/api/content/{content_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    def test_delete_content(self, client, auth_headers, sample_content_data):
        """Test content deletion"""
        # Create content
        create_response = client.post(
            "/api/content/create",
            json=sample_content_data,
            headers=auth_headers
        )
        content_id = create_response.json()["content_id"]
        
        # Delete content
        response = client.delete(f"/api/content/{content_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify content is deleted
        get_response = client.get(f"/api/content/{content_id}", headers=auth_headers)
        assert get_response.status_code == 404


class TestFingerprintingAPI:
    """Test suite for fingerprinting APIs"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authorization headers for testing"""
        user_data = {
            "email": "creator@example.com",
            "password": "password123",
            "name": "Creator User",
            "user_type": "creator"
        }
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_upload_for_fingerprinting(self, client, auth_headers):
        """Test file upload for fingerprinting"""
        # Mock file upload
        test_file_content = b"fake audio file content"
        files = {"file": ("test_audio.mp3", test_file_content, "audio/mpeg")}
        
        with patch('ai_engine.fingerprinting.audio_fingerprint_engine.AudioFingerprintEngine.generate_fingerprint') as mock_fingerprint:
            mock_fingerprint.return_value = "fp_test123456789"
            
            response = client.post(
                "/api/fingerprinting/upload",
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "fingerprint_id" in data
        assert "fingerprint" in data
        assert data["status"] == "completed"
    
    def test_get_fingerprint_status(self, client, auth_headers):
        """Test getting fingerprint status"""
        # Mock upload first
        test_file_content = b"fake audio file content"
        files = {"file": ("test_audio.mp3", test_file_content, "audio/mpeg")}
        
        with patch('ai_engine.fingerprinting.audio_fingerprint_engine.AudioFingerprintEngine.generate_fingerprint') as mock_fingerprint:
            mock_fingerprint.return_value = "fp_test123456789"
            
            upload_response = client.post(
                "/api/fingerprinting/upload",
                files=files,
                headers=auth_headers
            )
        
        fingerprint_id = upload_response.json()["fingerprint_id"]
        
        # Get status
        response = client.get(
            f"/api/fingerprinting/status/{fingerprint_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fingerprint_id"] == fingerprint_id
        assert "status" in data
        assert "created_at" in data
    
    def test_search_similar_content(self, client, auth_headers):
        """Test searching for similar content"""
        search_data = {
            "fingerprint": "fp_test123456789",
            "threshold": 0.85,
            "limit": 10
        }
        
        with patch('ai_engine.fingerprinting.vector_matching_engine.VectorMatchingEngine.search_similar') as mock_search:
            mock_search.return_value = [
                {"content_id": "content_1", "similarity": 0.95, "title": "Similar Track 1"},
                {"content_id": "content_2", "similarity": 0.87, "title": "Similar Track 2"}
            ]
            
            response = client.post(
                "/api/fingerprinting/search",
                json=search_data,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["results"][0]["similarity"] > 0.9
    
    def test_batch_fingerprinting(self, client, auth_headers):
        """Test batch fingerprinting"""
        # Mock multiple files
        files = [
            ("files", ("test1.mp3", b"fake audio 1", "audio/mpeg")),
            ("files", ("test2.mp3", b"fake audio 2", "audio/mpeg")),
            ("files", ("test3.mp3", b"fake audio 3", "audio/mpeg"))
        ]
        
        with patch('ai_engine.fingerprinting.audio_fingerprint_engine.AudioFingerprintEngine.generate_fingerprint') as mock_fingerprint:
            mock_fingerprint.side_effect = ["fp_1", "fp_2", "fp_3"]
            
            response = client.post(
                "/api/fingerprinting/batch",
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == 202  # Accepted for processing
        data = response.json()
        assert "batch_id" in data
        assert "files_count" in data
        assert data["files_count"] == 3


class TestProtectionAPI:
    """Test suite for content protection APIs"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authorization headers for testing"""
        user_data = {
            "email": "creator@example.com",
            "password": "password123",
            "name": "Creator User",
            "user_type": "creator"
        }
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_enable_protection(self, client, auth_headers):
        """Test enabling protection for content"""
        protection_data = {
            "content_id": "content_123",
            "protection_type": "dmca",
            "monitoring_platforms": ["youtube", "spotify", "instagram"],
            "auto_takedown": True
        }
        
        response = client.post(
            "/api/protection/enable",
            json=protection_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "protection_id" in data
        assert data["status"] == "active"
        assert data["content_id"] == protection_data["content_id"]
    
    def test_get_violations(self, client, auth_headers):
        """Test getting violation reports"""
        response = client.get("/api/protection/violations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "violations" in data
        assert "total" in data
        assert "page" in data
    
    def test_send_dmca_notice(self, client, auth_headers):
        """Test sending DMCA takedown notice"""
        dmca_data = {
            "violation_id": "violation_123",
            "platform": "youtube",
            "infringing_url": "https://youtube.com/watch?v=example",
            "copyright_owner": "Test Creator",
            "contact_email": "creator@example.com"
        }
        
        with patch('business.protection.dmca_manager.DMCAManager.send_notice') as mock_dmca:
            mock_dmca.return_value = {"notice_id": "dmca_456", "status": "sent"}
            
            response = client.post(
                "/api/protection/dmca",
                json=dmca_data,
                headers=auth_headers
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "notice_id" in data
        assert data["status"] == "sent"
    
    def test_get_protection_stats(self, client, auth_headers):
        """Test getting protection statistics"""
        response = client.get("/api/protection/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_protected" in data
        assert "violations_detected" in data
        assert "takedowns_successful" in data
        assert "monthly_stats" in data


class TestMonetizationAPI:
    """Test suite for monetization APIs"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Get authorization headers for testing"""
        user_data = {
            "email": "creator@example.com",
            "password": "password123",
            "name": "Creator User",
            "user_type": "creator"
        }
        client.post("/api/auth/register", json=user_data)
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_revenue_stats(self, client, auth_headers):
        """Test getting revenue statistics"""
        response = client.get("/api/monetization/revenue", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_revenue" in data
        assert "monthly_revenue" in data
        assert "platform_breakdown" in data
        assert "payment_history" in data
    
    def test_setup_payment_method(self, client, auth_headers):
        """Test setting up payment method"""
        payment_data = {
            "type": "stripe",
            "account_id": "acct_test123",
            "currency": "USD",
            "country": "US"
        }
        
        response = client.post(
            "/api/monetization/payment-method",
            json=payment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "payment_method_id" in data
        assert data["status"] == "active"
    
    def test_request_withdrawal(self, client, auth_headers):
        """Test requesting withdrawal"""
        withdrawal_data = {
            "amount": 100.00,
            "currency": "USD",
            "payment_method_id": "pm_test123"
        }
        
        with patch('monetization.payment_processor.PaymentProcessor.process_withdrawal') as mock_withdrawal:
            mock_withdrawal.return_value = {"withdrawal_id": "wd_456", "status": "pending"}
            
            response = client.post(
                "/api/monetization/withdraw",
                json=withdrawal_data,
                headers=auth_headers
            )
        
        assert response.status_code == 201
        data = response.json()
        assert "withdrawal_id" in data
        assert data["status"] == "pending"


class TestAPIPerformance:
    """Test suite for API performance"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_api_response_times(self, client):
        """Test API response times"""
        import time
        
        endpoints = [
            ("GET", "/api/health"),
            ("GET", "/api/status"),
            ("GET", "/docs"),  # OpenAPI docs
        ]
        
        for method, endpoint in endpoints:
            start_time = time.time()
            if method == "GET":
                response = client.get(endpoint)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = client.get("/api/health")
            end_time = time.time()
            results.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time
            })
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        assert len(results) == 10
        assert all(r["status_code"] == 200 for r in results)
        
        # Total time should be reasonable (not much longer than single request)
        assert total_time < 5.0


class TestAPIErrorHandling:
    """Test suite for API error handling"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_404_handling(self, client):
        """Test 404 error handling"""
        response = client.get("/api/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "message" in data
    
    def test_validation_errors(self, client):
        """Test request validation errors"""
        # Invalid registration data
        invalid_data = {
            "email": "invalid-email",  # Invalid email format
            "password": "123",         # Too short password
        }
        
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_rate_limiting(self, client):
        """Test rate limiting"""
        # Make multiple rapid requests
        responses = []
        for _ in range(100):  # Exceed rate limit
            response = client.get("/api/health")
            responses.append(response)
        
        # Should eventually get rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes  # Too Many Requests


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])