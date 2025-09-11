#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ML Module - Training Visualization Engine
Advanced training visualization with loss curves, gradient norms, and feature maps

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0
Letztes Update: Januar 2025

⚠️ WARNUNG: Dieser Code ist urheberrechtlich geschützt und vertraulich.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
import base64
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationType(Enum):
    """Types of training visualizations."""
    LOSS_CURVES = "loss_curves"
    ACCURACY_CURVES = "accuracy_curves"
    GRADIENT_NORMS = "gradient_norms"
    FEATURE_MAPS = "feature_maps"
    WEIGHT_DISTRIBUTIONS = "weight_distributions"
    LEARNING_RATE = "learning_rate"
    CONFUSION_MATRIX = "confusion_matrix"
    ROC_CURVES = "roc_curves"
    TRAINING_PROGRESS = "training_progress"
    MODEL_COMPARISON = "model_comparison"
    CREATOR_ANALYTICS = "creator_analytics"

class CreatorType(Enum):
    """Creator types for specialized visualizations."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class VisualizationConfig:
    """Configuration for visualization generation."""
    visualization_type: VisualizationType
    interactive: bool = True
    real_time: bool = True
    creator_specific: bool = True
    save_to_file: bool = True
    export_format: str = "html"
    update_frequency: int = 10  # epochs

@dataclass
class TrainingMetrics:
    """Training metrics for visualization."""
    epoch: int
    train_loss: float
    val_loss: float
    train_accuracy: float
    val_accuracy: float
    learning_rate: float
    gradient_norm: float
    timestamp: datetime
    creator_type: Optional[CreatorType] = None
    custom_metrics: Optional[Dict[str, float]] = None

class TrainingVisualizationEngine:
    """
    🎖️ LEAD DEV IA - Advanced Training Visualization System
    
    Comprehensive training visualization with real-time monitoring,
    creator-specific analytics, and enterprise-grade reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize training visualization engine."""
        self.config = config or {}
        self.visualization_configs: Dict[VisualizationType, VisualizationConfig] = {}
        self.training_history: List[TrainingMetrics] = []
        self.model_weights_history: List[Dict[str, torch.Tensor]] = []
        self.feature_maps_cache: Dict[str, np.ndarray] = {}
        self.visualization_cache: Dict[str, Any] = {}
        
        # Setup output directories
        self.output_dir = Path(self.config.get("output_dir", "ml/visualizations"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        logger.info("🎖️ TrainingVisualizationEngine initialized - Lead Dev IA expertise")
        
        # Setup default configurations
        self._initialize_default_configs()
        
        # Setup creator-specific themes
        self._initialize_creator_themes()
    
    def _initialize_default_configs(self):
        """Initialize default visualization configurations."""
        default_configs = {
            VisualizationType.LOSS_CURVES: VisualizationConfig(
                visualization_type=VisualizationType.LOSS_CURVES,
                interactive=True,
                real_time=True,
                creator_specific=True
            ),
            VisualizationType.GRADIENT_NORMS: VisualizationConfig(
                visualization_type=VisualizationType.GRADIENT_NORMS,
                interactive=True,
                real_time=True,
                update_frequency=5
            ),
            VisualizationType.FEATURE_MAPS: VisualizationConfig(
                visualization_type=VisualizationType.FEATURE_MAPS,
                interactive=False,
                real_time=False,
                update_frequency=20
            ),
            VisualizationType.CREATOR_ANALYTICS: VisualizationConfig(
                visualization_type=VisualizationType.CREATOR_ANALYTICS,
                interactive=True,
                real_time=True,
                creator_specific=True
            )
        }
        
        self.visualization_configs.update(default_configs)
    
    def _initialize_creator_themes(self):
        """Initialize creator-specific visualization themes."""
        self.creator_themes = {
            CreatorType.MUSICIAN: {
                "primary_color": "#FF6B6B",
                "secondary_color": "#4ECDC4",
                "accent_color": "#45B7D1",
                "background_color": "#F8F9FA",
                "style": "musical_waves"
            },
            CreatorType.BLOGGER: {
                "primary_color": "#96CEB4",
                "secondary_color": "#FECA57",
                "accent_color": "#FF9FF3",
                "background_color": "#F1F2F6",
                "style": "clean_modern"
            },
            CreatorType.PHOTOGRAPHER: {
                "primary_color": "#3742FA",
                "secondary_color": "#FF3838",
                "accent_color": "#2F3542",
                "background_color": "#F1F2F6",
                "style": "artistic_gradient"
            },
            CreatorType.INFLUENCER: {
                "primary_color": "#FF6348",
                "secondary_color": "#2ED573",
                "accent_color": "#1E90FF",
                "background_color": "#F8F9FA",
                "style": "vibrant_social"
            },
            CreatorType.COMEDIAN: {
                "primary_color": "#FFA502",
                "secondary_color": "#FF6B6B",
                "accent_color": "#3742FA",
                "background_color": "#F1F2F6",
                "style": "playful_bright"
            }
        }
    
    async def log_training_metrics(
        self,
        epoch: int,
        train_loss: float,
        val_loss: float,
        train_accuracy: float,
        val_accuracy: float,
        learning_rate: float,
        gradient_norm: float,
        creator_type: Optional[CreatorType] = None,
        custom_metrics: Optional[Dict[str, float]] = None
    ):
        """
        Log training metrics for visualization.
        
        Args:
            epoch: Current training epoch
            train_loss: Training loss
            val_loss: Validation loss
            train_accuracy: Training accuracy
            val_accuracy: Validation accuracy
            learning_rate: Current learning rate
            gradient_norm: Gradient norm
            creator_type: Creator type for specialized analytics
            custom_metrics: Additional custom metrics
        """
        metrics = TrainingMetrics(
            epoch=epoch,
            train_loss=train_loss,
            val_loss=val_loss,
            train_accuracy=train_accuracy,
            val_accuracy=val_accuracy,
            learning_rate=learning_rate,
            gradient_norm=gradient_norm,
            timestamp=datetime.now(),
            creator_type=creator_type,
            custom_metrics=custom_metrics or {}
        )
        
        self.training_history.append(metrics)
        
        # Generate real-time visualizations if enabled
        if self._should_update_visualizations(epoch):
            await self._generate_real_time_visualizations(creator_type)
        
        logger.info(f"📊 Training metrics logged for epoch {epoch}")
    
    def _should_update_visualizations(self, epoch: int) -> bool:
        """Check if visualizations should be updated."""
        update_frequencies = [
            config.update_frequency 
            for config in self.visualization_configs.values()
            if config.real_time
        ]
        
        if not update_frequencies:
            return False
        
        min_frequency = min(update_frequencies)
        return epoch % min_frequency == 0
    
    async def _generate_real_time_visualizations(self, creator_type: Optional[CreatorType]):
        """Generate real-time visualizations."""
        tasks = []
        
        # Generate key real-time visualizations
        for viz_type in [VisualizationType.LOSS_CURVES, VisualizationType.GRADIENT_NORMS]:
            config = self.visualization_configs.get(viz_type)
            if config and config.real_time:
                tasks.append(self.generate_visualization(viz_type, creator_type))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    async def generate_visualization(
        self,
        visualization_type: VisualizationType,
        creator_type: Optional[CreatorType] = None,
        save_to_file: bool = True
    ) -> Dict[str, Any]:
        """
        Generate specific visualization.
        
        Args:
            visualization_type: Type of visualization to generate
            creator_type: Creator type for themed visualization
            save_to_file: Whether to save visualization to file
            
        Returns:
            Visualization data and metadata
        """
        logger.info(f"🎨 Generating {visualization_type.value} visualization")
        
        config = self.visualization_configs.get(visualization_type)
        if not config:
            logger.warning(f"⚠️ No configuration found for {visualization_type.value}")
            return {}
        
        # Get creator theme
        theme = self.creator_themes.get(creator_type, self.creator_themes[CreatorType.INFLUENCER])
        
        # Generate visualization based on type
        if visualization_type == VisualizationType.LOSS_CURVES:
            viz_data = await self._generate_loss_curves(theme, config)
        elif visualization_type == VisualizationType.ACCURACY_CURVES:
            viz_data = await self._generate_accuracy_curves(theme, config)
        elif visualization_type == VisualizationType.GRADIENT_NORMS:
            viz_data = await self._generate_gradient_norms(theme, config)
        elif visualization_type == VisualizationType.FEATURE_MAPS:
            viz_data = await self._generate_feature_maps(theme, config)
        elif visualization_type == VisualizationType.WEIGHT_DISTRIBUTIONS:
            viz_data = await self._generate_weight_distributions(theme, config)
        elif visualization_type == VisualizationType.LEARNING_RATE:
            viz_data = await self._generate_learning_rate_plot(theme, config)
        elif visualization_type == VisualizationType.TRAINING_PROGRESS:
            viz_data = await self._generate_training_progress(theme, config)
        elif visualization_type == VisualizationType.CREATOR_ANALYTICS:
            viz_data = await self._generate_creator_analytics(creator_type, theme, config)
        else:
            logger.warning(f"⚠️ Unsupported visualization type: {visualization_type.value}")
            return {}
        
        # Save to file if requested
        if save_to_file and config.save_to_file:
            await self._save_visualization(viz_data, visualization_type, creator_type)
        
        # Cache visualization
        cache_key = f"{visualization_type.value}_{creator_type.value if creator_type else 'default'}"
        self.visualization_cache[cache_key] = viz_data
        
        logger.info(f"✅ {visualization_type.value} visualization generated successfully")
        return viz_data
    
    async def _generate_loss_curves(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate loss curves visualization."""
        if not self.training_history:
            return {"error": "No training history available"}
        
        # Prepare data
        epochs = [m.epoch for m in self.training_history]
        train_losses = [m.train_loss for m in self.training_history]
        val_losses = [m.val_loss for m in self.training_history]
        
        # Create interactive plot
        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=("Training & Validation Loss"),
            specs=[[{"secondary_y": False}]]
        )
        
        # Add training loss
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=train_losses,
                name="Training Loss",
                line=dict(color=theme["primary_color"], width=3),
                mode="lines+markers"
            )
        )
        
        # Add validation loss
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=val_losses,
                name="Validation Loss",
                line=dict(color=theme["secondary_color"], width=3),
                mode="lines+markers"
            )
        )
        
        # Update layout with theme
        fig.update_layout(
            title="Training & Validation Loss Over Time",
            xaxis_title="Epoch",
            yaxis_title="Loss",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            font=dict(size=12),
            showlegend=True,
            hovermode="x unified"
        )
        
        # Add annotations for best validation loss
        if val_losses:
            best_val_idx = np.argmin(val_losses)
            best_val_loss = val_losses[best_val_idx]
            best_epoch = epochs[best_val_idx]
            
            fig.add_annotation(
                x=best_epoch,
                y=best_val_loss,
                text=f"Best Val Loss: {best_val_loss:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=theme["accent_color"],
                bgcolor=theme["background_color"],
                bordercolor=theme["accent_color"]
            )
        
        return {
            "type": "loss_curves",
            "figure": fig,
            "data": {
                "epochs": epochs,
                "train_losses": train_losses,
                "val_losses": val_losses
            },
            "metadata": {
                "best_val_loss": min(val_losses) if val_losses else None,
                "best_epoch": epochs[np.argmin(val_losses)] if val_losses else None,
                "current_overfitting": (val_losses[-1] - train_losses[-1]) / train_losses[-1] if len(train_losses) > 0 and train_losses[-1] > 0 else 0
            }
        }
    
    async def _generate_accuracy_curves(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate accuracy curves visualization."""
        if not self.training_history:
            return {"error": "No training history available"}
        
        # Prepare data
        epochs = [m.epoch for m in self.training_history]
        train_accs = [m.train_accuracy for m in self.training_history]
        val_accs = [m.val_accuracy for m in self.training_history]
        
        # Create interactive plot
        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=("Training & Validation Accuracy"),
            specs=[[{"secondary_y": False}]]
        )
        
        # Add training accuracy
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=train_accs,
                name="Training Accuracy",
                line=dict(color=theme["primary_color"], width=3),
                mode="lines+markers"
            )
        )
        
        # Add validation accuracy
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=val_accs,
                name="Validation Accuracy",
                line=dict(color=theme["secondary_color"], width=3),
                mode="lines+markers"
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Training & Validation Accuracy Over Time",
            xaxis_title="Epoch",
            yaxis_title="Accuracy",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            font=dict(size=12),
            showlegend=True,
            hovermode="x unified",
            yaxis=dict(range=[0, 1])
        )
        
        return {
            "type": "accuracy_curves",
            "figure": fig,
            "data": {
                "epochs": epochs,
                "train_accuracies": train_accs,
                "val_accuracies": val_accs
            },
            "metadata": {
                "best_val_accuracy": max(val_accs) if val_accs else None,
                "final_train_accuracy": train_accs[-1] if train_accs else None,
                "final_val_accuracy": val_accs[-1] if val_accs else None
            }
        }
    
    async def _generate_gradient_norms(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate gradient norms visualization."""
        if not self.training_history:
            return {"error": "No training history available"}
        
        # Prepare data
        epochs = [m.epoch for m in self.training_history]
        gradient_norms = [m.gradient_norm for m in self.training_history]
        
        # Create interactive plot
        fig = go.Figure()
        
        # Add gradient norms
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=gradient_norms,
                name="Gradient Norm",
                line=dict(color=theme["accent_color"], width=2),
                mode="lines+markers",
                fill="tonexty"
            )
        )
        
        # Add moving average
        if len(gradient_norms) > 5:
            window_size = min(10, len(gradient_norms) // 4)
            moving_avg = pd.Series(gradient_norms).rolling(window=window_size).mean()
            
            fig.add_trace(
                go.Scatter(
                    x=epochs,
                    y=moving_avg,
                    name=f"Moving Average ({window_size})",
                    line=dict(color=theme["primary_color"], width=3, dash="dash"),
                    mode="lines"
                )
            )
        
        # Update layout
        fig.update_layout(
            title="Gradient Norms During Training",
            xaxis_title="Epoch",
            yaxis_title="Gradient Norm",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            font=dict(size=12),
            showlegend=True,
            hovermode="x unified"
        )
        
        # Add threshold lines for gradient clipping
        if gradient_norms:
            max_norm = max(gradient_norms)
            fig.add_hline(
                y=max_norm * 0.1,
                line_dash="dot",
                line_color="red",
                annotation_text="Low Gradient Warning"
            )
            fig.add_hline(
                y=max_norm * 0.9,
                line_dash="dot",
                line_color="orange",
                annotation_text="High Gradient Warning"
            )
        
        return {
            "type": "gradient_norms",
            "figure": fig,
            "data": {
                "epochs": epochs,
                "gradient_norms": gradient_norms
            },
            "metadata": {
                "max_gradient_norm": max(gradient_norms) if gradient_norms else None,
                "min_gradient_norm": min(gradient_norms) if gradient_norms else None,
                "avg_gradient_norm": np.mean(gradient_norms) if gradient_norms else None,
                "gradient_stability": np.std(gradient_norms) if gradient_norms else None
            }
        }
    
    async def _generate_feature_maps(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate feature maps visualization."""
        # This would typically require model hooks to capture feature maps
        # For now, we'll create a placeholder structure
        
        # Generate sample feature map data (would be real in production)
        sample_feature_map = np.random.rand(64, 64, 16)  # Example: 64x64 with 16 channels
        
        # Create subplots for different channels
        n_channels = min(16, sample_feature_map.shape[2])
        cols = 4
        rows = (n_channels + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[f"Channel {i+1}" for i in range(n_channels)],
            specs=[[{"type": "heatmap"} for _ in range(cols)] for _ in range(rows)]
        )
        
        for i in range(n_channels):
            row = i // cols + 1
            col = i % cols + 1
            
            fig.add_trace(
                go.Heatmap(
                    z=sample_feature_map[:, :, i],
                    colorscale="Viridis",
                    showscale=False
                ),
                row=row,
                col=col
            )
        
        fig.update_layout(
            title="Feature Maps Visualization",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            height=200 * rows
        )
        
        return {
            "type": "feature_maps",
            "figure": fig,
            "data": {
                "feature_map_shape": sample_feature_map.shape,
                "n_channels_displayed": n_channels
            },
            "metadata": {
                "activation_statistics": {
                    "mean": float(np.mean(sample_feature_map)),
                    "std": float(np.std(sample_feature_map)),
                    "max": float(np.max(sample_feature_map)),
                    "min": float(np.min(sample_feature_map))
                }
            }
        }
    
    async def _generate_weight_distributions(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate weight distributions visualization."""
        if not self.model_weights_history:
            return {"error": "No weight history available"}
        
        # Get latest weights
        latest_weights = self.model_weights_history[-1]
        
        # Create subplot for each layer
        layer_names = list(latest_weights.keys())[:6]  # Limit to 6 layers for visualization
        
        fig = make_subplots(
            rows=2,
            cols=3,
            subplot_titles=layer_names,
            specs=[[{"type": "histogram"} for _ in range(3)] for _ in range(2)]
        )
        
        for i, layer_name in enumerate(layer_names):
            weights = latest_weights[layer_name].detach().cpu().numpy().flatten()
            row = i // 3 + 1
            col = i % 3 + 1
            
            fig.add_trace(
                go.Histogram(
                    x=weights,
                    nbinsx=50,
                    name=layer_name,
                    marker_color=theme["primary_color"],
                    opacity=0.7
                ),
                row=row,
                col=col
            )
        
        fig.update_layout(
            title="Weight Distributions by Layer",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            height=600,
            showlegend=False
        )
        
        return {
            "type": "weight_distributions",
            "figure": fig,
            "data": {
                "layer_names": layer_names,
                "weight_statistics": {
                    name: {
                        "mean": float(weights.mean()),
                        "std": float(weights.std()),
                        "min": float(weights.min()),
                        "max": float(weights.max())
                    }
                    for name, weights in latest_weights.items()
                }
            }
        }
    
    async def _generate_learning_rate_plot(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate learning rate plot."""
        if not self.training_history:
            return {"error": "No training history available"}
        
        epochs = [m.epoch for m in self.training_history]
        learning_rates = [m.learning_rate for m in self.training_history]
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=learning_rates,
                name="Learning Rate",
                line=dict(color=theme["accent_color"], width=3),
                mode="lines+markers"
            )
        )
        
        fig.update_layout(
            title="Learning Rate Schedule",
            xaxis_title="Epoch",
            yaxis_title="Learning Rate",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            yaxis_type="log" if max(learning_rates) / min(learning_rates) > 100 else "linear"
        )
        
        return {
            "type": "learning_rate",
            "figure": fig,
            "data": {
                "epochs": epochs,
                "learning_rates": learning_rates
            },
            "metadata": {
                "initial_lr": learning_rates[0] if learning_rates else None,
                "final_lr": learning_rates[-1] if learning_rates else None,
                "lr_decay_factor": learning_rates[0] / learning_rates[-1] if learning_rates and learning_rates[-1] > 0 else None
            }
        }
    
    async def _generate_training_progress(
        self,
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate comprehensive training progress dashboard."""
        if not self.training_history:
            return {"error": "No training history available"}
        
        # Create 2x2 subplot dashboard
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Loss Curves",
                "Accuracy Curves", 
                "Learning Rate",
                "Gradient Norms"
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}]
            ]
        )
        
        epochs = [m.epoch for m in self.training_history]
        train_losses = [m.train_loss for m in self.training_history]
        val_losses = [m.val_loss for m in self.training_history]
        train_accs = [m.train_accuracy for m in self.training_history]
        val_accs = [m.val_accuracy for m in self.training_history]
        learning_rates = [m.learning_rate for m in self.training_history]
        gradient_norms = [m.gradient_norm for m in self.training_history]
        
        # Loss curves (row 1, col 1)
        fig.add_trace(
            go.Scatter(x=epochs, y=train_losses, name="Train Loss", 
                      line=dict(color=theme["primary_color"])),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=epochs, y=val_losses, name="Val Loss",
                      line=dict(color=theme["secondary_color"])),
            row=1, col=1
        )
        
        # Accuracy curves (row 1, col 2)
        fig.add_trace(
            go.Scatter(x=epochs, y=train_accs, name="Train Acc",
                      line=dict(color=theme["primary_color"])),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=epochs, y=val_accs, name="Val Acc",
                      line=dict(color=theme["secondary_color"])),
            row=1, col=2
        )
        
        # Learning rate (row 2, col 1)
        fig.add_trace(
            go.Scatter(x=epochs, y=learning_rates, name="Learning Rate",
                      line=dict(color=theme["accent_color"])),
            row=2, col=1
        )
        
        # Gradient norms (row 2, col 2)
        fig.add_trace(
            go.Scatter(x=epochs, y=gradient_norms, name="Gradient Norm",
                      line=dict(color=theme["accent_color"])),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Training Progress Dashboard",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            height=800,
            showlegend=True
        )
        
        return {
            "type": "training_progress",
            "figure": fig,
            "data": {
                "summary_statistics": {
                    "total_epochs": len(epochs),
                    "best_val_loss": min(val_losses) if val_losses else None,
                    "best_val_accuracy": max(val_accs) if val_accs else None,
                    "final_learning_rate": learning_rates[-1] if learning_rates else None,
                    "avg_gradient_norm": np.mean(gradient_norms) if gradient_norms else None
                }
            }
        }
    
    async def _generate_creator_analytics(
        self,
        creator_type: Optional[CreatorType],
        theme: Dict[str, str],
        config: VisualizationConfig
    ) -> Dict[str, Any]:
        """Generate creator-specific analytics visualization."""
        if not creator_type or not self.training_history:
            return {"error": "No creator-specific data available"}
        
        # Filter metrics for specific creator type
        creator_metrics = [
            m for m in self.training_history 
            if m.creator_type == creator_type
        ]
        
        if not creator_metrics:
            return {"error": f"No metrics found for {creator_type.value}"}
        
        # Create creator-specific analytics
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                f"{creator_type.value.title()} Performance",
                "Engagement Metrics",
                "Content Quality Score",
                "Platform Optimization"
            )
        )
        
        epochs = [m.epoch for m in creator_metrics]
        
        # Performance metrics
        val_accs = [m.val_accuracy for m in creator_metrics]
        fig.add_trace(
            go.Scatter(x=epochs, y=val_accs, name="Validation Accuracy",
                      line=dict(color=theme["primary_color"], width=3)),
            row=1, col=1
        )
        
        # Engagement metrics (from custom metrics)
        engagement_scores = [
            m.custom_metrics.get("engagement_score", 0.5) 
            for m in creator_metrics if m.custom_metrics
        ]
        if engagement_scores:
            fig.add_trace(
                go.Scatter(x=epochs[:len(engagement_scores)], y=engagement_scores, 
                          name="Engagement Score",
                          line=dict(color=theme["secondary_color"], width=3)),
                row=1, col=2
            )
        
        # Content quality score
        quality_scores = [
            m.custom_metrics.get("content_quality", 0.7)
            for m in creator_metrics if m.custom_metrics
        ]
        if quality_scores:
            fig.add_trace(
                go.Scatter(x=epochs[:len(quality_scores)], y=quality_scores,
                          name="Content Quality",
                          line=dict(color=theme["accent_color"], width=3)),
                row=2, col=1
            )
        
        # Platform optimization score
        platform_scores = [
            m.custom_metrics.get("platform_optimization", 0.6)
            for m in creator_metrics if m.custom_metrics
        ]
        if platform_scores:
            fig.add_trace(
                go.Scatter(x=epochs[:len(platform_scores)], y=platform_scores,
                          name="Platform Optimization",
                          line=dict(color=theme["primary_color"], width=3)),
                row=2, col=2
            )
        
        fig.update_layout(
            title=f"{creator_type.value.title()} Creator Analytics Dashboard",
            template="plotly_white",
            plot_bgcolor=theme["background_color"],
            height=800,
            showlegend=True
        )
        
        return {
            "type": "creator_analytics",
            "figure": fig,
            "creator_type": creator_type.value,
            "data": {
                "creator_performance": {
                    "best_accuracy": max(val_accs) if val_accs else None,
                    "avg_engagement": np.mean(engagement_scores) if engagement_scores else None,
                    "avg_quality": np.mean(quality_scores) if quality_scores else None,
                    "platform_score": np.mean(platform_scores) if platform_scores else None
                }
            }
        }
    
    async def _save_visualization(
        self,
        viz_data: Dict[str, Any],
        visualization_type: VisualizationType,
        creator_type: Optional[CreatorType]
    ):
        """Save visualization to file."""
        if "figure" not in viz_data:
            return
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        creator_suffix = f"_{creator_type.value}" if creator_type else ""
        filename = f"{visualization_type.value}{creator_suffix}_{timestamp}"
        
        # Save as HTML (interactive)
        html_path = self.output_dir / f"{filename}.html"
        viz_data["figure"].write_html(str(html_path))
        
        # Save as PNG (static)
        png_path = self.output_dir / f"{filename}.png"
        try:
            viz_data["figure"].write_image(str(png_path), width=1200, height=800)
        except Exception as e:
            logger.warning(f"Could not save PNG: {e}")
        
        logger.info(f"💾 Visualization saved: {html_path}")
    
    async def log_model_weights(self, model: nn.Module, epoch: int):
        """Log model weights for distribution analysis."""
        weights_dict = {}
        
        for name, param in model.named_parameters():
            if param.requires_grad and len(param.shape) > 1:  # Skip biases
                weights_dict[name] = param.data.clone()
        
        # Keep only last 10 weight snapshots to manage memory
        self.model_weights_history.append(weights_dict)
        if len(self.model_weights_history) > 10:
            self.model_weights_history.pop(0)
        
        logger.info(f"📊 Model weights logged for epoch {epoch}")
    
    async def generate_comprehensive_report(
        self,
        creator_type: Optional[CreatorType] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive training visualization report.
        
        Args:
            creator_type: Creator type for specialized report
            
        Returns:
            Comprehensive visualization report
        """
        logger.info("📊 Generating comprehensive training visualization report")
        
        # Generate all key visualizations
        visualizations = {}
        
        viz_types = [
            VisualizationType.LOSS_CURVES,
            VisualizationType.ACCURACY_CURVES,
            VisualizationType.GRADIENT_NORMS,
            VisualizationType.LEARNING_RATE,
            VisualizationType.TRAINING_PROGRESS
        ]
        
        if creator_type:
            viz_types.append(VisualizationType.CREATOR_ANALYTICS)
        
        if self.model_weights_history:
            viz_types.append(VisualizationType.WEIGHT_DISTRIBUTIONS)
        
        # Generate all visualizations
        for viz_type in viz_types:
            try:
                viz_data = await self.generate_visualization(viz_type, creator_type)
                if viz_data and "error" not in viz_data:
                    visualizations[viz_type.value] = viz_data
            except Exception as e:
                logger.error(f"Error generating {viz_type.value}: {e}")
        
        # Compile report
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "creator_type": creator_type.value if creator_type else None,
                "total_epochs": len(self.training_history),
                "visualization_count": len(visualizations)
            },
            "training_summary": self._generate_training_summary(),
            "visualizations": visualizations,
            "recommendations": await self._generate_visualization_recommendations(creator_type)
        }
        
        # Save report
        report_path = self.output_dir / f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert figures to JSON-serializable format
        json_report = self._prepare_report_for_json(report)
        
        with open(report_path, 'w') as f:
            json.dump(json_report, f, indent=2, default=str)
        
        logger.info(f"✅ Comprehensive training report generated: {report_path}")
        return report
    
    def _generate_training_summary(self) -> Dict[str, Any]:
        """Generate training summary statistics."""
        if not self.training_history:
            return {}
        
        # Calculate summary statistics
        final_metrics = self.training_history[-1]
        best_val_loss_idx = np.argmin([m.val_loss for m in self.training_history])
        best_val_acc_idx = np.argmax([m.val_accuracy for m in self.training_history])
        
        return {
            "total_epochs": len(self.training_history),
            "final_train_loss": final_metrics.train_loss,
            "final_val_loss": final_metrics.val_loss,
            "final_train_accuracy": final_metrics.train_accuracy,
            "final_val_accuracy": final_metrics.val_accuracy,
            "best_val_loss": self.training_history[best_val_loss_idx].val_loss,
            "best_val_loss_epoch": self.training_history[best_val_loss_idx].epoch,
            "best_val_accuracy": self.training_history[best_val_acc_idx].val_accuracy,
            "best_val_accuracy_epoch": self.training_history[best_val_acc_idx].epoch,
            "training_duration": (
                self.training_history[-1].timestamp - self.training_history[0].timestamp
            ).total_seconds() / 3600,  # hours
            "overfitting_score": (
                final_metrics.val_loss - final_metrics.train_loss
            ) / final_metrics.train_loss if final_metrics.train_loss > 0 else 0,
            "generalization_gap": final_metrics.train_accuracy - final_metrics.val_accuracy
        }
    
    async def _generate_visualization_recommendations(
        self,
        creator_type: Optional[CreatorType]
    ) -> List[str]:
        """Generate recommendations based on visualization analysis."""
        recommendations = []
        
        if not self.training_history:
            return ["No training data available for analysis"]
        
        summary = self._generate_training_summary()
        
        # Overfitting analysis
        if summary.get("overfitting_score", 0) > 0.2:
            recommendations.append("🚨 High overfitting detected - consider regularization")
        elif summary.get("overfitting_score", 0) < 0.05:
            recommendations.append("📈 Low overfitting - model may have more capacity")
        
        # Generalization gap analysis
        if summary.get("generalization_gap", 0) > 0.1:
            recommendations.append("📊 Large generalization gap - review validation strategy")
        
        # Learning rate analysis
        if len(self.training_history) > 10:
            recent_losses = [m.val_loss for m in self.training_history[-10:]]
            if np.std(recent_losses) < 0.001:
                recommendations.append("🔄 Loss plateau detected - consider LR scheduling")
        
        # Gradient norm analysis
        gradient_norms = [m.gradient_norm for m in self.training_history]
        if gradient_norms:
            avg_grad_norm = np.mean(gradient_norms)
            if avg_grad_norm < 0.1:
                recommendations.append("⚠️ Low gradient norms - check for vanishing gradients")
            elif avg_grad_norm > 10:
                recommendations.append("📈 High gradient norms - consider gradient clipping")
        
        # Creator-specific recommendations
        if creator_type:
            if creator_type == CreatorType.PHOTOGRAPHER:
                recommendations.append("📸 Consider data augmentation for visual content")
            elif creator_type == CreatorType.MUSICIAN:
                recommendations.append("🎵 Monitor audio-specific quality metrics")
            elif creator_type == CreatorType.BLOGGER:
                recommendations.append("📝 Track text coherence and readability metrics")
        
        return recommendations
    
    def _prepare_report_for_json(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare report for JSON serialization by converting Plotly figures."""
        json_report = report.copy()
        
        # Convert visualizations to base64 encoded images or remove figures
        if "visualizations" in json_report:
            for viz_name, viz_data in json_report["visualizations"].items():
                if "figure" in viz_data:
                    # Remove the Plotly figure object (too complex for JSON)
                    # In production, could convert to base64 image
                    viz_data_copy = viz_data.copy()
                    del viz_data_copy["figure"]
                    json_report["visualizations"][viz_name] = viz_data_copy
        
        return json_report

# Export main class
__all__ = ['TrainingVisualizationEngine', 'VisualizationType', 'CreatorType', 'VisualizationConfig', 'TrainingMetrics']

if __name__ == "__main__":
    # Test the training visualization engine
    async def test_training_visualization_engine():
        engine = TrainingVisualizationEngine()
        
        # Simulate training metrics
        for epoch in range(20):
            await engine.log_training_metrics(
                epoch=epoch,
                train_loss=1.0 - epoch * 0.05 + np.random.normal(0, 0.02),
                val_loss=1.2 - epoch * 0.045 + np.random.normal(0, 0.03),
                train_accuracy=epoch * 0.04 + np.random.normal(0, 0.01),
                val_accuracy=epoch * 0.035 + np.random.normal(0, 0.015),
                learning_rate=0.001 * (0.9 ** (epoch // 5)),
                gradient_norm=1.0 + np.random.normal(0, 0.1),
                creator_type=CreatorType.MUSICIAN,
                custom_metrics={
                    "engagement_score": 0.5 + epoch * 0.02,
                    "content_quality": 0.6 + epoch * 0.015,
                    "platform_optimization": 0.55 + epoch * 0.018
                }
            )
        
        # Generate visualizations
        loss_viz = await engine.generate_visualization(
            VisualizationType.LOSS_CURVES,
            CreatorType.MUSICIAN
        )
        
        progress_viz = await engine.generate_visualization(
            VisualizationType.TRAINING_PROGRESS,
            CreatorType.MUSICIAN
        )
        
        creator_viz = await engine.generate_visualization(
            VisualizationType.CREATOR_ANALYTICS,
            CreatorType.MUSICIAN
        )
        
        # Generate comprehensive report
        report = await engine.generate_comprehensive_report(CreatorType.MUSICIAN)
        
        print(f"✅ Generated {len(report['visualizations'])} visualizations")
        print(f"📊 Training summary: {report['training_summary']}")
        print(f"💡 Recommendations: {len(report['recommendations'])}")
        
        print("✅ TrainingVisualizationEngine test completed successfully!")
    
    # Run test
    asyncio.run(test_training_visualization_engine())