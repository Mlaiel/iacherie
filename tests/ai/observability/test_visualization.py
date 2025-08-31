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
Ultra-Industrial Test Suite for Visualization Module

This module provides comprehensive testing for visualization engines,
chart generators, dashboard renderers, and interactive plotters.

Expert Team Specialties:
 Lead Dev + Architecte Développeur IA
 Développeur Backend Senior (Python/FastAPI/Django)
 Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
 DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
 Spécialiste Sécurité Backend
 Architecte Microservices
 Développeur Audio
 DevOps Engineer
 IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  STRICT LEGAL WARNING & COPYRIGHT PROTECTION 
This entire test suite is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.

 UNAUTHORIZED USE STRICTLY PROHIBITED:
- NO copying, cloning, or replication without explicit written authorization
- NO commercial use without licensing agreement  
- NO redistribution under any circumstances
- NO reverse engineering or code analysis

 LEGAL CONSEQUENCES:
Any attempt to steal, copy, or use this code/concept without explicit written permission
from Fahed Mlaiel will result in immediate legal action under German and international
copyright law, financial damages claims, and criminal prosecution where applicable.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import json
import numpy as np
import pandas as pd
import pytest
import sys
import os
from pathlib import Path
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Import the module under test
from ai.observability.visualization import (
    VisualizationEngine,
    ChartGenerator,
    DashboardRenderer,
    RealtimeVisualizer,
    BusinessVisualization,
    TechnicalVisualization,
    InteractivePlotter,
    DataVisualizer,
    MetricsVisualizer,
    ChartType,
    VisualizationTheme,
    InteractionType,
    DataFormat,
    RenderingBackend
)


class TestVisualizationEngine:
    """Ultra-industrial tests for VisualizationEngine class"""
    
    @pytest.fixture
    def visualization_engine(self):
        """Create VisualizationEngine instance for testing"""
        config = {
            "supported_backends": ["plotly", "d3js", "matplotlib", "bokeh"],
            "default_theme": "professional",
            "caching_enabled": True,
            "real_time_enabled": True,
            "export_formats": ["png", "svg", "pdf", "html", "json"],
            "performance_optimization": True
        }
        return VisualizationEngine(config)
    
    @pytest.fixture
    def comprehensive_dataset(self):
        """Generate comprehensive dataset for visualization testing"""
        # Time series data
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        time_series_data = []
        
        for i, date in enumerate(dates):
            base_value = 1000
            trend = i * 0.5
            seasonal = 200 * np.sin(2 * np.pi * i / 365.25)
            weekly = 100 * np.sin(2 * np.pi * i / 7)
            noise = np.random.normal(0, 50)
            
            value = base_value + trend + seasonal + weekly + noise
            
            time_series_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "revenue": max(0, value),
                "users": int(value / 10) + np.random.randint(-20, 20),
                "engagement": np.random.uniform(0.3, 0.9),
                "category": np.random.choice(["premium", "standard", "basic"])
            })
        
        # Categorical data
        categorical_data = [
            {"category": "Content Creation", "value": 45.2, "subcategory": "Video"},
            {"category": "Content Creation", "value": 32.1, "subcategory": "Image"},
            {"category": "Content Creation", "value": 22.7, "subcategory": "Audio"},
            {"category": "AI Processing", "value": 67.8, "subcategory": "Copyright Detection"},
            {"category": "AI Processing", "value": 54.3, "subcategory": "Watermarking"},
            {"category": "AI Processing", "value": 38.9, "subcategory": "Quality Assessment"},
            {"category": "User Engagement", "value": 76.4, "subcategory": "Social Sharing"},
            {"category": "User Engagement", "value": 63.2, "subcategory": "Comments"},
            {"category": "User Engagement", "value": 58.7, "subcategory": "Likes"}
        ]
        
        # Geographic data
        geographic_data = [
            {"country": "Germany", "users": 15420, "revenue": 248750, "lat": 51.1657, "lon": 10.4515},
            {"country": "France", "users": 12350, "revenue": 195800, "lat": 46.2276, "lon": 2.2137},
            {"country": "United Kingdom", "users": 9870, "revenue": 167400, "lat": 55.3781, "lon": -3.4360},
            {"country": "Spain", "users": 8640, "revenue": 142300, "lat": 40.4637, "lon": -3.7492},
            {"country": "Italy", "users": 7530, "revenue": 128900, "lat": 41.8719, "lon": 12.5674},
            {"country": "Netherlands", "users": 6420, "revenue": 115600, "lat": 52.1326, "lon": 5.2913}
        ]
        
        # Network/Graph data
        network_data = {
            "nodes": [
                {"id": "content_upload", "label": "Content Upload", "size": 100, "color": "#1f77b4"},
                {"id": "ai_processing", "label": "AI Processing", "size": 150, "color": "#ff7f0e"},
                {"id": "copyright_check", "label": "Copyright Check", "size": 80, "color": "#2ca02c"},
                {"id": "watermarking", "label": "Watermarking", "size": 90, "color": "#d62728"},
                {"id": "quality_assessment", "label": "Quality Assessment", "size": 70, "color": "#9467bd"},
                {"id": "publication", "label": "Publication", "size": 120, "color": "#8c564b"}
            ],
            "edges": [
                {"source": "content_upload", "target": "ai_processing", "weight": 95, "label": "Process"},
                {"source": "ai_processing", "target": "copyright_check", "weight": 80, "label": "Check"},
                {"source": "ai_processing", "target": "watermarking", "weight": 75, "label": "Mark"},
                {"source": "ai_processing", "target": "quality_assessment", "weight": 70, "label": "Assess"},
                {"source": "copyright_check", "target": "publication", "weight": 60, "label": "Approve"},
                {"source": "watermarking", "target": "publication", "weight": 55, "label": "Protect"},
                {"source": "quality_assessment", "target": "publication", "weight": 50, "label": "Validate"}
            ]
        }
        
        return {
            "time_series": time_series_data,
            "categorical": categorical_data,
            "geographic": geographic_data,
            "network": network_data
        }
    
    def test_initialization(self, visualization_engine):
        """Test VisualizationEngine initialization"""
        assert visualization_engine is not None
        assert "plotly" in visualization_engine.config["supported_backends"]
        assert hasattr(visualization_engine, 'chart_generators')
        assert hasattr(visualization_engine, 'theme_manager')
        assert hasattr(visualization_engine, 'cache_manager')
        assert hasattr(visualization_engine, 'export_manager')
    
    def test_chart_type_support(self, visualization_engine, comprehensive_dataset):
        """Test support for various chart types"""
        # Test line chart creation
        line_chart = visualization_engine.create_chart(
            chart_type=ChartType.LINE,
            data=comprehensive_dataset["time_series"],
            config={
                "x_field": "date",
                "y_field": "revenue",
                "title": "Revenue Trend Over Time"
            }
        )
        
        assert line_chart is not None
        assert line_chart["chart_type"] == ChartType.LINE
        assert "chart_data" in line_chart
        assert "chart_config" in line_chart
        
        # Test bar chart creation
        bar_chart = visualization_engine.create_chart(
            chart_type=ChartType.BAR,
            data=comprehensive_dataset["categorical"],
            config={
                "x_field": "category",
                "y_field": "value",
                "title": "Performance by Category"
            }
        )
        
        assert bar_chart["chart_type"] == ChartType.BAR
        
        # Test pie chart creation
        pie_chart = visualization_engine.create_chart(
            chart_type=ChartType.PIE,
            data=comprehensive_dataset["categorical"][:3],  # First 3 items
            config={
                "value_field": "value",
                "label_field": "subcategory",
                "title": "Content Distribution"
            }
        )
        
        assert pie_chart["chart_type"] == ChartType.PIE
        
        # Test scatter plot creation
        scatter_plot = visualization_engine.create_chart(
            chart_type=ChartType.SCATTER,
            data=comprehensive_dataset["time_series"],
            config={
                "x_field": "users",
                "y_field": "revenue",
                "size_field": "engagement",
                "title": "Users vs Revenue Correlation"
            }
        )
        
        assert scatter_plot["chart_type"] == ChartType.SCATTER
    
    def test_advanced_chart_types(self, visualization_engine, comprehensive_dataset):
        """Test advanced chart types"""
        # Test heatmap creation
        heatmap_data = []
        for day in range(7):
            for hour in range(24):
                heatmap_data.append({
                    "day": day,
                    "hour": hour,
                    "activity": np.random.uniform(0, 100)
                })
        
        heatmap = visualization_engine.create_chart(
            chart_type=ChartType.HEATMAP,
            data=heatmap_data,
            config={
                "x_field": "hour",
                "y_field": "day",
                "value_field": "activity",
                "title": "User Activity Heatmap"
            }
        )
        
        assert heatmap["chart_type"] == ChartType.HEATMAP
        
        # Test treemap creation
        treemap_data = [
            {"category": "Video", "subcategory": "HD", "value": 450},
            {"category": "Video", "subcategory": "4K", "value": 320},
            {"category": "Image", "subcategory": "JPEG", "value": 280},
            {"category": "Image", "subcategory": "PNG", "value": 180},
            {"category": "Audio", "subcategory": "MP3", "value": 150},
            {"category": "Audio", "subcategory": "WAV", "value": 90}
        ]
        
        treemap = visualization_engine.create_chart(
            chart_type=ChartType.TREEMAP,
            data=treemap_data,
            config={
                "hierarchy_fields": ["category", "subcategory"],
                "value_field": "value",
                "title": "Content Type Distribution"
            }
        )
        
        assert treemap["chart_type"] == ChartType.TREEMAP
        
        # Test network diagram creation
        network_diagram = visualization_engine.create_chart(
            chart_type=ChartType.NETWORK,
            data=comprehensive_dataset["network"],
            config={
                "title": "AI Processing Workflow",
                "layout": "force_directed",
                "show_labels": True
            }
        )
        
        assert network_diagram["chart_type"] == ChartType.NETWORK
    
    def test_interactive_features(self, visualization_engine, comprehensive_dataset):
        """Test interactive visualization features"""
        # Create interactive line chart
        interactive_chart = visualization_engine.create_interactive_chart(
            chart_type=ChartType.LINE,
            data=comprehensive_dataset["time_series"],
            interactions=[
                InteractionType.ZOOM,
                InteractionType.PAN,
                InteractionType.HOVER,
                InteractionType.SELECT
            ],
            config={
                "x_field": "date",
                "y_field": "revenue",
                "title": "Interactive Revenue Trend"
            }
        )
        
        assert "interactions_enabled" in interactive_chart
        assert InteractionType.ZOOM in interactive_chart["interactions_enabled"]
        assert InteractionType.HOVER in interactive_chart["interactions_enabled"]
        
        # Test drill-down functionality
        drill_down_chart = visualization_engine.create_drill_down_chart(
            chart_type=ChartType.BAR,
            data=comprehensive_dataset["categorical"],
            drill_down_config={
                "levels": ["category", "subcategory"],
                "enable_breadcrumbs": True
            }
        )
        
        assert "drill_down_enabled" in drill_down_chart
        assert "drill_down_levels" in drill_down_chart
        
        # Test cross-filtering
        cross_filter_charts = visualization_engine.create_cross_filtered_charts([
            {
                "chart_type": ChartType.BAR,
                "data": comprehensive_dataset["categorical"],
                "filter_field": "category"
            },
            {
                "chart_type": ChartType.PIE,
                "data": comprehensive_dataset["categorical"],
                "filter_field": "subcategory"
            }
        ])
        
        assert "cross_filter_enabled" in cross_filter_charts
        assert len(cross_filter_charts["charts"]) == 2
    
    def test_theme_management(self, visualization_engine, comprehensive_dataset):
        """Test theme and styling management"""
        # Test default theme
        default_themed_chart = visualization_engine.create_chart(
            chart_type=ChartType.LINE,
            data=comprehensive_dataset["time_series"][:30],  # First 30 days
            config={
                "x_field": "date",
                "y_field": "revenue",
                "theme": VisualizationTheme.PROFESSIONAL
            }
        )
        
        assert "theme_applied" in default_themed_chart
        assert default_themed_chart["theme_applied"] == VisualizationTheme.PROFESSIONAL
        
        # Test custom theme
        custom_theme = {
            "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
            "background_color": "#ffffff",
            "grid_color": "#e0e0e0",
            "font_family": "Arial, sans-serif",
            "font_size": 12
        }
        
        custom_themed_chart = visualization_engine.create_chart(
            chart_type=ChartType.BAR,
            data=comprehensive_dataset["categorical"],
            config={
                "x_field": "category",
                "y_field": "value",
                "custom_theme": custom_theme
            }
        )
        
        assert "custom_theme_applied" in custom_themed_chart
        
        # Test responsive design
        responsive_chart = visualization_engine.create_responsive_chart(
            chart_type=ChartType.LINE,
            data=comprehensive_dataset["time_series"][:100],
            responsive_config={
                "breakpoints": {
                    "mobile": {"width": 320, "height": 240},
                    "tablet": {"width": 768, "height": 480},
                    "desktop": {"width": 1200, "height": 600}
                },
                "adapt_content": True
            }
        )
        
        assert "responsive_config" in responsive_chart
        assert "breakpoints" in responsive_chart["responsive_config"]
    
    def test_data_processing_and_aggregation(self, visualization_engine, comprehensive_dataset):
        """Test data processing and aggregation for visualization"""
        # Test automatic data aggregation
        aggregated_chart = visualization_engine.create_chart_with_aggregation(
            chart_type=ChartType.BAR,
            data=comprehensive_dataset["time_series"],
            aggregation_config={
                "group_by": "category",
                "aggregation_method": "mean",
                "value_field": "revenue"
            }
        )
        
        assert "data_aggregated" in aggregated_chart
        assert "aggregation_applied" in aggregated_chart
        
        # Test time-based aggregation
        time_aggregated_chart = visualization_engine.create_time_aggregated_chart(
            data=comprehensive_dataset["time_series"],
            time_field="date",
            value_field="revenue",
            aggregation_period="monthly",
            aggregation_method="sum"
        )
        
        assert "time_aggregation_applied" in time_aggregated_chart
        assert "aggregation_period" in time_aggregated_chart
        
        # Test data transformation
        transformed_data = visualization_engine.transform_data_for_visualization(
            data=comprehensive_dataset["time_series"],
            transformations=[
                {"type": "moving_average", "window": 7, "field": "revenue"},
                {"type": "normalize", "field": "users", "method": "min_max"},
                {"type": "percentage_change", "field": "engagement", "period": 1}
            ]
        )
        
        assert "transformations_applied" in transformed_data
        assert len(transformed_data["transformations_applied"]) == 3
    
    def test_export_functionality(self, visualization_engine, comprehensive_dataset):
        """Test chart export functionality"""
        # Create a chart for export testing
        chart = visualization_engine.create_chart(
            chart_type=ChartType.LINE,
            data=comprehensive_dataset["time_series"][:50],
            config={
                "x_field": "date",
                "y_field": "revenue",
                "title": "Export Test Chart"
            }
        )
        
        # Test PNG export
        png_export = visualization_engine.export_chart(
            chart=chart,
            format="png",
            options={
                "width": 800,
                "height": 600,
                "dpi": 300
            }
        )
        
        assert png_export["export_successful"] is True
        assert png_export["format"] == "png"
        assert "file_size" in png_export
        
        # Test SVG export
        svg_export = visualization_engine.export_chart(
            chart=chart,
            format="svg",
            options={"optimize": True}
        )
        
        assert svg_export["export_successful"] is True
        assert svg_export["format"] == "svg"
        
        # Test HTML export
        html_export = visualization_engine.export_chart(
            chart=chart,
            format="html",
            options={
                "include_plotlyjs": "cdn",
                "responsive": True
            }
        )
        
        assert html_export["export_successful"] is True
        assert html_export["format"] == "html"
        
        # Test PDF export
        pdf_export = visualization_engine.export_chart(
            chart=chart,
            format="pdf",
            options={
                "page_size": "A4",
                "orientation": "landscape"
            }
        )
        
        assert pdf_export["export_successful"] is True
        assert pdf_export["format"] == "pdf"
    
    def test_performance_optimization(self, visualization_engine):
        """Test performance optimization features"""
        # Generate large dataset for performance testing
        large_dataset = []
        for i in range(10000):
            large_dataset.append({
                "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                "value": np.random.uniform(0, 100),
                "category": f"category_{i % 10}",
                "subcategory": f"subcat_{i % 50}"
            })
        
        # Test data sampling for large datasets
        start_time = time.time()
        sampled_chart = visualization_engine.create_chart_with_sampling(
            chart_type=ChartType.SCATTER,
            data=large_dataset,
            sampling_config={
                "method": "random",
                "sample_size": 1000,
                "preserve_distribution": True
            }
        )
        end_time = time.time()
        
        assert sampled_chart["data_sampled"] is True
        assert sampled_chart["original_size"] == 10000
        assert sampled_chart["sampled_size"] == 1000
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
        
        # Test progressive loading
        progressive_chart = visualization_engine.create_progressive_chart(
            chart_type=ChartType.LINE,
            data=large_dataset,
            progressive_config={
                "initial_load_size": 100,
                "chunk_size": 500,
                "enable_virtual_scrolling": True
            }
        )
        
        assert "progressive_loading_enabled" in progressive_chart
        assert progressive_chart["initial_data_size"] == 100
        
        # Test caching
        cache_stats_before = visualization_engine.get_cache_statistics()
        
        # Create the same chart twice (should hit cache on second call)
        chart_config = {
            "chart_type": ChartType.BAR,
            "data": large_dataset[:100],
            "config": {"x_field": "category", "y_field": "value"}
        }
        
        chart1 = visualization_engine.create_chart(**chart_config)
        chart2 = visualization_engine.create_chart(**chart_config)
        
        cache_stats_after = visualization_engine.get_cache_statistics()
        
        assert cache_stats_after["cache_hits"] > cache_stats_before["cache_hits"]


class TestChartGenerator:
    """Ultra-industrial tests for ChartGenerator class"""
    
    @pytest.fixture
    def chart_generator(self):
        """Create ChartGenerator instance for testing"""
        config = {
            "default_backend": "plotly",
            "fallback_backends": ["matplotlib", "bokeh"],
            "optimization_enabled": True,
            "accessibility_enabled": True
        }
        return ChartGenerator(config)
    
    def test_initialization(self, chart_generator):
        """Test ChartGenerator initialization"""
        assert chart_generator is not None
        assert chart_generator.config["default_backend"] == "plotly"
        assert hasattr(chart_generator, 'backend_engines')
        assert hasattr(chart_generator, 'chart_templates')
    
    def test_time_series_generation(self, chart_generator):
        """Test time series chart generation"""
        # Generate time series data
        time_data = []
        base_time = datetime.now()
        for i in range(100):
            time_data.append({
                "timestamp": (base_time - timedelta(hours=i)).isoformat(),
                "cpu_usage": 45 + np.random.normal(0, 10),
                "memory_usage": 60 + np.random.normal(0, 15),
                "disk_io": np.random.uniform(10, 100)
            })
        
        # Generate multi-series time chart
        time_chart = chart_generator.generate_time_series_chart(
            data=time_data,
            time_field="timestamp",
            series_fields=["cpu_usage", "memory_usage", "disk_io"],
            chart_config={
                "title": "System Metrics Over Time",
                "y_axis_label": "Usage %",
                "show_legend": True,
                "enable_zoom": True
            }
        )
        
        assert time_chart["chart_type"] == "time_series"
        assert len(time_chart["series"]) == 3
        assert "zoom_enabled" in time_chart["features"]
        
        # Test time series with anomaly highlighting
        anomaly_chart = chart_generator.generate_anomaly_highlighted_time_series(
            data=time_data,
            time_field="timestamp",
            value_field="cpu_usage",
            anomaly_threshold=2.0  # Standard deviations
        )
        
        assert "anomalies_highlighted" in anomaly_chart
        assert "anomaly_threshold" in anomaly_chart
    
    def test_distribution_charts(self, chart_generator):
        """Test distribution chart generation"""
        # Generate sample data for distribution
        distribution_data = []
        for i in range(1000):
            distribution_data.append({
                "response_time": np.random.gamma(2, 50),  # Response times
                "user_age": np.random.normal(35, 12),     # User ages
                "session_duration": np.random.exponential(300),  # Session durations
                "category": np.random.choice(["A", "B", "C"])
            })
        
        # Generate histogram
        histogram = chart_generator.generate_histogram(
            data=distribution_data,
            value_field="response_time",
            bins=50,
            chart_config={
                "title": "Response Time Distribution",
                "x_axis_label": "Response Time (ms)",
                "y_axis_label": "Frequency"
            }
        )
        
        assert histogram["chart_type"] == "histogram"
        assert histogram["bin_count"] == 50
        
        # Generate box plot for multiple categories
        box_plot = chart_generator.generate_box_plot(
            data=distribution_data,
            value_field="session_duration",
            category_field="category",
            chart_config={
                "title": "Session Duration by Category",
                "show_outliers": True
            }
        )
        
        assert box_plot["chart_type"] == "box_plot"
        assert "outliers_shown" in box_plot
        
        # Generate violin plot
        violin_plot = chart_generator.generate_violin_plot(
            data=distribution_data,
            value_field="user_age",
            category_field="category"
        )
        
        assert violin_plot["chart_type"] == "violin_plot"
    
    def test_correlation_charts(self, chart_generator):
        """Test correlation and relationship charts"""
        # Generate correlated data
        correlation_data = []
        for i in range(500):
            base_value = np.random.normal(100, 20)
            correlation_data.append({
                "feature_a": base_value + np.random.normal(0, 10),
                "feature_b": base_value * 1.2 + np.random.normal(0, 15),
                "feature_c": base_value * 0.8 + np.random.normal(0, 12),
                "feature_d": np.random.normal(50, 10),  # Uncorrelated
                "size_factor": np.random.uniform(10, 100),
                "category": np.random.choice(["X", "Y", "Z"])
            })
        
        # Generate correlation matrix heatmap
        correlation_matrix = chart_generator.generate_correlation_heatmap(
            data=correlation_data,
            numeric_fields=["feature_a", "feature_b", "feature_c", "feature_d"],
            chart_config={
                "title": "Feature Correlation Matrix",
                "color_scale": "RdBu",
                "show_values": True
            }
        )
        
        assert correlation_matrix["chart_type"] == "correlation_heatmap"
        assert "correlation_values" in correlation_matrix
        
        # Generate scatter plot matrix
        scatter_matrix = chart_generator.generate_scatter_matrix(
            data=correlation_data[:100],  # Limit for performance
            fields=["feature_a", "feature_b", "feature_c"],
            color_field="category"
        )
        
        assert scatter_matrix["chart_type"] == "scatter_matrix"
        assert "matrix_size" in scatter_matrix
        
        # Generate bubble chart
        bubble_chart = chart_generator.generate_bubble_chart(
            data=correlation_data,
            x_field="feature_a",
            y_field="feature_b",
            size_field="size_factor",
            color_field="category",
            chart_config={
                "title": "Feature Relationship Analysis",
                "size_range": [5, 50]
            }
        )
        
        assert bubble_chart["chart_type"] == "bubble_chart"
        assert "size_encoding" in bubble_chart
    
    def test_geospatial_charts(self, chart_generator):
        """Test geospatial chart generation"""
        # Generate geographic data
        geo_data = [
            {"country": "Germany", "value": 1500, "lat": 51.1657, "lon": 10.4515},
            {"country": "France", "value": 1200, "lat": 46.2276, "lon": 2.2137},
            {"country": "UK", "value": 980, "lat": 55.3781, "lon": -3.4360},
            {"country": "Spain", "value": 860, "lat": 40.4637, "lon": -3.7492},
            {"country": "Italy", "value": 750, "lat": 41.8719, "lon": 12.5674}
        ]
        
        # Generate choropleth map
        choropleth_map = chart_generator.generate_choropleth_map(
            data=geo_data,
            location_field="country",
            value_field="value",
            chart_config={
                "title": "User Distribution by Country",
                "color_scale": "Blues",
                "scope": "europe"
            }
        )
        
        assert choropleth_map["chart_type"] == "choropleth"
        assert "geographic_scope" in choropleth_map
        
        # Generate scatter map
        scatter_map = chart_generator.generate_scatter_map(
            data=geo_data,
            lat_field="lat",
            lon_field="lon",
            size_field="value",
            hover_data=["country", "value"],
            chart_config={
                "title": "Geographic Distribution",
                "mapbox_style": "open-street-map"
            }
        )
        
        assert scatter_map["chart_type"] == "scatter_map"
        assert "mapbox_config" in scatter_map
    
    def test_specialized_business_charts(self, chart_generator):
        """Test specialized business charts"""
        # Funnel data
        funnel_data = [
            {"stage": "Visitors", "count": 10000},
            {"stage": "Sign-ups", "count": 2500},
            {"stage": "Trials", "count": 1200},
            {"stage": "Purchases", "count": 480},
            {"stage": "Renewals", "count": 360}
        ]
        
        # Generate funnel chart
        funnel_chart = chart_generator.generate_funnel_chart(
            data=funnel_data,
            stage_field="stage",
            value_field="count",
            chart_config={
                "title": "Conversion Funnel",
                "show_percentages": True,
                "calculate_conversion_rates": True
            }
        )
        
        assert funnel_chart["chart_type"] == "funnel"
        assert "conversion_rates" in funnel_chart
        
        # Waterfall data
        waterfall_data = [
            {"category": "Starting Revenue", "value": 10000, "type": "absolute"},
            {"category": "New Customers", "value": 3000, "type": "positive"},
            {"category": "Upsells", "value": 1500, "type": "positive"},
            {"category": "Churn", "value": -800, "type": "negative"},
            {"category": "Downgrades", "value": -300, "type": "negative"},
            {"category": "Ending Revenue", "value": 13400, "type": "total"}
        ]
        
        # Generate waterfall chart
        waterfall_chart = chart_generator.generate_waterfall_chart(
            data=waterfall_data,
            category_field="category",
            value_field="value",
            type_field="type",
            chart_config={
                "title": "Revenue Waterfall Analysis",
                "show_running_total": True
            }
        )
        
        assert waterfall_chart["chart_type"] == "waterfall"
        assert "running_totals" in waterfall_chart
        
        # Sankey diagram data
        sankey_data = {
            "nodes": [
                {"name": "Desktop", "id": 0},
                {"name": "Mobile", "id": 1},
                {"name": "Tablet", "id": 2},
                {"name": "Free Trial", "id": 3},
                {"name": "Basic Plan", "id": 4},
                {"name": "Premium Plan", "id": 5}
            ],
            "links": [
                {"source": 0, "target": 3, "value": 2000},
                {"source": 1, "target": 3, "value": 1500},
                {"source": 2, "target": 3, "value": 500},
                {"source": 3, "target": 4, "value": 1800},
                {"source": 3, "target": 5, "value": 1200},
                {"source": 4, "target": 5, "value": 300}
            ]
        }
        
        # Generate Sankey diagram
        sankey_diagram = chart_generator.generate_sankey_diagram(
            data=sankey_data,
            chart_config={
                "title": "User Journey Flow",
                "node_padding": 15,
                "link_opacity": 0.7
            }
        )
        
        assert sankey_diagram["chart_type"] == "sankey"
        assert "flow_analysis" in sankey_diagram
    
    def test_chart_customization_and_styling(self, chart_generator):
        """Test chart customization and styling capabilities"""
        # Sample data for customization testing
        sample_data = [
            {"category": "A", "value": 100, "secondary": 80},
            {"category": "B", "value": 150, "secondary": 120},
            {"category": "C", "value": 200, "secondary": 180},
            {"category": "D", "value": 120, "secondary": 90}
        ]
        
        # Test custom colors and styling
        styled_chart = chart_generator.generate_styled_chart(
            chart_type=ChartType.BAR,
            data=sample_data,
            style_config={
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
                "background_color": "#FFFFFF",
                "grid_color": "#E0E0E0",
                "font_family": "Inter, sans-serif",
                "font_size": 14,
                "border_radius": 4,
                "shadow": "0 2px 4px rgba(0,0,0,0.1)"
            }
        )
        
        assert "custom_styling_applied" in styled_chart
        assert styled_chart["style_config"]["colors"] is not None
        
        # Test annotations and markers
        annotated_chart = chart_generator.generate_annotated_chart(
            chart_type=ChartType.LINE,
            data=sample_data,
            annotations=[
                {
                    "x": "B", "y": 150,
                    "text": "Peak Performance",
                    "arrow": True,
                    "style": {"color": "red", "font_weight": "bold"}
                },
                {
                    "x": "D", "y": 120,
                    "text": "Target Achievement",
                    "arrow": False,
                    "style": {"color": "green"}
                }
            ]
        )
        
        assert "annotations" in annotated_chart
        assert len(annotated_chart["annotations"]) == 2
        
        # Test dual-axis chart
        dual_axis_chart = chart_generator.generate_dual_axis_chart(
            data=sample_data,
            left_axis_field="value",
            right_axis_field="secondary",
            category_field="category",
            chart_config={
                "title": "Dual Axis Comparison",
                "left_axis_label": "Primary Metric",
                "right_axis_label": "Secondary Metric"
            }
        )
        
        assert dual_axis_chart["chart_type"] == "dual_axis"
        assert "left_axis_config" in dual_axis_chart
        assert "right_axis_config" in dual_axis_chart


class TestRealtimeVisualizer:
    """Ultra-industrial tests for RealtimeVisualizer class"""
    
    @pytest.fixture
    def realtime_visualizer(self):
        """Create RealtimeVisualizer instance for testing"""
        config = {
            "update_interval_ms": 1000,
            "max_data_points": 1000,
            "buffer_size": 5000,
            "websocket_enabled": True,
            "performance_monitoring": True
        }
        return RealtimeVisualizer(config)
    
    def test_initialization(self, realtime_visualizer):
        """Test RealtimeVisualizer initialization"""
        assert realtime_visualizer is not None
        assert realtime_visualizer.config["update_interval_ms"] == 1000
        assert hasattr(realtime_visualizer, 'data_buffer')
        assert hasattr(realtime_visualizer, 'websocket_manager')
        assert hasattr(realtime_visualizer, 'update_scheduler')
    
    @pytest.mark.asyncio
    async def test_streaming_data_visualization(self, realtime_visualizer):
        """Test streaming data visualization"""
        # Initialize streaming chart
        streaming_config = {
            "chart_type": ChartType.LINE,
            "x_field": "timestamp",
            "y_field": "value",
            "title": "Real-time Metrics",
            "max_points": 100
        }
        
        stream_result = await realtime_visualizer.initialize_streaming_chart(streaming_config)
        assert stream_result["stream_initialized"] is True
        assert "chart_id" in stream_result
        
        chart_id = stream_result["chart_id"]
        
        # Simulate streaming data
        for i in range(20):
            data_point = {
                "timestamp": (datetime.now() - timedelta(seconds=i)).isoformat(),
                "value": 50 + np.random.normal(0, 10),
                "category": "system_metric"
            }
            
            update_result = await realtime_visualizer.update_streaming_chart(
                chart_id=chart_id,
                data_point=data_point
            )
            
            assert update_result["update_applied"] is True
            
            # Small delay to simulate real-time streaming
            await asyncio.sleep(0.01)
        
        # Get current chart state
        chart_state = await realtime_visualizer.get_chart_state(chart_id)
        assert "data_points" in chart_state
        assert len(chart_state["data_points"]) <= 100  # Should respect max_points
    
    @pytest.mark.asyncio
    async def test_multiple_stream_management(self, realtime_visualizer):
        """Test management of multiple concurrent streams"""
        # Create multiple streaming charts
        stream_configs = [
            {"chart_type": ChartType.LINE, "title": "CPU Usage", "y_field": "cpu"},
            {"chart_type": ChartType.LINE, "title": "Memory Usage", "y_field": "memory"},
            {"chart_type": ChartType.BAR, "title": "Request Rate", "y_field": "requests"}
        ]
        
        chart_ids = []
        for config in stream_configs:
            result = await realtime_visualizer.initialize_streaming_chart(config)
            chart_ids.append(result["chart_id"])
        
        assert len(chart_ids) == 3
        
        # Update all streams simultaneously
        for i in range(10):
            timestamp = (datetime.now() - timedelta(seconds=i)).isoformat()
            
            # Update CPU chart
            await realtime_visualizer.update_streaming_chart(
                chart_ids[0], 
                {"timestamp": timestamp, "cpu": 45 + np.random.normal(0, 10)}
            )
            
            # Update Memory chart
            await realtime_visualizer.update_streaming_chart(
                chart_ids[1], 
                {"timestamp": timestamp, "memory": 60 + np.random.normal(0, 15)}
            )
            
            # Update Request Rate chart
            await realtime_visualizer.update_streaming_chart(
                chart_ids[2], 
                {"timestamp": timestamp, "requests": np.random.poisson(100)}
            )
        
        # Verify all streams are active
        active_streams = await realtime_visualizer.get_active_streams()
        assert len(active_streams) == 3
        
        # Test stream cleanup
        cleanup_result = await realtime_visualizer.cleanup_inactive_streams()
        assert "streams_cleaned" in cleanup_result
    
    @pytest.mark.asyncio
    async def test_realtime_dashboard_updates(self, realtime_visualizer):
        """Test real-time dashboard updates"""
        # Create dashboard with multiple charts
        dashboard_config = {
            "dashboard_id": "realtime_dashboard_001",
            "charts": [
                {
                    "chart_id": "chart_1",
                    "chart_type": ChartType.GAUGE,
                    "title": "System Health",
                    "value_field": "health_score"
                },
                {
                    "chart_id": "chart_2", 
                    "chart_type": ChartType.LINE,
                    "title": "Performance Trend",
                    "y_field": "performance"
                }
            ],
            "update_interval": 500  # ms
        }
        
        dashboard_result = await realtime_visualizer.initialize_realtime_dashboard(dashboard_config)
        assert dashboard_result["dashboard_initialized"] is True
        
        dashboard_id = dashboard_result["dashboard_id"]
        
        # Send batch updates to dashboard
        for i in range(15):
            batch_update = {
                "timestamp": datetime.now().isoformat(),
                "chart_updates": {
                    "chart_1": {"health_score": np.random.uniform(0.7, 1.0)},
                    "chart_2": {"performance": 80 + np.random.normal(0, 10)}
                }
            }
            
            update_result = await realtime_visualizer.update_dashboard_batch(
                dashboard_id=dashboard_id,
                batch_update=batch_update
            )
            
            assert update_result["batch_applied"] is True
            await asyncio.sleep(0.05)
        
        # Get dashboard performance metrics
        perf_metrics = await realtime_visualizer.get_dashboard_performance_metrics(dashboard_id)
        assert "average_update_time" in perf_metrics
        assert "update_frequency" in perf_metrics
    
    def test_data_buffering_and_windowing(self, realtime_visualizer):
        """Test data buffering and windowing mechanisms"""
        # Test circular buffer implementation
        buffer_test = realtime_visualizer.test_data_buffer(
            buffer_size=100,
            data_points=150  # More than buffer size
        )
        
        assert buffer_test["buffer_overflow_handled"] is True
        assert buffer_test["final_buffer_size"] == 100
        assert buffer_test["oldest_data_discarded"] is True
        
        # Test time-based windowing
        time_window_config = {
            "window_type": "sliding",
            "window_size": "5m",  # 5 minutes
            "slide_interval": "1m"  # Slide every minute
        }
        
        windowing_result = realtime_visualizer.configure_time_windowing(time_window_config)
        assert windowing_result["windowing_configured"] is True
        assert windowing_result["window_type"] == "sliding"
        
        # Test data aggregation within windows
        aggregation_config = {
            "aggregation_method": "mean",
            "grouping_interval": "30s",
            "fields": ["cpu_usage", "memory_usage"]
        }
        
        aggregation_result = realtime_visualizer.configure_window_aggregation(aggregation_config)
        assert aggregation_result["aggregation_configured"] is True
    
    def test_performance_monitoring_and_optimization(self, realtime_visualizer):
        """Test performance monitoring and optimization features"""
        # Enable performance monitoring
        performance_config = {
            "monitor_fps": True,
            "monitor_memory_usage": True,
            "monitor_update_latency": True,
            "auto_optimization": True
        }
        
        monitoring_result = realtime_visualizer.enable_performance_monitoring(performance_config)
        assert monitoring_result["monitoring_enabled"] is True
        
        # Simulate high-frequency updates to test performance
        start_time = time.time()
        
        for i in range(1000):
            realtime_visualizer.simulate_data_update({
                "timestamp": (datetime.now() - timedelta(milliseconds=i)).isoformat(),
                "value": np.random.uniform(0, 100)
            })
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Get performance metrics
        perf_metrics = realtime_visualizer.get_performance_metrics()
        assert "average_processing_time" in perf_metrics
        assert "memory_usage" in perf_metrics
        assert "dropped_frames" in perf_metrics
        
        # Should handle 1000 updates reasonably quickly
        assert processing_time < 5.0  # Less than 5 seconds
        
        # Test automatic optimization
        optimization_result = realtime_visualizer.apply_automatic_optimizations()
        assert "optimizations_applied" in optimization_result
        assert "performance_improvement" in optimization_result
