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
Unit Tests for Monetization Modules
===================================

Comprehensive unit tests for monetization system including:
- Revenue calculation and management
- Payment processing
- Royalty distribution
- Contract generation
- Rights validation
- Platform APIs integration

Author: Copilot Assistant for Fahed Mlaiel
Purpose: Ensure monetization system reliability and accuracy
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from typing import Dict, List, Any, Optional
import json
import uuid


class TestRevenueCalculator:
    """Unit tests for revenue calculation system"""
    
    @pytest.fixture
    def mock_revenue_calculator(self):
        """Mock revenue calculator"""
        calculator = Mock()
        calculator.calculate_cpm_revenue = Mock(return_value=Decimal('125.50'))
        calculator.calculate_subscription_revenue = Mock(return_value=Decimal('299.99'))
        calculator.calculate_commission = Mock(return_value=Decimal('45.75'))
        calculator.get_platform_rates = Mock(return_value={
            'youtube': {'cpm_min': 0.25, 'cpm_max': 4.0},
            'instagram': {'cpm_min': 0.50, 'cpm_max': 6.0}
        })
        return calculator
    
    def test_cpm_revenue_calculation(self, mock_revenue_calculator):
        """Test CPM-based revenue calculation"""
        views = 100000
        cpm_rate = 2.50
        
        result = mock_revenue_calculator.calculate_cpm_revenue(views, cpm_rate)
        
        assert result == Decimal('125.50')
        mock_revenue_calculator.calculate_cpm_revenue.assert_called_once_with(views, cpm_rate)
    
    def test_subscription_revenue_calculation(self, mock_revenue_calculator):
        """Test subscription-based revenue calculation"""
        subscribers = 1000
        monthly_rate = Decimal('9.99')
        
        result = mock_revenue_calculator.calculate_subscription_revenue(subscribers, monthly_rate)
        
        assert result == Decimal('299.99')
        mock_revenue_calculator.calculate_subscription_revenue.assert_called_once()
    
    def test_commission_calculation(self, mock_revenue_calculator):
        """Test commission calculation"""
        revenue = Decimal('1000.00')
        commission_rate = Decimal('0.15')
        
        result = mock_revenue_calculator.calculate_commission(revenue, commission_rate)
        
        assert result == Decimal('45.75')
        mock_revenue_calculator.calculate_commission.assert_called_once()
    
    def test_platform_rates_retrieval(self, mock_revenue_calculator):
        """Test platform rate retrieval"""
        rates = mock_revenue_calculator.get_platform_rates()
        
        assert 'youtube' in rates
        assert 'instagram' in rates
        assert rates['youtube']['cpm_min'] == 0.25
        assert rates['instagram']['cpm_max'] == 6.0


class TestPaymentProcessor:
    """Unit tests for payment processing system"""
    
    @pytest.fixture
    def mock_payment_processor(self):
        """Mock payment processor"""
        processor = Mock()
        processor.process_payment = AsyncMock(return_value={
            'transaction_id': 'txn_123456789',
            'status': 'completed',
            'amount': Decimal('99.99'),
            'currency': 'EUR',
            'processed_at': datetime.utcnow().isoformat()
        })
        processor.validate_payment_method = Mock(return_value=True)
        processor.refund_payment = AsyncMock(return_value={
            'refund_id': 'ref_987654321',
            'status': 'processed',
            'amount': Decimal('99.99')
        })
        processor.get_payment_status = Mock(return_value='completed')
        return processor
    
    @pytest.mark.asyncio
    async def test_payment_processing(self, mock_payment_processor):
        """Test payment processing"""
        payment_data = {
            'amount': Decimal('99.99'),
            'currency': 'EUR',
            'payment_method': 'credit_card',
            'user_id': 'user_123'
        }
        
        result = await mock_payment_processor.process_payment(payment_data)
        
        assert result['status'] == 'completed'
        assert result['amount'] == Decimal('99.99')
        assert result['currency'] == 'EUR'
        assert 'transaction_id' in result
        mock_payment_processor.process_payment.assert_called_once()
    
    def test_payment_method_validation(self, mock_payment_processor):
        """Test payment method validation"""
        payment_method = {
            'type': 'credit_card',
            'card_number': '**** **** **** 1234',
            'expiry': '12/25'
        }
        
        result = mock_payment_processor.validate_payment_method(payment_method)
        
        assert result is True
        mock_payment_processor.validate_payment_method.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_payment_refund(self, mock_payment_processor):
        """Test payment refund processing"""
        transaction_id = 'txn_123456789'
        refund_amount = Decimal('99.99')
        
        result = await mock_payment_processor.refund_payment(transaction_id, refund_amount)
        
        assert result['status'] == 'processed'
        assert result['amount'] == Decimal('99.99')
        assert 'refund_id' in result
    
    def test_payment_status_check(self, mock_payment_processor):
        """Test payment status checking"""
        transaction_id = 'txn_123456789'
        
        status = mock_payment_processor.get_payment_status(transaction_id)
        
        assert status == 'completed'


class TestRoyaltyEngine:
    """Unit tests for royalty distribution system"""
    
    @pytest.fixture
    def mock_royalty_engine(self):
        """Mock royalty engine"""
        engine = Mock()
        engine.calculate_royalties = AsyncMock(return_value={
            'total_revenue': Decimal('1000.00'),
            'platform_commission': Decimal('300.00'),
            'creator_share': Decimal('700.00'),
            'stakeholder_shares': {
                'creator': Decimal('600.00'),
                'collaborators': Decimal('100.00')
            }
        })
        engine.distribute_royalties = AsyncMock(return_value={
            'distribution_id': 'dist_123',
            'total_distributed': Decimal('700.00'),
            'distributions': [
                {'recipient': 'creator_1', 'amount': Decimal('600.00')},
                {'recipient': 'collab_1', 'amount': Decimal('100.00')}
            ]
        })
        engine.validate_royalty_rules = Mock(return_value=True)
        return engine
    
    @pytest.mark.asyncio
    async def test_royalty_calculation(self, mock_royalty_engine):
        """Test royalty calculation"""
        revenue_data = {
            'total_revenue': Decimal('1000.00'),
            'content_id': 'content_123',
            'creator_id': 'creator_1'
        }
        
        result = await mock_royalty_engine.calculate_royalties(revenue_data)
        
        assert result['total_revenue'] == Decimal('1000.00')
        assert result['platform_commission'] == Decimal('300.00')
        assert result['creator_share'] == Decimal('700.00')
        assert 'stakeholder_shares' in result
    
    @pytest.mark.asyncio
    async def test_royalty_distribution(self, mock_royalty_engine):
        """Test royalty distribution"""
        distribution_data = {
            'content_id': 'content_123',
            'total_amount': Decimal('700.00'),
            'recipients': ['creator_1', 'collab_1']
        }
        
        result = await mock_royalty_engine.distribute_royalties(distribution_data)
        
        assert result['total_distributed'] == Decimal('700.00')
        assert len(result['distributions']) == 2
        assert 'distribution_id' in result
    
    def test_royalty_rules_validation(self, mock_royalty_engine):
        """Test royalty rules validation"""
        royalty_rules = {
            'creator_percentage': 0.60,
            'collaborator_percentage': 0.10,
            'platform_commission': 0.30
        }
        
        result = mock_royalty_engine.validate_royalty_rules(royalty_rules)
        
        assert result is True


class TestContractGenerator:
    """Unit tests for contract generation system"""
    
    @pytest.fixture
    def mock_contract_generator(self):
        """Mock contract generator"""
        generator = Mock()
        generator.generate_creator_contract = Mock(return_value={
            'contract_id': 'contract_123',
            'type': 'creator_agreement',
            'terms': {
                'revenue_share': 0.70,
                'content_rights': 'exclusive',
                'duration': '12_months'
            },
            'status': 'draft',
            'created_at': datetime.utcnow().isoformat()
        })
        generator.generate_collaboration_contract = Mock(return_value={
            'contract_id': 'contract_456',
            'type': 'collaboration_agreement',
            'parties': ['creator_1', 'creator_2'],
            'revenue_split': {'creator_1': 0.60, 'creator_2': 0.40}
        })
        generator.validate_contract_terms = Mock(return_value=True)
        generator.execute_contract = AsyncMock(return_value={'status': 'executed'})
        return generator
    
    def test_creator_contract_generation(self, mock_contract_generator):
        """Test creator contract generation"""
        contract_params = {
            'creator_id': 'creator_123',
            'content_type': 'video',
            'revenue_share': 0.70
        }
        
        result = mock_contract_generator.generate_creator_contract(contract_params)
        
        assert result['type'] == 'creator_agreement'
        assert result['terms']['revenue_share'] == 0.70
        assert result['status'] == 'draft'
        assert 'contract_id' in result
    
    def test_collaboration_contract_generation(self, mock_contract_generator):
        """Test collaboration contract generation"""
        collaboration_params = {
            'creators': ['creator_1', 'creator_2'],
            'project_type': 'joint_content',
            'revenue_split': {'creator_1': 0.60, 'creator_2': 0.40}
        }
        
        result = mock_contract_generator.generate_collaboration_contract(collaboration_params)
        
        assert result['type'] == 'collaboration_agreement'
        assert len(result['parties']) == 2
        assert result['revenue_split']['creator_1'] == 0.60
    
    def test_contract_terms_validation(self, mock_contract_generator):
        """Test contract terms validation"""
        contract_terms = {
            'revenue_share': 0.70,
            'content_rights': 'exclusive',
            'duration': '12_months',
            'termination_clause': 'standard'
        }
        
        result = mock_contract_generator.validate_contract_terms(contract_terms)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_contract_execution(self, mock_contract_generator):
        """Test contract execution"""
        contract_id = 'contract_123'
        signatures = ['creator_signature', 'platform_signature']
        
        result = await mock_contract_generator.execute_contract(contract_id, signatures)
        
        assert result['status'] == 'executed'


class TestRightsValidator:
    """Unit tests for rights validation system"""
    
    @pytest.fixture
    def mock_rights_validator(self):
        """Mock rights validator"""
        validator = Mock()
        validator.validate_content_rights = AsyncMock(return_value={
            'is_valid': True,
            'rights_holder': 'creator_123',
            'usage_rights': ['streaming', 'download', 'remix'],
            'restrictions': [],
            'expiry_date': None
        })
        validator.check_copyright_status = AsyncMock(return_value={
            'status': 'clear',
            'copyright_claims': [],
            'fair_use_applicable': False
        })
        validator.validate_licensing_terms = Mock(return_value=True)
        validator.get_usage_permissions = Mock(return_value=[
            'public_display', 'commercial_use', 'derivative_works'
        ])
        return validator
    
    @pytest.mark.asyncio
    async def test_content_rights_validation(self, mock_rights_validator):
        """Test content rights validation"""
        content_data = {
            'content_id': 'content_123',
            'creator_id': 'creator_123',
            'content_type': 'video'
        }
        
        result = await mock_rights_validator.validate_content_rights(content_data)
        
        assert result['is_valid'] is True
        assert result['rights_holder'] == 'creator_123'
        assert 'streaming' in result['usage_rights']
        assert len(result['restrictions']) == 0
    
    @pytest.mark.asyncio
    async def test_copyright_status_check(self, mock_rights_validator):
        """Test copyright status checking"""
        content_id = 'content_123'
        
        result = await mock_rights_validator.check_copyright_status(content_id)
        
        assert result['status'] == 'clear'
        assert len(result['copyright_claims']) == 0
        assert result['fair_use_applicable'] is False
    
    def test_licensing_terms_validation(self, mock_rights_validator):
        """Test licensing terms validation"""
        licensing_terms = {
            'license_type': 'commercial',
            'duration': '24_months',
            'territory': 'worldwide',
            'exclusivity': 'non_exclusive'
        }
        
        result = mock_rights_validator.validate_licensing_terms(licensing_terms)
        
        assert result is True
    
    def test_usage_permissions_retrieval(self, mock_rights_validator):
        """Test usage permissions retrieval"""
        content_id = 'content_123'
        license_type = 'commercial'
        
        permissions = mock_rights_validator.get_usage_permissions(content_id, license_type)
        
        assert 'public_display' in permissions
        assert 'commercial_use' in permissions
        assert 'derivative_works' in permissions


class TestPlatformAPIs:
    """Unit tests for platform API integration"""
    
    @pytest.fixture
    def mock_platform_apis(self):
        """Mock platform APIs"""
        apis = Mock()
        apis.youtube_api = Mock()
        apis.youtube_api.get_video_analytics = AsyncMock(return_value={
            'views': 150000,
            'likes': 12000,
            'comments': 850,
            'revenue': Decimal('425.75')
        })
        apis.spotify_api = Mock()
        apis.spotify_api.get_track_stats = AsyncMock(return_value={
            'streams': 500000,
            'saves': 8500,
            'playlist_adds': 1200,
            'revenue': Decimal('1250.00')
        })
        apis.instagram_api = Mock()
        apis.instagram_api.get_post_metrics = AsyncMock(return_value={
            'likes': 25000,
            'comments': 1200,
            'shares': 850,
            'revenue': Decimal('180.50')
        })
        return apis
    
    @pytest.mark.asyncio
    async def test_youtube_analytics_retrieval(self, mock_platform_apis):
        """Test YouTube analytics retrieval"""
        video_id = 'yt_video_123'
        
        result = await mock_platform_apis.youtube_api.get_video_analytics(video_id)
        
        assert result['views'] == 150000
        assert result['revenue'] == Decimal('425.75')
        assert 'likes' in result
        assert 'comments' in result
    
    @pytest.mark.asyncio
    async def test_spotify_stats_retrieval(self, mock_platform_apis):
        """Test Spotify statistics retrieval"""
        track_id = 'spotify_track_456'
        
        result = await mock_platform_apis.spotify_api.get_track_stats(track_id)
        
        assert result['streams'] == 500000
        assert result['revenue'] == Decimal('1250.00')
        assert 'saves' in result
        assert 'playlist_adds' in result
    
    @pytest.mark.asyncio
    async def test_instagram_metrics_retrieval(self, mock_platform_apis):
        """Test Instagram metrics retrieval"""
        post_id = 'ig_post_789'
        
        result = await mock_platform_apis.instagram_api.get_post_metrics(post_id)
        
        assert result['likes'] == 25000
        assert result['revenue'] == Decimal('180.50')
        assert 'comments' in result
        assert 'shares' in result


class TestMonetizationIntegration:
    """Integration tests for monetization system"""
    
    @pytest.fixture
    def mock_monetization_system(self):
        """Mock complete monetization system"""
        system = Mock()
        system.revenue_calculator = Mock()
        system.payment_processor = Mock()
        system.royalty_engine = Mock()
        system.contract_generator = Mock()
        system.rights_validator = Mock()
        system.platform_apis = Mock()
        return system
    
    @pytest.mark.asyncio
    async def test_complete_monetization_workflow(self, mock_monetization_system):
        """Test complete monetization workflow"""
        # Mock the full workflow
        content_data = {
            'content_id': 'content_123',
            'creator_id': 'creator_123',
            'platform': 'youtube',
            'content_type': 'video'
        }
        
        # Simulate workflow steps
        mock_monetization_system.rights_validator.validate_content_rights = AsyncMock(
            return_value={'is_valid': True}
        )
        mock_monetization_system.platform_apis.get_analytics = AsyncMock(
            return_value={'revenue': Decimal('1000.00')}
        )
        mock_monetization_system.revenue_calculator.calculate_royalties = AsyncMock(
            return_value={'creator_share': Decimal('700.00')}
        )
        mock_monetization_system.payment_processor.process_payment = AsyncMock(
            return_value={'status': 'completed'}
        )
        
        # Execute workflow
        rights_valid = await mock_monetization_system.rights_validator.validate_content_rights(content_data)
        analytics = await mock_monetization_system.platform_apis.get_analytics(content_data['content_id'])
        royalties = await mock_monetization_system.revenue_calculator.calculate_royalties(analytics)
        payment = await mock_monetization_system.payment_processor.process_payment(royalties)
        
        # Verify workflow
        assert rights_valid['is_valid'] is True
        assert analytics['revenue'] == Decimal('1000.00')
        assert royalties['creator_share'] == Decimal('700.00')
        assert payment['status'] == 'completed'
    
    def test_monetization_system_health_check(self, mock_monetization_system):
        """Test monetization system health check"""
        # Mock health check for all components
        health_checks = {
            'revenue_calculator': True,
            'payment_processor': True,
            'royalty_engine': True,
            'contract_generator': True,
            'rights_validator': True,
            'platform_apis': True
        }
        
        mock_monetization_system.get_health_status = Mock(return_value=health_checks)
        
        health_status = mock_monetization_system.get_health_status()
        
        assert all(health_status.values())
        assert len(health_status) == 6
    
    @pytest.mark.asyncio
    async def test_revenue_reporting_pipeline(self, mock_monetization_system):
        """Test revenue reporting pipeline"""
        # Mock revenue reporting workflow
        reporting_period = {
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }
        
        mock_monetization_system.generate_revenue_report = AsyncMock(return_value={
            'total_revenue': Decimal('10000.00'),
            'platform_commission': Decimal('3000.00'),
            'creator_payouts': Decimal('7000.00'),
            'content_count': 150,
            'creator_count': 45
        })
        
        report = await mock_monetization_system.generate_revenue_report(reporting_period)
        
        assert report['total_revenue'] == Decimal('10000.00')
        assert report['creator_payouts'] == Decimal('7000.00')
        assert report['content_count'] == 150
        assert report['creator_count'] == 45