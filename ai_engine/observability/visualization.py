"""Visualization Engine

Advanced visualization system for the IA Influencer platform providing
chart generation, reporting, and data visualization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import base64
import io
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
import statistics
import logging

# Note: In production, these would be actual imports
# import matplotlib.pyplot as plt
# import seaborn as sns
# import plotly.graph_objects as go
# import plotly.express as px
# from PIL import Image
# import pandas as pd

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """
Chart types for visualization"""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    AREA = "area"
    CANDLESTICK = "candlestick"
    TREEMAP = "treemap"
    FUNNEL = "funnel"
    GAUGE = "gauge"
    RADAR = "radar"
    SANKEY = "sankey"
    WATERFALL = "waterfall"
    BOXPLOT = "boxplot"


class OutputFormat(Enum):
    """Output formats for visualizations"""

    PNG = "png"
    JPEG = "jpeg"
    SVG = "svg"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    BASE64 = "base64"


class ColorScheme(Enum):
    """Color schemes for visualizations"""

    DEFAULT = "default"
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    BLUES = "blues"
    GREENS = "greens"
    REDS = "reds"
    ORANGES = "oranges"
    PURPLES = "purples"
    RAINBOW = "rainbow"
    CORPORATE = "corporate"
    MATERIAL = "material"


@dataclass
class ChartConfig:
    """Chart configuration settings"""
    title: str
    chart_type: ChartType
    width: int = 800
    height: int = 600
    color_scheme: ColorScheme = ColorScheme.DEFAULT
    show_legend: bool = True
    show_grid: bool = True
    show_axes: bool = True
    font_size: int = 12
    title_font_size: int = 16
    background_color: str = "white"
    grid_color: str = "#E0E0E0"
    text_color: str = "black"
    margin: Dict[str, int] = field(default_factory=lambda: {'top': 50, 'right': 50, 'bottom': 50, 'left': 50})
    animation: bool = True
    interactive: bool = True
    responsive: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'chart_type': self.chart_type.value,
            'width': self.width,
            'height': self.height,
            'color_scheme': self.color_scheme.value,
            'show_legend': self.show_legend,
            'show_grid': self.show_grid,
            'show_axes': self.show_axes,
            'font_size': self.font_size,
            'title_font_size': self.title_font_size,
            'background_color': self.background_color,
            'grid_color': self.grid_color,
            'text_color': self.text_color,
            'margin': self.margin,
            'animation': self.animation,
            'interactive': self.interactive,
            'responsive': self.responsive
        }


@dataclass
class ChartData:
    """
Chart data structure"""
    labels: List[str]
    datasets: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'labels': self.labels,
            'datasets': self.datasets,
            'metadata': self.metadata
        }


@dataclass
class VisualizationResult:
    """
Visualization generation result"""
    chart_id: str
    config: ChartConfig
    data: ChartData
    output_format: OutputFormat
    content: Union[str, bytes]
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'chart_id': self.chart_id,
            'config': self.config.to_dict(),
            'data': self.data.to_dict(),
            'output_format': self.output_format.value,
            'content': self.content if isinstance(self.content, str) else base64.b64encode(self.content).decode(),
            'metadata': self.metadata,
            'error': self.error,
            'generated_at': self.generated_at.isoformat()
        }


class BaseChartGenerator:
    """
Base class for chart generators"""
    
    def __init__(self, name: str):
        """
Initialize chart generator"""
        self.name = name
        self.supported_types = set()
    
    def supports_chart_type(self, chart_type: ChartType) -> bool:
        """
Check if this generator supports the chart type"""
        return chart_type in self.supported_types
    
    async def generate(self, config: ChartConfig, data: ChartData, 
                      output_format: OutputFormat) -> VisualizationResult:
        """
Generate chart visualization - base implementation"""
        try:
            chart_id = f"base_{int(datetime.now(timezone.utc).timestamp())}"
            
            # Basic text-based chart representation
            content = self._generate_text_chart(config, data)
            
            return VisualizationResult(
                chart_id=chart_id,
                config=config,
                data=data,
                output_format=output_format,
                content=content,
                metadata={
                    'generator': self.name,
                    'chart_type': config.chart_type.value,
                    'format': 'text'
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate base chart: {str(e)}")
            return VisualizationResult(
                chart_id=f"error_{int(datetime.now(timezone.utc).timestamp())}",
                config=config,
                data=data,
                output_format=output_format,
                content="",
                error=str(e)
            )
    
    def _generate_text_chart(self, config: ChartConfig, data: ChartData) -> str:
        """Generate basic text representation of chart"""
        lines = [
            f"Chart: {config.title}",
            f"Type: {config.chart_type.value}",
            f"Dimensions: {config.width}x{config.height}",
            "-" * 40,
            "Data Summary:"
        ]
        
        if hasattr(data, 'series') and data.series:
            for series in data.series:
                lines.append(f"  {series.name}: {len(series.values)} points")
                if series.values:
                    min_val = min(series.values)
                    max_val = max(series.values)
                    avg_val = sum(series.values) / len(series.values)
                    lines.append(f"    Range: {min_val:.2f} - {max_val:.2f}")
                    lines.append(f"    Average: {avg_val:.2f}")
        
        return "\n".join(lines)
    
    def _prepare_color_palette(self, color_scheme: ColorScheme, num_colors: int) -> List[str]:
        """Prepare color palette based on scheme"""
        color_palettes = {
            ColorScheme.DEFAULT: ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
            ColorScheme.VIRIDIS: ["#440154", "#404387", "#2a788e", "#22a884", "#7ad151", "#fde725"],
            ColorScheme.PLASMA: ["#0d0887", "#6a00a8", "#b12a90", "#e16462", "#fca636", "#f0f921"],
            ColorScheme.BLUES: ["#08519c", "#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#deebf7"],
            ColorScheme.GREENS: ["#00441b", "#238b45", "#66c2a4", "#abdda4", "#e5f5f9"],
            ColorScheme.REDS: ["#67000d", "#a50f15", "#cb181d", "#ef3b2c", "#fb6a4a", "#fc9272"],
            ColorScheme.CORPORATE: ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"],
            ColorScheme.MATERIAL: ["#f44336", "#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3", "#03a9f4", "#00bcd4"]
        }
        
        palette = color_palettes.get(color_scheme, color_palettes[ColorScheme.DEFAULT])
        
        # Repeat colors if needed
        while len(palette) < num_colors:
            palette.extend(palette)
        
        return palette[:num_colors]


class MatplotlibGenerator(BaseChartGenerator):
    """Matplotlib-based chart generator"""
    
    def __init__(self):
        """
Initialize matplotlib generator"""
        super().__init__("matplotlib")
        self.supported_types = {
            ChartType.LINE, ChartType.BAR, ChartType.PIE, ChartType.SCATTER,
            ChartType.HISTOGRAM, ChartType.AREA, ChartType.BOXPLOT
        }
    
    async def generate(self, config: ChartConfig, data: ChartData, 
                      output_format: OutputFormat) -> VisualizationResult:
        """Generate chart using matplotlib"""
        try:
            chart_id = f"mpl_{int(datetime.now(timezone.utc).timestamp())}"
            
            # For demo purposes, we'll simulate chart generation
            # In production, this would use actual matplotlib
            
            if config.chart_type == ChartType.LINE:
                content = await self._generate_line_chart(config, data, output_format)
            elif config.chart_type == ChartType.BAR:
                content = await self._generate_bar_chart(config, data, output_format)
            elif config.chart_type == ChartType.PIE:
                content = await self._generate_pie_chart(config, data, output_format)
            elif config.chart_type == ChartType.SCATTER:
                content = await self._generate_scatter_chart(config, data, output_format)
            elif config.chart_type == ChartType.HISTOGRAM:
                content = await self._generate_histogram(config, data, output_format)
            else:
                content = await self._generate_default_chart(config, data, output_format)
            
            return VisualizationResult(
                chart_id=chart_id,
                config=config,
                data=data,
                output_format=output_format,
                content=content,
                metadata={
                    'generator': self.name,
                    'chart_type': config.chart_type.value
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate matplotlib chart: {str(e)}")
            return VisualizationResult(
                chart_id=f"error_{int(datetime.now(timezone.utc).timestamp())}",
                config=config,
                data=data,
                output_format=output_format,
                content="",
                error=str(e)
            )
    
    async def _generate_line_chart(self, config: ChartConfig, data: ChartData, 
                                 output_format: OutputFormat) -> str:
        """Generate line chart"""
        # Simulate matplotlib line chart generation
        chart_svg = f"""
        <svg width="{config.width}" height="{config.height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{config.background_color}"/>
            <text x="50%" y="30" text-anchor="middle" font-size="{config.title_font_size}" fill="{config.text_color}">
                {config.title}
            </text>
            <!-- Simulated line chart -->
            <g transform="translate({config.margin['left']},{config.margin['top']})">
                <line x1="0" y1="0" x2="{config.width - config.margin['left'] - config.margin['right']}" 
                      y2="0" stroke="{config.grid_color}" stroke-width="1"/>
                <line x1="0" y1="0" x2="0" 
                      y2="{config.height - config.margin['top'] - config.margin['bottom']}" 
                      stroke="{config.grid_color}" stroke-width="1"/>
                <!-- Sample data line -->
                <path d="M 0,{config.height//2} Q {config.width//4},{config.height//4} {config.width//2},{config.height//3} T {config.width-100},{config.height//4}" 
                      stroke="#1f77b4" stroke-width="2" fill="none"/>
            </g>
        </svg>
        """
        
        if output_format == OutputFormat.SVG:
            return chart_svg
        elif output_format == OutputFormat.HTML:
            return f"<div>{chart_svg}</div>"
        else:
            return f"Simulated {config.chart_type.value} chart content"
    
    async def _generate_bar_chart(self, config: ChartConfig, data: ChartData, 
                                output_format: OutputFormat) -> str:
        """Generate bar chart"""
        # Simulate bar chart generation
        colors = self._prepare_color_palette(config.color_scheme, len(data.datasets))
        
        bars_svg = ""
        if data.datasets:
            dataset = data.datasets[0]
            values = dataset.get('data', [])
            bar_width = (config.width - config.margin['left'] - config.margin['right']) // max(len(values), 1)
            
            for i, value in enumerate(values):
                if isinstance(value, (int, float)):
                    bar_height = min(value * 2, config.height - config.margin['top'] - config.margin['bottom'] - 50)
                    bars_svg += f'''
                    <rect x="{i * bar_width + 10}" y="{config.height - config.margin['bottom'] - bar_height}" 
                          width="{bar_width - 20}" height="{bar_height}" 
                          fill="{colors[i % len(colors)]}" opacity="0.8"/>
                    '''
        
        chart_svg = f"""
        <svg width="{config.width}" height="{config.height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{config.background_color}"/>
            <text x="50%" y="30" text-anchor="middle" font-size="{config.title_font_size}" fill="{config.text_color}">
                {config.title}
            </text>
            <g transform="translate({config.margin['left']},{config.margin['top']})">
                {bars_svg}
            </g>
        </svg>
        """
        
        if output_format == OutputFormat.SVG:
            return chart_svg
        elif output_format == OutputFormat.HTML:
            return f"<div>{chart_svg}</div>"
        else:
            return f"Simulated {config.chart_type.value} chart content"
    
    async def _generate_pie_chart(self, config: ChartConfig, data: ChartData, 
                                output_format: OutputFormat) -> str:
        """Generate pie chart"""
        # Simulate pie chart generation
        colors = self._prepare_color_palette(config.color_scheme, len(data.datasets))
        
        chart_svg = f"""
        <svg width="{config.width}" height="{config.height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="{config.background_color}"/>
            <text x="50%" y="30" text-anchor="middle" font-size="{config.title_font_size}" fill="{config.text_color}">
                {config.title}
            </text>
            <!-- Simulated pie chart -->
            <circle cx="{config.width//2}" cy="{config.height//2}" r="100" 
                    fill="#1f77b4" opacity="0.8"/>
            <path d="M {config.width//2},{config.height//2} L {config.width//2},{config.height//2-100} A 100,100 0 0,1 {config.width//2+70},{config.height//2-70} Z" 
                  fill="#ff7f0e" opacity="0.8"/>
        </svg>
        """
        
        if output_format == OutputFormat.SVG:
            return chart_svg
        elif output_format == OutputFormat.HTML:
            return f"<div>{chart_svg}</div>"
        else:
            return f"Simulated {config.chart_type.value} chart content"
    
    async def _generate_scatter_chart(self, config: ChartConfig, data: ChartData, 
                                    output_format: OutputFormat) -> str:
        """Generate scatter chart"""
        return await self._generate_default_chart(config, data, output_format)
    
    async def _generate_histogram(self, config: ChartConfig, data: ChartData, 
                                output_format: OutputFormat) -> str:
        """
Generate histogram"""
        return await self._generate_default_chart(config, data, output_format)
    
    async def _generate_default_chart(self, config: ChartConfig, data: ChartData, 
                                    output_format: OutputFormat) -> str:
        """
Generate default chart visualization"""
        return f"Simulated {config.chart_type.value} chart - Generated with {self.name}"


class PlotlyGenerator(BaseChartGenerator):
    """Plotly-based chart generator"""
    
    def __init__(self):
        """
Initialize plotly generator"""
        super().__init__("plotly")
        self.supported_types = {
            ChartType.LINE, ChartType.BAR, ChartType.PIE, ChartType.SCATTER,
            ChartType.HEATMAP, ChartType.CANDLESTICK, ChartType.TREEMAP,
            ChartType.FUNNEL, ChartType.GAUGE, ChartType.RADAR, ChartType.SANKEY
        }
    
    async def generate(self, config: ChartConfig, data: ChartData, 
                      output_format: OutputFormat) -> VisualizationResult:
        """Generate chart using plotly"""
        try:
            chart_id = f"plotly_{int(datetime.now(timezone.utc).timestamp())}"
            
            # Generate interactive HTML content
            content = await self._generate_interactive_chart(config, data, output_format)
            
            return VisualizationResult(
                chart_id=chart_id,
                config=config,
                data=data,
                output_format=output_format,
                content=content,
                metadata={
                    'generator': self.name,
                    'chart_type': config.chart_type.value,
                    'interactive': config.interactive
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate plotly chart: {str(e)}")
            return VisualizationResult(
                chart_id=f"error_{int(datetime.now(timezone.utc).timestamp())}",
                config=config,
                data=data,
                output_format=output_format,
                content="",
                error=str(e)
            )
    
    async def _generate_interactive_chart(self, config: ChartConfig, data: ChartData, 
                                        output_format: OutputFormat) -> str:
        """Generate interactive chart"""
        # Simulate plotly chart generation
        chart_data_json = json.dumps(data.to_dict())
        config_json = json.dumps(config.to_dict())
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config.title}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{ width: {config.width}px; height: {config.height}px; }}
            </style>
        </head>
        <body>
            <div id="chart" class="chart-container"></div>
            <script>
                // Chart configuration
                var config = {config_json};
                var data = {chart_data_json};
                
                // Simulate plotly chart creation
                var traces = [];
                
                if (data.datasets && data.datasets.length > 0) {{
                    data.datasets.forEach(function(dataset, index) {{
                        traces.push({{
                            x: data.labels,
                            y: dataset.data,
                            type: '{config.chart_type.value}',
                            name: dataset.label || 'Series ' + (index + 1),
                            marker: {{ color: getColor(index) }}
                        }});
                    }});
                }}
                
                var layout = {{
                    title: config.title,
                    showlegend: config.show_legend,
                    width: config.width,
                    height: config.height,
                    paper_bgcolor: config.background_color,
                    plot_bgcolor: config.background_color,
                    font: {{ size: config.font_size, color: config.text_color }}
                }};
                
                var plotConfig = {{
                    responsive: config.responsive,
                    displayModeBar: config.interactive
                }};
                
                // Create the plot
                Plotly.newPlot('chart', traces, layout, plotConfig);
                
                function getColor(index) {{
                    var colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'];
                    return colors[index % colors.length];
                }}
            </script>
        </body>
        </html>
        """
        
        if output_format == OutputFormat.HTML:
            return html_content
        elif output_format == OutputFormat.JSON:
            return json.dumps({
                'data': data.to_dict(),
                'config': config.to_dict(),
                'type': 'plotly'
            })
        else:
            return f"Interactive {config.chart_type.value} chart generated with Plotly"


class D3Generator(BaseChartGenerator):
    """D3.js-based chart generator"""
    
    def __init__(self):
        """
Initialize D3 generator"""
        super().__init__("d3")
        self.supported_types = {
            ChartType.LINE, ChartType.BAR, ChartType.PIE, ChartType.SCATTER,
            ChartType.HEATMAP, ChartType.TREEMAP, ChartType.SANKEY,
            ChartType.AREA, ChartType.HISTOGRAM
        }
    
    async def generate(self, config: ChartConfig, data: ChartData, 
                      output_format: OutputFormat) -> VisualizationResult:
        """Generate chart using D3.js"""
        try:
            chart_id = f"d3_{int(datetime.now(timezone.utc).timestamp())}"
            
            content = await self._generate_d3_chart(config, data, output_format)
            
            return VisualizationResult(
                chart_id=chart_id,
                config=config,
                data=data,
                output_format=output_format,
                content=content,
                metadata={
                    'generator': self.name,
                    'chart_type': config.chart_type.value,
                    'library': 'd3.js'
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate D3 chart: {str(e)}")
            return VisualizationResult(
                chart_id=f"error_{int(datetime.now(timezone.utc).timestamp())}",
                config=config,
                data=data,
                output_format=output_format,
                content="",
                error=str(e)
            )
    
    async def _generate_d3_chart(self, config: ChartConfig, data: ChartData, 
                               output_format: OutputFormat) -> str:
        """Generate D3.js chart"""
        chart_data_json = json.dumps(data.to_dict())
        config_json = json.dumps(config.to_dict())
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config.title}</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{ width: {config.width}px; height: {config.height}px; }}
                .axis {{ font: 12px sans-serif; }}
                .grid line {{ stroke: {config.grid_color}; stroke-opacity: 0.7; shape-rendering: crispEdges; }}
                .grid path {{ stroke-width: 0; }}
            </style>
        </head>
        <body>
            <div id="chart" class="chart-container">
                <h2 style="text-align: center; color: {config.text_color};">{config.title}</h2>
                <svg id="chart-svg"></svg>
            </div>
            <script>
                // Chart configuration and data
                var config = {config_json};
                var chartData = {chart_data_json};
                
                // Set up dimensions and margins
                var margin = config.margin;
                var width = config.width - margin.left - margin.right;
                var height = config.height - margin.top - margin.bottom;
                
                // Create SVG
                var svg = d3.select("#chart-svg")
                    .attr("width", config.width)
                    .attr("height", config.height);
                
                var g = svg.append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
                
                // Simulated chart rendering based on type
                if (config.chart_type === 'bar') {{
                    drawBarChart();
                }} else if (config.chart_type === 'line') {{
                    drawLineChart();
                }} else if (config.chart_type === 'pie') {{
                    drawPieChart();
                }} else {{
                    drawDefaultChart();
                }}
                
                function drawBarChart() {{
                    // Simulate bar chart with D3
                    var x = d3.scaleBand()
                        .domain(chartData.labels)
                        .range([0, width])
                        .padding(0.1);
                    
                    var y = d3.scaleLinear()
                        .domain([0, 100])
                        .nice()
                        .range([height, 0]);
                    
                    // Add axes
                    g.append("g")
                        .attr("class", "axis")
                        .attr("transform", "translate(0," + height + ")")
                        .call(d3.axisBottom(x));
                    
                    g.append("g")
                        .attr("class", "axis")
                        .call(d3.axisLeft(y));
                    
                    // Add sample bars
                    g.selectAll(".bar")
                        .data([30, 60, 45, 80, 25])
                        .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", function(d, i) {{ return x(chartData.labels[i] || i); }})
                        .attr("y", function(d) {{ return y(d); }})
                        .attr("width", x.bandwidth())
                        .attr("height", function(d) {{ return height - y(d); }})
                        .attr("fill", "#1f77b4")
                        .attr("opacity", 0.8);
                }}
                
                function drawLineChart() {{
                    // Simulate line chart
                    var line = d3.line()
                        .x(function(d, i) {{ return (width / 4) * i; }})
                        .y(function(d) {{ return height - (d * 3); }})
                        .curve(d3.curveMonotoneX);
                    
                    g.append("path")
                        .datum([20, 40, 30, 60, 45])
                        .attr("fill", "none")
                        .attr("stroke", "#1f77b4")
                        .attr("stroke-width", 2)
                        .attr("d", line);
                }}
                
                function drawPieChart() {{
                    // Simulate pie chart
                    var radius = Math.min(width, height) / 2;
                    var pie = d3.pie().value(function(d) {{ return d; }});
                    var arc = d3.arc().innerRadius(0).outerRadius(radius);
                    
                    var pieG = g.append("g")
                        .attr("transform", "translate(" + width/2 + "," + height/2 + ")");
                    
                    var arcs = pieG.selectAll(".arc")
                        .data(pie([30, 25, 20, 15, 10]))
                        .enter().append("g")
                        .attr("class", "arc");
                    
                    arcs.append("path")
                        .attr("d", arc)
                        .attr("fill", function(d, i) {{ 
                            var colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"];
                            return colors[i]; 
                        }});
                }}
                
                function drawDefaultChart() {{
                    g.append("text")
                        .attr("x", width / 2)
                        .attr("y", height / 2)
                        .attr("text-anchor", "middle")
                        .style("font-size", "16px")
                        .text("D3.js Chart: " + config.chart_type);
                }}
            </script>
        </body>
        </html>
        """
        
        return html_content


class VisualizationEngine:
    """
    Main visualization engine managing chart generation and rendering
    
    Features:
    - Multiple chart generators (Matplotlib, Plotly, D3.js)
    - Automatic generator selection
    - Chart caching and optimization
    - Batch chart generation
    - Custom chart templates
    - Export capabilities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize visualization engine"""
        self.config = config or {}
        
        # Chart generators
        self.generators: Dict[str, BaseChartGenerator] = {}
        self._initialize_generators()
        
        # Chart cache
        self.chart_cache: Dict[str, VisualizationResult] = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        
        # Performance tracking
        self.generation_stats = {
            'total_charts': 0,
            'cache_hits': 0,
            'generation_times': [],
            'error_count': 0
        }
        
        # Template storage
        self.chart_templates: Dict[str, ChartConfig] = {}
        self._initialize_templates()
    
    def _initialize_generators(self):
        """
Initialize chart generators"""
        try:
            # Register available generators
            self.generators['matplotlib'] = MatplotlibGenerator()
            self.generators['plotly'] = PlotlyGenerator()
            self.generators['d3'] = D3Generator()
            
            logger.info(f"Initialized {len(self.generators)} chart generators")
            
        except Exception as e:
            logger.error(f"Failed to initialize generators: {str(e)}")
    
    def _initialize_templates(self):
        """Initialize chart templates"""
        try:
            # System performance dashboard charts
            self.chart_templates['system_performance'] = ChartConfig(
                title="System Performance",
                chart_type=ChartType.LINE,
                width=800,
                height=400,
                color_scheme=ColorScheme.VIRIDIS,
                show_grid=True,
                interactive=True
            )
            
            # Business metrics charts
            self.chart_templates['revenue_trend'] = ChartConfig(
                title="Revenue Trend",
                chart_type=ChartType.AREA,
                width=1000,
                height=500,
                color_scheme=ColorScheme.CORPORATE,
                show_legend=True
            )
            
            # Alert distribution
            self.chart_templates['alert_distribution'] = ChartConfig(
                title="Alert Distribution",
                chart_type=ChartType.PIE,
                width=600,
                height=600,
                color_scheme=ColorScheme.MATERIAL,
                show_legend=True
            )
            
            # User engagement
            self.chart_templates['user_engagement'] = ChartConfig(
                title="User Engagement",
                chart_type=ChartType.BAR,
                width=900,
                height=450,
                color_scheme=ColorScheme.BLUES,
                show_grid=True
            )
            
            logger.info(f"Initialized {len(self.chart_templates)} chart templates")
            
        except Exception as e:
            logger.error(f"Failed to initialize templates: {str(e)}")
    
    async def generate_chart(self, config: ChartConfig, data: ChartData, 
                           output_format: OutputFormat = OutputFormat.HTML,
                           generator_preference: Optional[str] = None) -> VisualizationResult:
        """Generate a chart visualization"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Check cache first
            cache_key = self._generate_cache_key(config, data, output_format)
            
            if cache_key in self.chart_cache:
                cached_result = self.chart_cache[cache_key]
                cache_age = (start_time - cached_result.generated_at).total_seconds()
                
                if cache_age < self.cache_ttl:
                    self.generation_stats['cache_hits'] += 1
                    return cached_result
            
            # Select appropriate generator
            generator = self._select_generator(config.chart_type, generator_preference)
            
            if not generator:
                return VisualizationResult(
                    chart_id=f"error_{int(start_time.timestamp())}",
                    config=config,
                    data=data,
                    output_format=output_format,
                    content="",
                    error=f"No suitable generator found for chart type: {config.chart_type.value}"
                )
            
            # Generate chart
            result = await generator.generate(config, data, output_format)
            
            # Cache result if successful
            if not result.error:
                self.chart_cache[cache_key] = result
            else:
                self.generation_stats['error_count'] += 1
            
            # Update statistics
            generation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.generation_stats['generation_times'].append(generation_time)
            self.generation_stats['total_charts'] += 1
            
            # Add performance metadata
            result.metadata['generation_time_ms'] = generation_time * 1000
            result.metadata['generator_used'] = generator.name
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate chart: {str(e)}")
            self.generation_stats['error_count'] += 1
            
            return VisualizationResult(
                chart_id=f"error_{int(datetime.now(timezone.utc).timestamp())}",
                config=config,
                data=data,
                output_format=output_format,
                content="",
                error=str(e)
            )
    
    def _generate_cache_key(self, config: ChartConfig, data: ChartData, 
                          output_format: OutputFormat) -> str:
        """Generate cache key for chart configuration and data"""
        try:
            # Create a hash of the key components
            key_components = {
                'config': config.to_dict(),
                'data_hash': hash(json.dumps(data.to_dict(), sort_keys=True)),
                'output_format': output_format.value
            }
            
            return f"chart_{hash(json.dumps(key_components, sort_keys=True))}"
            
        except Exception as e:
            logger.error(f"Failed to generate cache key: {str(e)}")
            return f"chart_{int(datetime.now(timezone.utc).timestamp())}"
    
    def _select_generator(self, chart_type: ChartType, 
                         preference: Optional[str] = None) -> Optional[BaseChartGenerator]:
        """Select appropriate generator for chart type"""
        try:
            # Use preference if specified and available
            if preference and preference in self.generators:
                generator = self.generators[preference]
                if generator.supports_chart_type(chart_type):
                    return generator
            
            # Find best generator for chart type
            suitable_generators = [
                gen for gen in self.generators.values()
                if gen.supports_chart_type(chart_type)
            ]
            
            if not suitable_generators:
                return None
            
            # Priority order: Plotly > D3 > Matplotlib
            generator_priority = ['plotly', 'd3', 'matplotlib']
            
            for preferred_gen in generator_priority:
                for generator in suitable_generators:
                    if generator.name == preferred_gen:
                        return generator
            
            # Return first suitable generator
            return suitable_generators[0]
            
        except Exception as e:
            logger.error(f"Failed to select generator: {str(e)}")
            return None
    
    async def generate_dashboard_charts(self, chart_configs: List[Dict[str, Any]]) -> List[VisualizationResult]:
        """Generate multiple charts for dashboard"""
        try:
            results = []
            tasks = []
            
            for chart_config in chart_configs:
                # Parse configuration
                config = self._parse_chart_config(chart_config)
                data = self._parse_chart_data(chart_config.get('data', {}))
                output_format = OutputFormat(chart_config.get('output_format', 'html'))
                
                # Create generation task
                task = self.generate_chart(config, data, output_format)
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Chart generation failed: {str(result)}")
                    # Create error result
                    error_result = VisualizationResult(
                        chart_id=f"error_{int(datetime.now(timezone.utc).timestamp())}",
                        config=ChartConfig("Error", ChartType.LINE),
                        data=ChartData([], []),
                        output_format=OutputFormat.HTML,
                        content="",
                        error=str(result)
                    )
                    valid_results.append(error_result)
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard charts: {str(e)}")
            return []
    
    def _parse_chart_config(self, config_dict: Dict[str, Any]) -> ChartConfig:
        """Parse chart configuration from dictionary"""
        try:
            return ChartConfig(
                title=config_dict.get('title', 'Untitled Chart'),
                chart_type=ChartType(config_dict.get('chart_type', 'line')),
                width=config_dict.get('width', 800),
                height=config_dict.get('height', 600),
                color_scheme=ColorScheme(config_dict.get('color_scheme', 'default')),
                show_legend=config_dict.get('show_legend', True),
                show_grid=config_dict.get('show_grid', True),
                interactive=config_dict.get('interactive', True)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse chart config: {str(e)}")
            return ChartConfig("Error Chart", ChartType.LINE)
    
    def _parse_chart_data(self, data_dict: Dict[str, Any]) -> ChartData:
        """Parse chart data from dictionary"""
        try:
            return ChartData(
                labels=data_dict.get('labels', []),
                datasets=data_dict.get('datasets', []),
                metadata=data_dict.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to parse chart data: {str(e)}")
            return ChartData([], [])
    
    def get_chart_template(self, template_name: str) -> Optional[ChartConfig]:
        """Get chart template by name"""
        return self.chart_templates.get(template_name)
    
    def register_chart_template(self, name: str, config: ChartConfig):
        """
Register new chart template"""
        try:
            self.chart_templates[name] = config
            logger.info(f"Registered chart template: {name}")
            
        except Exception as e:
            logger.error(f"Failed to register chart template {name}: {str(e)}")
    
    def list_supported_chart_types(self, generator_name: Optional[str] = None) -> Dict[str, List[str]]:
        """List supported chart types by generator"""
        try:
            supported_types = {}
            
            if generator_name and generator_name in self.generators:
                generator = self.generators[generator_name]
                supported_types[generator_name] = [ct.value for ct in generator.supported_types]
            else:
                for name, generator in self.generators.items():
                    supported_types[name] = [ct.value for ct in generator.supported_types]
            
            return supported_types
            
        except Exception as e:
            logger.error(f"Failed to list supported chart types: {str(e)}")
            return {}
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get chart generation statistics"""
        try:
            stats = self.generation_stats.copy()
            
            # Calculate additional metrics
            if stats['generation_times']:
                stats['avg_generation_time_ms'] = (sum(stats['generation_times']) / len(stats['generation_times'])) * 1000
                stats['min_generation_time_ms'] = min(stats['generation_times']) * 1000
                stats['max_generation_time_ms'] = max(stats['generation_times']) * 1000
            
            stats['cache_hit_rate'] = (stats['cache_hits'] / max(stats['total_charts'], 1)) * 100
            stats['error_rate'] = (stats['error_count'] / max(stats['total_charts'], 1)) * 100
            stats['cached_charts'] = len(self.chart_cache)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get generation stats: {str(e)}")
            return {}
    
    async def export_chart(self, chart_id: str, export_format: OutputFormat) -> Optional[VisualizationResult]:
        """Export existing chart to different format"""
        try:
            # Find chart in cache
            cached_chart = None
            for cached_result in self.chart_cache.values():
                if cached_result.chart_id == chart_id:
                    cached_chart = cached_result
                    break
            
            if not cached_chart:
                logger.warning(f"Chart not found in cache: {chart_id}")
                return None
            
            # Generate in new format
            return await self.generate_chart(
                cached_chart.config,
                cached_chart.data,
                export_format
            )
            
        except Exception as e:
            logger.error(f"Failed to export chart {chart_id}: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear chart cache"""
        try:
            self.chart_cache.clear()
            logger.info("Chart cache cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")


# Specialized visualization classes for domain-specific charts
class BusinessVisualization:
    """Business-specific visualization utilities"""
    
    def __init__(self, visualization_engine: VisualizationEngine):
        """
Initialize business visualization"""
        self.viz_engine = visualization_engine
    
    async def create_revenue_dashboard(self, revenue_data: Dict[str, Any]) -> List[VisualizationResult]:
        """
Create revenue dashboard charts"""
        charts = []
        
        # Revenue trend chart
        revenue_config = ChartConfig(
            title="Revenue Trend",
            chart_type=ChartType.AREA,
            width=1000,
            height=400,
            color_scheme=ColorScheme.CORPORATE
        )
        
        revenue_chart_data = ChartData(
            labels=revenue_data.get('dates', []),
            datasets=[{
                'label': 'Revenue',
                'data': revenue_data.get('values', []),
                'backgroundColor': '#3f51b5'
            }]
        )
        
        charts.append(await self.viz_engine.generate_chart(revenue_config, revenue_chart_data))
        
        # Revenue by source pie chart
        source_config = ChartConfig(
            title="Revenue by Source",
            chart_type=ChartType.PIE,
            width=600,
            height=600,
            color_scheme=ColorScheme.MATERIAL
        )
        
        source_chart_data = ChartData(
            labels=revenue_data.get('sources', []),
            datasets=[{
                'label': 'Revenue',
                'data': revenue_data.get('source_values', [])
            }]
        )
        
        charts.append(await self.viz_engine.generate_chart(source_config, source_chart_data))
        
        return charts
    
    async def create_user_analytics(self, user_data: Dict[str, Any]) -> List[VisualizationResult]:
        """Create user analytics charts"""
        charts = []
        
        # User growth chart
        growth_config = ChartConfig(
            title="User Growth",
            chart_type=ChartType.LINE,
            width=900,
            height=400,
            color_scheme=ColorScheme.VIRIDIS
        )
        
        growth_chart_data = ChartData(
            labels=user_data.get('dates', []),
            datasets=[{
                'label': 'Active Users',
                'data': user_data.get('active_users', [])
            }, {
                'label': 'New Users',
                'data': user_data.get('new_users', [])
            }]
        )
        
        charts.append(await self.viz_engine.generate_chart(growth_config, growth_chart_data))
        
        return charts


class TechnicalVisualization:
    """Technical monitoring visualization utilities"""
    
    def __init__(self, visualization_engine: VisualizationEngine):
        """
Initialize technical visualization"""
        self.viz_engine = visualization_engine
    
    async def create_performance_charts(self, performance_data: Dict[str, Any]) -> List[VisualizationResult]:
        """
Create performance monitoring charts"""
        charts = []
        
        # Response time chart
        response_config = ChartConfig(
            title="API Response Time",
            chart_type=ChartType.LINE,
            width=800,
            height=400,
            color_scheme=ColorScheme.BLUES
        )
        
        response_chart_data = ChartData(
            labels=performance_data.get('timestamps', []),
            datasets=[{
                'label': 'Response Time (ms)',
                'data': performance_data.get('response_times', [])
            }]
        )
        
        charts.append(await self.viz_engine.generate_chart(response_config, response_chart_data))
        
        # Resource usage heatmap
        resource_config = ChartConfig(
            title="Resource Usage Heatmap",
            chart_type=ChartType.HEATMAP,
            width=1000,
            height=600,
            color_scheme=ColorScheme.VIRIDIS
        )
        
        resource_chart_data = ChartData(
            labels=performance_data.get('resources', []),
            datasets=[{
                'label': 'Usage %',
                'data': performance_data.get('usage_matrix', [])
            }]
        )
        
        charts.append(await self.viz_engine.generate_chart(resource_config, resource_chart_data))
        
        return charts
