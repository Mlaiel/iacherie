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

"""
Workflow Integration Tests

Tests for end-to-end workflows including content upload to protection,
user registration to monetization, and complete business workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import aiohttp
import tempfile
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Test configuration
TEST_BASE_URL = "http://localhost:8000"
WORKFLOW_TIMEOUT = 300  # 5 minutes for complex workflows


class WorkflowTestClient:
    """Enhanced test client for workflow testing."""
    
    def __init__(self, base_url: str = TEST_BASE_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.workflow_state: Dict[str, Any] = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Register and authenticate a user for workflow testing."""
        # Register user
        register_response = await self.session.post(
            f"{self.base_url}/auth/register",
            json=user_data
        )
        
        if register_response.status != 201:
            registration_data = await register_response.json()
            if "already exists" in str(registration_data).lower():
                # User exists, try to login
                pass
            else:
                raise Exception(f"Registration failed: {registration_data}")
        else:
            registration_data = await register_response.json()
            self.workflow_state["user_id"] = registration_data.get("user_id")
        
        # Login user
        login_response = await self.session.post(
            f"{self.base_url}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        
        if login_response.status != 200:
            raise Exception(f"Login failed: {await login_response.json()}")
        
        login_data = await login_response.json()
        self.auth_token = login_data["access_token"]
        
        return login_data
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def upload_content(self, file_path: str, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content file with metadata."""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        with open(file_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('file', file, filename=Path(file_path).name)
            
            for key, value in content_metadata.items():
                data.add_field(key, str(value))
            
            response = await self.session.post(
                f"{self.base_url}/content/upload",
                data=data,
                headers=headers
            )
        
        if response.status not in [200, 201]:
            raise Exception(f"Content upload failed: {await response.json()}")
        
        return await response.json()
    
    async def wait_for_processing(self, resource_id: str, resource_type: str, 
                                 timeout: int = 120) -> Dict[str, Any]:
        """Wait for asynchronous processing to complete."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            status_response = await self.session.get(
                f"{self.base_url}/{resource_type}/status/{resource_id}",
                headers=self.get_auth_headers()
            )
            
            if status_response.status != 200:
                await asyncio.sleep(2)
                continue
            
            status_data = await status_response.json()
            
            if status_data.get("status") == "completed":
                return status_data
            elif status_data.get("status") == "failed":
                raise Exception(f"Processing failed: {status_data.get('error')}")
            
            await asyncio.sleep(2)
        
        raise TimeoutError(f"Processing timeout for {resource_type} {resource_id}")


@pytest.fixture
async def workflow_client():
    """Create workflow test client."""
    async with WorkflowTestClient() as client:
        yield client


@pytest.fixture
def sample_audio_file():
    """
Create a sample audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        # Create minimal WAV file header
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        wav_data = b'\x00\x00' * 1000  # Simple audio data
        f.write(wav_header + wav_data)
        f.flush()
        
        yield f.name
    
    # Cleanup
    try:
        Path(f.name).unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_image_file():
    """
Create a sample image file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Minimal JPEG header
        jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
        jpeg_data = b'\x00' * 1000  # Simple image data
        jpeg_footer = b'\xff\xd9'
        f.write(jpeg_header + jpeg_data + jpeg_footer)
        f.flush()
        
        yield f.name
    
    # Cleanup
    try:
        Path(f.name).unlink()
    except FileNotFoundError:
        pass


class TestContentUploadToProtectionWorkflow:
    """
Test complete content upload to protection workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_audio_content_protection_workflow(self, workflow_client, sample_audio_file):
        """
Test complete audio content protection workflow."""
        # Step 1: Create and authenticate user
        user_data = {
            "email": f"audio_creator_{uuid.uuid4()}@example.com",
            "password": "secure_password_123",
            "first_name": "Audio",
            "last_name": "Creator",
            "creator_type": "musician"
        }
        
        auth_result = await workflow_client.authenticate_user(user_data)
        assert "access_token" in auth_result
        
        # Step 2: Upload audio content
        content_metadata = {
            "title": "Test Song",
            "description": "Original musical composition for testing",
            "content_type": "audio",
            "genre": "electronic",
            "duration": "180"  # 3 minutes
        }
        
        upload_result = await workflow_client.upload_content(sample_audio_file, content_metadata)
        
        assert "content_id" in upload_result
        assert "fingerprint_id" in upload_result
        content_id = upload_result["content_id"]
        fingerprint_id = upload_result["fingerprint_id"]
        
        # Step 3: Wait for fingerprinting to complete
        fingerprint_result = await workflow_client.wait_for_processing(
            fingerprint_id, "fingerprinting", timeout=120
        )
        
        assert fingerprint_result["status"] == "completed"
        assert "fingerprint_hash" in fingerprint_result
        assert "audio_features" in fingerprint_result
        
        # Step 4: Set up content monitoring
        monitoring_data = {
            "content_id": content_id,
            "platforms": ["spotify", "youtube", "soundcloud"],
            "monitoring_frequency": "daily",
            "sensitivity": "high"
        }
        
        monitoring_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/monitoring/setup",
            json=monitoring_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert monitoring_response.status == 201
        monitoring_result = await monitoring_response.json()
        assert "monitoring_id" in monitoring_result
        
        # Step 5: Verify protection is active
        protection_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/protection/status/{content_id}",
            headers=workflow_client.get_auth_headers()
        )
        
        assert protection_response.status == 200
        protection_data = await protection_response.json()
        assert protection_data["protection_active"] is True
        assert protection_data["monitoring_active"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_image_content_protection_workflow(self, workflow_client, sample_image_file):
        """Test complete image content protection workflow."""
        # Step 1: Authenticate user
        user_data = {
            "email": f"image_creator_{uuid.uuid4()}@example.com",
            "password": "secure_password_123",
            "first_name": "Image",
            "last_name": "Creator",
            "creator_type": "photographer"
        }
        
        await workflow_client.authenticate_user(user_data)
        
        # Step 2: Upload image content
        content_metadata = {
            "title": "Test Artwork",
            "description": "Original digital artwork for testing",
            "content_type": "image",
            "category": "digital_art",
            "resolution": "1920x1080"
        }
        
        upload_result = await workflow_client.upload_content(sample_image_file, content_metadata)
        content_id = upload_result["content_id"]
        
        # Step 3: Wait for image fingerprinting
        fingerprint_result = await workflow_client.wait_for_processing(
            upload_result["fingerprint_id"], "fingerprinting", timeout=60
        )
        
        assert "image_hash" in fingerprint_result
        assert "visual_features" in fingerprint_result
        
        # Step 4: Enable reverse image search monitoring
        monitoring_data = {
            "content_id": content_id,
            "platforms": ["google_images", "tineye", "pinterest"],
            "monitoring_frequency": "weekly"
        }
        
        monitoring_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/monitoring/setup",
            json=monitoring_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert monitoring_response.status == 201


class TestUserRegistrationToMonetizationWorkflow:
    """Test complete user registration to monetization workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_creator_monetization_setup_workflow(self, workflow_client):
        """
Test complete creator monetization setup workflow."""
        # Step 1: Register new creator
        user_data = {
            "email": f"monetization_creator_{uuid.uuid4()}@example.com",
            "password": "secure_password_123",
            "first_name": "Monetization",
            "last_name": "Creator",
            "creator_type": "musician",
            "country": "US"
        }
        
        auth_result = await workflow_client.authenticate_user(user_data)
        user_id = workflow_client.workflow_state["user_id"]
        
        # Step 2: Complete profile setup
        profile_data = {
            "bio": "Professional musician and content creator",
            "website": "https://example.com",
            "social_media": {
                "twitter": "@testcreator",
                "instagram": "@testcreator",
                "youtube": "testcreator"
            },
            "payment_preferences": {
                "currency": "USD",
                "payout_method": "bank_transfer"
            }
        }
        
        profile_response = await workflow_client.session.put(
            f"{workflow_client.base_url}/user/profile",
            json=profile_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert profile_response.status == 200
        
        # Step 3: Set up payment methods
        payment_setup_data = {
            "type": "stripe_connect",
            "business_type": "individual",
            "tax_id": "123-45-6789",
            "bank_account": {
                "account_number": "000123456789",
                "routing_number": "110000000",
                "account_type": "checking"
            }
        }
        
        payment_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/payments/setup",
            json=payment_setup_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert payment_response.status == 201
        payment_result = await payment_response.json()
        assert "stripe_account_id" in payment_result
        
        # Step 4: Create pricing tiers
        pricing_data = {
            "subscription_tiers": [
                {
                    "name": "Basic",
                    "price": 9.99,
                    "currency": "USD",
                    "interval": "monthly",
                    "features": ["basic_protection", "email_alerts"]
                },
                {
                    "name": "Premium",
                    "price": 29.99,
                    "currency": "USD",
                    "interval": "monthly",
                    "features": ["advanced_protection", "real_time_alerts", "takedown_automation"]
                }
            ],
            "licensing_rates": {
                "commercial_use": 100.00,
                "sync_license": 250.00,
                "exclusive_rights": 1000.00
            }
        }
        
        pricing_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/monetization/pricing",
            json=pricing_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert pricing_response.status == 201
        
        # Step 5: Verify monetization is active
        monetization_status_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/monetization/status",
            headers=workflow_client.get_auth_headers()
        )
        
        assert monetization_status_response.status == 200
        monetization_status = await monetization_status_response.json()
        assert monetization_status["monetization_active"] is True
        assert monetization_status["payment_setup_complete"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_subscription_purchase_workflow(self, workflow_client):
        """Test complete subscription purchase workflow."""
        # Step 1: Register customer
        customer_data = {
            "email": f"customer_{uuid.uuid4()}@example.com",
            "password": "customer_password_123",
            "first_name": "Test",
            "last_name": "Customer",
            "creator_type": "consumer"
        }
        
        await workflow_client.authenticate_user(customer_data)
        
        # Step 2: Browse available subscriptions
        subscriptions_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/subscriptions/available",
            headers=workflow_client.get_auth_headers()
        )
        
        assert subscriptions_response.status == 200
        subscriptions = await subscriptions_response.json()
        assert len(subscriptions["plans"]) > 0
        
        # Step 3: Select and purchase subscription
        selected_plan = subscriptions["plans"][0]
        purchase_data = {
            "plan_id": selected_plan["id"],
            "payment_method": {
                "type": "card",
                "card_number": "4242424242424242",
                "exp_month": "12",
                "exp_year": "2025",
                "cvc": "123"
            }
        }
        
        purchase_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/subscriptions/purchase",
            json=purchase_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert purchase_response.status == 201
        purchase_result = await purchase_response.json()
        assert "subscription_id" in purchase_result
        assert purchase_result["status"] == "active"
        
        # Step 4: Verify subscription activation
        subscription_status_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/subscriptions/status",
            headers=workflow_client.get_auth_headers()
        )
        
        assert subscription_status_response.status == 200
        subscription_status = await subscription_status_response.json()
        assert subscription_status["active"] is True
        assert subscription_status["plan_name"] == selected_plan["name"]


class TestCollaborationWorkflow:
    """Test collaboration creation to completion workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_music_collaboration_workflow(self, workflow_client):
        """
Test complete music collaboration workflow."""
        # Step 1: Create two artists
        artist1_data = {
            "email": f"artist1_{uuid.uuid4()}@example.com",
            "password": "artist_password_123",
            "first_name": "Artist",
            "last_name": "One",
            "creator_type": "musician"
        }
        
        artist2_data = {
            "email": f"artist2_{uuid.uuid4()}@example.com",
            "password": "artist_password_123",
            "first_name": "Artist",
            "last_name": "Two",
            "creator_type": "producer"
        }
        
        # Authenticate as artist 1
        await workflow_client.authenticate_user(artist1_data)
        artist1_id = workflow_client.workflow_state["user_id"]
        
        # Step 2: Create collaboration request
        collaboration_data = {
            "title": "Electronic Music Collaboration",
            "description": "Looking for a producer to collaborate on electronic music",
            "collaboration_type": "music_production",
            "requirements": {
                "genre": "electronic",
                "experience_level": "intermediate",
                "duration": "3_months"
            },
            "revenue_split": {
                "initiator": 60,
                "collaborator": 40
            }
        }
        
        collaboration_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/collaboration/create",
            json=collaboration_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert collaboration_response.status == 201
        collaboration_result = await collaboration_response.json()
        collaboration_id = collaboration_result["collaboration_id"]
        
        # Step 3: Switch to artist 2 and accept collaboration
        await workflow_client.authenticate_user(artist2_data)
        
        # Browse available collaborations
        browse_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/collaboration/browse",
            params={"genre": "electronic", "type": "music_production"},
            headers=workflow_client.get_auth_headers()
        )
        
        assert browse_response.status == 200
        available_collaborations = await browse_response.json()
        assert len(available_collaborations["collaborations"]) > 0
        
        # Accept collaboration
        accept_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/collaboration/{collaboration_id}/accept",
            json={"message": "Excited to work together!"},
            headers=workflow_client.get_auth_headers()
        )
        
        assert accept_response.status == 200
        
        # Step 4: Upload collaborative content
        content_data = {
            "collaboration_id": collaboration_id,
            "title": "Collaborative Track",
            "description": "Result of our collaboration",
            "content_type": "audio",
            "contributors": [artist1_id, workflow_client.workflow_state["user_id"]]
        }
        
        # Create a mock audio file for upload
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(b"mock audio data")
            f.flush()
            
            upload_result = await workflow_client.upload_content(f.name, content_data)
            
        assert "content_id" in upload_result
        
        # Step 5: Finalize collaboration
        finalize_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/collaboration/{collaboration_id}/finalize",
            json={
                "final_content_id": upload_result["content_id"],
                "revenue_distribution_confirmed": True
            },
            headers=workflow_client.get_auth_headers()
        )
        
        assert finalize_response.status == 200


class TestLicenseToPaymentWorkflow:
    """Test license creation to payment workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_licensing_workflow(self, workflow_client, sample_audio_file):
        """
Test complete content licensing workflow."""
        # Step 1: Setup licensor (content owner)
        licensor_data = {
            "email": f"licensor_{uuid.uuid4()}@example.com",
            "password": "licensor_password_123",
            "first_name": "Content",
            "last_name": "Owner",
            "creator_type": "musician"
        }
        
        await workflow_client.authenticate_user(licensor_data)
        
        # Upload content to license
        content_metadata = {
            "title": "Licensable Track",
            "description": "High-quality track available for licensing",
            "content_type": "audio",
            "licensing_available": True
        }
        
        upload_result = await workflow_client.upload_content(sample_audio_file, content_metadata)
        content_id = upload_result["content_id"]
        
        # Step 2: Create licensing terms
        licensing_terms = {
            "content_id": content_id,
            "license_types": [
                {
                    "type": "sync_license",
                    "price": 500.00,
                    "duration_days": 365,
                    "territory": "worldwide",
                    "usage_rights": ["advertisement", "film", "tv"]
                },
                {
                    "type": "commercial_license",
                    "price": 250.00,
                    "duration_days": 180,
                    "territory": "US",
                    "usage_rights": ["retail", "streaming"]
                }
            ]
        }
        
        licensing_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/licensing/terms",
            json=licensing_terms,
            headers=workflow_client.get_auth_headers()
        )
        
        assert licensing_response.status == 201
        
        # Step 3: Setup licensee (buyer)
        licensee_data = {
            "email": f"licensee_{uuid.uuid4()}@example.com",
            "password": "licensee_password_123",
            "first_name": "Content",
            "last_name": "Buyer",
            "creator_type": "business"
        }
        
        await workflow_client.authenticate_user(licensee_data)
        
        # Step 4: Browse and purchase license
        browse_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/licensing/browse",
            params={"content_type": "audio", "max_price": "1000"},
            headers=workflow_client.get_auth_headers()
        )
        
        assert browse_response.status == 200
        available_licenses = await browse_response.json()
        assert len(available_licenses["content"]) > 0
        
        # Purchase sync license
        purchase_data = {
            "content_id": content_id,
            "license_type": "sync_license",
            "project_details": {
                "project_name": "Commercial Advertisement",
                "usage_description": "Background music for product advertisement",
                "duration": "30_seconds"
            },
            "payment_method": {
                "type": "card",
                "card_number": "4242424242424242",
                "exp_month": "12",
                "exp_year": "2025",
                "cvc": "123"
            }
        }
        
        purchase_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/licensing/purchase",
            json=purchase_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert purchase_response.status == 201
        purchase_result = await purchase_response.json()
        
        assert "license_id" in purchase_result
        assert "contract_url" in purchase_result
        assert purchase_result["status"] == "active"
        
        # Step 5: Verify payment and licensing completion
        license_status_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/licensing/status/{purchase_result['license_id']}",
            headers=workflow_client.get_auth_headers()
        )
        
        assert license_status_response.status == 200
        license_status = await license_status_response.json()
        assert license_status["payment_status"] == "completed"
        assert license_status["license_active"] is True


class TestMonitoringToDetectionWorkflow:
    """Test monitoring setup to detection workflow."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_monitoring_detection_workflow(self, workflow_client, sample_audio_file):
        """
Test complete content monitoring and detection workflow."""
        # Step 1: Setup content owner
        owner_data = {
            "email": f"content_owner_{uuid.uuid4()}@example.com",
            "password": "owner_password_123",
            "first_name": "Content",
            "last_name": "Owner",
            "creator_type": "musician"
        }
        
        await workflow_client.authenticate_user(owner_data)
        
        # Upload and fingerprint content
        content_metadata = {
            "title": "Protected Song",
            "description": "Original song to be protected from unauthorized use",
            "content_type": "audio"
        }
        
        upload_result = await workflow_client.upload_content(sample_audio_file, content_metadata)
        content_id = upload_result["content_id"]
        
        # Wait for fingerprinting
        await workflow_client.wait_for_processing(
            upload_result["fingerprint_id"], "fingerprinting", timeout=60
        )
        
        # Step 2: Setup comprehensive monitoring
        monitoring_config = {
            "content_id": content_id,
            "platforms": ["youtube", "spotify", "soundcloud", "instagram"],
            "monitoring_frequency": "hourly",
            "sensitivity": "high",
            "automated_actions": {
                "send_takedown_notice": True,
                "notify_owner": True,
                "create_protection_report": True
            },
            "alert_preferences": {
                "email": True,
                "sms": False,
                "push_notification": True
            }
        }
        
        monitoring_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/monitoring/setup",
            json=monitoring_config,
            headers=workflow_client.get_auth_headers()
        )
        
        assert monitoring_response.status == 201
        monitoring_result = await monitoring_response.json()
        monitoring_id = monitoring_result["monitoring_id"]
        
        # Step 3: Simulate detection trigger
        # In real implementation, this would be triggered by platform crawlers
        detection_data = {
            "monitoring_id": monitoring_id,
            "platform": "youtube",
            "detected_url": "https://youtube.com/watch?v=mock_video_id",
            "similarity_score": 0.95,
            "detection_type": "unauthorized_upload",
            "metadata": {
                "uploader": "UnauthorizedUser123",
                "upload_date": datetime.now().isoformat(),
                "views": 10000
            }
        }
        
        detection_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/monitoring/detection",
            json=detection_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert detection_response.status == 201
        detection_result = await detection_response.json()
        detection_id = detection_result["detection_id"]
        
        # Step 4: Verify automated actions were triggered
        actions_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/protection/actions/{detection_id}",
            headers=workflow_client.get_auth_headers()
        )
        
        assert actions_response.status == 200
        actions_data = await actions_response.json()
        
        assert actions_data["takedown_notice_sent"] is True
        assert actions_data["owner_notified"] is True
        assert "protection_report_id" in actions_data
        
        # Step 5: Review detection and take manual action if needed
        review_data = {
            "detection_id": detection_id,
            "owner_decision": "confirm_violation",
            "additional_actions": ["escalate_to_legal", "request_revenue_claim"]
        }
        
        review_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/protection/review",
            json=review_data,
            headers=workflow_client.get_auth_headers()
        )
        
        assert review_response.status == 200
        
        # Verify workflow completion
        workflow_status_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/monitoring/workflow_status/{monitoring_id}",
            headers=workflow_client.get_auth_headers()
        )
        
        assert workflow_status_response.status == 200
        workflow_status = await workflow_status_response.json()
        assert workflow_status["detections_processed"] >= 1
        assert workflow_status["automated_actions_executed"] >= 1


class TestCrossServiceWorkflowIntegration:
    """Test workflows that span multiple services and systems."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_platform_workflow(self, workflow_client, sample_audio_file):
        """
Test complete end-to-end platform workflow."""
        # This test combines multiple workflows into one comprehensive test
        
        # Step 1: Creator onboarding and setup
        creator_data = {
            "email": f"complete_workflow_{uuid.uuid4()}@example.com",
            "password": "complete_password_123",
            "first_name": "Complete",
            "last_name": "Workflow",
            "creator_type": "musician"
        }
        
        auth_result = await workflow_client.authenticate_user(creator_data)
        
        # Complete profile and monetization setup
        profile_data = {
            "bio": "Professional musician testing complete workflow",
            "payment_preferences": {"currency": "USD", "payout_method": "stripe"}
        }
        
        await workflow_client.session.put(
            f"{workflow_client.base_url}/user/profile",
            json=profile_data,
            headers=workflow_client.get_auth_headers()
        )
        
        # Step 2: Content upload and protection
        content_metadata = {
            "title": "Complete Workflow Test Track",
            "description": "Testing the complete platform workflow",
            "content_type": "audio",
            "genre": "electronic"
        }
        
        upload_result = await workflow_client.upload_content(sample_audio_file, content_metadata)
        content_id = upload_result["content_id"]
        
        # Wait for processing
        await workflow_client.wait_for_processing(
            upload_result["fingerprint_id"], "fingerprinting", timeout=120
        )
        
        # Step 3: Setup monitoring and protection
        monitoring_config = {
            "content_id": content_id,
            "platforms": ["youtube", "spotify"],
            "monitoring_frequency": "daily"
        }
        
        monitoring_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/monitoring/setup",
            json=monitoring_config,
            headers=workflow_client.get_auth_headers()
        )
        
        assert monitoring_response.status == 201
        
        # Step 4: Setup licensing and monetization
        licensing_terms = {
            "content_id": content_id,
            "license_types": [
                {
                    "type": "commercial_license",
                    "price": 100.00,
                    "duration_days": 365
                }
            ]
        }
        
        licensing_response = await workflow_client.session.post(
            f"{workflow_client.base_url}/licensing/terms",
            json=licensing_terms,
            headers=workflow_client.get_auth_headers()
        )
        
        assert licensing_response.status == 201
        
        # Step 5: Verify complete workflow state
        dashboard_response = await workflow_client.session.get(
            f"{workflow_client.base_url}/dashboard/overview",
            headers=workflow_client.get_auth_headers()
        )
        
        assert dashboard_response.status == 200
        dashboard_data = await dashboard_response.json()
        
        assert dashboard_data["total_content"] >= 1
        assert dashboard_data["active_monitoring"] >= 1
        assert dashboard_data["available_licenses"] >= 1
        assert dashboard_data["profile_complete"] is True
        
        # Verify the entire workflow is functional
        assert "content_protection_active" in dashboard_data
        assert "monetization_ready" in dashboard_data


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--asyncio-mode=auto", "--timeout=300"])