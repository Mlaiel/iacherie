#!/usr/bin/env python3
"""
🔄 Configuration Watcher - Enterprise Infrastructure Service
============================================================

Dynamic configuration watcher service for real-time configuration changes.
Provides automated configuration monitoring, validation, and hot reloading.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import yaml
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ConfigurationChange:
    """Configuration change data structure."""
    file_path: str
    change_type: str  # 'created', 'modified', 'deleted'
    timestamp: datetime = field(default_factory=datetime.now)
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    validation_passed: bool = False
    applied: bool = False
    error_message: Optional[str] = None


class ConfigurationWatcher:
    """
    🔄 Enterprise Configuration Watcher Service
    
    Monitors configuration files for changes and provides real-time
    configuration updates with validation and hot reloading capabilities.
    """
    
    def __init__(self, config_paths: List[str]):
        """Initialize the configuration watcher."""
        self.config_paths = config_paths
        self.observers: List[Observer] = []
        self.configurations: Dict[str, Dict[str, Any]] = {}
        self.file_hashes: Dict[str, str] = {}
        self.change_callbacks: List[Callable] = []
        self.validation_callbacks: Dict[str, Callable] = {}
        self.change_history: List[ConfigurationChange] = []
        
        logger.info("🔄 Configuration Watcher Service initialized")
    
    async def start(self):
        """Start watching configuration files."""
        logger.info("🚀 Starting Configuration Watcher")
        
        # Load initial configurations
        await self._load_initial_configurations()
        
        # Start file watchers
        for config_path in self.config_paths:
            if Path(config_path).exists():
                observer = Observer()
                observer.schedule(
                    ConfigFileHandler(self), 
                    config_path, 
                    recursive=True
                )
                observer.start()
                self.observers.append(observer)
                logger.info(f"👀 Watching configuration path: {config_path}")
        
        logger.info("✅ Configuration Watcher started")
    
    async def stop(self):
        """Stop the configuration watcher."""
        logger.info("🛑 Stopping Configuration Watcher")
        
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        logger.info("✅ Configuration Watcher stopped")
    
    async def _load_initial_configurations(self):
        """Load initial configuration files."""
        for config_path in self.config_paths:
            path = Path(config_path)
            if path.is_file():
                await self._load_configuration_file(str(path))
            elif path.is_dir():
                for file_path in path.rglob("*.yaml"):
                    await self._load_configuration_file(str(file_path))
                for file_path in path.rglob("*.yml"):
                    await self._load_configuration_file(str(file_path))
                for file_path in path.rglob("*.json"):
                    await self._load_configuration_file(str(file_path))
    
    async def _load_configuration_file(self, file_path: str):
        """Load a single configuration file."""
        try:
            path = Path(file_path)
            content = path.read_text()
            
            # Calculate file hash
            file_hash = hashlib.md5(content.encode()).hexdigest()
            self.file_hashes[file_path] = file_hash
            
            # Parse configuration based on file extension
            if path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(content)
            elif path.suffix.lower() == '.json':
                config_data = json.loads(content)
            else:
                logger.warning(f"⚠️ Unsupported configuration file format: {file_path}")
                return
            
            self.configurations[file_path] = config_data
            logger.info(f"📁 Loaded configuration: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration {file_path}: {e}")
    
    async def handle_file_change(self, file_path: str, event_type: str):
        """Handle configuration file change."""
        try:
            change = ConfigurationChange(
                file_path=file_path,
                change_type=event_type,
                old_hash=self.file_hashes.get(file_path)
            )
            
            if event_type == 'deleted':
                # Handle file deletion
                if file_path in self.configurations:
                    del self.configurations[file_path]
                if file_path in self.file_hashes:
                    del self.file_hashes[file_path]
                
                change.applied = True
                logger.info(f"🗑️ Configuration file deleted: {file_path}")
                
            else:
                # Handle file creation or modification
                path = Path(file_path)
                if not path.exists():
                    return
                
                content = path.read_text()
                new_hash = hashlib.md5(content.encode()).hexdigest()
                change.new_hash = new_hash
                
                # Check if file actually changed
                if self.file_hashes.get(file_path) == new_hash:
                    return  # No actual change
                
                # Validate configuration
                validation_result = await self._validate_configuration(file_path, content)
                change.validation_passed = validation_result['valid']
                
                if not validation_result['valid']:
                    change.error_message = validation_result['error']
                    logger.error(f"❌ Configuration validation failed for {file_path}: {validation_result['error']}")
                else:
                    # Apply configuration change
                    try:
                        if path.suffix.lower() in ['.yaml', '.yml']:
                            config_data = yaml.safe_load(content)
                        elif path.suffix.lower() == '.json':
                            config_data = json.loads(content)
                        else:
                            raise ValueError(f"Unsupported file format: {path.suffix}")
                        
                        old_config = self.configurations.get(file_path, {})
                        self.configurations[file_path] = config_data
                        self.file_hashes[file_path] = new_hash
                        
                        # Notify change callbacks
                        await self._notify_change_callbacks(file_path, old_config, config_data)
                        
                        change.applied = True
                        logger.info(f"✅ Configuration updated: {file_path}")
                        
                    except Exception as e:
                        change.error_message = str(e)
                        logger.error(f"❌ Failed to apply configuration change for {file_path}: {e}")
            
            # Record change in history
            self.change_history.append(change)
            
            # Keep only last 1000 changes
            if len(self.change_history) > 1000:
                self.change_history = self.change_history[-1000:]
            
        except Exception as e:
            logger.error(f"❌ Error handling file change for {file_path}: {e}")
    
    async def _validate_configuration(self, file_path: str, content: str) -> Dict[str, Any]:
        """Validate configuration content."""
        try:
            # Basic syntax validation
            path = Path(file_path)
            if path.suffix.lower() in ['.yaml', '.yml']:
                yaml.safe_load(content)
            elif path.suffix.lower() == '.json':
                json.loads(content)
            
            # Custom validation if callback is registered
            if file_path in self.validation_callbacks:
                validation_func = self.validation_callbacks[file_path]
                custom_result = await validation_func(content)
                if not custom_result.get('valid', True):
                    return custom_result
            
            return {'valid': True}
            
        except yaml.YAMLError as e:
            return {'valid': False, 'error': f"YAML syntax error: {e}"}
        except json.JSONDecodeError as e:
            return {'valid': False, 'error': f"JSON syntax error: {e}"}
        except Exception as e:
            return {'valid': False, 'error': f"Validation error: {e}"}
    
    async def _notify_change_callbacks(self, file_path: str, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Notify registered change callbacks."""
        for callback in self.change_callbacks:
            try:
                await callback(file_path, old_config, new_config)
            except Exception as e:
                logger.error(f"❌ Error in change callback: {e}")
    
    def register_change_callback(self, callback: Callable):
        """Register a callback for configuration changes."""
        self.change_callbacks.append(callback)
        logger.info("📞 Registered configuration change callback")
    
    def register_validation_callback(self, file_pattern: str, callback: Callable):
        """Register a validation callback for specific files."""
        self.validation_callbacks[file_pattern] = callback
        logger.info(f"✅ Registered validation callback for: {file_pattern}")
    
    def get_configuration(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get current configuration for a file."""
        return self.configurations.get(file_path)
    
    def get_all_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Get all current configurations."""
        return self.configurations.copy()
    
    def get_change_history(self, limit: int = 100) -> List[ConfigurationChange]:
        """Get configuration change history."""
        return self.change_history[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration watcher status."""
        return {
            'watching_paths': self.config_paths,
            'loaded_configurations': len(self.configurations),
            'active_observers': len(self.observers),
            'registered_callbacks': len(self.change_callbacks),
            'validation_callbacks': len(self.validation_callbacks),
            'total_changes': len(self.change_history),
            'files_monitored': list(self.configurations.keys())
        }


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration files."""
    
    def __init__(self, watcher: ConfigurationWatcher):
        self.watcher = watcher
        super().__init__()
    
    def on_created(self, event):
        if not event.is_directory and self._is_config_file(event.src_path):
            asyncio.create_task(self.watcher.handle_file_change(event.src_path, 'created'))
    
    def on_modified(self, event):
        if not event.is_directory and self._is_config_file(event.src_path):
            asyncio.create_task(self.watcher.handle_file_change(event.src_path, 'modified'))
    
    def on_deleted(self, event):
        if not event.is_directory and self._is_config_file(event.src_path):
            asyncio.create_task(self.watcher.handle_file_change(event.src_path, 'deleted'))
    
    def _is_config_file(self, file_path: str) -> bool:
        """Check if file is a configuration file."""
        path = Path(file_path)
        return path.suffix.lower() in ['.yaml', '.yml', '.json']


async def main():
    """Example usage of the Configuration Watcher."""
    print("🔄 Configuration Watcher Example")
    print("=" * 36)
    
    # Create a test configuration directory
    test_dir = Path("/tmp/config_test")
    test_dir.mkdir(exist_ok=True)
    
    # Create test configuration files
    config1 = test_dir / "app.yaml"
    config1.write_text("""
app:
  name: "test-app"
  version: "1.0.0"
  debug: false
""")
    
    config2 = test_dir / "database.json"
    config2.write_text("""
{
  "host": "localhost",
  "port": 5432,
  "database": "testdb"
}
""")
    
    # Create configuration watcher
    watcher = ConfigurationWatcher([str(test_dir)])
    
    # Register change callback
    async def config_change_handler(file_path: str, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        print(f"🔄 Configuration changed: {file_path}")
        print(f"   Old config keys: {list(old_config.keys()) if old_config else 'None'}")
        print(f"   New config keys: {list(new_config.keys())}")
    
    watcher.register_change_callback(config_change_handler)
    
    # Start watcher
    await watcher.start()
    
    print("\n📁 Initial configurations loaded:")
    for file_path, config in watcher.get_all_configurations().items():
        print(f"   {file_path}: {list(config.keys())}")
    
    # Simulate configuration change
    print(f"\n🔄 Modifying configuration...")
    config1.write_text("""
app:
  name: "test-app"
  version: "1.1.0"
  debug: true
  features:
    - "feature1"
    - "feature2"
""")
    
    # Wait for change detection
    await asyncio.sleep(2)
    
    # Show status
    status = watcher.get_status()
    print(f"\n📊 Watcher Status:")
    print(f"   Loaded configurations: {status['loaded_configurations']}")
    print(f"   Total changes: {status['total_changes']}")
    print(f"   Active observers: {status['active_observers']}")
    
    # Show recent changes
    changes = watcher.get_change_history(5)
    print(f"\n📜 Recent Changes:")
    for change in changes:
        print(f"   {change.change_type}: {change.file_path} at {change.timestamp.strftime('%H:%M:%S')}")
    
    await watcher.stop()
    print("\n🛑 Configuration watcher stopped")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)


if __name__ == "__main__":
    asyncio.run(main())