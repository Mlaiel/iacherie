#!/usr/bin/env python3
"""
🎯 Accuracy Tracker - Enterprise MLOps Platform
ML Engineer Expertise: Tracker de précision continue avec baseline comparison

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import sqlite3
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccuracyTrend(Enum):
    """Tendances de précision détectées"""
    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

class ModelCategory(Enum):
    """Catégories de modèles créateurs"""
    MUSICIAN_AUDIO = "musician_audio"
    BLOGGER_NLP = "blogger_nlp"
    PHOTOGRAPHER_CV = "photographer_cv"
    INFLUENCER_MULTI = "influencer_multi"
    COMEDIAN_SENTIMENT = "comedian_sentiment"
    GENERAL_ML = "general_ml"

@dataclass
class AccuracyMetrics:
    """Métriques de précision complètes"""
    timestamp: datetime
    model_id: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    baseline_comparison: float
    trend: AccuracyTrend
    confidence_interval: Tuple[float, float]
    sample_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BaselineConfig:
    """Configuration du baseline"""
    baseline_accuracy: float
    baseline_date: datetime
    baseline_version: str
    comparison_method: str = "statistical_test"
    significance_threshold: float = 0.05
    improvement_threshold: float = 0.02

class AccuracyTracker:
    """
    Tracker de précision continue avec baseline comparison enterprise
    
    Fonctionnalités:
    - Tracking temps réel de la précision
    - Comparaison statistique avec baseline
    - Détection de tendances de dégradation
    - Alertes intelligentes basées sur les seuils
    - Support multi-modèles créateurs spécifiques
    """
    
    def __init__(self, 
                 db_path: str = "/tmp/accuracy_tracker.db",
                 retention_days: int = 90):
        self.db_path = db_path
        self.retention_days = retention_days
        self.baselines: Dict[str, BaselineConfig] = {}
        self.accuracy_history: Dict[str, List[AccuracyMetrics]] = {}
        self.alert_callbacks: List[Callable] = []
        
        # Seuils par catégorie de créateur
        self.creator_thresholds = {
            ModelCategory.MUSICIAN_AUDIO: {
                "min_accuracy": 0.85,
                "degradation_threshold": 0.05,
                "sample_size_min": 100
            },
            ModelCategory.BLOGGER_NLP: {
                "min_accuracy": 0.80,
                "degradation_threshold": 0.03,
                "sample_size_min": 50
            },
            ModelCategory.PHOTOGRAPHER_CV: {
                "min_accuracy": 0.90,
                "degradation_threshold": 0.04,
                "sample_size_min": 200
            },
            ModelCategory.INFLUENCER_MULTI: {
                "min_accuracy": 0.82,
                "degradation_threshold": 0.03,
                "sample_size_min": 150
            },
            ModelCategory.COMEDIAN_SENTIMENT: {
                "min_accuracy": 0.78,
                "degradation_threshold": 0.04,
                "sample_size_min": 75
            }
        }
        
        self._setup_database()
        logger.info("🎯 AccuracyTracker initialized for enterprise MLOps monitoring")
    
    def _setup_database(self):
        """Initialisation de la base de données SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des métriques de précision
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accuracy_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        model_version TEXT NOT NULL,
                        accuracy REAL NOT NULL,
                        precision_score REAL NOT NULL,
                        recall_score REAL NOT NULL,
                        f1_score REAL NOT NULL,
                        baseline_comparison REAL NOT NULL,
                        trend TEXT NOT NULL,
                        confidence_lower REAL NOT NULL,
                        confidence_upper REAL NOT NULL,
                        sample_size INTEGER NOT NULL,
                        metadata TEXT
                    )
                """)
                
                # Table des baselines
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS baselines (
                        model_id TEXT PRIMARY KEY,
                        baseline_accuracy REAL NOT NULL,
                        baseline_date TEXT NOT NULL,
                        baseline_version TEXT NOT NULL,
                        comparison_method TEXT NOT NULL,
                        significance_threshold REAL NOT NULL,
                        improvement_threshold REAL NOT NULL
                    )
                """)
                
                # Index pour performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_timestamp ON accuracy_metrics(model_id, timestamp)")
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    async def set_baseline(self, 
                          model_id: str,
                          baseline_accuracy: float,
                          baseline_version: str,
                          comparison_method: str = "statistical_test",
                          significance_threshold: float = 0.05,
                          improvement_threshold: float = 0.02):
        """Définir le baseline pour un modèle"""
        try:
            baseline_config = BaselineConfig(
                baseline_accuracy=baseline_accuracy,
                baseline_date=datetime.now(),
                baseline_version=baseline_version,
                comparison_method=comparison_method,
                significance_threshold=significance_threshold,
                improvement_threshold=improvement_threshold
            )
            
            self.baselines[model_id] = baseline_config
            
            # Persistance en DB
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO baselines 
                    (model_id, baseline_accuracy, baseline_date, baseline_version,
                     comparison_method, significance_threshold, improvement_threshold)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    model_id, baseline_accuracy, baseline_config.baseline_date.isoformat(),
                    baseline_version, comparison_method, significance_threshold, improvement_threshold
                ))
                conn.commit()
            
            logger.info(f"📊 Baseline set for model {model_id}: {baseline_accuracy:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting baseline for {model_id}: {e}")
            return False
    
    async def track_accuracy(self,
                           model_id: str,
                           model_version: str,
                           y_true: np.ndarray,
                           y_pred: np.ndarray,
                           model_category: ModelCategory = ModelCategory.GENERAL_ML,
                           metadata: Optional[Dict[str, Any]] = None) -> AccuracyMetrics:
        """Tracker la précision d'un modèle avec comparaison baseline"""
        try:
            # Calcul des métriques de base
            accuracy = accuracy_score(y_true, y_pred)
            
            # Métriques additionnelles selon le type de problème
            if len(np.unique(y_true)) == 2:  # Classification binaire
                precision = precision_score(y_true, y_pred, average='binary')
                recall = recall_score(y_true, y_pred, average='binary')
                f1 = f1_score(y_true, y_pred, average='binary')
            else:  # Multi-classe ou régression
                if np.issubdtype(y_true.dtype, np.number) and len(np.unique(y_true)) > 10:
                    # Régression
                    precision = 1 - mean_absolute_error(y_true, y_pred) / np.std(y_true)
                    recall = r2_score(y_true, y_pred)
                    f1 = precision  # Placeholder pour régression
                else:
                    # Multi-classe
                    precision = precision_score(y_true, y_pred, average='weighted')
                    recall = recall_score(y_true, y_pred, average='weighted')
                    f1 = f1_score(y_true, y_pred, average='weighted')
            
            # Intervalle de confiance
            n = len(y_true)
            se = np.sqrt(accuracy * (1 - accuracy) / n)
            z_score = stats.norm.ppf(0.975)  # 95% confidence
            ci_lower = max(0, accuracy - z_score * se)
            ci_upper = min(1, accuracy + z_score * se)
            
            # Comparaison avec baseline
            baseline_comparison = 0.0
            if model_id in self.baselines:
                baseline = self.baselines[model_id]
                baseline_comparison = accuracy - baseline.baseline_accuracy
            
            # Détection de tendance
            trend = await self._detect_trend(model_id, accuracy)
            
            # Création de la métrique
            accuracy_metric = AccuracyMetrics(
                timestamp=datetime.now(),
                model_id=model_id,
                model_version=model_version,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                baseline_comparison=baseline_comparison,
                trend=trend,
                confidence_interval=(ci_lower, ci_upper),
                sample_size=n,
                metadata=metadata or {}
            )
            
            # Stockage en mémoire
            if model_id not in self.accuracy_history:
                self.accuracy_history[model_id] = []
            self.accuracy_history[model_id].append(accuracy_metric)
            
            # Persistance en DB
            await self._save_accuracy_metric(accuracy_metric)
            
            # Vérification des alertes
            await self._check_alerts(accuracy_metric, model_category)
            
            logger.info(f"📈 Accuracy tracked for {model_id}: {accuracy:.4f} (trend: {trend.value})")
            return accuracy_metric
            
        except Exception as e:
            logger.error(f"❌ Error tracking accuracy for {model_id}: {e}")
            raise
    
    async def _detect_trend(self, model_id: str, current_accuracy: float) -> AccuracyTrend:
        """Détection de tendance dans l'historique de précision"""
        try:
            if model_id not in self.accuracy_history or len(self.accuracy_history[model_id]) < 5:
                return AccuracyTrend.UNKNOWN
            
            history = self.accuracy_history[model_id]
            recent_accuracies = [m.accuracy for m in history[-10:]]  # 10 dernières mesures
            
            # Test de tendance avec régression linéaire
            x = np.arange(len(recent_accuracies))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, recent_accuracies)
            
            # Calcul de la volatilité
            volatility = np.std(recent_accuracies)
            
            if volatility > 0.05:  # Haute volatilité
                return AccuracyTrend.VOLATILE
            elif abs(slope) < 0.001:  # Pente négligeable
                return AccuracyTrend.STABLE
            elif slope > 0.001 and p_value < 0.05:  # Amélioration significative
                return AccuracyTrend.IMPROVING
            elif slope < -0.001 and p_value < 0.05:  # Dégradation significative
                return AccuracyTrend.DEGRADING
            else:
                return AccuracyTrend.STABLE
                
        except Exception as e:
            logger.error(f"❌ Error detecting trend for {model_id}: {e}")
            return AccuracyTrend.UNKNOWN
    
    async def _save_accuracy_metric(self, metric: AccuracyMetrics):
        """Sauvegarde d'une métrique en base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO accuracy_metrics 
                    (timestamp, model_id, model_version, accuracy, precision_score, 
                     recall_score, f1_score, baseline_comparison, trend,
                     confidence_lower, confidence_upper, sample_size, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.timestamp.isoformat(),
                    metric.model_id,
                    metric.model_version,
                    metric.accuracy,
                    metric.precision,
                    metric.recall,
                    metric.f1_score,
                    metric.baseline_comparison,
                    metric.trend.value,
                    metric.confidence_interval[0],
                    metric.confidence_interval[1],
                    metric.sample_size,
                    json.dumps(metric.metadata)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving accuracy metric: {e}")
    
    async def _check_alerts(self, metric: AccuracyMetrics, model_category: ModelCategory):
        """Vérification et déclenchement d'alertes"""
        try:
            thresholds = self.creator_thresholds.get(model_category, self.creator_thresholds[ModelCategory.GENERAL_ML])
            
            alerts = []
            
            # Alerte précision minimale
            if metric.accuracy < thresholds["min_accuracy"]:
                alerts.append({
                    "type": "low_accuracy",
                    "severity": "high",
                    "message": f"Accuracy below threshold: {metric.accuracy:.4f} < {thresholds['min_accuracy']}"
                })
            
            # Alerte dégradation vs baseline
            if metric.baseline_comparison < -thresholds["degradation_threshold"]:
                alerts.append({
                    "type": "baseline_degradation",
                    "severity": "critical",
                    "message": f"Significant degradation from baseline: {metric.baseline_comparison:.4f}"
                })
            
            # Alerte tendance négative
            if metric.trend == AccuracyTrend.DEGRADING:
                alerts.append({
                    "type": "degrading_trend",
                    "severity": "medium",
                    "message": f"Model showing degrading accuracy trend"
                })
            
            # Alerte taille d'échantillon insuffisante
            if metric.sample_size < thresholds["sample_size_min"]:
                alerts.append({
                    "type": "insufficient_sample",
                    "severity": "low",
                    "message": f"Sample size too small: {metric.sample_size} < {thresholds['sample_size_min']}"
                })
            
            # Déclenchement des callbacks d'alerte
            for alert in alerts:
                alert_data = {
                    "model_id": metric.model_id,
                    "timestamp": metric.timestamp,
                    "alert": alert,
                    "metric": metric
                }
                
                for callback in self.alert_callbacks:
                    try:
                        await callback(alert_data)
                    except Exception as e:
                        logger.error(f"❌ Alert callback error: {e}")
            
            if alerts:
                logger.warning(f"🚨 {len(alerts)} alerts triggered for model {metric.model_id}")
                
        except Exception as e:
            logger.error(f"❌ Error checking alerts: {e}")
    
    async def get_accuracy_report(self, 
                                model_id: str,
                                days_back: int = 7) -> Dict[str, Any]:
        """Générer un rapport de précision pour un modèle"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM accuracy_metrics 
                    WHERE model_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (model_id, start_date.isoformat()))
                
                rows = cursor.fetchall()
                
                if not rows:
                    return {"error": "No data found for the specified period"}
                
                # Conversion en DataFrame pour analyse
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Statistiques de base
                stats_report = {
                    "model_id": model_id,
                    "period": f"{days_back} days",
                    "total_measurements": len(df),
                    "avg_accuracy": float(df['accuracy'].mean()),
                    "min_accuracy": float(df['accuracy'].min()),
                    "max_accuracy": float(df['accuracy'].max()),
                    "std_accuracy": float(df['accuracy'].std()),
                    "latest_accuracy": float(df.iloc[0]['accuracy']),
                    "trend_distribution": df['trend'].value_counts().to_dict(),
                    "avg_baseline_comparison": float(df['baseline_comparison'].mean()),
                    "improvement_rate": float((df['baseline_comparison'] > 0).mean()),
                    "total_samples_processed": int(df['sample_size'].sum())
                }
                
                # Analyse de tendance récente
                recent_df = df.head(10)  # 10 dernières mesures
                if len(recent_df) >= 5:
                    x = np.arange(len(recent_df))
                    slope, _, r_value, p_value, _ = stats.linregress(x, recent_df['accuracy'])
                    stats_report["recent_trend"] = {
                        "slope": float(slope),
                        "r_squared": float(r_value ** 2),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05
                    }
                
                return stats_report
                
        except Exception as e:
            logger.error(f"❌ Error generating accuracy report for {model_id}: {e}")
            return {"error": str(e)}
    
    async def compare_models(self, model_ids: List[str], days_back: int = 7) -> Dict[str, Any]:
        """Comparaison de précision entre plusieurs modèles"""
        try:
            comparison_data = {}
            
            for model_id in model_ids:
                report = await self.get_accuracy_report(model_id, days_back)
                if "error" not in report:
                    comparison_data[model_id] = {
                        "avg_accuracy": report["avg_accuracy"],
                        "latest_accuracy": report["latest_accuracy"],
                        "std_accuracy": report["std_accuracy"],
                        "improvement_rate": report["improvement_rate"]
                    }
            
            if not comparison_data:
                return {"error": "No valid data found for any model"}
            
            # Ranking des modèles
            ranked_by_avg = sorted(comparison_data.items(), 
                                 key=lambda x: x[1]["avg_accuracy"], 
                                 reverse=True)
            
            ranked_by_latest = sorted(comparison_data.items(), 
                                    key=lambda x: x[1]["latest_accuracy"], 
                                    reverse=True)
            
            return {
                "comparison_period": f"{days_back} days",
                "models_compared": len(comparison_data),
                "rankings": {
                    "by_average_accuracy": ranked_by_avg,
                    "by_latest_accuracy": ranked_by_latest
                },
                "best_performer": ranked_by_avg[0][0] if ranked_by_avg else None,
                "most_stable": min(comparison_data.items(), 
                                 key=lambda x: x[1]["std_accuracy"])[0] if comparison_data else None,
                "detailed_comparison": comparison_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error comparing models: {e}")
            return {"error": str(e)}
    
    def add_alert_callback(self, callback: Callable):
        """Ajouter un callback pour les alertes"""
        self.alert_callbacks.append(callback)
        logger.info(f"📢 Alert callback added. Total callbacks: {len(self.alert_callbacks)}")
    
    async def cleanup_old_data(self):
        """Nettoyage des données anciennes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM accuracy_metrics 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"🧹 Cleaned up {deleted_count} old accuracy records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0


# Exemple d'utilisation pour démonstration
async def main():
    """Démonstration des capacités de l'AccuracyTracker"""
    tracker = AccuracyTracker()
    
    # Configuration d'un baseline pour un modèle musicien
    await tracker.set_baseline(
        model_id="musician_genre_classifier",
        baseline_accuracy=0.89,
        baseline_version="v1.0.0"
    )
    
    # Simulation de données de test
    np.random.seed(42)
    y_true = np.random.choice([0, 1], size=1000, p=[0.6, 0.4])
    y_pred = y_true.copy()
    # Introduction d'erreurs pour simulation
    error_indices = np.random.choice(len(y_pred), size=int(0.12 * len(y_pred)), replace=False)
    y_pred[error_indices] = 1 - y_pred[error_indices]
    
    # Tracking de la précision
    metric = await tracker.track_accuracy(
        model_id="musician_genre_classifier",
        model_version="v1.1.0",
        y_true=y_true,
        y_pred=y_pred,
        model_category=ModelCategory.MUSICIAN_AUDIO,
        metadata={"creator_type": "musician", "genre": "rock"}
    )
    
    print(f"📊 Accuracy tracked: {metric.accuracy:.4f}")
    print(f"📈 Baseline comparison: {metric.baseline_comparison:.4f}")
    print(f"📉 Trend: {metric.trend.value}")
    
    # Génération d'un rapport
    report = await tracker.get_accuracy_report("musician_genre_classifier")
    print(f"📋 Report: {json.dumps(report, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())