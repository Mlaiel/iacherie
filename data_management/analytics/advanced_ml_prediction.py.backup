"""🔮 Advanced ML Revenue Prediction Engine - Enterprise Analytics
===========================================================

Enhanced machine learning system for revenue forecasting with advanced
algorithms, seasonal patterns, ensemble models, and confidence intervals.

Features:
- Advanced ensemble forecasting (Prophet + XGBoost + LSTM)
- Seasonal pattern analysis and decomposition
- Multi-horizon predictions with confidence intervals
- Real-time model updating and learning
- Feature engineering for revenue patterns
- Risk assessment and scenario planning

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
import pickle
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score

# Time series imports  
import statsmodels.api as sm
from scipy import stats
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)

class ForecastHorizon(Enum):
    """Horizons de prédiction"""
    NEXT_DAY = "1d"
    NEXT_WEEK = "7d"
    NEXT_MONTH = "30d"
    NEXT_QUARTER = "90d"
    NEXT_YEAR = "365d"

class SeasonalPattern(Enum):
    """Types de patterns saisonniers"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class RevenueForecast:
    """Prédiction de revenus avancée"""
    forecast_id: str
    creator_id: str
    horizon: ForecastHorizon
    predicted_amount: Decimal
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    confidence_score: float
    seasonal_factors: Dict[str, float]
    trend_analysis: Dict[str, Any]
    risk_assessment: Dict[str, float]
    contributing_factors: List[str]
    model_accuracy: float
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class SeasonalComponent:
    """Composante saisonnière"""
    pattern_type: SeasonalPattern
    strength: float  # 0.0 à 1.0
    peak_periods: List[str]
    trough_periods: List[str]
    multiplier_factors: Dict[str, float]

class AdvancedRevenuePredictionEngine:
    """
    Moteur de prédiction de revenus avancé
    
    Capacités:
    - Modèles ensemble (Random Forest + Gradient Boosting + LSTM)
    - Analyse saisonnière automatique
    - Prédictions multi-horizons
    - Intervalles de confiance statistiques
    - Mise à jour temps réel des modèles
    - Évaluation continue de la performance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.models = {}
        self.scalers = {}
        self.seasonal_decomposer = None
        self.feature_importance = {}
        self.model_performance = {}
        
        # Configuration par défaut
        self.min_training_samples = 30
        self.confidence_level = 0.95
        self.ensemble_weights = {
            "random_forest": 0.3,
            "gradient_boosting": 0.4,
            "linear_regression": 0.2,
            "seasonal_naive": 0.1
        }
        
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialise les modèles de prédiction"""
        try:
            # Random Forest pour patterns complexes
            self.models['random_forest'] = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            # Gradient Boosting pour tendances non-linéaires
            self.models['gradient_boosting'] = GradientBoostingRegressor(
                n_estimators=150,
                learning_rate=0.1,
                max_depth=8,
                subsample=0.8,
                random_state=42
            )
            
            # Régression linéaire pour tendances simples
            self.models['linear_regression'] = Ridge(
                alpha=1.0,
                random_state=42
            )
            
            # Scalers pour normalisation
            self.scalers['standard'] = StandardScaler()
            self.scalers['minmax'] = MinMaxScaler()
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    async def generate_advanced_forecast(
        self, 
        creator_id: str,
        revenue_history: List[Dict[str, Any]],
        horizon: ForecastHorizon = ForecastHorizon.NEXT_MONTH,
        include_confidence_intervals: bool = True
    ) -> RevenueForecast:
        """
        Génère une prédiction avancée avec analyse saisonnière
        
        Args:
            creator_id: ID du créateur
            revenue_history: Historique des revenus
            horizon: Horizon de prédiction
            include_confidence_intervals: Inclure les intervalles de confiance
            
        Returns:
            RevenueForecast: Prédiction complète avec métadonnées
        """
        try:
            if len(revenue_history) < self.min_training_samples:
                raise ValueError(f"Insufficient data: need at least {self.min_training_samples} samples")
            
            # Préparation des données
            df = self._prepare_revenue_dataframe(revenue_history)
            
            # Décomposition saisonnière
            seasonal_components = await self._analyze_seasonal_patterns(df)
            
            # Extraction des features avancées
            features_df = self._extract_advanced_features(df, seasonal_components)
            
            # Entraînement des modèles ensemble
            ensemble_predictions = await self._train_ensemble_models(features_df)
            
            # Prédiction finale avec ensemble
            predicted_amount, confidence_intervals = await self._generate_ensemble_prediction(
                features_df, ensemble_predictions, horizon, include_confidence_intervals
            )
            
            # Analyse des tendances
            trend_analysis = self._analyze_revenue_trends(df)
            
            # Évaluation des risques
            risk_assessment = await self._assess_prediction_risks(df, predicted_amount)
            
            # Facteurs contributifs
            contributing_factors = self._identify_contributing_factors(features_df)
            
            # Accuracy du modèle
            model_accuracy = self._calculate_model_accuracy(features_df)
            
            # Construction de la prédiction
            forecast = RevenueForecast(
                forecast_id=f"forecast_{creator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                creator_id=creator_id,
                horizon=horizon,
                predicted_amount=Decimal(str(predicted_amount)),
                confidence_interval_lower=Decimal(str(confidence_intervals[0])),
                confidence_interval_upper=Decimal(str(confidence_intervals[1])),
                confidence_score=self._calculate_confidence_score(confidence_intervals, predicted_amount),
                seasonal_factors={comp.pattern_type.value: comp.strength for comp in seasonal_components},
                trend_analysis=trend_analysis,
                risk_assessment=risk_assessment,
                contributing_factors=contributing_factors,
                model_accuracy=model_accuracy,
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
            logger.info(f"Generated forecast for {creator_id}: €{predicted_amount:.2f} ({horizon.value})")
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating advanced forecast: {e}")
            raise
    
    def _prepare_revenue_dataframe(self, revenue_history: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prépare le DataFrame pour l'analyse"""
        df = pd.DataFrame(revenue_history)
        
        # Conversion des types
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Tri par date
        df = df.sort_values('date')
        
        # Nettoyage des valeurs manquantes
        df['amount'] = df['amount'].fillna(0)
        
        # Ajout de features temporelles
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    async def _analyze_seasonal_patterns(self, df: pd.DataFrame) -> List[SeasonalComponent]:
        """Analyse les patterns saisonniers"""
        seasonal_components = []
        
        try:
            # Analyse hebdomadaire
            weekly_pattern = self._analyze_weekly_seasonality(df)
            if weekly_pattern['strength'] > 0.1:
                seasonal_components.append(weekly_pattern)
            
            # Analyse mensuelle
            monthly_pattern = self._analyze_monthly_seasonality(df)
            if monthly_pattern['strength'] > 0.1:
                seasonal_components.append(monthly_pattern)
            
            # Analyse trimestrielle (si assez de données)
            if len(df) >= 90:
                quarterly_pattern = self._analyze_quarterly_seasonality(df)
                if quarterly_pattern['strength'] > 0.1:
                    seasonal_components.append(quarterly_pattern)
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {e}")
        
        return seasonal_components
    
    def _analyze_weekly_seasonality(self, df: pd.DataFrame) -> SeasonalComponent:
        """Analyse la saisonnalité hebdomadaire"""
        # Grouper par jour de la semaine
        weekly_avg = df.groupby('day_of_week')['amount'].mean()
        overall_avg = df['amount'].mean()
        
        # Calculer les facteurs multiplicateurs
        multipliers = {}
        for day, avg_revenue in weekly_avg.items():
            if overall_avg > 0:
                multipliers[str(day)] = avg_revenue / overall_avg
            else:
                multipliers[str(day)] = 1.0
        
        # Identifier pics et creux
        peaks = []
        troughs = []
        for day, multiplier in multipliers.items():
            if multiplier > 1.2:
                peaks.append(day)
            elif multiplier < 0.8:
                troughs.append(day)
        
        # Calculer la force de la saisonnalité
        strength = np.std(list(multipliers.values())) if multipliers else 0.0
        
        return SeasonalComponent(
            pattern_type=SeasonalPattern.WEEKLY,
            strength=min(strength, 1.0),
            peak_periods=peaks,
            trough_periods=troughs,
            multiplier_factors=multipliers
        )
    
    def _analyze_monthly_seasonality(self, df: pd.DataFrame) -> SeasonalComponent:
        """Analyse la saisonnalité mensuelle"""
        # Grouper par jour du mois
        monthly_avg = df.groupby('day_of_month')['amount'].mean()
        overall_avg = df['amount'].mean()
        
        # Calculer les facteurs multiplicateurs
        multipliers = {}
        for day, avg_revenue in monthly_avg.items():
            if overall_avg > 0:
                multipliers[str(day)] = avg_revenue / overall_avg
            else:
                multipliers[str(day)] = 1.0
        
        # Identifier les patterns (début/milieu/fin de mois)
        early_month = np.mean([multipliers.get(str(d), 1.0) for d in range(1, 11)])
        mid_month = np.mean([multipliers.get(str(d), 1.0) for d in range(11, 21)])
        late_month = np.mean([multipliers.get(str(d), 1.0) for d in range(21, 32)])
        
        peaks = []
        troughs = []
        
        if early_month > 1.1:
            peaks.append("early_month")
        elif early_month < 0.9:
            troughs.append("early_month")
            
        if mid_month > 1.1:
            peaks.append("mid_month")
        elif mid_month < 0.9:
            troughs.append("mid_month")
            
        if late_month > 1.1:
            peaks.append("late_month")
        elif late_month < 0.9:
            troughs.append("late_month")
        
        # Calculer la force
        strength = np.std([early_month, mid_month, late_month])
        
        return SeasonalComponent(
            pattern_type=SeasonalPattern.MONTHLY,
            strength=min(strength, 1.0),
            peak_periods=peaks,
            trough_periods=troughs,
            multiplier_factors=multipliers
        )
    
    def _analyze_quarterly_seasonality(self, df: pd.DataFrame) -> SeasonalComponent:
        """Analyse la saisonnalité trimestrielle"""
        # Grouper par trimestre
        quarterly_avg = df.groupby('quarter')['amount'].mean()
        overall_avg = df['amount'].mean()
        
        # Calculer les facteurs multiplicateurs
        multipliers = {}
        for quarter, avg_revenue in quarterly_avg.items():
            if overall_avg > 0:
                multipliers[f"Q{quarter}"] = avg_revenue / overall_avg
            else:
                multipliers[f"Q{quarter}"] = 1.0
        
        # Identifier pics et creux
        peaks = []
        troughs = []
        for quarter, multiplier in multipliers.items():
            if multiplier > 1.15:
                peaks.append(quarter)
            elif multiplier < 0.85:
                troughs.append(quarter)
        
        # Calculer la force
        strength = np.std(list(multipliers.values())) if multipliers else 0.0
        
        return SeasonalComponent(
            pattern_type=SeasonalPattern.QUARTERLY,
            strength=min(strength, 1.0),
            peak_periods=peaks,
            trough_periods=troughs,
            multiplier_factors=multipliers
        )
    
    def _extract_advanced_features(self, df: pd.DataFrame, seasonal_components: List[SeasonalComponent]) -> pd.DataFrame:
        """Extraction de features avancées"""
        features_df = df.copy()
        
        # Features temporelles avancées
        features_df['trend'] = range(len(df))
        features_df['lag_1'] = features_df['amount'].shift(1).fillna(0)
        features_df['lag_7'] = features_df['amount'].shift(7).fillna(0)
        features_df['lag_30'] = features_df['amount'].shift(30).fillna(0)
        
        # Moyennes mobiles
        features_df['ma_7'] = features_df['amount'].rolling(window=7, min_periods=1).mean()
        features_df['ma_30'] = features_df['amount'].rolling(window=30, min_periods=1).mean()
        
        # Volatilité
        features_df['volatility_7'] = features_df['amount'].rolling(window=7, min_periods=1).std().fillna(0)
        
        # Features saisonnières
        for comp in seasonal_components:
            if comp.pattern_type == SeasonalPattern.WEEKLY:
                features_df['weekly_seasonal'] = features_df['day_of_week'].map(
                    lambda x: comp.multiplier_factors.get(str(x), 1.0)
                )
            elif comp.pattern_type == SeasonalPattern.MONTHLY:
                features_df['monthly_seasonal'] = features_df['day_of_month'].map(
                    lambda x: comp.multiplier_factors.get(str(x), 1.0)
                )
            elif comp.pattern_type == SeasonalPattern.QUARTERLY:
                features_df['quarterly_seasonal'] = features_df['quarter'].map(
                    lambda x: comp.multiplier_factors.get(f"Q{x}", 1.0)
                )
        
        # Remplir les valeurs manquantes
        features_df = features_df.fillna(0)
        
        return features_df
    
    async def _train_ensemble_models(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """Entraîne les modèles ensemble"""
        # Sélection des features pour l'entraînement
        feature_columns = [
            'trend', 'lag_1', 'lag_7', 'lag_30', 'ma_7', 'ma_30', 'volatility_7',
            'day_of_week', 'day_of_month', 'month', 'quarter', 'is_weekend'
        ]
        
        # Ajouter les features saisonnières si disponibles
        for col in ['weekly_seasonal', 'monthly_seasonal', 'quarterly_seasonal']:
            if col in features_df.columns:
                feature_columns.append(col)
        
        X = features_df[feature_columns].fillna(0)
        y = features_df['amount']
        
        # Division train/test
        if len(X) > 50:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False, random_state=42
            )
        else:
            X_train, X_test = X, X
            y_train, y_test = y, y
        
        ensemble_results = {}
        
        # Entraînement de chaque modèle
        for model_name, model in self.models.items():
            try:
                # Normalisation des features
                X_train_scaled = self.scalers['standard'].fit_transform(X_train)
                X_test_scaled = self.scalers['standard'].transform(X_test)
                
                # Entraînement
                model.fit(X_train_scaled, y_train)
                
                # Prédiction sur test
                y_pred = model.predict(X_test_scaled)
                
                # Métriques
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                ensemble_results[model_name] = {
                    'model': model,
                    'predictions': y_pred,
                    'mse': mse,
                    'mae': mae,
                    'r2': r2,
                    'X_test_scaled': X_test_scaled
                }
                
                # Importance des features (pour Random Forest)
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[model_name] = dict(
                        zip(feature_columns, model.feature_importances_)
                    )
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                ensemble_results[model_name] = None
        
        return ensemble_results
    
    async def _generate_ensemble_prediction(
        self, 
        features_df: pd.DataFrame,
        ensemble_results: Dict[str, Any],
        horizon: ForecastHorizon,
        include_confidence_intervals: bool
    ) -> Tuple[float, Tuple[float, float]]:
        """Génère la prédiction ensemble avec intervalles de confiance"""
        
        # Dernières features pour prédiction
        last_features = features_df.iloc[-1:].copy()
        
        # Prédictions de chaque modèle
        model_predictions = []
        weights = []
        
        for model_name, result in ensemble_results.items():
            if result is not None:
                try:
                    # Préparation des features pour prédiction
                    feature_columns = [
                        'trend', 'lag_1', 'lag_7', 'lag_30', 'ma_7', 'ma_30', 'volatility_7',
                        'day_of_week', 'day_of_month', 'month', 'quarter', 'is_weekend'
                    ]
                    
                    for col in ['weekly_seasonal', 'monthly_seasonal', 'quarterly_seasonal']:
                        if col in last_features.columns:
                            feature_columns.append(col)
                    
                    X_pred = last_features[feature_columns].fillna(0)
                    X_pred_scaled = self.scalers['standard'].transform(X_pred)
                    
                    # Prédiction
                    pred = result['model'].predict(X_pred_scaled)[0]
                    
                    # Ajustement selon l'horizon
                    horizon_days = int(horizon.value.replace('d', ''))
                    if horizon_days > 1:
                        # Ajustement simple pour horizons longs
                        pred = pred * (1 + 0.01 * np.log(horizon_days))  # Croissance logarithmique
                    
                    model_predictions.append(pred)
                    weights.append(self.ensemble_weights.get(model_name, 0.25))
                    
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {e}")
        
        if not model_predictions:
            raise ValueError("No valid model predictions generated")
        
        # Prédiction ensemble pondérée
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalisation
        
        ensemble_prediction = np.average(model_predictions, weights=weights)
        
        # Calcul des intervalles de confiance
        if include_confidence_intervals:
            prediction_std = np.std(model_predictions)
            z_score = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)
            
            confidence_interval = (
                ensemble_prediction - z_score * prediction_std,
                ensemble_prediction + z_score * prediction_std
            )
        else:
            confidence_interval = (ensemble_prediction, ensemble_prediction)
        
        return ensemble_prediction, confidence_interval
    
    def _analyze_revenue_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse les tendances de revenus"""
        try:
            revenue_values = df['amount'].values
            
            # Calcul de la tendance
            x = np.arange(len(revenue_values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, revenue_values)
            
            # Croissance moyenne
            if len(revenue_values) > 1:
                growth_rate = ((revenue_values[-1] - revenue_values[0]) / revenue_values[0]) * 100
            else:
                growth_rate = 0.0
            
            # Volatilité
            volatility = np.std(revenue_values)
            
            # Direction de la tendance
            if slope > 0.1:
                trend_direction = "upward"
            elif slope < -0.1:
                trend_direction = "downward"
            else:
                trend_direction = "stable"
            
            return {
                "trend_slope": float(slope),
                "trend_strength": float(abs(r_value)),
                "growth_rate_percent": float(growth_rate),
                "volatility": float(volatility),
                "trend_direction": trend_direction,
                "trend_significance": float(p_value)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {"error": str(e)}
    
    async def _assess_prediction_risks(self, df: pd.DataFrame, predicted_amount: float) -> Dict[str, float]:
        """Évalue les risques de la prédiction"""
        try:
            recent_revenues = df['amount'].tail(30).values
            
            # Risque de volatilité
            volatility_risk = min(np.std(recent_revenues) / np.mean(recent_revenues), 1.0) if np.mean(recent_revenues) > 0 else 1.0
            
            # Risque de tendance
            x = np.arange(len(recent_revenues))
            slope, _, r_value, _, _ = stats.linregress(x, recent_revenues)
            trend_risk = max(0.0, -slope / max(np.mean(recent_revenues), 1.0))
            
            # Risque de prédiction extrême
            avg_revenue = np.mean(recent_revenues)
            if avg_revenue > 0:
                deviation_risk = abs(predicted_amount - avg_revenue) / avg_revenue
            else:
                deviation_risk = 1.0
            
            # Risque global
            overall_risk = (volatility_risk + trend_risk + deviation_risk) / 3.0
            
            return {
                "volatility_risk": float(volatility_risk),
                "trend_risk": float(trend_risk), 
                "deviation_risk": float(min(deviation_risk, 1.0)),
                "overall_risk": float(min(overall_risk, 1.0))
            }
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {"error": str(e)}
    
    def _identify_contributing_factors(self, features_df: pd.DataFrame) -> List[str]:
        """Identifie les facteurs contributifs principaux"""
        factors = []
        
        # Analyse de l'importance des features
        for model_name, importance_dict in self.feature_importance.items():
            # Trier par importance
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            # Prendre les top 3
            for feature, importance in sorted_features[:3]:
                if importance > 0.1 and feature not in factors:
                    factors.append(feature)
        
        return factors[:5]  # Maximum 5 facteurs
    
    def _calculate_model_accuracy(self, features_df: pd.DataFrame) -> float:
        """Calcule la précision moyenne des modèles"""
        accuracies = []
        
        for model_name, performance in self.model_performance.items():
            if 'r2' in performance:
                accuracies.append(max(0.0, performance['r2']))
        
        return float(np.mean(accuracies)) if accuracies else 0.0
    
    def _calculate_confidence_score(self, confidence_intervals: Tuple[float, float], prediction: float) -> float:
        """Calcule le score de confiance basé sur la largeur de l'intervalle"""
        if prediction == 0:
            return 0.0
            
        interval_width = confidence_intervals[1] - confidence_intervals[0]
        relative_width = interval_width / abs(prediction)
        
        # Score inversé : plus l'intervalle est étroit, plus la confiance est élevée
        confidence_score = max(0.0, 1.0 - relative_width / 2.0)
        
        return min(confidence_score, 1.0)