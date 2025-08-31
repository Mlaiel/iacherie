"""AI Core Module Setup and Installation

Provides setup utilities for the AI core module including:
- Dependency installation
- Configuration validation
- Environment setup
- Model downloading
- Database initialization

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import asyncio
from datetime import datetime

# Import core components for setup
from .config import CoreConfig, ConfigManager
from .exceptions import BaseAIException

logger = logging.getLogger(__name__)


class SetupError(BaseAIException):
    """Exception raised during module setup"""    pass


class ModuleSetup:
    """    AI Core Module Setup Manager
    
    Handles complete module setup including:
    - Environment validation
    - Dependency installation
    - Configuration initialization
    - Model preparation
    - System validation
    """    
    def __init__(self, setup_config: Optional[Dict[str, Any]] = None):
        self.setup_config = setup_config or {}
        self.setup_log = []
        self.config_manager = ConfigManager()
        
    def log_step(self, message: str, level: str = "INFO"):
        """Log setup step"""        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.setup_log.append(log_entry)
        
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
            
    def check_system_requirements(self) -> bool:
        """Check system requirements for AI core module"""        self.log_step("Checking system requirements...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version < (3, 8):
                raise SetupError(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
                
            self.log_step(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check available memory
            try:
                import psutil
                memory_gb = psutil.virtual_memory().total / (1024**3)
                if memory_gb < 4:
                    self.log_step(f"Warning: Low memory detected ({memory_gb:.1f}GB). Recommend 8GB+", "WARNING")
                else:
                    self.log_step(f"System memory: {memory_gb:.1f}GB")
            except ImportError:
                self.log_step("Could not check system memory (psutil not installed)", "WARNING")
                
            # Check disk space
            try:
                disk_usage = os.statvfs('.')
                free_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
                if free_gb < 5:
                    self.log_step(f"Warning: Low disk space ({free_gb:.1f}GB free). Recommend 10GB+", "WARNING")
                else:
                    self.log_step(f"Free disk space: {free_gb:.1f}GB")
            except (OSError, AttributeError):
                self.log_step("Could not check disk space", "WARNING")
                
            # Check GPU availability
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_count = torch.cuda.device_count()
                    gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                    self.log_step(f"GPU detected: {gpu_name} ({gpu_count} devices)")
                else:
                    self.log_step("No GPU detected - using CPU mode", "WARNING")
            except ImportError:
                self.log_step("PyTorch not installed - cannot check GPU", "WARNING")
                
            self.log_step("System requirements check completed")
            return True
            
        except Exception as e:
            self.log_step(f"System requirements check failed: {e}", "ERROR")
            return False
            
    def install_dependencies(self) -> bool:
        """Install required dependencies"""        self.log_step("Installing dependencies...")
        
        # Core dependencies
        core_deps = [
            "torch>=1.9.0",
            "tensorflow>=2.8.0",
            "transformers>=4.20.0",
            "opencv-python>=4.5.0",
            "librosa>=0.9.0",
            "psutil>=5.8.0",
            "numpy>=1.21.0",
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0",
            "Pillow>=8.3.0",
            "requests>=2.25.0",
            "aiohttp>=3.8.0",
            "asyncio-throttle>=1.0.0"
        ]
        
        # Optional dependencies
        optional_deps = [
            "accelerate>=0.12.0",  # For GPU optimization
            "soundfile>=0.10.0",   # For audio processing
            "ffmpeg-python>=0.2.0", # For video processing
            "prometheus-client>=0.14.0",  # For metrics export
            "redis>=4.0.0",        # For caching
            "sqlalchemy>=1.4.0"    # For database support
        ]
        
        try:
            # Install core dependencies
            for dep in core_deps:
                self.log_step(f"Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.log_step(f"Failed to install {dep}: {result.stderr}", "ERROR")
                    return False
                    
            # Install optional dependencies (non-critical)
            for dep in optional_deps:
                self.log_step(f"Installing optional dependency {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.log_step(f"Optional dependency {dep} failed to install (skipping)", "WARNING")
                    
            self.log_step("Dependencies installation completed")
            return True
            
        except Exception as e:
            self.log_step(f"Dependencies installation failed: {e}", "ERROR")
            return False
            
    def setup_configuration(self, config_path: Optional[str] = None) -> bool:
        """Setup initial configuration"""        self.log_step("Setting up configuration...")
        
        try:
            # Create default configuration
            config = CoreConfig()
            
            # Apply setup-specific configuration
            if self.setup_config:
                if "environment" in self.setup_config:
                    config.environment = self.setup_config["environment"]
                if "debug_mode" in self.setup_config:
                    config.debug_mode = self.setup_config["debug_mode"]
                    
            # Validate configuration
            self.config_manager._validate_config(config)
            
            # Save configuration if path provided
            if config_path:
                config_path = Path(config_path)
                config_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(config_path, 'w') as f:
                    json.dump(config.to_dict(), f, indent=2)
                    
                self.log_step(f"Configuration saved to {config_path}")
            else:
                self.log_step("Configuration created (not saved to file)")
                
            self.log_step("Configuration setup completed")
            return True
            
        except Exception as e:
            self.log_step(f"Configuration setup failed: {e}", "ERROR")
            return False
            
    def create_directories(self) -> bool:
        """Create necessary directories"""        self.log_step("Creating directories...")
        
        directories = [
            "models",
            "cache",
            "logs",
            "data/uploads",
            "data/processed",
            "data/exports",
            "backups",
            "temp"
        ]
        
        try:
            for directory in directories:
                dir_path = Path(directory)
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log_step(f"Created directory: {directory}")
                
            self.log_step("Directory creation completed")
            return True
            
        except Exception as e:
            self.log_step(f"Directory creation failed: {e}", "ERROR")
            return False
            
    def download_default_models(self) -> bool:
        """Download default AI models"""        self.log_step("Downloading default models...")
        
        # Default models to download
        models = [
            {
                "name": "text-classifier",
                "url": "https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english",
                "type": "huggingface"
            },
            {
                "name": "audio-classifier", 
                "url": "https://huggingface.co/MIT/ast-finetuned-audioset-10-10-0.4593",
                "type": "huggingface"
            }
        ]
        
        try:
            # Try to download models if transformers is available
            try:
                from transformers import AutoModel, AutoTokenizer
                
                for model in models:
                    self.log_step(f"Downloading model: {model['name']}")
                    
                    model_path = Path("models") / model["name"]
                    model_path.mkdir(parents=True, exist_ok=True)
                    
                    # Download model and tokenizer
                    try:
                        AutoModel.from_pretrained(model["url"])
                        AutoTokenizer.from_pretrained(model["url"])
                        self.log_step(f"Model {model['name']} downloaded successfully")
                    except Exception as model_e:
                        self.log_step(f"Failed to download {model['name']}: {model_e}", "WARNING")
                        
            except ImportError:
                self.log_step("Transformers not available - skipping model downloads", "WARNING")
                
            self.log_step("Model download process completed")
            return True
            
        except Exception as e:
            self.log_step(f"Model download failed: {e}", "ERROR")
            return False
            
    def validate_installation(self) -> bool:
        """Validate the installation"""        self.log_step("Validating installation...")
        
        try:
            # Test imports
            from . import exceptions, metrics, performance, validation, ai_engine, content_processor, config
            self.log_step("Core modules imported successfully")
            
            # Test basic functionality
            from .metrics import MetricsCollector
            from .performance import PerformanceMonitor
            from .validation import ContentValidator
            
            # Create test instances
            metrics_collector = MetricsCollector()
            performance_monitor = PerformanceMonitor()
            content_validator = ContentValidator()
            
            self.log_step("Core components instantiated successfully")
            
            # Test configuration loading
            config = self.config_manager.load_config()
            self.log_step(f"Configuration loaded (environment: {config.environment})")
            
            self.log_step("Installation validation completed successfully")
            return True
            
        except Exception as e:
            self.log_step(f"Installation validation failed: {e}", "ERROR")
            return False
            
    def run_setup(self, config_path: Optional[str] = None) -> bool:
        """Run complete setup process"""        self.log_step("Starting AI Core Module setup...")
        
        setup_steps = [
            ("System Requirements", self.check_system_requirements),
            ("Dependencies", self.install_dependencies),
            ("Directories", self.create_directories),
            ("Configuration", lambda: self.setup_configuration(config_path)),
            ("Default Models", self.download_default_models),
            ("Validation", self.validate_installation)
        ]
        
        for step_name, step_func in setup_steps:
            self.log_step(f"Starting: {step_name}")
            
            if not step_func():
                self.log_step(f"Setup failed at step: {step_name}", "ERROR")
                return False
                
            self.log_step(f"Completed: {step_name}")
            
        self.log_step("AI Core Module setup completed successfully!")
        return True
        
    def get_setup_log(self) -> List[Dict[str, Any]]:
        """Get setup log entries"""        return self.setup_log
        
    def save_setup_log(self, log_path: str) -> bool:
        """Save setup log to file"""        try:
            log_path = Path(log_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_path, 'w') as f:
                json.dump(self.setup_log, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to save setup log: {e}")
            return False


def setup_ai_core(config: Optional[Dict[str, Any]] = None, 
                  config_path: Optional[str] = None,
                  log_path: Optional[str] = None) -> bool:
    """    Quick setup function for AI Core module
    
    Args:
        config: Setup configuration
        config_path: Path to save configuration file
        log_path: Path to save setup log
        
    Returns:
        True if setup successful
    """    setup_manager = ModuleSetup(config)
    
    # Run setup
    success = setup_manager.run_setup(config_path)
    
    # Save log if path provided
    if log_path:
        setup_manager.save_setup_log(log_path)
        
    return success


def quick_setup() -> bool:
    """Quick setup with default configuration"""    return setup_ai_core(
        config={"environment": "development", "debug_mode": True},
        config_path="config/ai_core.json",
        log_path="logs/setup.json"
    )


def production_setup() -> bool:
    """Production setup with optimized configuration"""    return setup_ai_core(
        config={"environment": "production", "debug_mode": False},
        config_path="config/ai_core_production.json",
        log_path="logs/production_setup.json"
    )
