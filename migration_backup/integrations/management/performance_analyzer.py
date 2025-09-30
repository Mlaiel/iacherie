"""
🔗 Ainflue Enterprise Integration Management - Performance Analyzer with ML

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, vol ou reproduction sans autorisation écrite de Fahed Mlaiel (mlaiel@live.de)
est strictement interdite et passible de poursuites judiciaires.

© 2025 Fahed Mlaiel - Tous droits réservés
Email: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import cProfile
import pstats
import io
import psutil
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import sqlite3
import pandas as pd
from collections import defaultdict, deque
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BottleneckType(Enum):
    """Types de goulots d'étranglement"""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    ALGORITHM = "algorithm"
    CONCURRENCY = "concurrency"

class PerformanceMetric(Enum):
    """Métriques de performance"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"
    CONCURRENCY_LEVEL = "concurrency_level"

class OptimizationStrategy(Enum):
    """Stratégies d'optimisation"""
    CACHING = "caching"
    INDEXING = "indexing"
    LOAD_BALANCING = "load_balancing"
    RESOURCE_SCALING = "resource_scaling"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    CONCURRENCY_TUNING = "concurrency_tuning"
    COMPRESSION = "compression"
    PREFETCHING = "prefetching"

@dataclass
class PerformanceDataPoint:
    """Point de données de performance"""
    timestamp: datetime
    metric: PerformanceMetric
    value: float
    context: Dict[str, Any]
    tags: Dict[str, str]

@dataclass
class Bottleneck:
    """Goulot d'étranglement identifié"""
    id: str
    type: BottleneckType
    severity: float  # 0-100
    location: str
    description: str
    impact: str
    detected_at: datetime
    metrics: List[PerformanceDataPoint]
    recommendations: List[str]

@dataclass
class OptimizationRecommendation:
    """Recommandation d'optimisation"""
    id: str
    strategy: OptimizationStrategy
    priority: int  # 1-10
    estimated_improvement: float  # %
    implementation_effort: str  # low, medium, high
    description: str
    code_changes: List[str]
    config_changes: Dict[str, Any]
    expected_metrics: Dict[str, float]

@dataclass
class ProfileReport:
    """Rapport de profilage"""
    id: str
    function_name: str
    execution_time: float
    call_count: int
    cumulative_time: float
    hotspots: List[Dict[str, Any]]
    memory_usage: float
    generated_at: datetime

class DatabaseQueryAnalyzer:
    """Analyseur de requêtes de base de données"""
    
    def __init__(self):
        self.slow_queries: List[Dict[str, Any]] = []
        self.query_patterns: Dict[str, int] = defaultdict(int)
        
    def analyze_query(self, query: str, execution_time: float, 
                     explain_plan: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyse une requête de base de données"""
        try:
            analysis = {
                "query": query,
                "execution_time": execution_time,
                "is_slow": execution_time > 1.0,  # > 1 seconde
                "recommendations": [],
                "severity": "low"
            }
            
            # Analyser les patterns de requête
            query_lower = query.lower().strip()
            
            # Détecter les requêtes problématiques
            if "select *" in query_lower:
                analysis["recommendations"].append("Éviter SELECT *, spécifier les colonnes nécessaires")
                analysis["severity"] = "medium"
            
            if "where" not in query_lower and ("select" in query_lower or "update" in query_lower or "delete" in query_lower):
                analysis["recommendations"].append("Ajouter une clause WHERE pour limiter les résultats")
                analysis["severity"] = "high"
            
            if "order by" in query_lower and "limit" not in query_lower:
                analysis["recommendations"].append("Ajouter LIMIT avec ORDER BY pour améliorer les performances")
                analysis["severity"] = "medium"
            
            if "like '%" in query_lower:
                analysis["recommendations"].append("Éviter LIKE avec préfixe wildcard, considérer full-text search")
                analysis["severity"] = "medium"
            
            # Suggestions d'index basées sur les colonnes WHERE
            where_columns = self._extract_where_columns(query)
            if where_columns:
                analysis["index_suggestions"] = [
                    f"CREATE INDEX idx_{col} ON table_name ({col})" 
                    for col in where_columns
                ]
            
            # Analyser le plan d'exécution si disponible
            if explain_plan:
                analysis["explain_analysis"] = self._analyze_explain_plan(explain_plan)
            
            # Enregistrer si c'est une requête lente
            if analysis["is_slow"]:
                self.slow_queries.append(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de requête: {e}")
            return {"error": str(e)}
    
    def _extract_where_columns(self, query: str) -> List[str]:
        """Extrait les colonnes utilisées dans les clauses WHERE"""
        # Implémentation simplifiée - en réalité, utiliser un parser SQL
        columns = []
        try:
            query_lower = query.lower()
            if "where" in query_lower:
                where_part = query_lower.split("where")[1].split("order by")[0].split("group by")[0]
                # Extraction basique - améliorer avec un parser SQL réel
                words = where_part.split()
                for i, word in enumerate(words):
                    if word in ["=", "<", ">", "<=", ">=", "!=", "like", "in"] and i > 0:
                        potential_column = words[i-1].strip("(),")
                        if potential_column.isalnum():
                            columns.append(potential_column)
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des colonnes WHERE: {e}")
        
        return columns
    
    def _analyze_explain_plan(self, plan: Dict) -> Dict[str, Any]:
        """Analyse un plan d'exécution"""
        analysis = {
            "table_scans": 0,
            "index_usage": [],
            "join_types": [],
            "recommendations": []
        }
        
        # Analyser le plan (structure simplifiée)
        if isinstance(plan, dict):
            if "Seq Scan" in str(plan):
                analysis["table_scans"] += 1
                analysis["recommendations"].append("Table scan détecté - considérer ajouter un index")
            
            if "Index Scan" in str(plan):
                analysis["index_usage"].append("Index utilisé efficacement")
            
            if "Hash Join" in str(plan):
                analysis["join_types"].append("Hash Join")
            elif "Nested Loop" in str(plan):
                analysis["join_types"].append("Nested Loop")
                analysis["recommendations"].append("Nested Loop peut être lent pour grandes données")
        
        return analysis

class MemoryProfiler:
    """Profileur de mémoire avancé"""
    
    def __init__(self):
        self.memory_snapshots: List[Dict[str, Any]] = []
        self.leak_candidates: List[Dict[str, Any]] = []
        
    def take_snapshot(self, label: str = "") -> Dict[str, Any]:
        """Prend un snapshot de l'utilisation mémoire"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            snapshot = {
                "timestamp": datetime.now(),
                "label": label,
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available,
                "details": {
                    "rss_mb": memory_info.rss / 1024 / 1024,
                    "vms_mb": memory_info.vms / 1024 / 1024,
                    "shared": getattr(memory_info, 'shared', 0) / 1024 / 1024,
                    "text": getattr(memory_info, 'text', 0) / 1024 / 1024,
                    "data": getattr(memory_info, 'data', 0) / 1024 / 1024
                }
            }
            
            self.memory_snapshots.append(snapshot)
            
            # Limiter l'historique
            if len(self.memory_snapshots) > 1000:
                self.memory_snapshots = self.memory_snapshots[-1000:]
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Erreur lors de la prise de snapshot mémoire: {e}")
            return {}
    
    def detect_memory_leaks(self) -> List[Dict[str, Any]]:
        """Détecte les fuites mémoire potentielles"""
        try:
            if len(self.memory_snapshots) < 10:
                return []
            
            leaks = []
            
            # Analyser la tendance de consommation mémoire
            recent_snapshots = self.memory_snapshots[-50:]  # 50 derniers
            memory_values = [s["rss"] for s in recent_snapshots]
            
            # Calculer la tendance (régression linéaire simple)
            x = np.arange(len(memory_values))
            coefficients = np.polyfit(x, memory_values, 1)
            slope = coefficients[0]
            
            # Si la pente est positive et significative, c'est potentiellement une fuite
            if slope > 1024 * 1024:  # Plus de 1MB de croissance par snapshot
                leak = {
                    "type": "memory_growth",
                    "severity": "high" if slope > 10 * 1024 * 1024 else "medium",
                    "growth_rate_mb_per_snapshot": slope / 1024 / 1024,
                    "detected_at": datetime.now(),
                    "recommendations": [
                        "Vérifier les objets non libérés",
                        "Analyser les caches qui grandissent indéfiniment",
                        "Vérifier les closures et références circulaires"
                    ]
                }
                leaks.append(leak)
            
            # Détecter les pics de mémoire
            if len(memory_values) > 5:
                mean_mem = statistics.mean(memory_values)
                std_mem = statistics.stdev(memory_values)
                
                for i, value in enumerate(memory_values[-10:]):  # 10 dernières valeurs
                    if value > mean_mem + 2 * std_mem:  # 2 écarts-types au-dessus
                        spike = {
                            "type": "memory_spike",
                            "severity": "medium",
                            "value_mb": value / 1024 / 1024,
                            "deviation_from_mean": (value - mean_mem) / 1024 / 1024,
                            "timestamp": recent_snapshots[-(10-i)]["timestamp"],
                            "recommendations": [
                                "Identifier l'opération causant le pic",
                                "Optimiser l'allocation mémoire",
                                "Considérer le streaming pour les gros volumes"
                            ]
                        }
                        leaks.append(spike)
            
            self.leak_candidates.extend(leaks)
            return leaks
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de fuites mémoire: {e}")
            return []

class CacheAnalyzer:
    """Analyseur de performance du cache"""
    
    def __init__(self):
        self.cache_stats: Dict[str, Dict[str, Any]] = {}
        self.recommendations: List[str] = []
        
    def analyze_cache_performance(self, cache_name: str, 
                                hits: int, misses: int, 
                                evictions: int = 0) -> Dict[str, Any]:
        """Analyse les performances d'un cache"""
        try:
            total_requests = hits + misses
            if total_requests == 0:
                return {"error": "Aucune requête de cache"}
            
            hit_rate = (hits / total_requests) * 100
            miss_rate = (misses / total_requests) * 100
            
            analysis = {
                "cache_name": cache_name,
                "hit_rate": hit_rate,
                "miss_rate": miss_rate,
                "total_requests": total_requests,
                "evictions": evictions,
                "efficiency": "excellent" if hit_rate > 90 else "good" if hit_rate > 80 else "poor",
                "recommendations": []
            }
            
            # Générer des recommandations
            if hit_rate < 80:
                analysis["recommendations"].extend([
                    "Taux de hit faible - vérifier la stratégie de mise en cache",
                    "Considérer augmenter la taille du cache",
                    "Analyser les patterns d'accès aux données"
                ])
            
            if evictions > total_requests * 0.1:  # Plus de 10% d'évictions
                analysis["recommendations"].extend([
                    "Trop d'évictions - augmenter la taille du cache",
                    "Optimiser la politique d'éviction (LRU, LFU, etc.)"
                ])
            
            if miss_rate > 50:
                analysis["recommendations"].extend([
                    "Taux de miss très élevé - revoir la stratégie de cache",
                    "Implémenter le cache warming",
                    "Optimiser les clés de cache"
                ])
            
            # Enregistrer les statistiques
            self.cache_stats[cache_name] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du cache: {e}")
            return {"error": str(e)}
    
    def suggest_cache_improvements(self, cache_name: str) -> List[str]:
        """Suggère des améliorations pour un cache"""
        if cache_name not in self.cache_stats:
            return ["Aucune donnée disponible pour ce cache"]
        
        stats = self.cache_stats[cache_name]
        suggestions = []
        
        # Suggestions basées sur les métriques
        if stats["hit_rate"] < 70:
            suggestions.extend([
                "Implémenter le prefetching pour les données prévisibles",
                "Utiliser une stratégie de cache à plusieurs niveaux (L1, L2)",
                "Optimiser la sérialisation/désérialisation des objets cachés"
            ])
        
        if stats["evictions"] > 0:
            suggestions.extend([
                "Monitorer les patterns d'éviction",
                "Considérer un cache distribué pour plus de capacité",
                "Implémenter la compression des données cachées"
            ])
        
        return suggestions

class MLPerformancePredictor:
    """Prédicteur de performance basé sur ML"""
    
    def __init__(self):
        self.models: Dict[str, RandomForestRegressor] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.training_data: Dict[str, List[Dict]] = defaultdict(list)
        self.is_trained: Dict[str, bool] = defaultdict(bool)
        
    def add_training_data(self, metric: str, features: List[float], target: float) -> None:
        """Ajoute des données d'entraînement"""
        self.training_data[metric].append({
            "features": features,
            "target": target,
            "timestamp": datetime.now()
        })
    
    def train_model(self, metric: str) -> Dict[str, Any]:
        """Entraîne un modèle pour prédire une métrique"""
        try:
            if len(self.training_data[metric]) < 50:
                return {"error": "Pas assez de données d'entraînement"}
            
            # Préparer les données
            data = self.training_data[metric]
            X = np.array([d["features"] for d in data])
            y = np.array([d["target"] for d in data])
            
            # Diviser en train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Normaliser les features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entraîner le modèle
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Évaluer
            y_pred = model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            
            # Sauvegarder
            self.models[metric] = model
            self.scalers[metric] = scaler
            self.is_trained[metric] = True
            
            results = {
                "metric": metric,
                "r2_score": r2,
                "mse": mse,
                "feature_importance": model.feature_importances_.tolist(),
                "training_samples": len(data),
                "model_accuracy": "excellent" if r2 > 0.9 else "good" if r2 > 0.7 else "poor"
            }
            
            logger.info(f"Modèle entraîné pour {metric}: R²={r2:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle: {e}")
            return {"error": str(e)}
    
    def predict(self, metric: str, features: List[float]) -> Optional[float]:
        """Fait une prédiction"""
        try:
            if not self.is_trained.get(metric, False):
                return None
            
            model = self.models[metric]
            scaler = self.scalers[metric]
            
            # Normaliser et prédire
            features_scaled = scaler.transform([features])
            prediction = model.predict(features_scaled)[0]
            
            return float(prediction)
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return None
    
    def predict_bottlenecks(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Prédit les goulots d'étranglement potentiels"""
        predictions = []
        
        try:
            # Prédire chaque métrique
            for metric_name in ["cpu_usage", "memory_usage", "response_time"]:
                if metric_name in self.models:
                    # Utiliser les métriques actuelles comme features
                    features = list(current_metrics.values())
                    
                    if len(features) >= 3:  # Minimum de features requises
                        predicted_value = self.predict(metric_name, features[:3])
                        
                        if predicted_value is not None:
                            # Déterminer si c'est un bottleneck potentiel
                            current_value = current_metrics.get(metric_name, 0)
                            increase = predicted_value - current_value
                            
                            if increase > 0:
                                severity = "high" if increase > current_value * 0.5 else "medium"
                                predictions.append({
                                    "metric": metric_name,
                                    "current_value": current_value,
                                    "predicted_value": predicted_value,
                                    "increase": increase,
                                    "severity": severity,
                                    "probability": min(increase / current_value, 1.0) if current_value > 0 else 0.5
                                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction de bottlenecks: {e}")
            return []

class EnterprisePerformanceAnalyzer:
    """
    Analyseur de performance enterprise pour Ainflue
    
    Fonctionnalités:
    - Détection ML des goulots d'étranglement
    - Profilage automatique du code
    - Analyse des requêtes de base de données
    - Optimisation intelligente des ressources  
    - Prédictions de performance avec ML
    """
    
    def __init__(self):
        # Propriété intellectuelle
        self.creator = "Fahed Mlaiel"
        self.email = "mlaiel@live.de"
        self.copyright = "© 2025 Fahed Mlaiel - Tous droits réservés"
        
        # Composants d'analyse
        self.db_analyzer = DatabaseQueryAnalyzer()
        self.memory_profiler = MemoryProfiler()
        self.cache_analyzer = CacheAnalyzer()
        self.ml_predictor = MLPerformancePredictor()
        
        # Données de performance
        self.performance_data: List[PerformanceDataPoint] = []
        self.bottlenecks: Dict[str, Bottleneck] = {}
        self.recommendations: List[OptimizationRecommendation] = []
        self.profile_reports: List[ProfileReport] = []
        
        # Configuration
        self.monitoring_enabled = True
        self.profiling_enabled = True
        self.ml_enabled = True
        
        # Base de données pour l'historique
        self.db_path = "/tmp/performance_history.db"
        self._init_database()
        
        logger.info("🔗 Enterprise Performance Analyzer initialisé par Fahed Mlaiel")
    
    def _init_database(self) -> None:
        """Initialise la base de données pour l'historique"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour les données de performance
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    metric TEXT,
                    value REAL,
                    context TEXT,
                    tags TEXT
                )
            """)
            
            # Table pour les bottlenecks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bottlenecks (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    severity REAL,
                    location TEXT,
                    description TEXT,
                    detected_at TEXT,
                    resolved_at TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la BDD: {e}")
    
    def add_performance_data(self, metric: PerformanceMetric, value: float,
                           context: Dict[str, Any] = None,
                           tags: Dict[str, str] = None) -> None:
        """Ajoute un point de données de performance"""
        try:
            data_point = PerformanceDataPoint(
                timestamp=datetime.now(),
                metric=metric,
                value=value,
                context=context or {},
                tags=tags or {}
            )
            
            self.performance_data.append(data_point)
            
            # Limiter l'historique en mémoire
            if len(self.performance_data) > 10000:
                self.performance_data = self.performance_data[-10000:]
            
            # Sauvegarder en base
            self._save_performance_data(data_point)
            
            # Alimenter le ML si activé
            if self.ml_enabled:
                self._feed_ml_model(data_point)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des données de performance: {e}")
    
    def _save_performance_data(self, data_point: PerformanceDataPoint) -> None:
        """Sauvegarde un point de données en base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_data (timestamp, metric, value, context, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data_point.timestamp.isoformat(),
                data_point.metric.value,
                data_point.value,
                json.dumps(data_point.context),
                json.dumps(data_point.tags)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde en BDD: {e}")
    
    def _feed_ml_model(self, data_point: PerformanceDataPoint) -> None:
        """Alimente les modèles ML avec les nouvelles données"""
        try:
            # Récupérer les métriques récentes pour créer des features
            recent_data = self.performance_data[-10:]  # 10 derniers points
            
            if len(recent_data) >= 3:
                # Créer des features basées sur les métriques récentes
                features = []
                for metric_type in [PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE, PerformanceMetric.RESPONSE_TIME]:
                    recent_values = [d.value for d in recent_data if d.metric == metric_type]
                    if recent_values:
                        features.append(statistics.mean(recent_values))
                    else:
                        features.append(0.0)
                
                # Ajouter aux données d'entraînement
                if len(features) >= 3:
                    self.ml_predictor.add_training_data(
                        data_point.metric.value,
                        features,
                        data_point.value
                    )
                    
                    # Entraîner périodiquement
                    if len(self.ml_predictor.training_data[data_point.metric.value]) % 100 == 0:
                        self.ml_predictor.train_model(data_point.metric.value)
        
        except Exception as e:
            logger.error(f"Erreur lors de l'alimentation ML: {e}")
    
    def profile_function(self, func: Callable, *args, **kwargs) -> ProfileReport:
        """Profile une fonction spécifique"""
        try:
            profiler = cProfile.Profile()
            
            # Prendre un snapshot mémoire avant
            mem_before = self.memory_profiler.take_snapshot("before_" + func.__name__)
            
            # Profiler l'exécution
            start_time = time.time()
            profiler.enable()
            
            result = func(*args, **kwargs)
            
            profiler.disable()
            end_time = time.time()
            
            # Prendre un snapshot mémoire après
            mem_after = self.memory_profiler.take_snapshot("after_" + func.__name__)
            
            # Analyser les résultats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 fonctions
            
            profile_output = s.getvalue()
            
            # Extraire les hotspots
            hotspots = self._extract_hotspots(ps)
            
            # Calculer l'utilisation mémoire
            memory_usage = 0
            if mem_before and mem_after:
                memory_usage = mem_after.get("rss", 0) - mem_before.get("rss", 0)
            
            # Créer le rapport
            report = ProfileReport(
                id=hashlib.md5(f"{func.__name__}_{int(time.time())}".encode()).hexdigest()[:8],
                function_name=func.__name__,
                execution_time=end_time - start_time,
                call_count=ps.total_calls,
                cumulative_time=ps.total_tt,
                hotspots=hotspots,
                memory_usage=memory_usage,
                generated_at=datetime.now()
            )
            
            self.profile_reports.append(report)
            
            # Analyser pour détecter des bottlenecks
            self._analyze_profile_for_bottlenecks(report)
            
            logger.info(f"🔍 Profilage de {func.__name__} terminé: {report.execution_time:.3f}s")
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors du profilage: {e}")
            return ProfileReport(
                id="error",
                function_name=func.__name__,
                execution_time=0,
                call_count=0,
                cumulative_time=0,
                hotspots=[],
                memory_usage=0,
                generated_at=datetime.now()
            )
    
    def _extract_hotspots(self, ps: pstats.Stats) -> List[Dict[str, Any]]:
        """Extrait les hotspots du profilage"""
        hotspots = []
        
        try:
            # Récupérer les statistiques triées
            stats = ps.get_stats_profile()
            
            # Extraire les fonctions les plus coûteuses
            for func_key, (call_count, rec_count, total_time, cumulative_time) in stats.func_profiles.items():
                if cumulative_time > 0.001:  # Seulement les fonctions qui prennent >1ms
                    filename, line_number, function_name = func_key
                    
                    hotspot = {
                        "function": function_name,
                        "filename": filename,
                        "line": line_number,
                        "call_count": call_count,
                        "total_time": total_time,
                        "cumulative_time": cumulative_time,
                        "time_per_call": total_time / call_count if call_count > 0 else 0
                    }
                    
                    hotspots.append(hotspot)
            
            # Trier par temps cumulatif
            hotspots.sort(key=lambda x: x["cumulative_time"], reverse=True)
            return hotspots[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des hotspots: {e}")
            return []
    
    def _analyze_profile_for_bottlenecks(self, report: ProfileReport) -> None:
        """Analyse un rapport de profilage pour détecter des bottlenecks"""
        try:
            # Détecter les bottlenecks basés sur le temps d'exécution
            if report.execution_time > 1.0:  # Plus de 1 seconde
                bottleneck_id = f"exec_time_{report.id}"
                
                bottleneck = Bottleneck(
                    id=bottleneck_id,
                    type=BottleneckType.ALGORITHM,
                    severity=min(report.execution_time * 10, 100),  # Max 100
                    location=report.function_name,
                    description=f"Fonction lente: {report.function_name} prend {report.execution_time:.3f}s",
                    impact=f"Impact sur la performance globale: {report.execution_time:.1f}s par appel",
                    detected_at=datetime.now(),
                    metrics=[],
                    recommendations=[
                        "Optimiser l'algorithme de la fonction",
                        "Considérer la mise en cache des résultats",
                        "Profiler plus en détail pour identifier les sous-opérations coûteuses"
                    ]
                )
                
                self.bottlenecks[bottleneck_id] = bottleneck
            
            # Détecter les bottlenecks mémoire
            if report.memory_usage > 100 * 1024 * 1024:  # Plus de 100MB
                bottleneck_id = f"memory_{report.id}"
                
                bottleneck = Bottleneck(
                    id=bottleneck_id,
                    type=BottleneckType.MEMORY,
                    severity=min(report.memory_usage / (10 * 1024 * 1024), 100),  # Échelle sur 10MB
                    location=report.function_name,
                    description=f"Forte consommation mémoire: {report.memory_usage / 1024 / 1024:.1f}MB",
                    impact="Risque de saturation mémoire",
                    detected_at=datetime.now(),
                    metrics=[],
                    recommendations=[
                        "Optimiser l'utilisation mémoire",
                        "Utiliser des générateurs au lieu de listes",
                        "Implémenter la pagination pour les gros datasets"
                    ]
                )
                
                self.bottlenecks[bottleneck_id] = bottleneck
            
            # Analyser les hotspots
            for hotspot in report.hotspots[:3]:  # Top 3 hotspots
                if hotspot["cumulative_time"] > 0.1:  # Plus de 100ms
                    bottleneck_id = f"hotspot_{report.id}_{hotspot['function']}"
                    
                    bottleneck = Bottleneck(
                        id=bottleneck_id,
                        type=BottleneckType.ALGORITHM,
                        severity=min(hotspot["cumulative_time"] * 100, 100),
                        location=f"{hotspot['function']} ({hotspot['filename']}:{hotspot['line']})",
                        description=f"Hotspot détecté: {hotspot['function']} - {hotspot['cumulative_time']:.3f}s",
                        impact=f"{hotspot['call_count']} appels, {hotspot['time_per_call']:.4f}s par appel",
                        detected_at=datetime.now(),
                        metrics=[],
                        recommendations=[
                            f"Optimiser la fonction {hotspot['function']}",
                            "Réduire le nombre d'appels si possible",
                            "Considérer la parallélisation"
                        ]
                    )
                    
                    self.bottlenecks[bottleneck_id] = bottleneck
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des bottlenecks: {e}")
    
    def analyze_database_performance(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les performances des requêtes de base de données"""
        try:
            analysis = {
                "total_queries": len(queries),
                "slow_queries": 0,
                "avg_execution_time": 0,
                "recommendations": [],
                "query_analysis": []
            }
            
            execution_times = []
            
            for query_info in queries:
                query = query_info.get("query", "")
                exec_time = query_info.get("execution_time", 0)
                explain_plan = query_info.get("explain_plan")
                
                execution_times.append(exec_time)
                
                # Analyser chaque requête
                query_analysis = self.db_analyzer.analyze_query(query, exec_time, explain_plan)
                analysis["query_analysis"].append(query_analysis)
                
                if query_analysis.get("is_slow", False):
                    analysis["slow_queries"] += 1
            
            # Calculer les statistiques globales
            if execution_times:
                analysis["avg_execution_time"] = statistics.mean(execution_times)
                analysis["max_execution_time"] = max(execution_times)
                analysis["min_execution_time"] = min(execution_times)
                analysis["median_execution_time"] = statistics.median(execution_times)
            
            # Générer des recommandations globales
            if analysis["slow_queries"] > len(queries) * 0.1:  # Plus de 10% de requêtes lentes
                analysis["recommendations"].extend([
                    "Trop de requêtes lentes détectées",
                    "Considérer l'ajout d'index sur les colonnes fréquemment utilisées",
                    "Optimiser les requêtes les plus coûteuses en priorité"
                ])
            
            if analysis["avg_execution_time"] > 0.5:  # Plus de 500ms en moyenne
                analysis["recommendations"].extend([
                    "Temps d'exécution moyen élevé",
                    "Analyser les plans d'exécution",
                    "Considérer la mise en cache des résultats"
                ])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des performances BDD: {e}")
            return {"error": str(e)}
    
    def get_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Génère des recommandations d'optimisation basées sur l'analyse"""
        try:
            recommendations = []
            
            # Analyser les bottlenecks pour générer des recommandations
            for bottleneck_id, bottleneck in self.bottlenecks.items():
                
                if bottleneck.type == BottleneckType.CPU:
                    recommendation = OptimizationRecommendation(
                        id=f"cpu_opt_{bottleneck_id}",
                        strategy=OptimizationStrategy.ALGORITHM_OPTIMIZATION,
                        priority=8,
                        estimated_improvement=25.0,
                        implementation_effort="medium",
                        description="Optimiser l'utilisation CPU avec algorithmes plus efficaces",
                        code_changes=[
                            "Remplacer les boucles imbriquées par des opérations vectorisées",
                            "Utiliser des structures de données plus efficaces (dict vs list)",
                            "Implémenter la mise en cache pour les calculs répétitifs"
                        ],
                        config_changes={
                            "worker_processes": "auto",
                            "cpu_affinity": True,
                            "optimization_level": "O2"
                        },
                        expected_metrics={
                            "cpu_usage_reduction": 20.0,
                            "response_time_improvement": 15.0
                        }
                    )
                    recommendations.append(recommendation)
                
                elif bottleneck.type == BottleneckType.MEMORY:
                    recommendation = OptimizationRecommendation(
                        id=f"memory_opt_{bottleneck_id}",
                        strategy=OptimizationStrategy.CACHING,
                        priority=7,
                        estimated_improvement=30.0,
                        implementation_effort="low",
                        description="Optimiser l'utilisation mémoire et implémenter le caching",
                        code_changes=[
                            "Implémenter un cache LRU pour les objets fréquemment utilisés",
                            "Utiliser des générateurs au lieu de listes pour les gros datasets",
                            "Optimiser la sérialisation des objets"
                        ],
                        config_changes={
                            "cache_size": "1GB",
                            "cache_ttl": 3600,
                            "memory_limit": "2GB"
                        },
                        expected_metrics={
                            "memory_usage_reduction": 25.0,
                            "cache_hit_rate": 85.0
                        }
                    )
                    recommendations.append(recommendation)
                
                elif bottleneck.type == BottleneckType.DATABASE:
                    recommendation = OptimizationRecommendation(
                        id=f"db_opt_{bottleneck_id}",
                        strategy=OptimizationStrategy.INDEXING,
                        priority=9,
                        estimated_improvement=40.0,
                        implementation_effort="medium",
                        description="Optimiser les performances de base de données",
                        code_changes=[
                            "Ajouter des index sur les colonnes WHERE fréquentes",
                            "Optimiser les requêtes JOIN",
                            "Implémenter la pagination pour les gros résultats"
                        ],
                        config_changes={
                            "query_cache_size": "256MB",
                            "innodb_buffer_pool_size": "1GB",
                            "slow_query_log": True
                        },
                        expected_metrics={
                            "query_time_reduction": 35.0,
                            "database_cpu_usage": -20.0
                        }
                    )
                    recommendations.append(recommendation)
            
            # Trier par priorité
            recommendations.sort(key=lambda x: x.priority, reverse=True)
            
            self.recommendations = recommendations
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return []
    
    def predict_future_performance(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Prédit les performances futures"""
        try:
            predictions = {}
            
            # Récupérer les métriques actuelles
            current_metrics = {}
            for data_point in self.performance_data[-10:]:  # 10 derniers points
                current_metrics[data_point.metric.value] = data_point.value
            
            # Faire des prédictions avec ML
            if self.ml_enabled:
                bottleneck_predictions = self.ml_predictor.predict_bottlenecks(current_metrics)
                predictions["bottlenecks"] = bottleneck_predictions
            
            # Prédictions basées sur les tendances
            trend_predictions = {}
            for metric in [PerformanceMetric.CPU_USAGE, PerformanceMetric.MEMORY_USAGE, PerformanceMetric.RESPONSE_TIME]:
                recent_values = [
                    d.value for d in self.performance_data[-100:] 
                    if d.metric == metric
                ]
                
                if len(recent_values) >= 10:
                    # Régression linéaire simple pour la tendance
                    x = np.arange(len(recent_values))
                    coefficients = np.polyfit(x, recent_values, 1)
                    slope = coefficients[0]
                    intercept = coefficients[1]
                    
                    # Prédire la valeur dans X heures
                    future_x = len(recent_values) + hours_ahead
                    predicted_value = slope * future_x + intercept
                    
                    trend_predictions[metric.value] = {
                        "current_value": recent_values[-1],
                        "predicted_value": max(0, predicted_value),  # Pas de valeurs négatives
                        "trend": "increasing" if slope > 0 else "decreasing",
                        "slope": slope,
                        "confidence": min(len(recent_values) / 100, 1.0)  # Confiance basée sur le nombre de points
                    }
            
            predictions["trends"] = trend_predictions
            
            # Recommandations préventives
            preventive_actions = []
            for metric, pred in trend_predictions.items():
                if pred["trend"] == "increasing" and pred["predicted_value"] > pred["current_value"] * 1.5:
                    preventive_actions.append({
                        "metric": metric,
                        "action": f"Surveiller de près {metric} - augmentation prévue de {pred['predicted_value'] - pred['current_value']:.1f}",
                        "urgency": "high" if pred["predicted_value"] > pred["current_value"] * 2 else "medium"
                    })
            
            predictions["preventive_actions"] = preventive_actions
            predictions["prediction_timestamp"] = datetime.now().isoformat()
            predictions["hours_ahead"] = hours_ahead
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return {"error": str(e)}
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Génère un rapport complet de performance"""
        try:
            report = {
                "generated_at": datetime.now().isoformat(),
                "creator": self.creator,
                "email": self.email,
                "copyright": self.copyright,
                "summary": {},
                "bottlenecks": {},
                "recommendations": [],
                "ml_insights": {},
                "database_analysis": {},
                "memory_analysis": {},
                "cache_analysis": {},
                "predictions": {}
            }
            
            # Résumé général
            report["summary"] = {
                "total_data_points": len(self.performance_data),
                "bottlenecks_detected": len(self.bottlenecks),
                "recommendations_count": len(self.recommendations),
                "profile_reports": len(self.profile_reports),
                "monitoring_period_hours": 24,  # Exemple
                "overall_health": "good"  # À calculer basé sur les métriques
            }
            
            # Bottlenecks détectés
            report["bottlenecks"] = {
                bid: asdict(bottleneck) for bid, bottleneck in self.bottlenecks.items()
            }
            
            # Recommandations
            report["recommendations"] = [
                asdict(rec) for rec in self.get_optimization_recommendations()
            ]
            
            # Insights ML
            if self.ml_enabled:
                report["ml_insights"] = {
                    "models_trained": len([k for k, v in self.ml_predictor.is_trained.items() if v]),
                    "training_data_points": sum(len(data) for data in self.ml_predictor.training_data.values()),
                    "prediction_accuracy": "good"  # À calculer basé sur les métriques réelles
                }
            
            # Analyse mémoire
            memory_leaks = self.memory_profiler.detect_memory_leaks()
            report["memory_analysis"] = {
                "snapshots_taken": len(self.memory_profiler.memory_snapshots),
                "leaks_detected": len(memory_leaks),
                "leak_details": memory_leaks
            }
            
            # Analyse du cache
            report["cache_analysis"] = {
                "caches_monitored": len(self.cache_analyzer.cache_stats),
                "cache_stats": self.cache_analyzer.cache_stats
            }
            
            # Prédictions
            report["predictions"] = self.predict_future_performance(24)
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {"error": str(e)}

# Exemple d'utilisation
async def main():
    """Fonction principale de démonstration"""
    print("🔗 Démarrage de l'analyseur de performance enterprise Ainflue")
    print("Créé par Fahed Mlaiel (mlaiel@live.de)")
    print("© 2025 Fahed Mlaiel - Tous droits réservés")
    
    # Créer l'analyseur
    analyzer = EnterprisePerformanceAnalyzer()
    
    # Simuler des données de performance
    print("📊 Simulation de données de performance...")
    
    for i in range(100):
        # CPU usage
        cpu_value = 50 + np.random.normal(0, 10) + i * 0.1  # Tendance croissante
        analyzer.add_performance_data(
            PerformanceMetric.CPU_USAGE,
            max(0, min(100, cpu_value)),
            {"source": "system_monitor"}
        )
        
        # Memory usage
        mem_value = 60 + np.random.normal(0, 8) + i * 0.05
        analyzer.add_performance_data(
            PerformanceMetric.MEMORY_USAGE,
            max(0, min(100, mem_value)),
            {"source": "system_monitor"}
        )
        
        # Response time
        response_time = 100 + np.random.normal(0, 20) + i * 0.2
        analyzer.add_performance_data(
            PerformanceMetric.RESPONSE_TIME,
            max(0, response_time),
            {"source": "application"}
        )
        
        await asyncio.sleep(0.01)  # Petite pause
    
    # Profiler une fonction exemple
    def example_slow_function():
        # Fonction intentionnellement lente pour démonstration
        time.sleep(0.1)
        data = [i**2 for i in range(1000)]
        return sum(data)
    
    print("🔍 Profilage d'une fonction exemple...")
    profile_report = analyzer.profile_function(example_slow_function)
    print(f"Fonction profilée: {profile_report.function_name}")
    print(f"Temps d'exécution: {profile_report.execution_time:.3f}s")
    
    # Analyser des requêtes de base de données fictives
    print("💾 Analyse des requêtes de base de données...")
    fake_queries = [
        {"query": "SELECT * FROM users WHERE active = 1", "execution_time": 0.5},
        {"query": "SELECT name FROM products ORDER BY created_at", "execution_time": 1.2},
        {"query": "UPDATE users SET last_login = NOW()", "execution_time": 2.5}
    ]
    
    db_analysis = analyzer.analyze_database_performance(fake_queries)
    print(f"Requêtes analysées: {db_analysis['total_queries']}")
    print(f"Requêtes lentes: {db_analysis['slow_queries']}")
    
    # Générer le rapport complet
    print("📄 Génération du rapport de performance...")
    report = analyzer.generate_performance_report()
    
    # Sauvegarder le rapport
    with open("/tmp/performance_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("\n✅ Analyse terminée!")
    print(f"📊 Points de données collectés: {len(analyzer.performance_data)}")
    print(f"🚨 Bottlenecks détectés: {len(analyzer.bottlenecks)}")
    print(f"💡 Recommandations générées: {len(analyzer.recommendations)}")
    print("💾 Rapport sauvegardé: /tmp/performance_report.json")

if __name__ == "__main__":
    asyncio.run(main())