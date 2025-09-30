"""
📊 Data Analytics Engine - Moteur d'Analytics Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Moteur d'analytics avancé pour traitement de données massives et insights temps réel.
Machine Learning intégré avec pipelines automatisés et visualisations interactives.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsQuery:
    """Requête d'analytics structurée"""
    query_id: str
    dataset: str
    metrics: List[str]
    dimensions: List[str]
    filters: Dict[str, Any]
    time_range: Dict[str, str]
    aggregation: str = "sum"
    limit: int = 1000


@dataclass 
class AnalyticsResult:
    """Résultat d'analytics"""
    query_id: str
    data: pd.DataFrame
    metadata: Dict[str, Any]
    execution_time: float
    insights: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]


class DataAnalyticsEngine:
    """Moteur d'analytics avancé pour données massives"""
    
    def __init__(self):
        self.supported_aggregations = [
            'sum', 'avg', 'count', 'min', 'max', 'median', 'std'
        ]
        self.cache_results = {}
        self.ml_models = {}
        self.insight_generators = self._initialize_insight_generators()
    
    async def execute_analytics_query(
        self,
        query: AnalyticsQuery
    ) -> AnalyticsResult:
        """Exécute une requête d'analytics complexe"""
        
        start_time = datetime.utcnow()
        
        try:
            # Vérifier le cache
            cache_key = self._generate_cache_key(query)
            if cache_key in self.cache_results:
                cached_result = self.cache_results[cache_key]
                if self._is_cache_valid(cached_result):
                    logger.info(f"Returning cached result for query {query.query_id}")
                    return cached_result['result']
            
            # Charger les données
            raw_data = await self._load_dataset(query.dataset, query.filters, query.time_range)
            
            # Appliquer les transformations
            processed_data = await self._process_data(raw_data, query)
            
            # Calculer les métriques
            aggregated_data = await self._calculate_metrics(processed_data, query)
            
            # Générer des insights automatiques
            insights = await self._generate_insights(aggregated_data, query)
            
            # Créer visualisations
            visualizations = await self._create_visualizations(aggregated_data, query)
            
            # Calculer temps d'exécution
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Créer résultat
            result = AnalyticsResult(
                query_id=query.query_id,
                data=aggregated_data,
                metadata={
                    'row_count': len(aggregated_data),
                    'columns': list(aggregated_data.columns),
                    'data_quality_score': await self._calculate_data_quality_score(aggregated_data),
                    'query_complexity': self._assess_query_complexity(query)
                },
                execution_time=execution_time,
                insights=insights,
                visualizations=visualizations
            )
            
            # Mettre en cache
            self._cache_result(cache_key, result)
            
            logger.info(f"Analytics query {query.query_id} executed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Erreur exécution query analytics {query.query_id}: {e}")
            raise
    
    async def _load_dataset(
        self,
        dataset_name: str,
        filters: Dict[str, Any],
        time_range: Dict[str, str]
    ) -> pd.DataFrame:
        """Charge un dataset avec filtres appliqués"""
        
        # Simuler chargement depuis différentes sources
        if dataset_name == "content_metrics":
            data = await self._load_content_metrics_data(filters, time_range)
        elif dataset_name == "user_engagement":
            data = await self._load_user_engagement_data(filters, time_range)
        elif dataset_name == "financial_data":
            data = await self._load_financial_data(filters, time_range)
        elif dataset_name == "platform_performance":
            data = await self._load_platform_performance_data(filters, time_range)
        else:
            # Dataset générique
            data = await self._load_generic_dataset(dataset_name, filters, time_range)
        
        return data
    
    async def _load_content_metrics_data(
        self,
        filters: Dict[str, Any],
        time_range: Dict[str, str]
    ) -> pd.DataFrame:
        """Charge les données de métriques de contenu"""
        
        # Simuler données réelles
        np.random.seed(42)
        n_records = 10000
        
        data = {
            'content_id': [f"content_{i}" for i in range(n_records)],
            'creator_id': [f"creator_{np.random.randint(1, 1000)}" for _ in range(n_records)],
            'platform': np.random.choice(['youtube', 'instagram', 'tiktok', 'facebook'], n_records),
            'content_type': np.random.choice(['video', 'image', 'audio', 'text'], n_records),
            'views': np.random.randint(100, 100000, n_records),
            'likes': np.random.randint(10, 10000, n_records),
            'shares': np.random.randint(1, 1000, n_records),
            'comments': np.random.randint(0, 500, n_records),
            'engagement_rate': np.random.uniform(0.01, 0.15, n_records),
            'watch_time': np.random.uniform(30, 600, n_records),
            'revenue': np.random.uniform(0, 1000, n_records),
            'created_at': pd.date_range(
                start=time_range.get('start', '2024-01-01'),
                end=time_range.get('end', '2024-12-31'),
                periods=n_records
            )
        }
        
        df = pd.DataFrame(data)
        
        # Appliquer filtres
        for key, value in filters.items():
            if key in df.columns:
                if isinstance(value, list):
                    df = df[df[key].isin(value)]
                else:
                    df = df[df[key] == value]
        
        return df
    
    async def _load_user_engagement_data(
        self,
        filters: Dict[str, Any],
        time_range: Dict[str, str]
    ) -> pd.DataFrame:
        """Charge les données d'engagement utilisateur"""
        
        np.random.seed(123)
        n_records = 50000
        
        data = {
            'user_id': [f"user_{i}" for i in range(n_records)],
            'session_duration': np.random.uniform(60, 3600, n_records),
            'pages_visited': np.random.randint(1, 20, n_records),
            'actions_taken': np.random.randint(0, 50, n_records),
            'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], n_records),
            'location': np.random.choice(['US', 'UK', 'CA', 'AU', 'DE', 'FR'], n_records),
            'conversion': np.random.choice([0, 1], n_records, p=[0.95, 0.05]),
            'timestamp': pd.date_range(
                start=time_range.get('start', '2024-01-01'),
                end=time_range.get('end', '2024-12-31'),
                periods=n_records
            )
        }
        
        return pd.DataFrame(data)
    
    async def _load_financial_data(
        self,
        filters: Dict[str, Any],
        time_range: Dict[str, str]
    ) -> pd.DataFrame:
        """Charge les données financières"""
        
        np.random.seed(456)
        n_records = 5000
        
        data = {
            'transaction_id': [f"txn_{i}" for i in range(n_records)],
            'creator_id': [f"creator_{np.random.randint(1, 500)}" for _ in range(n_records)],
            'amount': np.random.uniform(1, 5000, n_records),
            'currency': np.random.choice(['USD', 'EUR', 'GBP', 'CAD'], n_records),
            'transaction_type': np.random.choice(['payment', 'withdrawal', 'refund'], n_records),
            'platform_fee': np.random.uniform(0.05, 0.15, n_records),
            'net_amount': lambda x: x['amount'] * (1 - x['platform_fee']),
            'date': pd.date_range(
                start=time_range.get('start', '2024-01-01'),
                end=time_range.get('end', '2024-12-31'),
                periods=n_records
            )
        }
        
        df = pd.DataFrame(data)
        df['net_amount'] = df['amount'] * (1 - df['platform_fee'])
        
        return df
    
    async def _load_platform_performance_data(
        self,
        filters: Dict[str, Any],
        time_range: Dict[str, str]
    ) -> pd.DataFrame:
        """Charge les données de performance plateforme"""
        
        np.random.seed(789)
        n_records = 1000
        
        data = {
            'platform': np.random.choice(['youtube', 'instagram', 'tiktok', 'facebook'], n_records),
            'response_time': np.random.uniform(100, 2000, n_records),
            'error_rate': np.random.uniform(0, 0.05, n_records),
            'throughput': np.random.uniform(1000, 10000, n_records),
            'cpu_usage': np.random.uniform(20, 90, n_records),
            'memory_usage': np.random.uniform(30, 85, n_records),
            'timestamp': pd.date_range(
                start=time_range.get('start', '2024-01-01'),
                end=time_range.get('end', '2024-12-31'),
                periods=n_records
            )
        }
        
        return pd.DataFrame(data)
    
    async def _load_generic_dataset(
        self,
        dataset_name: str,
        filters: Dict[str, Any],
        time_range: Dict[str, str]
    ) -> pd.DataFrame:
        """Charge un dataset générique"""
        
        # Dataset par défaut pour démonstration
        n_records = 1000
        data = {
            'id': range(n_records),
            'value': np.random.uniform(0, 100, n_records),
            'category': np.random.choice(['A', 'B', 'C'], n_records),
            'timestamp': pd.date_range('2024-01-01', periods=n_records, freq='H')
        }
        
        return pd.DataFrame(data)
    
    async def _process_data(
        self,
        raw_data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> pd.DataFrame:
        """Traite et nettoie les données"""
        
        processed_data = raw_data.copy()
        
        # Nettoyer les valeurs manquantes
        processed_data = processed_data.dropna()
        
        # Filtrer par colonnes demandées
        required_columns = query.metrics + query.dimensions
        available_columns = [col for col in required_columns if col in processed_data.columns]
        
        if available_columns:
            processed_data = processed_data[available_columns]
        
        # Appliquer des transformations spécifiques
        processed_data = await self._apply_data_transformations(processed_data, query)
        
        return processed_data
    
    async def _apply_data_transformations(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> pd.DataFrame:
        """Applique des transformations de données spécifiques"""
        
        # Transformations conditionnelles basées sur le type de données
        for column in data.columns:
            if data[column].dtype == 'object':
                # Nettoyer les données textuelles
                data[column] = data[column].str.strip().str.lower()
            
            elif np.issubdtype(data[column].dtype, np.number):
                # Gérer les outliers numériques
                q1 = data[column].quantile(0.25)
                q3 = data[column].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                # Optionnel: clipper les outliers au lieu de les supprimer
                # data[column] = data[column].clip(lower_bound, upper_bound)
        
        return data
    
    async def _calculate_metrics(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> pd.DataFrame:
        """Calcule les métriques agrégées"""
        
        if not query.dimensions:
            # Agrégation globale
            result = self._aggregate_global_metrics(data, query)
        else:
            # Agrégation par dimensions
            result = self._aggregate_by_dimensions(data, query)
        
        # Limiter les résultats
        if len(result) > query.limit:
            result = result.head(query.limit)
        
        return result
    
    def _aggregate_global_metrics(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> pd.DataFrame:
        """Agrégation globale des métriques"""
        
        result = {}
        
        for metric in query.metrics:
            if metric in data.columns:
                if query.aggregation == 'sum':
                    result[metric] = data[metric].sum()
                elif query.aggregation == 'avg':
                    result[metric] = data[metric].mean()
                elif query.aggregation == 'count':
                    result[metric] = data[metric].count()
                elif query.aggregation == 'min':
                    result[metric] = data[metric].min()
                elif query.aggregation == 'max':
                    result[metric] = data[metric].max()
                elif query.aggregation == 'median':
                    result[metric] = data[metric].median()
                elif query.aggregation == 'std':
                    result[metric] = data[metric].std()
        
        return pd.DataFrame([result])
    
    def _aggregate_by_dimensions(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> pd.DataFrame:
        """Agrégation par dimensions"""
        
        # Grouper par dimensions
        grouped = data.groupby(query.dimensions)
        
        # Calculer agrégations pour chaque métrique
        agg_dict = {}
        for metric in query.metrics:
            if metric in data.columns:
                agg_dict[metric] = query.aggregation
        
        if agg_dict:
            result = grouped.agg(agg_dict)
            result = result.reset_index()
        else:
            result = pd.DataFrame()
        
        return result
    
    async def _generate_insights(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> List[Dict[str, Any]]:
        """Génère des insights automatiques"""
        
        insights = []
        
        try:
            # Insights basiques
            insights.extend(await self._generate_basic_insights(data, query))
            
            # Insights de tendances
            insights.extend(await self._generate_trend_insights(data, query))
            
            # Insights d'anomalies
            insights.extend(await self._detect_anomalies(data, query))
            
            # Insights prédictifs
            insights.extend(await self._generate_predictive_insights(data, query))
            
        except Exception as e:
            logger.error(f"Erreur génération insights: {e}")
            insights.append({
                'type': 'error',
                'message': f'Error generating insights: {str(e)}'
            })
        
        return insights
    
    async def _generate_basic_insights(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> List[Dict[str, Any]]:
        """Génère des insights de base"""
        
        insights = []
        
        if data.empty:
            return insights
        
        # Insight sur la taille des données
        insights.append({
            'type': 'data_volume',
            'message': f'Dataset contains {len(data)} records',
            'value': len(data),
            'importance': 'low'
        })
        
        # Insights sur les métriques numériques
        for metric in query.metrics:
            if metric in data.columns and pd.api.types.is_numeric_dtype(data[metric]):
                metric_stats = data[metric].describe()
                
                # Insight sur la distribution
                if metric_stats['std'] > metric_stats['mean']:
                    insights.append({
                        'type': 'distribution',
                        'message': f'{metric} shows high variability',
                        'metric': metric,
                        'std_dev': metric_stats['std'],
                        'mean': metric_stats['mean'],
                        'importance': 'medium'
                    })
                
                # Insight sur les valeurs extrêmes
                if metric_stats['max'] > metric_stats['75%'] * 3:
                    insights.append({
                        'type': 'outlier',
                        'message': f'{metric} has potential outliers',
                        'metric': metric,
                        'max_value': metric_stats['max'],
                        'q75': metric_stats['75%'],
                        'importance': 'medium'
                    })
        
        return insights
    
    async def _generate_trend_insights(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> List[Dict[str, Any]]:
        """Génère des insights de tendances"""
        
        insights = []
        
        # Rechercher des colonnes de dates
        date_columns = data.select_dtypes(include=['datetime', 'datetime64']).columns
        
        if len(date_columns) > 0 and query.dimensions:
            date_col = date_columns[0]
            
            # Analyser tendances par dimension
            for dimension in query.dimensions:
                if dimension in data.columns:
                    # Grouper par dimension et calculer tendance
                    for value in data[dimension].unique()[:5]:  # Top 5 valeurs
                        subset = data[data[dimension] == value]
                        
                        if len(subset) > 2:
                            # Calculer tendance simple
                            subset_sorted = subset.sort_values(date_col)
                            first_half = subset_sorted.head(len(subset_sorted)//2)
                            second_half = subset_sorted.tail(len(subset_sorted)//2)
                            
                            for metric in query.metrics:
                                if metric in data.columns and pd.api.types.is_numeric_dtype(data[metric]):
                                    first_avg = first_half[metric].mean()
                                    second_avg = second_half[metric].mean()
                                    
                                    if second_avg > first_avg * 1.1:
                                        insights.append({
                                            'type': 'positive_trend',
                                            'message': f'{metric} trending up for {dimension}={value}',
                                            'dimension': dimension,
                                            'dimension_value': value,
                                            'metric': metric,
                                            'growth': (second_avg - first_avg) / first_avg * 100,
                                            'importance': 'high'
                                        })
                                    elif second_avg < first_avg * 0.9:
                                        insights.append({
                                            'type': 'negative_trend',
                                            'message': f'{metric} trending down for {dimension}={value}',
                                            'dimension': dimension,
                                            'dimension_value': value,
                                            'metric': metric,
                                            'decline': (first_avg - second_avg) / first_avg * 100,
                                            'importance': 'high'
                                        })
        
        return insights
    
    async def _detect_anomalies(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> List[Dict[str, Any]]:
        """Détecte des anomalies dans les données"""
        
        insights = []
        
        for metric in query.metrics:
            if metric in data.columns and pd.api.types.is_numeric_dtype(data[metric]):
                # Détection simple d'anomalies basée sur IQR
                q1 = data[metric].quantile(0.25)
                q3 = data[metric].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                anomalies = data[(data[metric] < lower_bound) | (data[metric] > upper_bound)]
                
                if len(anomalies) > 0:
                    insights.append({
                        'type': 'anomaly',
                        'message': f'{len(anomalies)} anomalies detected in {metric}',
                        'metric': metric,
                        'anomaly_count': len(anomalies),
                        'percentage': len(anomalies) / len(data) * 100,
                        'importance': 'medium'
                    })
        
        return insights
    
    async def _generate_predictive_insights(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> List[Dict[str, Any]]:
        """Génère des insights prédictifs avec ML"""
        
        insights = []
        
        try:
            # Prédictions simples pour métriques numériques
            numeric_metrics = [m for m in query.metrics 
                             if m in data.columns and pd.api.types.is_numeric_dtype(data[m])]
            
            if len(numeric_metrics) > 0 and len(data) > 10:
                # Prédiction basée sur les tendances historiques
                for metric in numeric_metrics[:2]:  # Limiter à 2 métriques
                    values = data[metric].values
                    
                    if len(values) > 5:
                        # Prédiction simple avec régression linéaire
                        x = np.arange(len(values)).reshape(-1, 1)
                        y = values
                        
                        from sklearn.linear_model import LinearRegression
                        model = LinearRegression()
                        model.fit(x, y)
                        
                        # Prédire prochaines valeurs
                        next_x = np.array([[len(values)], [len(values) + 1]])
                        predictions = model.predict(next_x)
                        
                        insights.append({
                            'type': 'prediction',
                            'message': f'Predicted next values for {metric}',
                            'metric': metric,
                            'current_value': values[-1],
                            'predicted_next': predictions[0],
                            'predicted_trend': 'increasing' if predictions[1] > predictions[0] else 'decreasing',
                            'confidence': 'medium',
                            'importance': 'medium'
                        })
        
        except Exception as e:
            logger.warning(f"Erreur génération insights prédictifs: {e}")
        
        return insights
    
    async def _create_visualizations(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> List[Dict[str, Any]]:
        """Crée des visualisations automatiques"""
        
        visualizations = []
        
        try:
            if data.empty:
                return visualizations
            
            # Graphique en barres pour dimensions catégorielles
            if query.dimensions and len(query.dimensions) == 1:
                viz = await self._create_bar_chart(data, query)
                if viz:
                    visualizations.append(viz)
            
            # Graphique en ligne pour données temporelles
            date_columns = data.select_dtypes(include=['datetime', 'datetime64']).columns
            if len(date_columns) > 0:
                viz = await self._create_time_series_chart(data, query, date_columns[0])
                if viz:
                    visualizations.append(viz)
            
            # Heatmap pour corrélations
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 2:
                viz = await self._create_correlation_heatmap(data, numeric_columns)
                if viz:
                    visualizations.append(viz)
        
        except Exception as e:
            logger.error(f"Erreur création visualisations: {e}")
        
        return visualizations
    
    async def _create_bar_chart(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery
    ) -> Optional[Dict[str, Any]]:
        """Crée un graphique en barres"""
        
        try:
            dimension = query.dimensions[0]
            metric = query.metrics[0] if query.metrics else 'count'
            
            if dimension in data.columns:
                if metric == 'count':
                    chart_data = data[dimension].value_counts().head(10)
                else:
                    chart_data = data.groupby(dimension)[metric].sum().head(10)
                
                return {
                    'type': 'bar_chart',
                    'title': f'{metric} by {dimension}',
                    'data': {
                        'labels': chart_data.index.tolist(),
                        'values': chart_data.values.tolist()
                    },
                    'config': {
                        'x_axis': dimension,
                        'y_axis': metric
                    }
                }
        
        except Exception as e:
            logger.error(f"Erreur création bar chart: {e}")
        
        return None
    
    async def _create_time_series_chart(
        self,
        data: pd.DataFrame,
        query: AnalyticsQuery,
        date_column: str
    ) -> Optional[Dict[str, Any]]:
        """Crée un graphique de série temporelle"""
        
        try:
            metric = query.metrics[0] if query.metrics else 'count'
            
            if metric == 'count':
                time_series = data.groupby(data[date_column].dt.date).size()
            else:
                time_series = data.groupby(data[date_column].dt.date)[metric].sum()
            
            return {
                'type': 'time_series',
                'title': f'{metric} over time',
                'data': {
                    'dates': [str(d) for d in time_series.index],
                    'values': time_series.values.tolist()
                },
                'config': {
                    'x_axis': 'Date',
                    'y_axis': metric
                }
            }
        
        except Exception as e:
            logger.error(f"Erreur création time series: {e}")
        
        return None
    
    async def _create_correlation_heatmap(
        self,
        data: pd.DataFrame,
        numeric_columns: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Crée une heatmap de corrélations"""
        
        try:
            correlation_matrix = data[numeric_columns].corr()
            
            return {
                'type': 'heatmap',
                'title': 'Correlation Matrix',
                'data': {
                    'matrix': correlation_matrix.values.tolist(),
                    'labels': correlation_matrix.columns.tolist()
                },
                'config': {
                    'colorscale': 'RdBu',
                    'center': 0
                }
            }
        
        except Exception as e:
            logger.error(f"Erreur création heatmap: {e}")
        
        return None
    
    async def _calculate_data_quality_score(self, data: pd.DataFrame) -> float:
        """Calcule un score de qualité des données"""
        
        if data.empty:
            return 0.0
        
        # Facteurs de qualité
        completeness = 1 - (data.isnull().sum().sum() / (len(data) * len(data.columns)))
        uniqueness = data.nunique().mean() / len(data)
        
        # Score global (moyenne pondérée)
        quality_score = (completeness * 0.7 + uniqueness * 0.3) * 100
        
        return min(quality_score, 100.0)
    
    def _assess_query_complexity(self, query: AnalyticsQuery) -> str:
        """Évalue la complexité d'une requête"""
        
        complexity_score = 0
        
        # Facteurs de complexité
        complexity_score += len(query.metrics)
        complexity_score += len(query.dimensions) * 2
        complexity_score += len(query.filters)
        
        if query.limit > 1000:
            complexity_score += 1
        
        if complexity_score <= 3:
            return 'low'
        elif complexity_score <= 7:
            return 'medium'
        else:
            return 'high'
    
    def _generate_cache_key(self, query: AnalyticsQuery) -> str:
        """Génère une clé de cache pour la requête"""
        
        key_components = [
            query.dataset,
            ','.join(sorted(query.metrics)),
            ','.join(sorted(query.dimensions)),
            json.dumps(query.filters, sort_keys=True),
            json.dumps(query.time_range, sort_keys=True),
            query.aggregation,
            str(query.limit)
        ]
        
        import hashlib
        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Vérifie si le résultat en cache est encore valide"""
        
        cache_ttl = 300  # 5 minutes
        cached_time = cached_result['timestamp']
        
        return (datetime.utcnow() - cached_time).seconds < cache_ttl
    
    def _cache_result(self, cache_key: str, result: AnalyticsResult) -> None:
        """Met en cache un résultat"""
        
        self.cache_results[cache_key] = {
            'result': result,
            'timestamp': datetime.utcnow()
        }
        
        # Limiter la taille du cache
        if len(self.cache_results) > 100:
            # Supprimer les plus anciens
            oldest_key = min(self.cache_results.keys(), 
                           key=lambda k: self.cache_results[k]['timestamp'])
            del self.cache_results[oldest_key]
    
    def _initialize_insight_generators(self) -> Dict[str, Any]:
        """Initialise les générateurs d'insights"""
        
        return {
            'trend_detector': {
                'window_size': 7,
                'threshold': 0.1
            },
            'anomaly_detector': {
                'method': 'iqr',
                'sensitivity': 1.5
            },
            'pattern_detector': {
                'min_support': 0.1,
                'confidence': 0.8
            }
        }


# Instance globale du service
data_analytics_engine = DataAnalyticsEngine()