#!/usr/bin/env python3
"""
Development File Watcher
Monitors file changes and triggers hot-reload for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class AinflueDevelopmentHandler(FileSystemEventHandler):
    """Enhanced file system event handler for Ainflue development."""
    
    def __init__(self):
        self.last_reload = 0
        self.reload_delay = 2  # seconds
        self.ignored_extensions = {'.pyc', '.pyo', '.pyd', '__pycache__'}
        self.ignored_directories = {'__pycache__', '.pytest_cache', '.git', 'node_modules'}
        
    def should_ignore(self, path):
        """Check if file should be ignored."""
        path_obj = Path(path)
        
        # Check extensions
        if path_obj.suffix in self.ignored_extensions:
            return True
            
        # Check directory names
        for part in path_obj.parts:
            if part in self.ignored_directories:
                return True
                
        return False
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory or self.should_ignore(event.src_path):
            return
            
        current_time = time.time()
        if current_time - self.last_reload < self.reload_delay:
            return
            
        self.last_reload = current_time
        
        console.print(f"🔄 File changed: {event.src_path}", style="yellow")
        self.trigger_reload(event.src_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory or self.should_ignore(event.src_path):
            return
            
        console.print(f"✨ File created: {event.src_path}", style="green")
        self.trigger_reload(event.src_path)
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if event.is_directory or self.should_ignore(event.src_path):
            return
            
        console.print(f"🗑️ File deleted: {event.src_path}", style="red")
        self.trigger_reload(event.src_path)
    
    def trigger_reload(self, file_path):
        """Trigger application reload."""
        try:
            # Check file type and run appropriate actions
            path_obj = Path(file_path)
            
            if path_obj.suffix == '.py':
                self.handle_python_change(file_path)
            elif path_obj.suffix in {'.yml', '.yaml'}:
                self.handle_config_change(file_path)
            elif path_obj.suffix == '.sql':
                self.handle_sql_change(file_path)
            elif path_obj.suffix in {'.js', '.ts', '.jsx', '.tsx'}:
                self.handle_frontend_change(file_path)
            
        except Exception as e:
            console.print(f"❌ Error during reload: {e}", style="red")
    
    def handle_python_change(self, file_path):
        """Handle Python file changes."""
        console.print("🐍 Python file changed - triggering reload", style="blue")
        
        # Run syntax check
        try:
            subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                         check=True, capture_output=True)
            console.print("✅ Syntax check passed", style="green")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Syntax error: {e.stderr.decode()}", style="red")
            return
            
        # Notify application (could send signal to running process)
        self.notify_application_reload()
    
    def handle_config_change(self, file_path):
        """Handle configuration file changes."""
        console.print("⚙️ Configuration file changed", style="cyan")
        self.notify_application_reload()
    
    def handle_sql_change(self, file_path):
        """Handle SQL file changes."""
        console.print("🗄️ SQL file changed", style="magenta")
        # Could validate SQL syntax here
        
    def handle_frontend_change(self, file_path):
        """Handle frontend file changes."""
        console.print("🎨 Frontend file changed", style="yellow")
        # Could trigger frontend build here
    
    def notify_application_reload(self):
        """Notify the application to reload."""
        # In a real implementation, this could send a signal to the FastAPI process
        # or use websockets to notify the development server
        console.print("📡 Notifying application to reload...", style="green")

def main():
    """Main function to start file watching."""
    console.print(Panel.fit(
        Text("🚀 Ainflue Development File Watcher", justify="center", style="bold blue"),
        title="Development Tools",
        border_style="blue"
    ))
    
    # Setup file watcher
    event_handler = AinflueDevelopmentHandler()
    observer = Observer()
    
    # Watch directories
    watch_paths = [
        '/app',  # Main application directory in Docker
        '/app/ai_agents',
        '/app/api',
        '/app/config',
        '/app/core'
    ]
    
    for path in watch_paths:
        if os.path.exists(path):
            observer.schedule(event_handler, path, recursive=True)
            console.print(f"👀 Watching: {path}")
    
    observer.start()
    console.print("🔍 File watcher started. Press Ctrl+C to stop.", style="green")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("🛑 File watcher stopped.", style="yellow")
    
    observer.join()

if __name__ == "__main__":
    main()