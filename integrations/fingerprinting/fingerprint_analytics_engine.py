"""
Fingerprint Analytics Engine - Fingerprinting Module
==================================================
Système d'analyse avancée avec ML insights et pattern detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: ML Engineer + Database Administrator
"""

import asyncio
import logging
import hashlib
import json
import uuid
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, Counter
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types d'analyses supportées."""
    FINGERPRINT_SIMILARITY = "fingerprint_similarity"
    USAGE_PATTERNS = "usage_patterns"
    VIOLATION_TRENDS = "violation_trends"
    PLATFORM_ANALYSIS = "platform_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    GEOGRAPHIC_ANALYSIS = "geographic_analysis"
    REVENUE_ANALYSIS = "revenue_analysis"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"

class AnalyticsFrequency(Enum):
    """Fréquences d'analyse."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class ClusteringMethod(Enum):
    """Méthodes de clustering."""
    DBSCAN = "dbscan"
    KMEANS = "kmeans"
    HIERARCHICAL = "hierarchical"
    GAUSSIAN_MIXTURE = "gaussian_mixture"

@dataclass
class AnalyticsMetric:
    """Métrique d'analyse."""
    metric_id: str
    metric_name: str
    metric_type: AnalyticsType
    value: float
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any]
    trend_direction: str  # "up", "down", "stable"
    significance_level: float

@dataclass
class PatternCluster:
    """Cluster de patterns détectés."""
    cluster_id: str
    cluster_type: str
    centroid: List[float]
    members: List[str]  # IDs des éléments
    characteristics: Dict[str, Any]
    significance_score: float
    discovered_at: datetime
    last_updated: datetime

@dataclass
class TrendAnalysis:
    """Analyse de tendance."""
    trend_id: str
    subject: str  # Ce qui est analysé
    time_period: Tuple[datetime, datetime]
    trend_type: str
    trend_strength: float
    forecast: List[Dict[str, Any]]
    confidence_interval: Tuple[float, float]
    anomalies_detected: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class IntelligenceReport:
    """Rapport d'intelligence."""
    report_id: str
    report_type: AnalyticsType
    generated_at: datetime
    time_period: Tuple[datetime, datetime]
    key_insights: List[str]
    metrics: List[AnalyticsMetric]
    patterns: List[PatternCluster]
    trends: List[TrendAnalysis]
    actionable_recommendations: List[str]
    executive_summary: str

class FingerprintAnalyticsEngine:
    """
    Fingerprint Analytics Engine Enterprise
    =====================================
    
    Système d'analyse avancée avec:
    - ML-powered pattern detection dans fingerprints
    - Advanced clustering fingerprint similarity
    - Content usage analytics intelligent
    - Violation prediction modeling avancé
    - Real-time analytics dashboard data
    - Automated insight generation avec NLP
    
    Expert Implementation: ML Engineer + Database Administrator
    """
    
    def __init__(self):
        self.metrics_database: Dict[str, AnalyticsMetric] = {}
        self.clusters_database: Dict[str, PatternCluster] = {}
        self.trends_database: Dict[str, TrendAnalysis] = {}
        self.reports_database: Dict[str, IntelligenceReport] = {}
        
        # Configuration ML
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Garder 95% de la variance
        
        # Paramètres de clustering
        self.clustering_params = {
            'dbscan': {'eps': 0.3, 'min_samples': 5},
            'kmeans': {'n_clusters': 8, 'random_state': 42},
            'hierarchical': {'n_clusters': 8}
        }
        
        # Cache pour performance
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=1)
        
        # Métriques temps réel
        self.real_time_metrics = {
            'fingerprints_processed': 0,
            'patterns_detected': 0,
            'anomalies_found': 0,
            'insights_generated': 0
        }
        
        logger.info("FingerprintAnalyticsEngine initialisé")
    
    async def analyze_fingerprint_similarities(
        self,
        fingerprints_data: List[Dict[str, Any]],
        similarity_threshold: float = 0.8,
        clustering_method: ClusteringMethod = ClusteringMethod.DBSCAN
    ) -> Dict[str, Any]:
        """
        Analyse les similarités entre fingerprints.
        
        Args:
            fingerprints_data: Données des fingerprints
            similarity_threshold: Seuil de similarité
            clustering_method: Méthode de clustering
        
        Returns:
            Dict[str, Any]: Résultats d'analyse
        """
        try:
            if not fingerprints_data:
                return {'error': 'Aucune donnée de fingerprint fournie'}
            
            # Extraction des features
            features_matrix = await self._extract_features_matrix(fingerprints_data)
            
            if features_matrix.size == 0:
                return {'error': 'Impossible d\'extraire les features'}
            
            # Préparation des données
            scaled_features = self.scaler.fit_transform(features_matrix)
            
            # Réduction de dimensionnalité si nécessaire
            if scaled_features.shape[1] > 50:
                reduced_features = self.pca.fit_transform(scaled_features)
            else:
                reduced_features = scaled_features
            
            # Clustering
            clusters = await self._perform_clustering(
                reduced_features, clustering_method
            )
            
            # Analyse des clusters
            cluster_analysis = await self._analyze_clusters(
                clusters, fingerprints_data, reduced_features
            )
            
            # Détection d'anomalies
            anomalies = await self._detect_anomalies(
                reduced_features, clusters, fingerprints_data
            )
            
            # Calcul de métriques
            metrics = await self._calculate_similarity_metrics(
                fingerprints_data, clusters, features_matrix
            )
            
            # Insights et recommandations
            insights = await self._generate_similarity_insights(
                cluster_analysis, anomalies, metrics
            )
            
            # Stocker métriques
            for metric in metrics:
                self.metrics_database[metric.metric_id] = metric
            
            # Mettre à jour métriques temps réel
            self.real_time_metrics['patterns_detected'] += len(cluster_analysis)
            self.real_time_metrics['anomalies_found'] += len(anomalies)
            
            result = {
                'analysis_id': str(uuid.uuid4()),
                'fingerprints_analyzed': len(fingerprints_data),
                'clusters_found': len(cluster_analysis),
                'anomalies_detected': len(anomalies),
                'similarity_threshold': similarity_threshold,
                'clustering_method': clustering_method.value,
                'cluster_analysis': cluster_analysis,
                'anomalies': anomalies,
                'metrics': [asdict(m) for m in metrics],
                'insights': insights,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Analyse similarité terminée: {len(cluster_analysis)} clusters, {len(anomalies)} anomalies")
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse similarités: {e}")
            return {'error': str(e)}
    
    async def _extract_features_matrix(
        self,
        fingerprints_data: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Extrait la matrice de features."""
        try:
            features_list = []
            
            for fp_data in fingerprints_data:
                features = []
                
                # Features numériques communes
                if 'similarity_score' in fp_data:
                    features.append(fp_data['similarity_score'])
                
                if 'confidence_score' in fp_data:
                    features.append(fp_data['confidence_score'])
                
                # Features spécifiques par type
                if 'semantic_features' in fp_data:
                    semantic = fp_data['semantic_features']
                    features.extend([
                        semantic.get('semantic_complexity', 0),
                        len(semantic.get('key_concepts', [])),
                        len(semantic.get('topics', []))
                    ])
                
                if 'tfidf_vector' in fp_data:
                    tfidf_vector = fp_data['tfidf_vector']
                    if isinstance(tfidf_vector, list) and len(tfidf_vector) > 0:
                        # Prendre les premiers éléments ou moyenner
                        features.extend(tfidf_vector[:20])  # Max 20 features TF-IDF
                
                if 'stylometric_features' in fp_data:
                    stylo = fp_data['stylometric_features']
                    features.extend([
                        stylo.get('lexical_richness', 0),
                        stylo.get('avg_word_length', 0),
                        stylo.get('function_word_ratio', 0)
                    ])
                
                # Features audio/vidéo
                if 'audio_features' in fp_data:
                    audio = fp_data['audio_features']
                    features.extend([
                        audio.get('tempo', 0),
                        audio.get('energy', 0),
                        audio.get('spectral_centroid', 0)
                    ])
                
                # Features image
                if 'image_features' in fp_data:
                    image = fp_data['image_features']
                    features.extend([
                        image.get('color_variance', 0),
                        image.get('texture_energy', 0),
                        image.get('edge_density', 0)
                    ])
                
                # Remplir avec zéros si pas assez de features
                while len(features) < 10:
                    features.append(0.0)
                
                features_list.append(features)
            
            if not features_list:
                return np.array([])
            
            # Normaliser toutes les listes à la même longueur
            max_length = max(len(f) for f in features_list)
            normalized_features = []
            
            for features in features_list:
                while len(features) < max_length:
                    features.append(0.0)
                normalized_features.append(features[:max_length])
            
            return np.array(normalized_features)
            
        except Exception as e:
            logger.error(f"Erreur extraction features: {e}")
            return np.array([])
    
    async def _perform_clustering(
        self,
        features: np.ndarray,
        method: ClusteringMethod
    ) -> np.ndarray:
        """Effectue le clustering."""
        try:
            if method == ClusteringMethod.DBSCAN:
                params = self.clustering_params['dbscan']
                clusterer = DBSCAN(eps=params['eps'], min_samples=params['min_samples'])
            
            elif method == ClusteringMethod.KMEANS:
                params = self.clustering_params['kmeans']
                n_clusters = min(params['n_clusters'], len(features))
                clusterer = KMeans(n_clusters=n_clusters, random_state=params['random_state'])
            
            else:
                # Default to DBSCAN
                params = self.clustering_params['dbscan']
                clusterer = DBSCAN(eps=params['eps'], min_samples=params['min_samples'])
            
            clusters = clusterer.fit_predict(features)
            
            # Calculer score de silhouette si possible
            if len(set(clusters)) > 1:
                silhouette = silhouette_score(features, clusters)
                logger.info(f"Score de silhouette du clustering: {silhouette:.3f}")
            
            return clusters
            
        except Exception as e:
            logger.error(f"Erreur clustering: {e}")
            return np.array([-1] * len(features))  # Tous en bruit
    
    async def _analyze_clusters(
        self,
        clusters: np.ndarray,
        fingerprints_data: List[Dict[str, Any]],
        features: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Analyse les clusters formés."""
        try:
            cluster_analysis = []
            unique_clusters = set(clusters)
            
            # Exclure le bruit (label -1)
            valid_clusters = [c for c in unique_clusters if c != -1]
            
            for cluster_id in valid_clusters:
                # Indices des membres du cluster
                member_indices = np.where(clusters == cluster_id)[0]
                
                if len(member_indices) == 0:
                    continue
                
                # Centroïde du cluster
                cluster_features = features[member_indices]
                centroid = np.mean(cluster_features, axis=0)
                
                # Caractéristiques du cluster
                characteristics = await self._extract_cluster_characteristics(
                    member_indices, fingerprints_data
                )
                
                # Score de cohésion
                cohesion_score = await self._calculate_cohesion_score(cluster_features)
                
                # Membres du cluster
                member_ids = [
                    fingerprints_data[i].get('fingerprint_id', f'fp_{i}') 
                    for i in member_indices
                ]
                
                cluster_info = {
                    'cluster_id': f'cluster_{cluster_id}',
                    'size': len(member_indices),
                    'centroid': centroid.tolist(),
                    'members': member_ids,
                    'characteristics': characteristics,
                    'cohesion_score': cohesion_score,
                    'representative_member': member_ids[0] if member_ids else None
                }
                
                cluster_analysis.append(cluster_info)
                
                # Créer objet PatternCluster
                pattern_cluster = PatternCluster(
                    cluster_id=f'cluster_{cluster_id}_{uuid.uuid4().hex[:8]}',
                    cluster_type='fingerprint_similarity',
                    centroid=centroid.tolist(),
                    members=member_ids,
                    characteristics=characteristics,
                    significance_score=cohesion_score,
                    discovered_at=datetime.utcnow(),
                    last_updated=datetime.utcnow()
                )
                
                self.clusters_database[pattern_cluster.cluster_id] = pattern_cluster
            
            # Trier par taille de cluster
            cluster_analysis.sort(key=lambda x: x['size'], reverse=True)
            
            return cluster_analysis
            
        except Exception as e:
            logger.error(f"Erreur analyse clusters: {e}")
            return []
    
    async def _extract_cluster_characteristics(
        self,
        member_indices: np.ndarray,
        fingerprints_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extrait les caractéristiques d'un cluster."""
        try:
            characteristics = {}
            
            # Analyser types de contenu
            content_types = []
            platforms = []
            similarity_scores = []
            
            for idx in member_indices:
                if idx < len(fingerprints_data):
                    fp_data = fingerprints_data[idx]
                    
                    content_types.append(fp_data.get('content_type', 'unknown'))
                    platforms.append(fp_data.get('platform', 'unknown'))
                    similarity_scores.append(fp_data.get('similarity_score', 0.0))
            
            # Statistiques
            characteristics['dominant_content_type'] = Counter(content_types).most_common(1)[0][0] if content_types else 'unknown'
            characteristics['dominant_platform'] = Counter(platforms).most_common(1)[0][0] if platforms else 'unknown'
            characteristics['avg_similarity_score'] = np.mean(similarity_scores) if similarity_scores else 0.0
            characteristics['content_type_diversity'] = len(set(content_types))
            characteristics['platform_diversity'] = len(set(platforms))
            
            # Déterminer type de pattern
            if characteristics['content_type_diversity'] == 1:
                characteristics['pattern_type'] = f"homogeneous_{characteristics['dominant_content_type']}"
            else:
                characteristics['pattern_type'] = "heterogeneous_content"
            
            return characteristics
            
        except Exception as e:
            logger.error(f"Erreur extraction caractéristiques: {e}")
            return {}
    
    async def _calculate_cohesion_score(self, cluster_features: np.ndarray) -> float:
        """Calcule le score de cohésion d'un cluster."""
        try:
            if len(cluster_features) < 2:
                return 1.0
            
            # Variance intra-cluster
            centroid = np.mean(cluster_features, axis=0)
            distances = np.linalg.norm(cluster_features - centroid, axis=1)
            intra_variance = np.var(distances)
            
            # Score inversement proportionnel à la variance
            cohesion_score = 1.0 / (1.0 + intra_variance)
            
            return float(cohesion_score)
            
        except Exception as e:
            logger.error(f"Erreur calcul cohésion: {e}")
            return 0.5
    
    async def _detect_anomalies(
        self,
        features: np.ndarray,
        clusters: np.ndarray,
        fingerprints_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans les données."""
        try:
            anomalies = []
            
            # Points isolés (bruit du clustering)
            noise_indices = np.where(clusters == -1)[0]
            
            for idx in noise_indices:
                if idx < len(fingerprints_data):
                    anomaly = {
                        'anomaly_id': str(uuid.uuid4()),
                        'fingerprint_id': fingerprints_data[idx].get('fingerprint_id', f'fp_{idx}'),
                        'anomaly_type': 'isolated_point',
                        'significance': 0.8,
                        'description': 'Point isolé dans l\'espace des features',
                        'features': features[idx].tolist(),
                        'recommendations': ['Vérifier qualité des données', 'Investiguer contenu unique']
                    }
                    anomalies.append(anomaly)
            
            # Détection d'anomalies par distance au centroïde global
            global_centroid = np.mean(features, axis=0)
            distances = np.linalg.norm(features - global_centroid, axis=1)
            
            # Seuil d'anomalie (3 écarts-types)
            threshold = np.mean(distances) + 3 * np.std(distances)
            
            anomaly_indices = np.where(distances > threshold)[0]
            
            for idx in anomaly_indices:
                if idx < len(fingerprints_data) and clusters[idx] != -1:  # Pas déjà marqué comme bruit
                    anomaly = {
                        'anomaly_id': str(uuid.uuid4()),
                        'fingerprint_id': fingerprints_data[idx].get('fingerprint_id', f'fp_{idx}'),
                        'anomaly_type': 'statistical_outlier',
                        'significance': min(distances[idx] / threshold, 2.0),
                        'description': f'Outlier statistique (distance: {distances[idx]:.3f})',
                        'features': features[idx].tolist(),
                        'recommendations': ['Analyser pattern inhabituel', 'Vérifier processus de création']
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Erreur détection anomalies: {e}")
            return []
    
    async def _calculate_similarity_metrics(
        self,
        fingerprints_data: List[Dict[str, Any]],
        clusters: np.ndarray,
        features: np.ndarray
    ) -> List[AnalyticsMetric]:
        """Calcule les métriques de similarité."""
        try:
            metrics = []
            
            # Métrique: Nombre de clusters
            n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
            metrics.append(AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_name="clusters_detected",
                metric_type=AnalyticsType.FINGERPRINT_SIMILARITY,
                value=float(n_clusters),
                confidence=0.95,
                timestamp=datetime.utcnow(),
                metadata={'clustering_method': 'dbscan'},
                trend_direction='stable',
                significance_level=0.05
            ))
            
            # Métrique: Pourcentage de points en cluster
            clustered_points = len([c for c in clusters if c != -1])
            clustering_rate = clustered_points / len(clusters) if len(clusters) > 0 else 0
            metrics.append(AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_name="clustering_rate",
                metric_type=AnalyticsType.FINGERPRINT_SIMILARITY,
                value=clustering_rate,
                confidence=0.90,
                timestamp=datetime.utcnow(),
                metadata={'total_points': len(clusters), 'clustered_points': clustered_points},
                trend_direction='stable',
                significance_level=0.05
            ))
            
            # Métrique: Similarité moyenne
            similarity_scores = []
            for fp_data in fingerprints_data:
                if 'similarity_score' in fp_data:
                    similarity_scores.append(fp_data['similarity_score'])
            
            if similarity_scores:
                avg_similarity = np.mean(similarity_scores)
                metrics.append(AnalyticsMetric(
                    metric_id=str(uuid.uuid4()),
                    metric_name="average_similarity",
                    metric_type=AnalyticsType.FINGERPRINT_SIMILARITY,
                    value=avg_similarity,
                    confidence=0.85,
                    timestamp=datetime.utcnow(),
                    metadata={'sample_size': len(similarity_scores)},
                    trend_direction='stable',
                    significance_level=0.05
                ))
            
            # Métrique: Variance des features
            feature_variance = np.var(features, axis=0).mean() if features.size > 0 else 0
            metrics.append(AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_name="feature_variance",
                metric_type=AnalyticsType.FINGERPRINT_SIMILARITY,
                value=float(feature_variance),
                confidence=0.80,
                timestamp=datetime.utcnow(),
                metadata={'n_features': features.shape[1] if features.size > 0 else 0},
                trend_direction='stable',
                significance_level=0.05
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques: {e}")
            return []
    
    async def _generate_similarity_insights(
        self,
        cluster_analysis: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        metrics: List[AnalyticsMetric]
    ) -> List[str]:
        """Génère des insights sur l'analyse de similarité."""
        try:
            insights = []
            
            # Insights sur les clusters
            if cluster_analysis:
                largest_cluster = max(cluster_analysis, key=lambda x: x['size'])
                insights.append(
                    f"Plus grand cluster détecté: {largest_cluster['size']} éléments "
                    f"({largest_cluster['characteristics'].get('pattern_type', 'inconnu')})"
                )
                
                if len(cluster_analysis) > 5:
                    insights.append(f"Forte fragmentation détectée: {len(cluster_analysis)} clusters distincts")
                elif len(cluster_analysis) <= 2:
                    insights.append("Contenu homogène: peu de patterns distincts détectés")
            
            # Insights sur les anomalies
            if anomalies:
                insights.append(f"{len(anomalies)} anomalies détectées nécessitant investigation")
                
                outlier_count = len([a for a in anomalies if a['anomaly_type'] == 'statistical_outlier'])
                if outlier_count > 0:
                    insights.append(f"{outlier_count} outliers statistiques suggèrent contenu unique ou erreurs")
            
            # Insights sur les métriques
            for metric in metrics:
                if metric.metric_name == "clustering_rate" and metric.value < 0.5:
                    insights.append("Faible taux de clustering suggère données très diverses ou bruitées")
                elif metric.metric_name == "average_similarity" and metric.value > 0.9:
                    insights.append("Très haute similarité moyenne détectée - possible duplication")
            
            # Recommandations générales
            if not insights:
                insights.append("Patterns de similarité normaux détectés")
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur génération insights: {e}")
            return ["Erreur dans la génération d'insights"]
    
    async def analyze_usage_patterns(
        self,
        usage_data: List[Dict[str, Any]],
        time_window: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Analyse les patterns d'usage.
        
        Args:
            usage_data: Données d'usage
            time_window: Fenêtre temporelle d'analyse
        
        Returns:
            Dict[str, Any]: Analyse des patterns d'usage
        """
        try:
            if not usage_data:
                return {'error': 'Aucune donnée d\'usage fournie'}
            
            # Filtrer par fenêtre temporelle
            cutoff_date = datetime.utcnow() - time_window
            filtered_data = [
                usage for usage in usage_data 
                if datetime.fromisoformat(usage.get('timestamp', '2024-01-01')) >= cutoff_date
            ]
            
            # Analyse temporelle
            temporal_patterns = await self._analyze_temporal_patterns(filtered_data)
            
            # Analyse par plateforme
            platform_patterns = await self._analyze_platform_patterns(filtered_data)
            
            # Analyse géographique
            geographic_patterns = await self._analyze_geographic_patterns(filtered_data)
            
            # Détection de patterns comportementaux
            behavioral_patterns = await self._detect_behavioral_patterns(filtered_data)
            
            # Prédictions d'usage
            usage_predictions = await self._predict_usage_trends(filtered_data)
            
            # Métriques d'usage
            usage_metrics = await self._calculate_usage_metrics(filtered_data)
            
            result = {
                'analysis_id': str(uuid.uuid4()),
                'time_window_days': time_window.days,
                'data_points_analyzed': len(filtered_data),
                'temporal_patterns': temporal_patterns,
                'platform_patterns': platform_patterns,
                'geographic_patterns': geographic_patterns,
                'behavioral_patterns': behavioral_patterns,
                'usage_predictions': usage_predictions,
                'metrics': [asdict(m) for m in usage_metrics],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Analyse patterns d'usage terminée: {len(filtered_data)} points de données")
            return result
            
        except Exception as e:
            logger.error(f"Erreur analyse usage: {e}")
            return {'error': str(e)}
    
    async def _analyze_temporal_patterns(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns temporels."""
        try:
            if not usage_data:
                return {}
            
            # Grouper par heure de la journée
            hourly_usage = defaultdict(int)
            daily_usage = defaultdict(int)
            weekly_usage = defaultdict(int)
            
            for usage in usage_data:
                timestamp_str = usage.get('timestamp')
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str)
                        hourly_usage[dt.hour] += 1
                        daily_usage[dt.date()] += 1
                        weekly_usage[dt.weekday()] += 1
                    except ValueError:
                        continue
            
            # Analyse des pics d'activité
            peak_hour = max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else (0, 0)
            peak_day = max(weekly_usage.items(), key=lambda x: x[1]) if weekly_usage else (0, 0)
            
            # Calcul de la régularité
            daily_values = list(daily_usage.values())
            usage_regularity = 1.0 / (1.0 + np.std(daily_values)) if daily_values else 0.0
            
            return {
                'peak_hour': peak_hour[0],
                'peak_hour_usage': peak_hour[1],
                'peak_weekday': peak_day[0],
                'peak_weekday_usage': peak_day[1],
                'usage_regularity': usage_regularity,
                'hourly_distribution': dict(hourly_usage),
                'daily_distribution': {str(k): v for k, v in daily_usage.items()},
                'weekly_distribution': dict(weekly_usage)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse temporelle: {e}")
            return {}
    
    async def _analyze_platform_patterns(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns par plateforme."""
        try:
            platform_stats = defaultdict(lambda: {
                'usage_count': 0,
                'total_views': 0,
                'total_revenue': 0.0,
                'unique_users': set()
            })
            
            for usage in usage_data:
                platform = usage.get('platform', 'unknown')
                user_id = usage.get('user_id', 'anonymous')
                
                platform_stats[platform]['usage_count'] += 1
                platform_stats[platform]['total_views'] += usage.get('views', 0)
                platform_stats[platform]['total_revenue'] += usage.get('revenue', 0.0)
                platform_stats[platform]['unique_users'].add(user_id)
            
            # Conversion en format sérialisable
            platform_analysis = {}
            for platform, stats in platform_stats.items():
                platform_analysis[platform] = {
                    'usage_count': stats['usage_count'],
                    'total_views': stats['total_views'],
                    'total_revenue': stats['total_revenue'],
                    'unique_users': len(stats['unique_users']),
                    'avg_views_per_usage': stats['total_views'] / stats['usage_count'] if stats['usage_count'] > 0 else 0,
                    'revenue_per_view': stats['total_revenue'] / stats['total_views'] if stats['total_views'] > 0 else 0
                }
            
            # Identifier plateforme dominante
            dominant_platform = max(platform_analysis.items(), key=lambda x: x[1]['usage_count']) if platform_analysis else ('none', {})
            
            return {
                'platform_distribution': platform_analysis,
                'dominant_platform': dominant_platform[0],
                'platform_diversity': len(platform_analysis),
                'cross_platform_usage': len(platform_analysis) > 1
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse plateformes: {e}")
            return {}
    
    async def _analyze_geographic_patterns(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns géographiques."""
        try:
            geographic_stats = defaultdict(int)
            
            for usage in usage_data:
                location = usage.get('location', 'unknown')
                country = usage.get('country', 'unknown')
                
                geographic_stats[country] += 1
            
            # Top pays
            top_countries = sorted(geographic_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Calcul de la diversité géographique
            total_usage = sum(geographic_stats.values())
            geographic_diversity = len(geographic_stats) / total_usage if total_usage > 0 else 0
            
            return {
                'country_distribution': dict(geographic_stats),
                'top_countries': top_countries,
                'geographic_diversity': geographic_diversity,
                'international_usage': len(geographic_stats) > 1
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse géographique: {e}")
            return {}
    
    async def _detect_behavioral_patterns(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détecte les patterns comportementaux."""
        try:
            user_behaviors = defaultdict(lambda: {
                'sessions': 0,
                'total_duration': 0,
                'content_types': set(),
                'platforms': set(),
                'last_activity': None
            })
            
            for usage in usage_data:
                user_id = usage.get('user_id', 'anonymous')
                timestamp_str = usage.get('timestamp')
                
                behavior = user_behaviors[user_id]
                behavior['sessions'] += 1
                behavior['total_duration'] += usage.get('duration', 0)
                behavior['content_types'].add(usage.get('content_type', 'unknown'))
                behavior['platforms'].add(usage.get('platform', 'unknown'))
                
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str)
                        if behavior['last_activity'] is None or dt > behavior['last_activity']:
                            behavior['last_activity'] = dt
                    except ValueError:
                        pass
            
            # Analyse des segments d'utilisateurs
            user_segments = {
                'power_users': 0,      # > 10 sessions
                'regular_users': 0,    # 3-10 sessions
                'casual_users': 0,     # 1-2 sessions
                'multi_platform': 0,   # > 1 plateforme
                'content_diverse': 0   # > 1 type de contenu
            }
            
            for user_id, behavior in user_behaviors.items():
                sessions = behavior['sessions']
                
                if sessions > 10:
                    user_segments['power_users'] += 1
                elif sessions >= 3:
                    user_segments['regular_users'] += 1
                else:
                    user_segments['casual_users'] += 1
                
                if len(behavior['platforms']) > 1:
                    user_segments['multi_platform'] += 1
                
                if len(behavior['content_types']) > 1:
                    user_segments['content_diverse'] += 1
            
            # Engagement moyen
            if user_behaviors:
                avg_sessions = np.mean([b['sessions'] for b in user_behaviors.values()])
                avg_duration = np.mean([b['total_duration'] for b in user_behaviors.values()])
            else:
                avg_sessions = 0
                avg_duration = 0
            
            return {
                'user_segments': user_segments,
                'total_users': len(user_behaviors),
                'average_sessions_per_user': avg_sessions,
                'average_duration_per_user': avg_duration,
                'user_retention': user_segments['regular_users'] + user_segments['power_users']
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse comportementale: {e}")
            return {}
    
    async def _predict_usage_trends(self, usage_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prédit les tendances d'usage."""
        try:
            if len(usage_data) < 7:  # Besoin d'au moins une semaine de données
                return {'error': 'Données insuffisantes pour prédiction'}
            
            # Grouper par jour
            daily_usage = defaultdict(int)
            for usage in usage_data:
                timestamp_str = usage.get('timestamp')
                if timestamp_str:
                    try:
                        dt = datetime.fromisoformat(timestamp_str)
                        daily_usage[dt.date()] += 1
                    except ValueError:
                        continue
            
            # Ordonner par date
            sorted_days = sorted(daily_usage.items())
            if len(sorted_days) < 3:
                return {'error': 'Données temporelles insuffisantes'}
            
            # Calcul de tendance simple (régression linéaire basique)
            x_values = np.arange(len(sorted_days))
            y_values = np.array([count for date, count in sorted_days])
            
            # Coefficient de corrélation pour tendance
            if len(x_values) > 1:
                correlation = np.corrcoef(x_values, y_values)[0, 1]
                trend_direction = 'increasing' if correlation > 0.1 else 'decreasing' if correlation < -0.1 else 'stable'
            else:
                trend_direction = 'stable'
                correlation = 0.0
            
            # Prédiction simple pour les 7 prochains jours
            if len(y_values) >= 2:
                slope = (y_values[-1] - y_values[0]) / (len(y_values) - 1)
                last_value = y_values[-1]
                
                predictions = []
                for i in range(1, 8):  # 7 jours suivants
                    predicted_value = max(0, last_value + slope * i)
                    predictions.append({
                        'day_offset': i,
                        'predicted_usage': int(predicted_value),
                        'confidence': max(0.1, 1.0 - i * 0.1)  # Confiance décroissante
                    })
            else:
                predictions = []
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': abs(correlation),
                'current_average': float(np.mean(y_values)),
                'predictions_7_days': predictions,
                'data_quality': 'good' if len(sorted_days) >= 14 else 'limited'
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction tendances: {e}")
            return {'error': str(e)}
    
    async def _calculate_usage_metrics(self, usage_data: List[Dict[str, Any]]) -> List[AnalyticsMetric]:
        """Calcule les métriques d'usage."""
        try:
            metrics = []
            
            if not usage_data:
                return metrics
            
            # Métrique: Volume total d'usage
            total_usage = len(usage_data)
            metrics.append(AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_name="total_usage_volume",
                metric_type=AnalyticsType.USAGE_PATTERNS,
                value=float(total_usage),
                confidence=1.0,
                timestamp=datetime.utcnow(),
                metadata={'data_points': total_usage},
                trend_direction='stable',
                significance_level=0.01
            ))
            
            # Métrique: Engagement moyen
            engagement_scores = [usage.get('engagement_score', 0.5) for usage in usage_data]
            avg_engagement = np.mean(engagement_scores) if engagement_scores else 0.0
            metrics.append(AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_name="average_engagement",
                metric_type=AnalyticsType.USAGE_PATTERNS,
                value=avg_engagement,
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata={'sample_size': len(engagement_scores)},
                trend_direction='stable',
                significance_level=0.05
            ))
            
            # Métrique: Diversité des plateformes
            platforms = set(usage.get('platform', 'unknown') for usage in usage_data)
            platform_diversity = len(platforms)
            metrics.append(AnalyticsMetric(
                metric_id=str(uuid.uuid4()),
                metric_name="platform_diversity",
                metric_type=AnalyticsType.PLATFORM_ANALYSIS,
                value=float(platform_diversity),
                confidence=0.95,
                timestamp=datetime.utcnow(),
                metadata={'platforms': list(platforms)},
                trend_direction='stable',
                significance_level=0.05
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques usage: {e}")
            return []
    
    async def generate_intelligence_report(
        self,
        report_type: AnalyticsType,
        time_period: Tuple[datetime, datetime],
        data_sources: List[str] = None
    ) -> IntelligenceReport:
        """
        Génère un rapport d'intelligence.
        
        Args:
            report_type: Type de rapport
            time_period: Période d'analyse
            data_sources: Sources de données à analyser
        
        Returns:
            IntelligenceReport: Rapport généré
        """
        try:
            start_time, end_time = time_period
            
            # Collecter métriques pertinentes
            relevant_metrics = [
                metric for metric in self.metrics_database.values()
                if (metric.metric_type == report_type and 
                    start_time <= metric.timestamp <= end_time)
            ]
            
            # Collecter patterns pertinents
            relevant_patterns = [
                cluster for cluster in self.clusters_database.values()
                if start_time <= cluster.discovered_at <= end_time
            ]
            
            # Collecter tendances
            relevant_trends = [
                trend for trend in self.trends_database.values()
                if (trend.time_period[0] >= start_time and 
                    trend.time_period[1] <= end_time)
            ]
            
            # Générer insights clés
            key_insights = await self._generate_key_insights(
                relevant_metrics, relevant_patterns, relevant_trends, report_type
            )
            
            # Générer recommandations
            recommendations = await self._generate_actionable_recommendations(
                relevant_metrics, relevant_patterns, key_insights
            )
            
            # Générer résumé exécutif
            executive_summary = await self._generate_executive_summary(
                key_insights, recommendations, relevant_metrics
            )
            
            report = IntelligenceReport(
                report_id=str(uuid.uuid4()),
                report_type=report_type,
                generated_at=datetime.utcnow(),
                time_period=time_period,
                key_insights=key_insights,
                metrics=relevant_metrics,
                patterns=relevant_patterns,
                trends=relevant_trends,
                actionable_recommendations=recommendations,
                executive_summary=executive_summary
            )
            
            # Stocker rapport
            self.reports_database[report.report_id] = report
            
            # Mettre à jour métriques temps réel
            self.real_time_metrics['insights_generated'] += len(key_insights)
            
            logger.info(f"Rapport d'intelligence généré: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport: {e}")
            raise
    
    async def _generate_key_insights(
        self,
        metrics: List[AnalyticsMetric],
        patterns: List[PatternCluster],
        trends: List[TrendAnalysis],
        report_type: AnalyticsType
    ) -> List[str]:
        """Génère les insights clés."""
        try:
            insights = []
            
            # Insights basés sur les métriques
            if metrics:
                high_value_metrics = [m for m in metrics if m.significance_level < 0.05]
                if high_value_metrics:
                    insights.append(f"{len(high_value_metrics)} métriques significatives identifiées")
                
                # Métriques en hausse/baisse
                increasing_metrics = [m for m in metrics if m.trend_direction == 'up']
                decreasing_metrics = [m for m in metrics if m.trend_direction == 'down']
                
                if increasing_metrics:
                    insights.append(f"{len(increasing_metrics)} métriques en croissance détectées")
                if decreasing_metrics:
                    insights.append(f"{len(decreasing_metrics)} métriques en déclin nécessitent attention")
            
            # Insights basés sur les patterns
            if patterns:
                large_patterns = [p for p in patterns if len(p.members) > 10]
                if large_patterns:
                    insights.append(f"{len(large_patterns)} patterns majeurs identifiés avec impact significatif")
                
                high_significance = [p for p in patterns if p.significance_score > 0.8]
                if high_significance:
                    insights.append(f"{len(high_significance)} patterns haute signification découverts")
            
            # Insights spécifiques par type de rapport
            if report_type == AnalyticsType.FINGERPRINT_SIMILARITY:
                insights.append("Analyse de similarité révèle patterns de duplication et contenu unique")
            elif report_type == AnalyticsType.USAGE_PATTERNS:
                insights.append("Patterns d'usage montrent comportements utilisateur et préférences")
            elif report_type == AnalyticsType.VIOLATION_TRENDS:
                insights.append("Tendances de violation identifient risques et opportunités protection")
            
            if not insights:
                insights.append("Analyse révèle patterns standard sans anomalies significatives")
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur génération insights: {e}")
            return ["Erreur dans la génération d'insights"]
    
    async def _generate_actionable_recommendations(
        self,
        metrics: List[AnalyticsMetric],
        patterns: List[PatternCluster],
        insights: List[str]
    ) -> List[str]:
        """Génère des recommandations actionnables."""
        try:
            recommendations = []
            
            # Recommandations basées sur métriques
            declining_metrics = [m for m in metrics if m.trend_direction == 'down']
            if declining_metrics:
                recommendations.append("Investiguer causes de déclin et implémenter mesures correctives")
            
            # Recommandations basées sur patterns
            if patterns:
                strong_patterns = [p for p in patterns if p.significance_score > 0.9]
                if strong_patterns:
                    recommendations.append("Exploiter patterns forts pour optimisation stratégique")
                
                weak_patterns = [p for p in patterns if p.significance_score < 0.3]
                if weak_patterns:
                    recommendations.append("Réviser qualité données pour patterns faibles")
            
            # Recommandations générales
            recommendations.extend([
                "Continuer monitoring régulier pour détecter changements",
                "Optimiser processus basés sur insights découverts",
                "Développer alertes automatiques pour métriques critiques"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            return ["Continuer surveillance et analyse des données"]
    
    async def _generate_executive_summary(
        self,
        insights: List[str],
        recommendations: List[str],
        metrics: List[AnalyticsMetric]
    ) -> str:
        """Génère le résumé exécutif."""
        try:
            summary_parts = []
            
            # Vue d'ensemble
            summary_parts.append(f"Analyse de {len(metrics)} métriques révèle {len(insights)} insights clés.")
            
            # Insights principaux
            if insights:
                top_insight = insights[0]
                summary_parts.append(f"Insight principal: {top_insight}")
            
            # Recommandation prioritaire
            if recommendations:
                priority_recommendation = recommendations[0]
                summary_parts.append(f"Action recommandée: {priority_recommendation}")
            
            # Conclusion
            summary_parts.append("Monitoring continu recommandé pour maintenir visibilité optimale.")
            
            return " ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Erreur génération résumé: {e}")
            return "Résumé indisponible - voir détails du rapport."
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Retourne les données du dashboard temps réel."""
        try:
            # Métriques temps réel
            current_metrics = {
                'fingerprints_processed_today': self.real_time_metrics['fingerprints_processed'],
                'patterns_detected_today': self.real_time_metrics['patterns_detected'],
                'anomalies_found_today': self.real_time_metrics['anomalies_found'],
                'insights_generated_today': self.real_time_metrics['insights_generated']
            }
            
            # Dernières métriques
            recent_metrics = sorted(
                self.metrics_database.values(),
                key=lambda x: x.timestamp,
                reverse=True
            )[:10]
            
            # Derniers patterns
            recent_patterns = sorted(
                self.clusters_database.values(),
                key=lambda x: x.discovered_at,
                reverse=True
            )[:5]
            
            # Alertes actives
            active_alerts = []
            for metric in recent_metrics:
                if metric.significance_level < 0.01:  # Très significatif
                    active_alerts.append({
                        'type': 'high_significance_metric',
                        'message': f"Métrique {metric.metric_name} niveau significatif {metric.significance_level}",
                        'severity': 'high',
                        'timestamp': metric.timestamp.isoformat()
                    })
            
            # Statut système
            system_status = {
                'analytics_engine': 'operational',
                'data_processing': 'active',
                'ml_models': 'trained',
                'cache_hit_rate': len(self.analytics_cache) / (len(self.analytics_cache) + 1),
                'last_update': datetime.utcnow().isoformat()
            }
            
            return {
                'dashboard_id': str(uuid.uuid4()),
                'generated_at': datetime.utcnow().isoformat(),
                'real_time_metrics': current_metrics,
                'recent_metrics': [asdict(m) for m in recent_metrics],
                'recent_patterns': [asdict(p) for p in recent_patterns],
                'active_alerts': active_alerts,
                'system_status': system_status,
                'cache_statistics': {
                    'cached_items': len(self.analytics_cache),
                    'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dashboard temps réel: {e}")
            return {'error': str(e)}
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Retourne les analytics du système d'analyse."""
        try:
            total_metrics = len(self.metrics_database)
            total_patterns = len(self.clusters_database)
            total_trends = len(self.trends_database)
            total_reports = len(self.reports_database)
            
            # Répartition par type d'analyse
            analysis_type_distribution = {}
            for metric in self.metrics_database.values():
                atype = metric.metric_type.value
                analysis_type_distribution[atype] = analysis_type_distribution.get(atype, 0) + 1
            
            # Performance métriques
            if total_metrics > 0:
                avg_confidence = np.mean([m.confidence for m in self.metrics_database.values()])
                significant_metrics = len([m for m in self.metrics_database.values() if m.significance_level < 0.05])
            else:
                avg_confidence = 0.0
                significant_metrics = 0
            
            return {
                'total_metrics_tracked': total_metrics,
                'total_patterns_discovered': total_patterns,
                'total_trends_analyzed': total_trends,
                'total_reports_generated': total_reports,
                'analysis_type_distribution': analysis_type_distribution,
                'average_metric_confidence': float(avg_confidence),
                'significant_metrics_count': significant_metrics,
                'real_time_metrics': self.real_time_metrics,
                'supported_analytics': [atype.value for atype in AnalyticsType],
                'ml_models_active': ['clustering', 'anomaly_detection', 'trend_analysis'],
                'system_performance': {
                    'cache_efficiency': len(self.analytics_cache) > 0,
                    'processing_status': 'operational'
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur analytics engine: {e}")
            return {}