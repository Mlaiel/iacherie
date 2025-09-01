#!/usr/bin/env python3
"""
Development Performance Monitor
Continuous performance monitoring and profiling for Ainflue platform development.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import time
import psutil
import asyncio
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import json

console = Console()

class PerformanceMonitor:
    """Enhanced performance monitoring for development."""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2.0  # seconds
        }
        
    def collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process-specific metrics (if available)
            process_metrics = self.get_process_metrics()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'cpu_count': cpu_count,
                    'memory_percent': memory_percent,
                    'memory_used_gb': memory_used,
                    'memory_total_gb': memory_total,
                    'disk_percent': disk_percent,
                    'disk_used_gb': disk_used,
                    'disk_total_gb': disk_total,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                },
                'process': process_metrics
            }
            
            return metrics
            
        except Exception as e:
            console.print(f"❌ Error collecting metrics: {e}", style="red")
            return None
    
    def get_process_metrics(self):
        """Get metrics for Python/FastAPI processes."""
        process_metrics = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if 'python' in pinfo['name'].lower() or 'uvicorn' in pinfo['name'].lower():
                        process_metrics.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_percent': pinfo['cpu_percent'],
                            'memory_percent': pinfo['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            console.print(f"⚠️ Warning collecting process metrics: {e}", style="yellow")
            
        return process_metrics
    
    def check_thresholds(self, metrics):
        """Check if metrics exceed thresholds and generate alerts."""
        alerts = []
        
        if not metrics or 'system' not in metrics:
            return alerts
            
        system = metrics['system']
        
        if system['cpu_percent'] > self.thresholds['cpu_usage']:
            alerts.append({
                'type': 'HIGH_CPU',
                'message': f"High CPU usage: {system['cpu_percent']:.1f}%",
                'severity': 'warning'
            })
            
        if system['memory_percent'] > self.thresholds['memory_usage']:
            alerts.append({
                'type': 'HIGH_MEMORY',
                'message': f"High memory usage: {system['memory_percent']:.1f}%",
                'severity': 'warning'
            })
            
        if system['disk_percent'] > self.thresholds['disk_usage']:
            alerts.append({
                'type': 'HIGH_DISK',
                'message': f"High disk usage: {system['disk_percent']:.1f}%",
                'severity': 'critical'
            })
            
        return alerts
    
    def create_performance_dashboard(self, metrics):
        """Create a rich dashboard display."""
        if not metrics:
            return Panel("❌ No metrics available", title="Performance Monitor")
            
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(Panel(
            Text("🔍 Ainflue Performance Monitor", justify="center", style="bold green"),
            subtitle=f"Last update: {datetime.now().strftime('%H:%M:%S')}"
        ))
        
        # Body - split into system and process metrics
        layout["body"].split_row(
            Layout(name="system"),
            Layout(name="processes")
        )
        
        # System metrics table
        system_table = Table(title="System Metrics", show_header=True)
        system_table.add_column("Metric", style="cyan")
        system_table.add_column("Value", style="magenta")
        system_table.add_column("Status", style="green")
        
        system = metrics['system']
        
        # Add rows with color coding based on thresholds
        cpu_status = "🔴 HIGH" if system['cpu_percent'] > self.thresholds['cpu_usage'] else "🟢 OK"
        memory_status = "🔴 HIGH" if system['memory_percent'] > self.thresholds['memory_usage'] else "🟢 OK"
        disk_status = "🔴 HIGH" if system['disk_percent'] > self.thresholds['disk_usage'] else "🟢 OK"
        
        system_table.add_row("CPU Usage", f"{system['cpu_percent']:.1f}%", cpu_status)
        system_table.add_row("Memory Usage", f"{system['memory_percent']:.1f}%", memory_status)
        system_table.add_row("Memory Used", f"{system['memory_used_gb']:.1f} GB", "")
        system_table.add_row("Disk Usage", f"{system['disk_percent']:.1f}%", disk_status)
        system_table.add_row("Disk Used", f"{system['disk_used_gb']:.1f} GB", "")
        
        layout["system"].update(Panel(system_table))
        
        # Process metrics table
        process_table = Table(title="Python Processes", show_header=True)
        process_table.add_column("PID", style="cyan")
        process_table.add_column("Name", style="blue")
        process_table.add_column("CPU %", style="magenta")
        process_table.add_column("Memory %", style="yellow")
        
        for proc in metrics['process'][:10]:  # Show top 10 processes
            process_table.add_row(
                str(proc['pid']),
                proc['name'],
                f"{proc['cpu_percent']:.1f}%",
                f"{proc['memory_percent']:.1f}%"
            )
        
        layout["processes"].update(Panel(process_table))
        
        # Footer with alerts
        alerts = self.check_thresholds(metrics)
        if alerts:
            alert_text = " | ".join([alert['message'] for alert in alerts])
            layout["footer"].update(Panel(
                Text(alert_text, style="bold red"),
                title="🚨 Alerts"
            ))
        else:
            layout["footer"].update(Panel(
                Text("All systems normal", style="bold green"),
                title="✅ Status"
            ))
        
        return layout
    
    def save_metrics(self, metrics):
        """Save metrics to file for historical analysis."""
        if not metrics:
            return
            
        # Create reports directory if it doesn't exist
        reports_dir = Path("/app/performance-reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Save to daily file
        date_str = datetime.now().strftime("%Y-%m-%d")
        metrics_file = reports_dir / f"metrics-{date_str}.jsonl"
        
        try:
            with open(metrics_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            console.print(f"⚠️ Failed to save metrics: {e}", style="yellow")

async def main():
    """Main monitoring loop."""
    monitor = PerformanceMonitor()
    
    console.print(Panel.fit(
        Text("🚀 Starting Ainflue Performance Monitor", justify="center", style="bold blue"),
        title="Development Tools",
        border_style="blue"
    ))
    
    try:
        with Live(refresh_per_second=1) as live:
            while True:
                # Collect metrics
                metrics = monitor.collect_system_metrics()
                
                # Update display
                dashboard = monitor.create_performance_dashboard(metrics)
                live.update(dashboard)
                
                # Save metrics
                monitor.save_metrics(metrics)
                
                # Wait before next collection
                await asyncio.sleep(5)
                
    except KeyboardInterrupt:
        console.print("🛑 Performance monitor stopped.", style="yellow")

if __name__ == "__main__":
    asyncio.run(main())