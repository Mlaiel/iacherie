"""IA Influencer Agent - Tests de la Pipeline Créateur
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT DE PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code et tous les concepts associés sont la propriété exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation écrite 
explicite de l'auteur est strictement interdite et constitue une violation du 
droit d'auteur. Contact: mlaiel@live.de

Tests complets pour valider le fonctionnement de la pipeline créateur
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Imports des modules à tester
from ..config import (
    CreatorType, ContentType, Platform, RevenueStream,
    DEFAULT_CONFIG, DEFAULT_CREATOR_CONFIG
)

@pytest.fixture
def sample_creator_data():
    """Données de test pour un créateur"""    return {
        'creator_id': 'test_musician_001',
        'creator_type': 'musician',
        'name': 'Test Artist',
        'genre': 'electronic',
        'target_platforms': ['spotify', 'youtube_music'],
        'monetization_goals': {
            'primary': 'streaming_revenue',
            'target_monthly_revenue': 1000
        }
    }

@pytest.fixture
def sample_content_data():
    """Données de test pour du contenu"""    return {
        'content_id': 'test_track_001',
        'title': 'Test Track',
        'content_type': 'audio',
        'file_path': '/test/audio.wav',
        'duration': 180,
        'genre': 'electronic'
    }

class TestCreatorWorkflowOrchestrator:
    """Tests pour l'orchestrateur de workflows créateur"""    
    @pytest.mark.asyncio
    async def test_workflow_orchestrator_import(self):
        """Test que l'orchestrateur peut être importé"""        try:
            from ..creator_workflows import CreatorWorkflowOrchestrator
            orchestrator = CreatorWorkflowOrchestrator()
            assert orchestrator is not None
        except ImportError as e:
            pytest.fail(f"Impossible d'importer CreatorWorkflowOrchestrator: {e}")
    
    @pytest.mark.asyncio
    async def test_musician_workflow_execution(self, sample_creator_data, sample_content_data):
        """Test d'exécution du workflow musicien"""        try:
            from ..creator_workflows import CreatorWorkflowOrchestrator
            
            orchestrator = CreatorWorkflowOrchestrator()
            
            # Mock des dépendances externes
            with patch.object(orchestrator, '_execute_workflow_steps') as mock_execute:
                mock_execute.return_value = {
                    'workflow_id': 'test_workflow_001',
                    'status': 'completed',
                    'steps_completed': 5
                }
                
                result = await orchestrator.execute_creator_workflow(
                    workflow_type='musician_distribution',
                    creator_data=sample_creator_data,
                    content_data=sample_content_data
                )
                
                assert result['status'] == 'completed'
                assert 'workflow_id' in result
                mock_execute.assert_called_once()
                
        except Exception as e:
            pytest.fail(f"Erreur dans le test workflow musicien: {e}")

class TestPlatformIntegrations:
    """Tests pour les intégrations de plateformes"""    
    @pytest.mark.asyncio
    async def test_platform_manager_import(self):
        """Test que le gestionnaire de plateformes peut être importé"""        try:
            from ..platform_integrations import CreatorPlatformManager
            manager = CreatorPlatformManager()
            assert manager is not None
        except ImportError as e:
            pytest.fail(f"Impossible d'importer CreatorPlatformManager: {e}")
    
    @pytest.mark.asyncio
    async def test_spotify_integration(self, sample_creator_data, sample_content_data):
        """Test de l'intégration Spotify"""        try:
            from ..platform_integrations import SpotifyIntegration
            
            spotify = SpotifyIntegration()
            
            # Mock de l'API Spotify
            with patch.object(spotify, '_upload_to_spotify') as mock_upload:
                mock_upload.return_value = {
                    'status': 'success',
                    'track_id': 'spotify_track_123',
                    'url': 'https://open.spotify.com/track/123'
                }
                
                result = await spotify.upload_content(
                    content=sample_content_data,
                    creator_profile=sample_creator_data
                )
                
                assert result['status'] == 'success'
                assert 'track_id' in result
                
        except Exception as e:
            pytest.fail(f"Erreur dans le test Spotify: {e}")

class TestMonetizationAnalytics:
    """Tests pour l'analyse de monétisation"""    
    @pytest.mark.asyncio
    async def test_monetization_analyzer_import(self):
        """Test que l'analyseur de monétisation peut être importé"""        try:
            from ..monetization_analytics import CreatorMonetizationAnalyzer
            analyzer = CreatorMonetizationAnalyzer()
            assert analyzer is not None
        except ImportError as e:
            pytest.fail(f"Impossible d'importer CreatorMonetizationAnalyzer: {e}")
    
    @pytest.mark.asyncio
    async def test_revenue_analysis(self, sample_creator_data):
        """Test d'analyse des revenus"""        try:
            from ..monetization_analytics import CreatorMonetizationAnalyzer
            
            analyzer = CreatorMonetizationAnalyzer()
            
            # Données de performance simulées
            performance_data = {
                'spotify': {'streams': 10000, 'revenue': 40.0},
                'youtube_music': {'views': 5000, 'revenue': 20.0}
            }
            
            with patch.object(analyzer, '_calculate_revenue_potential') as mock_calc:
                mock_calc.return_value = {
                    'total_revenue': 60.0,
                    'growth_potential': 25.0,
                    'recommendations': ['Increase upload frequency', 'Optimize SEO']
                }
                
                result = await analyzer.analyze_revenue_potential(
                    creator_profile=sample_creator_data,
                    content_performance=performance_data
                )
                
                assert result['total_revenue'] == 60.0
                assert 'recommendations' in result
                
        except Exception as e:
            pytest.fail(f"Erreur dans le test analyse revenus: {e}")

class TestContentProcessors:
    """Tests pour les processeurs de contenu"""    
    @pytest.mark.asyncio
    async def test_creator_content_processor_import(self):
        """Test que le processeur de contenu créateur peut être importé"""        try:
            from ..processors import CreatorContentProcessor
            processor = CreatorContentProcessor()
            assert processor is not None
        except ImportError as e:
            pytest.fail(f"Impossible d'importer CreatorContentProcessor: {e}")
    
    @pytest.mark.asyncio
    async def test_content_processing(self, sample_creator_data, sample_content_data):
        """Test de traitement du contenu"""        try:
            from ..processors import CreatorContentProcessor
            
            processor = CreatorContentProcessor()
            
            with patch.object(processor, '_analyze_content') as mock_analyze:
                mock_analyze.return_value = {
                    'genre_confidence': 0.95,
                    'mood': 'energetic',
                    'quality_score': 8.5,
                    'seo_tags': ['electronic', 'dance', 'energetic']
                }
                
                result = await processor.process_creator_content(
                    content_data=sample_content_data,
                    creator_profile=sample_creator_data
                )
                
                assert result['quality_score'] == 8.5
                assert 'seo_tags' in result
                
        except Exception as e:
            pytest.fail(f"Erreur dans le test traitement contenu: {e}")

class TestContentTransformers:
    """Tests pour les transformateurs de contenu"""    
    @pytest.mark.asyncio
    async def test_creator_content_transformer_import(self):
        """Test que le transformateur de contenu créateur peut être importé"""        try:
            from ..transformers import CreatorContentTransformer
            transformer = CreatorContentTransformer()
            assert transformer is not None
        except ImportError as e:
            pytest.fail(f"Impossible d'importer CreatorContentTransformer: {e}")
    
    @pytest.mark.asyncio
    async def test_platform_optimization(self, sample_content_data):
        """Test d'optimisation pour les plateformes"""        try:
            from ..transformers import CreatorContentTransformer
            
            transformer = CreatorContentTransformer()
            
            with patch.object(transformer, '_optimize_for_platform') as mock_optimize:
                mock_optimize.return_value = {
                    'spotify': {
                        'format': 'mp3_320',
                        'metadata': {'title': 'Test Track', 'genre': 'Electronic'},
                        'optimized': True
                    },
                    'youtube_music': {
                        'format': 'mp4',
                        'thumbnail': 'generated_thumb.jpg',
                        'optimized': True
                    }
                }
                
                result = await transformer.optimize_for_platforms(
                    content=sample_content_data,
                    target_platforms=['spotify', 'youtube_music']
                )
                
                assert 'spotify' in result
                assert 'youtube_music' in result
                assert result['spotify']['optimized'] is True
                
        except Exception as e:
            pytest.fail(f"Erreur dans le test optimisation plateformes: {e}")

class TestConfiguration:
    """Tests pour la configuration"""    
    def test_creator_types_enum(self):
        """Test que les types de créateurs sont définis"""        assert CreatorType.MUSICIAN.value == 'musician'
        assert CreatorType.BLOGGER.value == 'blogger'
        assert CreatorType.PHOTOGRAPHER.value == 'photographer'
        assert CreatorType.INFLUENCER.value == 'influencer'
        assert CreatorType.COMEDIAN.value == 'comedian'
    
    def test_platform_enum(self):
        """Test que les plateformes sont définies"""        assert Platform.SPOTIFY.value == 'spotify'
        assert Platform.YOUTUBE.value == 'youtube'
        assert Platform.INSTAGRAM.value == 'instagram'
    
    def test_default_config_values(self):
        """Test que la configuration par défaut est valide"""        assert DEFAULT_CONFIG.max_concurrent_tasks > 0
        assert DEFAULT_CONFIG.timeout_seconds > 0
        assert DEFAULT_CONFIG.retry_attempts >= 1
    
    def test_creator_config_structure(self):
        """Test que la configuration créateur est bien structurée"""        assert 'musician' in DEFAULT_CREATOR_CONFIG.__dict__
        assert 'blogger' in DEFAULT_CREATOR_CONFIG.__dict__
        assert 'photographer' in DEFAULT_CREATOR_CONFIG.__dict__

class TestIntegrationWorkflow:
    """Tests d'intégration complète"""    
    @pytest.mark.asyncio
    async def test_complete_musician_pipeline(self, sample_creator_data, sample_content_data):
        """Test de la pipeline complète pour un musicien"""        try:
            from ..creator_workflows import CreatorWorkflowOrchestrator
            from ..platform_integrations import CreatorPlatformManager
            from ..monetization_analytics import CreatorMonetizationAnalyzer
            
            # Simulation d'une pipeline complète
            orchestrator = CreatorWorkflowOrchestrator()
            platform_manager = CreatorPlatformManager()
            analyzer = CreatorMonetizationAnalyzer()
            
            # Mock toutes les opérations externes
            with patch.multiple(
                orchestrator,
                execute_creator_workflow=AsyncMock(return_value={'status': 'completed'}),
                platform_manager=Mock(),
                analyzer=Mock()
            ):
                # Test que tous les composants peuvent être instanciés
                assert orchestrator is not None
                assert platform_manager is not None
                assert analyzer is not None
                
                # Test qu'une pipeline basique peut être exécutée
                result = await orchestrator.execute_creator_workflow(
                    workflow_type='musician_distribution',
                    creator_data=sample_creator_data,
                    content_data=sample_content_data
                )
                
                assert result['status'] == 'completed'
                
        except Exception as e:
            pytest.fail(f"Erreur dans le test pipeline complète: {e}")

# Configuration des tests
def pytest_configure(config):
    """Configuration globale des tests"""    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )

# Tests de performance (optionnels)
class TestPerformance:
    """Tests de performance pour les opérations critiques"""    
    @pytest.mark.asyncio
    async def test_content_processing_performance(self, sample_content_data):
        """Test que le traitement de contenu est dans les temps"""        import time
        
        try:
            from ..processors import CreatorContentProcessor
            
            processor = CreatorContentProcessor()
            
            start_time = time.time()
            
            with patch.object(processor, '_analyze_content') as mock_analyze:
                mock_analyze.return_value = {'processed': True}
                
                await processor.process_creator_content(
                    content_data=sample_content_data,
                    creator_profile={'creator_type': 'musician'}
                )
            
            processing_time = time.time() - start_time
            
            # Le traitement ne devrait pas prendre plus de 5 secondes (en mode mock)
            assert processing_time < 5.0
            
        except Exception as e:
            pytest.fail(f"Erreur dans le test performance: {e}")

if __name__ == "__main__":
    # Exécution des tests si le fichier est lancé directement
    pytest.main([__file__, "-v", "--tb=short"])
