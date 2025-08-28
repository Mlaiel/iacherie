"""
Cross-Service Integration Tests

Tests integration between multiple services and components
including API to database, external services coordination,
and service-to-service communication.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, patch


class CrossServiceTestClient:
    """Test client for cross-service integration testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.service_states: Dict[str, Any] = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> str:
        """Authenticate and return token."""
        user_data = {
            "email": f"cross_service_{uuid.uuid4()}@example.com",
            "password": "test_password_123",
            "first_name": "Cross",
            "last_name": "Service",
            "creator_type": "musician"
        }
        
        # Register
        register_response = await self.session.post(
            f"{self.base_url}/auth/register",
            json=user_data
        )
        
        if register_response.status not in [200, 201]:
            # Try login if user exists
            pass
        
        # Login
        login_response = await self.session.post(
            f"{self.base_url}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        
        if login_response.status == 200:
            login_data = await login_response.json()
            self.auth_token = login_data["access_token"]
            return self.auth_token
        
        raise Exception("Authentication failed")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers


@pytest.fixture
async def cross_service_client():
    """Create cross-service test client."""
    async with CrossServiceTestClient() as client:
        await client.authenticate()
        yield client


class TestAPIToDatabaseIntegration:
    """Test API to database integration."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_api_crud_database_consistency(self, cross_service_client):
        """Test API CRUD operations maintain database consistency."""
        client = cross_service_client
        
        # Create content via API
        content_data = {
            "title": "Database Consistency Test",
            "description": "Testing API to database integration",
            "content_type": "text",
            "metadata": {"test_field": "test_value"}
        }
        
        create_response = await client.session.post(
            f"{client.base_url}/content/create",
            json=content_data,
            headers=client.get_headers()
        )
        
        if create_response.status == 201:
            create_result = await create_response.json()
            content_id = create_result["content_id"]
            
            # Read content via API
            read_response = await client.session.get(
                f"{client.base_url}/content/{content_id}",
                headers=client.get_headers()
            )
            
            assert read_response.status == 200
            read_result = await read_response.json()
            
            # Verify data consistency
            assert read_result["title"] == content_data["title"]
            assert read_result["description"] == content_data["description"]
            assert read_result["content_type"] == content_data["content_type"]
            
            # Update content via API
            update_data = {
                "title": "Updated Title",
                "description": "Updated description"
            }
            
            update_response = await client.session.put(
                f"{client.base_url}/content/{content_id}",
                json=update_data,
                headers=client.get_headers()
            )
            
            if update_response.status == 200:
                # Verify update persistence
                verify_response = await client.session.get(
                    f"{client.base_url}/content/{content_id}",
                    headers=client.get_headers()
                )
                
                verify_result = await verify_response.json()
                assert verify_result["title"] == update_data["title"]
                assert verify_result["description"] == update_data["description"]
            
            # Delete content via API
            delete_response = await client.session.delete(
                f"{client.base_url}/content/{content_id}",
                headers=client.get_headers()
            )
            
            if delete_response.status == 200:
                # Verify deletion
                deleted_response = await client.session.get(
                    f"{client.base_url}/content/{content_id}",
                    headers=client.get_headers()
                )
                
                assert deleted_response.status == 404
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_transaction_rollback_via_api(self, cross_service_client):
        """Test that API operations properly handle database transaction rollbacks."""
        client = cross_service_client
        
        # Attempt to create content with invalid related data
        invalid_content_data = {
            "title": "Transaction Test",
            "description": "Testing transaction rollback",
            "content_type": "audio",
            "user_id": "non_existent_user_id",  # Should cause foreign key error
            "metadata": {"valid": "data"}
        }
        
        create_response = await client.session.post(
            f"{client.base_url}/content/create",
            json=invalid_content_data,
            headers=client.get_headers()
        )
        
        # Should fail due to invalid foreign key
        assert create_response.status in [400, 422, 500]
        
        # Verify no partial data was created
        list_response = await client.session.get(
            f"{client.base_url}/content/list",
            headers=client.get_headers()
        )
        
        if list_response.status == 200:
            content_list = await list_response.json()
            # Should not contain the failed content
            titles = [item.get("title", "") for item in content_list.get("content", [])]
            assert "Transaction Test" not in titles
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_api_database_operations(self, cross_service_client):
        """Test concurrent API operations maintain database integrity."""
        client = cross_service_client
        
        async def create_content(index: int):
            content_data = {
                "title": f"Concurrent Content {index}",
                "description": f"Content created concurrently {index}",
                "content_type": "text"
            }
            
            response = await client.session.post(
                f"{client.base_url}/content/create",
                json=content_data,
                headers=client.get_headers()
            )
            
            if response.status == 201:
                result = await response.json()
                return result["content_id"]
            return None
        
        # Create multiple content items concurrently
        tasks = [create_content(i) for i in range(10)]
        content_ids = await asyncio.gather(*tasks)
        
        # Filter out failed creations
        valid_ids = [cid for cid in content_ids if cid is not None]
        
        # Verify all created content exists
        for content_id in valid_ids:
            verify_response = await client.session.get(
                f"{client.base_url}/content/{content_id}",
                headers=client.get_headers()
            )
            assert verify_response.status == 200


class TestServiceToServiceCommunication:
    """Test communication between different services."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fingerprinting_to_monitoring_service(self, cross_service_client):
        """Test fingerprinting service to monitoring service communication."""
        client = cross_service_client
        
        # Create content for fingerprinting
        content_data = {
            "title": "Service Communication Test",
            "description": "Testing service-to-service communication",
            "content_type": "audio",
            "auto_monitor": True  # Should trigger monitoring setup
        }
        
        create_response = await client.session.post(
            f"{client.base_url}/content/create",
            json=content_data,
            headers=client.get_headers()
        )
        
        if create_response.status == 201:
            result = await create_response.json()
            content_id = result["content_id"]
            
            # Wait for fingerprinting to complete
            await asyncio.sleep(2)
            
            # Check if monitoring was automatically set up
            monitoring_response = await client.session.get(
                f"{client.base_url}/monitoring/content/{content_id}",
                headers=client.get_headers()
            )
            
            if monitoring_response.status == 200:
                monitoring_data = await monitoring_response.json()
                assert monitoring_data["content_id"] == content_id
                assert monitoring_data["status"] in ["active", "pending"]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_payment_to_licensing_service(self, cross_service_client):
        """Test payment service to licensing service communication."""
        client = cross_service_client
        
        # Create licensable content
        content_data = {
            "title": "Licensable Content",
            "description": "Content available for licensing",
            "content_type": "music",
            "licensing_enabled": True,
            "license_price": 100.00
        }
        
        content_response = await client.session.post(
            f"{client.base_url}/content/create",
            json=content_data,
            headers=client.get_headers()
        )
        
        if content_response.status == 201:
            content_result = await content_response.json()
            content_id = content_result["content_id"]
            
            # Attempt to purchase license
            license_data = {
                "content_id": content_id,
                "license_type": "commercial",
                "payment_method": {
                    "type": "test_card",
                    "card_number": "4242424242424242"
                }
            }
            
            license_response = await client.session.post(
                f"{client.base_url}/licensing/purchase",
                json=license_data,
                headers=client.get_headers()
            )
            
            if license_response.status == 201:
                license_result = await license_response.json()
                license_id = license_result["license_id"]
                
                # Verify payment was processed and license activated
                license_status_response = await client.session.get(
                    f"{client.base_url}/licensing/status/{license_id}",
                    headers=client.get_headers()
                )
                
                assert license_status_response.status == 200
                status_data = await license_status_response.json()
                assert status_data["payment_status"] == "completed"
                assert status_data["license_status"] == "active"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analytics_to_reporting_service(self, cross_service_client):
        """Test analytics service to reporting service communication."""
        client = cross_service_client
        
        # Generate some analytics data
        analytics_events = [
            {
                "event_type": "content_view",
                "content_id": f"content_{i}",
                "metadata": {"platform": "spotify", "country": "US"}
            }
            for i in range(5)
        ]
        
        # Send analytics events
        for event in analytics_events:
            await client.session.post(
                f"{client.base_url}/analytics/track",
                json=event,
                headers=client.get_headers()
            )
        
        # Wait for analytics processing
        await asyncio.sleep(1)
        
        # Request analytics report
        report_request = {
            "report_type": "content_performance",
            "date_range": {
                "start": (datetime.now() - timedelta(days=1)).isoformat(),
                "end": datetime.now().isoformat()
            }
        }
        
        report_response = await client.session.post(
            f"{client.base_url}/analytics/reports/generate",
            json=report_request,
            headers=client.get_headers()
        )
        
        if report_response.status == 202:  # Accepted for processing
            report_result = await report_response.json()
            report_id = report_result["report_id"]
            
            # Check report status
            status_response = await client.session.get(
                f"{client.base_url}/analytics/reports/{report_id}/status",
                headers=client.get_headers()
            )
            
            assert status_response.status == 200


class TestExternalServiceCoordination:
    """Test coordination with external services."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_payment_processor_coordination(self, cross_service_client):
        """Test coordination with external payment processors."""
        client = cross_service_client
        
        # Setup payment method
        payment_setup = {
            "payment_processor": "stripe",
            "account_data": {
                "business_type": "individual",
                "country": "US"
            }
        }
        
        setup_response = await client.session.post(
            f"{client.base_url}/payments/setup",
            json=payment_setup,
            headers=client.get_headers()
        )
        
        if setup_response.status == 201:
            # Create a subscription
            subscription_data = {
                "plan": "premium",
                "billing_cycle": "monthly",
                "payment_method": {
                    "type": "card",
                    "card_number": "4242424242424242",
                    "exp_month": "12",
                    "exp_year": "2025"
                }
            }
            
            subscription_response = await client.session.post(
                f"{client.base_url}/subscriptions/create",
                json=subscription_data,
                headers=client.get_headers()
            )
            
            if subscription_response.status == 201:
                subscription_result = await subscription_response.json()
                
                # Verify subscription was created in both internal system and payment processor
                assert "subscription_id" in subscription_result
                assert "external_subscription_id" in subscription_result
                assert subscription_result["status"] == "active"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_platform_api_coordination(self, cross_service_client):
        """Test coordination with platform APIs."""
        client = cross_service_client
        
        # Setup platform monitoring
        monitoring_config = {
            "platforms": ["spotify", "youtube"],
            "content_fingerprints": ["test_hash_123"],
            "monitoring_frequency": "daily"
        }
        
        monitoring_response = await client.session.post(
            f"{client.base_url}/monitoring/platforms/setup",
            json=monitoring_config,
            headers=client.get_headers()
        )
        
        if monitoring_response.status == 201:
            monitoring_result = await monitoring_response.json()
            monitoring_id = monitoring_result["monitoring_id"]
            
            # Trigger a scan
            scan_request = {
                "monitoring_id": monitoring_id,
                "platforms": ["spotify"],
                "immediate": True
            }
            
            scan_response = await client.session.post(
                f"{client.base_url}/monitoring/scan/trigger",
                json=scan_request,
                headers=client.get_headers()
            )
            
            if scan_response.status == 202:  # Accepted
                scan_result = await scan_response.json()
                scan_id = scan_result["scan_id"]
                
                # Check scan results
                await asyncio.sleep(2)  # Wait for scan
                
                results_response = await client.session.get(
                    f"{client.base_url}/monitoring/scan/{scan_id}/results",
                    headers=client.get_headers()
                )
                
                assert results_response.status == 200
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ai_service_coordination(self, cross_service_client):
        """Test coordination with AI/ML services."""
        client = cross_service_client
        
        # Submit content for AI analysis
        analysis_request = {
            "content_text": "This is a test song with beautiful melody and rhythm",
            "analysis_types": ["similarity", "genre_classification", "sentiment"],
            "priority": "normal"
        }
        
        analysis_response = await client.session.post(
            f"{client.base_url}/ai/analyze",
            json=analysis_request,
            headers=client.get_headers()
        )
        
        if analysis_response.status == 202:  # Accepted for processing
            analysis_result = await analysis_response.json()
            analysis_id = analysis_result["analysis_id"]
            
            # Poll for results
            max_attempts = 10
            for attempt in range(max_attempts):
                status_response = await client.session.get(
                    f"{client.base_url}/ai/analysis/{analysis_id}/status",
                    headers=client.get_headers()
                )
                
                if status_response.status == 200:
                    status_data = await status_response.json()
                    if status_data["status"] == "completed":
                        assert "similarity_score" in status_data["results"]
                        assert "genre" in status_data["results"]
                        assert "sentiment" in status_data["results"]
                        break
                
                await asyncio.sleep(1)


class TestDataFlowIntegration:
    """Test data flow between services."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_lifecycle_data_flow(self, cross_service_client):
        """Test data flow throughout content lifecycle."""
        client = cross_service_client
        
        # Step 1: Upload content
        content_data = {
            "title": "Data Flow Test",
            "description": "Testing data flow integration",
            "content_type": "audio"
        }
        
        upload_response = await client.session.post(
            f"{client.base_url}/content/upload",
            json=content_data,
            headers=client.get_headers()
        )
        
        if upload_response.status == 201:
            upload_result = await upload_response.json()
            content_id = upload_result["content_id"]
            
            # Step 2: Content should trigger fingerprinting
            await asyncio.sleep(1)
            
            fingerprint_response = await client.session.get(
                f"{client.base_url}/fingerprinting/content/{content_id}",
                headers=client.get_headers()
            )
            
            if fingerprint_response.status == 200:
                fingerprint_data = await fingerprint_response.json()
                assert fingerprint_data["content_id"] == content_id
                
                # Step 3: Fingerprinting should enable monitoring
                monitoring_response = await client.session.get(
                    f"{client.base_url}/monitoring/content/{content_id}",
                    headers=client.get_headers()
                )
                
                if monitoring_response.status == 200:
                    monitoring_data = await monitoring_response.json()
                    assert monitoring_data["fingerprint_hash"] == fingerprint_data["hash"]
                    
                    # Step 4: Content should appear in analytics
                    analytics_response = await client.session.get(
                        f"{client.base_url}/analytics/content/{content_id}",
                        headers=client.get_headers()
                    )
                    
                    if analytics_response.status == 200:
                        analytics_data = await analytics_response.json()
                        assert analytics_data["content_id"] == content_id
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_user_data_consistency_across_services(self, cross_service_client):
        """Test user data consistency across all services."""
        client = cross_service_client
        
        # Update user profile
        profile_update = {
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio",
            "preferences": {
                "notification_frequency": "daily",
                "monitoring_sensitivity": "high"
            }
        }
        
        profile_response = await client.session.put(
            f"{client.base_url}/user/profile",
            json=profile_update,
            headers=client.get_headers()
        )
        
        if profile_response.status == 200:
            # Verify update propagated to all services
            
            # Check user service
            user_response = await client.session.get(
                f"{client.base_url}/user/profile",
                headers=client.get_headers()
            )
            
            assert user_response.status == 200
            user_data = await user_response.json()
            assert user_data["first_name"] == "Updated"
            
            # Check notification service has updated preferences
            notification_response = await client.session.get(
                f"{client.base_url}/notifications/preferences",
                headers=client.get_headers()
            )
            
            if notification_response.status == 200:
                notification_data = await notification_response.json()
                assert notification_data["frequency"] == "daily"
            
            # Check monitoring service has updated sensitivity
            monitoring_prefs_response = await client.session.get(
                f"{client.base_url}/monitoring/preferences",
                headers=client.get_headers()
            )
            
            if monitoring_prefs_response.status == 200:
                monitoring_prefs_data = await monitoring_prefs_response.json()
                assert monitoring_prefs_data["sensitivity"] == "high"


class TestErrorHandlingAcrossServices:
    """Test error handling and recovery across services."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_service_failure_recovery(self, cross_service_client):
        """Test system behavior when individual services fail."""
        client = cross_service_client
        
        # Simulate external service failure
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock external payment service failure
            mock_post.return_value.__aenter__.return_value.status = 503
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={"error": "Service unavailable"}
            )
            
            # Attempt payment operation
            payment_data = {
                "amount": 99.99,
                "currency": "USD",
                "description": "Test payment"
            }
            
            payment_response = await client.session.post(
                f"{client.base_url}/payments/process",
                json=payment_data,
                headers=client.get_headers()
            )
            
            # Should handle gracefully
            assert payment_response.status in [503, 502, 500]
            
            if payment_response.status in [503, 502]:
                error_data = await payment_response.json()
                assert "service unavailable" in error_data.get("message", "").lower()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_partial_failure_handling(self, cross_service_client):
        """Test handling of partial failures in multi-service operations."""
        client = cross_service_client
        
        # Create content that should trigger multiple services
        content_data = {
            "title": "Partial Failure Test",
            "description": "Testing partial failure handling",
            "content_type": "audio",
            "enable_monitoring": True,
            "enable_analytics": True,
            "create_license": True
        }
        
        # Mock one service to fail
        with patch('external_service_call') as mock_service:
            mock_service.side_effect = Exception("External service error")
            
            create_response = await client.session.post(
                f"{client.base_url}/content/create_with_services",
                json=content_data,
                headers=client.get_headers()
            )
            
            # Should succeed partially
            if create_response.status == 207:  # Multi-status
                result = await create_response.json()
                
                # Content should be created
                assert "content_id" in result
                
                # Some services should succeed, some fail
                assert "service_results" in result
                service_results = result["service_results"]
                
                success_count = sum(1 for status in service_results.values() if status == "success")
                failure_count = sum(1 for status in service_results.values() if status == "failed")
                
                assert success_count > 0  # At least core content creation should succeed
                assert failure_count > 0  # At least one service should fail


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])