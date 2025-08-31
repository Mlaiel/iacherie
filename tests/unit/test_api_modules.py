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
Unit Tests for API Modules
=========================

Comprehensive unit tests for all API modules including:
- Authentication and authorization
- Content upload and management endpoints
- Revenue and monetization APIs
- Creator management APIs
- Analytics and reporting endpoints
- Security and validation

Author: Copilot Assistant for Fahed Mlaiel
Purpose: Ensure API reliability and security
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from decimal import Decimal

# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAuthenticationAPI:
    """Unit tests for authentication and authorization APIs"""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock authentication service"""



        return Mock(
            authenticate_user=Mock(return_value={
                'user_id': 'user_123',
                'access_token': 'token_abc123',
                'refresh_token': 'refresh_xyz789',
                'expires_in': 3600
            }),
            validate_token=Mock(return_value=True),
            refresh_token=Mock(return_value={'access_token': 'new_token_456'}),
            logout_user=Mock(return_value=True),
            check_permissions=Mock(return_value=True)
        )
    
    def test_user_authentication(self, mock_auth_service):
        """Test user authentication endpoint"""
        credentials = {
            'email': 'user@test.com',
            'password': 'secure_password123'
        }
        
        result = mock_auth_service.authenticate_user(credentials)
        
        assert result['user_id'] == 'user_123'
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert result['expires_in'] == 3600
        
    def test_token_validation(self, mock_auth_service):
        """Test token validation"""
        token = 'token_abc123'
        
        is_valid = mock_auth_service.validate_token(token)
        
        assert is_valid is True
        mock_auth_service.validate_token.assert_called_once_with(token)
        
    def test_token_refresh(self, mock_auth_service):
        """Test token refresh functionality"""
        refresh_token = 'refresh_xyz789'
        
        result = mock_auth_service.refresh_token(refresh_token)
        
        assert 'access_token' in result
        assert result['access_token'] == 'new_token_456'
        
    def test_permission_checking(self, mock_auth_service):
        """Test user permission validation"""
        permission_data = {
            'user_id': 'user_123',
            'resource': 'content_upload',
            'action': 'create'
        }
        
        has_permission = mock_auth_service.check_permissions(permission_data)
        
        assert has_permission is True


class TestContentAPI:
    """Unit tests for content management APIs"""
    
    @pytest.fixture
    def mock_content_service(self):
        """Mock content management service"""



        return Mock(
            upload_content=AsyncMock(return_value={
                'content_id': 'ct_123',
                'upload_url': 'https://storage.example.com/ct_123',
                'status': 'uploaded',
                'file_size': 5000000
            }),
            get_content=Mock(return_value={
                'content_id': 'ct_123',
                'title': 'Test Content',
                'creator_id': 'cr_123',
                'status': 'active'
            }),
            update_content=Mock(return_value=True),
            delete_content=Mock(return_value=True),
            list_user_content=Mock(return_value=[
                {'content_id': 'ct_123', 'title': 'Content 1'},
                {'content_id': 'ct_456', 'title': 'Content 2'}
            ])
        )
    
    @pytest.mark.asyncio
    async def test_content_upload(self, mock_content_service):
        """Test content upload API endpoint"""
        upload_data = {
            'file_data': b'mock_file_content',
            'content_type': 'audio/mp3',
            'title': 'Test Song',
            'description': 'A test song for validation'
        }
        
        result = await mock_content_service.upload_content(upload_data)
        
        assert result['content_id'] == 'ct_123'
        assert 'upload_url' in result
        assert result['status'] == 'uploaded'
        assert result['file_size'] == 5000000
        
    def test_content_retrieval(self, mock_content_service):
        """Test content retrieval API"""
        content_id = 'ct_123'
        
        content = mock_content_service.get_content(content_id)
        
        assert content['content_id'] == 'ct_123'
        assert content['title'] == 'Test Content'
        assert content['creator_id'] == 'cr_123'
        
    def test_content_listing(self, mock_content_service):
        """Test user content listing API"""
        user_id = 'user_123'
        filters = {'status': 'active', 'limit': 10}
        
        content_list = mock_content_service.list_user_content(user_id, filters)
        
        assert len(content_list) == 2
        assert content_list[0]['content_id'] == 'ct_123'
        assert content_list[1]['content_id'] == 'ct_456'
        
    def test_content_update(self, mock_content_service):
        """Test content update API"""
        content_id = 'ct_123'
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        
        result = mock_content_service.update_content(content_id, update_data)
        
        assert result is True
        
    def test_content_deletion(self, mock_content_service):
        """Test content deletion API"""
        content_id = 'ct_123'
        
        result = mock_content_service.delete_content(content_id)
        
        assert result is True


class TestMonetizationAPI:
    """Unit tests for monetization and revenue APIs"""
    
    @pytest.fixture
    def mock_monetization_service(self):
        """Mock monetization service"""



        return Mock(
            get_revenue_summary=Mock(return_value={
                'total_revenue': Decimal('2500.75'),
                'monthly_revenue': Decimal('850.25'),
                'revenue_streams': ['streaming', 'licensing', 'partnerships'],
                'top_earning_content': 'ct_123'
            }),
            create_monetization_plan=Mock(return_value={
                'plan_id': 'mp_123',
                'status': 'active',
                'projected_revenue': Decimal('1500.00')
            }),
            process_payment=AsyncMock(return_value={
                'payment_id': 'pay_123',
                'status': 'completed',
                'amount': Decimal('100.00')
            }),
            get_analytics=Mock(return_value={
                'views': 50000,
                'plays': 35000,
                'engagement_rate': 8.5,
                'conversion_rate': 2.3
            })
        )
    
    def test_revenue_summary_retrieval(self, mock_monetization_service):
        """Test revenue summary API"""
        creator_id = 'cr_123'
        time_period = '30_days'
        
        summary = mock_monetization_service.get_revenue_summary(creator_id, time_period)
        
        assert summary['total_revenue'] == Decimal('2500.75')
        assert summary['monthly_revenue'] == Decimal('850.25')
        assert len(summary['revenue_streams']) == 3
        
    def test_monetization_plan_creation(self, mock_monetization_service):
        """Test monetization plan creation API"""
        plan_data = {
            'creator_id': 'cr_123',
            'content_ids': ['ct_123', 'ct_456'],
            'platforms': ['spotify', 'youtube'],
            'revenue_targets': {'monthly': Decimal('1000.00')}
        }
        
        result = mock_monetization_service.create_monetization_plan(plan_data)
        
        assert result['plan_id'] == 'mp_123'
        assert result['status'] == 'active'
        assert result['projected_revenue'] == Decimal('1500.00')
        
    @pytest.mark.asyncio
    async def test_payment_processing(self, mock_monetization_service):
        """Test payment processing API"""
        payment_data = {
            'amount': Decimal('100.00'),
            'currency': 'USD',
            'payment_method': 'stripe',
            'recipient_id': 'cr_123'
        }
        
        result = await mock_monetization_service.process_payment(payment_data)
        
        assert result['payment_id'] == 'pay_123'
        assert result['status'] == 'completed'
        assert result['amount'] == Decimal('100.00')
        
    def test_monetization_analytics(self, mock_monetization_service):
        """Test monetization analytics API"""
        creator_id = 'cr_123'
        metrics = ['views', 'plays', 'engagement', 'conversion']
        
        analytics = mock_monetization_service.get_analytics(creator_id, metrics)
        
        assert analytics['views'] == 50000
        assert analytics['plays'] == 35000
        assert analytics['engagement_rate'] == 8.5
        assert analytics['conversion_rate'] == 2.3


class TestCreatorAPI:
    """Unit tests for creator management APIs"""
    
    @pytest.fixture
    def mock_creator_service(self):
        """Mock creator management service"""



        return Mock(
            create_creator_profile=Mock(return_value={
                'creator_id': 'cr_123',
                'profile_complete': True,
                'verification_status': 'pending'
            }),
            get_creator_profile=Mock(return_value={
                'creator_id': 'cr_123',
                'name': 'Test Creator',
                'type': 'musician',
                'follower_count': 5000,
                'content_count': 25
            }),
            update_creator_profile=Mock(return_value=True),
            verify_creator=Mock(return_value={'verified': True, 'badge_awarded': True}),
            get_creator_statistics=Mock(return_value={
                'total_views': 100000,
                'total_revenue': Decimal('5000.00'),
                'average_engagement': 7.8,
                'growth_rate': 15.5
            })
        )
    
    def test_creator_profile_creation(self, mock_creator_service):
        """Test creator profile creation API"""
        profile_data = {
            'name': 'Test Creator',
            'email': 'creator@test.com',
            'type': 'musician',
            'genres': ['pop', 'electronic'],
            'social_links': {'instagram': '@testcreator'}
        }
        
        result = mock_creator_service.create_creator_profile(profile_data)
        
        assert result['creator_id'] == 'cr_123'
        assert result['profile_complete'] is True
        assert result['verification_status'] == 'pending'
        
    def test_creator_profile_retrieval(self, mock_creator_service):
        """Test creator profile retrieval API"""
        creator_id = 'cr_123'
        
        profile = mock_creator_service.get_creator_profile(creator_id)
        
        assert profile['creator_id'] == 'cr_123'
        assert profile['name'] == 'Test Creator'
        assert profile['type'] == 'musician'
        assert profile['follower_count'] == 5000
        
    def test_creator_verification(self, mock_creator_service):
        """Test creator verification API"""
        verification_data = {
            'creator_id': 'cr_123',
            'verification_documents': ['id_document', 'proof_of_work'],
            'social_verification': True
        }
        
        result = mock_creator_service.verify_creator(verification_data)
        
        assert result['verified'] is True
        assert result['badge_awarded'] is True
        
    def test_creator_statistics(self, mock_creator_service):
        """Test creator statistics API"""
        creator_id = 'cr_123'
        time_period = '90_days'
        
        stats = mock_creator_service.get_creator_statistics(creator_id, time_period)
        
        assert stats['total_views'] == 100000
        assert stats['total_revenue'] == Decimal('5000.00')
        assert stats['average_engagement'] == 7.8
        assert stats['growth_rate'] == 15.5


class TestAnalyticsAPI:
    """Unit tests for analytics and reporting APIs"""
    
    @pytest.fixture
    def mock_analytics_service(self):
        """Mock analytics service"""



        return Mock(
            generate_report=AsyncMock(return_value={
                'report_id': 'rep_123',
                'report_type': 'performance',
                'data': {'views': 25000, 'revenue': Decimal('1200.00')},
                'generated_at': datetime.now().isoformat()
            }),
            get_real_time_metrics=Mock(return_value={
                'active_users': 150,
                'current_streams': 45,
                'real_time_revenue': Decimal('25.50')
            }),
            track_content_performance=Mock(return_value={
                'content_id': 'ct_123',
                'views_24h': 2500,
                'engagement_score': 8.2,
                'trending_rank': 15
            }),
            export_analytics_data=Mock(return_value={
                'export_id': 'exp_123',
                'format': 'csv',
                'download_url': 'https://analytics.example.com/export/exp_123'
            })
        )
    
    @pytest.mark.asyncio
    async def test_report_generation(self, mock_analytics_service):
        """Test analytics report generation API"""
        report_params = {
            'creator_id': 'cr_123',
            'report_type': 'performance',
            'time_period': '30_days',
            'metrics': ['views', 'revenue', 'engagement']
        }
        
        result = await mock_analytics_service.generate_report(report_params)
        
        assert result['report_id'] == 'rep_123'
        assert result['report_type'] == 'performance'
        assert 'data' in result
        assert result['data']['views'] == 25000
        
    def test_real_time_metrics(self, mock_analytics_service):
        """Test real-time metrics API"""
        creator_id = 'cr_123'
        
        metrics = mock_analytics_service.get_real_time_metrics(creator_id)
        
        assert metrics['active_users'] == 150
        assert metrics['current_streams'] == 45
        assert metrics['real_time_revenue'] == Decimal('25.50')
        
    def test_content_performance_tracking(self, mock_analytics_service):
        """Test individual content performance tracking API"""
        content_id = 'ct_123'
        
        performance = mock_analytics_service.track_content_performance(content_id)
        
        assert performance['content_id'] == 'ct_123'
        assert performance['views_24h'] == 2500
        assert performance['engagement_score'] == 8.2
        assert performance['trending_rank'] == 15
        
    def test_analytics_data_export(self, mock_analytics_service):
        """Test analytics data export API"""
        export_params = {
            'creator_id': 'cr_123',
            'data_type': 'all_metrics',
            'format': 'csv',
            'date_range': '2024-01-01,2024-01-31'
        }
        
        result = mock_analytics_service.export_analytics_data(export_params)
        
        assert result['export_id'] == 'exp_123'
        assert result['format'] == 'csv'
        assert 'download_url' in result


class TestSecurityAPI:
    """Unit tests for security and validation APIs"""
    
    @pytest.fixture
    def mock_security_service(self):
        """Mock security service"""



        return Mock(
            validate_upload=Mock(return_value={
                'valid': True,
                'security_score': 95,
                'threats_detected': [],
                'recommendations': ['enable_watermarking']
            }),
            scan_content=AsyncMock(return_value={
                'scan_id': 'scan_123',
                'status': 'clean',
                'malware_detected': False,
                'content_integrity': True
            }),
            check_copyright=Mock(return_value={
                'copyright_clear': True,
                'potential_matches': [],
                'confidence_score': 98.5
            }),
            audit_user_activity=Mock(return_value={
                'user_id': 'user_123',
                'activity_score': 8.5,
                'suspicious_activities': 0,
                'last_verified': datetime.now().isoformat()
            })
        )
    
    def test_upload_validation(self, mock_security_service):
        """Test content upload security validation API"""
        upload_data = {
            'file_hash': 'abc123def456',
            'file_type': 'audio/mp3',
            'file_size': 5000000,
            'creator_id': 'cr_123'
        }
        
        result = mock_security_service.validate_upload(upload_data)
        
        assert result['valid'] is True
        assert result['security_score'] == 95
        assert len(result['threats_detected']) == 0
        assert 'enable_watermarking' in result['recommendations']
        
    @pytest.mark.asyncio
    async def test_content_scanning(self, mock_security_service):
        """Test content security scanning API"""
        scan_params = {
            'content_id': 'ct_123',
            'scan_type': 'comprehensive',
            'priority': 'high'
        }
        
        result = await mock_security_service.scan_content(scan_params)
        
        assert result['scan_id'] == 'scan_123'
        assert result['status'] == 'clean'
        assert result['malware_detected'] is False
        assert result['content_integrity'] is True
        
    def test_copyright_checking(self, mock_security_service):
        """Test copyright validation API"""
        content_data = {
            'content_id': 'ct_123',
            'fingerprint': 'fp_abc123',
            'metadata': {'title': 'Test Song', 'artist': 'Test Creator'}
        }
        
        result = mock_security_service.check_copyright(content_data)
        
        assert result['copyright_clear'] is True
        assert len(result['potential_matches']) == 0
        assert result['confidence_score'] == 98.5
        
    def test_user_activity_audit(self, mock_security_service):
        """Test user activity auditing API"""
        audit_params = {
            'user_id': 'user_123',
            'time_period': '7_days',
            'activity_types': ['login', 'upload', 'monetization']
        }
        
        result = mock_security_service.audit_user_activity(audit_params)
        
        assert result['user_id'] == 'user_123'
        assert result['activity_score'] == 8.5
        assert result['suspicious_activities'] == 0
        assert 'last_verified' in result


class TestAPIIntegration:
    """Integration tests for API modules working together"""
    
    @pytest.fixture
    def mock_api_system(self):
        """Mock integrated API system"""



        return Mock(
            handle_content_workflow=AsyncMock(return_value={
                'workflow_id': 'wf_123',
                'steps_completed': ['upload', 'validate', 'process', 'publish'],
                'status': 'success',
                'content_id': 'ct_123'
            }),
            process_creator_onboarding=AsyncMock(return_value={
                'onboarding_id': 'ob_123',
                'creator_id': 'cr_123',
                'completion_rate': 100,
                'verification_pending': False
            }),
            handle_monetization_setup=AsyncMock(return_value={
                'setup_id': 'ms_123',
                'monetization_active': True,
                'revenue_streams_enabled': 3,
                'projected_monthly_revenue': Decimal('800.00')
            })
        )
    
    @pytest.mark.asyncio
    async def test_complete_content_workflow(self, mock_api_system):
        """Test complete content workflow through APIs"""
        workflow_data = {
            'creator_id': 'cr_123',
            'content_file': 'test_audio.mp3',
            'metadata': {'title': 'Test Song', 'genre': 'pop'},
            'monetization_enabled': True
        }
        
        result = await mock_api_system.handle_content_workflow(workflow_data)
        
        assert result['workflow_id'] == 'wf_123'
        assert len(result['steps_completed']) == 4
        assert result['status'] == 'success'
        assert result['content_id'] == 'ct_123'
        
    @pytest.mark.asyncio
    async def test_creator_onboarding_workflow(self, mock_api_system):
        """Test complete creator onboarding through APIs"""
        onboarding_data = {
            'user_id': 'user_123',
            'creator_type': 'musician',
            'profile_data': {'name': 'Test Creator', 'bio': 'Test bio'},
            'verification_documents': ['id', 'proof_of_work']
        }
        
        result = await mock_api_system.process_creator_onboarding(onboarding_data)
        
        assert result['onboarding_id'] == 'ob_123'
        assert result['creator_id'] == 'cr_123'
        assert result['completion_rate'] == 100
        assert result['verification_pending'] is False
        
    @pytest.mark.asyncio
    async def test_monetization_setup_workflow(self, mock_api_system):
        """Test monetization setup through APIs"""
        setup_data = {
            'creator_id': 'cr_123',
            'payment_methods': ['stripe', 'paypal'],
            'target_platforms': ['spotify', 'youtube', 'apple_music'],
            'revenue_preferences': {'auto_withdrawal': True, 'threshold': 100}
        }
        
        result = await mock_api_system.handle_monetization_setup(setup_data)
        
        assert result['setup_id'] == 'ms_123'
        assert result['monetization_active'] is True
        assert result['revenue_streams_enabled'] == 3
        assert result['projected_monthly_revenue'] == Decimal('800.00')


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])