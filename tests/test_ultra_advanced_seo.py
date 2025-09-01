"""🧪 Tests Ultra-Avancés pour SEO API Integrations
=================================================
Tests complets pour les intégrations API SEO
Author: Fahed Mlaiel (mlaiel@live.de)
Type: ULTRA_ADVANCED_SEO_TESTS
=================================================
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List

# Import des modules à tester
from business.influencer_ai.seo_api_integrations import (
    SEOAPIManager, APIProvider, APIConfig, KeywordMetrics,
    CompetitorData, TrendingKeyword, GoogleKeywordPlannerConnector,
    SEMrushConnector, AhrefsConnector, GoogleTrendsConnector,
    create_api_config, create_seo_api_manager
)

from business.influencer_ai.seo_marketing import (
    SEOMarketingManager, SEOMarketingConfig, SEOPlatform, Keyword
)

from business.influencer_ai.seo_config import (
    UltraAdvancedSEOConfig, load_seo_config, validate_api_config
)

class TestUltraAdvancedSEOAPIs:
    """
Tests pour les APIs SEO ultra-avancées"""
    
    @pytest.fixture
    def api_config(self):
        """
Configuration de test pour les APIs"""
        return APIConfig(
            provider=APIProvider.GOOGLE_KEYWORD_PLANNER,
            api_key="test_key",
            api_secret="test_secret",
            base_url="https://test.api.com",
            rate_limit_per_hour=100,
            timeout_seconds=10,
            enabled=True
        )
    
    @pytest.fixture
    def mock_api_keys(self):
        """Clés API de test"""
        return {
            'google_ads_api_key': 'test_google_key',
            'google_ads_developer_token': 'test_developer_token',
            'semrush_api_key': 'test_semrush_key',
            'ahrefs_api_key': 'test_ahrefs_key'
        }
    
    def test_api_config_creation(self):
        """
Test de création de configuration API"""
        config = create_api_config(
            APIProvider.GOOGLE_KEYWORD_PLANNER,
            api_key="test_key",
            api_secret="test_secret"
        )
        
        assert config.provider == APIProvider.GOOGLE_KEYWORD_PLANNER
        assert config.api_key == "test_key"
        assert config.api_secret == "test_secret"
        assert config.enabled == True
        assert config.base_url == "https://googleads.googleapis.com/v14"
    
    def test_seo_api_manager_creation(self, mock_api_keys):
        """Test de création du gestionnaire d'APIs"""
        manager = create_seo_api_manager(mock_api_keys)
        
        assert isinstance(manager, SEOAPIManager)
        assert len(manager.api_configs) >= 3  # Au moins Google, SEMrush, Ahrefs
    
    @pytest.mark.asyncio
    async def test_google_keyword_planner_connector(self, api_config):
        """
Test du connecteur Google Keyword Planner"""
        connector = GoogleKeywordPlannerConnector(api_config)
        
        # Mock de la session HTTP
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'results': [
                    {
                        'text': 'test keyword',
                        'keywordIdeaMetrics': {
                            'avgMonthlySearches': 1000,
                            'competition': 'MEDIUM',
                            'lowTopOfPageBidMicros': 1000000,
                            'highTopOfPageBidMicros': 5000000
                        }
                    }
                ]
            })
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            # Test d'initialisation
            success = await connector.initialize()
            assert success == True
            
            # Test de recherche de mots-clés
            keywords = await connector.research_keywords(['test'], 'en')
            assert len(keywords) > 0
            assert keywords[0].keyword == 'test keyword'
            assert keywords[0].search_volume == 1000
            
            await connector.close()
    
    @pytest.mark.asyncio
    async def test_semrush_connector(self, api_config):
        """
Test du connecteur SEMrush"""
        api_config.provider = APIProvider.SEMRUSH
        api_config.base_url = "https://api.semrush.com"
        connector = SEMrushConnector(api_config)
        
        # Mock de la réponse SEMrush (format CSV)
        mock_response_text = "Keyword;Volume;Difficulty;CPC;Competition\ntest keyword;1500;45;2.5;0.7"
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_response_text)
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Test d'initialisation
            success = await connector.initialize()
            assert success == True
            
            # Test de récupération de données
            keywords = await connector.get_keyword_data(['test'])
            assert len(keywords) > 0
            assert keywords[0].keyword == 'test keyword'
            assert keywords[0].search_volume == 1500
            
            await connector.close()
    
    @pytest.mark.asyncio
    async def test_ahrefs_connector(self, api_config):
        """Test du connecteur Ahrefs"""
        api_config.provider = APIProvider.AHREFS
        api_config.base_url = "https://apiv2.ahrefs.com"
        connector = AhrefsConnector(api_config)
        
        # Mock de la réponse Ahrefs
        mock_domain_data = {
            'domain_rating': 75,
            'organic_traffic': 50000,
            'backlinks': 10000
        }
        
        mock_keywords_data = {
            'keywords': [
                {
                    'keyword': 'competitor keyword',
                    'volume': 2000,
                    'difficulty': 60
                }
            ]
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(side_effect=[mock_domain_data, mock_keywords_data])
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Test d'initialisation
            success = await connector.initialize()
            assert success == True
            
            # Test d'analyse concurrentielle
            competitors = await connector.analyze_competitors(['example.com'])
            assert len(competitors) > 0
            assert competitors[0].domain == 'example.com'
            assert competitors[0].domain_rating == 75
            
            await connector.close()
    
    @pytest.mark.asyncio
    async def test_google_trends_connector(self, api_config):
        """Test du connecteur Google Trends"""
        api_config.provider = APIProvider.GOOGLE_TRENDS
        api_config.base_url = "https://trends.google.com/trends"
        connector = GoogleTrendsConnector(api_config)
        
        # Mock de la réponse Google Trends
        mock_trends_data = {
            'default': {
                'trendingSearchesDays': [
                    {
                        'trendingSearches': [
                            {
                                'title': {'query': 'trending topic'},
                                'formattedTraffic': '100K+',
                                'relatedQueries': [
                                    {'query': 'related query 1'},
                                    {'query': 'related query 2'}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=f")]}}'{json.dumps(mock_trends_data)}")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            # Test d'initialisation
            success = await connector.initialize()
            assert success == True
            
            # Test de récupération des tendances
            trending = await connector.get_trending_keywords()
            assert len(trending) > 0
            assert trending[0].keyword == 'trending topic'
            
            await connector.close()


class TestSEOMarketingManagerAdvanced:
    """Tests pour le gestionnaire SEO Marketing avancé"""
    
    @pytest.fixture
    def seo_config(self):
        """
Configuration SEO de test"""
        return SEOMarketingConfig(
            enabled=True,
            use_real_apis=True,
            api_keys={
                'google_ads_api_key': 'test_google_key',
                'semrush_api_key': 'test_semrush_key',
                'ahrefs_api_key': 'test_ahrefs_key'
            }
        )
    
    @pytest.mark.asyncio
    async def test_seo_manager_initialization(self, seo_config):
        """
Test d'initialisation du gestionnaire SEO"""
        manager = SEOMarketingManager(seo_config)
        
        # Mock des APIs
        with patch('business.influencer_ai.seo_marketing.create_seo_api_manager') as mock_create:
            mock_api_manager = Mock()
            mock_api_manager.initialize_all = AsyncMock(return_value={
                APIProvider.GOOGLE_KEYWORD_PLANNER: True,
                APIProvider.SEMRUSH: True,
                APIProvider.AHREFS: True
            })
            mock_create.return_value = mock_api_manager
            
            success = await manager.initialize()
            assert success == True
            assert manager.real_apis_available == True
    
    @pytest.mark.asyncio
    async def test_ultra_advanced_keyword_research(self, seo_config):
        """
Test de recherche de mots-clés ultra-avancée"""
        manager = SEOMarketingManager(seo_config)
        
        # Mock des connecteurs API
        mock_google_connector = Mock()
        mock_google_connector.research_keywords = AsyncMock(return_value=[
            KeywordMetrics(
                keyword='advanced keyword',
                search_volume=5000,
                competition=0.6,
                cpc_low=1.5,
                cpc_high=4.0,
                difficulty=65
            )
        ])
        
        mock_semrush_connector = Mock()
        mock_semrush_connector.get_keyword_data = AsyncMock(return_value=[
            KeywordMetrics(
                keyword='semrush keyword',
                search_volume=3000,
                competition=0.4,
                difficulty=50
            )
        ])
        
        mock_api_manager = Mock()
        mock_api_manager.get_connector.side_effect = lambda provider: {
            APIProvider.GOOGLE_KEYWORD_PLANNER: mock_google_connector,
            APIProvider.SEMRUSH: mock_semrush_connector
        }.get(provider)
        
        manager.api_manager = mock_api_manager
        manager.real_apis_available = True
        
        # Test de recherche
        keywords = await manager.research_keywords(
            ['test keyword'],
            [SEOPlatform.GOOGLE, SEOPlatform.YOUTUBE],
            'en'
        )
        
        assert len(keywords) > 0
        # Vérifier que les mots-clés de différentes sources sont inclus
        keyword_sources = [kw.term for kw in keywords]
        assert any('advanced keyword' in term for term in keyword_sources)
    
    @pytest.mark.asyncio
    async def test_real_time_trend_monitoring(self, seo_config):
        """
Test de surveillance des tendances en temps réel"""
        manager = SEOMarketingManager(seo_config)
        
        # Mock du connecteur Google Trends
        mock_trends_connector = Mock()
        mock_trends_connector.get_trending_keywords = AsyncMock(return_value=[
            TrendingKeyword(
                keyword='viral trend',
                trend_score=95000,
                volume_change=150,
                related_queries=['viral content', 'trending now']
            )
        ])
        
        mock_api_manager = Mock()
        mock_api_manager.get_connector.return_value = mock_trends_connector
        
        manager.api_manager = mock_api_manager
        manager.real_apis_available = True
        
        # Test de mise à jour des tendances
        await manager._update_real_time_trending_keywords()
        
        # Vérifier que les tendances sont stockées en cache
        assert len(manager.trend_cache) > 0
        trend_keys = list(manager.trend_cache.keys())
        assert any('realtime_trends' in key for key in trend_keys)
    
    @pytest.mark.asyncio
    async def test_advanced_competitor_analysis(self, seo_config):
        """
Test d'analyse concurrentielle avancée"""
        manager = SEOMarketingManager(seo_config)
        
        # Mock du connecteur Ahrefs
        mock_ahrefs_connector = Mock()
        mock_ahrefs_connector.analyze_competitors = AsyncMock(return_value=[
            CompetitorData(
                domain='competitor.com',
                domain_rating=80,
                organic_keywords=25000,
                organic_traffic=500000,
                backlinks=50000,
                top_keywords=[
                    KeywordMetrics(
                        keyword='competitor keyword',
                        search_volume=10000,
                        difficulty=70
                    )
                ]
            )
        ])
        
        mock_api_manager = Mock()
        mock_api_manager.get_connector.return_value = mock_ahrefs_connector
        
        manager.api_manager = mock_api_manager
        manager.real_apis_available = True
        
        # Test de mise à jour de l'analyse concurrentielle
        await manager._update_advanced_competitor_analysis()
        
        # Vérifier que l'analyse est stockée en cache
        assert len(manager.competitor_cache) > 0
        competitor_keys = list(manager.competitor_cache.keys())
        assert any('ahrefs_analysis' in key for key in competitor_keys)
    
    @pytest.mark.asyncio
    async def test_api_health_monitoring(self, seo_config):
        """
Test de surveillance de l'état de santé des APIs"""
        manager = SEOMarketingManager(seo_config)
        
        # Mock du gestionnaire d'APIs
        mock_api_manager = Mock()
        mock_api_manager.health_check = AsyncMock(return_value={
            APIProvider.GOOGLE_KEYWORD_PLANNER: 'active',
            APIProvider.SEMRUSH: 'active',
            APIProvider.AHREFS: 'rate_limited'
        })
        
        manager.api_manager = mock_api_manager
        
        # Test de vérification de santé
        health_status = await manager.get_api_health_status()
        
        assert 'google_keyword_planner' in health_status
        assert 'semrush' in health_status
        assert 'ahrefs' in health_status


class TestSEOConfiguration:
    """
Tests pour la configuration SEO ultra-avancée"""
    
    def test_seo_config_loading(self):
        """
Test de chargement de la configuration"""
        config = load_seo_config()
        assert isinstance(config, UltraAdvancedSEOConfig)
    
    def test_api_validation(self):
        """
Test de validation des APIs"""
        config = UltraAdvancedSEOConfig(
            google_ads_api_key='test_key',
            google_ads_developer_token='test_token',
            semrush_api_key='test_semrush'
        )
        
        validation = validate_api_config(config)
        assert validation['google_ads'] == True
        assert validation['semrush'] == True
        assert validation['ahrefs'] == False
        assert validation['any_configured'] == True
    
    def test_configured_apis_detection(self):
        """
Test de détection des APIs configurées"""
        config = UltraAdvancedSEOConfig(
            google_ads_api_key='test_key',
            semrush_api_key='test_semrush'
        )
        
        configured = config.get_configured_apis()
        assert 'google_ads' in configured
        assert 'semrush' in configured
        assert 'ahrefs' not in configured


class TestIntegrationComplete:
    """
Tests d'intégration complets"""
    
    @pytest.mark.asyncio
    async def test_complete_seo_workflow(self):
        """
Test du workflow SEO complet avec APIs"""
        
        # Configuration avec APIs simulées
        config = SEOMarketingConfig(
            enabled=True,
            use_real_apis=False,  # Mode simulation pour les tests
            fallback_to_simulation=True
        )
        
        manager = SEOMarketingManager(config)
        
        # Initialisation
        success = await manager.initialize()
        assert success == True
        
        # Recherche de mots-clés
        keywords = await manager.research_keywords(
            ['content creation', 'SEO optimization'],
            [SEOPlatform.GOOGLE, SEOPlatform.YOUTUBE],
            'en'
        )
        
        assert len(keywords) > 0
        assert all(isinstance(kw, Keyword) for kw in keywords)
        
        # Analyse SEO de contenu
        seo_analysis = await manager.analyze_content_seo(
            title="Ultimate Guide to Content Creation",
            description="Learn how to create engaging content with our comprehensive guide covering SEO optimization, keyword research, and content strategy.",
            content_body="Content creation is essential for digital marketing success. This guide covers advanced SEO techniques, keyword optimization strategies, and content planning methods.",
            target_keywords=['content creation', 'SEO optimization'],
            platform=SEOPlatform.GOOGLE
        )
        
        assert seo_analysis.seo_score > 0
        assert len(seo_analysis.recommendations) > 0
        assert seo_analysis.optimized_title != ""
        
        # Nettoyage
        await manager.close()
    
    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test du comportement de fallback en cas d'échec API"""
        
        config = SEOMarketingConfig(
            enabled=True,
            use_real_apis=True,
            fallback_to_simulation=True,
            api_keys={'invalid_key': 'invalid_value'}
        )
        
        manager = SEOMarketingManager(config)
        
        # L'initialisation devrait réussir même avec des clés invalides
        success = await manager.initialize()
        assert success == True
        
        # La recherche de mots-clés devrait fonctionner en mode fallback
        keywords = await manager.research_keywords(
            ['test'],
            [SEOPlatform.GOOGLE],
            'en'
        )
        
        assert len(keywords) > 0  # Devrait utiliser la simulation
        
        await manager.close()


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v", "--tb=short"])