"""
Hot Reload Configuration Manager
===============================

Enterprise hot configuration reloading with file monitoring, change detection,
and zero-downtime configuration updates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Set
from datetime import datetime, timedelta
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

logger = logging.getLogger(__name__)

class ConfigurationChangeEvent:
    """Configuration change event."""
    
    def __init__(self, file_path: str, change_type: str, timestamp: datetime):
        self.file_path = file_path
        self.change_type = change_type  # 'modified', 'created', 'deleted'
        self.timestamp = timestamp

class ConfigurationFileHandler(FileSystemEventHandler):
    """File system event handler for configuration files."""
    
    def __init__(self, hot_reload_manager: 'HotReloadManager'):
        self.manager = hot_reload_manager
        self.config_extensions = {'.yaml', '.yml', '.json', '.toml', '.ini'}
        
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in self.config_extensions:
                change_event = ConfigurationChangeEvent(
                    file_path=str(file_path),
                    change_type='modified',
                    timestamp=datetime.now()
                )
                self.manager._handle_change_event(change_event)
                
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in self.config_extensions:
                change_event = ConfigurationChangeEvent(
                    file_path=str(file_path),
                    change_type='created',
                    timestamp=datetime.now()
                )
                self.manager._handle_change_event(change_event)
                
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in self.config_extensions:
                change_event = ConfigurationChangeEvent(
                    file_path=str(file_path),
                    change_type='deleted',
                    timestamp=datetime.now()
                )
                self.manager._handle_change_event(change_event)

class HotReloadManager:
    """
    Enterprise hot configuration reload manager.
    
    Features:
    - Real-time file monitoring
    - Debounced reload to prevent excessive reloads
    - Atomic configuration updates
    - Rollback on validation failure
    - Performance monitoring
    - Thread-safe operations
    """
    
    def __init__(self, config_manager, validation_schema=None):
        self.config_manager = config_manager
        self.validation_schema = validation_schema
        self.observer: Optional[Observer] = None
        self.is_monitoring = False
        
        # Configuration state
        self.watched_paths: Set[str] = set()
        self.last_reload_time = datetime.now()
        self.reload_debounce_seconds = 1.0
        self.pending_changes: List[ConfigurationChangeEvent] = []
        self.change_lock = threading.Lock()
        
        # Callbacks
        self.pre_reload_callbacks: List[Callable] = []
        self.post_reload_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Performance monitoring
        self.reload_count = 0
        self.last_reload_duration = 0.0
        self.total_reload_time = 0.0
        
        # Backup and rollback
        self.config_backup: Optional[Dict[str, Any]] = None
        self.enable_rollback = True
        
    def start_monitoring(self, paths: List[str]) -> None:
        """
        Start monitoring configuration files for changes.
        
        Args:
            paths: List of file or directory paths to monitor
        """
        if self.is_monitoring:
            logger.warning("Hot reload monitoring is already active")
            return
            
        self.observer = Observer()
        event_handler = ConfigurationFileHandler(self)
        
        for path in paths:
            path_obj = Path(path)
            if path_obj.exists():
                if path_obj.is_file():
                    # Monitor parent directory for file changes
                    watch_path = str(path_obj.parent)
                else:
                    # Monitor directory
                    watch_path = str(path_obj)
                    
                self.observer.schedule(event_handler, watch_path, recursive=True)
                self.watched_paths.add(watch_path)
                logger.info(f"Monitoring configuration path: {watch_path}")
            else:
                logger.warning(f"Configuration path does not exist: {path}")
                
        self.observer.start()
        self.is_monitoring = True
        logger.info("Hot reload monitoring started")
        
    def stop_monitoring(self) -> None:
        """Stop monitoring configuration files."""
        if not self.is_monitoring or not self.observer:
            return
            
        self.observer.stop()
        self.observer.join()
        self.observer = None
        self.is_monitoring = False
        self.watched_paths.clear()
        logger.info("Hot reload monitoring stopped")
        
    def _handle_change_event(self, event: ConfigurationChangeEvent) -> None:
        """Handle configuration file change event."""
        with self.change_lock:
            self.pending_changes.append(event)
            
        # Debounce: wait for a short period to collect multiple changes
        threading.Timer(self.reload_debounce_seconds, self._process_pending_changes).start()
        
    def _process_pending_changes(self) -> None:
        """Process all pending configuration changes."""
        with self.change_lock:
            if not self.pending_changes:
                return
                
            # Check if enough time has passed since last reload
            time_since_last_reload = datetime.now() - self.last_reload_time
            if time_since_last_reload < timedelta(seconds=self.reload_debounce_seconds):
                return
                
            changes = self.pending_changes.copy()
            self.pending_changes.clear()
            
        logger.info(f"Processing {len(changes)} configuration changes")
        
        try:
            self._reload_configuration(changes)
        except Exception as e:
            logger.error(f"Failed to process configuration changes: {e}")
            
    def _reload_configuration(self, changes: List[ConfigurationChangeEvent]) -> None:
        """Reload configuration with atomic updates and validation."""
        start_time = time.time()
        
        try:
            # Run pre-reload callbacks
            self._run_callbacks(self.pre_reload_callbacks, "pre-reload")
            
            # Backup current configuration if rollback is enabled
            if self.enable_rollback:
                self.config_backup = self.config_manager.get_all()
                
            # Determine what needs to be reloaded based on changes
            modified_files = {change.file_path for change in changes if change.change_type == 'modified'}
            created_files = {change.file_path for change in changes if change.change_type == 'created'}
            deleted_files = {change.file_path for change in changes if change.change_type == 'deleted'}
            
            logger.info(f"Reloading config: {len(modified_files)} modified, {len(created_files)} created, {len(deleted_files)} deleted")
            
            # Reload configuration
            new_config = self._load_updated_configuration(modified_files, created_files, deleted_files)
            
            # Validate new configuration
            if self.validation_schema:
                validation_result = self.validation_schema.validate_config(new_config)
                if not validation_result.is_valid:
                    error_msg = f"Configuration validation failed: {validation_result.errors}"
                    logger.error(error_msg)
                    
                    if self.enable_rollback and self.config_backup:
                        self._rollback_configuration()
                        
                    self._run_callbacks(self.error_callbacks, "validation-error", error_msg)
                    return
                    
            # Apply new configuration atomically
            self.config_manager._config_data = new_config
            
            # Update performance metrics
            reload_duration = time.time() - start_time
            self.reload_count += 1
            self.last_reload_duration = reload_duration
            self.total_reload_time += reload_duration
            self.last_reload_time = datetime.now()
            
            # Run post-reload callbacks
            self._run_callbacks(self.post_reload_callbacks, "post-reload")
            
            logger.info(f"Configuration reloaded successfully in {reload_duration:.3f}s")
            
        except Exception as e:
            logger.error(f"Configuration reload failed: {e}")
            
            if self.enable_rollback and self.config_backup:
                self._rollback_configuration()
                
            self._run_callbacks(self.error_callbacks, "reload-error", str(e))
            
    def _load_updated_configuration(self, modified_files: Set[str], 
                                   created_files: Set[str], 
                                   deleted_files: Set[str]) -> Dict[str, Any]:
        """Load updated configuration from changed files."""
        # For simplicity, we reload all configuration
        # In a more sophisticated implementation, we could selectively update
        return self.config_manager.load_configuration()
        
    def _rollback_configuration(self) -> None:
        """Rollback to previous configuration."""
        if self.config_backup:
            self.config_manager._config_data = self.config_backup
            logger.info("Configuration rolled back to previous state")
        else:
            logger.warning("No backup available for rollback")
            
    def _run_callbacks(self, callbacks: List[Callable], callback_type: str, *args) -> None:
        """Run callback functions."""
        for callback in callbacks:
            try:
                callback(*args)
            except Exception as e:
                logger.error(f"{callback_type} callback failed: {e}")
                
    def add_pre_reload_callback(self, callback: Callable) -> None:
        """Add callback to run before configuration reload."""
        self.pre_reload_callbacks.append(callback)
        
    def add_post_reload_callback(self, callback: Callable) -> None:
        """Add callback to run after successful configuration reload."""
        self.post_reload_callbacks.append(callback)
        
    def add_error_callback(self, callback: Callable) -> None:
        """Add callback to run when reload fails."""
        self.error_callbacks.append(callback)
        
    def remove_callback(self, callback: Callable) -> None:
        """Remove callback from all callback lists."""
        for callback_list in [self.pre_reload_callbacks, self.post_reload_callbacks, self.error_callbacks]:
            if callback in callback_list:
                callback_list.remove(callback)
                
    def force_reload(self) -> None:
        """Force immediate configuration reload."""
        logger.info("Forcing configuration reload")
        self._reload_configuration([])
        
    def get_reload_stats(self) -> Dict[str, Any]:
        """Get hot reload performance statistics."""
        return {
            'is_monitoring': self.is_monitoring,
            'watched_paths': list(self.watched_paths),
            'reload_count': self.reload_count,
            'last_reload_duration': self.last_reload_duration,
            'average_reload_duration': self.total_reload_time / max(self.reload_count, 1),
            'total_reload_time': self.total_reload_time,
            'last_reload_time': self.last_reload_time.isoformat(),
            'pending_changes': len(self.pending_changes)
        }
        
    def set_debounce_time(self, seconds: float) -> None:
        """Set debounce time for configuration reloads."""
        self.reload_debounce_seconds = max(0.1, seconds)
        logger.info(f"Reload debounce time set to {self.reload_debounce_seconds}s")
        
    def enable_backup_rollback(self, enable: bool = True) -> None:
        """Enable or disable automatic rollback on validation failure."""
        self.enable_rollback = enable
        logger.info(f"Automatic rollback {'enabled' if enable else 'disabled'}")
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_monitoring()