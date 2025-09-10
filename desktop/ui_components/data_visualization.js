/**
 * Ainflue Desktop - Data Visualization Components
 * 
 * Professional data visualization widgets for analytics and monitoring
 * Implements real-time charts, graphs, and interactive visualizations
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This code is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

class DataVisualizationComponents {
  constructor() {
    this.charts = new Map();
    this.animations = new Map();
    this.themes = {
      dark: {
        background: '#1a1a1a',
        surface: '#2a2a2a',
        primary: '#007aff',
        secondary: '#34c759',
        text: '#ffffff',
        textSecondary: '#888888',
        accent: '#ff9500',
        danger: '#ff3b30'
      },
      light: {
        background: '#ffffff',
        surface: '#f2f2f7',
        primary: '#007aff',
        secondary: '#34c759',
        text: '#000000',
        textSecondary: '#666666',
        accent: '#ff9500',
        danger: '#ff3b30'
      }
    };
    this.currentTheme = 'dark';
    
    this.initialize();
  }

  initialize() {
    this.setupCanvas();
    this.loadTheme();
    console.log('📊 Data Visualization Components initialized');
  }

  setupCanvas() {
    // Create canvas pool for high-performance rendering
    this.canvasPool = [];
    for (let i = 0; i < 5; i++) {
      const canvas = document.createElement('canvas');
      canvas.style.display = 'none';
      document.body.appendChild(canvas);
      this.canvasPool.push(canvas);
    }
  }

  loadTheme() {
    this.theme = this.themes[this.currentTheme];
  }

  // Real-time Line Chart for Analytics
  createRealtimeLineChart(container, options = {}) {
    const chartId = `chart_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const config = {
      title: 'Real-time Data',
      width: 800,
      height: 400,
      maxDataPoints: 100,
      updateInterval: 1000,
      smoothing: true,
      gridLines: true,
      legend: true,
      animation: true,
      metrics: ['views', 'engagement', 'revenue'],
      colors: [this.theme.primary, this.theme.secondary, this.theme.accent],
      ...options
    };

    const chart = {
      id: chartId,
      type: 'realtime_line',
      config,
      data: {
        timestamps: [],
        datasets: config.metrics.map((metric, index) => ({
          label: metric,
          data: [],
          color: config.colors[index] || this.theme.primary,
          visible: true
        }))
      },
      container,
      canvas: null,
      context: null,
      animationFrame: null
    };

    this.setupChart(chart);
    this.charts.set(chartId, chart);
    
    // Start real-time updates
    this.startRealtimeUpdates(chartId);

    return chartId;
  }

  // Revenue Analytics Dashboard
  createRevenueDashboard(container, options = {}) {
    const dashboardId = `dashboard_${Date.now()}`;
    
    const config = {
      title: 'Revenue Analytics',
      timeframe: '30d',
      currency: 'USD',
      metrics: {
        totalRevenue: { value: 0, change: 0 },
        activeStreams: { value: 0, change: 0 },
        averageRPM: { value: 0, change: 0 },
        conversionRate: { value: 0, change: 0 }
      },
      charts: ['revenue_trend', 'stream_performance', 'geographic_distribution'],
      ...options
    };

    container.innerHTML = `
      <div class="revenue-dashboard" id="${dashboardId}">
        <div class="dashboard-header">
          <h2>${config.title}</h2>
          <div class="timeframe-selector">
            <button class="timeframe-btn active" data-timeframe="7d">7D</button>
            <button class="timeframe-btn" data-timeframe="30d">30D</button>
            <button class="timeframe-btn" data-timeframe="90d">90D</button>
            <button class="timeframe-btn" data-timeframe="1y">1Y</button>
          </div>
        </div>
        
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">$${config.metrics.totalRevenue.value.toLocaleString()}</div>
            <div class="metric-change ${config.metrics.totalRevenue.change >= 0 ? 'positive' : 'negative'}">
              ${config.metrics.totalRevenue.change >= 0 ? '↗' : '↘'} ${Math.abs(config.metrics.totalRevenue.change)}%
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-label">Active Streams</div>
            <div class="metric-value">${config.metrics.activeStreams.value.toLocaleString()}</div>
            <div class="metric-change ${config.metrics.activeStreams.change >= 0 ? 'positive' : 'negative'}">
              ${config.metrics.activeStreams.change >= 0 ? '↗' : '↘'} ${Math.abs(config.metrics.activeStreams.change)}%
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-label">Average RPM</div>
            <div class="metric-value">$${config.metrics.averageRPM.value.toFixed(2)}</div>
            <div class="metric-change ${config.metrics.averageRPM.change >= 0 ? 'positive' : 'negative'}">
              ${config.metrics.averageRPM.change >= 0 ? '↗' : '↘'} ${Math.abs(config.metrics.averageRPM.change)}%
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-label">Conversion Rate</div>
            <div class="metric-value">${config.metrics.conversionRate.value.toFixed(1)}%</div>
            <div class="metric-change ${config.metrics.conversionRate.change >= 0 ? 'positive' : 'negative'}">
              ${config.metrics.conversionRate.change >= 0 ? '↗' : '↘'} ${Math.abs(config.metrics.conversionRate.change)}%
            </div>
          </div>
        </div>
        
        <div class="charts-grid">
          <div class="chart-container">
            <canvas class="revenue-trend-chart"></canvas>
          </div>
          <div class="chart-container">
            <canvas class="performance-heatmap"></canvas>
          </div>
        </div>
      </div>
    `;

    this.addDashboardStyling();
    this.setupDashboardEventHandlers(dashboardId);
    this.loadRevenueData(dashboardId, config);

    return dashboardId;
  }

  // Performance Monitoring Charts
  createPerformanceMonitor(container, options = {}) {
    const monitorId = `monitor_${Date.now()}`;
    
    const config = {
      title: 'System Performance',
      metrics: ['cpu', 'memory', 'gpu', 'network'],
      updateInterval: 1000,
      historyLength: 60,
      ...options
    };

    container.innerHTML = `
      <div class="performance-monitor" id="${monitorId}">
        <div class="monitor-header">
          <h3>${config.title}</h3>
          <div class="monitor-controls">
            <button class="pause-btn">⏸</button>
            <button class="reset-btn">🔄</button>
          </div>
        </div>
        
        <div class="metrics-container">
          <div class="metric-chart cpu-chart">
            <div class="metric-title">CPU Usage</div>
            <canvas class="metric-canvas"></canvas>
            <div class="metric-current">0%</div>
          </div>
          
          <div class="metric-chart memory-chart">
            <div class="metric-title">Memory Usage</div>
            <canvas class="metric-canvas"></canvas>
            <div class="metric-current">0 MB</div>
          </div>
          
          <div class="metric-chart gpu-chart">
            <div class="metric-title">GPU Usage</div>
            <canvas class="metric-canvas"></canvas>
            <div class="metric-current">0%</div>
          </div>
          
          <div class="metric-chart network-chart">
            <div class="metric-title">Network I/O</div>
            <canvas class="metric-canvas"></canvas>
            <div class="metric-current">0 KB/s</div>
          </div>
        </div>
      </div>
    `;

    this.setupPerformanceMonitor(monitorId, config);
    return monitorId;
  }

  // Audio Waveform Visualizer
  createWaveformVisualizer(container, options = {}) {
    const vizId = `waveform_${Date.now()}`;
    
    const config = {
      width: 800,
      height: 200,
      color: this.theme.primary,
      backgroundColor: this.theme.surface,
      responsive: true,
      interactive: true,
      showTimeaxis: true,
      showFrequencyData: false,
      ...options
    };

    const canvas = document.createElement('canvas');
    canvas.width = config.width;
    canvas.height = config.height;
    canvas.className = 'waveform-canvas';
    canvas.id = vizId;
    
    container.appendChild(canvas);
    
    const visualizer = {
      id: vizId,
      type: 'waveform',
      config,
      canvas,
      context: canvas.getContext('2d'),
      audioData: null,
      isPlaying: false,
      currentTime: 0
    };

    this.setupWaveformInteraction(visualizer);
    this.renderWaveform(visualizer);
    return vizId;
  }

  // Chart Setup and Rendering Methods
  setupChart(chart) {
    const canvas = document.createElement('canvas');
    canvas.width = chart.config.width;
    canvas.height = chart.config.height;
    canvas.className = 'chart-canvas';
    
    chart.container.appendChild(canvas);
    chart.canvas = canvas;
    chart.context = canvas.getContext('2d');
    
    // Setup responsive resizing
    if (chart.config.responsive) {
      this.makeResponsive(chart);
    }
  }

  makeResponsive(chart) {
    const resizeObserver = new ResizeObserver(() => {
      const rect = chart.container.getBoundingClientRect();
      chart.canvas.width = rect.width;
      chart.canvas.height = rect.height;
      this.renderChart(chart);
    });
    
    resizeObserver.observe(chart.container);
  }

  renderChart(chart) {
    const { canvas, context, config, data } = chart;
    
    // Clear canvas
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set background
    context.fillStyle = this.theme.background;
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    switch (chart.type) {
      case 'realtime_line':
        this.renderRealtimeLineChart(chart);
        break;
      case 'waveform':
        this.renderWaveform(chart);
        break;
      default:
        console.warn(`Unknown chart type: ${chart.type}`);
    }
  }

  renderRealtimeLineChart(chart) {
    const { context, config, data, canvas } = chart;
    const { width, height } = canvas;
    
    // Draw grid
    if (config.gridLines) {
      this.drawGrid(context, width, height);
    }
    
    // Draw axes
    this.drawAxes(context, width, height);
    
    // Draw data lines
    data.datasets.forEach((dataset, index) => {
      if (!dataset.visible || dataset.data.length < 2) return;
      
      context.strokeStyle = dataset.color;
      context.lineWidth = 2;
      context.beginPath();
      
      const xStep = (width - 80) / (config.maxDataPoints - 1);
      const yScale = (height - 80) / 100; // Assuming 0-100 scale
      
      dataset.data.forEach((value, pointIndex) => {
        const x = 60 + pointIndex * xStep;
        const y = height - 60 - (value * yScale);
        
        if (pointIndex === 0) {
          context.moveTo(x, y);
        } else {
          context.lineTo(x, y);
        }
      });
      
      context.stroke();
    });
    
    // Draw legend
    if (config.legend) {
      this.drawLegend(context, data.datasets, width, height);
    }
  }

  renderWaveform(visualizer) {
    const { context, config, canvas, audioData } = visualizer;
    const { width, height } = canvas;
    
    context.clearRect(0, 0, width, height);
    
    // Background
    context.fillStyle = config.backgroundColor;
    context.fillRect(0, 0, width, height);
    
    if (!audioData) {
      // Draw placeholder waveform
      this.drawPlaceholderWaveform(context, width, height, config.color);
      return;
    }
    
    // Draw actual waveform
    context.strokeStyle = config.color;
    context.lineWidth = 1;
    context.beginPath();
    
    const centerY = height / 2;
    const amplitude = height * 0.4;
    
    for (let i = 0; i < audioData.length; i++) {
      const x = (i / audioData.length) * width;
      const y = centerY + (audioData[i] * amplitude);
      
      if (i === 0) {
        context.moveTo(x, y);
      } else {
        context.lineTo(x, y);
      }
    }
    
    context.stroke();
  }

  // Helper Drawing Methods
  drawGrid(context, width, height) {
    context.strokeStyle = this.theme.textSecondary + '40';
    context.lineWidth = 1;
    
    // Vertical lines
    for (let x = 60; x <= width - 20; x += (width - 80) / 10) {
      context.beginPath();
      context.moveTo(x, 20);
      context.lineTo(x, height - 60);
      context.stroke();
    }
    
    // Horizontal lines
    for (let y = 20; y <= height - 60; y += (height - 80) / 5) {
      context.beginPath();
      context.moveTo(60, y);
      context.lineTo(width - 20, y);
      context.stroke();
    }
  }

  drawAxes(context, width, height) {
    context.strokeStyle = this.theme.text;
    context.lineWidth = 2;
    
    // Y-axis
    context.beginPath();
    context.moveTo(60, 20);
    context.lineTo(60, height - 60);
    context.stroke();
    
    // X-axis
    context.beginPath();
    context.moveTo(60, height - 60);
    context.lineTo(width - 20, height - 60);
    context.stroke();
  }

  drawLegend(context, datasets, width, height) {
    const legendX = width - 150;
    const legendY = 30;
    
    datasets.forEach((dataset, index) => {
      const y = legendY + index * 25;
      
      // Color box
      context.fillStyle = dataset.color;
      context.fillRect(legendX, y, 15, 15);
      
      // Label
      context.fillStyle = this.theme.text;
      context.font = '12px Arial';
      context.fillText(dataset.label, legendX + 20, y + 12);
    });
  }

  drawPlaceholderWaveform(context, width, height, color) {
    context.strokeStyle = color + '60';
    context.lineWidth = 1;
    context.beginPath();
    
    const centerY = height / 2;
    const frequency = 0.02;
    const amplitude = height * 0.2;
    
    for (let x = 0; x < width; x++) {
      const y = centerY + Math.sin(x * frequency) * amplitude * Math.random();
      
      if (x === 0) {
        context.moveTo(x, y);
      } else {
        context.lineTo(x, y);
      }
    }
    
    context.stroke();
  }

  // Real-time Data Management
  startRealtimeUpdates(chartId) {
    const chart = this.charts.get(chartId);
    if (!chart) return;
    
    const updateInterval = setInterval(() => {
      this.updateRealtimeData(chart);
      this.renderChart(chart);
    }, chart.config.updateInterval);
    
    chart.updateInterval = updateInterval;
  }

  updateRealtimeData(chart) {
    const now = Date.now();
    chart.data.timestamps.push(now);
    
    chart.data.datasets.forEach(dataset => {
      // Generate mock data
      const newValue = Math.random() * 100;
      dataset.data.push(newValue);
      
      // Limit data points
      if (dataset.data.length > chart.config.maxDataPoints) {
        dataset.data.shift();
      }
    });
    
    // Limit timestamps
    if (chart.data.timestamps.length > chart.config.maxDataPoints) {
      chart.data.timestamps.shift();
    }
  }

  // Event Handlers and Interactions
  setupWaveformInteraction(visualizer) {
    const { canvas } = visualizer;
    
    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const progress = x / canvas.width;
      
      // Simulate seeking in audio
      visualizer.currentTime = progress;
      console.log(`🔊 Seek to ${(progress * 100).toFixed(1)}%`);
    });
    
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const progress = x / canvas.width;
      
      // Show time tooltip
      canvas.title = `${(progress * 100).toFixed(1)}%`;
    });
  }

  setupDashboardEventHandlers(dashboardId) {
    const dashboard = document.getElementById(dashboardId);
    
    // Timeframe selector
    dashboard.querySelectorAll('.timeframe-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        dashboard.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        const timeframe = e.target.dataset.timeframe;
        this.updateDashboardTimeframe(dashboardId, timeframe);
      });
    });
  }

  setupPerformanceMonitor(monitorId, config) {
    const monitor = document.getElementById(monitorId);
    let isPaused = false;
    
    // Setup canvases for each metric
    const canvases = monitor.querySelectorAll('.metric-canvas');
    canvases.forEach(canvas => {
      canvas.width = 200;
      canvas.height = 100;
    });
    
    // Start monitoring
    const updateInterval = setInterval(() => {
      if (!isPaused) {
        this.updatePerformanceMetrics(monitorId);
      }
    }, config.updateInterval);
    
    // Pause/resume
    monitor.querySelector('.pause-btn').addEventListener('click', () => {
      isPaused = !isPaused;
      const btn = monitor.querySelector('.pause-btn');
      btn.textContent = isPaused ? '▶' : '⏸';
    });
    
    // Reset
    monitor.querySelector('.reset-btn').addEventListener('click', () => {
      this.resetPerformanceMonitor(monitorId);
    });
  }

  // Data Loading and Updates
  loadRevenueData(dashboardId, config) {
    // Simulate loading revenue data
    setTimeout(() => {
      config.metrics.totalRevenue.value = Math.floor(Math.random() * 50000) + 10000;
      config.metrics.totalRevenue.change = Math.floor(Math.random() * 40) - 20;
      
      config.metrics.activeStreams.value = Math.floor(Math.random() * 1000) + 100;
      config.metrics.activeStreams.change = Math.floor(Math.random() * 30) - 15;
      
      config.metrics.averageRPM.value = Math.random() * 10 + 2;
      config.metrics.averageRPM.change = Math.floor(Math.random() * 20) - 10;
      
      config.metrics.conversionRate.value = Math.random() * 10 + 1;
      config.metrics.conversionRate.change = Math.floor(Math.random() * 15) - 7;
      
      this.updateDashboardMetrics(dashboardId, config.metrics);
    }, 1000);
  }

  updateDashboardMetrics(dashboardId, metrics) {
    const dashboard = document.getElementById(dashboardId);
    
    Object.entries(metrics).forEach(([key, metric]) => {
      const cards = dashboard.querySelectorAll('.metric-card');
      // Update logic would be implemented here
    });
  }

  updatePerformanceMetrics(monitorId) {
    const monitor = document.getElementById(monitorId);
    
    // Generate mock performance data
    const metrics = {
      cpu: Math.random() * 50 + 10,
      memory: Math.random() * 2000 + 500,
      gpu: Math.random() * 60 + 5,
      network: Math.random() * 1000 + 50
    };
    
    // Update displays
    monitor.querySelector('.cpu-chart .metric-current').textContent = `${metrics.cpu.toFixed(1)}%`;
    monitor.querySelector('.memory-chart .metric-current').textContent = `${metrics.memory.toFixed(0)} MB`;
    monitor.querySelector('.gpu-chart .metric-current').textContent = `${metrics.gpu.toFixed(1)}%`;
    monitor.querySelector('.network-chart .metric-current').textContent = `${metrics.network.toFixed(0)} KB/s`;
  }

  // Styling
  addDashboardStyling() {
    if (document.getElementById('dashboard-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'dashboard-styles';
    style.textContent = `
      .revenue-dashboard {
        background: ${this.theme.background};
        color: ${this.theme.text};
        padding: 20px;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
      }
      
      .timeframe-selector {
        display: flex;
        gap: 4px;
      }
      
      .timeframe-btn {
        background: ${this.theme.surface};
        border: 1px solid ${this.theme.textSecondary}40;
        color: ${this.theme.text};
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
      }
      
      .timeframe-btn.active {
        background: ${this.theme.primary};
        color: white;
        border-color: ${this.theme.primary};
      }
      
      .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
      }
      
      .metric-card {
        background: ${this.theme.surface};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid ${this.theme.textSecondary}20;
      }
      
      .metric-change.positive {
        color: ${this.theme.secondary};
      }
      
      .metric-change.negative {
        color: ${this.theme.danger};
      }
      
      .performance-monitor {
        background: ${this.theme.background};
        color: ${this.theme.text};
        padding: 16px;
        border-radius: 12px;
      }
      
      .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
      }
      
      .metric-chart {
        background: ${this.theme.surface};
        padding: 12px;
        border-radius: 8px;
        text-align: center;
      }
    `;
    document.head.appendChild(style);
  }

  // Public API
  updateChart(chartId, newData) {
    const chart = this.charts.get(chartId);
    if (chart) {
      chart.data = { ...chart.data, ...newData };
      this.renderChart(chart);
    }
  }

  destroyChart(chartId) {
    const chart = this.charts.get(chartId);
    if (chart) {
      if (chart.updateInterval) {
        clearInterval(chart.updateInterval);
      }
      if (chart.animationFrame) {
        cancelAnimationFrame(chart.animationFrame);
      }
      chart.canvas?.remove();
      this.charts.delete(chartId);
    }
  }

  setTheme(theme) {
    this.currentTheme = theme;
    this.loadTheme();
    
    // Re-render all charts
    this.charts.forEach(chart => {
      this.renderChart(chart);
    });
  }

  exportChart(chartId, format = 'png') {
    const chart = this.charts.get(chartId);
    if (!chart) return null;
    
    return chart.canvas.toDataURL(`image/${format}`);
  }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DataVisualizationComponents;
}