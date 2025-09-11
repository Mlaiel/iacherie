"""Model Convergence Analyzer for Ainflue ML Platform

Advanced model convergence analysis and early stopping strategies with creator-specific
convergence patterns and intelligent stopping criteria.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import math
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from collections import deque, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import savgol_filter
import warnings

logger = logging.getLogger(__name__)


class ConvergenceStatus(Enum):
    """Convergence status enumeration."""
    CONVERGING = "converging"
    CONVERGED = "converged"
    DIVERGING = "diverging"
    OSCILLATING = "oscillating"
    STAGNANT = "stagnant"
    OVERFITTING = "overfitting"
    UNDERFITTING = "underfitting"
    UNKNOWN = "unknown"


class StoppingCriterion(Enum):
    """Early stopping criterion enumeration."""
    VALIDATION_LOSS = "validation_loss"
    VALIDATION_ACCURACY = "validation_accuracy"
    TRAINING_LOSS = "training_loss"
    GRADIENT_NORM = "gradient_norm"
    LEARNING_PLATEAU = "learning_plateau"
    CREATOR_ENGAGEMENT = "creator_engagement"
    COMBINED_SCORE = "combined_score"


@dataclass
class ConvergenceConfig:
    """Configuration for convergence analysis."""
    # Early stopping settings
    patience: int = 20
    min_delta: float = 1e-4
    restore_best_weights: bool = True
    
    # Convergence detection
    window_size: int = 10
    smoothing_factor: float = 0.1
    convergence_threshold: float = 1e-5
    
    # Overfitting detection
    overfitting_threshold: float = 0.1  # validation loss increase threshold
    overfitting_patience: int = 5
    
    # Oscillation detection
    oscillation_threshold: float = 0.05
    oscillation_min_cycles: int = 3
    
    # Creator-specific settings
    creator_adaptive: bool = True
    engagement_weight: float = 0.3
    quality_weight: float = 0.7
    
    # Advanced stopping criteria
    use_combined_criteria: bool = True
    gradient_threshold: float = 1e-6
    learning_plateau_threshold: float = 1e-7
    
    # Monitoring settings
    save_convergence_plots: bool = True
    plot_update_frequency: int = 10
    verbose_logging: bool = True


@dataclass
class ConvergencePoint:
    """Data point for convergence analysis."""
    epoch: int
    batch: int
    timestamp: datetime
    training_loss: float
    validation_loss: Optional[float] = None
    validation_accuracy: Optional[float] = None
    gradient_norm: Optional[float] = None
    learning_rate: float = 0.001
    creator_id: Optional[str] = None
    engagement_score: Optional[float] = None
    quality_score: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ConvergenceAnalysis:
    """Results of convergence analysis."""
    status: ConvergenceStatus
    confidence: float
    epochs_analyzed: int
    best_epoch: int
    best_score: float
    current_score: float
    trend_slope: float
    volatility: float
    plateau_detected: bool
    overfitting_detected: bool
    oscillation_detected: bool
    early_stop_triggered: bool
    recommendations: List[str]
    creator_specific_insights: Dict[str, Any] = field(default_factory=dict)


class TrendAnalyzer:
    """Analyzes trends in training metrics."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
    
    def analyze_trend(self, values: List[float]) -> Dict[str, float]:
        """Analyze trend in a series of values."""
        if len(values) < 3:
            return {
                'slope': 0.0,
                'r_squared': 0.0,
                'volatility': 0.0,
                'direction': 0.0
            }
        
        # Calculate linear trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Calculate volatility (coefficient of variation)
        volatility = np.std(values) / (np.mean(values) + 1e-8)
        
        # Determine direction
        recent_window = min(self.window_size, len(values))
        recent_slope = np.polyfit(
            np.arange(recent_window), 
            values[-recent_window:], 
            1
        )[0]
        
        return {
            'slope': slope,
            'r_squared': r_value ** 2,
            'volatility': volatility,
            'direction': recent_slope,
            'p_value': p_value,
            'std_error': std_err
        }
    
    def detect_plateau(
        self, 
        values: List[float], 
        threshold: float = 1e-5,
        min_length: int = 5
    ) -> bool:
        """Detect if values have plateaued."""
        if len(values) < min_length:
            return False
        
        recent_values = values[-min_length:]
        
        # Check if the variance is below threshold
        variance = np.var(recent_values)
        return variance < threshold
    
    def detect_oscillation(
        self,
        values: List[float],
        threshold: float = 0.05,
        min_cycles: int = 3
    ) -> bool:
        """Detect oscillating behavior."""
        if len(values) < min_cycles * 4:  # Need at least min_cycles complete cycles
            return False
        
        # Find peaks and valleys
        diffs = np.diff(values)
        sign_changes = np.diff(np.sign(diffs))
        
        # Count direction changes
        direction_changes = np.sum(np.abs(sign_changes) > 1)
        
        # Check if there are enough changes and amplitude is significant
        if direction_changes >= min_cycles * 2:
            amplitude = np.max(values[-len(values)//2:]) - np.min(values[-len(values)//2:])
            mean_value = np.mean(values[-len(values)//2:])
            relative_amplitude = amplitude / (mean_value + 1e-8)
            
            return relative_amplitude > threshold
        
        return False
    
    def smooth_values(self, values: List[float], window_length: int = 5) -> List[float]:
        """Apply smoothing to values."""
        if len(values) < window_length:
            return values
        
        # Use Savitzky-Golay filter for smoothing
        try:
            if window_length % 2 == 0:
                window_length += 1  # Must be odd
            
            smoothed = savgol_filter(values, window_length, 2)
            return smoothed.tolist()
        except:
            # Fallback to simple moving average
            smoothed = []
            for i in range(len(values)):
                start_idx = max(0, i - window_length // 2)
                end_idx = min(len(values), i + window_length // 2 + 1)
                smoothed.append(np.mean(values[start_idx:end_idx]))
            return smoothed


class OverfittingDetector:
    """Detects overfitting patterns in training."""
    
    def __init__(self, config: ConvergenceConfig):
        self.config = config
        self.train_losses = deque(maxlen=100)
        self.val_losses = deque(maxlen=100)
        
    def add_point(self, train_loss: float, val_loss: Optional[float]):
        """Add a new data point."""
        self.train_losses.append(train_loss)
        if val_loss is not None:
            self.val_losses.append(val_loss)
    
    def detect_overfitting(self) -> Tuple[bool, float]:
        """Detect overfitting based on train/validation loss divergence."""
        if len(self.train_losses) < 5 or len(self.val_losses) < 5:
            return False, 0.0
        
        # Calculate recent trends
        recent_window = min(10, len(self.train_losses))
        
        recent_train = list(self.train_losses)[-recent_window:]
        recent_val = list(self.val_losses)[-recent_window:]
        
        if len(recent_val) != len(recent_train):
            return False, 0.0
        
        # Calculate slopes
        train_slope = np.polyfit(np.arange(len(recent_train)), recent_train, 1)[0]
        val_slope = np.polyfit(np.arange(len(recent_val)), recent_val, 1)[0]
        
        # Overfitting detected if training loss decreases while validation increases
        divergence = val_slope - train_slope
        
        overfitting_detected = (
            train_slope < -self.config.convergence_threshold and
            val_slope > self.config.overfitting_threshold and
            divergence > self.config.overfitting_threshold
        )
        
        return overfitting_detected, divergence
    
    def calculate_generalization_gap(self) -> float:
        """Calculate the generalization gap."""
        if not self.train_losses or not self.val_losses:
            return 0.0
        
        recent_train = np.mean(list(self.train_losses)[-5:])
        recent_val = np.mean(list(self.val_losses)[-5:])
        
        return recent_val - recent_train


class CreatorConvergenceProfiler:
    """Profiles convergence patterns for different creator types."""
    
    def __init__(self):
        self.creator_profiles = defaultdict(lambda: {
            'typical_convergence_epochs': [],
            'best_stopping_criteria': [],
            'overfitting_tendency': 0.0,
            'volatility_patterns': []
        })
    
    def update_profile(
        self,
        creator_id: str,
        creator_type: str,
        analysis: ConvergenceAnalysis
    ):
        """Update creator convergence profile."""
        profile = self.creator_profiles[creator_type]
        
        # Update convergence epochs
        if analysis.best_epoch > 0:
            profile['typical_convergence_epochs'].append(analysis.best_epoch)
            
            # Keep only recent history
            if len(profile['typical_convergence_epochs']) > 20:
                profile['typical_convergence_epochs'] = profile['typical_convergence_epochs'][-10:]
        
        # Update overfitting tendency
        if analysis.overfitting_detected:
            profile['overfitting_tendency'] = min(1.0, profile['overfitting_tendency'] + 0.1)
        else:
            profile['overfitting_tendency'] = max(0.0, profile['overfitting_tendency'] - 0.05)
        
        # Update volatility patterns
        profile['volatility_patterns'].append(analysis.volatility)
        if len(profile['volatility_patterns']) > 20:
            profile['volatility_patterns'] = profile['volatility_patterns'][-10:]
    
    def get_creator_recommendations(
        self,
        creator_type: str,
        current_epoch: int
    ) -> List[str]:
        """Get creator-specific recommendations."""
        recommendations = []
        profile = self.creator_profiles.get(creator_type, {})
        
        # Convergence timing recommendations
        typical_epochs = profile.get('typical_convergence_epochs', [])
        if typical_epochs:
            avg_epochs = np.mean(typical_epochs)
            if current_epoch > avg_epochs * 1.5:
                recommendations.append(
                    f"Consider stopping - {creator_type} models typically converge around epoch {int(avg_epochs)}"
                )
        
        # Overfitting recommendations
        overfitting_tendency = profile.get('overfitting_tendency', 0.0)
        if overfitting_tendency > 0.7:
            recommendations.append(
                f"High overfitting risk for {creator_type} - consider stronger regularization"
            )
        
        # Volatility recommendations
        volatility_patterns = profile.get('volatility_patterns', [])
        if volatility_patterns and np.mean(volatility_patterns) > 0.3:
            recommendations.append(
                f"{creator_type} models tend to be volatile - consider learning rate scheduling"
            )
        
        return recommendations
    
    def get_optimal_patience(self, creator_type: str, default_patience: int) -> int:
        """Get optimal patience for creator type."""
        profile = self.creator_profiles.get(creator_type, {})
        typical_epochs = profile.get('typical_convergence_epochs', [])
        
        if not typical_epochs:
            return default_patience
        
        # Set patience to be a fraction of typical convergence time
        avg_epochs = np.mean(typical_epochs)
        optimal_patience = max(5, int(avg_epochs * 0.3))
        
        return min(optimal_patience, default_patience * 2)


class EarlyStoppingManager:
    """Manages early stopping decisions with multiple criteria."""
    
    def __init__(self, config: ConvergenceConfig):
        self.config = config
        self.best_score = float('inf')
        self.best_epoch = 0
        self.patience_counter = 0
        self.stopped = False
        self.best_weights = None
        
        # Multi-criteria tracking
        self.criteria_scores = defaultdict(list)
        self.criteria_patience = defaultdict(int)
        
    def check_early_stopping(
        self,
        epoch: int,
        convergence_point: ConvergencePoint,
        model: Optional[nn.Module] = None
    ) -> Tuple[bool, str]:
        """Check if early stopping should be triggered."""
        if self.stopped:
            return True, "Already stopped"
        
        # Primary criterion (validation loss)
        primary_score = convergence_point.validation_loss
        if primary_score is None:
            primary_score = convergence_point.training_loss
        
        should_stop = False
        stop_reason = ""
        
        # Check primary criterion
        if primary_score < self.best_score - self.config.min_delta:
            self.best_score = primary_score
            self.best_epoch = epoch
            self.patience_counter = 0
            
            # Save best weights
            if model is not None and self.config.restore_best_weights:
                self.best_weights = {name: param.clone() for name, param in model.named_parameters()}
        else:
            self.patience_counter += 1
        
        # Check if patience exceeded
        if self.patience_counter >= self.config.patience:
            should_stop = True
            stop_reason = f"Patience exceeded ({self.config.patience} epochs without improvement)"
        
        # Additional stopping criteria
        if self.config.use_combined_criteria:
            additional_stop, additional_reason = self._check_additional_criteria(convergence_point)
            if additional_stop:
                should_stop = True
                stop_reason = additional_reason
        
        if should_stop:
            self.stopped = True
            
            # Restore best weights if requested
            if model is not None and self.config.restore_best_weights and self.best_weights:
                for name, param in model.named_parameters():
                    if name in self.best_weights:
                        param.data.copy_(self.best_weights[name])
        
        return should_stop, stop_reason
    
    def _check_additional_criteria(self, point: ConvergencePoint) -> Tuple[bool, str]:
        """Check additional stopping criteria."""
        # Gradient norm criterion
        if point.gradient_norm is not None:
            if point.gradient_norm < self.config.gradient_threshold:
                return True, f"Gradient norm below threshold ({self.config.gradient_threshold})"
        
        # Learning plateau criterion
        if len(self.criteria_scores['training_loss']) > 10:
            recent_losses = self.criteria_scores['training_loss'][-10:]
            loss_variance = np.var(recent_losses)
            if loss_variance < self.config.learning_plateau_threshold:
                return True, f"Learning plateau detected (variance: {loss_variance:.2e})"
        
        # Creator engagement criterion
        if point.engagement_score is not None and point.engagement_score > 0.95:
            return True, "High creator engagement achieved"
        
        return False, ""
    
    def get_stopping_statistics(self) -> Dict[str, Any]:
        """Get early stopping statistics."""
        return {
            'best_score': self.best_score,
            'best_epoch': self.best_epoch,
            'patience_counter': self.patience_counter,
            'stopped': self.stopped,
            'total_patience': self.config.patience
        }


class ModelConvergenceAnalyzer:
    """Main convergence analyzer for ML models."""
    
    def __init__(self, config: Optional[ConvergenceConfig] = None):
        self.config = config or ConvergenceConfig()
        
        # Components
        self.trend_analyzer = TrendAnalyzer(self.config.window_size)
        self.overfitting_detector = OverfittingDetector(self.config)
        self.creator_profiler = CreatorConvergenceProfiler()
        self.early_stopping = EarlyStoppingManager(self.config)
        
        # Data storage
        self.convergence_history: List[ConvergencePoint] = []
        self.analysis_history: List[ConvergenceAnalysis] = []
        
        # State tracking
        self.current_epoch = 0
        self.analysis_active = False
        
        logger.info("Initialized ModelConvergenceAnalyzer")
    
    async def start_analysis(self):
        """Start convergence analysis."""
        self.analysis_active = True
        self.convergence_history.clear()
        self.analysis_history.clear()
        logger.info("Started convergence analysis")
    
    async def stop_analysis(self):
        """Stop convergence analysis."""
        self.analysis_active = False
        logger.info("Stopped convergence analysis")
    
    async def add_convergence_point(
        self,
        epoch: int,
        batch: int,
        training_loss: float,
        validation_loss: Optional[float] = None,
        validation_accuracy: Optional[float] = None,
        gradient_norm: Optional[float] = None,
        learning_rate: float = 0.001,
        creator_id: Optional[str] = None,
        engagement_score: Optional[float] = None,
        quality_score: Optional[float] = None,
        **custom_metrics
    ) -> ConvergencePoint:
        """Add a new convergence data point."""
        point = ConvergencePoint(
            epoch=epoch,
            batch=batch,
            timestamp=datetime.now(),
            training_loss=training_loss,
            validation_loss=validation_loss,
            validation_accuracy=validation_accuracy,
            gradient_norm=gradient_norm,
            learning_rate=learning_rate,
            creator_id=creator_id,
            engagement_score=engagement_score,
            quality_score=quality_score,
            custom_metrics=custom_metrics
        )
        
        if self.analysis_active:
            self.convergence_history.append(point)
            
            # Update overfitting detector
            self.overfitting_detector.add_point(training_loss, validation_loss)
            
            # Limit history size
            if len(self.convergence_history) > 1000:
                self.convergence_history = self.convergence_history[-500:]
        
        self.current_epoch = max(self.current_epoch, epoch)
        
        return point
    
    async def analyze_convergence(
        self,
        creator_type: Optional[str] = None
    ) -> ConvergenceAnalysis:
        """Perform comprehensive convergence analysis."""
        if len(self.convergence_history) < 3:
            return ConvergenceAnalysis(
                status=ConvergenceStatus.UNKNOWN,
                confidence=0.0,
                epochs_analyzed=len(self.convergence_history),
                best_epoch=0,
                best_score=float('inf'),
                current_score=float('inf'),
                trend_slope=0.0,
                volatility=0.0,
                plateau_detected=False,
                overfitting_detected=False,
                oscillation_detected=False,
                early_stop_triggered=False,
                recommendations=["Need more data points for analysis"]
            )
        
        # Extract metrics for analysis
        training_losses = [p.training_loss for p in self.convergence_history]
        validation_losses = [p.validation_loss for p in self.convergence_history if p.validation_loss is not None]
        
        # Primary analysis on validation loss if available, otherwise training loss
        primary_losses = validation_losses if validation_losses else training_losses
        
        # Trend analysis
        trend_stats = self.trend_analyzer.analyze_trend(primary_losses)
        
        # Detect patterns
        plateau_detected = self.trend_analyzer.detect_plateau(
            primary_losses, 
            self.config.convergence_threshold
        )
        
        oscillation_detected = self.trend_analyzer.detect_oscillation(
            primary_losses,
            self.config.oscillation_threshold,
            self.config.oscillation_min_cycles
        )
        
        # Overfitting detection
        overfitting_detected, divergence = self.overfitting_detector.detect_overfitting()
        
        # Determine convergence status
        status = self._determine_convergence_status(
            trend_stats, plateau_detected, oscillation_detected, overfitting_detected
        )
        
        # Find best epoch and score
        best_idx = np.argmin(primary_losses)
        best_epoch = self.convergence_history[best_idx].epoch
        best_score = primary_losses[best_idx]
        current_score = primary_losses[-1]
        
        # Calculate confidence
        confidence = self._calculate_confidence(trend_stats, len(primary_losses))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            status, trend_stats, plateau_detected, overfitting_detected, creator_type
        )
        
        # Creator-specific insights
        creator_insights = {}
        if creator_type:
            creator_insights = self._generate_creator_insights(creator_type)
        
        analysis = ConvergenceAnalysis(
            status=status,
            confidence=confidence,
            epochs_analyzed=len(self.convergence_history),
            best_epoch=best_epoch,
            best_score=best_score,
            current_score=current_score,
            trend_slope=trend_stats['slope'],
            volatility=trend_stats['volatility'],
            plateau_detected=plateau_detected,
            overfitting_detected=overfitting_detected,
            oscillation_detected=oscillation_detected,
            early_stop_triggered=self.early_stopping.stopped,
            recommendations=recommendations,
            creator_specific_insights=creator_insights
        )
        
        self.analysis_history.append(analysis)
        
        # Update creator profile
        if creator_type and hasattr(self.convergence_history[-1], 'creator_id'):
            self.creator_profiler.update_profile(
                self.convergence_history[-1].creator_id or "unknown",
                creator_type,
                analysis
            )
        
        return analysis
    
    def _determine_convergence_status(
        self,
        trend_stats: Dict[str, float],
        plateau_detected: bool,
        oscillation_detected: bool,
        overfitting_detected: bool
    ) -> ConvergenceStatus:
        """Determine overall convergence status."""
        if overfitting_detected:
            return ConvergenceStatus.OVERFITTING
        
        if oscillation_detected:
            return ConvergenceStatus.OSCILLATING
        
        if plateau_detected:
            if abs(trend_stats['slope']) < self.config.convergence_threshold:
                return ConvergenceStatus.CONVERGED
            else:
                return ConvergenceStatus.STAGNANT
        
        # Check trend direction
        if trend_stats['slope'] < -self.config.convergence_threshold:
            return ConvergenceStatus.CONVERGING
        elif trend_stats['slope'] > self.config.convergence_threshold:
            return ConvergenceStatus.DIVERGING
        else:
            return ConvergenceStatus.CONVERGING
    
    def _calculate_confidence(self, trend_stats: Dict[str, float], data_points: int) -> float:
        """Calculate confidence in convergence analysis."""
        # Base confidence on R-squared and number of data points
        r_squared_confidence = trend_stats['r_squared']
        sample_size_confidence = min(1.0, data_points / 50.0)  # Full confidence at 50+ points
        
        # Combine confidences
        confidence = (r_squared_confidence + sample_size_confidence) / 2.0
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_recommendations(
        self,
        status: ConvergenceStatus,
        trend_stats: Dict[str, float],
        plateau_detected: bool,
        overfitting_detected: bool,
        creator_type: Optional[str] = None
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if status == ConvergenceStatus.OVERFITTING:
            recommendations.extend([
                "Overfitting detected - consider reducing model complexity",
                "Implement stronger regularization (dropout, weight decay)",
                "Reduce learning rate or implement early stopping",
                "Increase training data or use data augmentation"
            ])
        
        elif status == ConvergenceStatus.DIVERGING:
            recommendations.extend([
                "Model is diverging - reduce learning rate significantly",
                "Check gradient clipping and ensure stable optimization",
                "Verify data preprocessing and model architecture"
            ])
        
        elif status == ConvergenceStatus.OSCILLATING:
            recommendations.extend([
                "Training is oscillating - reduce learning rate",
                "Consider using learning rate scheduling",
                "Implement gradient clipping if not already used"
            ])
        
        elif status == ConvergenceStatus.STAGNANT:
            recommendations.extend([
                "Training has stagnated - consider learning rate adjustment",
                "Try different optimization algorithm",
                "Check if model capacity is sufficient"
            ])
        
        elif status == ConvergenceStatus.CONVERGED:
            recommendations.append("Model has converged - training can be stopped")
        
        # High volatility recommendations
        if trend_stats['volatility'] > 0.3:
            recommendations.append("High training volatility - consider batch size adjustment")
        
        # Creator-specific recommendations
        if creator_type:
            creator_recs = self.creator_profiler.get_creator_recommendations(
                creator_type, self.current_epoch
            )
            recommendations.extend(creator_recs)
        
        return recommendations
    
    def _generate_creator_insights(self, creator_type: str) -> Dict[str, Any]:
        """Generate creator-specific insights."""
        profile = self.creator_profiler.creator_profiles.get(creator_type, {})
        
        insights = {
            'creator_type': creator_type,
            'overfitting_tendency': profile.get('overfitting_tendency', 0.0),
            'typical_convergence_epochs': profile.get('typical_convergence_epochs', []),
            'recommended_patience': self.creator_profiler.get_optimal_patience(
                creator_type, self.config.patience
            )
        }
        
        # Add performance comparison
        if self.convergence_history:
            current_performance = self.convergence_history[-1].training_loss
            typical_epochs = profile.get('typical_convergence_epochs', [])
            
            if typical_epochs and self.current_epoch in range(
                int(np.mean(typical_epochs) * 0.8),
                int(np.mean(typical_epochs) * 1.2)
            ):
                insights['performance_vs_typical'] = 'on_track'
            elif self.current_epoch > (np.mean(typical_epochs) if typical_epochs else 50):
                insights['performance_vs_typical'] = 'slow_convergence'
            else:
                insights['performance_vs_typical'] = 'fast_convergence'
        
        return insights
    
    async def check_early_stopping(
        self,
        model: Optional[nn.Module] = None
    ) -> Tuple[bool, str]:
        """Check if early stopping should be triggered."""
        if not self.convergence_history:
            return False, "No convergence data available"
        
        latest_point = self.convergence_history[-1]
        return self.early_stopping.check_early_stopping(
            latest_point.epoch, latest_point, model
        )
    
    async def create_convergence_plots(self, save_dir: Optional[Path] = None):
        """Create convergence visualization plots."""
        if not self.config.save_convergence_plots or not self.convergence_history:
            return
        
        save_dir = save_dir or Path("convergence_plots")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract data
        epochs = [p.epoch for p in self.convergence_history]
        train_losses = [p.training_loss for p in self.convergence_history]
        val_losses = [p.validation_loss for p in self.convergence_history if p.validation_loss is not None]
        val_epochs = [p.epoch for p in self.convergence_history if p.validation_loss is not None]
        
        # Create loss plot
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(epochs, train_losses, label='Training Loss', alpha=0.7)
        if val_losses:
            plt.plot(val_epochs, val_losses, label='Validation Loss', alpha=0.7)
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training Convergence')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Create smoothed loss plot
        plt.subplot(2, 2, 2)
        if len(train_losses) > 5:
            smoothed_train = self.trend_analyzer.smooth_values(train_losses)
            plt.plot(epochs, smoothed_train, label='Smoothed Training Loss', linewidth=2)
        if len(val_losses) > 5:
            smoothed_val = self.trend_analyzer.smooth_values(val_losses)
            plt.plot(val_epochs, smoothed_val, label='Smoothed Validation Loss', linewidth=2)
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Smoothed Convergence')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Create gradient norm plot if available
        gradient_norms = [p.gradient_norm for p in self.convergence_history if p.gradient_norm is not None]
        if gradient_norms:
            grad_epochs = [p.epoch for p in self.convergence_history if p.gradient_norm is not None]
            plt.subplot(2, 2, 3)
            plt.plot(grad_epochs, gradient_norms, label='Gradient Norm', color='red', alpha=0.7)
            plt.xlabel('Epoch')
            plt.ylabel('Gradient Norm')
            plt.title('Gradient Convergence')
            plt.yscale('log')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        # Create learning rate plot
        learning_rates = [p.learning_rate for p in self.convergence_history]
        plt.subplot(2, 2, 4)
        plt.plot(epochs, learning_rates, label='Learning Rate', color='green', alpha=0.7)
        plt.xlabel('Epoch')
        plt.ylabel('Learning Rate')
        plt.title('Learning Rate Schedule')
        plt.yscale('log')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_dir / f"convergence_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved convergence plots to {save_dir}")
    
    def get_convergence_summary(self) -> Dict[str, Any]:
        """Get comprehensive convergence summary."""
        if not self.convergence_history:
            return {'status': 'no_data'}
        
        latest_analysis = self.analysis_history[-1] if self.analysis_history else None
        
        summary = {
            'total_epochs': self.current_epoch,
            'data_points': len(self.convergence_history),
            'analysis_active': self.analysis_active,
            'early_stopping_stats': self.early_stopping.get_stopping_statistics(),
            'overfitting_gap': self.overfitting_detector.calculate_generalization_gap()
        }
        
        if latest_analysis:
            summary.update({
                'current_status': latest_analysis.status.value,
                'confidence': latest_analysis.confidence,
                'best_epoch': latest_analysis.best_epoch,
                'best_score': latest_analysis.best_score,
                'current_score': latest_analysis.current_score,
                'recommendations': latest_analysis.recommendations[:3]  # Top 3 recommendations
            })
        
        return summary


# Factory function for easy instantiation
def create_convergence_analyzer(
    patience: int = 20,
    min_delta: float = 1e-4,
    creator_adaptive: bool = True,
    **kwargs
) -> ModelConvergenceAnalyzer:
    """Factory function to create convergence analyzer."""
    config = ConvergenceConfig(
        patience=patience,
        min_delta=min_delta,
        creator_adaptive=creator_adaptive,
        **kwargs
    )
    return ModelConvergenceAnalyzer(config)


# Example usage for Ainflue creators
async def example_convergence_analysis():
    """Example of convergence analysis for creator training."""
    
    # Create convergence analyzer
    analyzer = create_convergence_analyzer(
        patience=15,
        min_delta=1e-4,
        creator_adaptive=True,
        use_combined_criteria=True,
        save_convergence_plots=True
    )
    
    await analyzer.start_analysis()
    
    logger.info("Model convergence analyzer ready for creator training monitoring")
    
    return analyzer


if __name__ == "__main__":
    # Run example
    asyncio.run(example_convergence_analysis())