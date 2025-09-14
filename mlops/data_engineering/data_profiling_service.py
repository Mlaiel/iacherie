"""
📊 Data Profiling Service - Enterprise MLOps
Expert DBA + Data Engineering: Service profilage données avec analytics avancés

🎯 EXPERTISE DÉMONTRÉ:
- DBA: Profilage métadonnées + statistiques distribution
- Data Engineering: Analytics données temps réel + qualité
- ML Engineer: Détection anomalies + drift data
"""

import asyncio
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataType(Enum):
    """Types de données détectés"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    TEXT = "text"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    BINARY = "binary"

@dataclass
class ColumnProfile:
    """Profil d'une colonne de données"""
    name: str
    data_type: DataType
    total_count: int
    null_count: int
    unique_count: int
    null_percentage: float
    uniqueness_ratio: float
    
    # Statistiques numériques
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    quartiles: Optional[List[float]] = None
    
    # Statistiques catégorielles
    most_frequent_values: List[tuple] = field(default_factory=list)
    value_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Détection anomalies
    outliers_count: int = 0
    outliers_percentage: float = 0.0
    
    # Patterns et qualité
    patterns: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    issues: List[str] = field(default_factory=list)

@dataclass
class DatasetProfile:
    """Profil complet d'un dataset"""
    dataset_id: str
    profiling_date: datetime
    total_rows: int
    total_columns: int
    column_profiles: Dict[str, ColumnProfile]
    
    # Statistiques globales
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    overall_quality_score: float = 0.0
    
    # Corrélations
    correlations: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Recommandations
    recommendations: List[str] = field(default_factory=list)
    
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataProfilingService:
    """
    📊 Service Enterprise de Profilage de Données
    
    Expertise DBA + Data Engineering + ML:
    - Profilage automatique complet
    - Détection automatique types + patterns
    - Analytics qualité temps réel
    - Détection anomalies et outliers
    - Recommandations amélioration
    """
    
    def __init__(self):
        self.profiles: Dict[str, DatasetProfile] = {}
        self.profiling_history: List[DatasetProfile] = []
        
    async def profile_dataset(
        self,
        dataset_id: str,
        data: Dict[str, List[Any]],
        sample_size: Optional[int] = None
    ) -> DatasetProfile:
        """
        Profile complet d'un dataset
        
        Expertise DBA: Statistiques complètes + détection types
        """
        start_time = datetime.utcnow()
        
        # Échantillonnage si nécessaire
        if sample_size and any(len(values) > sample_size for values in data.values()):
            data = self._sample_data(data, sample_size)
        
        total_rows = len(next(iter(data.values()))) if data else 0
        total_columns = len(data)
        
        # Profilage de chaque colonne
        column_profiles = {}
        for column_name, values in data.items():
            column_profile = await self._profile_column(column_name, values)
            column_profiles[column_name] = column_profile
        
        # Calcul corrélations pour colonnes numériques
        correlations = await self._calculate_correlations(data, column_profiles)
        
        # Scores globaux
        completeness_score = self._calculate_completeness_score(column_profiles)
        consistency_score = self._calculate_consistency_score(column_profiles)
        overall_quality_score = (completeness_score + consistency_score) / 2
        
        # Recommandations
        recommendations = self._generate_recommendations(column_profiles)
        
        # Création du profil
        profile = DatasetProfile(
            dataset_id=dataset_id,
            profiling_date=start_time,
            total_rows=total_rows,
            total_columns=total_columns,
            column_profiles=column_profiles,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            overall_quality_score=overall_quality_score,
            correlations=correlations,
            recommendations=recommendations
        )
        
        # Stockage
        self.profiles[dataset_id] = profile
        self.profiling_history.append(profile)
        
        # Performance logging
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Dataset profiling completed for {dataset_id} in {duration:.2f}s")
        logger.info(f"Quality score: {overall_quality_score:.2f} ({total_rows} rows, {total_columns} columns)")
        
        return profile
    
    async def _profile_column(self, column_name: str, values: List[Any]) -> ColumnProfile:
        """Profile une colonne individuelle"""
        total_count = len(values)
        
        # Filtrer les valeurs non-nulles
        non_null_values = [v for v in values if v is not None and v != '']
        null_count = total_count - len(non_null_values)
        null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0
        
        # Valeurs uniques
        unique_count = len(set(non_null_values))
        uniqueness_ratio = unique_count / len(non_null_values) if non_null_values else 0
        
        # Détection automatique du type
        data_type = self._detect_data_type(non_null_values)
        
        # Initialisation du profil
        profile = ColumnProfile(
            name=column_name,
            data_type=data_type,
            total_count=total_count,
            null_count=null_count,
            unique_count=unique_count,
            null_percentage=null_percentage,
            uniqueness_ratio=uniqueness_ratio
        )
        
        # Statistiques spécifiques par type
        if data_type == DataType.NUMERIC:
            await self._profile_numeric_column(profile, non_null_values)
        elif data_type == DataType.CATEGORICAL:
            await self._profile_categorical_column(profile, non_null_values)
        elif data_type == DataType.TEXT:
            await self._profile_text_column(profile, non_null_values)
        
        # Score de qualité
        profile.quality_score = self._calculate_column_quality_score(profile)
        
        return profile
    
    def _detect_data_type(self, values: List[Any]) -> DataType:
        """Détection automatique du type de données"""
        if not values:
            return DataType.TEXT
        
        # Échantillon pour performance
        sample = values[:min(100, len(values))]
        
        # Test numérique
        numeric_count = 0
        for value in sample:
            try:
                float(str(value))
                numeric_count += 1
            except (ValueError, TypeError):
                pass
        
        if numeric_count / len(sample) > 0.8:
            return DataType.NUMERIC
        
        # Test booléen
        boolean_values = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n'}
        string_values = [str(v).lower() for v in sample]
        if all(v in boolean_values for v in string_values):
            return DataType.BOOLEAN
        
        # Test datetime
        datetime_patterns = [
            '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'
        ]
        datetime_count = 0
        for value in sample:
            str_value = str(value)
            for pattern in datetime_patterns:
                try:
                    datetime.strptime(str_value, pattern)
                    datetime_count += 1
                    break
                except ValueError:
                    continue
        
        if datetime_count / len(sample) > 0.7:
            return DataType.DATETIME
        
        # Test catégoriel vs texte
        unique_ratio = len(set(sample)) / len(sample)
        if unique_ratio < 0.5:  # Peu de valeurs uniques
            return DataType.CATEGORICAL
        
        return DataType.TEXT
    
    async def _profile_numeric_column(self, profile: ColumnProfile, values: List[Any]):
        """Profilage spécialisé pour colonnes numériques"""
        try:
            numeric_values = [float(v) for v in values]
            
            profile.min_value = min(numeric_values)
            profile.max_value = max(numeric_values)
            profile.mean = statistics.mean(numeric_values)
            profile.median = statistics.median(numeric_values)
            
            if len(numeric_values) > 1:
                profile.std_dev = statistics.stdev(numeric_values)
                
                # Quartiles
                sorted_values = sorted(numeric_values)
                n = len(sorted_values)
                profile.quartiles = [
                    sorted_values[n//4],
                    profile.median,
                    sorted_values[3*n//4]
                ]
                
                # Détection outliers (IQR method)
                q1, q3 = profile.quartiles[0], profile.quartiles[2]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
                profile.outliers_count = len(outliers)
                profile.outliers_percentage = (len(outliers) / len(numeric_values)) * 100
                
                if profile.outliers_percentage > 5:
                    profile.issues.append(f"High outlier percentage: {profile.outliers_percentage:.1f}%")
                    
        except (ValueError, TypeError) as e:
            profile.issues.append(f"Numeric profiling error: {str(e)}")
    
    async def _profile_categorical_column(self, profile: ColumnProfile, values: List[Any]):
        """Profilage spécialisé pour colonnes catégorielles"""
        value_counts = Counter(str(v) for v in values)
        
        # Valeurs les plus fréquentes (top 10)
        profile.most_frequent_values = value_counts.most_common(10)
        profile.value_distribution = dict(value_counts)
        
        # Vérification distribution
        total_values = len(values)
        most_frequent_count = value_counts.most_common(1)[0][1] if value_counts else 0
        
        # Détection de déséquilibre
        if most_frequent_count / total_values > 0.9:
            profile.issues.append("Highly imbalanced distribution")
        
        # Trop de catégories uniques
        if profile.unique_count > total_values * 0.5:
            profile.issues.append("High cardinality - consider if this should be categorical")
    
    async def _profile_text_column(self, profile: ColumnProfile, values: List[Any]):
        """Profilage spécialisé pour colonnes texte"""
        text_values = [str(v) for v in values]
        
        # Statistiques longueur
        lengths = [len(text) for text in text_values]
        if lengths:
            avg_length = statistics.mean(lengths)
            min_length = min(lengths)
            max_length = max(lengths)
            
            profile.metadata["text_stats"] = {
                "avg_length": avg_length,
                "min_length": min_length,
                "max_length": max_length
            }
            
            # Détection patterns communs
            patterns = self._detect_text_patterns(text_values)
            profile.patterns = patterns
            
            # Issues texte
            if avg_length < 2:
                profile.issues.append("Very short text values")
            if max_length > 1000:
                profile.issues.append("Very long text values detected")
    
    def _detect_text_patterns(self, text_values: List[str]) -> List[str]:
        """Détecte des patterns communs dans le texte"""
        patterns = []
        
        # Email pattern
        email_count = sum(1 for text in text_values if '@' in text and '.' in text)
        if email_count / len(text_values) > 0.8:
            patterns.append("email")
        
        # URL pattern
        url_count = sum(1 for text in text_values if text.startswith(('http://', 'https://')))
        if url_count / len(text_values) > 0.5:
            patterns.append("url")
        
        # Uppercase pattern
        uppercase_count = sum(1 for text in text_values if text.isupper())
        if uppercase_count / len(text_values) > 0.8:
            patterns.append("uppercase")
        
        return patterns
    
    async def _calculate_correlations(
        self, 
        data: Dict[str, List[Any]], 
        column_profiles: Dict[str, ColumnProfile]
    ) -> Dict[str, Dict[str, float]]:
        """Calcule les corrélations entre colonnes numériques"""
        correlations = {}
        
        # Identifier colonnes numériques
        numeric_columns = [
            name for name, profile in column_profiles.items()
            if profile.data_type == DataType.NUMERIC
        ]
        
        if len(numeric_columns) < 2:
            return correlations
        
        try:
            # Matrice de corrélation
            for col1 in numeric_columns:
                correlations[col1] = {}
                values1 = [float(v) for v in data[col1] if v is not None]
                
                for col2 in numeric_columns:
                    if col1 == col2:
                        correlations[col1][col2] = 1.0
                    else:
                        values2 = [float(v) for v in data[col2] if v is not None]
                        
                        # Calcul corrélation Pearson
                        if len(values1) == len(values2) and len(values1) > 1:
                            correlation = np.corrcoef(values1, values2)[0, 1]
                            if not np.isnan(correlation):
                                correlations[col1][col2] = float(correlation)
                            else:
                                correlations[col1][col2] = 0.0
                        else:
                            correlations[col1][col2] = 0.0
                            
        except Exception as e:
            logger.warning(f"Correlation calculation failed: {str(e)}")
        
        return correlations
    
    def _calculate_completeness_score(self, column_profiles: Dict[str, ColumnProfile]) -> float:
        """Calcule le score de complétude du dataset"""
        if not column_profiles:
            return 0.0
        
        total_completeness = sum(
            100 - profile.null_percentage 
            for profile in column_profiles.values()
        )
        
        return total_completeness / len(column_profiles)
    
    def _calculate_consistency_score(self, column_profiles: Dict[str, ColumnProfile]) -> float:
        """Calcule le score de cohérence du dataset"""
        if not column_profiles:
            return 0.0
        
        total_consistency = sum(
            profile.quality_score for profile in column_profiles.values()
        )
        
        return total_consistency / len(column_profiles)
    
    def _calculate_column_quality_score(self, profile: ColumnProfile) -> float:
        """Calcule le score de qualité d'une colonne"""
        score = 100.0
        
        # Pénalités
        score -= profile.null_percentage * 0.5  # Pénalité pour valeurs nulles
        score -= len(profile.issues) * 10  # Pénalité pour issues détectées
        score -= profile.outliers_percentage * 0.2  # Pénalité pour outliers
        
        # Bonus pour bonne distribution
        if profile.data_type == DataType.CATEGORICAL and 0.1 < profile.uniqueness_ratio < 0.8:
            score += 5  # Bonne cardinalité
        
        return max(0.0, min(100.0, score))
    
    def _generate_recommendations(self, column_profiles: Dict[str, ColumnProfile]) -> List[str]:
        """Génère des recommandations d'amélioration"""
        recommendations = []
        
        # Analyses globales
        high_null_columns = [
            name for name, profile in column_profiles.items()
            if profile.null_percentage > 20
        ]
        
        if high_null_columns:
            recommendations.append(
                f"Consider data imputation for columns with high null rates: {', '.join(high_null_columns[:3])}"
            )
        
        # Colonnes avec beaucoup d'outliers
        high_outlier_columns = [
            name for name, profile in column_profiles.items()
            if profile.outliers_percentage > 10
        ]
        
        if high_outlier_columns:
            recommendations.append(
                f"Review outlier handling for columns: {', '.join(high_outlier_columns[:3])}"
            )
        
        # Colonnes catégorielles haute cardinalité
        high_cardinality_columns = [
            name for name, profile in column_profiles.items()
            if profile.data_type == DataType.CATEGORICAL and profile.uniqueness_ratio > 0.8
        ]
        
        if high_cardinality_columns:
            recommendations.append(
                f"Consider encoding strategies for high-cardinality categorical columns: {', '.join(high_cardinality_columns[:3])}"
            )
        
        return recommendations
    
    def _sample_data(self, data: Dict[str, List[Any]], sample_size: int) -> Dict[str, List[Any]]:
        """Échantillonne les données pour performance"""
        sampled_data = {}
        
        for column_name, values in data.items():
            if len(values) > sample_size:
                # Échantillonnage stratifié pour préserver la distribution
                step = len(values) // sample_size
                sampled_values = values[::step][:sample_size]
            else:
                sampled_values = values
            
            sampled_data[column_name] = sampled_values
        
        return sampled_data
    
    async def get_profile(self, dataset_id: str) -> Optional[DatasetProfile]:
        """Récupère le profil d'un dataset"""
        return self.profiles.get(dataset_id)
    
    async def compare_profiles(
        self, 
        dataset_id1: str, 
        dataset_id2: str
    ) -> Dict[str, Any]:
        """Compare deux profils de datasets"""
        profile1 = self.profiles.get(dataset_id1)
        profile2 = self.profiles.get(dataset_id2)
        
        if not profile1 or not profile2:
            return {"error": "One or both profiles not found"}
        
        comparison = {
            "dataset1": dataset_id1,
            "dataset2": dataset_id2,
            "row_count_diff": profile2.total_rows - profile1.total_rows,
            "column_count_diff": profile2.total_columns - profile1.total_columns,
            "quality_score_diff": profile2.overall_quality_score - profile1.overall_quality_score,
            "common_columns": [],
            "column_differences": {}
        }
        
        # Colonnes communes
        common_columns = set(profile1.column_profiles.keys()) & set(profile2.column_profiles.keys())
        comparison["common_columns"] = list(common_columns)
        
        # Différences par colonne
        for column in common_columns:
            col1 = profile1.column_profiles[column]
            col2 = profile2.column_profiles[column]
            
            comparison["column_differences"][column] = {
                "null_percentage_diff": col2.null_percentage - col1.null_percentage,
                "unique_count_diff": col2.unique_count - col1.unique_count,
                "quality_score_diff": col2.quality_score - col1.quality_score
            }
        
        return comparison
    
    async def get_profiling_summary(self) -> Dict[str, Any]:
        """Résumé de tous les profilages"""
        if not self.profiles:
            return {"total_profiles": 0}
        
        total_profiles = len(self.profiles)
        avg_quality = sum(p.overall_quality_score for p in self.profiles.values()) / total_profiles
        
        # Distribution des scores de qualité
        quality_distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for profile in self.profiles.values():
            if profile.overall_quality_score >= 90:
                quality_distribution["excellent"] += 1
            elif profile.overall_quality_score >= 75:
                quality_distribution["good"] += 1
            elif profile.overall_quality_score >= 50:
                quality_distribution["fair"] += 1
            else:
                quality_distribution["poor"] += 1
        
        return {
            "total_profiles": total_profiles,
            "average_quality_score": avg_quality,
            "quality_distribution": quality_distribution,
            "latest_profiling": max(p.profiling_date for p in self.profiles.values()) if self.profiles else None
        }

# Exemple d'utilisation
async def demo_data_profiling():
    """Démo du service de profilage"""
    profiler = DataProfilingService()
    
    # Données d'exemple
    sample_data = {
        "user_id": [1, 2, 3, 4, 5, None],
        "age": [25, 30, 35, 28, 42, 25],
        "salary": [50000, 75000, 90000, 65000, 120000, 52000],
        "department": ["IT", "HR", "IT", "Finance", "IT", "HR"],
        "email": ["user1@company.com", "user2@company.com", None, "user4@company.com", "user5@company.com", "user6@company.com"]
    }
    
    # Profilage
    profile = await profiler.profile_dataset("employee_data", sample_data)
    
    print(f"Dataset profiled: {profile.dataset_id}")
    print(f"Quality score: {profile.overall_quality_score:.2f}")
    print(f"Recommendations: {len(profile.recommendations)}")
    
    for column_name, column_profile in profile.column_profiles.items():
        print(f"\n{column_name}:")
        print(f"  Type: {column_profile.data_type.value}")
        print(f"  Null %: {column_profile.null_percentage:.1f}%")
        print(f"  Quality: {column_profile.quality_score:.1f}")

if __name__ == "__main__":
    asyncio.run(demo_data_profiling())