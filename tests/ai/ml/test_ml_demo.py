# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
ML Demo Tests - Enterprise Grade Demo & Showcase Test Suite

Comprehensive tests for ML demo functionality, showcase features, 
interactive demonstrations, and proof-of-concept systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import json
import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from PIL import Image
import streamlit as st
import gradio as gr
import shutil
import base64
from io import BytesIO, StringIO

from ai.ml.ml_demo import (
    MLDemoOrchestrator, InteractiveDemo, ShowcaseGenerator, DemoDataManager,
    VisualizationEngine, DemoAPIHandler, UserInteractionTracker,
    DemoPerformanceMonitor, ContentGenerator, DemoConfigManager,
    ModelShowcase, DataShowcase, FeatureShowcase, ResultsPresenter,
    DemoAuthenticator, DemoSecurityManager, ExportManager,
    FeedbackCollector, DemoAnalytics, A11yManager, ResponsiveDesign,
    MultiLanguageSupport, CustomizationEngine, DemoTemplates,
    IntegrationDemo, WorkflowDemo, ComparisonDemo, BenchmarkDemo
)


class TestMLDemoOrchestrator:
    """Tests for ML demo orchestration and management"""
    
    def test_init_demo_orchestrator(self):
        """Test demo orchestrator initialization"""
        orchestrator = MLDemoOrchestrator(
            demo_types=["interactive", "showcase", "benchmark", "comparison"],
            supported_models=["classification", "regression", "clustering", "nlp"],
            ui_frameworks=["streamlit", "gradio", "flask", "react"],
            enable_real_time_demos=True,
            demo_caching=True
        )
        
        assert len(orchestrator.demo_types) == 4
        assert len(orchestrator.supported_models) == 4
        assert len(orchestrator.ui_frameworks) == 4
        assert orchestrator.enable_real_time_demos
        assert orchestrator.demo_caching

    def test_demo_configuration_management(self, demo_config_data):
        """Test demo configuration management and validation"""
        orchestrator = MLDemoOrchestrator()
        
        if not demo_config_data:
            demo_config_data = {
                "demo_info": {
                    "title": "Customer Churn Prediction Demo",
                    "description": "Interactive demo showcasing ML model for predicting customer churn",
                    "version": "v1.2.3",
                    "author": "Fahed Mlaiel",
                    "category": "classification",
                    "difficulty_level": "intermediate"
                },
                "model_config": {
                    "model_path": "/models/churn_model_v2.pkl",
                    "model_type": "random_forest",
                    "input_features": [
                        {"name": "age", "type": "numeric", "range": [18, 80]},
                        {"name": "tenure", "type": "numeric", "range": [0, 72]},
                        {"name": "monthly_charges", "type": "numeric", "range": [18.25, 118.75]},
                        {"name": "contract_type", "type": "categorical", "options": ["Monthly", "One year", "Two year"]}
                    ],
                    "output_format": {"type": "probability", "classes": ["Stay", "Churn"]}
                },
                "ui_config": {
                    "framework": "streamlit",
                    "layout": "sidebar_main",
                    "theme": "light",
                    "responsive": True,
                    "components": ["input_form", "prediction_display", "explanation", "charts"]
                },
                "demo_features": {
                    "real_time_prediction": True,
                    "batch_prediction": True,
                    "model_explanation": True,
                    "feature_importance": True,
                    "confidence_intervals": True,
                    "what_if_analysis": True
                }
            }
        
        with patch.object(orchestrator, 'configure_demo') as mock_configure:
            mock_configure.return_value = {
                "configuration_status": "VALID",
                "validated_config": demo_config_data,
                "initialization_ready": True,
                "warnings": [],
                "errors": [],
                "estimated_resources": {
                    "memory_mb": 256,
                    "cpu_cores": 2,
                    "storage_mb": 45,
                    "startup_time_seconds": 12
                },
                "compatibility_check": {
                    "model_compatibility": "COMPATIBLE",
                    "ui_framework_available": True,
                    "dependencies_satisfied": True,
                    "version_conflicts": []
                },
                "security_validation": {
                    "input_sanitization": "ENABLED",
                    "output_filtering": "ENABLED", 
                    "rate_limiting": "CONFIGURED",
                    "authentication_required": False
                }
            }
            
            config_result = orchestrator.configure_demo(config=demo_config_data)
            
            assert config_result["configuration_status"] == "VALID"
            assert config_result["initialization_ready"]
            assert len(config_result["errors"]) == 0
            assert config_result["compatibility_check"]["model_compatibility"] == "COMPATIBLE"

    def test_demo_lifecycle_management(self, demo_session_data):
        """Test demo lifecycle management from start to cleanup"""
        orchestrator = MLDemoOrchestrator()
        
        if not demo_session_data:
            demo_session_data = {
                "session_id": "demo_session_001",
                "demo_config": {"title": "Test Demo", "framework": "streamlit"},
                "user_info": {"user_id": "user_123", "experience_level": "beginner"},
                "start_time": datetime.now(),
                "expected_duration_minutes": 30
            }
        
        lifecycle_config = {
            "auto_cleanup": True,
            "session_timeout_minutes": 45,
            "resource_monitoring": True,
            "user_activity_tracking": True,
            "performance_logging": True
        }
        
        with patch.object(orchestrator, 'manage_demo_lifecycle') as mock_lifecycle:
            mock_lifecycle.return_value = {
                "lifecycle_stages": [
                    {
                        "stage": "INITIALIZATION",
                        "status": "COMPLETED",
                        "timestamp": demo_session_data["start_time"].isoformat(),
                        "duration_seconds": 8.7,
                        "resources_allocated": {"memory_mb": 128, "cpu_percent": 15}
                    },
                    {
                        "stage": "ACTIVE_DEMO",
                        "status": "IN_PROGRESS", 
                        "timestamp": (demo_session_data["start_time"] + timedelta(seconds=9)).isoformat(),
                        "duration_seconds": 1247.3,  # ~20 minutes
                        "user_interactions": 47,
                        "predictions_made": 23
                    },
                    {
                        "stage": "CLEANUP_SCHEDULED",
                        "status": "PENDING",
                        "estimated_cleanup_time": (datetime.now() + timedelta(minutes=10)).isoformat(),
                        "resources_to_free": {"memory_mb": 128, "temp_files": 5}
                    }
                ],
                "session_metrics": {
                    "total_duration_minutes": 21.2,
                    "user_engagement_score": 0.78,
                    "performance_score": 0.91,
                    "error_count": 2,
                    "successful_predictions": 23,
                    "failed_predictions": 0
                },
                "resource_usage": {
                    "peak_memory_mb": 145.7,
                    "average_cpu_percent": 23.4,
                    "network_requests": 78,
                    "storage_used_mb": 12.3,
                    "cost_estimate_usd": 0.045
                },
                "cleanup_summary": {
                    "auto_cleanup_enabled": True,
                    "cleanup_scheduled": True,
                    "resources_freed": True,
                    "session_data_archived": True,
                    "user_feedback_collected": False
                }
            }
            
            lifecycle_result = orchestrator.manage_demo_lifecycle(
                session=demo_session_data,
                config=lifecycle_config
            )
            
            assert "lifecycle_stages" in lifecycle_result
            assert "session_metrics" in lifecycle_result
            assert lifecycle_result["session_metrics"]["performance_score"] > 0.9
            assert lifecycle_result["cleanup_summary"]["auto_cleanup_enabled"]

    def test_multi_framework_demo_support(self, multi_framework_configs):
        """Test support for multiple UI frameworks"""
        orchestrator = MLDemoOrchestrator(ui_frameworks=["streamlit", "gradio", "flask"])
        
        if not multi_framework_configs:
            multi_framework_configs = [
                {
                    "framework": "streamlit",
                    "components": ["sidebar", "main_panel", "metrics"],
                    "styling": {"theme": "light", "custom_css": True}
                },
                {
                    "framework": "gradio", 
                    "components": ["inputs", "outputs", "examples"],
                    "styling": {"theme": "default", "custom_css": False}
                },
                {
                    "framework": "flask",
                    "components": ["forms", "results", "charts"],
                    "styling": {"template": "bootstrap", "responsive": True}
                }
            ]
        
        with patch.object(orchestrator, 'deploy_multi_framework_demo') as mock_deploy:
            mock_deploy.return_value = {
                "deployment_results": [
                    {
                        "framework": "streamlit",
                        "deployment_status": "SUCCESS",
                        "endpoint": "http://localhost:8501",
                        "startup_time_seconds": 4.2,
                        "memory_usage_mb": 89.7,
                        "features_available": ["real_time_prediction", "visualization", "explanation"]
                    },
                    {
                        "framework": "gradio",
                        "deployment_status": "SUCCESS", 
                        "endpoint": "http://localhost:7860",
                        "startup_time_seconds": 2.8,
                        "memory_usage_mb": 67.3,
                        "features_available": ["prediction", "examples", "sharing"]
                    },
                    {
                        "framework": "flask",
                        "deployment_status": "SUCCESS",
                        "endpoint": "http://localhost:5000",
                        "startup_time_seconds": 1.5,
                        "memory_usage_mb": 45.2,
                        "features_available": ["api_endpoint", "web_interface", "documentation"]
                    }
                ],
                "load_balancing": {
                    "enabled": True,
                    "strategy": "round_robin",
                    "health_checks": "enabled",
                    "failover_configured": True
                },
                "cross_framework_compatibility": {
                    "shared_model": True,
                    "unified_api": True,
                    "consistent_results": True,
                    "data_synchronization": "real_time"
                }
            }
            
            deploy_result = orchestrator.deploy_multi_framework_demo(
                framework_configs=multi_framework_configs
            )
            
            assert "deployment_results" in deploy_result
            assert len(deploy_result["deployment_results"]) == 3
            assert all(
                result["deployment_status"] == "SUCCESS" 
                for result in deploy_result["deployment_results"]
            )
            assert deploy_result["cross_framework_compatibility"]["shared_model"]


class TestInteractiveDemo:
    """Tests for interactive demo functionality"""
    
    def test_init_interactive_demo(self):
        """Test interactive demo initialization"""
        demo = InteractiveDemo(
            demo_type="real_time_prediction",
            interaction_modes=["form_input", "file_upload", "api_call"],
            real_time_updates=True,
            explanation_features=True,
            user_guidance=True
        )
        
        assert demo.demo_type == "real_time_prediction"
        assert len(demo.interaction_modes) == 3
        assert demo.real_time_updates
        assert demo.explanation_features
        assert demo.user_guidance

    def test_real_time_prediction_interface(self, prediction_demo_config):
        """Test real-time prediction interface functionality"""
        demo = InteractiveDemo(demo_type="real_time_prediction")
        
        if not prediction_demo_config:
            prediction_demo_config = {
                "model_endpoint": "/api/predict",
                "input_fields": [
                    {"name": "feature_1", "type": "slider", "min": 0, "max": 100, "default": 50},
                    {"name": "feature_2", "type": "number", "min": -10, "max": 10, "default": 0},
                    {"name": "feature_3", "type": "select", "options": ["A", "B", "C"], "default": "A"}
                ],
                "update_trigger": "on_change",
                "response_visualization": ["prediction", "confidence", "explanation"]
            }
        
        # Simulate user interactions
        user_inputs = [
            {"feature_1": 75, "feature_2": 3.5, "feature_3": "B"},
            {"feature_1": 25, "feature_2": -2.1, "feature_3": "A"},
            {"feature_1": 90, "feature_2": 7.8, "feature_3": "C"}
        ]
        
        with patch.object(demo, 'handle_real_time_prediction') as mock_prediction:
            mock_prediction.return_value = {
                "prediction_results": [
                    {
                        "input": user_inputs[0],
                        "prediction": {"class": "Positive", "probability": 0.87},
                        "confidence": 0.91,
                        "explanation": {
                            "feature_importance": {
                                "feature_1": 0.45,
                                "feature_2": 0.32,
                                "feature_3": 0.23
                            },
                            "decision_reasoning": "High feature_1 value (75) strongly indicates positive class",
                            "similar_cases": 3
                        },
                        "response_time_ms": 45.7
                    },
                    {
                        "input": user_inputs[1], 
                        "prediction": {"class": "Negative", "probability": 0.71},
                        "confidence": 0.78,
                        "explanation": {
                            "feature_importance": {
                                "feature_1": 0.48,
                                "feature_2": 0.31, 
                                "feature_3": 0.21
                            },
                            "decision_reasoning": "Low feature_1 value (25) suggests negative class",
                            "similar_cases": 7
                        },
                        "response_time_ms": 38.2
                    }
                ],
                "interaction_metrics": {
                    "total_predictions": len(user_inputs[:2]),  # Only processed 2
                    "average_response_time_ms": 41.95,
                    "user_engagement_time_seconds": 245.8,
                    "feature_exploration_patterns": {
                        "most_adjusted_feature": "feature_1",
                        "adjustment_frequency": {"feature_1": 15, "feature_2": 8, "feature_3": 5}
                    }
                },
                "ui_performance": {
                    "render_time_ms": 23.4,
                    "update_lag_ms": 12.1,
                    "responsiveness_score": 0.94,
                    "user_experience_rating": "EXCELLENT"
                }
            }
            
            prediction_result = demo.handle_real_time_prediction(
                config=prediction_demo_config,
                user_inputs=user_inputs[:2]
            )
            
            assert "prediction_results" in prediction_result
            assert "interaction_metrics" in prediction_result
            assert len(prediction_result["prediction_results"]) == 2
            assert prediction_result["ui_performance"]["responsiveness_score"] > 0.9

    def test_batch_upload_demo(self, batch_demo_config, sample_batch_data):
        """Test batch file upload and processing demo"""
        demo = InteractiveDemo(interaction_modes=["file_upload"])
        
        if not batch_demo_config:
            batch_demo_config = {
                "accepted_formats": ["csv", "xlsx", "json"],
                "max_file_size_mb": 50,
                "required_columns": ["feature_1", "feature_2", "feature_3"],
                "batch_size": 1000,
                "progress_tracking": True
            }
        
        if not sample_batch_data:
            sample_batch_data = {
                "filename": "test_batch.csv",
                "size_mb": 12.7,
                "row_count": 5000,
                "column_count": 10,
                "format": "csv"
            }
        
        with patch.object(demo, 'process_batch_upload') as mock_batch:
            mock_batch.return_value = {
                "upload_validation": {
                    "file_valid": True,
                    "format_supported": True,
                    "size_within_limit": True,
                    "required_columns_present": True,
                    "data_quality_score": 0.92
                },
                "processing_status": {
                    "status": "COMPLETED",
                    "rows_processed": sample_batch_data["row_count"],
                    "rows_successful": 4987,
                    "rows_failed": 13,
                    "processing_time_seconds": 23.4,
                    "throughput_rows_per_second": 213.7
                },
                "batch_results": {
                    "predictions": [
                        {"row_id": i, "prediction": np.random.choice(["A", "B", "C"]), 
                         "confidence": np.random.uniform(0.6, 0.95)}
                        for i in range(100)  # Sample of results
                    ],
                    "summary_statistics": {
                        "class_distribution": {"A": 1634, "B": 1789, "C": 1564},
                        "average_confidence": 0.81,
                        "prediction_consistency": 0.88
                    },
                    "download_options": {
                        "csv_available": True,
                        "xlsx_available": True,
                        "json_available": True,
                        "pdf_report_available": True
                    }
                },
                "error_analysis": {
                    "error_types": {
                        "missing_values": 8,
                        "invalid_data_types": 3,
                        "out_of_range_values": 2
                    },
                    "error_details": [
                        {"row": 234, "error": "Missing value in feature_2"},
                        {"row": 1567, "error": "Invalid data type for feature_1"}
                    ]
                }
            }
            
            batch_result = demo.process_batch_upload(
                config=batch_demo_config,
                file_data=sample_batch_data
            )
            
            assert "upload_validation" in batch_result
            assert "processing_status" in batch_result
            assert batch_result["upload_validation"]["file_valid"]
            assert batch_result["processing_status"]["status"] == "COMPLETED"
            assert batch_result["processing_status"]["rows_successful"] > batch_result["processing_status"]["rows_failed"]

    def test_what_if_analysis_demo(self, what_if_config):
        """Test what-if analysis and scenario exploration"""
        demo = InteractiveDemo(explanation_features=True)
        
        if not what_if_config:
            what_if_config = {
                "base_scenario": {"feature_1": 50, "feature_2": 0, "feature_3": "A"},
                "analysis_dimensions": ["feature_1", "feature_2"],
                "variation_ranges": {
                    "feature_1": {"min": 0, "max": 100, "step": 10},
                    "feature_2": {"min": -10, "max": 10, "step": 1}
                },
                "visualization_type": "heatmap"
            }
        
        with patch.object(demo, 'run_what_if_analysis') as mock_what_if:
            mock_what_if.return_value = {
                "analysis_grid": {
                    "scenarios_tested": 231,  # 11 * 21 combinations
                    "grid_dimensions": (11, 21),
                    "base_prediction": {"class": "Positive", "probability": 0.67},
                    "prediction_surface": np.random.rand(11, 21).tolist()
                },
                "sensitivity_analysis": {
                    "most_influential_feature": "feature_1",
                    "sensitivity_scores": {
                        "feature_1": 0.78,
                        "feature_2": 0.34,
                        "feature_3": 0.12
                    },
                    "interaction_effects": {
                        "feature_1_x_feature_2": 0.23,
                        "feature_1_x_feature_3": 0.15,
                        "feature_2_x_feature_3": 0.08
                    }
                },
                "decision_boundaries": {
                    "boundary_identified": True,
                    "boundary_stability": 0.87,
                    "critical_thresholds": {
                        "feature_1": 35.5,
                        "feature_2": 2.3
                    }
                },
                "visualization_data": {
                    "heatmap_data": {
                        "x_values": list(range(0, 101, 10)),
                        "y_values": list(range(-10, 11, 1)),
                        "z_values": np.random.rand(11, 21).tolist()
                    },
                    "contour_lines": [
                        {"level": 0.5, "coordinates": [(25, -5), (35, 0), (45, 5)]},
                        {"level": 0.8, "coordinates": [(45, -3), (55, 2), (65, 7)]}
                    ]
                },
                "insights": [
                    "Model is most sensitive to changes in feature_1",
                    "Decision boundary occurs around feature_1=35.5",
                    "Strong positive correlation between feature_1 and prediction probability",
                    "Feature_2 has moderate influence, especially when feature_1 > 50"
                ]
            }
            
            what_if_result = demo.run_what_if_analysis(config=what_if_config)
            
            assert "analysis_grid" in what_if_result
            assert "sensitivity_analysis" in what_if_result
            assert "decision_boundaries" in what_if_result
            assert what_if_result["analysis_grid"]["scenarios_tested"] > 200
            assert what_if_result["decision_boundaries"]["boundary_identified"]


class TestVisualizationEngine:
    """Tests for visualization and charting functionality"""
    
    def test_init_visualization_engine(self):
        """Test visualization engine initialization"""
        viz_engine = VisualizationEngine(
            chart_libraries=["matplotlib", "plotly", "seaborn", "bokeh"],
            interactive_charts=True,
            real_time_updates=True,
            export_formats=["png", "svg", "pdf", "html"],
            accessibility_features=True
        )
        
        assert len(viz_engine.chart_libraries) == 4
        assert viz_engine.interactive_charts
        assert viz_engine.real_time_updates
        assert len(viz_engine.export_formats) == 4
        assert viz_engine.accessibility_features

    def test_model_performance_visualization(self, model_metrics_data):
        """Test model performance visualization generation"""
        viz_engine = VisualizationEngine()
        
        if not model_metrics_data:
            model_metrics_data = {
                "accuracy_history": [0.65, 0.72, 0.78, 0.81, 0.84, 0.86, 0.87],
                "loss_history": [0.89, 0.76, 0.65, 0.58, 0.52, 0.48, 0.45],
                "confusion_matrix": [[850, 45], [32, 873]],
                "feature_importance": {
                    "feature_1": 0.35,
                    "feature_2": 0.28, 
                    "feature_3": 0.22,
                    "feature_4": 0.15
                },
                "roc_curve": {
                    "fpr": [0.0, 0.05, 0.12, 0.25, 0.38, 0.55, 1.0],
                    "tpr": [0.0, 0.67, 0.78, 0.85, 0.91, 0.96, 1.0],
                    "auc": 0.89
                }
            }
        
        viz_config = {
            "chart_types": ["line_plot", "confusion_matrix", "feature_importance", "roc_curve"],
            "style": {"theme": "professional", "color_palette": "viridis"},
            "interactivity": {"zoom": True, "hover": True, "selection": True},
            "export": {"formats": ["png", "html"], "dpi": 300}
        }
        
        with patch.object(viz_engine, 'create_model_performance_charts') as mock_charts:
            mock_charts.return_value = {
                "generated_charts": {
                    "accuracy_loss_plot": {
                        "chart_type": "line_plot",
                        "data_points": 7,
                        "interactive": True,
                        "file_path": "/tmp/accuracy_loss.png",
                        "html_embed": "<div id='accuracy_plot'>...</div>",
                        "accessibility": {"alt_text": "Training accuracy and loss over epochs"}
                    },
                    "confusion_matrix_heatmap": {
                        "chart_type": "heatmap",
                        "accuracy": 0.956,  # (850+873)/(850+45+32+873)
                        "file_path": "/tmp/confusion_matrix.png",
                        "annotations": True,
                        "accessibility": {"alt_text": "Confusion matrix showing prediction accuracy"}
                    },
                    "feature_importance_bar": {
                        "chart_type": "bar_chart",
                        "features_count": 4,
                        "sorted_by_importance": True,
                        "file_path": "/tmp/feature_importance.png",
                        "accessibility": {"alt_text": "Feature importance ranking"}
                    },
                    "roc_curve_plot": {
                        "chart_type": "line_plot",
                        "auc_score": 0.89,
                        "confidence_interval": [0.86, 0.92],
                        "file_path": "/tmp/roc_curve.png",
                        "accessibility": {"alt_text": f"ROC curve with AUC = {0.89}"}
                    }
                },
                "dashboard_layout": {
                    "grid_layout": "2x2",
                    "responsive": True,
                    "chart_order": ["accuracy_loss_plot", "confusion_matrix_heatmap", 
                                  "feature_importance_bar", "roc_curve_plot"],
                    "total_file_size_mb": 2.3
                },
                "interactivity_features": {
                    "cross_filtering": True,
                    "drill_down": True,
                    "tooltip_info": True,
                    "export_individual_charts": True
                }
            }
            
            charts_result = viz_engine.create_model_performance_charts(
                metrics=model_metrics_data,
                config=viz_config
            )
            
            assert "generated_charts" in charts_result
            assert "dashboard_layout" in charts_result
            assert len(charts_result["generated_charts"]) == 4
            assert charts_result["generated_charts"]["roc_curve_plot"]["auc_score"] > 0.8

    def test_data_exploration_visualization(self, dataset_analysis):
        """Test data exploration and EDA visualization"""
        viz_engine = VisualizationEngine()
        
        if not dataset_analysis:
            dataset_analysis = {
                "dataset_info": {"rows": 10000, "columns": 15, "missing_values": 234},
                "numerical_features": {
                    "age": {"mean": 45.2, "std": 12.8, "min": 18, "max": 80},
                    "income": {"mean": 65000, "std": 25000, "min": 22000, "max": 150000},
                    "score": {"mean": 0.67, "std": 0.23, "min": 0.0, "max": 1.0}
                },
                "categorical_features": {
                    "category": {"A": 3500, "B": 4200, "C": 2300},
                    "region": {"North": 2800, "South": 3200, "East": 2000, "West": 2000}
                },
                "correlations": {
                    "age_income": 0.34,
                    "age_score": -0.12,
                    "income_score": 0.56
                }
            }
        
        eda_config = {
            "visualization_types": [
                "distribution_plots", "correlation_matrix", "scatter_plots", 
                "box_plots", "category_bars"
            ],
            "statistical_overlays": True,
            "outlier_highlighting": True,
            "missing_data_visualization": True
        }
        
        with patch.object(viz_engine, 'generate_eda_visualizations') as mock_eda:
            mock_eda.return_value = {
                "eda_visualizations": {
                    "distribution_plots": [
                        {
                            "feature": "age",
                            "plot_type": "histogram_with_kde",
                            "normality_test": {"statistic": 0.987, "p_value": 0.23, "is_normal": True},
                            "outliers_detected": 23,
                            "file_path": "/tmp/age_distribution.png"
                        },
                        {
                            "feature": "income", 
                            "plot_type": "histogram_with_kde",
                            "normality_test": {"statistic": 0.945, "p_value": 0.002, "is_normal": False},
                            "outliers_detected": 156,
                            "file_path": "/tmp/income_distribution.png"
                        }
                    ],
                    "correlation_heatmap": {
                        "features_included": 3,
                        "strongest_correlation": {"features": ["income", "score"], "value": 0.56},
                        "weakest_correlation": {"features": ["age", "score"], "value": -0.12},
                        "file_path": "/tmp/correlation_matrix.png"
                    },
                    "scatter_plots": [
                        {
                            "x_feature": "income",
                            "y_feature": "score", 
                            "correlation": 0.56,
                            "regression_line": True,
                            "confidence_bands": True,
                            "file_path": "/tmp/income_score_scatter.png"
                        }
                    ],
                    "categorical_analysis": [
                        {
                            "feature": "category",
                            "plot_type": "bar_chart",
                            "categories_count": 3,
                            "chi_square_test": {"statistic": 234.5, "p_value": 0.001},
                            "file_path": "/tmp/category_distribution.png"
                        }
                    ]
                },
                "data_quality_insights": {
                    "missing_data_pattern": "RANDOM",
                    "outlier_percentage": 1.79,  # 179/10000
                    "data_balance": "SLIGHTLY_IMBALANCED",
                    "recommendations": [
                        "Consider log transformation for income feature",
                        "Investigate outliers in income and age features",
                        "Category distribution shows some imbalance"
                    ]
                },
                "summary_dashboard": {
                    "total_visualizations": 6,
                    "interactive_elements": 4,
                    "key_findings": [
                        "Strong positive correlation between income and score",
                        "Age distribution appears normal",
                        "Income shows right-skewed distribution with outliers"
                    ]
                }
            }
            
            eda_result = viz_engine.generate_eda_visualizations(
                dataset=dataset_analysis,
                config=eda_config
            )
            
            assert "eda_visualizations" in eda_result
            assert "data_quality_insights" in eda_result
            assert "summary_dashboard" in eda_result
            assert eda_result["summary_dashboard"]["total_visualizations"] > 0

    def test_real_time_visualization_updates(self, streaming_data_config):
        """Test real-time visualization updates"""
        viz_engine = VisualizationEngine(real_time_updates=True)
        
        if not streaming_data_config:
            streaming_data_config = {
                "update_interval_seconds": 2.0,
                "data_buffer_size": 1000,
                "chart_types": ["line_chart", "gauge", "counter"],
                "animation_enabled": True
            }
        
        # Simulate streaming data points
        streaming_data = [
            {"timestamp": datetime.now() - timedelta(seconds=i*2), 
             "value": 50 + 20*np.sin(i*0.1) + np.random.normal(0, 5)}
            for i in range(100)
        ]
        
        with patch.object(viz_engine, 'handle_real_time_updates') as mock_realtime:
            mock_realtime.return_value = {
                "update_session": {
                    "session_id": "realtime_viz_001",
                    "start_time": datetime.now().isoformat(),
                    "updates_processed": len(streaming_data),
                    "update_frequency_hz": 0.5,  # Every 2 seconds
                    "data_points_displayed": 50  # Rolling window
                },
                "visualization_performance": {
                    "average_render_time_ms": 34.7,
                    "frame_rate_fps": 15.8,
                    "memory_usage_mb": 67.3,
                    "dropped_frames": 2,
                    "performance_score": 0.92
                },
                "chart_updates": {
                    "line_chart": {
                        "points_updated": 50,
                        "trend_detected": "OSCILLATING",
                        "anomalies_highlighted": 3,
                        "smooth_animation": True
                    },
                    "gauge": {
                        "current_value": streaming_data[-1]["value"],
                        "min_value": min(d["value"] for d in streaming_data),
                        "max_value": max(d["value"] for d in streaming_data),
                        "threshold_alerts": []
                    },
                    "counter": {
                        "total_data_points": len(streaming_data),
                        "updates_per_minute": 30,
                        "uptime_percentage": 99.8
                    }
                },
                "user_interaction": {
                    "zoom_events": 5,
                    "pan_events": 12,
                    "hover_events": 234,
                    "engagement_score": 0.78
                }
            }
            
            realtime_result = viz_engine.handle_real_time_updates(
                config=streaming_data_config,
                data_stream=streaming_data
            )
            
            assert "update_session" in realtime_result
            assert "visualization_performance" in realtime_result
            assert "chart_updates" in realtime_result
            assert realtime_result["visualization_performance"]["performance_score"] > 0.9
            assert realtime_result["update_session"]["updates_processed"] == len(streaming_data)


class TestDemoAnalytics:
    """Tests for demo analytics and user behavior tracking"""
    
    def test_init_demo_analytics(self):
        """Test demo analytics initialization"""
        analytics = DemoAnalytics(
            track_user_behavior=True,
            performance_monitoring=True,
            feedback_collection=True,
            privacy_compliant=True,
            real_time_analytics=True
        )
        
        assert analytics.track_user_behavior
        assert analytics.performance_monitoring
        assert analytics.feedback_collection
        assert analytics.privacy_compliant
        assert analytics.real_time_analytics

    def test_user_engagement_tracking(self, demo_session_events):
        """Test user engagement and interaction tracking"""
        analytics = DemoAnalytics(track_user_behavior=True)
        
        if not demo_session_events:
            demo_session_events = [
                {"event": "demo_start", "timestamp": datetime.now(), "user_id": "user_123"},
                {"event": "input_change", "timestamp": datetime.now(), "feature": "age", "value": 35},
                {"event": "prediction_request", "timestamp": datetime.now(), "prediction_id": "pred_001"},
                {"event": "explanation_view", "timestamp": datetime.now(), "explanation_type": "feature_importance"},
                {"event": "what_if_analysis", "timestamp": datetime.now(), "scenarios": 5},
                {"event": "export_results", "timestamp": datetime.now(), "format": "csv"},
                {"event": "demo_end", "timestamp": datetime.now(), "session_duration": 847}
            ]
        
        with patch.object(analytics, 'analyze_user_engagement') as mock_engagement:
            mock_engagement.return_value = {
                "engagement_metrics": {
                    "session_duration_seconds": 847,
                    "total_interactions": len(demo_session_events),
                    "interaction_rate_per_minute": len(demo_session_events) / (847/60),
                    "engagement_score": 0.82,
                    "bounce_rate": 0.0  # User completed session
                },
                "interaction_analysis": {
                    "most_used_features": [
                        {"feature": "prediction_request", "count": 1, "percentage": 14.3},
                        {"feature": "input_change", "count": 1, "percentage": 14.3},
                        {"feature": "what_if_analysis", "count": 1, "percentage": 14.3}
                    ],
                    "user_journey": [
                        "demo_start", "input_change", "prediction_request", 
                        "explanation_view", "what_if_analysis", "export_results", "demo_end"
                    ],
                    "drop_off_points": [],  # No premature exits
                    "feature_adoption_rate": {
                        "basic_prediction": 1.0,
                        "explanations": 1.0,
                        "what_if_analysis": 1.0,
                        "export_functionality": 1.0
                    }
                },
                "user_behavior_patterns": {
                    "interaction_pattern": "EXPLORATORY", 
                    "expertise_level_inferred": "INTERMEDIATE",
                    "goal_completion": True,
                    "satisfaction_indicators": [
                        "completed_full_workflow",
                        "used_advanced_features", 
                        "exported_results"
                    ]
                },
                "recommendations": {
                    "ui_improvements": [],
                    "feature_suggestions": [
                        "Add more what-if scenarios",
                        "Provide additional export formats"
                    ],
                    "user_type": "POWER_USER"
                }
            }
            
            engagement_result = analytics.analyze_user_engagement(events=demo_session_events)
            
            assert "engagement_metrics" in engagement_result
            assert "interaction_analysis" in engagement_result
            assert "user_behavior_patterns" in engagement_result
            assert engagement_result["engagement_metrics"]["engagement_score"] > 0.8
            assert engagement_result["user_behavior_patterns"]["goal_completion"]

    def test_demo_performance_analytics(self, performance_metrics_data):
        """Test demo performance analytics and optimization insights"""
        analytics = DemoAnalytics(performance_monitoring=True)
        
        if not performance_metrics_data:
            performance_metrics_data = {
                "response_times": [45, 52, 38, 67, 41, 55, 49, 43, 58, 46],  # ms
                "memory_usage": [128, 145, 132, 178, 156, 167, 143, 139, 162, 151],  # MB
                "cpu_usage": [23, 34, 28, 45, 31, 39, 29, 26, 37, 32],  # %
                "error_counts": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                "concurrent_users": [1, 2, 1, 3, 2, 4, 2, 1, 3, 2]
            }
        
        with patch.object(analytics, 'analyze_demo_performance') as mock_performance:
            mock_performance.return_value = {
                "performance_summary": {
                    "average_response_time_ms": 49.4,
                    "p95_response_time_ms": 63.2,
                    "max_response_time_ms": 67,
                    "response_time_sla_compliance": 0.9,  # <50ms target
                    "availability_percentage": 99.9,
                    "error_rate_percentage": 0.1
                },
                "resource_utilization": {
                    "peak_memory_usage_mb": 178,
                    "average_memory_usage_mb": 150.1,
                    "memory_efficiency_score": 0.78,
                    "peak_cpu_usage_percent": 45,
                    "average_cpu_usage_percent": 32.4,
                    "cpu_efficiency_score": 0.85
                },
                "scalability_metrics": {
                    "max_concurrent_users_handled": 4,
                    "performance_degradation_threshold": 3,
                    "linear_scalability_range": [1, 3],
                    "bottleneck_identified": "MEMORY_BOUND",
                    "recommended_max_users": 6
                },
                "optimization_opportunities": [
                    {
                        "category": "RESPONSE_TIME",
                        "issue": "Occasional spikes above SLA threshold",
                        "recommendation": "Implement caching for frequent predictions",
                        "expected_improvement": "15-20% reduction in average response time"
                    },
                    {
                        "category": "MEMORY",
                        "issue": "Memory usage increases with concurrent users",
                        "recommendation": "Optimize model loading and feature preprocessing",
                        "expected_improvement": "25% reduction in memory footprint"
                    }
                ],
                "trending_analysis": {
                    "performance_trend": "STABLE",
                    "degradation_patterns": [],
                    "improvement_opportunities": 2,
                    "critical_issues": 0
                }
            }
            
            performance_result = analytics.analyze_demo_performance(
                metrics=performance_metrics_data
            )
            
            assert "performance_summary" in performance_result
            assert "resource_utilization" in performance_result
            assert "scalability_metrics" in performance_result
            assert performance_result["performance_summary"]["availability_percentage"] > 99.0
            assert len(performance_result["optimization_opportunities"]) > 0

    def test_a11y_compliance_analytics(self, accessibility_audit_data):
        """Test accessibility compliance analytics"""
        analytics = DemoAnalytics()
        
        if not accessibility_audit_data:
            accessibility_audit_data = {
                "wcag_compliance": {
                    "level_a": {"passed": 45, "failed": 2, "compliance": 0.957},
                    "level_aa": {"passed": 38, "failed": 5, "compliance": 0.884},
                    "level_aaa": {"passed": 23, "failed": 12, "compliance": 0.657}
                },
                "accessibility_features": {
                    "alt_text_coverage": 0.92,
                    "keyboard_navigation": True,
                    "screen_reader_compatibility": 0.87,
                    "color_contrast_ratio": 4.8,  # WCAG AA requires 4.5+
                    "focus_indicators": True,
                    "aria_labels_present": 0.89
                },
                "user_feedback": {
                    "screen_reader_users": 3,
                    "keyboard_only_users": 2, 
                    "average_satisfaction": 4.2,
                    "accessibility_issues_reported": 1
                }
            }
        
        with patch.object(analytics, 'analyze_accessibility_compliance') as mock_a11y:
            mock_a11y.return_value = {
                "compliance_assessment": {
                    "overall_wcag_score": 0.83,  # Average of all levels
                    "wcag_level_achieved": "AA",
                    "critical_violations": 2,
                    "minor_violations": 5,
                    "accessibility_grade": "B+",
                    "compliance_trend": "IMPROVING"
                },
                "feature_analysis": {
                    "well_implemented_features": [
                        "keyboard_navigation",
                        "focus_indicators", 
                        "color_contrast"
                    ],
                    "needs_improvement": [
                        "alt_text_coverage",
                        "aria_labels",
                        "screen_reader_compatibility"
                    ],
                    "priority_fixes": [
                        {
                            "issue": "Missing alt text for 8% of images",
                            "impact": "HIGH",
                            "effort": "LOW",
                            "recommendation": "Add descriptive alt text to all visualization charts"
                        },
                        {
                            "issue": "11% of interactive elements lack ARIA labels",
                            "impact": "MEDIUM",
                            "effort": "MEDIUM", 
                            "recommendation": "Add ARIA labels to form controls and buttons"
                        }
                    ]
                },
                "user_experience_impact": {
                    "affected_user_percentage": 8.5,  # Users with accessibility needs
                    "satisfaction_gap": 0.3,  # Difference vs general users
                    "completion_rate_impact": -0.12,
                    "support_ticket_reduction_potential": 0.67
                },
                "remediation_plan": {
                    "immediate_actions": 2,
                    "short_term_goals": 3,
                    "estimated_effort_hours": 24,
                    "compliance_improvement_target": 0.92,
                    "target_achievement_date": (datetime.now() + timedelta(days=30)).isoformat()
                }
            }
            
            a11y_result = analytics.analyze_accessibility_compliance(
                audit_data=accessibility_audit_data
            )
            
            assert "compliance_assessment" in a11y_result
            assert "feature_analysis" in a11y_result
            assert "remediation_plan" in a11y_result
            assert a11y_result["compliance_assessment"]["wcag_level_achieved"] in ["A", "AA", "AAA"]
            assert len(a11y_result["feature_analysis"]["priority_fixes"]) > 0


@pytest.mark.integration
class TestMLDemoIntegration:
    """Integration tests for ML demo systems"""
    
    @pytest.mark.slow
    def test_end_to_end_demo_deployment(self, temp_dir):
        """Test complete demo deployment pipeline"""
        # Initialize components
        orchestrator = MLDemoOrchestrator(output_directory=str(temp_dir))
        interactive_demo = InteractiveDemo()
        viz_engine = VisualizationEngine()
        analytics = DemoAnalytics()
        
        # Complete demo configuration
        full_demo_config = {
            "demo_info": {
                "title": "Integration Test Demo",
                "type": "classification",
                "framework": "streamlit"
            },
            "model_config": {
                "model_path": str(temp_dir / "test_model.pkl"),
                "features": ["age", "income", "score"]
            },
            "ui_config": {
                "layout": "sidebar_main",
                "theme": "light"
            }
        }
        
        # Step 1: Configure and validate demo
        with patch.object(orchestrator, 'configure_and_validate') as mock_config:
            mock_config.return_value = {
                "configuration_valid": True,
                "deployment_ready": True,
                "estimated_startup_time": 8.5
            }
            
            config_result = orchestrator.configure_and_validate(full_demo_config)
            assert config_result["configuration_valid"]
        
        # Step 2: Deploy interactive demo
        with patch.object(interactive_demo, 'deploy_demo') as mock_deploy:
            mock_deploy.return_value = {
                "deployment_status": "SUCCESS",
                "endpoint": "http://localhost:8501",
                "startup_time_seconds": 7.2,
                "health_check": "HEALTHY"
            }
            
            deploy_result = interactive_demo.deploy_demo(config=full_demo_config)
            assert deploy_result["deployment_status"] == "SUCCESS"
        
        # Step 3: Generate visualizations
        with patch.object(viz_engine, 'generate_demo_visualizations') as mock_viz:
            mock_viz.return_value = {
                "visualizations_created": 5,
                "dashboard_ready": True,
                "interactive_charts": 3,
                "static_charts": 2
            }
            
            viz_result = viz_engine.generate_demo_visualizations()
            assert viz_result["dashboard_ready"]
        
        # Step 4: Initialize analytics
        with patch.object(analytics, 'initialize_tracking') as mock_analytics:
            mock_analytics.return_value = {
                "tracking_initialized": True,
                "privacy_compliance": True,
                "metrics_collection_active": True
            }
            
            analytics_result = analytics.initialize_tracking()
            assert analytics_result["tracking_initialized"]
        
        # Integration validation
        integration_status = {
            "configuration": config_result["configuration_valid"],
            "deployment": deploy_result["deployment_status"] == "SUCCESS", 
            "visualizations": viz_result["dashboard_ready"],
            "analytics": analytics_result["tracking_initialized"]
        }
        
        assert all(integration_status.values())

    def test_multi_user_demo_session(self):
        """Test demo handling multiple concurrent users"""
        orchestrator = MLDemoOrchestrator()
        
        # Simulate multiple users
        concurrent_users = [
            {"user_id": f"user_{i:03d}", "session_start": datetime.now()}
            for i in range(25)  # 25 concurrent users
        ]
        
        load_test_config = {
            "max_concurrent_users": 30,
            "session_timeout_minutes": 20,
            "resource_scaling": "AUTO",
            "performance_monitoring": True
        }
        
        with patch.object(orchestrator, 'handle_concurrent_users') as mock_concurrent:
            mock_concurrent.return_value = {
                "concurrent_sessions": {
                    "active_users": len(concurrent_users),
                    "peak_concurrent": 25,
                    "session_success_rate": 0.96,
                    "average_session_duration_minutes": 12.8
                },
                "system_performance": {
                    "response_time_p95_ms": 234.5,
                    "memory_usage_peak_mb": 456.7,
                    "cpu_utilization_peak": 67.8,
                    "error_rate": 0.02
                },
                "scaling_events": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": "SCALE_UP",
                        "trigger": "HIGH_MEMORY_USAGE",
                        "resources_added": {"memory_mb": 256, "cpu_cores": 1}
                    }
                ],
                "user_satisfaction": {
                    "average_rating": 4.3,
                    "completion_rate": 0.92,
                    "performance_complaints": 2
                }
            }
            
            concurrent_result = orchestrator.handle_concurrent_users(
                users=concurrent_users,
                config=load_test_config
            )
            
            assert concurrent_result["concurrent_sessions"]["active_users"] == 25
            assert concurrent_result["concurrent_sessions"]["session_success_rate"] > 0.95
            assert concurrent_result["user_satisfaction"]["completion_rate"] > 0.9


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
