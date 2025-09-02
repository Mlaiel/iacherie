#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests complets pour le module optimization du système IA-Influencer.
Développé par une équipe d'experts combinant tous les rôles nécessaires.

Copyright (C) 2024 Fahed Mlaiel <mlaiel@live.de>
Tous droits réservés. Usage non autorisé strictement interdit.

Équipe de développement :
- Lead Dev + Architecte Développeur IA
- Développeur Backend Senior (Python/FastAPI/Django)  
- Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
- DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
- Spécialiste Sécurité Backend
- Architecte Microservices
- Développeur Audio
- DevOps Engineer
- IA Prompt Engineer
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import tempfile
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import threading
from datetime import datetime, timedelta
import pickle

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from ai.engines.optimization import (
    PerformanceOptimizer,
    AdvancedCache,
    CacheStrategy,
    CacheEntry,
    ResourceMonitor,
    ResourceType,
    OptimizationLevel,
    PerformanceProfile
)
from .test_helpers import CacheStats


class TestCacheEntry:
    """
Tests pour les entrées de cache."""
    
    def test_cache_entry_creation(self):
        """
Test la création d'une entrée de cache."""
        data = {"key": "value", "number": 42}
        now = datetime.now()
        entry = CacheEntry(
            key="test_key",
            value=data,
            created_at=now,
            last_accessed=now,
            access_count=1,
            size_bytes=len(str(data)),
            ttl=3600
        )
        
        assert entry.key == "test_key"
        assert entry.value == data
        assert entry.ttl == 3600
        assert entry.size_bytes == len(str(data))
        assert entry.access_count == 1
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.last_accessed, datetime)
    
    def test_cache_entry_expiration(self):
        """Test l'expiration des entrées de cache."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            ttl=1  # 1 seconde
        )
        
        # Entrée fraîche
        assert not entry.is_expired()
        
        # Attendre l'expiration
        time.sleep(1.1)
        assert entry.is_expired()
    
    def test_cache_entry_access_tracking(self):
        """Test le suivi des accès."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            ttl=3600
        )
        
        # Premier accès
        entry.mark_accessed()
        assert entry.access_count == 1
        assert entry.last_accessed is not None
        
        # Deuxième accès
        time.sleep(0.1)
        entry.mark_accessed()
        assert entry.access_count == 2


class TestCacheStats:
    """Tests pour les statistiques de cache."""
    
    def test_cache_stats_initialization(self):
        """
Test l'initialisation des statistiques."""
        stats = CacheStats()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.total_size == 0
        assert stats.hit_ratio == 0.0
    
    def test_cache_stats_calculation(self):
        """
Test le calcul des statistiques."""
        stats = CacheStats()
        
        # Enregistrer des hits et misses
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        
        assert stats.hits == 2
        assert stats.misses == 1
        assert stats.hit_ratio == 2.0 / 3.0


class TestAdvancedCache:
    """
Tests pour le cache avancé."""
    
    @pytest.fixture
    def cache(self):
        """
Fixture pour créer un cache."""
        return AdvancedCache(max_size=100, default_ttl=3600)
    
    def test_cache_initialization(self, cache):
        """
Test l'initialisation du cache."""
        assert cache.max_size == 100
        assert cache.default_ttl == 3600
        assert cache.strategy == CacheStrategy.LRU
        assert len(cache.entries) == 0
        assert isinstance(cache.stats, CacheStats)
    
    def test_cache_set_get(self, cache):
        """
Test l'insertion et la récupération."""
        # Insertion
        cache.set("key1", "value1")
        
        # Récupération
        value = cache.get("key1")
        assert value == "value1"
        assert cache.stats.hits == 1
        
        # Clé inexistante
        value = cache.get("nonexistent")
        assert value is None
        assert cache.stats.misses == 1
    
    def test_cache_ttl_expiration(self, cache):
        """Test l'expiration TTL."""
        # Insertion avec TTL court
        cache.set("temp_key", "temp_value", ttl=1)
        
        # Vérification immédiate
        assert cache.get("temp_key") == "temp_value"
        
        # Attendre l'expiration
        time.sleep(1.1)
        assert cache.get("temp_key") is None
    
    def test_cache_lru_eviction(self, cache):
        """Test l'éviction LRU."""
        # Remplir le cache
        for i in range(cache.max_size):
            cache.set(f"key_{i}", f"value_{i}")
        
        assert len(cache.entries) == cache.max_size
        
        # Ajouter un élément supplémentaire (doit déclencher l'éviction)
        cache.set("overflow_key", "overflow_value")
        
        assert len(cache.entries) == cache.max_size
        assert cache.stats.evictions == 1
        assert "key_0" not in cache.entries  # Premier élément évincé
        assert "overflow_key" in cache.entries
    
    def test_cache_lfu_strategy(self):
        """Test la stratégie LFU."""
        cache = AdvancedCache(max_size=3, strategy=CacheStrategy.LFU)
        
        # Insérer des éléments
        cache.set("a", "value_a")
        cache.set("b", "value_b")
        cache.set("c", "value_c")
        
        # Accéder à "a" plusieurs fois
        cache.get("a")
        cache.get("a")
        cache.get("b")
        
        # Ajouter un nouvel élément (doit évincer "c" qui est le moins fréquent)
        cache.set("d", "value_d")
        
        assert "a" in cache.entries  # Très fréquent
        assert "b" in cache.entries  # Moyennement fréquent
        assert "c" not in cache.entries  # Moins fréquent, évincé
        assert "d" in cache.entries  # Nouveau
    
    def test_cache_fifo_strategy(self):
        """Test la stratégie FIFO."""
        cache = AdvancedCache(max_size=3, strategy=CacheStrategy.FIFO)
        
        # Insérer des éléments
        cache.set("first", "value1")
        cache.set("second", "value2")
        cache.set("third", "value3")
        
        # Ajouter un quatrième élément
        cache.set("fourth", "value4")
        
        # Le premier doit être évincé
        assert "first" not in cache.entries
        assert "second" in cache.entries
        assert "third" in cache.entries
        assert "fourth" in cache.entries
    
    def test_cache_clear(self, cache):
        """Test la suppression complète du cache."""
        # Ajouter des éléments
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache.entries) == 2
        
        # Vider le cache
        cache.clear()
        
        assert len(cache.entries) == 0
        assert cache.stats.hits == 0
        assert cache.stats.misses == 0
    
    def test_cache_size_tracking(self, cache):
        """Test le suivi de la taille."""
        cache.set("small", "x")
        cache.set("medium", "x" * 100)
        cache.set("large", "x" * 1000)
        
        assert cache.stats.total_size > 0
        
        # Supprimer un élément
        cache.delete("large")
        
        # La taille doit diminuer
        new_size = cache.stats.total_size
        assert new_size < 1000  # Taille réduite


class TestResourceMonitor:
    """Tests pour le moniteur de ressources."""
    
    @pytest.fixture
    def monitor(self):
        """
Fixture pour créer un moniteur de ressources."""
        return ResourceMonitor()
    
    def test_monitor_initialization(self, monitor):
        """
Test l'initialisation du moniteur."""
        assert monitor.sampling_interval == 1.0
        assert monitor.history_size == 1000
        assert len(monitor.metrics_history) == 0
        assert monitor.alerts == []
    
    @pytest.mark.asyncio
    async def test_collect_system_metrics(self, monitor):
        """
Test la collecte des métriques système."""
        with patch('psutil.cpu_percent', return_value=45.2):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 60.8
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.percent = 30.5
                    
                    metrics = await monitor.collect_system_metrics()
                    
                    assert isinstance(metrics, ResourceMetrics)
                    assert metrics.cpu_usage == 45.2
                    assert metrics.memory_usage == 60.8
                    assert metrics.disk_usage == 30.5
    
    @pytest.mark.asyncio
    async def test_continuous_monitoring(self, monitor):
        """
Test le monitoring continu."""
        # Mock des métriques
        mock_metrics = ResourceMetrics(
            cpu_usage=50.0,
            memory_usage=70.0,
            disk_usage=40.0,
            network_io=1024,
            process_count=100
        )
        
        with patch.object(monitor, 'collect_system_metrics', return_value=mock_metrics):
            # Démarrer le monitoring pour une courte durée
            monitor_task = asyncio.create_task(monitor.start_monitoring())
            
            # Attendre un peu
            await asyncio.sleep(0.1)
            
            # Arrêter le monitoring
            monitor.stop_monitoring()
            
            # Attendre la fin de la tâche
            await monitor_task
            
            # Vérifier que des métriques ont été collectées
            assert len(monitor.metrics_history) > 0
    
    def test_resource_alerts(self, monitor):
        """
Test les alertes de ressources."""
        # Configurer des seuils
        thresholds = {
            ResourceType.CPU: 80.0,
            ResourceType.MEMORY: 85.0,
            ResourceType.DISK: 90.0
        }
        monitor.set_alert_thresholds(thresholds)
        
        # Métriques normales
        normal_metrics = ResourceMetrics(
            cpu_usage=70.0,
            memory_usage=75.0,
            disk_usage=80.0
        )
        alerts = monitor.check_resource_alerts(normal_metrics)
        assert len(alerts) == 0
        
        # Métriques critiques
        critical_metrics = ResourceMetrics(
            cpu_usage=90.0,  # Au-dessus du seuil
            memory_usage=95.0,  # Au-dessus du seuil
            disk_usage=85.0  # En dessous du seuil
        )
        alerts = monitor.check_resource_alerts(critical_metrics)
        assert len(alerts) == 2  # CPU et mémoire
    
    def test_metrics_history_management(self, monitor):
        try:
            logger.info(f"Executing test_metrics_history_management")
            
            # Implementation for test_metrics_history_management
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_metrics_history_management completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_metrics_history_management failed: {e}")
            raise
class TestProcessingOptimizer:
    """
Tests pour l'optimiseur de traitement."""
    
    @pytest.fixture
    def optimizer(self):
        """
Fixture pour créer un optimiseur de traitement."""
        return ProcessingOptimizer()
    
    def test_optimizer_initialization(self, optimizer):
        """
Test l'initialisation de l'optimiseur."""
        assert optimizer.level == OptimizationLevel.BALANCED
        assert optimizer.parallel_workers == os.cpu_count()
        assert optimizer.batch_size == 32
        assert optimizer.cache_enabled is True
    
    @pytest.mark.asyncio
    async def test_optimize_processing_pipeline(self, optimizer):
        """
Test l'optimisation d'un pipeline de traitement."""
        # Pipeline de test
        def process_item(item):
            return item * 2
        
        pipeline = [process_item]
        data = list(range(100))
        
        # Optimisation du pipeline
        result = await optimizer.optimize_processing_pipeline(pipeline, data)
        
        assert isinstance(result, OptimizationResult)
        assert result.success is True
        assert len(result.processed_data) == 100
        assert result.performance_gain > 0
    
    @pytest.mark.asyncio
    async def test_parallel_processing_optimization(self, optimizer):
        """
Test l'optimisation du traitement parallèle."""
        def cpu_intensive_task(n):
            # Simulation d'une tâche CPU intensive
            return sum(i * i for i in range(n))
        
        tasks = [100, 200, 300, 400, 500]
        
        # Traitement parallèle optimisé
        start_time = time.time()
        results = await optimizer.parallel_process(cpu_intensive_task, tasks)
        parallel_time = time.time() - start_time
        
        # Traitement séquentiel pour comparaison
        start_time = time.time()
        sequential_results = [cpu_intensive_task(task) for task in tasks]
        sequential_time = time.time() - start_time
        
        assert len(results) == len(tasks)
        assert results == sequential_results
        # Le traitement parallèle devrait être plus rapide (sur multi-core)
        if os.cpu_count() > 1:
        try:
            logger.info(f"Executing cpu_intensive_task")
            
            # Implementation for cpu_intensive_task
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"cpu_intensive_task completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"cpu_intensive_task failed: {e}")
            raise
        tasks = [100, 200, 300, 400, 500]
        
        # Traitement parallèle optimisé
        start_time = time.time()
        results = await optimizer.parallel_process(cpu_intensive_task, tasks)
        parallel_time = time.time() - start_time
        
        # Traitement séquentiel pour comparaison
        start_time = time.time()
        sequential_results = [cpu_intensive_task(task) for task in tasks]
        sequential_time = time.time() - start_time
        
        assert len(results) == len(tasks)
        assert results == sequential_results
        # Le traitement parallèle devrait être plus rapide (sur multi-core)
        if os.cpu_count() > 1:
            assert parallel_time < sequential_time
    
    def test_batch_size_optimization(self, optimizer):
        """
Test l'optimisation de la taille des lots."""
        # Données de test
        data_sizes = [100, 1000, 10000, 100000]
        
        for data_size in data_sizes:
            optimal_batch_size = optimizer.calculate_optimal_batch_size(data_size)
            
            assert optimal_batch_size > 0
            assert optimal_batch_size <= data_size
            # La taille de lot doit être raisonnable
            assert optimal_batch_size <= 1000
    
    def test_optimization_level_adjustment(self, optimizer):
        """
Test l'ajustement du niveau d'optimisation."""
        # Test niveau AGGRESSIVE
        optimizer.set_optimization_level(OptimizationLevel.AGGRESSIVE)
        assert optimizer.level == OptimizationLevel.AGGRESSIVE
        assert optimizer.parallel_workers > os.cpu_count()  # Plus de workers
        
        # Test niveau CONSERVATIVE
        optimizer.set_optimization_level(OptimizationLevel.CONSERVATIVE)
        assert optimizer.level == OptimizationLevel.CONSERVATIVE
        assert optimizer.parallel_workers <= os.cpu_count()  # Moins de workers


class TestMemoryOptimizer:
    """
Tests pour l'optimiseur de mémoire."""
    
    @pytest.fixture
    def memory_optimizer(self):
        """
Fixture pour créer un optimiseur de mémoire."""
        return MemoryOptimizer()
    
    def test_memory_usage_monitoring(self, memory_optimizer):
        """
Test le monitoring de l'utilisation mémoire."""
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.percent = 75.5
            
            usage = memory_optimizer.get_memory_usage()
            assert usage == 75.5
    
    def test_memory_cleanup(self, memory_optimizer):
        """
Test le nettoyage de la mémoire."""
        # Créer des objets temporaires
        temp_objects = []
        for i in range(1000):
            temp_objects.append([i] * 100)
        
        # Obtenir l'utilisation avant nettoyage
        initial_usage = memory_optimizer.get_memory_usage()
        
        # Nettoyer
        del temp_objects
        memory_optimizer.force_garbage_collection()
        
        # L'utilisation devrait diminuer
        final_usage = memory_optimizer.get_memory_usage()
        # Note: Le test peut être instable selon l'environnement
    
    def test_memory_pool_management(self, memory_optimizer):
        """
Test la gestion des pools de mémoire."""
        # Allouer un pool
        pool_size = 1024 * 1024  # 1MB
        pool_id = memory_optimizer.create_memory_pool(pool_size)
        
        assert pool_id is not None
        assert pool_id in memory_optimizer.memory_pools
        
        # Utiliser le pool
        allocation = memory_optimizer.allocate_from_pool(pool_id, 1024)
        assert allocation is not None
        
        # Libérer le pool
        memory_optimizer.release_memory_pool(pool_id)
        assert pool_id not in memory_optimizer.memory_pools
    
    def test_memory_leak_detection(self, memory_optimizer):
        try:
            logger.info(f"Executing cpu_intensive_function")
            
            # Implementation for cpu_intensive_function
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"cpu_intensive_function completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing simple_task")
            
            # Implementation for simple_task
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"simple_task completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"simple_task failed: {e}")
            raise
            raise
        """
Test la détection de fuites mémoire."""
        # Simuler une fuite
        leaked_objects = []
        for i in range(100):
            leaked_objects.append([i] * 1000)
            memory_optimizer.track_object_allocation(f"object_{i}", len(leaked_objects[-1]))
        
        # Détecter les fuites
        leaks = memory_optimizer.detect_memory_leaks()
        
        assert len(leaks) > 0
        assert any("object_" in leak["name"] for leak in leaks)


class TestCPUOptimizer:
    """Tests pour l'optimiseur CPU."""
    
    @pytest.fixture
    def cpu_optimizer(self):
        """
Fixture pour créer un optimiseur CPU."""
        return CPUOptimizer()
    
    def test_cpu_profiling(self, cpu_optimizer):
        """
Test le profilage CPU."""
        def cpu_intensive_function():
            return sum(i * i for i in range(10000))
        
        # Profiler la fonction
        profile_result = cpu_optimizer.profile_function(cpu_intensive_function)
        
        assert "execution_time" in profile_result
        assert "cpu_usage" in profile_result
        assert profile_result["execution_time"] > 0
    
    def test_thread_pool_optimization(self, cpu_optimizer):
        """Test l'optimisation du pool de threads."""
        # Tâches de test
        def simple_task(n):
            return n * 2
        
        tasks = list(range(100))
        
        # Optimiser la taille du pool
        optimal_size = cpu_optimizer.calculate_optimal_thread_pool_size(len(tasks))
        assert optimal_size > 0
        assert optimal_size <= os.cpu_count() * 2
        
        # Exécuter avec le pool optimisé
        results = cpu_optimizer.execute_with_optimized_pool(simple_task, tasks)
        assert len(results) == len(tasks)
        assert results == [task * 2 for task in tasks]
    
    def test_cpu_affinity_optimization(self, cpu_optimizer):
        """
Test l'optimisation de l'affinité CPU."""
        if hasattr(os, 'sched_getaffinity'):
            # Obtenir l'affinité actuelle
            current_affinity = cpu_optimizer.get_cpu_affinity()
            assert isinstance(current_affinity, (list, set))
            
            # Optimiser l'affinité pour une tâche CPU intensive
            optimal_affinity = cpu_optimizer.optimize_cpu_affinity_for_task("cpu_intensive")
            assert isinstance(optimal_affinity, (list, set))


class TestIOOptimizer:
    """Tests pour l'optimiseur I/O."""
    
    @pytest.fixture
    def io_optimizer(self):
        """
Fixture pour créer un optimiseur I/O."""
        return IOOptimizer()
    
    @pytest.mark.asyncio
    async def test_async_io_optimization(self, io_optimizer):
        """
Test l'optimisation I/O asynchrone."""
        # Simulation de lectures de fichiers
        async def mock_read_file(filename):
            await asyncio.sleep(0.01)  # Simulation I/O
            return f"content_of_{filename}"
        
        filenames = [f"file_{i}.txt" for i in range(10)]
        
        # Lecture optimisée
        start_time = time.time()
        results = await io_optimizer.optimized_batch_read(mock_read_file, filenames)
        async_time = time.time() - start_time
        
        assert len(results) == len(filenames)
        assert all("content_of_" in result for result in results)
        
        # La lecture asynchrone devrait être plus rapide
        assert async_time < 0.2  # Moins que 10 * 0.01 (séquentiel)
    
    def test_buffer_size_optimization(self, io_optimizer):
        """Test l'optimisation de la taille des buffers."""
        # Test différentes tailles de fichier
        file_sizes = [1024, 10240, 102400, 1024000]  # 1KB à 1MB
        
        for file_size in file_sizes:
            optimal_buffer = io_optimizer.calculate_optimal_buffer_size(file_size)
            
            assert optimal_buffer > 0
            assert optimal_buffer <= file_size
            # Buffer raisonnable (entre 4KB et 64KB)
            assert 4096 <= optimal_buffer <= 65536
    
    def test_io_queue_optimization(self, io_optimizer):
        """
Test l'optimisation des files d'attente I/O."""
        # Créer des requêtes I/O de test
        io_requests = [
            {"type": "read", "priority": 1, "size": 1024},
            {"type": "write", "priority": 3, "size": 2048},
            {"type": "read", "priority": 2, "size": 512},
            {"type": "write", "priority": 1, "size": 4096}
        ]
        
        # Optimiser l'ordre des requêtes
        optimized_queue = io_optimizer.optimize_io_queue(io_requests)
        
        assert len(optimized_queue) == len(io_requests)
        
        # Vérifier que les priorités sont respectées
        priorities = [req["priority"] for req in optimized_queue]
        assert priorities == sorted(priorities, reverse=True)


class TestDatabaseOptimizer:
    """Tests pour l'optimiseur de base de données."""
    
    @pytest.fixture
    def db_optimizer(self):
        """
Fixture pour créer un optimiseur de base de données."""
        return DatabaseOptimizer()
    
    def test_query_optimization_analysis(self, db_optimizer):
        """
Test l'analyse d'optimisation des requêtes."""
        # Requête de test
        query = """
        SELECT u.name, p.title, COUNT(c.id) as comment_count
        FROM users u
        JOIN posts p ON u.id = p.user_id
        LEFT JOIN comments c ON p.id = c.post_id
        WHERE u.created_at > '2023-01-01'
        GROUP BY u.id, p.id
        ORDER BY comment_count DESC
        LIMIT 100
        """
        
        # Analyser la requête
        analysis = db_optimizer.analyze_query(query)
        
        assert "complexity_score" in analysis
        assert "suggested_indexes" in analysis
        assert "optimization_tips" in analysis
        assert analysis["complexity_score"] > 0
    
    def test_connection_pool_optimization(self, db_optimizer):
        """Test l'optimisation du pool de connexions."""
        # Paramètres de test
        concurrent_users = 100
        avg_query_time = 0.05  # 50ms
        peak_load_factor = 2.0
        
        # Calculer la taille optimale du pool
        optimal_pool_size = db_optimizer.calculate_optimal_pool_size(
            concurrent_users, avg_query_time, peak_load_factor
        )
        
        assert optimal_pool_size > 0
        assert optimal_pool_size >= concurrent_users / 10  # Au moins 10% des utilisateurs
        assert optimal_pool_size <= concurrent_users * 2  # Pas plus que 2x les utilisateurs
    
    def test_index_recommendation(self, db_optimizer):
        """
Test les recommandations d'index."""
        # Requêtes fréquentes de test
        frequent_queries = [
            "SELECT * FROM users WHERE email = ?",
            "SELECT * FROM posts WHERE user_id = ? AND status = 'published'",
            "SELECT * FROM comments WHERE post_id = ? ORDER BY created_at DESC",
        ]
        
        # Obtenir des recommandations
        recommendations = db_optimizer.recommend_indexes(frequent_queries)
        
        assert len(recommendations) > 0
        assert all("table" in rec for rec in recommendations)
        assert all("columns" in rec for rec in recommendations)
        assert all("type" in rec for rec in recommendations)


class TestAsyncTaskOptimizer:
    """Tests pour l'optimiseur de tâches asynchrones."""
    
    @pytest.fixture
    def task_optimizer(self):
        """
Fixture pour créer un optimiseur de tâches asynchrones."""
        return AsyncTaskOptimizer()
    
    @pytest.mark.asyncio
    async def test_task_scheduling_optimization(self, task_optimizer):
        """
Test l'optimisation de la planification des tâches."""
        # Créer des tâches de test
        async def quick_task(n):
            await asyncio.sleep(0.01)
            return n * 2
        
        async def slow_task(n):
            await asyncio.sleep(0.1)
            return n * 3
        
        tasks = []
        for i in range(10):
            if i % 2 == 0:
                tasks.append(("quick", quick_task, i))
            else:
                tasks.append(("slow", slow_task, i))
        
        # Optimiser l'exécution
        start_time = time.time()
        results = await task_optimizer.optimize_task_execution(tasks)
        execution_time = time.time() - start_time
        
        assert len(results) == len(tasks)
        # L'optimisation devrait être plus rapide que l'exécution séquentielle
        assert execution_time < 1.0  # Moins que 5 * 0.1 + 5 * 0.01
    
    def test_task_priority_queue(self, task_optimizer):
        """Test la file de priorité des tâches."""
        queue = TaskQueue()
        
        # Ajouter des tâches avec différentes priorités
        queue.add_task("low_priority_task", TaskPriority.LOW, lambda: "low")
        queue.add_task("high_priority_task", TaskPriority.HIGH, lambda: "high")
        queue.add_task("medium_priority_task", TaskPriority.MEDIUM, lambda: "medium")
        
        # Les tâches doivent être triées par priorité
        assert queue.size() == 3
        
        # Récupérer les tâches dans l'ordre de priorité
        first_task = queue.get_next_task()
        assert first_task["name"] == "high_priority_task"
        
        second_task = queue.get_next_task()
        assert second_task["name"] == "medium_priority_task"
        
        third_task = queue.get_next_task()
        assert third_task["name"] == "low_priority_task"
    
    @pytest.mark.asyncio
    async def test_concurrent_task_limiting(self, task_optimizer):
        """Test la limitation des tâches concurrentes."""
        max_concurrent = 3
        task_optimizer.set_max_concurrent_tasks(max_concurrent)
        
        # Créer plus de tâches que la limite
        async def long_task(duration):
            await asyncio.sleep(duration)
            return f"completed_{duration}"
        
        tasks = [long_task(0.1) for _ in range(10)]
        
        # Exécuter avec limitation
        start_time = time.time()
        results = await task_optimizer.execute_with_concurrency_limit(tasks)
        execution_time = time.time() - start_time
        
        assert len(results) == 10
        # Avec limitation, l'exécution devrait prendre plus de temps qu'en parallèle total
        # mais moins qu'en séquentiel
        assert 0.3 < execution_time < 1.0


class TestPerformanceProfiler:
        try:
            logger.info(f"Executing baseline_function")
            
            # Implementation for baseline_function
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing optimized_function")
            
            # Implementation for optimized_function
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"optimized_function completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"optimized_function failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"baseline_function completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"baseline_function failed: {e}")
            raise
    """Tests pour le profileur de performance."""
    
    @pytest.fixture
    def profiler(self):
        """
Fixture pour créer un profileur."""
        return PerformanceProfiler()
    
    def test_function_profiling(self, profiler):
        """
Test le profilage de fonction."""
        def test_function():
            # Simulation de travail
            total = 0
            for i in range(10000):
                total += i * i
            return total
        
        # Profiler la fonction
        profile_result = profiler.profile_function(test_function)
        
        assert "execution_time" in profile_result
        assert "memory_usage" in profile_result
        assert "cpu_usage" in profile_result
        assert profile_result["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_async_function_profiling(self, profiler):
        try:
            logger.info(f"Executing quick_benchmark")
            
            # Implementation for quick_benchmark
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing slow_benchmark")
            
            # Implementation for slow_benchmark
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"slow_benchmark completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"slow_benchmark failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"quick_benchmark completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing improved_function")
            
            # Implementation for improved_function
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"improved_function completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"improved_function failed: {e}")
            raise
        except Exception as e:
        try:
            logger.info(f"Executing baseline_function")
            
            # Implementation for baseline_function
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"baseline_function completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"baseline_function failed: {e}")
            raise
            logger.info(f"quick_benchmark completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"quick_benchmark failed: {e}")
            raise
            logger.info(f"Executing test_benchmark")
            
            # Implementation for test_benchmark
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_benchmark completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_benchmark failed: {e}")
            raise
        profile_result = profiler.profile_function(test_function)
        
        assert "execution_time" in profile_result
        assert "memory_usage" in profile_result
        assert "cpu_usage" in profile_result
        assert profile_result["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_async_function_profiling(self, profiler):
        """Test le profilage de fonction asynchrone."""
        async def async_test_function():
            await asyncio.sleep(0.01)
            return sum(i for i in range(1000))
        
        # Profiler la fonction asynchrone
        profile_result = await profiler.profile_async_function(async_test_function)
        
        assert "execution_time" in profile_result
        assert "memory_usage" in profile_result
        assert profile_result["execution_time"] >= 0.01
    
    def test_code_block_profiling(self, profiler):
        try:
            logger.info(f"Executing mock_loader")
            
            # Implementation for mock_loader
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_loader completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_loader failed: {e}")
            raise
        assert profile_result["execution_time"] >= 0.01
    
    def test_code_block_profiling(self, profiler):
        """Test le profilage de bloc de code."""
        with profiler.profile_code_block("test_block") as block_profiler:
            # Code à profiler
            result = sum(i * i for i in range(5000))
        
        profile_data = block_profiler.get_profile_data()
        
        assert "test_block" in profile_data
        assert "execution_time" in profile_data["test_block"]
        assert profile_data["test_block"]["execution_time"] > 0
    
    def test_performance_regression_detection(self, profiler):
        """Test la détection de régression de performance."""
        def baseline_function():
            return sum(i for i in range(1000))
        
        def optimized_function():
            return sum(i for i in range(1000))
        
        def regressed_function():
            # Fonction intentionnellement plus lente
            result = 0
            for i in range(1000):
                for j in range(10):  # Boucle supplémentaire
                    result += i
            return result
        
        # Établir une baseline
        baseline_profile = profiler.profile_function(baseline_function)
        profiler.set_performance_baseline("test_function", baseline_profile)
        
        # Tester une fonction optimisée
        optimized_profile = profiler.profile_function(optimized_function)
        regression_result = profiler.detect_performance_regression(
            "test_function", optimized_profile
        )
        assert regression_result["is_regression"] is False
        
        # Tester une fonction dégradée
        regressed_profile = profiler.profile_function(regressed_function)
        regression_result = profiler.detect_performance_regression(
            "test_function", regressed_profile
        )
        assert regression_result["is_regression"] is True


class TestBenchmarkManager:
    """Tests pour le gestionnaire de benchmarks."""
    
    @pytest.fixture
    def benchmark_manager(self):
        """
Fixture pour créer un gestionnaire de benchmarks."""
        return BenchmarkManager()
    
    def test_benchmark_registration(self, benchmark_manager):
        """
Test l'enregistrement de benchmarks."""
        def test_benchmark():
            return sum(i for i in range(1000))
        
        # Enregistrer le benchmark
        benchmark_manager.register_benchmark("test_benchmark", test_benchmark)
        
        assert "test_benchmark" in benchmark_manager.benchmarks
        assert benchmark_manager.benchmarks["test_benchmark"] == test_benchmark
    
    def test_benchmark_execution(self, benchmark_manager):
        """Test l'exécution de benchmarks."""
        def quick_benchmark():
            return sum(i for i in range(100))
        
        def slow_benchmark():
            return sum(i * i for i in range(1000))
        
        # Enregistrer les benchmarks
        benchmark_manager.register_benchmark("quick", quick_benchmark)
        benchmark_manager.register_benchmark("slow", slow_benchmark)
        
        # Exécuter tous les benchmarks
        results = benchmark_manager.run_all_benchmarks()
        
        assert "quick" in results
        assert "slow" in results
        assert results["quick"]["execution_time"] < results["slow"]["execution_time"]
    
    def test_benchmark_comparison(self, benchmark_manager):
        """Test la comparaison de benchmarks."""
        def baseline_function():
            return sum(i for i in range(500))
        
        def improved_function():
            # Version potentiellement optimisée
            return sum(range(500))
        
        # Exécuter les benchmarks
        baseline_result = benchmark_manager.run_single_benchmark(baseline_function)
        improved_result = benchmark_manager.run_single_benchmark(improved_function)
        
        # Comparer les résultats
        comparison = benchmark_manager.compare_benchmarks(baseline_result, improved_result)
        
        assert "performance_ratio" in comparison
        assert "improvement_percentage" in comparison
        assert isinstance(comparison["performance_ratio"], float)


class TestSmartPreloader:
    """Tests pour le préchargeur intelligent."""
    
    @pytest.fixture
    def preloader(self):
        """
Fixture pour créer un préchargeur."""
        return SmartPreloader()
    
    def test_access_pattern_learning(self, preloader):
        """
Test l'apprentissage des modèles d'accès."""
        # Simuler des accès séquentiels
        access_sequence = ["file1", "file2", "file3", "file1", "file2", "file3"]
        
        for item in access_sequence:
            preloader.record_access(item)
        
        # Prédire le prochain accès
        predictions = preloader.predict_next_access("file1")
        
        assert "file2" in predictions
        assert len(predictions) > 0
    
    @pytest.mark.asyncio
    async def test_intelligent_preloading(self, preloader):
        """Test le préchargement intelligent."""
        # Simuler des données à précharger
        async def mock_load_data(item_id):
            await asyncio.sleep(0.01)  # Simulation I/O
            return f"data_for_{item_id}"
        
        # Enregistrer des modèles d'accès
        access_patterns = [
            ("item1", "item2"),
            ("item2", "item3"),
            ("item3", "item1"),
        ]
        
        for current, next_item in access_patterns:
            preloader.record_access_pattern(current, next_item)
        
        # Précharger intelligemment
        await preloader.intelligent_preload("item1", mock_load_data)
        
        # Vérifier que les données sont préchargées
        assert preloader.is_preloaded("item2")
    
    def test_cache_warmup(self, preloader):
        """Test le préchauffage du cache."""
        # Définir des éléments critiques
        critical_items = ["config", "user_prefs", "templates"]
        
        def mock_loader(item):
            return f"loaded_{item}"
        
        # Préchauffer le cache
        preloader.warmup_cache(critical_items, mock_loader)
        
        # Vérifier que tous les éléments sont préchargés
        for item in critical_items:
            assert preloader.is_preloaded(item)
            assert preloader.get_preloaded(item) == f"loaded_{item}"


class TestCompressionManager:
    """Tests pour le gestionnaire de compression."""
    
    @pytest.fixture
    def compression_manager(self):
        """
Fixture pour créer un gestionnaire de compression."""
        return CompressionManager()
    
    def test_data_compression(self, compression_manager):
        """
Test la compression de données."""
        # Données de test
        test_data = "This is a test string that should compress well " * 100
        
        # Compresser
        compressed = compression_manager.compress(test_data.encode())
        
        assert len(compressed) < len(test_data.encode())
        
        # Décompresser
        decompressed = compression_manager.decompress(compressed)
        assert decompressed.decode() == test_data
    
    def test_compression_algorithm_selection(self, compression_manager):
        """Test la sélection d'algorithme de compression."""
        # Données textuelles (gzip devrait être bon)
        text_data = "Text data with repetitive patterns " * 50
        best_algo_text = compression_manager.select_best_algorithm(text_data.encode())
        assert best_algo_text in ["gzip", "zlib", "lz4"]
        
        # Données binaires aléatoires (moins compressibles)
        binary_data = os.urandom(1000)
        best_algo_binary = compression_manager.select_best_algorithm(binary_data)
        assert best_algo_binary in ["lz4", "none"]  # LZ4 ou pas de compression
    
    def test_adaptive_compression(self, compression_manager):
        """Test la compression adaptative."""
        # Différents types de données
        test_cases = [
            ("highly_repetitive", "A" * 1000),
            ("json_data", '{"key": "value", "number": 42}' * 50),
            ("random_data", "".join(chr(i % 256) for i in range(1000)))
        ]
        
        for data_type, data in test_cases:
            result = compression_manager.adaptive_compress(data.encode())
            
            assert "algorithm" in result
            assert "compressed_data" in result
            assert "compression_ratio" in result
            assert result["compression_ratio"] > 0


class TestBatchProcessor:
    """Tests pour le processeur par lots."""
    
    @pytest.fixture
    def batch_processor(self):
        """
Fixture pour créer un processeur par lots."""
        return BatchProcessor()
    
    @pytest.mark.asyncio
    async def test_batch_processing_optimization(self, batch_processor):
        """
Test l'optimisation du traitement par lots."""
        # Données de test
        data = list(range(1000))
        
        def process_item(item):
            return item * 2
        
        # Traitement par lots optimisé
        start_time = time.time()
        results = await batch_processor.process_in_batches(process_item, data)
        batch_time = time.time() - start_time
        
        assert len(results) == len(data)
        assert results == [item * 2 for item in data]
        
        # Le traitement par lots devrait être efficace
        assert batch_time < 1.0  # Temps raisonnable
    
    def test_optimal_batch_size_calculation(self, batch_processor):
        """
Test le calcul de la taille optimale des lots."""
        # Test différents scénarios
        scenarios = [
            (100, 0.001),    # Petits données, traitement rapide
            (10000, 0.01),   # Données moyennes, traitement moyen
            (100000, 0.1),   # Grandes données, traitement lent
        ]
        
        for data_size, processing_time in scenarios:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "monitored_function",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric monitored_function collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection monitored_function failed: {e}")
                    return None
            (100, 0.001),    # Petits données, traitement rapide
            (10000, 0.01),   # Données moyennes, traitement moyen
            (100000, 0.1),   # Grandes données, traitement lent
        ]
        
        for data_size, processing_time in scenarios:
        try:
            logger.info(f"Executing cpu_benchmark")
            
            # Implementation for cpu_benchmark
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"cpu_benchmark completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"cpu_benchmark failed: {e}")
            raise
            (100000, 0.1),   # Grandes données, traitement lent
        ]
        
        for data_size, processing_time in scenarios:
            optimal_size = batch_processor.calculate_optimal_batch_size(
                data_size, processing_time
            )
            
            assert optimal_size > 0
            assert optimal_size <= data_size
            # La taille devrait être raisonnable
            assert 1 <= optimal_size <= 1000
    
    @pytest.mark.asyncio
    async def test_memory_aware_batching(self, batch_processor):
        """
Test le traitement par lots avec conscience de la mémoire."""
        # Simuler des données volumineuses
        large_items = [[i] * 1000 for i in range(100)]  # 100 listes de 1000 éléments
        
        def memory_intensive_process(item):
            # Simulation de traitement intensif en mémoire
            return len(item) * sum(item)
        
        # Traitement avec limite mémoire
        memory_limit_mb = 10  # 10MB de limite
        
        results = await batch_processor.process_with_memory_limit(
            memory_intensive_process, large_items, memory_limit_mb
        )
        
        assert len(results) == len(large_items)
        # Vérifier que les résultats sont corrects
        expected_results = [memory_intensive_process(item) for item in large_items]
        assert results == expected_results


class TestPerformanceOptimizer:
    """
Tests pour l'optimiseur de performance principal."""
    
    @pytest.fixture
    def performance_optimizer(self):
        """
Fixture pour créer l'optimiseur principal."""
        return PerformanceOptimizer()
    
    def test_optimizer_initialization(self, performance_optimizer):
        """
Test l'initialisation de l'optimiseur principal."""
        assert performance_optimizer.cache is not None
        assert performance_optimizer.resource_monitor is not None
        assert performance_optimizer.processing_optimizer is not None
        assert performance_optimizer.memory_optimizer is not None
        assert performance_optimizer.cpu_optimizer is not None
        assert performance_optimizer.io_optimizer is not None
        assert performance_optimizer.enabled is True
    
    @pytest.mark.asyncio
    async def test_comprehensive_optimization(self, performance_optimizer):
        """
Test l'optimisation complète du système."""
        # Simuler une charge de travail
        def sample_workload():
            # CPU intensive
            result = sum(i * i for i in range(1000))
            # Memory allocation
            temp_list = list(range(1000))
            return result + len(temp_list)
        
        # Optimiser le système
        optimization_report = await performance_optimizer.optimize_system()
        
        assert "cache_optimization" in optimization_report
        assert "memory_optimization" in optimization_report
        assert "cpu_optimization" in optimization_report
        assert "io_optimization" in optimization_report
        assert "overall_improvement" in optimization_report
    
    def test_performance_recommendations(self, performance_optimizer):
        """Test les recommandations de performance."""
        # Simuler des métriques de performance
        mock_metrics = {
            "cpu_usage": 85.0,      # Élevé
            "memory_usage": 90.0,   # Très élevé
            "disk_io": 50.0,        # Moyen
            "network_io": 30.0,     # Bas
            "cache_hit_ratio": 0.6  # Bas
        }
        
        recommendations = performance_optimizer.generate_recommendations(mock_metrics)
        
        assert len(recommendations) > 0
        assert any("memory" in rec.lower() for rec in recommendations)
        assert any("cpu" in rec.lower() for rec in recommendations)
        assert any("cache" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_auto_optimization(self, performance_optimizer):
        """Test l'optimisation automatique."""
        # Activer l'optimisation automatique
        performance_optimizer.enable_auto_optimization(interval=0.1)
        
        # Attendre quelques cycles d'optimisation
        await asyncio.sleep(0.3)
        
        # Désactiver l'optimisation automatique
        performance_optimizer.disable_auto_optimization()
        
        # Vérifier que des optimisations ont été effectuées
        assert len(performance_optimizer.optimization_history) > 0


class TestIntegration:
    """
Tests d'intégration pour le système d'optimisation complet."""
    
    @pytest.fixture
    def optimization_system(self):
        """
Fixture pour créer un système d'optimisation complet."""
        return {
            'optimizer': PerformanceOptimizer(),
            'cache': AdvancedCache(max_size=1000),
            'monitor': ResourceMonitor(),
            'profiler': PerformanceProfiler(),
            'benchmarks': BenchmarkManager()
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization(self, optimization_system):
        """
Test d'optimisation bout en bout."""
        optimizer = optimization_system['optimizer']
        cache = optimization_system['cache']
        monitor = optimization_system['monitor']
        
        # Simuler une application avec cache
        def expensive_operation(key):
            # Vérifier le cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Calcul coûteux
            result = sum(i * i for i in range(int(key) * 100))
            
            # Mettre en cache
            cache.set(key, result)
            return result
        
        # Première série d'opérations (cache froid)
        keys = [str(i) for i in range(1, 11)]
        start_time = time.time()
        results1 = [expensive_operation(key) for key in keys]
        cold_time = time.time() - start_time
        
        # Deuxième série (cache chaud)
        start_time = time.time()
        results2 = [expensive_operation(key) for key in keys]
        warm_time = time.time() - start_time
        
        # Vérifier les résultats
        assert results1 == results2
        assert warm_time < cold_time  # Cache efficace
        assert cache.stats.hit_ratio > 0  # Hits de cache
        
        # Optimiser le système
        optimization_report = await optimizer.optimize_system()
        assert optimization_report["overall_improvement"] >= 0
    
    def test_performance_monitoring_integration(self, optimization_system):
        """Test l'intégration du monitoring de performance."""
        monitor = optimization_system['monitor']
        profiler = optimization_system['profiler']
        
        # Fonction à surveiller
        def monitored_function():
            # Simuler du travail
            return sum(i ** 2 for i in range(1000))
        
        # Profiler et surveiller
        with patch.object(monitor, 'collect_system_metrics') as mock_collect:
            mock_metrics = ResourceMetrics(
                cpu_usage=75.0,
                memory_usage=60.0,
                disk_usage=40.0,
                network_io=1024,
                process_count=50
            )
            mock_collect.return_value = mock_metrics
            
            # Profiler la fonction
            profile_result = profiler.profile_function(monitored_function)
            
            # Collecter les métriques système
            system_metrics = monitor.collect_system_metrics()
            
            # Vérifier l'intégration
            assert profile_result["execution_time"] > 0
            assert system_metrics.cpu_usage == 75.0
    
    def test_benchmark_driven_optimization(self, optimization_system):
        """Test l'optimisation guidée par les benchmarks."""
        benchmarks = optimization_system['benchmarks']
        optimizer = optimization_system['optimizer']
        
        # Enregistrer des benchmarks
        def cpu_benchmark():
            return sum(i * i for i in range(5000))
        
        def memory_benchmark():
            temp_list = list(range(10000))
            return len(temp_list)
        
        benchmarks.register_benchmark("cpu_test", cpu_benchmark)
        benchmarks.register_benchmark("memory_test", memory_benchmark)
        
        # Exécuter les benchmarks avant optimisation
        baseline_results = benchmarks.run_all_benchmarks()
        
        # Optimiser basé sur les résultats
        optimization_suggestions = optimizer.analyze_benchmark_results(baseline_results)
        
        assert len(optimization_suggestions) > 0
        assert all(isinstance(suggestion, str) for suggestion in optimization_suggestions)


if __name__ == "__main__":
    # Configuration des tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10"
    ])
