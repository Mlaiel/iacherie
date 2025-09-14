"""🚀 Temporal Feature Generator - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/feature_stores/temporal_feature_generator.py
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GÉNÉRATEUR DE FEATURES TEMPORELLES
Génération de features time-series pour analyse et prédiction
- Time-series feature generation pour trend analysis
- Seasonal decomposition et cyclical patterns
- Creator-specific temporal patterns
- Forecasting features et predictive indicators
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Configuration
logger = logging.getLogger(__name__)

class TemporalFeatureType(Enum):
    """Types de features temporelles"""
    TREND = "trend"
    SEASONALITY = "seasonality"
    CYCLICAL = "cyclical"
    LAG = "lag"
    ROLLING_STATS = "rolling_stats"
    DIFFERENCE = "difference"
    FOURIER = "fourier"
    CALENDAR = "calendar"

class AggregationType(Enum):
    """Types d'agrégation temporelle"""
    MEAN = "mean"
    MEDIAN = "median"
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    STD = "std"
    VAR = "var"
    SKEW = "skew"
    KURTOSIS = "kurtosis"

class TimeWindow(Enum):
    """Fenêtres temporelles"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class CreatorType(Enum):
    """Types de créateurs pour patterns temporels spécialisés"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class TemporalPattern:
    """Pattern temporel détecté"""
    pattern_id: str
    pattern_type: TemporalFeatureType
    frequency: str  # "daily", "weekly", "monthly"
    amplitude: float
    phase: float
    confidence: float
    creator_type: Optional[CreatorType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemporalFeature:
    """Feature temporelle générée"""
    feature_name: str
    value: Union[float, List[float]]
    feature_type: TemporalFeatureType
    window_size: int
    aggregation_type: AggregationType
    timestamp: datetime
    creator_type: Optional[CreatorType] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimeSeriesData:
    """Données de série temporelle"""
    timestamps: List[datetime]
    values: List[float]
    feature_name: str
    creator_type: Optional[CreatorType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratorConfig:
    """Configuration du générateur de features temporelles"""
    default_window_sizes: List[int] = field(default_factory=lambda: [7, 14, 30, 90])
    lag_periods: List[int] = field(default_factory=lambda: [1, 7, 30])
    rolling_windows: List[int] = field(default_factory=lambda: [3, 7, 14, 30])
    enable_seasonality: bool = True
    enable_trend_analysis: bool = True
    enable_fourier_features: bool = True
    fourier_terms: int = 3
    min_data_points: int = 30
    creator_specific_patterns: bool = True
    aggregation_types: List[AggregationType] = field(default_factory=lambda: [
        AggregationType.MEAN, AggregationType.STD, AggregationType.MIN, AggregationType.MAX
    ])

class TemporalFeatureGenerator:
    """🔬 Générateur de features temporelles pour ML"""
    
    def __init__(self, config -> None: GeneratorConfig) -> None:
        self.config = config
        self.generator_id = str(uuid.uuid4())
        self.patterns: Dict[str, List[TemporalPattern]] = {}
        self.feature_cache: Dict[str, List[TemporalFeature]] = {}
        self._creator_patterns = self._initialize_creator_patterns()
        
        logger.info(f"Temporal Feature Generator initialized: {self.generator_id}")
    
    def _initialize_creator_patterns(self) -> Dict[CreatorType, Dict[str, Any]]:
        """Initialise les patterns spécifiques aux créateurs"""
        return {
            CreatorType.MUSICIAN: {
                'peak_hours': [19, 20, 21, 22],  # 7-10 PM
                'peak_days': [5, 6],  # Weekend
                'seasonal_boost': {'summer': 1.2, 'winter': 0.9},
                'weekly_pattern': [0.8, 0.9, 0.9, 1.0, 1.1, 1.3, 1.2]  # Mon-Sun
            },
            CreatorType.BLOGGER: {
                'peak_hours': [8, 9, 12, 17, 18],  # Morning and evening
                'peak_days': [1, 2, 3, 4],  # Weekdays
                'seasonal_boost': {'spring': 1.1, 'fall': 1.1},
                'weekly_pattern': [1.2, 1.3, 1.2, 1.1, 1.0, 0.8, 0.7]
            },
            CreatorType.PHOTOGRAPHER: {
                'peak_hours': [6, 7, 17, 18, 19],  # Golden hours
                'peak_days': [5, 6],  # Weekend
                'seasonal_boost': {'spring': 1.3, 'summer': 1.2, 'fall': 1.1},
                'weekly_pattern': [0.9, 0.9, 1.0, 1.0, 1.1, 1.3, 1.2]
            },
            CreatorType.INFLUENCER: {
                'peak_hours': [11, 12, 19, 20, 21],  # Lunch and evening
                'peak_days': [0, 1, 2, 3, 4, 5, 6],  # All days
                'seasonal_boost': {'summer': 1.1, 'winter': 1.0},
                'weekly_pattern': [1.0, 1.1, 1.0, 1.0, 1.1, 1.2, 1.1]
            },
            CreatorType.COMEDIAN: {
                'peak_hours': [19, 20, 21, 22, 23],  # Evening/night
                'peak_days': [4, 5, 6],  # Fri-Sun
                'seasonal_boost': {'winter': 1.1},  # People stay inside more
                'weekly_pattern': [0.8, 0.8, 0.9, 0.9, 1.1, 1.3, 1.2]
            }
        }
    
    async def generate_temporal_features(self, time_series_data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère toutes les features temporelles pour une série"""
        try:
            if len(time_series_data.values) < self.config.min_data_points:
                logger.warning(f"Insufficient data points: {len(time_series_data.values)} < {self.config.min_data_points}")
                return []
            
            features = []
            
            # Lag features
            lag_features = await self._generate_lag_features(time_series_data)
            features.extend(lag_features)
            
            # Rolling statistics
            rolling_features = await self._generate_rolling_features(time_series_data)
            features.extend(rolling_features)
            
            # Trend features
            if self.config.enable_trend_analysis:
                trend_features = await self._generate_trend_features(time_series_data)
                features.extend(trend_features)
            
            # Seasonality features
            if self.config.enable_seasonality:
                seasonal_features = await self._generate_seasonal_features(time_series_data)
                features.extend(seasonal_features)
            
            # Calendar features
            calendar_features = await self._generate_calendar_features(time_series_data)
            features.extend(calendar_features)
            
            # Fourier features
            if self.config.enable_fourier_features:
                fourier_features = await self._generate_fourier_features(time_series_data)
                features.extend(fourier_features)
            
            # Difference features
            diff_features = await self._generate_difference_features(time_series_data)
            features.extend(diff_features)
            
            # Creator-specific features
            if time_series_data.creator_type and self.config.creator_specific_patterns:
                creator_features = await self._generate_creator_specific_features(time_series_data)
                features.extend(creator_features)
            
            # Cache des features
            cache_key = f"{time_series_data.feature_name}_{time_series_data.creator_type}"
            self.feature_cache[cache_key] = features
            
            logger.info(f"Generated {len(features)} temporal features for {time_series_data.feature_name}")
            return features
            
        except Exception as e:
            logger.error(f"Error generating temporal features: {e}")
            return []
    
    async def _generate_lag_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features de lag (valeurs décalées)"""
        features = []
        
        try:
            for lag in self.config.lag_periods:
                if lag < len(data.values):
                    lagged_values = [None] * lag + data.values[:-lag]
                    current_value = lagged_values[-1] if lagged_values[-1] is not None else 0.0
                    
                    feature = TemporalFeature(
                        feature_name=f"{data.feature_name}_lag_{lag}",
                        value=current_value,
                        feature_type=TemporalFeatureType.LAG,
                        window_size=lag,
                        aggregation_type=AggregationType.MEAN,
                        timestamp=data.timestamps[-1],
                        creator_type=data.creator_type,
                        metadata={'lag_period': lag}
                    )
                    features.append(feature)
        
        except Exception as e:
            logger.error(f"Error generating lag features: {e}")
        
        return features
    
    async def _generate_rolling_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features de statistiques mobiles"""
        features = []
        
        try:
            for window in self.config.rolling_windows:
                if window <= len(data.values):
                    for agg_type in self.config.aggregation_types:
                        window_values = data.values[-window:]
                        
                        if agg_type == AggregationType.MEAN:
                            value = np.mean(window_values)
                        elif agg_type == AggregationType.STD:
                            value = np.std(window_values)
                        elif agg_type == AggregationType.MIN:
                            value = np.min(window_values)
                        elif agg_type == AggregationType.MAX:
                            value = np.max(window_values)
                        elif agg_type == AggregationType.MEDIAN:
                            value = np.median(window_values)
                        elif agg_type == AggregationType.SUM:
                            value = np.sum(window_values)
                        else:
                            value = np.mean(window_values)  # Fallback
                        
                        feature = TemporalFeature(
                            feature_name=f"{data.feature_name}_rolling_{window}_{agg_type.value}",
                            value=float(value),
                            feature_type=TemporalFeatureType.ROLLING_STATS,
                            window_size=window,
                            aggregation_type=agg_type,
                            timestamp=data.timestamps[-1],
                            creator_type=data.creator_type,
                            metadata={'rolling_window': window}
                        )
                        features.append(feature)
        
        except Exception as e:
            logger.error(f"Error generating rolling features: {e}")
        
        return features
    
    async def _generate_trend_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features de tendance"""
        features = []
        
        try:
            # Tendance linéaire sur différentes fenêtres
            for window in self.config.default_window_sizes:
                if window <= len(data.values):
                    window_values = data.values[-window:]
                    
                    # Calcul de la pente (tendance)
                    x = np.arange(len(window_values))
                    slope = np.polyfit(x, window_values, 1)[0] if len(window_values) > 1 else 0.0
                    
                    # Coefficient de corrélation avec tendance linéaire
                    if len(window_values) > 2:
                        linear_trend = np.polyval([slope, window_values[0]], x)
                        correlation = np.corrcoef(window_values, linear_trend)[0, 1]
                        correlation = correlation if not np.isnan(correlation) else 0.0
                    else:
                        correlation = 0.0
                    
                    # Feature de pente
                    trend_feature = TemporalFeature(
                        feature_name=f"{data.feature_name}_trend_slope_{window}",
                        value=float(slope),
                        feature_type=TemporalFeatureType.TREND,
                        window_size=window,
                        aggregation_type=AggregationType.MEAN,
                        timestamp=data.timestamps[-1],
                        creator_type=data.creator_type,
                        confidence=abs(correlation),
                        metadata={'trend_type': 'slope', 'correlation': correlation}
                    )
                    features.append(trend_feature)
                    
                    # Feature de corrélation avec tendance
                    corr_feature = TemporalFeature(
                        feature_name=f"{data.feature_name}_trend_correlation_{window}",
                        value=float(correlation),
                        feature_type=TemporalFeatureType.TREND,
                        window_size=window,
                        aggregation_type=AggregationType.MEAN,
                        timestamp=data.timestamps[-1],
                        creator_type=data.creator_type,
                        metadata={'trend_type': 'correlation'}
                    )
                    features.append(corr_feature)
        
        except Exception as e:
            logger.error(f"Error generating trend features: {e}")
        
        return features
    
    async def _generate_seasonal_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features de saisonnalité"""
        features = []
        
        try:
            if len(data.values) < 14:  # Besoin d'au moins 2 semaines
                return features
            
            # Décomposition saisonnière simple
            # Detecter la périodicité hebdomadaire (7 jours)
            if len(data.values) >= 21:  # 3 semaines minimum
                weekly_pattern = []
                for day_of_week in range(7):
                    day_values = []
                    for i in range(day_of_week, len(data.values), 7):
                        day_values.append(data.values[i])
                    
                    if day_values:
                        weekly_pattern.append(np.mean(day_values))
                    else:
                        weekly_pattern.append(0.0)
                
                # Amplitude saisonnière
                seasonal_amplitude = np.std(weekly_pattern) if len(weekly_pattern) > 1 else 0.0
                
                # Day of week feature pour le timestamp actuel
                current_dow = data.timestamps[-1].weekday()
                dow_seasonal_value = weekly_pattern[current_dow] if current_dow < len(weekly_pattern) else 0.0
                
                amplitude_feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_seasonal_amplitude_weekly",
                    value=float(seasonal_amplitude),
                    feature_type=TemporalFeatureType.SEASONALITY,
                    window_size=21,
                    aggregation_type=AggregationType.STD,
                    timestamp=data.timestamps[-1],
                    creator_type=data.creator_type,
                    metadata={'seasonality_type': 'weekly', 'pattern': weekly_pattern}
                )
                features.append(amplitude_feature)
                
                dow_feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_seasonal_dow_value",
                    value=float(dow_seasonal_value),
                    feature_type=TemporalFeatureType.SEASONALITY,
                    window_size=7,
                    aggregation_type=AggregationType.MEAN,
                    timestamp=data.timestamps[-1],
                    creator_type=data.creator_type,
                    metadata={'seasonality_type': 'day_of_week', 'dow': current_dow}
                )
                features.append(dow_feature)
        
        except Exception as e:
            logger.error(f"Error generating seasonal features: {e}")
        
        return features
    
    async def _generate_calendar_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features calendaires"""
        features = []
        
        try:
            current_time = data.timestamps[-1]
            
            # Features temporelles basiques
            calendar_features_map = {
                'hour_of_day': current_time.hour,
                'day_of_week': current_time.weekday(),
                'day_of_month': current_time.day,
                'month_of_year': current_time.month,
                'quarter': (current_time.month - 1) // 3 + 1,
                'is_weekend': 1.0 if current_time.weekday() >= 5 else 0.0,
                'is_month_start': 1.0 if current_time.day <= 3 else 0.0,
                'is_month_end': 1.0 if current_time.day >= 28 else 0.0,
                'week_of_year': current_time.isocalendar()[1]
            }
            
            # Features cycliques (sin/cos pour capturer la cyclicité)
            calendar_features_map.update({
                'hour_sin': np.sin(2 * np.pi * current_time.hour / 24),
                'hour_cos': np.cos(2 * np.pi * current_time.hour / 24),
                'day_of_week_sin': np.sin(2 * np.pi * current_time.weekday() / 7),
                'day_of_week_cos': np.cos(2 * np.pi * current_time.weekday() / 7),
                'month_sin': np.sin(2 * np.pi * current_time.month / 12),
                'month_cos': np.cos(2 * np.pi * current_time.month / 12)
            })
            
            for feature_name, value in calendar_features_map.items():
                feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_calendar_{feature_name}",
                    value=float(value),
                    feature_type=TemporalFeatureType.CALENDAR,
                    window_size=1,
                    aggregation_type=AggregationType.MEAN,
                    timestamp=current_time,
                    creator_type=data.creator_type,
                    metadata={'calendar_type': feature_name}
                )
                features.append(feature)
        
        except Exception as e:
            logger.error(f"Error generating calendar features: {e}")
        
        return features
    
    async def _generate_fourier_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features de Fourier pour capturer les cycles"""
        features = []
        
        try:
            if len(data.values) < 14:
                return features
            
            # Analyse de Fourier sur les données
            values = np.array(data.values)
            fft = np.fft.fft(values)
            freqs = np.fft.fftfreq(len(values))
            
            # Prendre les N premiers termes non-DC
            for k in range(1, min(self.config.fourier_terms + 1, len(fft) // 2)):
                magnitude = abs(fft[k])
                phase = np.angle(fft[k])
                frequency = freqs[k]
                
                magnitude_feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_fourier_magnitude_{k}",
                    value=float(magnitude),
                    feature_type=TemporalFeatureType.FOURIER,
                    window_size=len(values),
                    aggregation_type=AggregationType.MEAN,
                    timestamp=data.timestamps[-1],
                    creator_type=data.creator_type,
                    metadata={'fourier_term': k, 'frequency': frequency, 'component': 'magnitude'}
                )
                features.append(magnitude_feature)
                
                phase_feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_fourier_phase_{k}",
                    value=float(phase),
                    feature_type=TemporalFeatureType.FOURIER,
                    window_size=len(values),
                    aggregation_type=AggregationType.MEAN,
                    timestamp=data.timestamps[-1],
                    creator_type=data.creator_type,
                    metadata={'fourier_term': k, 'frequency': frequency, 'component': 'phase'}
                )
                features.append(phase_feature)
        
        except Exception as e:
            logger.error(f"Error generating Fourier features: {e}")
        
        return features
    
    async def _generate_difference_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features de différenciation"""
        features = []
        
        try:
            # Première différence (changement par rapport au point précédent)
            if len(data.values) >= 2:
                first_diff = data.values[-1] - data.values[-2]
                
                first_diff_feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_first_difference",
                    value=float(first_diff),
                    feature_type=TemporalFeatureType.DIFFERENCE,
                    window_size=2,
                    aggregation_type=AggregationType.MEAN,
                    timestamp=data.timestamps[-1],
                    creator_type=data.creator_type,
                    metadata={'difference_order': 1}
                )
                features.append(first_diff_feature)
            
            # Pourcentage de changement
            if len(data.values) >= 2 and data.values[-2] != 0:
                pct_change = (data.values[-1] - data.values[-2]) / abs(data.values[-2])
                
                pct_change_feature = TemporalFeature(
                    feature_name=f"{data.feature_name}_pct_change",
                    value=float(pct_change),
                    feature_type=TemporalFeatureType.DIFFERENCE,
                    window_size=2,
                    aggregation_type=AggregationType.MEAN,
                    timestamp=data.timestamps[-1],
                    creator_type=data.creator_type,
                    metadata={'difference_type': 'percentage'}
                )
                features.append(pct_change_feature)
            
            # Différences sur différentes fenêtres
            for window in [7, 30]:
                if window < len(data.values):
                    window_diff = data.values[-1] - data.values[-window-1]
                    
                    window_diff_feature = TemporalFeature(
                        feature_name=f"{data.feature_name}_diff_{window}d",
                        value=float(window_diff),
                        feature_type=TemporalFeatureType.DIFFERENCE,
                        window_size=window,
                        aggregation_type=AggregationType.MEAN,
                        timestamp=data.timestamps[-1],
                        creator_type=data.creator_type,
                        metadata={'difference_window': window}
                    )
                    features.append(window_diff_feature)
        
        except Exception as e:
            logger.error(f"Error generating difference features: {e}")
        
        return features
    
    async def _generate_creator_specific_features(self, data: TimeSeriesData) -> List[TemporalFeature]:
        """Génère les features spécifiques au type de créateur"""
        features = []
        
        try:
            if not data.creator_type or data.creator_type not in self._creator_patterns:
                return features
            
            creator_config = self._creator_patterns[data.creator_type]
            current_time = data.timestamps[-1]
            
            # Peak hours alignment
            is_peak_hour = 1.0 if current_time.hour in creator_config['peak_hours'] else 0.0
            peak_hour_feature = TemporalFeature(
                feature_name=f"{data.feature_name}_creator_is_peak_hour",
                value=is_peak_hour,
                feature_type=TemporalFeatureType.CYCLICAL,
                window_size=1,
                aggregation_type=AggregationType.MEAN,
                timestamp=current_time,
                creator_type=data.creator_type,
                metadata={'creator_pattern': 'peak_hours'}
            )
            features.append(peak_hour_feature)
            
            # Peak days alignment
            is_peak_day = 1.0 if current_time.weekday() in creator_config['peak_days'] else 0.0
            peak_day_feature = TemporalFeature(
                feature_name=f"{data.feature_name}_creator_is_peak_day",
                value=is_peak_day,
                feature_type=TemporalFeatureType.CYCLICAL,
                window_size=1,
                aggregation_type=AggregationType.MEAN,
                timestamp=current_time,
                creator_type=data.creator_type,
                metadata={'creator_pattern': 'peak_days'}
            )
            features.append(peak_day_feature)
            
            # Weekly pattern multiplier
            weekly_multiplier = creator_config['weekly_pattern'][current_time.weekday()]
            weekly_pattern_feature = TemporalFeature(
                feature_name=f"{data.feature_name}_creator_weekly_multiplier",
                value=float(weekly_multiplier),
                feature_type=TemporalFeatureType.CYCLICAL,
                window_size=7,
                aggregation_type=AggregationType.MEAN,
                timestamp=current_time,
                creator_type=data.creator_type,
                metadata={'creator_pattern': 'weekly_pattern'}
            )
            features.append(weekly_pattern_feature)
            
            # Seasonal boost (approximation)
            month_to_season = {
                12: 'winter', 1: 'winter', 2: 'winter',
                3: 'spring', 4: 'spring', 5: 'spring',
                6: 'summer', 7: 'summer', 8: 'summer',
                9: 'fall', 10: 'fall', 11: 'fall'
            }
            current_season = month_to_season.get(current_time.month, 'spring')
            seasonal_boost = creator_config.get('seasonal_boost', {}).get(current_season, 1.0)
            
            seasonal_feature = TemporalFeature(
                feature_name=f"{data.feature_name}_creator_seasonal_boost",
                value=float(seasonal_boost),
                feature_type=TemporalFeatureType.SEASONALITY,
                window_size=90,  # ~3 months
                aggregation_type=AggregationType.MEAN,
                timestamp=current_time,
                creator_type=data.creator_type,
                metadata={'creator_pattern': 'seasonal_boost', 'season': current_season}
            )
            features.append(seasonal_feature)
        
        except Exception as e:
            logger.error(f"Error generating creator-specific features: {e}")
        
        return features
    
    async def analyze_temporal_patterns(self, time_series_data: TimeSeriesData) -> List[TemporalPattern]:
        """Analyse les patterns temporels dans les données"""
        try:
            patterns = []
            
            if len(time_series_data.values) < self.config.min_data_points:
                return patterns
            
            # Détection de tendance
            trend_pattern = await self._detect_trend_pattern(time_series_data)
            if trend_pattern:
                patterns.append(trend_pattern)
            
            # Détection de saisonnalité
            seasonal_pattern = await self._detect_seasonal_pattern(time_series_data)
            if seasonal_pattern:
                patterns.append(seasonal_pattern)
            
            # Stockage des patterns
            pattern_key = f"{time_series_data.feature_name}_{time_series_data.creator_type}"
            self.patterns[pattern_key] = patterns
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {e}")
            return []
    
    async def _detect_trend_pattern(self, data: TimeSeriesData) -> Optional[TemporalPattern]:
        """Détecte les patterns de tendance"""
        try:
            values = np.array(data.values)
            x = np.arange(len(values))
            
            # Régression linéaire
            slope, intercept = np.polyfit(x, values, 1)
            predicted = slope * x + intercept
            correlation = np.corrcoef(values, predicted)[0, 1]
            
            if abs(correlation) > 0.7:  # Forte corrélation avec tendance linéaire
                pattern = TemporalPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=TemporalFeatureType.TREND,
                    frequency="continuous",
                    amplitude=abs(slope),
                    phase=0.0,
                    confidence=abs(correlation),
                    creator_type=data.creator_type,
                    metadata={
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing',
                        'slope': slope,
                        'intercept': intercept
                    }
                )
                return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting trend pattern: {e}")
            return None
    
    async def _detect_seasonal_pattern(self, data: TimeSeriesData) -> Optional[TemporalPattern]:
        """Détecte les patterns saisonniers"""
        try:
            if len(data.values) < 14:  # Besoin d'au moins 2 semaines
                return None
            
            values = np.array(data.values)
            
            # Test pour périodicité hebdomadaire
            if len(values) >= 21:  # 3 semaines
                weekly_correlation = 0.0
                week_chunks = []
                
                for i in range(0, len(values) - 7, 7):
                    if i + 14 <= len(values):
                        week1 = values[i:i+7]
                        week2 = values[i+7:i+14]
                        if len(week1) == len(week2):
                            corr = np.corrcoef(week1, week2)[0, 1]
                            if not np.isnan(corr):
                                week_chunks.append(corr)
                
                if week_chunks:
                    weekly_correlation = np.mean(week_chunks)
                
                if weekly_correlation > 0.5:  # Pattern hebdomadaire détecté
                    pattern = TemporalPattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type=TemporalFeatureType.SEASONALITY,
                        frequency="weekly",
                        amplitude=np.std(values),
                        phase=0.0,
                        confidence=weekly_correlation,
                        creator_type=data.creator_type,
                        metadata={
                            'seasonality_type': 'weekly',
                            'correlation': weekly_correlation
                        }
                    )
                    return pattern
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting seasonal pattern: {e}")
            return None
    
    async def get_feature_summary(self) -> Dict[str, Any]:
        """Génère un résumé des features temporelles"""
        try:
            total_features = sum(len(features) for features in self.feature_cache.values())
            
            # Compter par type de feature
            feature_type_counts = {}
            for features in self.feature_cache.values():
                for feature in features:
                    feature_type = feature.feature_type.value
                    feature_type_counts[feature_type] = feature_type_counts.get(feature_type, 0) + 1
            
            # Patterns détectés
            total_patterns = sum(len(patterns) for patterns in self.patterns.values())
            
            return {
                'generator_id': self.generator_id,
                'total_features_generated': total_features,
                'feature_type_breakdown': feature_type_counts,
                'total_patterns_detected': total_patterns,
                'cached_feature_sets': len(self.feature_cache),
                'config': {
                    'window_sizes': self.config.default_window_sizes,
                    'lag_periods': self.config.lag_periods,
                    'rolling_windows': self.config.rolling_windows,
                    'fourier_terms': self.config.fourier_terms
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating feature summary: {e}")
            return {}

# Factory functions
def create_temporal_feature_generator(
    window_sizes: Optional[List[int]] = None,
    enable_seasonality: bool = True,
    enable_fourier: bool = True
) -> TemporalFeatureGenerator:
    """Factory pour créer un générateur de features temporelles"""
    config = GeneratorConfig(
        default_window_sizes=window_sizes or [7, 14, 30, 90],
        enable_seasonality=enable_seasonality,
        enable_fourier_features=enable_fourier
    )
    return TemporalFeatureGenerator(config)

async def demo_temporal_feature_generator() -> None:
    """Démo du générateur de features temporelles"""
    generator = create_temporal_feature_generator()
    
    print("📈 Temporal Feature Generator Demo")
    
    # Créer des données de série temporelle simulées
    base_time = datetime.now() - timedelta(days=60)
    timestamps = [base_time + timedelta(days=i) for i in range(60)]
    
    # Simuler des données avec tendance et saisonnalité
    trend = np.linspace(100, 150, 60)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(60) / 7)  # Pattern hebdomadaire
    noise = np.random.normal(0, 5, 60)
    values = trend + seasonal + noise
    
    time_series = TimeSeriesData(
        timestamps=timestamps,
        values=values.tolist(),
        feature_name="engagement_rate",
        creator_type=CreatorType.MUSICIAN
    )
    
    # Générer les features temporelles
    features = await generator.generate_temporal_features(time_series)
    
    print(f"\n📊 Generated {len(features)} temporal features")
    
    # Afficher quelques exemples de features
    feature_types = {}
    for feature in features:
        feature_type = feature.feature_type.value
        if feature_type not in feature_types:
            feature_types[feature_type] = []
        feature_types[feature_type].append(feature)
    
    for feature_type, type_features in feature_types.items():
        print(f"\n{feature_type.upper()} features ({len(type_features)}):")
        for feature in type_features[:3]:  # Afficher 3 exemples
            print(f"  • {feature.feature_name}: {feature.value:.3f}")
    
    # Analyser les patterns
    patterns = await generator.analyze_temporal_patterns(time_series)
    print(f"\n🔍 Detected {len(patterns)} temporal patterns:")
    for pattern in patterns:
        print(f"  • {pattern.pattern_type.value}: {pattern.frequency} (confidence: {pattern.confidence:.3f})")
    
    # Résumé
    summary = await generator.get_feature_summary()
    print(f"\n📈 Feature Summary:")
    print(f"Total Features: {summary['total_features_generated']}")
    print(f"Patterns Detected: {summary['total_patterns_detected']}")

if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(level=logging.INFO)
    
    # Lancer la démo
    asyncio.run(demo_temporal_feature_generator())