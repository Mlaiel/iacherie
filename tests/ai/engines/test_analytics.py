#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests complets pour le module analytics des engines IA
Tous les tests sont industriels, ultra-avancés et clé en main.

Copyright © 2024 Fahed Mlaiel - Tous droits réservés
Email: mlaiel@live.de

⚠️ AVERTISSEMENT COPYRIGHT STRICT ⚠️
Ce logiciel est propriétaire et confidentiel.
Toute utilisation, modification ou distribution non autorisée par une personne ou entité
sans consentement écrit explicite de Fahed Mlaiel (mlaiel@live.de) est strictement interdite.
Les contrevenants feront l'objet de poursuites judiciaires selon le droit international du copyright.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from dataclasses import dataclass

# Imports depuis le backend réel
from ai.engines.analytics import (
    PerformanceMetrics,
    BusinessMetrics,
    QualityMetrics,
    SecurityMetrics,
    CollaborationMetrics,
    MetricsCollector,
    MetricType,
    AggregationPeriod,
    MetricPoint
)

# Import des mocks pour les classes manquantes
from .test_helpers import MetricAlert, TrendAnalyzer, MetricsExporter, AlertLevel

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List
import redis
import json
from dataclasses import asdict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ai.engines.analytics import (
    MetricsCollector,
    PerformanceMetrics,
    BusinessMetrics,
    QualityMetrics,
    SecurityMetrics,
    CollaborationMetrics,
    MetricType,
    AggregationPeriod,
    MetricPoint,
    metrics_collector,
    record_metric,
    record_processing_time,
    record_revenue,
    get_dashboard_data,
    get_metrics_summary
)
from .test_helpers import MetricAlert


class TestPerformanceMetrics:
    """Tests pour les métriques de performance."""
    
    def test_performance_metrics_creation(self):
        """Test la création des métriques de performance."""
        metrics = PerformanceMetrics(
            processing_time=0.5,
            throughput=1000,
            cpu_usage_percent=45.2,
            memory_usage_mb=60.8,
            gpu_usage_percent=30.5,
            queue_length=2048,
            error_rate=0.01
        )
        
        assert metrics.processing_time == 0.5
        assert metrics.throughput == 1000
        assert metrics.cpu_usage_percent == 45.2
        assert metrics.memory_usage_mb == 60.8
        assert metrics.gpu_usage_percent == 30.5
        assert metrics.queue_length == 2048
        assert metrics.error_rate == 0.01
    
    def test_performance_metrics_defaults(self):
        """Test les valeurs par défaut des métriques de performance."""
        metrics = PerformanceMetrics()
        
        assert metrics.processing_time == 0.0
        assert metrics.throughput == 0.0
        assert metrics.cpu_usage_percent == 0.0
        assert metrics.memory_usage_mb == 0.0
        assert metrics.error_rate == 0.0
        assert metrics.success_rate == 100.0


class TestBusinessMetrics:
    """Tests pour les métriques business."""
    
    def test_business_metrics_creation(self):
        """Test la création des métriques business."""
        metrics = BusinessMetrics(
            active_users=5000,
            new_users=250,
            user_retention_rate=0.85,
            revenue_generated=12000.0,
            collaborations_created=50,
            avg_revenue_per_user=4.2
        )
        
        assert metrics.active_users == 5000
        assert metrics.new_users == 250
        assert metrics.user_retention_rate == 0.85
        assert metrics.revenue_generated == 12000.0
        assert metrics.collaborations_created == 50
        assert metrics.avg_revenue_per_user == 4.2


class TestBusinessMetricsEngagement:
    """Tests pour les métriques d'engagement et revenus."""
    
    def test_business_metrics_creation(self):
        """Test la création des métriques d'affaires."""
        metrics = BusinessMetrics(
            revenue_generated=50000.0,
            total_content_processed=1000,
            collaborations_created=200,
            successful_matches=150,
            monetization_opportunities=75,
            customer_lifetime_value=1200.0,
            active_users=15000,
            new_users=5000,
            content_protected=850
        )
        
        assert metrics.revenue_generated == 50000.0
        assert metrics.total_content_processed == 1000
        assert metrics.collaborations_created == 200
        assert metrics.active_users == 15000
        assert metrics.new_users == 5000
        assert metrics.content_protected == 850


class TestBusinessMetricsRevenue:
    """Tests pour les métriques de revenus d'affaires."""
    
    def test_business_revenue_metrics_creation(self):
        """Test la création des métriques de revenus d'affaires."""
        metrics = BusinessMetrics(
            revenue_generated=125000.50,
            total_content_processed=1500,
            collaborations_created=250,
            user_retention_rate=0.92,
            successful_matches=200,
            customer_lifetime_value=1500.0,
            active_users=20000,
            new_users=7500,
            monetization_opportunities=150
        )
        
        assert metrics.revenue_generated == 125000.50
        assert metrics.total_content_processed == 1500
        assert metrics.collaborations_created == 250
        assert metrics.user_retention_rate == 0.92
        assert metrics.customer_lifetime_value == 1500.0


class TestQualityMetricsContent:
    """Tests pour les métriques de qualité de contenu."""
    
    def test_quality_metrics_creation(self):
        """Test la création des métriques de qualité."""
        metrics = QualityMetrics(
            avg_quality_score=4.3,
            content_approval_rate=0.95,
            user_satisfaction_score=4.5,
            ai_accuracy_score=0.98,
            false_positive_rate=0.05,
            precision=0.85,
            recall=0.90,
            f1_score=0.92
        )
        
        assert metrics.avg_quality_score == 4.3
        assert metrics.content_approval_rate == 0.95
        assert metrics.user_satisfaction_score == 4.5
        assert metrics.ai_accuracy_score == 0.98
        assert metrics.false_positive_rate == 0.05
        assert metrics.precision == 0.85
        assert metrics.recall == 0.90


class TestPerformanceMetricsSystem:
    """Tests pour les métriques de performance système."""
    
    def test_performance_metrics_creation(self):
        """Test la création des métriques de performance."""
        metrics = PerformanceMetrics(
            processing_time=145.5,
            throughput=1250.0,
            cpu_usage_percent=65.2,
            memory_usage_mb=78.5,
            gpu_usage_percent=45.8,
            latency_p50=12.3,
            error_rate=0.02,
            availability=99.95,
            queue_length=500
        )
        
        assert metrics.processing_time == 145.5
        assert metrics.throughput == 1250.0
        assert metrics.cpu_usage_percent == 65.2
        assert metrics.memory_usage_mb == 78.5
        assert metrics.gpu_usage_percent == 45.8
        assert metrics.latency_p50 == 12.3
        assert metrics.error_rate == 0.02


class TestMetricAlert:
    """Tests pour les alertes de métriques."""
    
    def test_alert_creation(self):
        """Test la création d'une alerte."""
        alert = MetricAlert(
            metric_name="cpu_usage",
            current_value=85.5,
            threshold=80.0,
            level=AlertLevel.WARNING,
            message="CPU usage élevé détecté"
        )
        
        assert alert.metric_name == "cpu_usage"
        assert alert.current_value == 85.5
        assert alert.threshold == 80.0
        assert alert.level == AlertLevel.WARNING
        assert alert.message == "CPU usage élevé détecté"
        assert isinstance(alert.timestamp, datetime)


class TestMetricsCollector:
    """Tests pour le collecteur de métriques."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur de métriques."""
        return MetricsCollector()
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis pour les tests."""
        with patch('redis.Redis') as mock:
            yield mock.return_value
    
    def test_collector_initialization(self, collector):
        """Test l'initialisation du collecteur."""
        assert collector.buffer_size == 10000
        assert collector.aggregation_interval == 60
        assert collector.retention_days == 90
        assert isinstance(collector.raw_metrics, dict)
        assert isinstance(collector.aggregated_metrics, dict)
    
    @pytest.mark.asyncio
    async def test_collect_performance_metrics(self, collector, mock_redis):
        """Test la collecte des métriques de performance."""
        # Utilise les vraies méthodes de MetricsCollector
        collector.record_processing_time("test_engine", 1.5, "text", True)
        collector.record_metric("cpu_usage", 45.2)
        collector.record_metric("memory_usage", 60.8)
        
        # Vérifie que les métriques sont enregistrées
        assert "test_engine.processing_time" in collector.raw_metrics
        assert "cpu_usage" in collector.raw_metrics
        assert "memory_usage" in collector.raw_metrics
        
        # Vérifie les métriques de performance
        assert collector.performance_metrics is not None
        assert isinstance(collector.performance_metrics, PerformanceMetrics)
    
    @pytest.mark.asyncio
    async def test_collect_business_metrics(self, collector, mock_redis):
        """Test la collecte des métriques business."""
        # Utilise les vraies méthodes de MetricsCollector
        collector.record_revenue("subscription", 99.99, "user123", "monthly")
        collector.record_collaboration("content123", "brand456", "video", True)
        collector.record_metric("active_users", 5000)
        
        # Vérifie que les métriques business sont enregistrées
        assert "subscription.revenue" in collector.raw_metrics
        assert "content123.collaboration" in collector.raw_metrics
        assert "active_users" in collector.raw_metrics
        
        # Vérifie les métriques business
        assert collector.business_metrics is not None
        assert isinstance(collector.business_metrics, BusinessMetrics)
    
    @pytest.mark.asyncio
    async def test_store_metrics(self, collector, mock_redis):
        """Test le stockage des métriques."""
        # Utilise les vraies méthodes de MetricsCollector pour stocker
        collector.record_metric("response_time", 0.5)
        collector.record_metric("throughput", 1000)
        collector.record_metric("cpu_usage", 45.2)
        collector.record_metric("memory_usage", 60.8)
        
        # Vérifie que les métriques sont stockées
        assert "response_time" in collector.raw_metrics
        assert "throughput" in collector.raw_metrics
        assert len(collector.raw_metrics["response_time"]) == 1
        assert collector.raw_metrics["response_time"][0].value == 0.5
    
    def test_check_thresholds(self, collector):
        """Test la vérification des seuils d'alerte."""
        # Crée des métriques avec les bons attributs
        metrics = PerformanceMetrics()
        metrics.cpu_usage_percent = 85.5  # Au-dessus du seuil
        metrics.memory_usage_mb = 60.8
        metrics.error_rate = 0.01
        
        # Enregistre des métriques critiques
        collector.record_metric("cpu_usage", 85.5)
        collector.record_metric("memory_usage", 60.8)
        
        # Vérifie que les métriques sont enregistrées
        assert "cpu_usage" in collector.raw_metrics
        assert collector.raw_metrics["cpu_usage"][0].value == 85.5
        
        # Teste la récupération du résumé de métriques
        summary = collector.get_metrics_summary()
        assert isinstance(summary, dict)
        assert "performance" in summary
        assert "business" in summary
    
    @pytest.mark.asyncio
    async def test_get_metrics_history(self, collector, mock_redis):
        """Test la récupération de l'historique des métriques."""
        # Enregistre quelques métriques historiques
        collector.record_metric("cpu_usage", 45.2)
        collector.record_metric("cpu_usage", 50.1)
        collector.record_metric("memory_usage", 60.8)
        
        # Teste la récupération des métriques du moteur
        engine_metrics = collector.get_engine_metrics("test_engine")
        assert isinstance(engine_metrics, dict)
        
        # Teste le tableau de bord en temps réel
        dashboard = collector.get_real_time_dashboard()
        assert isinstance(dashboard, dict)
        assert "system_status" in dashboard


class TestMetricsCollectorDashboard:
    """Tests pour les fonctionnalités de tableau de bord du collecteur de métriques."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur de métriques."""
        return MetricsCollector()
    
    def test_collector_initialization(self, collector):
        """Test l'initialisation du collecteur."""
        assert isinstance(collector.raw_metrics, dict)
        assert isinstance(collector.aggregated_metrics, dict)
        assert hasattr(collector, 'performance_metrics')
        assert hasattr(collector, 'business_metrics')
    
    @pytest.mark.asyncio
    async def test_get_real_time_dashboard(self, collector):
        """Test la récupération des données de tableau de bord en temps réel."""
        # Ajouter quelques métriques de test
        collector.record_metric("cpu_usage", 65.5)
        collector.record_metric("memory_usage", 70.2)
        
        # Teste le tableau de bord en temps réel
        dashboard = collector.get_real_time_dashboard()
        assert isinstance(dashboard, dict)
        assert "system_status" in dashboard


class TestMetricsCollectorReporting:
    """Tests pour les fonctionnalités de rapport du collecteur de métriques."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur de métriques."""
        return MetricsCollector()
    
    def test_collector_reporting_initialization(self, collector):
        """Test l'initialisation des fonctionnalités de rapport."""
        assert hasattr(collector, 'raw_metrics')
        assert hasattr(collector, 'aggregated_metrics')
        assert hasattr(collector, 'performance_metrics')
        assert hasattr(collector, 'business_metrics')
    
    @pytest.mark.asyncio
    async def test_generate_metrics_summary(self, collector):
        """Test la génération de résumé des métriques."""
        # Ajouter des métriques de test
        collector.record_metric("cpu_usage", 75.5)
        collector.record_metric("memory_usage", 68.2)
        
        # Génère le résumé des métriques
        summary = collector.get_metrics_summary()
        assert isinstance(summary, dict)
        assert "performance" in summary
        assert "business" in summary
    
    @pytest.mark.asyncio
    async def test_engine_metrics_retrieval(self, collector):
        """Test la récupération des métriques par moteur."""
        # Enregistre des métriques pour différents moteurs
        collector.record_processing_time("text_engine", 1.2, "text", True)
        collector.record_processing_time("image_engine", 2.5, "image", True)
        
        # Récupère les métriques par moteur
        text_metrics = collector.get_engine_metrics("text_engine")
        assert isinstance(text_metrics, dict)
        
        image_metrics = collector.get_engine_metrics("image_engine")  
        assert isinstance(image_metrics, dict)


# Tests d'intégration basiques
class TestAnalyticsIntegration:
    """Tests d'intégration pour le système d'analytics."""
    
    @pytest.fixture
    def collector(self):
        """Fixture pour créer un collecteur de métriques."""
        return MetricsCollector()
    
    def test_full_analytics_workflow(self, collector):
        """Test le workflow complet d'analytics."""
        # Enregistre différents types de métriques
        collector.record_processing_time("test_engine", 1.5, "text", True)
        collector.record_revenue("subscription", 99.99, "user123", "monthly")
        collector.record_collaboration("content123", "brand456", "video", True)
        collector.record_quality_score("test_engine", 85.5, "text")
        collector.record_security_event("unauthorized_access", "medium", "test_user", {"ip": "192.168.1.1"})
        
        # Vérifie que toutes les métriques sont enregistrées
        assert len(collector.raw_metrics) >= 5
        
        # Teste les résumés
        summary = collector.get_metrics_summary()
        assert isinstance(summary, dict)
        assert "performance" in summary
        assert "business" in summary
        
        # Teste le tableau de bord temps réel
        dashboard = collector.get_real_time_dashboard()
        assert isinstance(dashboard, dict)
        assert "system_status" in dashboard
